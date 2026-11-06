#!/usr/bin/env python3
"""Exercise archive validation and release activation without SSH or live files."""

import hashlib
import importlib.util
import io
import os
from pathlib import Path
import tarfile
import tempfile
import unittest


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


package = load_script("package-site")
activation = load_script("activate-site")


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "incoming").mkdir()

    def archive(self, version, extra=None):
        release = "a" * 40 + f"-10-{version}"
        archive = self.root / "incoming" / f"{release}.tar.gz"
        entries = {
            "product/index.html": f"version {version}".encode(),
            "product/assets/site.css": b"body {}",
            "product/assets/site.js": b"'use strict'",
        }
        entries.update(extra or {})
        with tarfile.open(archive, "w:gz") as output:
            for name, body in entries.items():
                member = tarfile.TarInfo(name)
                member.size = len(body)
                output.addfile(member, io.BytesIO(body))
        checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
        return archive, release, checksum

    def activate(self, args):
        activation.activate(self.root, *args)

    def test_successive_releases_keep_previous_files(self):
        first = self.archive(1)
        self.activate(first)
        self.assertFalse(first[0].exists())
        self.assertEqual((self.root / "current/product/index.html").read_text(), "version 1")
        self.activate(self.archive(2))
        self.assertEqual((self.root / "current/product/index.html").read_text(), "version 2")
        self.assertEqual((self.root / "releases" / first[1] / "product/index.html").read_text(), "version 1")

    def test_checksum_failure_keeps_current(self):
        self.activate(self.archive(1))
        archive, release, _ = self.archive(2)
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.activate((archive, release, "0" * 64))
        self.assertEqual((self.root / "current/product/index.html").read_text(), "version 1")

    def test_invalid_members_never_activate(self):
        for index, member in enumerate(["../escape", "promo/film.mp4", "product/assets/../../escape", "product/assets/.env"], 1):
            with self.subTest(member=member), self.assertRaises(ValueError):
                self.activate(self.archive(index, {member: b"invalid"}))
        self.assertFalse((self.root / "current").exists())

    def test_missing_required_file_never_activates(self):
        with self.assertRaisesRegex(ValueError, "missing or empty"):
            self.activate(self.archive(1, {"product/assets/site.js": b""}))
        self.assertFalse((self.root / "current").exists())

    def test_existing_real_directory_is_not_replaced(self):
        (self.root / "current").mkdir()
        with self.assertRaisesRegex(ValueError, "must be a symlink"):
            self.activate(self.archive(1))
        self.assertFalse((self.root / "current").is_symlink())

    def test_release_permissions_allow_nginx_reads(self):
        previous = os.umask(0o022)
        try:
            self.activate(self.archive(1))
        finally:
            os.umask(previous)
        for path in (self.root / "current/product").rglob("*"):
            self.assertEqual(path.stat().st_mode & 0o777, 0o755 if path.is_dir() else 0o644)

    def test_packager_rejects_missing_assets(self):
        (self.root / "assets").mkdir()
        (self.root / "index.html").write_text('<img src="assets/missing.png">')
        (self.root / "assets/site.css").write_text("body {}")
        (self.root / "assets/site.js").write_text("'use strict'")
        with self.assertRaisesRegex(ValueError, "Missing reference"):
            package.validate(self.root)


if __name__ == "__main__":
    unittest.main()
