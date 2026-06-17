import time

from geometry_msgs.msg import Twist
from rclpy.node import Node


def move_forward(node: Node, speed: float = 0.1, duration: float = 2.0):
    """Move the robot forward at `speed` m/s for `duration` seconds."""
    msg = Twist()
    msg.linear.x = speed
    publisher = node.create_publisher(Twist, "/cmd_vel", 10)
    publisher.publish(msg)
    time.sleep(duration)
    publisher.publish(Twist())  # stop
    time.sleep(1.0)


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
    time.sleep(1.0)
