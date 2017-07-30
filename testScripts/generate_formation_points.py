import rospy
import matlab.engine
from std_msgs.msg import Float32MultiArray,MultiArrayLayout,MultiArrayDimension
import numpy as np
from geometry_msgs.msg import PoseArray
from geometry_msgs.msg import Pose
import sys

NUM_UAV=int(sys.argv[1])
rospy.init_node('formation',anonymous=True)
formation_pub = [None for i in range(NUM_UAV)]

def mavrosTopicStringRoot(uavID=0):
    return ('mavros' + str(uavID+1))

for uavID in range(0,NUM_UAV):
	formation_pub[uavID] = rospy.Publisher(mavrosTopicStringRoot(uavID) + '/formation_setpoints', PoseArray, queue_size=10)


rate = rospy.Rate(10)



eng=matlab.engine.start_matlab()
uav_setpoints = eng.eval('smc_for_flocking_parallel_OPENUAV2('+sys.argv[1] + ',20,5,10)')

pair_step = len(uav_setpoints[0])/2

print "Publishing..."
while not rospy.is_shutdown():
	for uavID in range(0,NUM_UAV):
        	poseArray = PoseArray()
        	poseArray.header.frame_id = mavrosTopicStringRoot(uavID)
        	for timestep in range(0,len(uav_setpoints)):
               		pose = Pose()
                	pose.position.x = uav_setpoints[timestep][uavID]
                	pose.position.y = uav_setpoints[timestep][uavID+pair_step]
                	poseArray.poses.append(pose)
		formation_pub[uavID].publish(poseArray)
	rate.sleep
