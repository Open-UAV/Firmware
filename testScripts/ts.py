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

#Setup
process = subprocess.Popen(["/bin/bash","/root/src/Firmware/Tools/swarm.sh","4"],stdout=subprocess.PIPE)
process.wait()
for line in process.stdout:
	print line
#print process.returncode
launchfile = "posix_sitl_multi_tmp.launch"

