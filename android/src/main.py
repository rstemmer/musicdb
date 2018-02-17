#!/usr/bin/env python2
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

import kivy
kivy.require('1.10.0')

try:
    import logging
except:
    from kivy.logger import Logger as logging
import os
import sys

from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label     import Label
from kivy.uix.button    import Button
from kivy.uix.textinput import TextInput
from kivy.uix.settings  import Settings, SettingsWithSidebar, SettingsWithSpinner, SettingsWithTabbedPanel


# When there is a syntax error in a module, buildozer does not inform the developer.
# It just does not add that module to the APK.
# So to not iterate through all modules, just leave an error message and continue.
# Then all can be fixed together.
try:
    from lib.player import MusicPlayer
except ImportError:
    logging.error("importing lib.player failed!")

try:
    from lib.websocketclient import WebSocketClient
except ImportError:
    logging.error("importing lib.websocketclient failed!")

try:
    from lib.httpclient import HTTPClient
except ImportError:
    logging.error("importing lib.httpclient failed!")

try:
    from ui.settings import SettingsView
except ImportError:
    logging.error("importing ui.settings failed!")


class MyApp(App):
    def build(self):
        self.settings_cls = SettingsWithSpinner

        screen = BoxLayout(orientation="vertical")

        self.playbutton = Button(text="Play")
        self.playbutton.bind(on_press=self.onPlayPressed)
        self.downloadbutton = Button(text="Download")
        self.downloadbutton.bind(on_press=self.onDownloadPressed)
        actionbox = BoxLayout(orientation="vertical")
        actionbox.add_widget(self.downloadbutton)
        actionbox.add_widget(self.playbutton)

        self.wsconnectbutton = Button(text="WS Connect")
        self.wsconnectbutton.bind(on_press=self.onWSConnectPressed)
        self.wsrequestbutton = Button(text="WS Request")
        self.wsrequestbutton.bind(on_press=self.onWSRequestPressed)
        self.wsdisconnectbutton = Button(text="WS Close")
        self.wsdisconnectbutton.bind(on_press=self.onWSDisconnectPressed)
        wsbox = BoxLayout(orientation="vertical")
        wsbox.add_widget(self.wsconnectbutton)
        wsbox.add_widget(self.wsrequestbutton)
        wsbox.add_widget(self.wsdisconnectbutton)

        self.settingsbutton = Button(text="Settings")
        self.settingsbutton.bind(on_press=self.onSettingsPressed)

        buttonbox = BoxLayout(orientation="horizontal")
        buttonbox.add_widget(actionbox)
        buttonbox.add_widget(wsbox)
        buttonbox.add_widget(self.settingsbutton)

        screen.add_widget(buttonbox)

        import os
        files = os.listdir(".")
        
        self.textwidget = TextInput(text="Initializing …\n%s\n%s\n\n"%(str(sys.version_info), str(files)))
        screen.add_widget(self.textwidget)

        # Create Music Player instance
        self.mplayer = MusicPlayer()

        # Create HTTP Client instance 
        self.httpclient = HTTPClient(
                url         = self.config.get("Network", "httpserver"),
                rootdir     = self.user_data_dir,
                certificate = None)

        # Create WebSocket Client instance
        self.wsclient = WebSocketClient(url = self.config.get("Network", "websocketserver"))

        return screen
    

    def build_config(self, config):
        """
        Set the default values for the configs sections.
        """
        config.setdefaults('Network', 
                {
                    "httpserver": "https://localhost/musicdb",
                    "websocketserver": "wss://localhost:9000"
                })

    def build_settings(self, settings):
        """
        Add our custom section to the default configuration object.
        """
        settings.add_json_panel("Network", self.config, "ui/networksettings.json")

    def on_config_change(self, config, section, key, value):
        """
        Respond to changes in the configuration.
        """
        self.Print("Config changed: [{0}]->{1} = {2}\n".format(section, key, value))

        if section == "Network" and key == "httpserver":
            self.httpclient.httpurl = value
        elif section == "Network" and key == "websocketserver":
            self.wsclient.wsurl = value

    def close_settings(self, settings=None):
        """
        The settings panel has been closed.
        """
        self.Print("Setting dialog closed.\n")
        App.close_settings(self, settings)



    def on_start(self):
        self.Print("on_start\n")

    def on_resume(self):
        self.Print("on_resume\n")

    def on_pause(self):
        self.Print("on_pause\n")
        # True: allow resume; False: stop app
        return True

    def on_stop(self):
        pass



    def Print(self, string):
        self.textwidget.insert_text(string)



    def onSettingsPressed(self, button):
        self.open_settings()



    def onDownloadPressed(self, button):
        self.Print("Downloading from HTTP server: ")
        try:
            self.httpclient.DownloadFile("music/Rammstein/2001 - Mutter/03 Sonne.m4a", "03 Sonne.m4a")
        except Exception as e:
            self.Print("failed!\n%s\n"%(str(e)))
        else:
            self.Print("done\n")



    def onWSConnectPressed(self, button):
        self.Print("Connecting to WS server: ")
        try:
            retval = self.wsclient.Connect()
        except Exception as e:
            self.Print("failed!\n%s\n"%(str(e)))
            return

        if retval == True:
            self.Print("done\n")
        else:
            self.Print("failed!\n")


    def onWSRequestPressed(self, button):
        self.Print("Receiving from WS server: ")
        retval = self.wsclient.Receive()
        if retval:
            self.Print("done\n")
            self.Print("%s\n"%(retval))
        else:
            self.Print("failed!\n")


    def onWSDisconnectPressed(self, button):
        self.Print("Disconnecting from WS server: ")
        retval = self.wsclient.Disconnect()
        if retval == True:
            self.Print("done\n")
        else:
            self.Print("failed!\n")



    def onPlayPressed(self, button):
        if self.mplayer.isplaying:
            self.StopMusic()
        else:
            path = os.path.join(self.user_data_dir, "03 Sonne.m4a")
            self.PlayMusic(path)


    def PlayMusic(self, path):
        self.Print("Playing %s…\n"%(path))
        if not os.path.exists(path):
            self.Print("Song file " + path + " does not exist!\n")
            return None

        self.mplayer.stop()
        if self.mplayer.load(path):
            self.mplayer.play()
        else:
            self.Print("Loading song file failed!\n")


    def StopMusic(self):
        self.Print("Stopping music…\n")
        self.mplayer.stop()
        self.mplayer.unload()



if __name__ == "__main__":
    MyApp().run()


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

