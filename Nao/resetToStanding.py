"""
Reset-to-standing routine.

Brings the robot from whatever pose it's currently in into the sit-down start
pose: capture the current pose from the node's cached /joint_states, interpolate
a smooth eased motion to the first keyframe of the sit-down motion, write it to
motionFiles/resetMotion.md, and play it through the node's playback path.

MotionControl owns the /joint_angles publisher and the playback loop, so this
module just needs the node to read its cached pose and to play the result.
"""

from generate_reset_motion import (
    JOINT_NAMES,
    OUTPUT_FILE,
    generate_motion,
    write_motion_file,
)


def _to_motion_order(
    names: list[str], positions: list[float], fallback: list[float]
) -> list[float]:
    """Reorder a /joint_states (name, position) pair into JOINT_NAMES order.

    /joint_states publishes its own joint name list, which need not match the
    motion-file order. Any joint missing from the message keeps the `fallback`
    angle so it simply isn't driven."""
    captured = dict(zip(names, positions))
    return [captured.get(name, fallback[i]) for i, name in enumerate(JOINT_NAMES)]


def reset_to_standing(node) -> None:
    """Capture the node's current pose, generate a smooth motion to the sitDown
    start pose, and play it. `node` must be a MotionControl exposing
    `latest_joint_state` and `play(Motion)`."""
    # Deferred import avoids a circular import at module load (motionControl
    # imports this module at the top level).
    from motionControl import Motion, parse_motion_file

    if node.latest_joint_state is None:
        node.get_logger().warn("No /joint_states received yet; skipping reset.")
        return

    poses = parse_motion_file(Motion.sitDown.path)
    if not poses:
        node.get_logger().error("sitDown motion empty; cannot reset.")
        return

    end_position = poses[0]["angles"]
    msg = node.latest_joint_state
    start = _to_motion_order(list(msg.name), list(msg.position), end_position)

    frames = generate_motion(start, end_position)
    write_motion_file(OUTPUT_FILE, frames)
    node.get_logger().info(f"Generated {len(frames)}-frame reset motion.")

    node.play(Motion.reset)
