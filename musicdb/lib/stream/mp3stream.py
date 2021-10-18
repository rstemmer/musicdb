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
This module provides a class to read any audio file and provide it as mp3 frames.
Transcoding is done by the :doc:`/lib/mp3transcoder` module.
"""
import sys
import logging
from musicdb.lib.stream.mp3transcoder import MP3Transcoder

BitrateTable = [ # in kilo
            [ # MPEG-2 & 2.5
                [   0,  32,  48,  56,  64,  80,  96, 112, 128, 144, 160, 176, 192, 224, 256, None ], # Layer 1
                [   0,   8,  16,  24,  32,  40,  48,  56,  64,  80,  96, 112, 128, 144, 160, None ], # Layer 2
                [   0,   8,  16,  24,  32,  40,  48,  56,  64,  80,  96, 112, 128, 144, 160, None ]  # Layer 3
            ],                                                                               
                                                                                             
            [ # MPEG-1                                                                  
                [   0,  32,  64,  96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448, None ], # Layer 1
                [   0,  32,  48,  56,  64,  80,  96, 112, 128, 160, 192, 224, 256, 320, 384, None ], # Layer 2
                [   0,  32,  40,  48,  56,  64,  80,  96, 112, 128, 160, 192, 224, 256, 320, None ]  # Layer 3
            ]
        ]

SamplerateTable = [
            [ 11025, 12000,  8000, None ], # MPEG-2.5
            [  None,  None,  None, None ], # reserved
            [ 22050, 24000, 16000, None ], # MPEG-2
            [ 44100, 48000, 32000, None ], # MPEG-1
        ]

FrameSamplesTable = [
            [  384, 1152,  576, None ], # MPEG-2.5
            [ None, None, None, None ], # reserved
            [  384, 1152,  576, None ], # MPEG-2
            [  384, 1152, 1152, None ]  # MPEG-1
        ]

ModeTable = [ "stereo", "joint stereo", "dual channel", "mono" ]

ModeExtensionTable = [
            [ "4-31", "8-31", "12-31", "16-31" ], # Layer 1
            [ "4-31", "8-31", "12-31", "16-31" ], # Layer 2
            [     "",   "IS",    "MS", "IS+MS" ]  # Layer 3
        ]

EmphaseTable = [ "none", "50/15 ms", "reserved", "CCIT J.17" ]

SlotsizeTable = [ 4, 1, 1, None ]


class MP3Stream(object):
    """
    This class allows frame wise access to mp3 frames generated from an valid audio file by transcoding it.
    See :doc:`/lib/mp3transcoder` for more details about the transcoding process.
    The frame wise access can be done by the :meth:`~Frames` generator.
    Beside the mp3 frames the generator returns lots of information extracted from the mp3 Frame Header.    

    This class expects a valid audio file and provides an MPEG Layer III mp3 stream without any meta data like an ID3 Tag.

    As soon as the object gets created, it starts the transcoding process.

    Args:
        path (str/Path):
            An absolute path to a valid audio file

    Example:
        
        .. code-block:: python

            mp3stream = MP3Stream("/tmp/test.m4a")  # Start transcoding
            for frame in mp3stream.Frames():        # Access mp3 frames
                print(frame["header"])
    """

    def __init__(self, path):
        self.path = path



    def Frames(self):
        r"""
        This is a generator that returns a mp3 frame each iteration.
        There will be no ID3 Tag or any other meta data.

        The returned dictionary contains the following information:

            * ``"frame"`` (bytes): A complete MP3 Frame including the Frame Header and the Frame Data
            * ``"header"`` (dict): The interpretation of the MP3 Frame Header as returned by :meth:`AnalyzeHeader`

        The following diagram shows how this method loads and processes the audio file:

        .. graphviz::

            digraph hierarchy {
                size="5,8"
                start           [label="Start"];


                readmp3header   [shape=box,     label="Read MP3 Frame Header"]
                analyzeheader   [shape=box,     label="Analyze MP3 Frame Header"]
                readmp3frame    [shape=box,     label="Read MP3 Frame"]
                savemp3frame    [shape=box,     label="Yield MP3 Frame"]

                end             [label="End"];

                start           -> readmp3header

                readmp3header   -> analyzeheader
                analyzeheader   -> readmp3frame
                readmp3frame    -> savemp3frame
                savemp3frame    -> readmp3header

                readmp3header   -> end              [label="No further data"]
            }


        When the Version code of an MP3 frame is not as expected, a warning will be printed.
        This warning will only be printed once for each file.

        Returns:
            A generator that returns a dictionary including a mp3 frame

        Raises:
            ValueError: When the MP3 Sync Bits are not correct

        Example:

            .. code-block:: python

                mp3stream = MP3Stream("/tmp/test.m4a")
                for frame in mp3stream.Frames():
                    print(frame["header"])

        """

        VersionCheckWarningPrinted = False

        with MP3Transcoder(self.path) as transcoder:
            while True:
                # read the next frame header (4 bytes)
                mp3header = transcoder.GetChunk(4)
                if len(mp3header) == 0:
                    break   # end of stream

                # roughly check if the header is valid
                headerchunk = int.from_bytes(mp3header[:2], byteorder='big', signed=False)  # Get first 2 bytes from header
                syncbits    = headerchunk &  0xFFE0
                version     = headerchunk & ~0xFFE0

                if syncbits != 0xFFE0:
                    raise ValueError("Expected Frame Sync Bits wrong! First two bytes of the MP3 Frame Header should be \"0xFFFE\", not \"%s\"!", hex(syncbits))

                if version != 0x1B and not VersionCheckWarningPrinted:
                    logging.warning("Unexpected MP3 Version Code \"%s\". Should be \"0x1b\". \033[1;30m(This only indicates an invalid MP3 file. Transcoding will be continued.)", hex(version))
                    VersionCheckWarningPrinted = True   # Print this warning only once per file

                # Read MP3 Header
                infos    = self.AnalyzeHeader(mp3header) # Analyze header
                datasize = infos["framesize"] - 4        # 4 bytes MP3 Frame Header already read, rest are MP3 Frame Data

                # Drop Frame Tag
                mp3frame = mp3header + transcoder.GetChunk(datasize)
                frame = {}
                frame["frame"] = mp3frame
                frame["header"]= infos
                yield frame



    def AnalyzeHeader(self, header):
        r"""
        This method analyzes a MP3 Frame Header and returns all information that are implicit included in these 4 bytes.
        It is build for the internal use inside this class.

        Primary source for analyzing the header is `mpgedit.org (no HTTPS) <http://mpgedit.org/mpgedit/mpeg_format/MP3Format.html>`_
        Another important source is `Wikipedia <https://en.wikipedia.org/wiki/MP3#Design>`_

        Base of the implementation of this method is from `a python script from Vivake Gupta (vivake AT lab49.com) <https://www.w3.org/2000/10/swap/pim/mp3/mp3info.py>`_
        A further helpful code example comes from `SirNickity from the hydrogenaud.io community <https://hydrogenaud.io/index.php?topic=85125.msg747716#msg747716>`_

        Those codes were improved by me to get information I need.
        These information (and more) are returned as dictionary.
        The returned dictionary contains the following keys:

            * Relevant information:
                * ``"framesize"`` (int): Size of a frame in the MP3 file. This includes the 4 bytes of the MP3 Frame Header.
                * ``"frametime"`` (float): The playtime of the audio in milliseconds that is encoded in one frame
                * ``"layer"`` (int): MPEG layer. For MP3 it should be ``3``
                * ``"mpeg version"`` (int): MPEG version. For MP3, it should be ``1``
            * Further information (I have no idea what some of the information mean. They are simply not relevant anyway.):
                * ``"protection"`` (bool): When ``True`` the header has a CRC16 checksum
                * ``"padding"`` (bool): When ``True`` the frame is padded with an extra slot. (The slot size is given in ``"slotsize"``)
                * ``"private"`` (bool): *free to use*
                * ``"mode"`` (str): Channel mode: ``"stereo"``, ``"joint stereo"``, ``"dual channel"`` or ``"mono"``
                * ``"modeextension"`` (str): For MPEG Layer 1 and 2: ``"4-31"``, ``"8-31"``, ``"12-31"`` or ``"16-31"``. For MPEG Layer 3: ``""`` (empty), ``"IS"``, ``"MS"`` or ``"IS+MS"``. ``"IS"`` stands for *Intensity Stereo Mode*, ``"MS"`` for *MS Stereo Mode*
                * ``"copyright"`` (bool): Copyrighted data
                * ``"original"`` (bool): Original data
                * ``"emphasis"`` (str): One of the following strings: ``"none"``, ``"50/15 ms"``, ``"reserved"`` or ``"CCIT J.17"``
                * ``"samples"`` (int): Samples per frame
                * ``"slotsize"`` (int): The size of one slot
                * ``"bitspersample"`` (int): Bit per sample
                * ``"samplerate"`` (int): Samplerate

        Args:
            header (int/bytes): The 4 byte MP3 Frame Header in bytes, or as integer (unsigned, big endian!)

        Returns:
            A dictionary with all information encoded in the header

        Raises:
            TypeError: When ``header`` is not of type bytes or int.
            ValueError: When there are invalid information encoded in the header.

        Example:

            .. code-block:: python

                # ...
                header = mp3stream.GetChunk(4)

                if header[:2] != b"\xFF\xFB":
                    raise ValueError("Expected Frame Sync Bits missing")
                try:
                    infos = self.AnalyzeHeader(header)
                except ValueError as e:
                    print("Invalid header! Problem: %s"%(str(e)))
                    
        """
        if type(header) == bytes:
            header = int.from_bytes(header, byteorder='big', signed=False)

        if type(header) != int:
            raise TypeError("The argument must be of type bytes, or an integer! Actual type is %s"%(str(type(header))))

        # The comments relate to this article: http://mpgedit.org/mpgedit/mpeg_format/MP3Format.html
        mpeg_version =    (header >> 19) & 3  # BB   00 = MPEG2.5, 01 = res, 10 = MPEG2, 11 = MPEG1  
        layer =           (header >> 17) & 3  # CC   00 = res, 01 = Layer 3, 10 = Layer 2, 11 = Layer 1
        protection_bit =  (header >> 16) & 1  # D    0 = protected, 1 = not protected
        bitrateindex =    (header >> 12) & 15 # EEEE 0000 = free, 1111 = bad
        samplerateindex = (header >> 10) & 3  # F    11 = res
        padding_bit =     (header >> 9)  & 1  # G    0 = not padded, 1 = padded
        private_bit =     (header >> 8)  & 1  # H
        mode =            (header >> 6)  & 3  # II   00 = stereo, 01 = joint stereo, 10 = dual channel, 11 = mono
        mode_extension =  (header >> 4)  & 3  # JJ
        copyright =       (header >> 3)  & 1  # K    00 = not copyrighted, 01 = copyrighted                            
        original =        (header >> 2)  & 1  # L    00 = copy, 01 = original                                          
        emphasis =        (header >> 0)  & 3  # MM   00 = none, 01 = 50/15 ms, 10 = res, 11 = CCIT J.17 

        infos = {}

        # Uncomment to get intermediate values
        #infos["dbg_mpeg_version"]   = mpeg_version
        #infos["dbg_layer"]          = layer
        #infos["dbg_protection_bit"] = protection_bit
        #infos["dbg_bitrateindex"]   = bitrateindex
        #infos["dbg_samplerateindex"]= samplerateindex
        #infos["dbg_padding_bit"]    = padding_bit
        #infos["dbg_private_bit"]    = private_bit
        #infos["dbg_mode"]           = mode
        #infos["dbg_mode_extension"] = mode_extension
        #infos["dbg_copyright"]      = copyright
        #infos["dbg_original"]       = original
        #infos["dbg_emphasis"]       = emphasis

        # Check version
        if mpeg_version == 0:
            infos["mpeg version"] = 2.5
        elif mpeg_version == 2:
            infos["mpeg version"] = 2
        elif mpeg_version == 3:
            infos["mpeg version"] = 1
        else:
            raise ValueError("Invalid MPEG version code. %i ∉ {0,2,3}"%(mpeg_version))

        # Check Layer
        if layer == 1:
            infos["layer"] = 3
        elif layer == 2:
            infos["layer"] = 2
        elif layer == 3:
            infos["layer"] = 1
        else:
            raise ValueError("Invalid MPEG layer code. $i ∉ {1,2,3}"%(layer))

        infos["bitrate"]    = BitrateTable[mpeg_version & 1][infos["layer"] - 1][bitrateindex] * 1000
        infos["samplerate"] = SamplerateTable[mpeg_version][samplerateindex]

        if infos["bitrate"] is None:
            raise ValueError("Invalid bit rate code %i"%(bitrateindex))
        
        if infos["samplerate"] is None:
            raise ValueError("Invalid sample rate code %i"%(samplerateindex))

        infos["protection"]     = not bool(protection_bit)
        infos["padding"]        = bool(padding_bit)
        infos["private"]        = bool(private_bit)
        infos["mode"]           = ModeTable[mode]
        infos["modeextension"]  = ModeExtensionTable[infos["layer"] - 1][mode_extension]
        infos["copyright"]      = bool(copyright)
        infos["original"]       = bool(original)
        infos["emphasis"]       = EmphaseTable[emphasis]
        infos["samples"]        = FrameSamplesTable[mpeg_version][infos["layer"] - 1]
        infos["slotsize"]       = SlotsizeTable[infos["layer"] - 1]
        infos["bitspersample"]  = infos["samples"] / 8.0;
        infos["framesize"]      = (infos["bitspersample"] * infos["bitrate"]) / infos["samplerate"]
        infos["frametime"]      = (infos["samples"] / infos["samplerate"]) * 1000
        if infos["padding"]:
            infos["framesize"] += infos["slotsize"]

        # Frame size must be an integer - it is the size in bytes
        infos["framesize"] = int(infos["framesize"])

        return infos



# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

