#!/bin/bash

cd "$(dirname "$0")"

echo Installing basic packages...
sudo apt-get -y install python3.4 python3-numpy build-essential python3-pil python3-flask fail2ban hostapd python3-pip vim python3-serial udhcpd || exit

echo Copying config...
# Copy config
sudo cp raspi_conf/rc.local /etc/rc.local
sudo chmod +x /etc/rc.local
sudo cp raspi_conf/udhcpd.conf /etc/udhcpd.conf
sudo cp raspi_conf/hostapd.conf /etc/hostapd/hostapd.conf
sudo cp raspi_conf/interfaces /etc/network/interfaces

# Finish setting up hostapd
echo Setting up hostapd
cd ~/tmp
wget http://www.adafruit.com/downloads/adafruit_hostapd.zip
unzip adafruit_hostapd.zip
sudo mv /usr/sbin/hostapd /usr/sbin/hostapd.ORIG
sudo mv hostapd /usr/sbin
sudo chmod 755 /usr/sbin/hostapd

echo Installing opencv3....
# Install opencv (gulp)
sudo apt-get -y install build-essential cmake git pkg-config || exit 1
sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev || exit 1
sudo apt-get -y install libgtk2.0-dev || exit 1
sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev || exit 1
sudo apt-get -y install libatlas-base-dev gfortran || exit 1
sudo apt-get -y install python3.4-dev || exit 1

echo I hope you have enough space...

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
if [ ! -f configured ]; then
cmake -D CMAKE_BUILD_TYPE=RELEASE \
	-D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_C_EXAMPLES=ON \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D OPENCV_EXTRA_MODULES_PATH=~/tmp/opencv_contrib/modules \
	-D BUILD_EXAMPLES=ON .. || exit 1
fi
touch configured
echo Actually making now...
make -j4
sudo make install
sudo ldconfig
