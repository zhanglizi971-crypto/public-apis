#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parse README.md API tables into structured data.json + build console assets."""
import json
import re
from datetime import datetime, timezone

ROOT = Path = None
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
README = REPO / "README.md"
OUT_JSON = REPO / "data.json"
OUT_HTML = REPO / "index.html"


def split_row(line: str):
    """Split a markdown table row into cells, tolerating pipes inside links."""
    cells = []
    buf = []
    depth = 0  # paren depth for () inside links
    for ch in line:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "|" and depth == 0:
            cells.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    cells.append("".join(buf))
    if cells and cells[0] == "":
        cells = cells[1:]  # leading pipe creates an empty first cell
    if cells and cells[-1] == "":
        cells = cells[:-1]  # trailing pipe creates an empty last cell
    return [c.strip() for c in cells]


def parse_entry(cells):
    """Parse a table row into an API record; return None if not a valid entry."""
    if len(cells) < 5:
        return None
    name_url = cells[0].strip()  # [Name](url)
    if not name_url.startswith("["):
        return None
    sep = name_url.find("](")
    if sep <= 1:
        return None
    name = name_url[1:sep].strip()
    # url = everything between the outer parens, using depth counting so that
    # nested parens inside the URL (e.g. wikipedia links) are kept intact
    s = name_url[sep + 2:]
    depth = 0
    cut = len(s)
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                cut = i
                break
            depth -= 1
    url = s[:cut].strip()
    if not url.startswith("http"):
        return None
    description = cells[1].strip() if len(cells) > 1 else ""
    if not description:
        return None
    auth = cells[2].strip().strip("`").strip() if len(cells) > 2 else "No"
    if auth == "":
        auth = "No"
    https = (cells[3].strip() if len(cells) > 3 else "No") == "Yes"
    cors = cells[4].strip() if len(cells) > 4 else "Unknown"
    if cors not in ("Yes", "No", "Unknown"):
        cors = "Unknown"
    return {
        "name": name,
        "url": url,
        "description": description,
        "auth": auth,
        "https": https,
        "cors": cors,
    }


def parse(readme: Path):
    categories = []
    cur = None
    in_index = False
    for raw in readme.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.rstrip()
        if line.startswith("## Index"):
            in_index = True
            continue
        if not in_index:
            continue
        if line.startswith("## ") and line != "## Index":
            break  # past the directory section (License etc.)
        if line.startswith("### "):
            cur = {"name": line[4:].strip(), "apis": []}
            categories.append(cur)
            continue
        if cur is not None and line.startswith("|"):
            cells = split_row(line)
            entry = parse_entry(cells)
            if entry:
                cur["apis"].append(entry)
    return categories


def main():
    categories = parse(README)
    total = sum(len(c["apis"]) for c in categories)
    assert total > 500, f"suspiciously few APIs parsed: {total}"
    doc = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "README.md",
        "total": total,
        "categories": categories,
    }
    OUT_JSON.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"categories: {len(categories)}, apis: {total}")
    for c in categories:
        print(f"  {c['name']}: {len(c['apis'])}")


if __name__ == "__main__":
    main()