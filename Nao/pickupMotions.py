import rclpy
import time

from doMotion import NaoCommandPublisher, Motion

# ---------------------------------------------------------------------------
# Lazy ROS2 init (same pattern as stepToTheSide.py)
# ---------------------------------------------------------------------------

_rclpy_ready = False


def _ensure_rclpy():
    """Initialise rclpy on the first call; no-op afterwards."""
    global _rclpy_ready
    if not _rclpy_ready or not rclpy.ok():
        rclpy.init()
        _rclpy_ready = True
        time.sleep(0.5)  # let ROS2 infrastructure settle


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _run_motion(motion: Motion, pose_speed: float = 0.15, motion_speed: float = 0.2):
    """
    Execute a single motion end-to-end:
      1. Ensure ROS2 is running.
      2. Create a NaoCommandPublisher, which loads and plays the motion.
      3. Tear down the node when playback is finished.
    """
    _ensure_rclpy()
    node = NaoCommandPublisher(
        motion_file=motion.path,
        pose_speed=pose_speed,
        motion_speed=motion_speed,
    )
    node.destroy_node()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def pickup():
    """Pick up an object from the floor using the recorded pick-up motion."""
    _run_motion(Motion.pickUp)


def sitDown():
    """Sit the robot down using the recorded sit-down motion."""
    _run_motion(Motion.sitDown)


def standUp():
    """Stand the robot up using the recorded stand-up motion."""
    _run_motion(Motion.standUp)


# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    standUp()
    sitDown()
    pickup()
    rclpy.shutdown()
