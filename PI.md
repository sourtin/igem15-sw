# Installation instructions
It is easiest to just use the preprepared disk image provided, however if you wish to customise the install more advanced instructions are also provided. We have provided the steps we used to construct the provided install, but feel free to deviate from the instructions as much as you wish, just remember to use an ARM-specific binaries and to obtain python 3.4+.

## Premade Image

## Operating System
First the installation media must be prepared. Acquire an 8GB (4GB is probably sufficient, larger is also fine) microSD card and connect it to a linux installation. Mac instructions should be similar assuming you are familiar with the terminal and can install ext4 fuse via homebrew. We wish Windows users the best of luck!

Look for the device name using `lsblk`. You can do this either by looking for one with the right size or by comparing the results of `lsblk` before and after plugging in the SD card. It may be /dev/sdX where X is a letter, mmcblk, or something else entirely. Below, we use /dev/sdX, replace it with your device name!!!!

1. Login as root, or run `su -`
2. `fdisk /dev/sdX` to create the partitions:
   Wipe the partition table!
    o
   Create the first (1) primary (p) partition at the first sector (<enter>) and 100MB big
    n
    p
    1
    <enter>
    +100M
   Make it FAT32
    t
    c
   Create the second (2) primary (p) partition at the next aligned sector (<enter>) and running to the end (<enter>)
    n
    p
    2
    <enter>
    <enter>
   Confirm and write!
    w
3. Create the file systems: 
    mkfs.vfat /dev/sdX1
    mkfs.ext4 /dev/sdX2
4. Mount the filesystems:
    cd /tmp
    mkdir -p boot root
    mount /dev/sdX1 boot
    mount /dev/sdX2 root
5. Acquire Arch:
   For the first pi (ARMv6):
    wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-latest.tar.gz
    bsdtar -xpf ArchLinuxARM-rpi-latest.tar.gz -C root
   For the second (ARMv7):
    wget http://archlinuxarm.org/os/ArchLinuxARM-rpi-2-latest.tar.gz
    bsdtar -xpf ArchLinuxARM-rpi-2-latest.tar.gz -C root
6. Bootloader
    sync
    mv root/boot/* boot
    sync
    umount boot root

You should now have a blank Arch install with default user 'alarm', password 'alarm', and root password 'root'.


