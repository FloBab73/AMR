import argparse
import json
import os
import re
import time
from enum import Enum

import rclpy
from naoqi_bridge_msgs.msg import Bumper, JointAnglesWithSpeed
from rclpy.node import Node
from std_msgs.msg import String
from stepToTheSide import move_forward, move_sideways, rotate

BUMPER_TOPIC = "/bumper"
COMMAND_TOPIC = "/KI_Node/command"
NONE_THRESHOLD = 3
MIN_DURATION = 0.05  # minimum seconds to dwell on each keyframe


class Motion(Enum):
    """Available motions mapped to their recorded motion files."""

    sitDown = "./motionFiles/sitDownMotion.md"
    standUp = "./motionFiles/standUpMotion.md"
    pickUp = "./motionFiles/pickUpMotion.md"

    @property
    def path(self) -> str:
        """Absolute path to this motion's file, resolved next to this script."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, self.value)

    @classmethod
    def from_name(cls, name: str) -> "Motion":
        """argparse type converter: map a name to a Motion with a clean error."""
        try:
            return cls[name]
        except KeyError:
            choices = ", ".join(m.name for m in cls)
            raise argparse.ArgumentTypeError(
                f"invalid motion '{name}' (choose from {choices})"
            )


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
# MotionControl Node
# ---------------------------------------------------------------------------


class MotionControl(Node):
    """Central motion control unit. Listens to the commands published by
    KI_Node and dispatches the matching Nao motion."""

    """Persistent ROS2 node that owns the /joint_angles publisher.
    Initialise once, then call play(motion) as many times as needed."""

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def send_pose(self, joints: list, angles: list, speed: float | None = None):
        msg = JointAnglesWithSpeed()
        msg.joint_names = joints
        msg.joint_angles = angles
        msg.speed = speed if speed is not None else self.pose_speed
        msg.relative = False
        self.joint_pub.publish(msg)

    # ------------------------------------------------------------------
    # Motion playback
    # ------------------------------------------------------------------

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
        """Load and play the given motion. Reuses the existing node/publisher."""
        poses = parse_motion_file(motion.path)
        if not poses:
            self.get_logger().error(f"No poses loaded for '{motion.name}'. Aborting.")
            return
        self.get_logger().info(f"Loaded {len(poses)} poses for '{motion.name}'.")
        self._play_poses(poses)

    def __init__(self, pose_speed: float = 0.15, motion_speed: float = 0.2):
        super().__init__("motion_control")
        self.none_count = 0
        self.command_count = 0
        self.bumper = False
        # Single shared publisher node — reused for every motion command.
        # self.nao_pub = NaoCommandPublisher(pose_speed=0.15, motion_speed=0.2)

        self.command_sub = self.create_subscription(
            String, COMMAND_TOPIC, self.on_command, 10
        )
        self.get_logger().info(f"Listening for commands on '{COMMAND_TOPIC}'.")

        self.pose_speed = pose_speed  # hardware joint speed fraction (0–1)
        self.motion_speed = motion_speed  # playback speed in rad/s

        self.posture_pub = self.create_publisher(String, "/cmd_pose", 10)
        self.joint_pub = self.create_publisher(
            JointAnglesWithSpeed, "/joint_angles", 10
        )

        # Wait for the bridge to subscribe — done once at startup.
        self.get_logger().info("Waiting for a subscriber on /joint_angles...")
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if self.joint_pub.get_subscription_count() > 0:
                break
            time.sleep(0.2)
        if self.joint_pub.get_subscription_count() == 0:
            self.get_logger().warn(
                "No subscriber on /joint_angles after 10 s — is naoqi_driver running "
                "with the right nao_ip, and do both terminals share ROS_DOMAIN_ID / RMW? "
                "Messages will be lost and the robot will not move."
            )
        else:
            self.get_logger().info("Bridge connected.")

        self.current_value: Bumper | None = None
        self.on_pressed = self.on_bumper_press
        self.bumper_sub = self.create_subscription(
            Bumper, BUMPER_TOPIC, self.on_bumper_press, 10
        )
        self.get_logger().info(f"Listening for bumper events on '{BUMPER_TOPIC}'.")

        move_forward(self)
        # self.play(Motion.sitDown)

    def on_bumper_press(self, msg):
        print(f"Bumper {msg.bumper} was pressed in motion control")
        self.bumper = True

    def on_command(self, msg: String):

        if self.bumper:
            self.bumper = False
            self.play(Motion.sitDown)
            self.play(Motion.pickUp)
            self.play(Motion.standUp)
            return

        try:
            data = json.loads(msg.data)
            command = data["command"]
            duration = data["duration"]

            # if self.command_count == 3:
            #     rotate(node=self, clockwise=False, duration=duration)
            #     self.command_count = 0

            if command == "right":
                self.none_count = 0
                move_sideways(self, "right", duration=duration)
            elif command == "left":
                self.none_count = 0
                move_sideways(self, "left", duration=duration)
            elif command == "rotate_right":
                self.none_count = 0
                rotate(node=self, clockwise=True, duration=duration)
            elif command == "rotate_left":
                self.none_count = 0
                rotate(node=self, clockwise=False, duration=duration)
            elif command == "forward":
                self.none_count = 0
                move_forward(self, duration=duration)
            elif command == "none":
                self.none_count += 1
                if self.none_count >= NONE_THRESHOLD:
                    self.none_count = 0
                    # self.nao_pub.play(Motion.pickUp)
                    self.play(Motion.pickUp)
            else:
                self.get_logger().warn(f"unknown command: {command}")

            self.command_count = self.command_count + 1

        except (json.JSONDecodeError, KeyError) as e:
            self.get_logger().error(f"Failed to parse command message: {e}")
            return


def main(args=None):
    rclpy.init(args=args)
    node = MotionControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
