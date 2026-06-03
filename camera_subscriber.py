import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2


class NaoCameraCollector(Node):

    def __init__(self):
        super().__init__('nao_command_publisher')
        self.bridge = CvBridge()
        self.counter = 159
        self.camera_sub = self.create_subscription(Image, '/camera/bottom/image_raw', self.get_camera_data, 10)
        

    def get_camera_data(self, msg):

        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )
        # print("jetzt")
        # imageName: str = f"./images/image_{self.counter}.jpg"
        # cv2.imwrite(imageName, frame)
        # self.counter = self.counter + 1
        return frame




def main(args=None):
    rclpy.init(args=args)
    node = NaoCameraCollector()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
