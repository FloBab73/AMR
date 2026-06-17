import time

import rclpy
from naoqi_bridge_msgs.msg import JointAnglesWithSpeed
from rclpy.node import Node
from sensor_msgs.msg import JointState

from motionControl import MIN_DURATION, Motion, parse_motion_file
from stepToTheSide import move_forward

JOINT_STATES_TOPIC = "/joint_states"
NUM_SAMPLES = 3  # how many /joint_states messages to capture


def format_pose_block(names: list[str], positions: list[float]) -> str:
    """Render a single keyframe in the same YAML-style block layout that
    parse_motion_file expects (a 'name:' list followed by a 'position:' list)."""
    lines = ["name:"]
    lines += [f"- {n}" for n in names]
    lines.append("position:")
    lines += [f"- {p}" for p in positions]
    return "\n".join(lines)


class ResetToStanding(Node):
    """Capture the robot's current pose from /joint_states, prepend it to the
    sit-down motion file as the starting keyframes, then play the motion so the
    transition begins smoothly from wherever the robot currently is."""

    def __init__(self, pose_speed: float = 0.15, motion_speed: float = 0.2):
        super().__init__("reset_to_standing")
        self.pose_speed = pose_speed  # hardware joint speed fraction (0–1)
        self.motion_speed = motion_speed  # playback speed in rad/s
        self.samples: list[tuple[list[str], list[float]]] = []
        self.finished = False
        self._handled = False

        self.joint_pub = self.create_publisher(
            JointAnglesWithSpeed, "/joint_angles", 10
        )
        self.joint_state_sub = self.create_subscription(
            JointState, JOINT_STATES_TOPIC, self.on_joint_state, 10
        )
        self.get_logger().info(
            f"Listening for {NUM_SAMPLES} samples on '{JOINT_STATES_TOPIC}'..."
        )

        # Take one step forward before capturing the current pose.
        move_forward(self)

    # ------------------------------------------------------------------
    # Sampling
    # ------------------------------------------------------------------

    def on_joint_state(self, msg: JointState):
        if self._handled:
            return

        self.samples.append((list(msg.name), list(msg.position)))
        self.get_logger().info(f"Captured sample {len(self.samples)}/{NUM_SAMPLES}.")

        if len(self.samples) >= NUM_SAMPLES:
            self._handled = True
            self.write_motion_file()
            self.play(Motion.sitDown)
            self.finished = True

    def write_motion_file(self):
        """Prepend the captured poses as the first keyframes of the motion file."""
        path = Motion.sitDown.path
        captured = "\n\n".join(
            format_pose_block(names, positions) for names, positions in self.samples
        )
        with open(path, "r") as f:
            existing = f.read()
        with open(path, "w") as f:
            f.write(captured + "\n\n" + existing)
        self.get_logger().info(f"Prepended {len(self.samples)} captured pose(s) to {path}.")

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

    def play(self, motion: Motion):
        """Load and play the given motion, waiting for the bridge first."""
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

        poses = parse_motion_file(motion.path)
        if not poses:
            self.get_logger().error(f"No poses loaded for '{motion.name}'. Aborting.")
            return
        self.get_logger().info(f"Loaded {len(poses)} poses for '{motion.name}'.")
        self._play_poses(poses)


def main(args=None):
    rclpy.init(args=args)
    node = ResetToStanding()
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
