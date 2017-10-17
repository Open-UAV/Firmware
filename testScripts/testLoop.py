"""
testing offboard positon control with a simple takeoff script
"""

import rospy
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion
import math
import numpy
import sys




class OffbPosCtl:
    curr_pose = PoseStamped()
    waypointIndex = 0
    distThreshold = 0.5
    sim_ctr = 1
    des_pose = PoseStamped()
    isReadyToFly = False

    def __init__(self, H,V,uav_prefix):
	self.locations = numpy.matrix([[H, H, V, 0, 0, -0.48717451, -0.87330464],
                              [-H, H, V, 0, 0, -0.48717451, -0.87330464],
                              [-H, -H, V, 0, 0, -0.48717451, -0.87330464],
                              [H, -H, V, 0, 0, -0.48717451, -0.87330464],
                              ])
	print self.locations
        print '/mavros'+ uav_prefix + '/setpoint_position/local'
        rospy.init_node('offboard_test', anonymous=True)
        pose_pub = rospy.Publisher('/mavros'+ uav_prefix + '/setpoint_position/local', PoseStamped, queue_size=10)
        mocap_sub = rospy.Subscriber('/mavros'+ uav_prefix + '/local_position/pose', PoseStamped, callback=self.mocap_cb)
        state_sub = rospy.Subscriber('/mavros'+ uav_prefix + '/state', State, callback=self.state_cb)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()
        self.des_pose = self.copy_pose(self.curr_pose)
        shape = self.locations.shape


        while not rospy.is_shutdown():
            print self.sim_ctr, shape[0], self.waypointIndex
            if self.waypointIndex is shape[0]:
                self.waypointIndex = 0
                self.sim_ctr += 1

            if self.isReadyToFly:

                des_x = self.locations[self.waypointIndex, 0]
                des_y = self.locations[self.waypointIndex, 1]
                des_z = self.locations[self.waypointIndex, 2]
                self.des_pose.pose.position.x = des_x
                self.des_pose.pose.position.y = des_y
                self.des_pose.pose.position.z = des_z
                self.des_pose.pose.orientation.x = self.locations[self.waypointIndex, 3]
                self.des_pose.pose.orientation.y = self.locations[self.waypointIndex, 4]
                self.des_pose.pose.orientation.z = self.locations[self.waypointIndex, 5]
                self.des_pose.pose.orientation.w = self.locations[self.waypointIndex, 6]


                curr_x = self.curr_pose.pose.position.x
                curr_y = self.curr_pose.pose.position.y
                curr_z = self.curr_pose.pose.position.z

                dist = math.sqrt((curr_x - des_x)*(curr_x - des_x) + (curr_y - des_y)*(curr_y - des_y) + (curr_z - des_z)*(curr_z - des_z))
                if dist < self.distThreshold:
                    self.waypointIndex += 1

                # print dist, curr_x, curr_y, curr_z, self.waypointIndex
            pose_pub.publish(self.des_pose)
            rate.sleep()

    def copy_pose(self, pose):
        pt = pose.pose.position
        quat = pose.pose.orientation
        copied_pose = PoseStamped()
        copied_pose.header.frame_id = pose.header.frame_id
        copied_pose.pose.position = Point(pt.x, pt.y, pt.z)
        copied_pose.pose.orientation = Quaternion(quat.x, quat.y, quat.z, quat.w)
        return copied_pose

    def mocap_cb(self, msg):
        # print msg
        self.curr_pose = msg

    def state_cb(self,msg):
        print msg.mode
        if(msg.mode=='OFFBOARD'):
            self.isReadyToFly = True
            print "readyToFly"

if __name__ == "__main__":
    OffbPosCtl(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3])

