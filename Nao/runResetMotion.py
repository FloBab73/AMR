"""
Reset motion runner.

Flow:
  1. Capture one /joint_states message and use it as the Start_Position.
  2. Take the first keyframe of pickUpMotion.md as the End_Position.
  3. Run generate_reset_motion to interpolate a clean motion between them
     (written to motionFiles/resetMotion.md).
  4. Play the generated motion on the robot.

This brings the robot smoothly from wherever it currently is into the pose
the pick-up motion expects to start from.
"""

import time
from stepToTheSide import move_forward
import rclpy
from naoqi_bridge_msgs.msg import JointAnglesWithSpeed
from rclpy.node import Node
from sensor_msgs.msg import JointState

from generate_reset_motion import (
    JOINT_NAMES,
    OUTPUT_FILE,
    generate_motion,
    write_motion_file,
)
from motionControl import MIN_DURATION, Motion, parse_motion_file

JOINT_STATES_TOPIC = "/joint_states"


class RunResetMotion(Node):
    """Capture the current pose, interpolate to the pick-up start pose, play it."""

    def __init__(self, pose_speed: float = 0.15, motion_speed: float = 0.2):
        super().__init__("run_reset_motion")
        self.pose_speed = pose_speed  # hardware joint speed fraction (0–1)
        self.motion_speed = motion_speed  # playback speed in rad/s
        self.finished = False
        self._handled = False
        move_forward(self)
        self.joint_pub = self.create_publisher(
            JointAnglesWithSpeed, "/joint_angles", 10
        )
        self.joint_state_sub = self.create_subscription(
            JointState, JOINT_STATES_TOPIC, self.on_joint_state, 10
        )
        self.get_logger().info(
            f"Waiting for one sample on '{JOINT_STATES_TOPIC}'..."
        )

    # ------------------------------------------------------------------
    # Capture + generate
    # ------------------------------------------------------------------

    def on_joint_state(self, msg: JointState):
        if self._handled:
            return
        self._handled = True

        start_position = self.to_motion_order(msg)
        end_position = self.pickup_start_pose()

        self.get_logger().info("Captured start pose; generating reset motion.")
        frames = generate_motion(start_position, end_position)
        write_motion_file(OUTPUT_FILE, frames)
        self.get_logger().info(f"Wrote {len(frames)} frames to {OUTPUT_FILE}.")

        self.play(OUTPUT_FILE)
        self.finished = True

    def to_motion_order(self, msg: JointState) -> list[float]:
        """Reorder /joint_states angles into the motion-file JOINT_NAMES order.

        /joint_states publishes its own joint name list, which need not match
        the motion-file order. Any joint missing from the message keeps the
        pick-up start angle so it simply isn't driven."""
        captured = dict(zip(msg.name, msg.position))
        end = self.pickup_start_pose()
        return [captured.get(name, end[i]) for i, name in enumerate(JOINT_NAMES)]

    def pickup_start_pose(self) -> list[float]:
        """First keyframe of the pick-up motion (already in JOINT_NAMES order)."""
        poses = parse_motion_file(Motion.pickUp.path)
        if not poses:
            raise RuntimeError(f"No poses found in {Motion.pickUp.path}.")
        return poses[0]["angles"]

    # ------------------------------------------------------------------
    # Playback (mirrors motionControl.MotionControl)
    # ------------------------------------------------------------------

    def send_pose(self, joints: list, angles: list, speed: float | None = None):
        msg = JointAnglesWithSpeed()
        msg.joint_names = joints
        msg.joint_angles = angles
        msg.speed = speed if speed is not None else self.pose_speed
        msg.relative = False
        self.joint_pub.publish(msg)

    def _play_poses(self, poses: list[dict]):
        prev_map: dict[str, float] = {}

        self.get_logger().info(
            f"Starting motion playback: {len(poses)} poses, "
            f"motion_speed={self.motion_speed} rad/s"
        )

        for idx, pose in enumerate(poses):
            joints = pose["joints"]
            targets = pose["angles"]
            starts = [prev_map.get(j, t) for j, t in zip(joints, targets)]

            max_delta = max((abs(t - s) for s, t in zip(starts, targets)), default=0.0)
            duration = max(max_delta / self.motion_speed, MIN_DURATION)

            self.get_logger().info(
                f"  Pose {idx + 1}/{len(poses)} — {len(joints)} joints, "
                f"max_delta={max_delta:.3f} rad, duration={duration:.2f}s"
            )

            self.send_pose(joints, targets)
            time.sleep(duration)

            for j, t in zip(joints, targets):
                prev_map[j] = t

        self.get_logger().info("Motion playback complete.")
        time.sleep(2.0)  # give DDS time to transmit the final pose

    def play(self, motion_path: str):
        """Load and play the motion at the given path, waiting for the bridge first."""
        self.get_logger().info("Waiting for a subscriber on /joint_angles...")
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if self.joint_pub.get_subscription_count() > 0:
                break
            time.sleep(0.2)
        if self.joint_pub.get_subscription_count() == 0:
            self.get_logger().warn(
                "No subscriber on /joint_angles after 10 s — is naoqi_driver running? "
                "Messages will be lost and the robot will not move."
            )

        poses = parse_motion_file(motion_path)
        if not poses:
            self.get_logger().error(f"No poses loaded from {motion_path}. Aborting.")
            return
        self.get_logger().info(f"Loaded {len(poses)} poses from {motion_path}.")
        self._play_poses(poses)


def main(args=None):
    rclpy.init(args=args)
    node = RunResetMotion()
    try:
        while rclpy.ok() and not node.finished:
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
