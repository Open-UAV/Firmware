# test dummy 
import rospy
import roslaunch
import subprocess
import os

from sensor_msgs.msg import LaserScan, NavSatFix
from std_msgs.msg import Float64;
from gazebo_msgs.msg import ModelStates

from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from geometry_msgs.msg import PoseStamped,Pose,Vector3,Twist,TwistStamped
from std_srvs.srv import Empty

cur_pose = PoseStamped()
def pos_cb(msg):
    global cur_pose
    cur_pose = msg

#Setup

import sys
NUM_UAV = sys.argv[1]
process = subprocess.Popen(["/bin/bash","/root/src/Firmware/Tools/swarm.sh",NUM_UAV],stdout=subprocess.PIPE)
process.wait()
for line in process.stdout:
        print line
launchfile = "posix_sitl_multi_tmp.launch"
subprocess.Popen("roscore")
print ("Roscore launched!")



# Launch the simulation with the given launchfile name
rospy.init_node('multi', anonymous=True)

fullpath = os.path.join(os.path.dirname(__file__),"../launch", launchfile)

subprocess.Popen(["roslaunch",fullpath])
print ("Gazebo launched!")

gzclient_pid = 0
local_pos = []
mode_proxy = []
arm_proxy = []
pos_sub = []


def mavrosTopicStringRoot(UAV_ID=0):
    return ('mavros' + str(UAV_ID)).replace('0', '')

start_pos = []
startPosX = [0, 5, 7]
startPosY = [0, 0, 0]
startPosZ = [5, 5, 5]
data = []

#Comm for drones
for uavID in range(0,NUM_UAV):
    local_pos[uavID] = rospy.Publisher(mavrosTopicStringRoot(uavID) + '/setpoint_position/local', PoseStamped, queue_size=10)
    mode_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/set_mode', SetMode)
    arm_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/cmd/arming', CommandBool)
    pos_sub[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/local_position/pose', PoseStamped, callback=pos_cb)

    start_pos[uavID] = PoseStamped()
    start_pos[uavID].pose.position.x = startPosX[uavID]
    start_pos[uavID].pose.position.y = startPosY[uavID]
    start_pos[uavID].pose.position.z = startPosZ[uavID]


    data[uavID] = None

for uavID in range(0, NUM_UAV):

    while None in data:
        try:
            data[uavID] = rospy.wait_for_message(mavrosTopicStringRoot(uavID) + '/global_position/rel_alt', Float64, timeout=5)
        except:
            pass

    print "wait for service"
    rospy.wait_for_service(mavrosTopicStringRoot(uavID) + '/set_mode')
    print "got service"

    for i in range(0,100):
        local_pos[uavID].publish(start_pos[uavID])

    #setup offboard
    success = []
    try:
        success[uavID] = mode_proxy[uavID](0,'OFFBOARD')
        print success[uavID]
    except rospy.ServiceException, e:
        print ("mavros/set_mode service call failed: %s"%e)


    #Arm
    print "arming"
    rospy.wait_for_service(mavrosTopicStringRoot(uavID) + '/cmd/arming')
    try:
       success[uavID] = arm_proxy[uavID](True)
       print success[uavID]
    except rospy.ServiceException, e:
       print ("mavros1/set_mode service call failed: %s"%e)
       print "armed"

#Main method
rate = rospy.Rate(10)
print "Main Running"
while not rospy.is_shutdown():
    local_pos[uavID].publish(start_pos[uavID])
    local_pos[uavID].publish(start_pos[uavID])
    rate.sleep()
