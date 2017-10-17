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
process = subprocess.Popen(["/bin/bash","/root/src/Firmware/Tools/swarm.sh","2"],stdout=subprocess.PIPE)
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
start_pos1.pose.position.y = 5
start_pos1.pose.position.z = 10

#Comm for drone 2
local_pos2 = rospy.Publisher('mavros2/setpoint_position/local',PoseStamped,queue_size=10)
mode_proxy2 = rospy.ServiceProxy('mavros2/set_mode', SetMode)
arm_proxy2 = rospy.ServiceProxy('mavros2/cmd/arming', CommandBool)

start_pos2 = PoseStamped()
start_pos2.pose.position.x = 10
start_pos2.pose.position.y = 0
start_pos2.pose.position.z = 5

print "Waiting for mavros..."
data1 = None
data2 = None
while data1 is None or data2 is None:
    try:
        data1 = rospy.wait_for_message('/mavros1/global_position/rel_alt', Float64, timeout=5)
        data2 = rospy.wait_for_message('/mavros2/global_position/rel_alt', Float64, timeout=5)
    except Exception  as e:
	print str(e)
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
rospy.wait_for_service('mavros2/cmd/arming')
try:
   success = arm_proxy1(True)
   print success
   success2 = arm_proxy2(True)
   print success2
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

