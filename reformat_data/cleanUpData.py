#!/usr/bin/env python3
"""Clean up recorded motion data.

Reads a file shaped like pickUpMotionRecored.txt: a sequence of YAML-style
data sets separated by '---' lines. Each data set contains the top-level
sections 'header', 'name', 'position', 'velocity' and 'effort'.

This strips the 'header', 'velocity' and 'effort' sections from every data
set and replaces each '---' separator with a blank newline, leaving 'name',
'position' and everything else untouched.
"""

import sys

# Top-level sections that should be removed from every data set.
SECTIONS_TO_REMOVE = ("header", "velocity", "effort")


def clean_up(lines):
    """Yield only the lines that should be kept."""
    drop = False  # whether we are currently inside a section to remove
    for line in lines:
        stripped = line.lstrip()

        # A document separator resets the section context and is replaced by
        # a single newline in the output.
        if stripped.startswith("---"):
            drop = False
            yield "\n"
            continue

        # A new top-level section starts at column 0 (no leading whitespace)
        # and is not a list item ('- ...').
        is_top_level = line[:1] not in (" ", "\t", "-", "\n", "")
        if is_top_level:
            key = stripped.split(":", 1)[0].strip()
            drop = key in SECTIONS_TO_REMOVE

        if not drop:
            yield line


def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else "output.txt"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "cleanedOuptut.txt"

    with open(in_path, "r") as f:
        lines = f.readlines()

    with open(out_path, "w") as f:
        f.writelines(clean_up(lines))

    print(f"Cleaned data written to {out_path}")


if __name__ == "__main__":
    main()
