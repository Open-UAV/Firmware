import rospy
import roslaunch
import subprocess
import os
import time
from sensor_msgs.msg import LaserScan, NavSatFix
from std_msgs.msg import Float64;
from gazebo_msgs.msg import ModelStates
from mavros_msgs.msg import State
import sys 
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from geometry_msgs.msg import PoseStamped,Pose,PoseArray,Vector3,Twist,TwistStamped
from std_srvs.srv import Empty
import math 
NUM_UAV=int(sys.argv[1])
NUM_STPNTS = 3

def state_cb(msg):
	if(msg.armed == False):
		print "Standby. Arming!!"
		for uavID in range(0, NUM_UAV):
			try:
                                arm_proxy[uavID](True)
                        except rospy.ServiceException, e:
                                print ("mavros1/set_mode service call failed: %s"%e)

	if(msg.mode != "OFFBOARD"):
		print "Attempting OFFBOARD mode."
		for uavID in range(0, NUM_UAV):
        	        try:
                	        mode_proxy[uavID](0,'OFFBOARD')
                	except rospy.ServiceException, e:
                        	print ("mavros/set_mode service call failed: %s"%e)
       


local_pos = [None for i in range(NUM_UAV)]
mode_proxy = [None for i in range(NUM_UAV)]
arm_proxy = [None for i in range(NUM_UAV)]
pos_sub = [None for i in range(NUM_UAV)]
cur_pos = [None for i in range(NUM_UAV)]
formation_setpoints = [None for i in range(NUM_UAV)]
next_pos = [None for i in range(NUM_UAV)]
mavros_state = [None for i in range(NUM_UAV)]
waypointIndex = [0 for i in range(NUM_UAV)]
distThreshold = 0.4 
sim_ctr=0 


def pos_cb(msg, args):
    global cur_pos
    cur_pos[args] = msg



def mavrosTopicStringRoot(uavID=0):
    return ('mavros' + str(uavID+1))

rospy.init_node('multicommand', anonymous=True)
def formation_cb(msg,args):
	global next_pos
	global cur_pos
	global waypointIndex 
	global NUM_STPNTS
	if cur_pos[args] is not None:
		next_pos[args]= PoseStamped()
		next_pos[args].header = cur_pos[args].header
		next_pos[args].pose = msg.poses[waypointIndex[args]]
		NUM_STPNTS = len(msg.poses)

for uavID in range(0,NUM_UAV):
    local_pos[uavID] = rospy.Publisher(mavrosTopicStringRoot(uavID) + '/setpoint_position/local', PoseStamped, queue_size=10)
    mode_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/set_mode', SetMode)
    arm_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/cmd/arming', CommandBool)
    pos_sub[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/local_position/pose', PoseStamped, pos_cb,(uavID))
    formation_setpoints[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/formation_setpoints', PoseArray, formation_cb,(uavID))

    mavros_state[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/state', State, callback=state_cb)



#Main method
rate = rospy.Rate(100)
print "Main Running"
while not rospy.is_shutdown():
    for uavID in range(0, NUM_UAV):
	 if next_pos[uavID] is not None:
	 	des_x = next_pos[uavID].pose.position.x
         	des_y = next_pos[uavID].pose.position.y
         	des_z = next_pos[uavID].pose.position.z

	 	curr_x = cur_pos[uavID].pose.position.x
         	curr_y = cur_pos[uavID].pose.position.y
         	curr_z = cur_pos[uavID].pose.position.z

	 	dist = math.sqrt((curr_x - des_x)*(curr_x - des_x) + (curr_y - des_y)*(curr_y - des_y) + (curr_z - des_z)*(curr_z - des_z))
	 	if dist < distThreshold:
         		waypointIndex[uavID] += 1

	 	if waypointIndex[uavID] > NUM_STPNTS-1:
                	waypointIndex[uavID] = NUM_STPNTS-1
                	print uavID, sim_ctr
			sim_ctr += 1
	
    	 	local_pos[uavID].publish(next_pos[uavID])
    rate.sleep()

