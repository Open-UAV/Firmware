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
process = subprocess.Popen(["/bin/bash","/root/src/Firmware/Tools/swarm.sh",str(NUM_UAV)],stdout=subprocess.PIPE)
process.wait()
for line in process.stdout:
	print line

launchfile = "posix_sitl_multi_tmp.launch"
subprocess.Popen("roscore")
print ("Roscore launched!")

# Launch the simulation with the given launchfile name
rospy.init_node('multi',anonymous=True)

fullpath = os.path.join(os.path.dirname(__file__),"../launch", launchfile)

subprocess.Popen(["roslaunch",fullpath])
print ("Gazebo launched!")

#Main method
rate = rospy.Rate(10)
while not rospy.is_shutdown():
    rate.sleep()



