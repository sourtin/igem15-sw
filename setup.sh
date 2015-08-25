#!/bin/bash

sudo apt-get -y install python3.4 python3-numpy build-essential python3-pil python3-flask fail2ban hostapd python3-pip python3-serial

# Copy config
sudo cp raspi_conf/rc.local /etc/rc.local
sudo chmod +x /etc/rc.local
sudo cp raspi_conf/udhcpd.conf /etc/udhcpd.conf
sudo cp raspi_conf/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp raspi_conf/interfaces /etc/network/interfaces

# Install opencv (gulp)
sudo apt-get -y install build-essential cmake git pkg-config
sudo apt-get -y install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev
sudo apt-get -y install libgtk2.0-dev
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
sudo apt-get -y install libatlas-base-dev gfortran
sudo apt-get -y install python3.4-dev

mkdir -p ~/tmp
cd ~/tmp
git clone https://github.com/Itseez/opencv.git
cd opencv
git checkout 3.0.0
cd ..
git clone https://github.com/Itseez/opencv_contrib.git
cd opencv_contrib
git checkout 3.0.0
cd ../opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_C_EXAMPLES=ON \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/tmp/opencv_contrib/modules \
	-D BUILD_EXAMPLES=ON ..
echo Actually making now...
make -j4
sudo make install
sudo ldconfig

