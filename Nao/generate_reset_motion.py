"""
Generates a smooth motion between two robot poses.

Given a start position and an end position (each a list of 26 joint angles,
in the joint order below), this produces 20 interpolated frames that mimic a
clean motion and writes them to Nao/motionFiles.md, structurally identical to
the files inside Nao/motionFiles/.

A smoothstep (ease-in / ease-out) curve is used instead of plain linear
interpolation so the motion accelerates and decelerates gently rather than
snapping to a constant velocity.

Usage:
    Edit START_POSITION / END_POSITION below (or import and call
    generate_motion from another script), then run:

        python3 generate_motion.py
"""

import os

# Joint order used by every motion file in Nao/motionFiles/.
JOINT_NAMES = [
    'HeadYaw',
    'HeadPitch',
    'LShoulderPitch',
    'LShoulderRoll',
    'LElbowYaw',
    'LElbowRoll',
    'LWristYaw',
    'LHand',
    'LHipYawPitch',
    'LHipRoll',
    'LHipPitch',
    'LKneePitch',
    'LAnklePitch',
    'LAnkleRoll',
    'RHipYawPitch',
    'RHipRoll',
    'RHipPitch',
    'RKneePitch',
    'RAnklePitch',
    'RAnkleRoll',
    'RShoulderPitch',
    'RShoulderRoll',
    'RElbowYaw',
    'RElbowRoll',
    'RWristYaw',
    'RHand',
]

# Number of interpolated frames to generate between start and end (inclusive).
NUM_FRAMES = 80

# Where the generated motion is written.
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'motionFiles/resetMotion.md')


def smoothstep(t: float) -> float:
    """Ease-in / ease-out curve mapping t in [0, 1] to [0, 1].

    Zero velocity at both ends gives a clean, natural-looking motion."""
    return t * t * (3.0 - 2.0 * t)


def interpolate(start: list[float], end: list[float], t: float) -> list[float]:
    """Interpolate every joint angle at eased fraction t in [0, 1]."""
    eased = smoothstep(t)
    return [s + (e - s) * eased for s, e in zip(start, end)]


def generate_motion(
    start_position: list[float],
    end_position: list[float],
    num_frames: int = NUM_FRAMES,
) -> list[list[float]]:
    """Generate `num_frames` poses from start to end using smooth easing.

    The first frame equals start_position and the last equals end_position."""
    if len(start_position) != len(JOINT_NAMES):
        raise ValueError(
            f"start_position has {len(start_position)} angles, "
            f"expected {len(JOINT_NAMES)}."
        )
    if len(end_position) != len(JOINT_NAMES):
        raise ValueError(
            f"end_position has {len(end_position)} angles, "
            f"expected {len(JOINT_NAMES)}."
        )
    if num_frames < 2:
        raise ValueError("num_frames must be at least 2.")

    return [
        interpolate(start_position, end_position, i / (num_frames - 1))
        for i in range(num_frames)
    ]


def frame_to_text(angles: list[float]) -> str:
    lines = ['name:']
    lines.extend(f'- {j}' for j in JOINT_NAMES)
    lines.append('position:')
    lines.extend(f'- {a}' for a in angles)
    return '\n'.join(lines)


def write_motion_file(filepath: str, frames: list[list[float]]) -> None:
    text = '\n\n'.join(frame_to_text(f) for f in frames) + '\n'
    with open(filepath, 'w') as f:
        f.write(text)


# ---------------------------------------------------------------------------
# Edit these two poses, then run the script. Both are lists of 26 joint angles
# in the JOINT_NAMES order above. The values below are placeholders (all zero
# for start, a small example for end) — replace them with your real poses.
# ---------------------------------------------------------------------------

START_POSITION = [0.0] * len(JOINT_NAMES)
END_POSITION = [0.0] * len(JOINT_NAMES)


def main():
    frames = generate_motion(START_POSITION, END_POSITION, NUM_FRAMES)
    write_motion_file(OUTPUT_FILE, frames)
    print(f"Done. Wrote {len(frames)} frames to {OUTPUT_FILE}.")


if __name__ == '__main__':
    main()
