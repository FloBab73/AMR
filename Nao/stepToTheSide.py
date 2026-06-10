import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

_node: Node | None = None
_pub = None


def _get_publisher():
    """Return a cached cmd_vel publisher, initialising ROS2 on first call."""
    global _node, _pub
    if _pub is None:
        if not rclpy.ok():
            rclpy.init()
        _node = Node('nao_move_node')
        _pub = _node.create_publisher(Twist, '/cmd_vel', 10)
        time.sleep(1.0)  # let publisher connect
    return _pub


def move_forward(speed: float = 0.1, duration: float = 2.0):
    """Move the robot forward at `speed` m/s for `duration` seconds."""
    pub = _get_publisher()
    msg = Twist()
    msg.linear.x = speed
    pub.publish(msg)
    time.sleep(duration)
    pub.publish(Twist())  # stop
    time.sleep(1.0)


def move_sideways(direction: str = 'left', speed: float = 0.1, duration: float = 2.0):
    """
    Move the robot sideways for `duration` seconds.

    direction : 'left' (positive Y) or 'right' (negative Y)
    speed     : magnitude in m/s
    """
    pub = _get_publisher()
    msg = Twist()
    msg.linear.y = speed if direction == 'left' else -speed
    pub.publish(msg)
    time.sleep(duration)
    pub.publish(Twist())  # stop
    time.sleep(1.0)


if __name__ == '__main__':
    move_forward(speed=0.1, duration=2.0)
    move_sideways(direction='left', speed=0.1, duration=2.0)
