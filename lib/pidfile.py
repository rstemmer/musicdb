# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017  Ralf Stemmer <ralf.stemmer@gmx.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os


def CreatePIDFile(pidfile, pid=None):
    """
    This function creates a PID file.
    If the process ID is not given via *pid*-argument, the current PID will be determined.

    The PID gets written into the file addressed by the *pidfile* parameter.
    If the file does not exist (it should not) a new one will be created.
    The path shall be absolute!

    Args:
        pidfile (str): absolute path for the PID file.
        pid: The Process ID. If ``None`` the PID gets determined.

    Returns:
        ``None``

    Example:

        .. code-block:: python

            CreatePIDFile("/tmp/test.pid")
            CreatePIDFile("/tmp/fake.pid", 1000)
    """
    if pid == None:
        pid = os.getpid()

    if type(pid) == int:
        pid = str(pid)

    with open(pidfile, "w+") as f:
        f.write(pid + "\n")

    return None



def DeletePIDFile(pidfile):
    """
    This function removes the PID file (or any other file) addressed by an absolute path in *pidfile*.

    Args:
        pidfile (str): Absolute path of a file to remove

    Returns:
        ``None``
    """
    os.remove(pidfile)
    return None



def CheckPIDFile(pidfile):
    """
    This function checks whether a PID file exists or not.
    If the file *pidfile* does exist its content, a process ID, gets read and returned.
    If the file does not exist, ``None`` gets returned.

    Args:
        pidfile (str): Absolute path to a PID file

    Returns:
        The stored process ID if the file exists, otherwise ``None``.
        The PID is of type int.

    Example:

        .. code-block:: python

            server = CheckPIDFile("/tmp/server.pid"):
            if server:
                print("Server has PID %d."%(server))
            else:
                print("There is no server running!")

    """
    try:
        with open(pidfile, "r") as f:
            pid = f.read()

        pid = pid.strip()
        pid = int(pid)
    except:
        pid = None

    return pid


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

