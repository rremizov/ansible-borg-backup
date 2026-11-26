#!/usr/bin/env python3

"""Repository statistics for Borg: repository summary, latest archive, and
du-style per-directory size and file-count breakdowns, computed from the
output of `borg info` and `borg list --json-lines`."""

import json
import os
import subprocess
import sys

TOP = 10


def borg(*args):
    return subprocess.run(("borg",) + args, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)


def human_size(num):
    if num < 1000:
        return f"{num} B"
    for unit in ("kB", "MB", "GB", "TB"):
        num /= 1000
        if num < 1000:
            return f"{num:.0f} {unit}" if num >= 10 else f"{num:.1f} {unit}"
    return f"{num:.0f} PB"


def breakdown(entries):
    counts = {}
    sizes = {}
    for entry in entries:
        if entry.get("type") != "f":
            continue
        parts = entry["path"].split("/")
        for depth in range(1, len(parts)):
            prefix = "/".join(parts[:depth])
            counts[prefix] = counts.get(prefix, 0) + 1
            sizes[prefix] = sizes.get(prefix, 0) + entry.get("size", 0)
    return counts, sizes


def main():
    repo = os.environ.get("BORG_REPO")
    if not repo:
        print("BORG_REPO is not set", file=sys.stderr)
        return 2

    info = borg("info", "--json")
    if info.returncode != 0:
        print(info.stderr.strip(), file=sys.stderr)
        return 1
    data = json.loads(info.stdout)
    stats = data.get("cache", {}).get("stats", {})
    location = data.get("repository", {}).get("location", repo)
    print("=== Repository ===")
    print(f"{location}: {human_size(stats.get('unique_csize', 0))} unique compressed")

    last = borg("info", "--json", "--last", "1")
    if last.returncode != 0:
        print(last.stderr.strip(), file=sys.stderr)
        return 1
    archive = json.loads(last.stdout)["archives"][0]
    print()
    print("=== Latest archive ===")
    print(f"{archive['name']} ({archive['start']})")

    listing = borg("list", "--json-lines", f"::{archive['name']}")
    if listing.returncode != 0:
        print(listing.stderr.strip(), file=sys.stderr)
        return 1

    entries = []
    for line in listing.stdout.splitlines():
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    counts, sizes = breakdown(entries)
    print()
    print("=== Files count by directory ===")
    for path, count in sorted(counts.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[:TOP]:
        print(f"{path}: {count} files")
    print()
    print("=== Size by directory ===")
    for path, size in sorted(sizes.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[:TOP]:
        print(f"{path}: {human_size(size)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
