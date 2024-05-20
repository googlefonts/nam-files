"""Diff the codepoints supported by two slice files.

Usage:

    python3 scripts/slice_cpdiff file1.nam file2.
"""

from pathlib import Path
import sys
from typing import Set


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
            codepoints.add(int(line[line.index(" "):]))
    return codepoints


def path_to_file(maybe: str) -> Path:
    path = Path(maybe)
    assert path.is_file(), f"{path} must be a file"
    return path


def list(tag: str, source: str, codepoints: Set[int]):
    for cp in sorted(codepoints):
        print(f"{tag} {source} 0x{cp:04x}")

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
    print(f"{len(only2)} only in {nam2.name}")


if __name__ == "__main__":
    main(sys.argv)
