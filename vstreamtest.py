#!/usr/bin/env python3

# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2017-2020  Ralf Stemmer <ralf.stemmer@gmx.net>
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

import argparse
import importlib.util
import os
import sys
import grp
import time
from threading import Thread
from lib.stream.icecast     import IcecastInterface
from lib.stream.gstreamer   import GStreamerInterface
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

def VideoTranscode(gstreamer, path):

    source    = gstreamer.CreateElement("filesrc",      "source")
    decoder   = gstreamer.CreateElement("decodebin",    "decoder")
    # videoconvert ???
    encoder   = gstreamer.CreateElement("vp8enc",       "encoder")
    mux       = gstreamer.CreateElement("webmmux",      "mux")
    sink      = gstreamer.CreateElement("fdsink",       "sink")


    unixpipesource, unixpipesink = os.pipe2(os.O_NONBLOCK)

    source.set_property("location", path)
    #encoder.set_property("target", 1)
    #encoder.set_property("bitrate", 320)
    #encoder.set_property("cbr", True)
    sink.set_property("fd", unixpipesink)
    
    source.link(decoder)
    encoder.link(mux)
    mux.link(sink)
    decoder.connect("pad-added", onDecoderPadAdded)
    return unixpipesource

def onDecoderPadAdded(dbin, pad):
    decoder   = pad.get_parent()
    pipeline  = decoder.get_parent()
    encoder   = pipeline.get_by_name('encoder')
    decoder.link(converter)

def GetChunk(gstreamer, gstreamerthread, unixpipesource, size):
    retval = bytes()
    while size > 0:
        try:
            print("Try to read %i bytes from unixpipesource"%(size))
            chunk = os.read(unixpipesource, size)
        except BlockingIOError:
            if gstreamer.GetState() == "RUNNING":
                # Buffer empty - just wait a bit for GStreamer, then continue
                time.sleep(0.1)
                continue

            gstreamerthread.join()
            gstreamerthread = None
            break

        if len(chunk) == 0 and gstreamer.GetState() != "RUNNING":
            gstreamerthread.join()
            gstreamerthread = None
            break

        size -= len(chunk)
        retval += chunk
        if size > 0:
            time.sleep(0.01)

    print("Succeeded reading chunk from unixpipesource")
    return retval

if __name__ == "__main__":
    GObject.threads_init()
    Gst.init(None)
    icecast = IcecastInterface(6666, "source", "PW#0source@icecast", "/vstream")
    gstreamer = GStreamerInterface("videotranscoder")

    icecast.Connect()
    icecast.UpdateTitle("Video Test")

    gstreamerthread = Thread(target=gstreamer.Execute)
    gstreamerthread.start()

    unixpipesource = VideoTranscode(gstreamer, "/data/music/Eisbrecher/2012\ -\ Miststück\ \(2012\).m4v")

    while True:
        gstate = gstreamer.GetState()
        if gstate != "RUNNING":
            break

        chunk = GetChunk(gstreamer, gstreamerthread, unixpipesource, 4096)
        print("Streaming chunk via IceCast")
        icecast.StreamChunk(chunk)
        time.sleep(0.1)

    icecast.Disconnect()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

