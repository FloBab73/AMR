import json
import time

import numpy as np
import rclpy
from PIL import Image as PILImage
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String

from image_processing import draw_result_on_image
from model import detect_and_segment

PROMPT = "Ein orange-brauner Tafelschwamm steht auf einer Oberfläche, suche nur den orange-braunen Tafelschwamm"


IMAGE_TOPIC = "/camera/bottom/image_republished"
COMMAND_TOPIC = "/KI_Node/command"


class ImageProcessor(Node):
    """Subscribes to the camera image topic, locates the target in each frame
    and publishes a movement command as a String."""

    SIDEWAYS_MOTION_TOLERANCE_LEFT = 0.03
    SIDEWAYS_MOTION_TOLERANCE_RIGHT = 0.16
    FAR_SIDEWAYS_MOTION_TOLERANCE = 0.4
    FAR_WIDTH_TOLERANCE = 0.2
    ROTATE_ANGLE_TOLERANCE = 4
    ROTATION_DURATION = 0.7
    SIDEWAYS_DURATION = 2
    FAR_FORWARD_DURATION = 2
    FORWARD_DURATION = 2

    def __init__(self):
        super().__init__("KI_Node")
        self.image_sub = self.create_subscription(Image, IMAGE_TOPIC, self.on_image, 10)
        self.command_pub = self.create_publisher(String, COMMAND_TOPIC, 10)
        self.get_logger().info(
            f"Listening on '{IMAGE_TOPIC}', publishing commands on '{COMMAND_TOPIC}'."
        )
        self.none_count = 0
        self.looking_down = False

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
        elif target < image_width * (0.5 + self.SIDEWAYS_MOTION_TOLERANCE_LEFT):
            self.prepare_command("left", self.SIDEWAYS_DURATION)
            draw_result_on_image(pil_image, result, "left")
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
            self.SIDEWAYS_MOTION_TOLERANCE_LEFT = -0.9
            self.SIDEWAYS_MOTION_TOLERANCE_RIGHT = -0.14
            self.FAR_SIDEWAYS_MOTION_TOLERANCE = 0.4
            self.FAR_WIDTH_TOLERANCE = 0.26
            self.ROTATE_ANGLE_TOLERANCE = 10
            self.ROTATION_DURATION = 0.7
            self.SIDEWAYS_DURATION = 0.8
            self.FAR_FORWARD_DURATION = 0.8
            self.FORWARD_DURATION = 0.8
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
