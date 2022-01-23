
extern - Music File Exporter
============================

.. automodule:: musicdb.mod.extern

File Export to External Device
------------------------------

It is recommended to write a short script to automate the update-process.
The following script mounts a SD-Card and runs the update-process.

.. code-block:: bash

   #!/usr/bin/env bash
    
   # Path to the storage device that shall be updated
   DEVICE="/dev/disk/by-id/usb-SD_USB3_Reader_000000000002-0:2-part1"
    
   if [ ! -L "$DEVICE" ] ; then
     echo -e "\e[1;31mDevice \"$DEVICE\" does not exist!\e[0m"
     exit 1
   fi

   echo -e "\e[1;34mRunning update …\e[0m"

   sudo mount $DEVICE /mnt
   musicdb extern -u /mnt
   sudo umount /mnt
    
   echo -e "\e[1;37mupdate complete\e[0m"
    
   exit 0
