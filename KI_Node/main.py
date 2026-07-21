import json
import time
from tkinter.constants import N

import numpy as np
import rclpy
from PIL import Image as PILImage
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from image_processing import draw_result_on_image
from model import detect_and_segment


def print_sponge_ascii(
    direction: str,
    target_x: float,
    image_width: int,
    box_width: float,
    tol_left: float,
    tol_right: float,
):
    """
    Print an ASCII art visualization of the sponge position.

    The diagram shows:
    - ### as the sponge (width proportional to box_width)
    - --- as the image width (320px scaled to terminal width)
    - | as the tolerance boundaries

    Image dimensions: 320x240, aspect ratio ~1.33:1
    Terminal representation: 40 chars wide, 10 lines tall (proportional)
    """
    TERMINAL_WIDTH = 40  # chars for the horizontal bar
    TERMINAL_HEIGHT = 10  # lines for vertical representation

    # Calculate positions scaled to terminal width
    left_tol_pos = int((0.5 + tol_left) * TERMINAL_WIDTH)
    right_tol_pos = int((0.5 + tol_right) * TERMINAL_WIDTH)
    sponge_center = int((target_x / image_width) * TERMINAL_WIDTH)

    # Calculate sponge width in terminal chars (proportional to box_width)
    sponge_width_chars = max(1, int((box_width / image_width) * TERMINAL_WIDTH))
    sponge_half_width = sponge_width_chars // 2

    # Calculate sponge left and right bounds
    sponge_left = sponge_center - sponge_half_width
    sponge_right = sponge_left + sponge_width_chars

    # Clamp to valid range
    sponge_left = max(0, sponge_left)
    sponge_right = min(TERMINAL_WIDTH, sponge_right)

    # Calculate vertical position (centered)
    sponge_vertical = TERMINAL_HEIGHT // 2

    print(f"\n  === Sponge Position: {direction.upper()} ===")
    print(f"  Target X: {target_x:.1f} / {image_width} px")
    print(f"  Box Width: {box_width:.1f} px ({sponge_width_chars} chars)")
    print()

    # Draw the ASCII art
    for row in range(TERMINAL_HEIGHT):
        line = [" "] * TERMINAL_WIDTH

        # Draw vertical tolerance lines on every row
        if 0 <= left_tol_pos < TERMINAL_WIDTH:
            line[left_tol_pos] = "|"
        if 0 <= right_tol_pos < TERMINAL_WIDTH:
            line[right_tol_pos] = "|"

        # Draw the sponge marker (width based on box_width) on sponge rows
        if sponge_vertical - 1 <= row <= sponge_vertical + 1:
            for pos in range(sponge_left, sponge_right):
                if 0 <= pos < TERMINAL_WIDTH:
                    line[pos] = "#"

        print("  " + "".join(line))

    # Draw the horizontal bar (image width representation)
    bar_line = ["-"] * TERMINAL_WIDTH
    if 0 <= left_tol_pos < TERMINAL_WIDTH:
        bar_line[left_tol_pos] = "|"
    if 0 <= right_tol_pos < TERMINAL_WIDTH:
        bar_line[right_tol_pos] = "|"
    print("  " + "".join(bar_line))
    print(f"  0{' ' * (TERMINAL_WIDTH - 7)}320px")
    print()


PROMPT = "Ein orange-brauner Tafelschwamm steht auf einer Oberfläche, suche nur den orange-braunen Tafelschwamm"


IMAGE_TOPIC = "/camera/bottom/image_republished"
COMMAND_TOPIC = "/KI_Node/command"

DEFAULT_MOTION_CONFIG = {
    "SIDEWAYS_MOTION_TOLERANCE_LEFT": -0.01,
    "SIDEWAYS_MOTION_TOLERANCE_RIGHT": 0.18,
    "FAR_SIDEWAYS_MOTION_TOLERANCE": 0.4,
    "FAR_WIDTH_TOLERANCE": 0.2,
    "ROTATE_ANGLE_TOLERANCE": 4,
    "ROTATION_DURATION": 0.7,
    "SIDEWAYS_DURATION": 2,
    "FAR_FORWARD_DURATION": 2,
    "FORWARD_DURATION": 1.5,
}

LOOK_DOWN_MOTION_CONFIG = {
    "SIDEWAYS_MOTION_TOLERANCE_LEFT": -0.11,
    "SIDEWAYS_MOTION_TOLERANCE_RIGHT": -0.16,
    "FAR_SIDEWAYS_MOTION_TOLERANCE": 0.4,
    "FAR_WIDTH_TOLERANCE": 0.26,
    "ROTATE_ANGLE_TOLERANCE": 10,
    "ROTATION_DURATION": 0.7,
    "SIDEWAYS_DURATION": 0.8,
    "FAR_FORWARD_DURATION": 0.8,
    "FORWARD_DURATION": 0.8,
}


class ImageProcessor(Node):
    """Subscribes to the camera image topic, locates the target in each frame
    and publishes a movement command as a String."""

    SIDEWAYS_MOTION_TOLERANCE_LEFT = None
    SIDEWAYS_MOTION_TOLERANCE_RIGHT = None
    FAR_SIDEWAYS_MOTION_TOLERANCE = None
    FAR_WIDTH_TOLERANCE = None
    ROTATE_ANGLE_TOLERANCE = None
    ROTATION_DURATION = None
    SIDEWAYS_DURATION = None
    FAR_FORWARD_DURATION = None
    FORWARD_DURATION = None

    def __init__(self):
        super().__init__("KI_Node")
        self.image_sub = self.create_subscription(Image, IMAGE_TOPIC, self.on_image, 10)
        self.command_pub = self.create_publisher(String, COMMAND_TOPIC, 10)
        self.get_logger().info(
            f"Listening on '{IMAGE_TOPIC}', publishing commands on '{COMMAND_TOPIC}'."
        )
        self.none_count = 0
        self.looking_down = False
        self._apply_config(DEFAULT_MOTION_CONFIG)

    def _apply_config(self, config: dict):
        """Apply a motion config dict to instance attributes."""
        for key, value in config.items():
            setattr(self, key, value)

    def on_image(self, msg: Image):
        # self.publish_command(f"got image: {msg}")
        # Decode BGR8 bytes directly — no cv_bridge required
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(
            msg.height, msg.width, 3
        )

        # BGR -> RGB, then wrap in PIL
        pil_image = PILImage.fromarray(frame[:, :, ::-1])

        result = detect_and_segment(pil_image, PROMPT)
        if not result:
            self.prepare_command("none")
            draw_result_on_image(pil_image, result, "none")
            return

        image_width = frame.shape[1]
        target = result["mean"]["x"]
        box_width = result["box_width"]
        angle = result["angle"]
        print(
            f"box_width={box_width}, image_width={image_width}, angle={angle}, target={target}"
        )
        if box_width >= image_width * 0.9:
            self.prepare_command("none")
            draw_result_on_image(pil_image, result, "big")
        elif angle > self.ROTATE_ANGLE_TOLERANCE:
            self.prepare_command("rotate_right", self.ROTATION_DURATION)
            draw_result_on_image(pil_image, result, "rotate_right")
        elif angle < -self.ROTATE_ANGLE_TOLERANCE:
            self.prepare_command("rotate_left", self.ROTATION_DURATION)
            draw_result_on_image(pil_image, result, "rotate_left")
        elif target > image_width * (0.5 + self.SIDEWAYS_MOTION_TOLERANCE_RIGHT):
            self.prepare_command("right", self.SIDEWAYS_DURATION)
            draw_result_on_image(pil_image, result, "right")
            print_sponge_ascii(
                "right",
                target,
                image_width,
                box_width,
                self.SIDEWAYS_MOTION_TOLERANCE_LEFT,
                self.SIDEWAYS_MOTION_TOLERANCE_RIGHT,
            )
        elif target < image_width * (0.5 + self.SIDEWAYS_MOTION_TOLERANCE_LEFT):
            self.prepare_command("left", self.SIDEWAYS_DURATION)
            draw_result_on_image(pil_image, result, "left")
            print_sponge_ascii(
                "left",
                target,
                image_width,
                box_width,
                self.SIDEWAYS_MOTION_TOLERANCE_LEFT,
                self.SIDEWAYS_MOTION_TOLERANCE_RIGHT,
            )
        # elif box_width < image_width * FAR_WIDTH_TOLERANCE:
        elif box_width < image_width * self.FAR_WIDTH_TOLERANCE:
            self.prepare_command("forward", self.FAR_FORWARD_DURATION)
            draw_result_on_image(pil_image, result, "forward")
        else:
            self.prepare_command("forward", self.FORWARD_DURATION)
            draw_result_on_image(pil_image, result, "center")

    def publish_command(self, command: str, value: float = None):
        payload = {"command": command, "duration": value, "timestamp": time.time()}
        self.command_pub.publish(String(data=json.dumps(payload)))
        self.get_logger().info(f"command: {command}, duration: {value}")

    def prepare_command(self, command: str, value: float = None):

        if command != "none":
            self.none_count = 0
        else:
            self.none_count += 1

        if self.none_count >= 4:
            self.publish_command("look_down")
            self._apply_config(LOOK_DOWN_MOTION_CONFIG)
            self.none_count = 0
        else:
            # self.SIDEWAYS_MOTION_TOLERANCE_LEFT = -0.15
            # self.SIDEWAYS_MOTION_TOLERANCE_RIGHT = 0.15
            # self.FAR_SIDEWAYS_MOTION_TOLERANCE = 0.4
            # self.FAR_WIDTH_TOLERANCE = 0.26
            # self.ROTATE_ANGLE_TOLERANCE = 8
            # self.ROTATION_DURATION = 0.7
            # self.SIDEWAYS_DURATION = 1.5
            # self.FAR_FORWARD_DURATION = 3
            # self.FORWARD_DURATION = 2
            self.publish_command(command, value)


def main(args=None):
    rclpy.init(args=args)
    node = ImageProcessor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
