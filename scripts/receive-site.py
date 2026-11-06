#!/usr/bin/env python3
"""Receive a static archive through a forced SSH command."""

import importlib.util
import os
from pathlib import Path
import re
import sys
import tarfile
import tempfile


MAX_ARCHIVE_BYTES = 25 * 1024 * 1024
DEPLOY_ROOT = Path("/srv/contexta/site")


def deployment_arguments(command):
    match = re.fullmatch(
        r"contexta-site deploy ([0-9a-f]{40}-[0-9]+-[0-9]+) ([0-9a-f]{64})",
        command,
    )
    if not match:
        raise ValueError("Only static product deployment is allowed")
    return match.groups()


def receive(root, stream, command):
    release, checksum = deployment_arguments(command)
    incoming = root / "incoming"
    incoming.mkdir(parents=True, exist_ok=True, mode=0o755)
    with tempfile.NamedTemporaryFile(prefix=".upload-", suffix=".tar.gz", dir=incoming, delete=False) as output:
        archive_path = Path(output.name)
        try:
            total = 0
            while chunk := stream.read(64 * 1024):
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    raise ValueError("Compressed archive exceeds the 25 MiB upload budget")
                output.write(chunk)
            output.close()
            # Both scripts are installed by the administrator in a root-owned directory.
            spec = importlib.util.spec_from_file_location("site_activation", Path(__file__).with_name("activate-site.py"))
            activation = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(activation)
            activation.activate(root, archive_path, release, checksum)
        finally:
            archive_path.unlink(missing_ok=True)


def main():
    os.umask(0o022)
    try:
        if len(sys.argv) != 1:
            raise ValueError("Receiver arguments are not allowed")
        receive(DEPLOY_ROOT, sys.stdin.buffer, os.environ.get("SSH_ORIGINAL_COMMAND", ""))
    except (ValueError, OSError, tarfile.TarError) as error:
        print(f"Static deployment rejected: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
