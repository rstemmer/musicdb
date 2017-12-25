
MusicDB Test VMs
================

To test MusicDB I created some VMs with different Linux distributions.
Most time I test on my productive installation.

To run a test system execute the following line:

.. code-block:: bash

   qemu-system-x86_64 -hda $SYSDISK -hdb MusicDB.cow -hdc music.cow -m 1024 -net user,hostfwd=tcp::10022-:22 -net nic -enable-kvm 

qemu Installation
-----------------

Basic Setup
^^^^^^^^^^^

.. code-block:: bash

   # Install qemu
   pacman -S qemu-headless

   # Create a VM directory for BTRFS
   mkdir /data/vms
   chattr +C /data/vms
   chown user:user /data/vms

Disk Images
^^^^^^^^^^^

I use multiple images to make the test environment more composable:

   * System image: ``$DISTNAME.cow``
   * Music collection: ``music.cow`` (mount read only to allow multiple OSs to access that device)

.. code-block:: bash

   qemu-img create -f qcow2 /data/vms/$DISTNAME.cow 20G
   qemu-img create -f qcow2 /data/vms/music.cow 10G


System Setup
------------

All system installations have the following setup:

   * Language: ``English`` (Location: ``Germany/Berlin``, Locales: ``de_DE.UTF-8``)
   * User: ``user:user`` with id ``1000:1000`` and group
   * Patitioning: Using the assistant; home on same partition; for the distribution recommended setup.
   * Installation: Minimal system. No GUI if possible.

Task to do for each new system:

   * Install: vim, git
   * edit fstap: 
      * music-disk: ``/data/music``

.. code-block:: bash

   mkdir -p /data/music


Installing/Updating MusicDB Test Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``icecast`` is not needed because it only handles encryption what is not necessary for test runs.

.. code-block:: bash

   # download
   mkdir /src
   cd /src
   git clone git@m45ch1n3.de:/data/git/musicdb.git

   cd /src/musicdb
   ./musicdb-check.sh   # Install all missing dependencies
   ./install.sh


Create Dummy Files
^^^^^^^^^^^^^^^^^^

The following code shows, how to create a simple fake song.
To create a complete fake album, the script ``testenv/mkalbum.sh`` can be used.
Before executing the it, edit the variables at the beginning of the script.

.. code-block:: bash

   # Generate 3 minutes and 37 seconds silence
   sox -n -r 44100 -c 2 silence.wav trim 0.0 3:37

   # Encode it as mpeg3
   lame silence.wav

   # Set meta data
   id3edit --create --set-name "Silence" --set-album "Full of Null" --set-artist "Lame Sox" --set-release "2017" --set-track "01/10" --set-cd "1/1" silence.mp3

Test Systems
------------

Debian
^^^^^^

**Version:** 9.1.0 AMD64

I used a *qemu* installation with GUI on my development PC to install Debian.
Later I copied the debain.cow image onto my workstation and use it via *qemu-headless*.

Selected Software: ``web server``, ``SSH server``, ``standard system utilities``. *NO* desktop or print server.

.. code-block:: bash

   # Download
   wget https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-9.1.0-amd64-netinst.iso

   # Install
   qemu-system-x86_64 -cdrom debian-9.1.0-amd64-netinst.iso -hda debian.cow -boot order=d -m 1024

   # Setup (first run)
   qemu-system-x86_64 -hda debian.cow -m 1024 -net user,hostfwd=tcp::10022-:22 -net nic -enable-kvm
   ssh user@localhost -p10022

.. attention::

   After installing MPD, the daemon gets started via systemd (enabled!!)

   So, after installing MPD run the following commands:

   .. code-block:: bash

      systemctl stop mpd
      systemctl disable mpd


.. attention::

   On Debian, the icecast executable is called ``icecast2``, not ``icecast``

.. attention::

   On Debian, uses the ancient Python 2 when calling ``python``! m(

Raspian
^^^^^^^

TODO
https://azeria-labs.com/emulate-raspberry-pi-with-qemu/

Arch Linux
^^^^^^^^^^

**Version:** *latest* (x86-64)

Compared to my development system that is also Arch Linux, this is only a minimal installation.
Furthermore, I use this VM to test an installation without any MusicAI components including its dependencies.
It also does not have an ``icecast`` installation.
So, this is the minimum environment MusicDB must have to run.

Selected Software: ``base``, ``base-devel``, ``vim``, ``git``, ``openssh``, ``ifplugd``

.. code-block:: bash

   # Download
   wget https://ftp.fau.de/archlinux/iso/2017.09.01/archlinux-2017.09.01-x86_64.iso

   # Install
   qemu-system-x86_64 -cdrom archlinux-2017.09.01-x86_64.iso -hda arch.cow -boot order=d -m 1024
   

