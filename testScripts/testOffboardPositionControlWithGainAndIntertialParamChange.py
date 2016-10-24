"""
testing offboard positon control with a simple takeoff script


"""

import rospy
from mavros_msgs.msg import State
from geometry_msgs.msg import PoseStamped, Point, Quaternion
import math
import numpy
from gazebo_msgs.srv import SetLinkProperties
from gazebo_msgs.srv import SetLinkPropertiesRequest
from gazebo_msgs.srv import GetLinkProperties
from gazebo_msgs.srv import GetLinkPropertiesRequest
from gazebo_msgs.srv import GetLinkPropertiesResponse
from sensor_msgs.msg import Joy
from mavros_msgs.srv import ParamSetRequest
from mavros_msgs.srv import ParamSet
from mavros_msgs.msg import ParamValue







class OffboardPosCtlWithOnlineDynamicalUpdates:
    curr_pose = PoseStamped()
    waypointIndex = 0
    distThreshold = 0.4
    sim_ctr = 1

    des_pose = PoseStamped()
    isReadyToFly = False

    locations = numpy.matrix([[2, 0, 1, 0, 0, -0.48717451, -0.87330464],
                              [0, 2, 1, 0, 0, 0, 1],
                              [-2, 0, 1, 0.,  0.,  0.99902148, -0.04422762],
                              [0, -2, 1, 0, 0, 0, 0],
                              ])

    MPC_PITCH_P = 0
    MPC_PITCH_D = 1
    MPC_ROLL_P = 2
    MPC_ROLL_D = 3
    MPC_PITCHRATE_P = 4
    MPC_PITCHRATE_D = 5
    MPC_ROLLRATE_P = 6
    MPC_ROLLRATE_D = 7
    MPC_XY_CRUISE = 8


    def __init__(self):
        rospy.init_node('offboard_test', anonymous=True)
        pose_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
        mocap_sub = rospy.Subscriber('/mavros/local_position/pose', PoseStamped, callback=self.mocap_cb)
        state_sub = rospy.Subscriber('/mavros/state', State, callback=self.state_cb)
        nanokontrolSub = rospy.Subscriber('/nanokontrol/nanokontrol', Joy, callback=self.nanokontrolCallback)
        gazebo_service_set_link_properties = rospy.ServiceProxy('/gazebo/set_link_properties', SetLinkProperties)
        gazebo_service_get_link_properties = rospy.ServiceProxy('/gazebo/get_link_properties', GetLinkProperties)
        self.param_service = rospy.ServiceProxy('/mavros/param/set', ParamSet)

        rate = rospy.Rate(10)  # Hz
        rate.sleep()
        self.des_pose = self.copy_pose(self.curr_pose)
        shape = self.locations.shape


        while not rospy.is_shutdown():
            #print self.sim_ctr, shape[0], self.waypointIndex
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
                    #des_params = self.updateUAVInertialParam(gazebo_service_get_link_properties)


                # print dist, curr_x, curr_y, curr_z, self.waypointIndex
            pose_pub.publish(self.des_pose)
            rate.sleep()

    def updateUAVInertialParam(self, gazebo_service_get_link_properties):
        # current_params = GetLinkPropertiesResponse()
        # current_params = gazebo_service_get_link_properties.call(GetLinkPropertiesRequest('base_link'))
        # des_params = current_params
        # des_params = SetLinkPropertiesRequest()
        # des_params.mass = current_params.mass + 0.3
        # des_params.gravity_mode = current_params.gravity_mode
        # des_params.com = current_params.com
        # des_params.ixx = current_params.ixx
        # des_params.ixy = current_params.ixy
        # des_params.ixz = current_params.ixz
        # des_params.iyy = current_params.iyy
        # des_params.iyz = current_params.ixz
        # des_params.izz = current_params.izz
        # des_params.link_name = 'base_link'
        # gazebo_service_set_link_properties.call(des_params)
        des_params = 0
        return des_params

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


    def nanokontrolCallback(self,msg):
        velocity =  (((msg.axes[0])+1)*4)
        param = ParamValue()
        param.real = velocity
        paramReq = ParamSetRequest()
        paramReq.param_id = 'MPC_XY_CRUISE'
        paramReq.value = param
        self.param_service.call(paramReq)



if __name__ == "__main__":
    OffboardPosCtlWithOnlineDynamicalUpdates()
