#!/usr/bin/env python3
"""
Read pickUpMotion.md, take the 8th position value of every keyframe
(index 7 in the position list, i.e. the ``LHand`` joint) and write each
one on its own line into a separate .txt file.

Usage:
    python3 extract_8th_position.py
    python3 extract_8th_position.py pickUpMotion.md eighth_position.txt
"""

import sys
import re

POSITION_INDEX = 7  # 8th value (0-based)


def collect_positions(text: str) -> list[list[float]]:
    """Return the ``position:`` value lists, one per keyframe.

    Handles both the full JointState format (documents split by '---', with
    extra velocity:/effort: sections) and the simpler name/position block
    format. Every ``position:`` block in the file becomes one keyframe.
    """
    frames: list[list[float]] = []
    capturing = False
    values: list[float] = []

    for line in text.splitlines():
        stripped = line.strip()

        if re.match(r'^\s*position\s*:\s*$', line):
            # Start of a new position block — flush any in-progress one.
            if values:
                frames.append(values)
            capturing = True
            values = []
            continue

        if capturing:
            if stripped.startswith('-'):
                values.append(float(stripped[1:].strip()))
            else:
                # Reached the next key (velocity:/effort:/name:) — close block.
                if values:
                    frames.append(values)
                capturing = False
                values = []

    if values:
        frames.append(values)

    return frames


def main(argv: list[str]) -> int:
    in_path = argv[1] if len(argv) > 1 else 'pickUpMotionCleaned.md'
    out_path = argv[2] if len(argv) > 2 else 'eighth_position.txt'

    with open(in_path, 'r') as f:
        text = f.read()

    frames = collect_positions(text)
    if not frames:
        print(f"No position data found in '{in_path}'.", file=sys.stderr)
        return 1

    eighth_values = []
    for i, values in enumerate(frames):
        if len(values) <= POSITION_INDEX:
            print(
                f"Keyframe {i} has only {len(values)} position values; "
                f"skipping (need at least {POSITION_INDEX + 1}).",
                file=sys.stderr,
            )
            continue
        eighth_values.append(values[POSITION_INDEX])

    with open(out_path, 'w') as f:
        f.write('\n'.join(str(v) for v in eighth_values) + '\n')

    print(f"Wrote {len(eighth_values)} values (8th position) to '{out_path}'.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
