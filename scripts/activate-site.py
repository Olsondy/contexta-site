#!/usr/bin/env python3
"""Run on the Linux host to validate and atomically activate a static release."""

import argparse
import fcntl
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile


def activate(root, archive_path, release, checksum):
    if not re.fullmatch(r"[0-9a-f]{40}-[0-9]+-[0-9]+", release):
        raise ValueError("Invalid commit/run/attempt release identifier")
    if not re.fullmatch(r"[0-9a-f]{64}", checksum):
        raise ValueError("Invalid SHA-256")
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != checksum:
        raise ValueError("Archive checksum mismatch")
    releases = root / "releases"
    releases.mkdir(parents=True, exist_ok=True, mode=0o755)
    with (root / ".deploy.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        current = root / "current"
        if current.exists() and not current.is_symlink():
            raise ValueError("current must be a symlink, not a real directory")
        target = releases / release
        if target.exists():
            raise ValueError("Release already exists; use a new workflow attempt")
        with tempfile.TemporaryDirectory(prefix=".upload-", dir=releases) as tmp:
            staging = Path(tmp)
            total = 0
            seen = set()
            with tarfile.open(archive_path, "r:gz") as archive:
                for member in archive:
                    path = PurePosixPath(member.name)
                    if (
                        not member.isfile()
                        or path.is_absolute()
                        or ".." in path.parts
                        or any(part.startswith(".") for part in path.parts)
                        or not (path == PurePosixPath("product/index.html") or path.parts[:2] == ("product", "assets"))
                        or path in seen
                    ):
                        raise ValueError(f"Unsupported archive member: {member.name}")
                    seen.add(path)
                    total += member.size
                    if total > 100 * 1024 * 1024 or len(seen) > 2000:
                        raise ValueError("Static archive exceeds the product site's size/file budget")
                    destination = staging / path
                    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                    with archive.extractfile(member) as source, destination.open("xb") as output:
                        shutil.copyfileobj(source, output)
                    destination.chmod(0o644)
            for required in ("product/index.html", "product/assets/site.css", "product/assets/site.js"):
                if not (staging / required).is_file() or (staging / required).stat().st_size == 0:
                    raise ValueError(f"Required file missing or empty: {required}")
            (staging / "release.txt").write_text(f"release={release}\nsha256={checksum}\n", encoding="ascii")
            staging.chmod(0o755)
            os.rename(staging, target)
        link = root / f".current-{release}"
        try:
            link.symlink_to(Path("releases") / release)
            os.replace(link, current)
        finally:
            link.unlink(missing_ok=True)
    archive_path.unlink()
    print(f"Activated static product release {release}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release")
    parser.add_argument("checksum")
    parser.add_argument("--root", type=Path, default=Path("/srv/contexta/site"))
    args = parser.parse_args()
    os.umask(0o022)
    root = args.root.resolve()
    activate(root, root / "incoming" / f"{args.release}.tar.gz", args.release, args.checksum)


if __name__ == "__main__":
    main()
