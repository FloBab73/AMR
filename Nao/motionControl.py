import rclpy
from stepToTheSide import move_sideways, move_forward
from rclpy.node import Node
from std_msgs.msg import String

COMMAND_TOPIC = '/KI_Node/command'
NONE_THRESHOLD = 3


def stepToTheSide(direction: str):
    move_sideways(direction)
    print(f"move to the side {direction}")


def moveForward():
    move_forward()
    print(f"move forward")


def PickUpMotion():
    """Run the pick-up motion sequence."""
    print(f"pick Up")


class MotionControl(Node):
    """Central motion control unit. Listens to the commands published by
    KI_Node and dispatches the matching Nao motion."""

    def __init__(self):
        super().__init__('motion_control')
        self.none_count = 0
        self.command_sub = self.create_subscription(
            String, COMMAND_TOPIC, self.on_command, 10
        )
        self.get_logger().info(f"Listening for commands on '{COMMAND_TOPIC}'.")

    def on_command(self, msg: String):
        command = msg.data

        if command == "right":
            self.none_count = 0
            stepToTheSide("right")
        elif command == "left":
            self.none_count = 0
            stepToTheSide("left")
        elif command == "center":
            self.none_count = 0
            moveForward()
        elif command == "none":
            self.none_count += 1
            if self.none_count >= NONE_THRESHOLD:
                self.none_count = 0
                PickUpMotion()
        else:
            self.get_logger().warn(f"unknown command: {command}")


def main(args=None):
    rclpy.init(args=args)
    node = MotionControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
