#!/bin/bash
# For automated install, set permissions to avoid sudo/passwd. On standalone VM, run sudo visudo and add the following line to your sudoers file (or use sudo visudo to enter the editor):
# Defaults        !tty_tickets

export DEBIAN_FRONTEND=noninteractive
sudo usermod -a -G dialout $USER

sudo add-apt-repository ppa:george-edison55/cmake-3.x -y
sudo apt-get update
sudo apt-get -q -y install cmake -y
sudo apt-get -q -y install ant protobuf-compiler libeigen3-dev libopencv-dev
sudo apt-get -q -y install python-argparse git-core wget zip python-empy qtcreator cmake build-essential genromfs -y
curl -ssL http://get.gazebosim.org | sh
echo "export GAZEBO_PLUGIN_PATH=${GAZEBO_PLUGIN_PATH}:$HOME/src/Firmware/Tools/sitl_gazebo/Build" >> ~/.bashrc
echo "export GAZEBO_MODEL_PATH=${GAZEBO_MODEL_PATH}:$HOME/src/Firmware/Tools/sitl_gazebo/models" >> ~/.bashrc
sudo apt-get remove -y gcc-arm-none-eabi gdb-arm-none-eabi binutils-arm-none-eabi
sudo add-apt-repository ppa:team-gcc-arm-embedded/ppa
sudo apt-get update
sudo apt-get -q -y install python-serial openocd flex bison libncurses5-dev autoconf texinfo build-essential \
    libftdi-dev libtool zlib1g-dev \
    python-empy gcc-arm-embedded -y

mkdir src 
cd src 
git clone https://github.com/darknight-007/Firmware
git submodule update --init --recursive
cd ~
