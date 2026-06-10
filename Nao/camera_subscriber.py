from datetime import datetime
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2


class NaoCameraCollector(Node):

    def __init__(self):
        super().__init__('nao_camera_collector')
        self.bridge = CvBridge()
        self.counter = 159
        self.camera_sub = self.create_subscription(Image, '/camera/bottom/image_raw', self.get_camera_data, 10)
        self.camera_pub = self.create_publisher(Image, '/camera/bottom/image_republished', 10)

    def get_camera_data(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        print(f"\r[camera] last image sent at {datetime.now().strftime('%H:%M:%S')}", end='', flush=True)
        out_msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        out_msg.header = msg.header
        self.camera_pub.publish(out_msg)

        return frame


def main(args=None):
    rclpy.init(args=args)
    node = NaoCameraCollector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
