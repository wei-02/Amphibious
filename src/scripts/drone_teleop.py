#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from geometry_msgs.msg import Twist
import sys, select, termios, tty

msg = """
Control quadcopter!
---------------------------
Moving around:
   w
a s d    (前后左右平移)
   x

r/f : 上升/下降
j/l : 左/右偏航
space key, k : force stop
q/z : increase/decrease max speeds by 10%
CTRL-C to quit
"""

moveBindings = {
    'w': (1, 0, 0, 0),   # 前
    'x': (-1, 0, 0, 0),  # 后
    'a': (0, 1, 0, 0),   # 左
    'd': (0, -1, 0, 0),  # 右
    'r': (0, 0, 1, 0),   # 上升
    'f': (0, 0, -1, 0),  # 下降
    'j': (0, 0, 0, 1),   # 左偏航
    'l': (0, 0, 0, -1),  # 右偏航
}

speedBindings = {
    'q': (1.1,),
    'z': (0.9,),
}

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = 1.0

def vels(speed):
    return "currently:\tspeed %s" % (speed)

if __name__ == "__main__":
    settings = termios.tcgetattr(sys.stdin)
    rospy.init_node('quadcopter_teleop')
    pub = rospy.Publisher('/amphibious/cmd_vel', Twist, queue_size=5)

    x = 0
    y = 0
    z = 0
    yaw = 0
    status = 0
    count = 0
    target_x = 0
    target_y = 0
    target_z = 0
    target_yaw = 0
    control_x = 0
    control_y = 0
    control_z = 0
    control_yaw = 0

    try:
        print(msg)
        print(vels(speed))
        while True:
            key = getKey()
            if key in moveBindings.keys():
                x, y, z, yaw = moveBindings[key]
                count = 0
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                print(vels(speed))
                if status == 14:
                    print(msg)
                status = (status + 1) % 15
            elif key == ' ' or key == 'k':
                x = 0
                y = 0
                z = 0
                yaw = 0
                control_x = 0
                control_y = 0
                control_z = 0
                control_yaw = 0
            else:
                count += 1
                if count > 4:
                    x = 0
                    y = 0
                    z = 0
                    yaw = 0
                if key == '\x03':
                    break

            target_x = speed * x
            target_y = speed * y
            target_z = speed * z
            target_yaw = speed * yaw

            # 平滑控制
            control_x = target_x
            control_y = target_y
            control_z = target_z
            control_yaw = target_yaw

            twist = Twist()
            twist.linear.x = control_x
            twist.linear.y = control_y
            twist.linear.z = control_z
            twist.angular.x = 0
            twist.angular.y = 0
            twist.angular.z = control_yaw
            pub.publish(twist)

    except Exception as e:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0
        twist.linear.y = 0
        twist.linear.z = 0
        twist.angular.x = 0
        twist.angular.y = 0
        twist.angular.z = 0
        pub.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)