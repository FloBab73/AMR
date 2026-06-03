import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
import os
import re
from naoqi_bridge_msgs.msg import JointAnglesWithSpeed


MIN_DURATION = 0.05  # minimum seconds to dwell on each keyframe

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

    def __init__(self, motion_file: str, pose_speed: float = 0.15, motion_speed: float = 0.3):
        super().__init__('nao_command_publisher')

        self.pose_speed   = pose_speed    # hardware joint speed fraction (0–1)
        self.motion_speed = motion_speed  # playback speed in rad/s — governs adaptive timing

        # Publishers
        self.posture_pub = self.create_publisher(String,               '/cmd_pose',     10)
        self.joint_pub   = self.create_publisher(JointAnglesWithSpeed, '/joint_angles', 10)

        # Wait until the bridge has connected to both topics (max 10 s)
        self.get_logger().info("Waiting for naoqi_bridge subscribers...")
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if (self.joint_pub.get_subscription_count() > 0 and
                    self.posture_pub.get_subscription_count() > 0):
                break
            time.sleep(0.2)
        if self.joint_pub.get_subscription_count() == 0:
            self.get_logger().warn("No subscriber on /joint_angles after 10 s — messages may be lost.")
        else:
            self.get_logger().info("Bridge connected.")

        # Load motion data
        self.poses = parse_motion_file(motion_file)
        if not self.poses:
            self.get_logger().error(f"No poses loaded from '{motion_file}'. Aborting.")
            return

        self.get_logger().info(
            f"Loaded {len(self.poses)} poses from '{motion_file}'."
        )

        self.start_motion()

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def send_pose(self, joints: list, angles: list, speed: float | None = None):
        msg = JointAnglesWithSpeed()
        msg.joint_names  = joints
        msg.joint_angles = angles
        msg.speed        = speed if speed is not None else self.pose_speed
        msg.relative     = False
        self.joint_pub.publish(msg)

    # ------------------------------------------------------------------
    # Motion sequences
    # ------------------------------------------------------------------

    def play_motion(self):
        prev_map: dict[str, float] = {}

        self.get_logger().info(
            f"Starting motion playback: {len(self.poses)} poses, "
            f"motion_speed={self.motion_speed} rad/s"
        )

        for idx, pose in enumerate(self.poses):
            joints  = pose['joints']
            targets = pose['angles']
            starts  = [prev_map.get(j, t) for j, t in zip(joints, targets)]

            max_delta = max((abs(t - s) for s, t in zip(starts, targets)), default=0.0)
            duration  = max(max_delta / self.motion_speed, MIN_DURATION)

            self.get_logger().info(
                f"  Pose {idx+1}/{len(self.poses)} — {len(joints)} joints, "
                f"max_delta={max_delta:.3f} rad, duration={duration:.2f}s"
            )

            self.send_pose(joints, targets)
            time.sleep(duration)

            for j, t in zip(joints, targets):
                prev_map[j] = t

        self.get_logger().info("Motion playback complete.")

    def start_motion(self):
        self.play_motion()

        # Give DDS time to transmit the final pose before the node is torn down
        time.sleep(2.0)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(args=None):
    rclpy.init(args=args)

    # Path to the recorded motion file (adjust as needed)
    script_dir   = os.path.dirname(os.path.abspath(__file__))
    motion_file  = os.path.join(script_dir, 'sitDownMotion.md')

    # Tunable parameters
    POSE_SPEED   = 0.15  # hardware joint speed fraction (0.0–1.0) — lower = smoother tracking
    MOTION_SPEED = 0.2   # playback speed in rad/s — lower = more dwell time per keyframe

    node = NaoCommandPublisher(
        motion_file=motion_file,
        pose_speed=POSE_SPEED,
        motion_speed=MOTION_SPEED,
    )
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()