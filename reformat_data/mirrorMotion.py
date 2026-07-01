"""
mirrorMotion.py

Swaps the left-arm and right-arm joint positions in a NAO motion file,
producing a mirrored version. Run from the repo root or from Nao/:

    python mirrorMotion.py                          # default paths
    python mirrorMotion.py -i motionFiles/pickUpMotion.md -o motionFiles/pickUpMotionRight.md

Joint sign convention on NAO (joints that must be negated when L↔R):
    ShoulderRoll, ElbowYaw, ElbowRoll, WristYaw
Joints that keep the same sign:
    ShoulderPitch, Hand
"""

import argparse
import os
import re

# ---------------------------------------------------------------------------
# Arm joint swap table
# ---------------------------------------------------------------------------

# Maps each left-arm joint to its right-arm counterpart.
# True  = negate the value when assigning to the other side
# False = copy the value as-is
L_TO_R: dict[str, tuple[str, bool]] = {
    "LShoulderPitch": ("RShoulderPitch", False),
    "LShoulderRoll": ("RShoulderRoll", True),
    "LElbowYaw": ("RElbowYaw", True),
    "LElbowRoll": ("RElbowRoll", True),
    "LWristYaw": ("RWristYaw", True),
    "LHand": ("RHand", False),
}

R_TO_L: dict[str, tuple[str, bool]] = {
    r: (l, negate) for l, (r, negate) in L_TO_R.items()
}


# ---------------------------------------------------------------------------
# Parser (mirrors parse_motion_file from motionControl.py)
# ---------------------------------------------------------------------------


def parse_motion_file(filepath: str) -> list[dict]:
    with open(filepath, "r") as f:
        content = f.read()

    poses = []
    blocks = re.split(r"\n\s*\n", content.strip())

    i = 0
    while i < len(blocks):
        block = blocks[i].strip()
        if not block:
            i += 1
            continue

        combined = block
        if "name:" in block and "position:" not in block:
            if i + 1 < len(blocks):
                combined = block + "\n" + blocks[i + 1]
                i += 1

        if "name:" in combined and "position:" in combined:
            names_section = re.search(r"name:\s*((?:- .+\n?)+)", combined)
            positions_section = re.search(r"position:\s*((?:- .+\n?)+)", combined)

            if names_section and positions_section:
                joints = [
                    line.strip().removeprefix("- ")
                    for line in names_section.group(1).strip().splitlines()
                    if line.strip().startswith("-")
                ]
                angles = [
                    float(line.strip().removeprefix("- "))
                    for line in positions_section.group(1).strip().splitlines()
                    if line.strip().startswith("-")
                ]

                if len(joints) == len(angles) and len(joints) > 0:
                    poses.append({"joints": joints, "angles": angles})

        i += 1

    return poses


# ---------------------------------------------------------------------------
# Mirroring logic
# ---------------------------------------------------------------------------


def mirror_pose(
    joints: list[str], angles: list[float]
) -> tuple[list[str], list[float]]:
    """Return a new (joints, angles) pair with L/R arm values swapped."""
    angle_map: dict[str, float] = dict(zip(joints, angles))

    new_angles = list(angles)

    for idx, joint in enumerate(joints):
        if joint in L_TO_R:
            r_joint, negate = L_TO_R[joint]
            r_val = angle_map.get(r_joint)
            if r_val is not None:
                new_angles[idx] = -r_val if negate else r_val

        elif joint in R_TO_L:
            l_joint, negate = R_TO_L[joint]
            l_val = angle_map.get(l_joint)
            if l_val is not None:
                new_angles[idx] = -l_val if negate else l_val

    return joints, new_angles


# ---------------------------------------------------------------------------
# Serialiser
# ---------------------------------------------------------------------------


def serialise_poses(poses: list[dict]) -> str:
    blocks = []
    for pose in poses:
        lines = ["name:"]
        for j in pose["joints"]:
            lines.append(f"- {j}")
        lines.append("position:")
        for a in pose["angles"]:
            lines.append(f"- {a}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_in = os.path.join("/home/amrss26/python-amr-project/AMR/Nao/motionFiles/standUpMotion.md")
    default_out = os.path.join("/home/amrss26/python-amr-project/AMR/Nao/motionFiles/standUpMotionRight.md")

    parser = argparse.ArgumentParser(
        description="Mirror a NAO motion file (L arm ↔ R arm)."
    )
    parser.add_argument("-i", "--input", default=default_in, help="Input motion file")
    parser.add_argument(
        "-o", "--output", default=default_out, help="Output motion file"
    )
    args = parser.parse_args()

    poses = parse_motion_file(args.input)
    print(f"Parsed {len(poses)} poses from '{args.input}'.")

    mirrored = []
    for pose in poses:
        joints, angles = mirror_pose(pose["joints"], pose["angles"])
        mirrored.append({"joints": joints, "angles": angles})

    output_text = serialise_poses(mirrored)
    with open(args.output, "w") as f:
        f.write(output_text)

    print(f"Mirrored motion written to '{args.output}'.")


if __name__ == "__main__":
    main()
