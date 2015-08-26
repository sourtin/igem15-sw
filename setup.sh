#!/bin/bash
LOGFILE=~/igem15-sw.log
function error {
    echo "Error: $@"
    echo "Check the log at $LOGFILE"
    exit 1
}

set -o pipefail
function log {
    while read l; do
       echo -n .
       echo "$l" >> $LOGFILE
    done
    echo
}

cd "$(dirname "$0")"

echo "---- START INSTALL $(date) ----" >> $LOGFILE

echo Installing basic packages...
(
    sudo apt-get -y install python3.4 python3-numpy build-essential python3-pil fail2ban hostapd python3-pip vim python3-serial python3-flask udhcpd python3-pip virtualenv || exit 1
) 2>&1 | log || error 'Installing python, fail2ban and hostapd'

echo Copying config...
(
    # Copy config
    dir=~/igem15-sw

    sudo touch /etc/udhcpd.conf /etc/hostapd/hostapd.conf
    sudo rm /etc/udhcpd.conf /etc/hostapd/hostapd.conf || exit 1

    # add to rc.local
    rscript="$(pwd)/raspi_conf/rc.local"
    grep "$rscript" /etc/rc.local || sed -ri "s|#\!\/bin.bash|#\!\/bin\/bash\n$rscript|g" /etc/rc.local

    sudo ln -s $dir/raspi_conf/udhcpd.conf /etc/udhcpd.conf || exit 1
    sudo ln -s $dir/raspi_conf/hostapd.conf /etc/hostapd/hostapd.conf || exit 1
    sudo cp raspi_conf/interfaces /etc/network/interfaces || exit 1
) 2>&1 | log || error 'Setting up configuration files'

(
    # Setup ssl cert and htpasswd
    cd nginx
    echo 'admin:$apr1$JD.wDERI$pNHlC/e4eUu7acirb4LW/.' > server.htpasswd || exit 1
    touch server.htpasswd.disabled
    unset OPENSSL_CONF
    openssl req -days 3600 -new -x509 -sha512 -subj "/C=GB/ST=Cambridgeshire/L=Cambridge/O=Cambridge-JIC iGEM 2015/CN=OpenScope" -nodes -out server.crt -keyout server.key
    cd ..
) 2>&1 | log || error 'Setting up SSL certificates and nginx'

(
    # Setup gunicorn
    sudo apt-get remove -y gunicorn
    sudo pip3 install gunicorn || exit 1

    # Compile mjpg-streamer
    cd contrib/mjpg-streamer/mjpg-streamer-experimental || exit 1
    make || exit 1
) 2>&1 | log || error 'Installing gunicorn and mjpeg-streamer'


# Finish setting up hostapd
echo Setting up hostapd
(
    mkdir -p ~/tmp || exit 1
    cd ~/tmp || exit 1
    wget http://www.adafruit.com/downloads/adafruit_hostapd.zip -O adafruit_hostapd.zip || exit 1
    unzip adafruit_hostapd.zip || exit 1
    sudo mv /usr/sbin/hostapd /usr/sbin/hostapd.ORIG || exit 1
    sudo mv hostapd /usr/sbin || exit 1
    sudo chmod 755 /usr/sbin/hostapd || exit 1
) 2>&1 | log || error 'Installing hostapd'

if python3 -c "import cv2"; then
    echo "OpenCV3 Installed"
else
    echo Installing opencv3....
    # Install opencv (gulp)

    (
        sudo apt-get -y install build-essential cmake git pkg-config || exit 1
        sudo apt-get -y install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev || exit 1
        sudo apt-get -y install libgtk2.0-dev || exit 1
        sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev || exit 1
        sudo apt-get -y install libatlas-base-dev gfortran || exit 1
        sudo apt-get -y install python3.4-dev || exit 1
    ) 2>&1 | log || error 'Installing opencv dependencies'

    echo I hope you have enough space...

    (
        cd ~/tmp || exit 3
        git clone https://github.com/Itseez/opencv.git || exit 1
        cd opencv || exit 1
        git checkout 3.0.0 || exit 1
        cd .. || exit 1
        git clone https://github.com/Itseez/opencv_contrib.git || exit 1
        cd opencv_contrib || exit 1
        git checkout 3.0.0 || exit 1
        cd ../opencv || exit 1
        mkdir build || exit 1
        cd build || exit 1
        if [ ! -f configured ]; then
            cmake -D CMAKE_BUILD_TYPE=RELEASE \
                  -D CMAKE_INSTALL_PREFIX=/usr/local \
                  -D INSTALL_C_EXAMPLES=ON \
                  -D INSTALL_PYTHON_EXAMPLES=ON \
                  -D OPENCV_EXTRA_MODULES_PATH=~/tmp/opencv_contrib/modules \
                  -D BUILD_EXAMPLES=ON .. || exit 1
        fi
        touch configured || exit 72
    ) 2>&1 | log || error 'Downloading and configuring opencv'

    echo Actually making now...
    (
        make -j4 || exit 4
        sudo make install || exit 5
        sudo ldconfig || exit 6
    ) 2>&1 | log || error 'Making and installing opencv'
fi

echo SUCCESS

