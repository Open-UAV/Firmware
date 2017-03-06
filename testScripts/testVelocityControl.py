"""
testing offboard velocity control for visual servoing
"""

import rospy
from mavros_msgs.msg import State
from geometry_msgs.msg import TwistStamped
from opencv_apps.msg import CircleArrayStamped

def computeVelocities():
    (0.1,0,0.2,0.01)


class VelocityController:
    curr_vel = TwistStamped()
    des_vel = TwistStamped()
    isReadyToFly = True
    x_vel = 0
    y_vel=0
    z_vel=0
    yaw_rate = 0


    def __init__(self):
        rospy.init_node('f450_velocity_controller', anonymous=True)
        vel_pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped, queue_size=10)
        vel_sub = rospy.Subscriber('/mavros/local_position/velocity', TwistStamped, callback=self.vel_cb)
        cicrcles_sub = rospy.Subscriber('/hough_circles/circles', CircleArrayStamped, callback=self.circles_cb)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()


        while not rospy.is_shutdown():
            if self.isReadyToFly:
                self.setvelocities(self.x_vel,self.y_vel,self.z_vel,self.yaw_rate)

                #vel_pub.publish(self.des_vel)
            rate.sleep()

    def setvelocities(self, x_vel, y_vel, z_vel, yaw_rate):
        self.des_vel = self.copy_vel(self.curr_vel)
        self.des_vel.twist.linear.x = x_vel
        self.des_vel.twist.linear.y = y_vel
        self.des_vel.twist.linear.z = z_vel
        self.des_vel.twist.angular.z = yaw_rate

    def copy_vel(self, vel):
        copied_vel = TwistStamped()
        copied_vel.header= vel.header
        return copied_vel

    def vel_cb(self, msg):
        self.curr_vel = msg

    def circles_cb(self,msg):
        print msg.circles[0].center.x, msg.circles[0].center.y, msg.circles[0].radius



if __name__ == "__main__":
    VelocityController()
