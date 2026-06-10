#!/usr/bin/env python3
"""
Inverse of extract_8th_position.py.

Read eighth_position.txt (one value per line) and write the i-th value into
the 8th position slot (index 7, the ``LHand`` joint) of the i-th keyframe of
the motion file. The number of values must match the number of keyframes.

Everything else in the motion file is preserved byte-for-byte; only the 8th
``- value`` line inside each ``position:`` block is replaced.

Usage:
    python3 inject_8th_position.py
    python3 inject_8th_position.py pickUpMotion.md eighth_position.txt out.md

If the output path is omitted, '<input>_updated.md' is written (the original
is left untouched). Pass the input path as the output to overwrite in place.
"""

import sys
import re

POSITION_INDEX = 7  # 8th value (0-based)


def load_values(path: str) -> list[str]:
    """Return the non-empty, stripped lines from the values file."""
    with open(path, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def inject(lines: list[str], values: list[str]) -> list[str]:
    """Replace the 8th position value of each keyframe with values[i].

    Operates on a list of raw file lines (without trailing newlines) and
    returns the modified list. Indentation/prefix of each replaced line is
    preserved so the output matches the surrounding style.
    """
    out = list(lines)
    frame = 0
    in_position = False
    item_idx = 0

    for n, line in enumerate(lines):
        if re.match(r'^\s*position\s*:\s*$', line):
            in_position = True
            item_idx = 0
            continue

        if not in_position:
            continue

        if line.strip().startswith('-'):
            if item_idx == POSITION_INDEX:
                if frame >= len(values):
                    raise ValueError(
                        f"More keyframes than values: keyframe {frame + 1} has "
                        f"no matching value (only {len(values)} provided)."
                    )
                # Preserve the original "- " prefix / indentation.
                prefix = line[: line.index('-') + 1]
                out[n] = f"{prefix} {values[frame]}"
            item_idx += 1
        else:
            # End of this position block.
            in_position = False
            frame += 1

    # The file may end while still inside the final position block.
    if in_position:
        frame += 1

    if frame != len(values):
        raise ValueError(
            f"Count mismatch: file has {frame} keyframes but "
            f"{len(values)} values were provided."
        )

    return out


def main(argv: list[str]) -> int:
    in_path = argv[1] if len(argv) > 1 else 'pickUpMotionCleaned.md'
    values_path = argv[2] if len(argv) > 2 else 'eighth_position.txt'
    out_path = argv[3] if len(argv) > 3 else _default_out(in_path)

    with open(in_path, 'r') as f:
        # Keep a trailing-newline flag so we reproduce the file faithfully.
        text = f.read()
    trailing_nl = text.endswith('\n')
    lines = text.splitlines()

    values = load_values(values_path)
    if not values:
        print(f"No values found in '{values_path}'.", file=sys.stderr)
        return 1

    updated = inject(lines, values)

    out_text = '\n'.join(updated) + ('\n' if trailing_nl else '')
    with open(out_path, 'w') as f:
        f.write(out_text)

    print(
        f"Injected {len(values)} values from '{values_path}' into the 8th "
        f"position of each keyframe: '{in_path}' -> '{out_path}'."
    )
    return 0


def _default_out(in_path: str) -> str:
    if in_path.endswith('.md'):
        return in_path[:-3] + '_updated.md'
    return in_path + '_updated'


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
