"""Validate workflow YAML, README regions, and checked-in profile assets."""
import re
from pathlib import Path
from xml.etree import ElementTree

import yaml

from scripts.markdown_renderer import render_regions
from scripts.profile_config import load_config


def main():
    root = Path(__file__).resolve().parents[1]
    load_config(root / "config/profile.yml")
    for path in (root / ".github/workflows").glob("*.yml"):
        workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not workflow.get("jobs") or not (workflow.get("on") or workflow.get(True)):
            raise ValueError(f"Invalid workflow structure in {path.name}")
    for name in ("README.md", "README.template.md"):
        readme = render_regions((root / name).read_text(encoding="utf-8"))
        for reference in re.findall(r"\]\((assets/[^)]+)\)", readme):
            # README image cache-busting query parameters are not filesystem paths.
            target = reference.split("?", 1)[0].split("#", 1)[0]
            if not (root / target).is_file():
                raise ValueError(f"{name} references missing {target}")
    for path in (root / "assets").glob("*.svg"):
        if ElementTree.parse(path).getroot().tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError(f"Invalid SVG root in {path.name}")
    if not (root / "assets/banner.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG fallback")
    print("Profile files passed validation")


if __name__ == "__main__":
    main()
