import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import time
import os
import re
from naoqi_bridge_msgs.msg import JointAnglesWithSpeed


INTERPOLATION_HZ = 25    # publish rate during interpolation
MIN_DURATION     = 0.15  # minimum seconds per pose transition

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_motion_file(filepath: str) -> list[dict]:
    """
    Parse a YAML-style motion file that contains repeated blocks of:

        name:
        - JointName
        ...
        position:
        - 0.123
        ...

    Returns a list of dicts: [{'joints': [...], 'angles': [...]}, ...]
    """
    with open(filepath, 'r') as f:
        content = f.read()

    poses = []
    # Split on blank lines to get individual pose blocks
    blocks = re.split(r'\n\s*\n', content.strip())

    i = 0
    while i < len(blocks):
        block = blocks[i].strip()
        if not block:
            i += 1
            continue

        # A pose may span two consecutive blocks: one for 'name:' and one for 'position:'
        # but often they are in the same block. Handle both.
        combined = block
        if 'name:' in block and 'position:' not in block:
            # position block is next
            if i + 1 < len(blocks):
                combined = block + '\n' + blocks[i + 1]
                i += 1

        if 'name:' in combined and 'position:' in combined:
            names_section = re.search(r'name:\s*((?:- .+\n?)+)', combined)
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

                if len(joints) == len(angles) and len(joints) > 0:
                    poses.append({'joints': joints, 'angles': angles})

        i += 1

    return poses


# ---------------------------------------------------------------------------
# ROS2 Node
# ---------------------------------------------------------------------------

class NaoCommandPublisher(Node):

    def __init__(self, motion_file: str, pose_speed: float = 0.3, motion_speed: float = 0.5):
        super().__init__('nao_command_publisher')

        self.pose_speed   = pose_speed    # hardware joint speed fraction (0–1)
        self.motion_speed = motion_speed  # playback speed in rad/s — governs adaptive timing

        # Publishers
        self.cmd_vel_pub  = self.create_publisher(Twist,              '/cmd_vel',      10)
        self.posture_pub  = self.create_publisher(String,             '/cmd_pose',     10)
        self.joint_pub    = self.create_publisher(JointAnglesWithSpeed, '/joint_angles', 10)

        # Give publishers time to connect
        time.sleep(1.0)

        # Load motion data
        self.poses = parse_motion_file(motion_file)
        if not self.poses:
            self.get_logger().error(f"No poses loaded from '{motion_file}'. Aborting.")
            return

        self.get_logger().info(
            f"Loaded {len(self.poses)} poses from '{motion_file}'."
        )

        self.publish_commands()

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def send_pose(self, joints: list, angles: list, speed: float | None = None):
        """Send a single pose (joint names + angles) to the robot."""
        msg = JointAnglesWithSpeed()
        msg.joint_names  = joints
        msg.joint_angles = angles
        msg.speed        = speed if speed is not None else self.pose_speed
        msg.relative     = False
        self.joint_pub.publish(msg)

    def move_forward(self, speed: float = 0.1, duration: float = 2.0):
        move_msg = Twist()
        move_msg.linear.x = speed
        self.cmd_vel_pub.publish(move_msg)
        self.get_logger().info("Moving forward...")
        time.sleep(duration)
        self.cmd_vel_pub.publish(Twist())
        self.get_logger().info("Stopped forward movement.")
        time.sleep(1.0)

    def move_sideways(self, speed: float = 0.1, duration: float = 2.0):
        move_msg = Twist()
        move_msg.linear.y = speed
        self.cmd_vel_pub.publish(move_msg)
        self.get_logger().info("Moving sideways...")
        time.sleep(duration)
        self.cmd_vel_pub.publish(Twist())
        self.get_logger().info("Stopped sideways movement.")
        time.sleep(1.0)

    # ------------------------------------------------------------------
    # Motion sequences
    # ------------------------------------------------------------------

    def play_motion(self):
        interval = 1.0 / INTERPOLATION_HZ
        prev_map: dict[str, float] = {}  # joint -> last commanded angle

        self.get_logger().info(
            f"Starting motion playback: {len(self.poses)} poses, "
            f"motion_speed={self.motion_speed} rad/s, interp={INTERPOLATION_HZ} Hz"
        )

        for idx, pose in enumerate(self.poses):
            joints  = pose['joints']
            targets = pose['angles']
            starts  = [prev_map.get(j, t) for j, t in zip(joints, targets)]

            max_delta = max((abs(t - s) for s, t in zip(starts, targets)), default=0.0)
            duration  = max(max_delta / self.motion_speed, MIN_DURATION)
            n_steps   = max(int(duration / interval), 1)

            self.get_logger().info(
                f"  Pose {idx+1}/{len(self.poses)} — {len(joints)} joints, "
                f"max_delta={max_delta:.3f} rad, duration={duration:.2f}s"
            )

            for step in range(1, n_steps + 1):
                alpha  = (1.0 - math.cos(math.pi * step / n_steps)) / 2.0
                interp = [s + alpha * (t - s) for s, t in zip(starts, targets)]
                self.send_pose(joints, interp)
                time.sleep(interval)

            for j, t in zip(joints, targets):
                prev_map[j] = t

        self.get_logger().info("Motion playback complete.")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def publish_commands(self):
        # Play back all recorded poses from the motion file
        self.play_motion()


        # Uncomment for locomotion:
        # self.move_forward(speed=0.08, duration=2.0)
        # self.move_sideways(speed=0.08, duration=5.0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args=None):
    rclpy.init(args=args)

    # Path to the recorded motion file (adjust as needed)
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    motion_file  = os.path.join(script_dir, 'sitDownMotion.md')

    # Tunable parameters
    POSE_SPEED   = 0.3  # hardware joint speed fraction (0.0–1.0)
    MOTION_SPEED = 0.5  # playback speed in rad/s — lower = slower & smoother

    node = NaoCommandPublisher(
        motion_file=motion_file,
        pose_speed=POSE_SPEED,
        motion_speed=MOTION_SPEED,
    )
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()