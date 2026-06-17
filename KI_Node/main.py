import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
import numpy as np
from PIL import Image as PILImage

from model import detect_and_segment
from image_processing import draw_result_on_image

PROMPT = "Ein Tafelschwamm steht auf einer Oberfläche, suche den Tafelschwamm"
SIDEWAYS_MOTION_TOLERANCE = 0.1

IMAGE_TOPIC = '/camera/bottom/image_republished'
COMMAND_TOPIC = '/KI_Node/command'


class ImageProcessor(Node):
    """Subscribes to the camera image topic, locates the target in each frame
    and publishes a movement command as a String."""

    def __init__(self):
        super().__init__('KI_Node')
        self.image_sub = self.create_subscription(
            Image, IMAGE_TOPIC, self.on_image, 10
        )
        self.command_pub = self.create_publisher(String, COMMAND_TOPIC, 10)
        self.get_logger().info(
            f"Listening on '{IMAGE_TOPIC}', publishing commands on '{COMMAND_TOPIC}'."
        )

    def on_image(self, msg: Image):
        # self.publish_command(f"got image: {msg}")
        # Decode BGR8 bytes directly — no cv_bridge required
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)

        # BGR -> RGB, then wrap in PIL
        pil_image = PILImage.fromarray(frame[:, :, ::-1])
        result = detect_and_segment(pil_image, PROMPT)
        draw_result_on_image(pil_image, result)

        if not result:
            self.publish_command("none")
            return

        image_width = frame.shape[1]
        target = result["mean"]["x"]

        if target > image_width * (0.5 + SIDEWAYS_MOTION_TOLERANCE):
            self.publish_command("right")
        elif target < image_width * (0.5 - SIDEWAYS_MOTION_TOLERANCE):
            self.publish_command("left")
        else:
            self.publish_command("center")

    def publish_command(self, command: str):
        print(command)
        self.command_pub.publish(String(data=command))
        self.get_logger().info(f"command: {command}")


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
