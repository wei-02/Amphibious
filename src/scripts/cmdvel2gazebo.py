#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist

class CmdVel2Gazebo:
    def __init__(self):
        rospy.init_node('cmdvel2gazebo', anonymous=True)
        rospy.Subscriber('/amphibious/cmd_vel', Twist, self.callback, queue_size=1)

        self.pub_fl = rospy.Publisher('/amphibious/front_left_wheel_velocity_controller/command', Float64, queue_size=1)
        self.pub_fr = rospy.Publisher('/amphibious/front_right_wheel_velocity_controller/command', Float64, queue_size=1)
        self.pub_rl = rospy.Publisher('/amphibious/rear_left_wheel_velocity_controller/command', Float64, queue_size=1)
        self.pub_rr = rospy.Publisher('/amphibious/rear_right_wheel_velocity_controller/command', Float64, queue_size=1)

        self.linear = 0
        self.angular = 0
        self.wheel_separation = 0.3  # 前后轮距，需根据实际调整

        self.timeout = rospy.Duration.from_sec(0.2)
        self.lastMsg = rospy.Time.now()

        rate = rospy.Rate(10)
        while not rospy.is_shutdown():
            self.publish()
            rate.sleep()

    def callback(self, data):
        self.linear = data.linear.x
        self.angular = data.angular.z
        self.lastMsg = rospy.Time.now()

    def publish(self):
        # 超时保护
        if rospy.Time.now() - self.lastMsg > self.timeout:
            self.linear = 0
            self.angular = 0

        # 四轮速度差速控制
        v_left = self.linear - self.angular * self.wheel_separation / 2.0
        v_right = self.linear + self.angular * self.wheel_separation / 2.0

        msg_fl = Float64()
        msg_fr = Float64()
        msg_rl = Float64()
        msg_rr = Float64()

        msg_fl.data = v_left
        msg_fr.data = v_right
        msg_rl.data = v_left
        msg_rr.data = v_right

        self.pub_fl.publish(msg_fl)
        self.pub_fr.publish(msg_fr)
        self.pub_rl.publish(msg_rl)
        self.pub_rr.publish(msg_rr)

if __name__ == '__main__':
    try:
        CmdVel2Gazebo()
    except rospy.ROSInterruptException:
        pass
