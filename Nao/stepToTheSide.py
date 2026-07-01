import time

from geometry_msgs.msg import Twist
from rclpy.node import Node

SLEEP_DURATION = 0.3


def move_forward(node: Node, speed: float = 0.1, duration: float = 2.0):
    """Move the robot forward at `speed` m/s for `duration` seconds."""
    msg = Twist()
    msg.linear.x = speed
    publisher = node.create_publisher(Twist, "/cmd_vel", 10)
    publisher.publish(msg)
    time.sleep(duration)
    publisher.publish(Twist())  # stop
    time.sleep(SLEEP_DURATION)


def move_sideways(
    node: Node,
    direction: str = "left",
    speed: float = 0.1,
    duration: float = 2.0,
):
    """
    Move the robot sideways for `duration` seconds.

    direction : 'left' (positive Y) or 'right' (negative Y)
    speed     : magnitude in m/s
    """
    pub = node.create_publisher(Twist, "/cmd_vel", 10)
    msg = Twist()
    msg.linear.y = speed if direction == "left" else -speed
    pub.publish(msg)
    time.sleep(duration)
    pub.publish(Twist())  # stop
    time.sleep(SLEEP_DURATION)


def rotate(
    node: Node,
    clockwise: bool = True,
    speed: float = 0.5,
    duration: float = 0.6,
):
    """
    Rotate the robot on the spot for `duration` seconds.

    clockwise : True to turn clockwise, False for counter-clockwise
    speed     : angular magnitude in rad/s
    """
    pub = node.create_publisher(Twist, "/cmd_vel", 10)
    msg = Twist()
    msg.angular.z = -speed if clockwise else speed
    pub.publish(msg)
    time.sleep(duration)
    pub.publish(Twist())  # stop
    time.sleep(SLEEP_DURATION + 1)
