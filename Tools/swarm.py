#!/usr/bin/env python
import sys
import os

def replaceInFile(orig, repl, filename):
    os.system('sed -i "s/' + orig + '/' +repl + '/g" ' + filename)

NUM_UAVs = int(sys.argv[1]) + 1
PX4_HOME = '/root/src'
print(NUM_UAVs)
for NUM in range(1, NUM_UAVs):

    # mavlink
    # < mavlink_udp_port > simulator_udp_port < / mavlink_udp_port >
    # simulator start -s -u simulator_udp_port
    # mavlink start -u mavlink_start_port -r 4000000
    # mavlink start -u mavlink_onboard_local -r 4000000 -m onboard -o mavlink_onboard_remote
    # <param name="fcu_url" value="udp://:mavlink_onboard_remote@localhost:mavlink_onboard_local"/>
    # mavlink stream -r 50 -s POSITION_TARGET_LOCAL_NED -u mavlink_start_port

    mavlink_onboard_remote = 14640
    mavlink_start_port = 14656
    mavlink_onboard_local = 14657
    simulator_udp_port = 14660

    uav_str = str(NUM)
    print(uav_str)
    print(os.system(
        "cp -r " + PX4_HOME + "/Firmware/Tools/sitl_gazebo/models/f450-1 " + PX4_HOME + "/Firmware/Tools/sitl_gazebo/models/f450-tmp-" + uav_str))
    print(os.system(
        "mv " + PX4_HOME + "/Firmware/Tools/sitl_gazebo/models/f450-tmp-" + uav_str +"/f450-1.sdf " + PX4_HOME + "/Firmware/Tools/sitl_gazebo/models/f450-tmp-" + uav_str +"/f450-tmp-" + uav_str + ".sdf"))

    replaceInFile(str(simulator_udp_port), str(simulator_udp_port+100*NUM), PX4_HOME + '/Firmware/Tools/sitl_gazebo/models/f450-tmp-' + uav_str +'/f450-tmp-' + uav_str + '.sdf')
    os.system(
        'cp '+ PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-1 ' + PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)

    replaceInFile(str(simulator_udp_port), str(simulator_udp_port+100*NUM), PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)
    replaceInFile(str(mavlink_start_port), str(mavlink_start_port+100*NUM), PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)
    replaceInFile(str(mavlink_onboard_local), str(mavlink_onboard_local+100*NUM), PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)
    replaceInFile(str(mavlink_onboard_remote), str(mavlink_onboard_remote+100*NUM), PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)
    replaceInFile('MAV_SYS_ID 2', 'MAV_SYS_ID ' + str(NUM), PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)
    replaceInFile('MAV_COMP_ID 2', 'MAV_COMP_ID ' + str(NUM), PX4_HOME + '/Firmware/posix-configs/SITL/init/lpe/f450-tmp-' + uav_str)

    replaceInFile('f450-1', 'f450-tmp-' + uav_str, PX4_HOME + '/Firmware/Tools/sitl_gazebo/models/f450-tmp-' + uav_str +'/f450-tmp-' + uav_str + '.sdf')
    replaceInFile('uav_camera',
                  'uav_' + uav_str + '_camera',
                  PX4_HOME + '/Firmware/Tools/sitl_gazebo/models/f450-tmp-' + uav_str + '/f450-tmp-' + uav_str + '.sdf')

launch_file = '$PX4_HOME/Firmware/launch/posix_sitl_multi_tmp.launch'

SOURCE = PX4_HOME + '/Firmware/launch/posix_sitl_openuav_swarm_base.launch'
DEST = PX4_HOME + '/Firmware/launch/posix_sitl_multi_tmp.launch'

file_block = ''
for NUM in range(1, NUM_UAVs):
    uav_block = '<arg name="x' + str(NUM) + '" default="0"/>' + \
                '<arg name="y' + str(NUM) + '" default="' + str(NUM) +'"/>\n' + \
                '<arg name="vehicle' + str(NUM) + '" default="f450-tmp-' + str(NUM) + '"/>\n' + \
                '<arg name="sdf' + str(
        NUM) + '" default="$(find mavlink_sitl_gazebo)/models/$(arg vehicle' + str(NUM) + ')/$(arg vehicle' + str(NUM) + ').sdf"/>\n' + \
                '<arg name="rcS' + str(
        NUM) + '" default="$(find px4)/posix-configs/SITL/init/$(arg est)/$(arg vehicle' + str(NUM) + ')"/>\n' + \
                '<node name="sitl' + str(
        NUM) + '" pkg="px4" type="px4" output="screen" args="$(find px4) $(arg rcS' + str(NUM) + ')"></node>\n' + \
                '<node name="$(anon vehicle_spawn_' + str(
        NUM) + ')" output="screen" pkg="gazebo_ros" type="spawn_model"\n' + \
                'args="-sdf -file $(arg sdf' + str(NUM) + ') -model $(arg vehicle' + str(NUM) + ') -x $(arg x' + str(
        NUM) + ') -y $(arg y' + str(
        NUM) + ') -z $(arg z) -R $(arg R) -P $(arg P) -Y $(arg Y)"/>\n'
    file_block = file_block + '\n' + uav_block

for NUM in range(1, NUM_UAVs):

    mavros_block = '<node pkg="mavros" type="mavros_node" name="mavros'+ str(NUM) +'" required="true" clear_params="true" output="$(arg log_output)"> \
		<param name="fcu_url" value="udp://:' + str(mavlink_onboard_remote+100*NUM) + '@localhost:' + str(mavlink_onboard_local+100*NUM) + '"/> \
		<param name="gcs_url" value="" /> \
		<param name="target_system_id" value="'+str(NUM)+'" /> \
		<param name="target_component_id" value="'+str(NUM)+'" /> \
		<param name="system_id" value="'+str(NUM+30)+'" /> \
		<rosparam command="load" file="$(arg pluginlists_yaml)" /> \
		<rosparam command="load" file="$(arg config_yaml)" /> \
    </node>'
    file_block = file_block + '\n' + mavros_block
print(file_block)
print(os.system("cp " + SOURCE + " " + DEST))
f=open(DEST,"a")
f.write(file_block + '\n </launch>')
f.close()

print('DRONES CREATED')
