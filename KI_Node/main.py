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

PROMPT = "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm. Gib lieber kein Ergebnis zurück, wenn du den Tafelschwamm nicht findest."
SIDEWAYS_MOTION_TOLERANCE = 0.14
FAR_SIDEWAYS_MOTION_TOLERANCE = 0.4
FAR_WIDTH_TOLERANCE = 0.26
ROTATE_ANGLE_TOLERANCE = 8

IMAGE_TOPIC = "/camera/bottom/image_republished"
COMMAND_TOPIC = "/KI_Node/command"


class ImageProcessor(Node):
    """Subscribes to the camera image topic, locates the target in each frame
    and publishes a movement command as a String."""

    def __init__(self):
        super().__init__("KI_Node")
        self.image_sub = self.create_subscription(Image, IMAGE_TOPIC, self.on_image, 10)
        self.command_pub = self.create_publisher(String, COMMAND_TOPIC, 10)
        self.get_logger().info(
            f"Listening on '{IMAGE_TOPIC}', publishing commands on '{COMMAND_TOPIC}'."
        )

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
            self.publish_command("none")
            draw_result_on_image(pil_image, result, "none")
            return

        image_width = frame.shape[1]
        target = result["mean"]["x"]
        box_width = result["box_width"]
        angle = result["angle"]
        print(
            f"box_width={box_width}, image_width={image_width}, angle={angle}, target={target}"
        )
        if angle > ROTATE_ANGLE_TOLERANCE:
            self.publish_command("rotate_right", 1)
            draw_result_on_image(pil_image, result, "rotate_right")
        elif angle < -ROTATE_ANGLE_TOLERANCE:
            self.publish_command("rotate_left", 1)
            draw_result_on_image(pil_image, result, "rotate_left")
        elif target > image_width * (0.5 + SIDEWAYS_MOTION_TOLERANCE):
            self.publish_command("right", 2)
            draw_result_on_image(pil_image, result, "right")
        elif target < image_width * (0.5 - SIDEWAYS_MOTION_TOLERANCE):
            self.publish_command("left", 2)
            draw_result_on_image(pil_image, result, "left")
        # elif box_width < image_width * FAR_WIDTH_TOLERANCE:
        elif box_width < image_width * FAR_WIDTH_TOLERANCE:
            self.publish_command("forward", 4)
            draw_result_on_image(pil_image, result, "forward")
        else:
            self.publish_command("forward", 2)
            draw_result_on_image(pil_image, result, "center")

    def publish_command(self, command: str, value: float = None):
        payload = {"command": command, "duration": value, "timestamp": time.time()}
        self.command_pub.publish(String(data=json.dumps(payload)))
        self.get_logger().info(f"command: {command}, duration: {value}")


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
