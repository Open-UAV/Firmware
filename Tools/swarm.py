#!/usr/bin/env python
import sys
import os


def replaceInFile(orig, repl, filename):
    for line in fileinput.input([filename], inplace=True):
        print(line.replace(orig, repl))



NUM_UAVs = int(sys.argv[1])
PX4_HOME = '/home/nsf/open-uav'
for NUM in range(1, NUM_UAVs):
    fcu1 = 14140
    mavlink_start_port = 14156
    fcu2 = 14157
    mavlink_port = 14160

uav_str = str(NUM)
os.system(
    "cp -r $PX4_HOME/Firmware/Tools/sitl_gazebo/models/f450-1 $PX4_HOME/Firmware/Tools/sitl_gazebo/models/f450-tmp-" + uav_str)
os.system(
    "mv $PX4_HOME/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-1.sdf $PX4_HOME/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-" + uav_str + ".sdf")

replaceInFile('146', PORT, '$PX4_HOME/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-" + NUM_UAVs + ".sdf')
os.system(
    'cp $PX4_HOME/Firmware/posix-configs/SITL/init/lpe/f450-1 $PX4_HOME/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' +
    uav_str)

replaceInFile('146', PORT, '$PX4_HOME/Firmware/posix-configs/SITL/init/lpe/f450-tmp-$NUM')

replaceInFile('f450-1', 'f450-tmp-$NUM', '$PX4_HOME/Firmware/Tools/sitl_gazebo/models/f450-tmp-$NUM/f450-tmp-$NUM.sdf')
replaceInFile('uav_camera',
              'uav_$NUM_camera',
              PX4_HOME + '/Firmware/Tools/sitl_gazebo/models/f450-tmp-' + uav_str + '/f450-tmp-' + uav_str + '.sdf')

launch_file = '$PX4_HOME/Firmware/launch/posix_sitl_multi_tmp.launch'

SOURCE = "$PX4_HOME/Firmware/launch/posix_sitl_multibase.launch"
DEST = "$PX4_HOME/Firmware/launch/posix_sitl_multi_tmp.launch"

file_block = ''
for ind in range(1, NUM_UAVs):
    uav_block = '<arg name="x1" default="0"/>' + \
                '<arg name="y' + str(ind) + '" default="1"/>' + \
                '<arg name="vehicle' + str(ind) + '" default="f450-tmp-1"/>' + \
                '<arg name="sdf' + str(
        ind) + '" default="$(find mavlink_sitl_gazebo)/models/$(arg vehicle1)/$(arg vehicle1).sdf"/>' + \
                '<arg name="rcS' + str(
        ind) + '" default="$(find px4)/posix-configs/SITL/init/$(arg est)/$(arg vehicle1)"/>' + \
                '<node name="sitl' + str(
        ind) + '" pkg="px4" type="px4" output="screen" args="$(find px4) $(arg rcS1)"></node>' + \
                '<node name="$(anon vehicle_spawn_' + str(
        ind) + ')" output="screen" pkg="gazebo_ros" type="spawn_model"' + \
                'args="-sdf -file $(arg sdf' + str(ind) + ') -model $(arg vehicle1) -x $(arg x' + str(
        ind) + '=) -y $(arg y' + str(
        ind) + ') -z $(arg z) -R $(arg R) -P $(arg P) -Y $(arg Y)"/>-->'
    file_block = file_block + '\n' + uav_block

for ind in range(1, NUM_UAVs):
    port1 = '14014'
    port2 = '14050'
    mavros_block = '<node pkg="mavros" type="mavros_node" name="mavros'+ str(ind) +'" required="true" clear_params="true" output="$(arg log_output)"> \
		<param name="fcu_url" value="udp://:'+ port1+'@localhost:'+port2+'"/> \
		<param name="gcs_url" value="" /> \
		<param name="target_system_id" value="'+str(ind)+'" /> \
		<param name="target_component_id" value="'+str(ind)+'" /> \
		<param name="system_id" value="'+str(ind+30)+'" /> \
		<rosparam command="load" file="$(arg pluginlists_yaml)" /> \
		<rosparam command="load" file="$(arg config_yaml)" /> \
    </node>'
    file_block = file_block + '\n' + mavros_block
print(file_block)

print('DRONES CREATED')
