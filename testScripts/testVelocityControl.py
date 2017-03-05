"""
testing offboard positon control with a simple takeoff script
"""

import rospy
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion
import math
import numpy
from geometry_msgs.msg import TwistStamped





class VelocityController:
    curr_vel = TwistStamped()
    sim_ctr = 1

    des_pose = PoseStamped()
    des_vel = TwistStamped()

    isReadyToFly = True


    def __init__(self):
        rospy.init_node('f450_velocity_controller', anonymous=True)
        vel_pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
        vel_sub = rospy.Subscriber('/mavros/local_position/velocity', TwistStamped, callback=self.vel_cb)

        state_sub = rospy.Subscriber('/mavros/state', State, callback=self.state_cb)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()
        self.des_vel = self.copy_vel(self.curr_vel)


        while not rospy.is_shutdown():
            if self.isReadyToFly:
                self.des_vel = self.copy_vel(self.curr_vel)

                self.des_vel.twist.linear.x = 0.1
                self.des_vel.twist.linear.y = 0
                self.des_vel.twist.linear.z = 0.1

                vel_pub.publish(self.des_vel)
            rate.sleep()

    def copy_vel(self, vel):
        copied_vel = TwistStamped()
        copied_vel.header= vel.header
        return copied_vel

    def vel_cb(self, msg):
        # print msg
        self.curr_vel = msg

    def state_cb(self,msg):
        print msg.mode
        if(msg.mode=='OFFBOARD'):
            self.isReadyToFly = True
            print "readyToFly"


if __name__ == "__main__":
    VelocityController()
