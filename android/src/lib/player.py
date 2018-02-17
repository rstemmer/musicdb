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

from jnius import autoclass

class MusicPlayer(object):
    # source: https://stackoverflow.com/questions/45061116/playing-mp3-on-android
    def __init__(self):
        MediaPlayer = autoclass('android.media.MediaPlayer')
        self.mplayer = MediaPlayer()

        self.secs = 0
        self.actualsong = ''
        self.length = 0
        self.isplaying = False

    def __del__(self):
        self.stop()
        self.mplayer.release()

    def load(self, filename):
        try:
            self.actualsong = filename
            self.secs = 0
            self.mplayer.setDataSource(filename)        
            self.mplayer.prepare()
            self.length = self.mplayer.getDuration() / 1000
            return True
        except Exception as e:
            return False

    def unload(self):
        self.mplayer.reset()

    def play(self):
        self.mplayer.start()
        self.isplaying = True

    def stop(self):
        self.mplayer.stop()
        self.secs=0
        self.isplaying = False

    def seek(self,timepos_secs):
        self.mplayer.seekTo(timepos_secs * 1000)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

