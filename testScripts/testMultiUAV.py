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
NUM_UAV = 3
launchfile = "posix_sitl_two.launch"
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

startPosX = [0 5 7]
startPosY = [0 0 0]
startPosZ = [5 5 5]


#Comm for drone 1
for uavID in range(0,NUM_UAV):
    local_pos[uavID] = rospy.Publisher(mavrosTopicStringRoot(uavID) + '/setpoint_position/local', PoseStamped, queue_size=10)
    mode_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/set_mode', SetMode)
    arm_proxy[uavID] = rospy.ServiceProxy(mavrosTopicStringRoot(uavID) + '/cmd/arming', CommandBool)
    pos_sub[uavID] = rospy.Subscriber(mavrosTopicStringRoot(uavID) + '/local_position/pose', PoseStamped, callback=pos_cb)

    start_pos[uavID] = PoseStamped()
    start_pos[uavID].pose.position.x = startPosX[uavID]
    start_pos[uavID].pose.position.y = startPosY[uavID]
    start_pos[uavID].pose.position.z = startPosZ[uavID]


print "Waiting for mavros..."
data1 = None
data2 = None
while data1 is None or data2 is None:
    try:
        data1 = rospy.wait_for_message('/mavros1/global_position/rel_alt', Float64, timeout=5)
        data2 = rospy.wait_for_message('/mavros2/global_position/rel_alt', Float64, timeout=5)
    except:
        pass

print "wait for service"
rospy.wait_for_service('mavros1/set_mode')
rospy.wait_for_service('mavros2/set_mode')
print "got service"

for i in range(0,100):
    local_pos1.publish(start_pos1)
    local_pos2.publish(start_pos2)

#setup offboard
try:
    success = mode_proxy1(0,'OFFBOARD')
    print success
    success2 = mode_proxy2(0,'OFFBOARD')
    print success2
except rospy.ServiceException, e:
    print ("mavros/set_mode service call failed: %s"%e)


#Arm
print "arming"
rospy.wait_for_service('mavros1/cmd/arming')
try:
   success = arm_proxy1(True)
   print success
   success2 = arm_proxy2(True)
   print success
except rospy.ServiceException, e:
   print ("mavros1/set_mode service call failed: %s"%e)
   print "armed"

#Main method
rate = rospy.Rate(10)
print "Main Running"
while not rospy.is_shutdown():
    local_pos1.publish(start_pos1)
    local_pos2.publish(start_pos2)
    rate.sleep()
