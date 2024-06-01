"""Diff the codepoints supported by two slice files.

Usage:

    python3 scripts/slice_cpdiff file1.nam file2.
"""

from collections import defaultdict
from pathlib import Path
import sys
from typing import Set
import unicodeblock.blocks


def codepoints(slice_file: Path) -> Set[int]:
    codepoints = set()
    with open(slice_file) as f:
        for line in f:
            comment_start = line.find("#")
            if comment_start != -1:
                line = line[:comment_start]
            line = line.strip()
            if not line.startswith("codepoints: "):
                continue
            codepoints.add(int(line[line.index(" ") :]))
    return codepoints


def path_to_file(maybe: str) -> Path:
    path = Path(maybe)
    assert path.is_file(), f"{path} must be a file"
    return path


def list(tag: str, source: str, codepoints: Set[int]):
    for cp in sorted(codepoints):
        print(f"{tag} {source} 0x{cp:04x}")


def list_blocks(prefix: str, codepoints: Set[int]):
    blocks = defaultdict(int)
    for cp in codepoints:
        blocks[unicodeblock.blocks.of(chr(cp))] += 1
    blocks = sorted([(count, block) for (block, count) in blocks.items()], reverse=True)
    for count, block in blocks:
        print(f"{prefix}{block} {count}")


def main(argv):
    assert len(argv) == 3, "Must have exactly two arguments"

    nam1 = path_to_file(argv[1])
    nam2 = path_to_file(argv[2])
    nam1cp = codepoints(nam1)
    nam2cp = codepoints(nam2)

    identical = nam1cp & nam2cp
    only1 = nam1cp - nam2cp
    only2 = nam2cp - nam1cp

    list("only", nam1.name, only1)
    list("only", nam2.name, only2)

    print()
    print(f"{len(identical)} match")
    print(f"{len(only1)} only in {nam1.name}")
    list_blocks("  ", only1)
    print(f"{len(only2)} only in {nam2.name}")
    list_blocks("  ", only2)


if __name__ == "__main__":
    main(sys.argv)
