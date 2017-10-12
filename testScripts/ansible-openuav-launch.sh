#!/bin/bash
#Script to automate all of swarm formation running
datestamp=`date +%s`
num_uavs=$1
gzweb_ctrl_port=$2"76" 
gzweb_gui_port=$2"86"
tensorboard_port=$2"002" 
ros_websocket_port=$2"090"
docker_image_name="openuav-swarm"
container_name="openuav-$datestamp"

echo $num_uavs
echo $gzweb_ctrl_port
echo $gzweb_gui_port
echo $tensorboard_port
echo $ros_websocket_port
echo $docker_image_name 
echo $container_name

nvidia-docker run -dit --name=$container_name -p $gzweb_ctrl_port:$gzweb_ctrl_port -p $gzweb_gui_port:$gzweb_gui_port -p $tensorboard_port:$tensorboard_port -p $ros_websocket_port:$ros_websocket_port $docker_image_name bash
nvidia-docker exec $container_name bash /runpy1.sh $num_uavs &>/dev/null &
nvidia-docker exec $container_name bash /runpy2.sh $gzweb_ctrl_port $gzweb_gui_port &>/dev/null &
nvidia-docker exec $container_name bash /runpy3.sh $num_uavs &>/dev/null &
nvidia-docker exec $container_name bash /runpy4.sh $ros_websocket_port &>/dev/null &
nvidia-docker exec $container_name bash /runpy5.sh 5 5 1 &>/dev/null &
nvidia-docker exec $container_name bash /runpy5.sh 5 4 2 &>/dev/null &
nvidia-docker exec $container_name bash /runpy5.sh 5 3 3 &>/dev/null &
nvidia-docker exec $container_name bash /runpy5.sh 5 2 4 &>/dev/null &
nvidia-docker exec $container_name bash /runpy5.sh 5 1 5 &>/dev/null &


