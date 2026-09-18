#!/usr/bin/env python3
"""Update GitHub star counts in the AI.skills README files.

Scans every README.md for GitHub repo links, fetches each repo's current
``stargazers_count`` from the GitHub API, and rewrites the star-count column in
the markdown tables. Cells marked ``官方`` / ``本地`` (no digits) are left alone.

Usage::

    GITHUB_TOKEN=... python3 .github/scripts/update_stars.py
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# GitHub repo link: [label](https://github.com/owner/repo)
LINK_RE = re.compile(r"\[[^\]]*\]\(https://github\.com/([^/)\s]+)/([^/)\s]+?)\)")
# Star-count cells must contain a digit (skip "官方" / "本地" markers)
DIGIT_RE = re.compile(r"\d")


def api_get(url: str) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "AI.skills-star-updater")
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def format_stars(n: int) -> str:
    """118000 -> '118k', 7000 -> '7k', 5400 -> '5.4k', 284 -> '284'."""
    if n >= 1000:
        v = n / 1000
        if v >= 100:
            return f"{round(v)}k"
        s = f"{v:.1f}"
        if s.endswith(".0"):
            s = s[:-2]
        return f"{s}k"
    return str(n)


def readmes():
    return sorted(ROOT.rglob("README.md"))


def collect_repos() -> dict:
    """Return {(owner, repo): [(path, line_index), ...]} for updatable cells."""
    repos = {}
    for path in readmes():
        for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            m = LINK_RE.search(line)
            if not m:
                continue
            cells = line.split("|")
            # table columns: | skill | source | star | desc |
            if len(cells) < 4 or not DIGIT_RE.search(cells[3]):
                continue  # "官方" / "本地" cell, not a number
            key = (m.group(1), m.group(2))
            repos.setdefault(key, []).append((path, idx))
    return repos


def main() -> None:
    repos = collect_repos()
    if not repos:
        print("No star-count cells found.")
        return

    files = {p for _, locs in repos.items() for p, _ in locs}
    print(f"{len(repos)} repos across {len(files)} files")

    stars = {}
    for owner, repo in repos:
        try:
            data = api_get(f"https://api.github.com/repos/{owner}/{repo}")
            stars[(owner, repo)] = data["stargazers_count"]
            print(f"  {owner}/{repo}: {stars[(owner, repo)]}")
        except Exception as exc:  # noqa: BLE001
            print(f"  [skip] {owner}/{repo}: {exc}", file=sys.stderr)

    changed = False
    for key, locations in repos.items():
        if key not in stars:
            continue
        new_val = format_stars(stars[key])
        for path, idx in locations:
            lines = path.read_text(encoding="utf-8").splitlines()
            cells = lines[idx].split("|")
            updated = re.sub(r"\d[\d.]*[kK]?", new_val, cells[3], count=1)
            if updated != cells[3]:
                cells[3] = updated
                lines[idx] = "|".join(cells)
                path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                changed = True
                print(f"  {path.relative_to(ROOT)}: {key[0]}/{key[1]} -> {new_val}")

    if not changed:
        print("All star counts already up to date.")
        return
    print("Star counts updated.")


if __name__ == "__main__":
    main()
