from typing import Callable

import rclpy
from naoqi_bridge_msgs.msg import Bumper
from rclpy.node import Node

BUMPER_TOPIC = "/bumper"


class BumperListener(Node):
    """Listens to the Nao bumper topic and keeps track of the latest state.

    Use :meth:`get_bumper` to read the most recently received bumper value.
    An optional callback can be supplied that is executed whenever a bumper
    is pressed.
    """

    def __init__(self, on_pressed: Callable[[Bumper], None] | None = None):
        super().__init__("bumper_listener")
        self.current_value: Bumper | None = None
        self.on_pressed = on_pressed
        self.bumper_sub = self.create_subscription(
            Bumper, BUMPER_TOPIC, self.on_bumper, 10
        )
        self.get_logger().info(f"Listening for bumper events on '{BUMPER_TOPIC}'.")

    def on_bumper(self, msg: Bumper):
        """Store the latest bumper message and fire the callback on a press."""
        self.current_value = msg

        if msg.state == Bumper.STATE_PRESSED and self.on_pressed is not None:
            self.on_pressed(msg)

def main(args=None):
    rclpy.init(args=args)
    node = BumperListener(on_pressed=handle_press)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


def handle_press(msg):
    print(f"Bumper {msg.bumper} was pressed")

if __name__ == "__main__":
    main()
