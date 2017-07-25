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

#Setup
process = subprocess.Popen(["/bin/bash","/root/src/Firmware/Tools/swarm.sh",sys.argv[0]],stdout=subprocess.PIPE)
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


#Comm for drone 1
local_pos1 = rospy.Publisher('mavros1/setpoint_position/local',PoseStamped,queue_size=10)
mode_proxy1 = rospy.ServiceProxy('mavros1/set_mode', SetMode)
arm_proxy1 = rospy.ServiceProxy('mavros1/cmd/arming', CommandBool)

start_pos1 = PoseStamped()
start_pos1.pose.position.x = 0
start_pos1.pose.position.y = 0
start_pos1.pose.position.z = 10

#Comm for drone 2
local_pos2 = rospy.Publisher('mavros2/setpoint_position/local',PoseStamped,queue_size=10)
mode_proxy2 = rospy.ServiceProxy('mavros2/set_mode', SetMode)
arm_proxy2 = rospy.ServiceProxy('mavros2/cmd/arming', CommandBool)

start_pos2 = PoseStamped()
start_pos2.pose.position.x = 10
start_pos2.pose.position.y = 0
start_pos2.pose.position.z = 5

#Comm for drone 3
local_pos3 = rospy.Publisher('mavros3/setpoint_position/local',PoseStamped,queue_size=10)
mode_proxy3 = rospy.ServiceProxy('mavros3/set_mode', SetMode)
arm_proxy3 = rospy.ServiceProxy('mavros3/cmd/arming', CommandBool)

start_pos3 = PoseStamped()
start_pos3.pose.position.x = 10
start_pos3.pose.position.y = 10
start_pos3.pose.position.z = 10

#Comm for drone 4
local_pos4 = rospy.Publisher('mavros4/setpoint_position/local',PoseStamped,queue_size=10)
mode_proxy4 = rospy.ServiceProxy('mavros4/set_mode', SetMode)
arm_proxy4 = rospy.ServiceProxy('mavros4/cmd/arming', CommandBool)

start_pos4 = PoseStamped()
start_pos4.pose.position.x = -10
start_pos4.pose.position.y = -10
start_pos4.pose.position.z = 5

print "Waiting for mavros..."
data1 = None
data2 = None
data3 = None
data4 = None
while data1 is None or data2 is None:
    try:
        data1 = rospy.wait_for_message('/mavros1/global_position/rel_alt', Float64, timeout=5)
        data2 = rospy.wait_for_message('/mavros2/global_position/rel_alt', Float64, timeout=5)
        data3 = rospy.wait_for_message('/mavros3/global_position/rel_alt', Float64, timeout=5)
        data4 = rospy.wait_for_message('/mavros4/global_position/rel_alt', Float64, timeout=5)
    except:
        pass

print "wait for service"
rospy.wait_for_service('mavros1/set_mode')
rospy.wait_for_service('mavros2/set_mode')
rospy.wait_for_service('mavros3/set_mode')
rospy.wait_for_service('mavros4/set_mode')
print "got service"

for i in range(0,100):
    local_pos1.publish(start_pos1)
    local_pos2.publish(start_pos2)
    local_pos3.publish(start_pos1)
    local_pos4.publish(start_pos2)

#setup offboard
try:
    success = mode_proxy1(0,'OFFBOARD')
    print success
    success2 = mode_proxy2(0,'OFFBOARD')
    print success2
    success3 = mode_proxy3(0,'OFFBOARD')
    print success3
    success4 = mode_proxy4(0,'OFFBOARD')
    print success4
except rospy.ServiceException, e:
    print ("mavros/set_mode service call failed: %s"%e)


#Arm
print "arming"
rospy.wait_for_service('mavros1/cmd/arming')
try:
   success = arm_proxy1(True)
   print success
   success2 = arm_proxy2(True)
   print success2
   success3 = arm_proxy3(True)
   print success3
   success4 = arm_proxy4(True)
   print success4
except rospy.ServiceException, e:
   print ("mavros1/set_mode service call failed: %s"%e)
   print "armed"

#Main method
rate = rospy.Rate(10)
print "Main Running"
while not rospy.is_shutdown():
    local_pos1.publish(start_pos1)
    local_pos2.publish(start_pos2)
    local_pos3.publish(start_pos3)
    local_pos4.publish(start_pos4)
    rate.sleep()

