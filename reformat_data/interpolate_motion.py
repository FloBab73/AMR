"""
Inserts an interpolated midpoint keyframe between every consecutive pair of
existing frames in a motion file.

The original frames are snapshotted before any insertion, so newly added
frames are never used as interpolation sources.

Usage:
    python3 interpolate_motion.py <motion_file>

Example:
    python3 interpolate_motion.py sitDownMotion.md
"""

import re
import sys


def parse_motion_file(filepath: str) -> list[dict]:
    with open(filepath, 'r') as f:
        content = f.read()

    poses = []
    blocks = re.split(r'\n\s*\n', content.strip())

    i = 0
    while i < len(blocks):
        block = blocks[i].strip()
        if not block:
            i += 1
            continue

        combined = block
        if 'name:' in block and 'position:' not in block:
            if i + 1 < len(blocks):
                combined = block + '\n' + blocks[i + 1]
                i += 1

        if 'name:' in combined and 'position:' in combined:
            names_section     = re.search(r'name:\s*((?:- .+\n?)+)',     combined)
            positions_section = re.search(r'position:\s*((?:- .+\n?)+)', combined)

            if names_section and positions_section:
                joints = [
                    line.strip().removeprefix('- ')
                    for line in names_section.group(1).strip().splitlines()
                    if line.strip().startswith('-')
                ]
                angles = [
                    float(line.strip().removeprefix('- '))
                    for line in positions_section.group(1).strip().splitlines()
                    if line.strip().startswith('-')
                ]

                if len(joints) == len(angles) and joints:
                    poses.append({'joints': joints, 'angles': angles})

        i += 1

    return poses


def frame_to_text(pose: dict) -> str:
    lines = ['name:']
    for j in pose['joints']:
        lines.append(f'- {j}')
    lines.append('position:')
    for a in pose['angles']:
        lines.append(f'- {a}')
    return '\n'.join(lines)


def interpolate(pose_a: dict, pose_b: dict) -> dict:
    if pose_a['joints'] != pose_b['joints']:
        raise ValueError(
            "Joint lists differ between the two frames — cannot interpolate.\n"
            f"  Frame A joints: {pose_a['joints']}\n"
            f"  Frame B joints: {pose_b['joints']}"
        )
    mid_angles = [
        (a + b) / 2.0
        for a, b in zip(pose_a['angles'], pose_b['angles'])
    ]
    return {'joints': pose_a['joints'], 'angles': mid_angles}


def write_motion_file(filepath: str, poses: list[dict]) -> None:
    text = '\n\n'.join(frame_to_text(p) for p in poses) + '\n'
    with open(filepath, 'w') as f:
        f.write(text)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    filepath = sys.argv[1]

    # Snapshot the original frames before any insertion.
    original = parse_motion_file(filepath)
    n = len(original)

    if n < 2:
        print(f"Error: need at least 2 frames to interpolate, found {n}.")
        sys.exit(1)

    # Build result by interleaving original frames with their midpoints.
    result = [original[0]]
    for i in range(n - 1):
        result.append(interpolate(original[i], original[i + 1]))
        result.append(original[i + 1])

    write_motion_file(filepath, result)

    print(f"Done. {n} original frames → {len(result)} frames ({n - 1} inserted).")


if __name__ == '__main__':
    main()
