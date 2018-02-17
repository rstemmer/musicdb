#!/usr/bin/env python3

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

