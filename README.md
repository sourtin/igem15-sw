# Cambridge-JIC iGEM 2015 Software Repo

# Installation instructions
The easiest way to install the pi software is to download our pre-prepared NOOBS zip from our wiki <http://2015.igem.org/Team:Cambridge-JIC> and image a microSD card by unzipping everything onto a blank FAT32-formatted microSD card. See <https://www.raspberrypi.org/help/noobs-setup/> for more info (but remember to use our NOOBS zip, not the default one! We have baked it with our code just for you!)

Once this is done, you will need to insert the microSD card and supply power to the raspberry pi. Assuming you have a ralink wifi adapter plugged in, you should be able to connect to the wifi network OPENSCOPE with the password PASSWORD and access the microscope at <https://192.168.0.1:9000/>.

If you do not have a wifi adapter, you can connect an ethernet cable. Once you find out the ip address of the microscope (e.g. from your router's web admin page or through `nmap`).

If you have a different wifi adapter (we used an Edimax wifi dongle), you may need to edit /etc/hostapd/hostapd.conf (see below) to work with the wifi adapter.

And connect to the `OPENSCOPE` wifi network from your laptop/other computer with wifi. **The default wifi password is `PASSWORD`** You can point your web browser to <https://192.168.0.1:9000/> to access the microscope!

Once you access the right url, you will be prompted for a username and password.

**The default username is `admin` and the default password is `test`**

You can add other user accounts and revoke access/change passwords from the admin interface at <https://192.168.0.1:9000/admin/>

If you have attached an ethernet cable to the pi, you will be able to use the OPENSCOPE network as a wifi access point to the internet. You will then also be able to access the microscope off the internet - you can find the ip address by running:

    ifconfig eth0

You will see the ip address under `inet addr:192.168.1.7` or similar. Assuming the ip address is `192.168.1.7`, you can then also connect to it on the local network at `https://192.168.1.7:9000/`

You will need to see how to set up port forwarding on your router if you wish to access the microscope over the internet on a different LAN. For the hardcore enthusiasts, you can google how to set up ssh port forwarding to tunnel port 9000 elsewhere securely ;)

It is easiest to just use the preprepared disk image provided, however if you wish to customise the install more advanced instructions are also provided. We have provided the steps we used to construct the provided install, but feel free to deviate from the instructions as much as you wish, just remember to use an ARM-specific binaries and to obtain python 3.4+.

## Raspbian
### Premade Image
### Operating System
First the installation media must be prepared. Acquire a 16GB+ microSD card (8GB is also sufficient, but at one point you will require a blank 4GB+ USB storage device) and follow the instructions for installing Raspbian at <https://www.raspberrypi.org/documentation/installation/installing-images/README.md>.

After downloading the latest version from the raspberry pi foundation and imaging a microSD card with it, boot the raspberrry pi from it by inserting the microSD card into it and supplying power. Now you will be provided with a menu. You should expand the filesystem, change the password and enable the camera. You may at this point want to increase the graphics memory split from 128 (MB) to 256. You can do this within Advanced Options, under Memory Split.

### Packages
Edit `/etc/apt/sources.list` with your favourite text editor, e.g. `nano`, or `vi` (`sudo nano /etc/apt/sources.list`) and change `wheezy` to `jessie` (or later) to get the appropriate packages. Now update the cache using `sudo apt-get -y update` and the distribution with `sudo apt-get -y dist-upgrade`. *This may take a while*. Finally let's recover some space with `sudo apt-get -y clean`. Finally, update your firmware to the latest version by running `sudo rpi-update`.

    sudo nano /etc/apt/sources.list
    sudo apt-get -y update
    sudo apt-get -y dist-upgrade
    sudo apt-get -y clean
    sudo rpi-update

Select 'yes' when prompted!

Now obtain our software, entering your password as needed:

    cd ~
    git clone https://github.com/sourtin/igem15-sw.git
    cd igem15-sw
    git submodule init
    git submodule update

We've set it all up for you, but for further configuring wifi access, you can edit raspi_conf/hostapd.conf (`nano raspi_conf/hostapd.conf`) - here you can change the broadcast wifi network name and password.

_NOTE: At this point, if you have opted for a smaller microSD card, it may be necessary to provide some extra storage until after setup.sh has been run (after which you may remove the extra storage). Plug in a USB stick of at least 4GB capacity and make sure it is formatted to ext2+. Mount this partition on ~/tmp (format and mount by running ```mkdir -p ~/tmp; sudo mkfs.ext4 /dev/sda1; sudo mount /dev/sda1 ~/tmp``` where /dev/sda1 should be replaced with the device file represented by your usb storage device) and follow the next steps as usual._

Now you are ready to start installing packages!

    sudo ./setup.sh

There! Wasn't that easy? You're welcome :)

After it has finished successfully, you can remove ~/tmp (unless you want to recompile opencv later more quickly) and reboot the pi:

    rm -rf ~/tmp/*
    sudo reboot
