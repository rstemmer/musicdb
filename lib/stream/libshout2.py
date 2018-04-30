# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 
# 2017, Edoardo Negri
# 2018, Ralf Stemmer <ralf.stemmer@gmx.net>
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
"""
This module is a highly modified fork of `Shouty <https://github.com/edne/shouty/>`_ - A python wrapper for *libshout2*.
Sadly the project seems to be dead or at least sleeping.
That's why this fork is necessary.

The module provides a wrapper for the shout library that will be used to access `Icecast <https://icecast.org/>`_.
For the Icecast interface, another module :mod:`lib.stream.icecast` is provided that uses this module.
"""

import logging
import atexit
import ctypes.util
from ctypes import CDLL, c_int, c_char_p, c_void_p, c_size_t
from enum   import IntEnum

so_file = ctypes.util.find_library('shout')

if not so_file:
    raise Exception('Library libshout not found')

lib = CDLL(so_file)
lib.shout_init()
atexit.register(lib.shout_shutdown)

class Error(IntEnum):
    SUCCESS     =   0
    INSANE      =  -1
    NOCONNECT   =  -2
    NOLOGIN     =  -3
    SOCKET      =  -4
    MALLOC      =  -5
    METADATA    =  -6
    CONNECTED   =  -7
    UNCONNECTED =  -8
    UNSUPPORTED =  -9
    BUSY        = -10
    NOTLS       = -11
    TLSBADCERT  = -12
    RETRY       = -13


class Format(IntEnum):
    OGG         = 0
    MP3         = 1
    WEBM        = 2
    WEBMAUDIO   = 3


class Protocol(IntEnum):
    HTTP        = 0
    XAUDIOCAST  = 1
    ICY         = 2
    ROARAUDIO   = 3



def check_error_code(f):
    def decorated(self, *args, **kwargs):
        error = f(self, *args, **kwargs)

        if error != Error.SUCCESS:
            error_name = Error(error).name

            lib.shout_get_error.restype = c_char_p
            lib.shout_get_error.argtypes = [c_void_p]
            error_desc = lib.shout_get_error(self.obj).decode()

            raise Exception('Failed {}! Error code: {} - {}'.format(f.__name__, error_name, error_desc))
    return decorated



class LibShout2(object):
    """

    Args:

    Example:

        .. code-block:: python

            # Create IcecastInterface object
    """

    def __init__(self,
                   host='localhost', port=8000,
                   user='source', password='',
                   protocol=Protocol.HTTP,
                   format=Format.OGG,
                   mount='/shout',
                   dumpfile=None, agent=None,
                   public=0,
                   name=None, url=None, genre=None, description=None,
                   audio_info=None):
        logging.debug('Init connection')

        # Create new shout object
        lib.shout_new.restype = c_void_p
        self.obj = lib.shout_new()
        if not self.obj:
            raise Exception('Memory error')

        # Setup libshout
        self.set_int(lib.shout_set_port, port)
        self.set_str(lib.shout_set_host, host)

        self.set_str(lib.shout_set_user, user)
        self.set_str(lib.shout_set_password, password)

        self.set_int(lib.shout_set_protocol, protocol)
        self.set_int(lib.shout_set_format, format)
        self.set_str(lib.shout_set_mount, mount)

        self.set_optional_str(lib.shout_set_dumpfile, dumpfile)
        self.set_optional_str(lib.shout_set_agent, agent)

        self.set_int(lib.shout_set_public, public)

        self.set_optional_str(lib.shout_set_name, name)
        self.set_optional_str(lib.shout_set_url, url)
        self.set_optional_str(lib.shout_set_genre, genre)
        self.set_optional_str(lib.shout_set_description, description)

        lib.shout_set_audio_info.argtypes = [c_void_p, c_char_p, c_char_p]
        if audio_info:
            for k, v in audio_info.items():
                self.set_audio_info(k, v)

        # Setup API
        lib.shout_open.argtypes = [c_void_p]
        lib.shout_send.argtypes = [c_void_p, c_char_p, c_size_t]
        lib.shout_sync.argtypes = [c_void_p]
        lib.shout_close.argtypes = [c_void_p]
        lib.shout_free.argtypes = [c_void_p]

    @check_error_code
    def set_str(self, f, s):
        f.argtypes = [c_void_p, c_char_p]
        return f(self.obj, s.encode("utf-8"))

    @check_error_code
    def set_int(self, f, n):
        f.argtypes = [c_void_p, c_int]
        return f(self.obj, n)

    def set_optional_str(self, f, s):
        if s:
            self.set_str(f, s)

    @check_error_code
    def set_audio_info(self, name, value):
        return lib.shout_set_audio_info(self.obj, name.encode("utf-8"), value.encode("utf-8"))

    def metadata_new(self):
        lib.shout_metadata_new.restype = c_void_p
        return lib.shout_metadata_new()

    @check_error_code
    def metadata_free(self, metadata):
        lib.shout_metadata_free.argtypes = [c_void_p]
        return lib.shout_metadata_free(metadata)

    @check_error_code
    def metadata_add(self, metadata, name, value):
        lib.shout_metadata_add.argtypes = [c_void_p, c_char_p, c_char_p]
        return lib.shout_metadata_add(metadata, name.encode("utf-8"), value.encode("utf-8"))

    @check_error_code
    def set_metadata(self, metadata):
        lib.shout_set_metadata.argtypes = [c_void_p, c_void_p]
        return lib.shout_set_metadata(self.obj, metadata)

    def set_metadata_song(self, songname):
        metadata = self.metadata_new()
        self.metadata_add(metadata, "song", songname)
        self.set_metadata(metadata)
        self.metadata_free(metadata)

    @check_error_code
    def open(self):
        logging.debug("Open connection")
        return lib.shout_open(self.obj)

    @check_error_code
    def send(self, chunk):
        return lib.shout_send(self.obj, chunk, len(chunk))

    def sync(self):
        return lib.shout_sync(self.obj)

    @check_error_code
    def close(self):
        logging.debug("Close connection")
        return lib.shout_close(self.obj)

    def free(self):
        logging.debug("Free library")
        lib.shout_free(self.obj)



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

