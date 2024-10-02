#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
import sys, select, termios, tty

LINEAR_SCALE = 1000.0  # Adjust this scale for finer control
ANGULAR_SCALE = 1000.0
RATE_HZ = 10
MAX_LINEAR_SPEED = 500000000.0
MAX_ANGULAR_SPEED = 20000000.0

def get_key() -> str:
    try:
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key
    except Exception as e:
        rospy.logerr(f"Error reading from stdin: {e}")
        return ""

def calculate_velocities(linear_speed: float, angular_speed: float) -> dict:
    velocities = {
        'r1': linear_speed - angular_speed,
        'f1': linear_speed + angular_speed,
        'r2': linear_speed - angular_speed,
        'f2': linear_speed + angular_speed,
    }
    return velocities

def publish_velocities(pub_dict: dict, velocities: dict) -> None:
    for wheel, velocity in velocities.items():
        pub_dict[wheel].publish(velocity)

def teleop_controller() -> None:
    rospy.init_node('controller_spawner')

    pub_dict = {
        'r1': rospy.Publisher('/wheel_r1_joint_velocity_controller/command', Float64, queue_size=10),
        'f1': rospy.Publisher('/wheel_f1_joint_velocity_controller/command', Float64, queue_size=10),
        'r2': rospy.Publisher('/wheel_r2_joint_velocity_controller/command', Float64, queue_size=10),
        'f2': rospy.Publisher('/wheel_f2_joint_velocity_controller/command', Float64, queue_size=10),
    }

    linear_speed = 0.0
    angular_speed = 0.0

    rate = rospy.Rate(RATE_HZ)

    while not rospy.is_shutdown():
        key = get_key()
        if key == 'w':
            linear_speed += LINEAR_SCALE
        elif key == 's':
            linear_speed -= LINEAR_SCALE
        elif key == 'a':
            angular_speed += ANGULAR_SCALE
        elif key == 'd':
            angular_speed -= ANGULAR_SCALE
        elif key == ' ':
            linear_speed = 0.0
            angular_speed = 0.0
        elif key == '\x03':  # Ctrl+C to stop
            break

        # Apply limits
        linear_speed = max(min(linear_speed, MAX_LINEAR_SPEED), -MAX_LINEAR_SPEED)
        angular_speed = max(min(angular_speed, MAX_ANGULAR_SPEED), -MAX_ANGULAR_SPEED)

        velocities = calculate_velocities(linear_speed, angular_speed)
        publish_velocities(pub_dict, velocities)

        rate.sleep()

if __name__ == "__main__":
    settings = termios.tcgetattr(sys.stdin)
    try:
        teleop_controller()
    except rospy.ROSInterruptException:
        pass
    finally:
        zero_velocities = {'r1': 0.0, 'f1': 0.0, 'r2': 0.0, 'f2': 0.0}
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
