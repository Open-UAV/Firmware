import rospy
import roslaunch
import subprocess
import os
import sys

from sensor_msgs.msg import LaserScan, NavSatFix
from std_msgs.msg import Float64;
from gazebo_msgs.msg import ModelStates

from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from geometry_msgs.msg import PoseStamped,Pose,Vector3,Twist,TwistStamped
from std_srvs.srv import Empty

NUM_UAV=int(sys.argv[1])
#Setup
process = subprocess.Popen(["/bin/bash","/root/src/Firmware/Tools/swarm.sh","5"],stdout=subprocess.PIPE)
process.wait()
for line in process.stdout:
	print line

launchfile = "posix_sitl_multi_tmp.launch"
#subprocess.Popen("roscore")
#print ("Roscore launched!")

# Launch the simulation with the given launchfile name
rospy.init_node('multi', anonymous=True)

fullpath = os.path.join(os.path.dirname(__file__),"../launch", launchfile)

subprocess.Popen(["roslaunch",fullpath])
print ("Gazebo launched!")

gzclient_pid = 0
startPosX = [5, 4, 4, 2, 3]
startPosY = [0, 0, 0, 2, 3]
startPosZ = [5, 5, 5, 5, 5]
local_pos = [None for i in range(NUM_UAV)]
mode_proxy = [None for i in range(NUM_UAV)]
arm_proxy = [None for i in range(NUM_UAV)]
pos_sub = [None for i in range(NUM_UAV)]
start_pos = [None for i in range(NUM_UAV)]

cur_pose = PoseStamped()
def pos_cb(msg):
    global cur_pose
    cur_pose = msg

def mavrosTopicStringRoot(uavID=0):
    return ('mavros' + str(uavID+1))

for uavID in range(0,NUM_UAV):
    local_pos[uavID] = rospy.Publisher(mavrosTopicStringRoot(uavID) + '/setpoint_position/local', PoseStamped, queue_size=10)
    mode_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/set_mode', SetMode)
    arm_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/cmd/arming', CommandBool)
    pos_sub[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/local_position/pose', PoseStamped, callback=pos_cb)

    start_pos[uavID] = PoseStamped()
    start_pos[uavID].pose.position.x = startPosX[uavID]
    start_pos[uavID].pose.position.y = startPosY[uavID]
    start_pos[uavID].pose.position.z = startPosZ[uavID]
    print uavID


data = [None for i in range(NUM_UAV)]

while None in data:
    for uavID in range(0, NUM_UAV):
        try:
            print mavrosTopicStringRoot(uavID) + '/global_position/rel_alt'
            data[uavID] = rospy.wait_for_message(mavrosTopicStringRoot(uavID) + '/global_position/rel_alt', Float64, timeout=5)
        except:
            pass

for uavID in range(0, NUM_UAV):
    print "wait for service"
    rospy.wait_for_service(mavrosTopicStringRoot(uavID) + '/set_mode')
    print "got service"

success = []
for uavID in range(0, NUM_UAV):
    try:
        print mode_proxy[uavID]
        success[uavID] = mode_proxy[uavID](1,'OFFBOARD')
        print 'mode '
        print success[uavID]
    except rospy.ServiceException, e:
        print ("mavros/set_mode service call failed: %s"%e)

for uavID in range(0, NUM_UAV):
    for i in range(0,100):
        local_pos[uavID].publish(start_pos[uavID])


#Arm
success = [None for i in range(NUM_UAV)]
for uavID in range(0, NUM_UAV):
    #Arm
    print 'arming' + mavrosTopicStringRoot(uavID)
    rospy.wait_for_service(mavrosTopicStringRoot(uavID) + '/cmd/arming')



#Main method
rate = rospy.Rate(10)
print "Main Running"
while not rospy.is_shutdown():
    for uavID in range(0, NUM_UAV):
        for i in range(0, 100):
            local_pos[uavID].publish(start_pos[uavID])
    rate.sleep()

success = []
for uavID in range(0, NUM_UAV):
    try:
       success[uavID] = arm_proxy[uavID](True)
       print 'arming '
       print success[uavID]
    except rospy.ServiceException, e:
       print ("mavros1/set_mode service call failed: %s"%e)
       print "armed"