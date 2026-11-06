#!/usr/bin/env python3
"""Validate local references and package only the public product site."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import tarfile
from urllib.parse import unquote, urlsplit


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"src", "href"} and value:
                self.urls.append(value)


def validate(root):
    root = root.resolve()
    for relative in ("index.html", "assets/site.css", "assets/site.js"):
        if not (root / relative).is_file():
            raise ValueError(f"Required file missing: {relative}")
    files = [root / "index.html"]
    for path in sorted((root / "assets").rglob("*")):
        if path.is_symlink() or path.name.startswith("."):
            raise ValueError(f"Unsupported asset: {path.relative_to(root)}")
        if path.is_file():
            files.append(path)
    references = References()
    references.feed((root / "index.html").read_text(encoding="utf-8"))
    urls = [(root / "index.html", url) for url in references.urls]
    for path in files:
        if path.suffix == ".css":
            urls.extend(
                (path, url)
                for url in re.findall(r"url\(\s*['\"]?([^'\")]+)", path.read_text(encoding="utf-8"))
            )
    for source, url in urls:
        parsed = urlsplit(url.strip())
        if not parsed.path or parsed.scheme or parsed.netloc:
            continue
        target = (source.parent / unquote(parsed.path)).resolve()
        if root not in target.parents:
            raise ValueError(f"Reference escapes the site: {url}")
        if not target.is_file():
            if target == root / "assets/img/miniprogram-code.png":
                print("NOTE: Mini-program code absent; existing brand fallback is retained.")
                continue
            raise ValueError(f"Missing reference in {source.relative_to(root)}: {url}")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional .tar.gz output; omit to validate only")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    files = validate(root)
    if args.output:
        output = args.output.resolve()
        if output == root / "index.html" or root / "assets" in output.parents:
            raise ValueError("Archive must be outside the public assets")
        with tarfile.open(output, "w:gz") as archive:
            for path in files:
                info = archive.gettarinfo(str(path), "product/" + path.relative_to(root).as_posix())
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                info.mode = 0o644
                info.mtime = 0
                with path.open("rb") as stream:
                    archive.addfile(info, stream)
        print(f"Packaged {len(files)} public files: {output.name}")
    else:
        print(f"Validated {len(files)} public files.")


if __name__ == "__main__":
    main()
