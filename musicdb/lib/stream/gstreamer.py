# MusicDB,  a music manager with web-bases UI that focus on music.
# Copyright (C) 2018 - 2021  Ralf Stemmer <ralf.stemmer@gmx.net>
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
GStreamer Pipeline
------------------

Installation
^^^^^^^^^^^^

    .. code-block:: bash

        pacman -S gst-plugins-good gst-python gst-plugins-bad
        # -good for mp3
        # -bad  for m4a/aac

Example
^^^^^^^

    .. code-block:: bash

        gst-launch-1.0 filesrc location=in.m4a ! decodebin ! audioconvert ! lamemp3enc target=1 bitrate=320 cbr=true ! filesink location=out.mp3

"""

import logging
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst

class GStreamerInterface(object):
    r"""
    This class provides a simple abstraction to the GStreamer Python module.
    The class is made to manage one pipeline that can be executed in a thread.
    Therefore a state machine is implemented providing the following states.
    The state represent the state of the pipeline execution process.
    The current state can be checked by calling :meth:`~GetState`

    IDLE:
        After instantiating the state machine is in IDLE state, as well as after the pipeline was completely executed.

    RUNNING:
        When the pipeline gets executed, the state machine is in RUNNING state.
        This happens when the blocking method :meth:`~Execute` got called.
        This method is thread save an can be executed concurrently.

    CANCEL:
        When the state machine is in this state, the RUNNING state will be left.
        This is state that can be forced by calling :meth:`~Cancel`.

    ERROR:
        When an error occures, the state machine goes into the ERROR state.
        This state will never be left!

    .. graphviz::

        digraph finite_state_machine {
            size="8,12"

            node [shape = circle, color=black, fontsize=10, label="IDLE"    ] idle;
            node [shape = circle, color=black, fontsize=10, label="RUNNING" ] running;
            node [shape = circle, color=black, fontsize=10, label="CANCEL"  ] cancel;
            node [shape = circle, color=black, fontsize=10, label="ERROR"   ] error;

            idle    -> running [ label = "GStreamerInterface.Execute()\n/ GStreamer Pipeline State := PLAYING" ];
            idle    -> error   [ label = "Starting GStreamer Pipeline failed" ];
            running -> cancel  [ label = "GStreamer Error Message" ];
            running -> cancel  [ label = "GStreamer EOS Message" ];
            cancel  -> idle    [ label = "/ GStreamer Pipeline State := NULL" ];
            running -> error   [ label = "Tried to start pipeline that was not IDLE" ];
            cancel  -> error   [ label = "Tried to start pipeline that was not IDLE" ];
            
        }

    These state machine is independent from the `GStreamer Pipeline State Machine <https://gstreamer.freedesktop.org/documentation/design/states.html>`_!

    Args:
        pipelinename (str): Optional name for the pipeline

    """

    def __init__(self, pipelinename="pipeline"):
        self.pipeline = Gst.Pipeline.new(pipelinename)
        self.state    = "IDLE"



    def CreateElement(self, elementname, name):
        """
        This method adds a GStreamer Element to the GStreamer Pipeline.
        When the element exists and gets added successfully, its instance gets returned.
        Otherwise ``None`` will be returned.

        Args:
            elementname (str): name of the GStreamer Element as it is used by GStreamer
            name(str): A unique name for the instance of the element that gets added to the Pipeline

        Returns:
            ``None`` on error, otherwise the instance of the added GStreamer Element.

        Example:

            Creates a new pipeline named ``"example"``.
            Then two elements from the GStreamer core elements called ``filesrc`` and ``decodebin`` gets added to the Pipeline.
            As source location the m4a file ``test.m4a`` will be set.
            Then, the source gets linked to the decoder.

            .. code-block:: python

                gstreamer = GStreamerInterface("example")
                source    = gstreamer.CreateElement("filesrc",   "source")
                decoder   = gstreamer.CreateElement("decodebin", "decoder")

                source.set_property("location", "./test.m4a")
                source.link(decoder)

            For more details about the ``filesrc`` and ``decodebin`` elements, call the following bash commands:

            .. code-block:: bash
    
                gst-inspect-1.0 filesrc
                gst-inspect-1.0 decodebin

        """
        # Find element
        factory = Gst.ElementFactory.find(elementname)
        if not factory:
            logging.error("GStreamer Element %s not installed! - Adding %s failed.", elementname, name)
            return None

        # Create instance of element
        element = Gst.ElementFactory.create(factory, name)
        if not element:
            logging.error("GStreamer Element %s not created, even though it exists! - Adding %s failed.", elementname, name)
            return None

        # Add element to pipeline
        self.pipeline.add(element)
        return element


    
    def GetState(self):
        """
        Returns:
            The current state of the GStreamer Pipeline execution as string

        """
        return self.state



    def Cancel(self):
        """
        This method cancels the current running execution of the GStreamer Pipeline.
        It sets the state to CANCEL only when the current state is RUNNING.
        Otherwise nothing will be changed.
        """
        if self.state == "RUNNING":
            self.state = "CANCEL"



    # TODO Control flow
    def Execute(self):
        """
        Only call this method when the pipeline execution is in IDLE state!

        Example:

            Running the pipeline as thread

            .. code-block:: python

                gstreamer = GStreamerInterface()
                
                # … Setup pipeline …

                def StartPipelineThread():
                    # Start GStreamer pipeline
                    gstreamerthread = Thread(target=gstreamer.Execute)
                    gstreamerthread.start()

                    # Wait until the pipeline actually started
                    while True:
                        state = gstreamer.GetState()
                        if state == "RUNNING":
                            return True
                        elif state != "IDLE":
                            print("Unexpected gstreamer state: %s"%(gstate))
                            return False

        """
        if self.state != "IDLE":
            logging.error("GStreamer Interface was not in IDLE state but in %s state. Entering ERROR state!", self.state)
            self.state = "ERROR"
            return

        # start playing
        ret = self.pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            logging.error("Unable to set the GStreamer Pipeline to the PLAYING state")
            self.state = "ERROR"
            return

        bus = self.pipeline.get_bus()

        self.state = "RUNNING"
        while self.state == "RUNNING":
            message = bus.timed_pop_filtered(0.1 * Gst.SECOND, Gst.MessageType.ERROR | Gst.MessageType.WARNING | Gst.MessageType.EOS)
            if message:
                messagetype = message.type
                if messagetype == Gst.MessageType.ERROR:
                    error, dbg = message.parse_error()
                    logging.error("GStreamer error for element %s: %s", message.src.get_name(), error.message)
                    if dbg:
                        logging.debug("Detailed information for previous GStreamer error: %s", dbg)
                    self.Cancel()
                elif messagetype == Gst.MessageType.WARNING:
                    warn, dbg = message.parse_warning()
                    logging.warning("GStreamer warning for element %s: %s", message.src.get_name(), warn.message)
                    if dbg:
                        logging.debug("Detailed information for previous GStreamer warning: %s", dbg)
                elif messagetype == Gst.MessageType.EOS:
                    self.Cancel()
                else:
                    # this should never happen
                    logging.warning("Unexpected message received from GStreamer bus!")

        self.pipeline.set_state(Gst.State.NULL)
        self.state = "IDLE"



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

