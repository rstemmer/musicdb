#!/usr/bin/env python3

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
"""
This module handles the reading and writing of ini-files.
The definition of names is shown in the ini file example below.

    .. code-block:: ini

        [section]
        option = value
"""

import configparser

class Config(configparser.ConfigParser, object):

    def __init__(self, filename=None):
        """
        If a file name is given, the file gets read.
        """
        super(Config, self).__init__()

        self.__filename       = None
        self.__allownonevalue = False

        if filename:
            self.Load(filename)


    def AllowNoneValue(self, allow=True):
        """
        This method enables the possibility to configure (read) a ``None`` value.
        In case a value has the string ``"None"``, the :meth:`~lib.cfg.config.Config.Get` method returns ``None``.
        The upper case N is important!

        Default behavior of this class is to return the string ``"None"`` as regular string.

        Args:
            allow (bool): if ``True`` none values are allowed, otherwise the string ``"None"`` gets returned as a string

        Returns:
            ``None``

        Example:

            .. code-block:: ini

                [test]
                option = None

            .. code-block:: python

                cfg = Config("test.ini")
                
                x = cfg.Get(str, "test", "option")
                print(type(x))  # str
                
                cfg.AllowNoneValue()

                x = cfg.Get(str, "test", "option")
                print(type(x))  # NoneType
                
        """
        self.__allownonevalue = allow
        return None


    def Load(self, path=None):
        """
        This method loads a configuration file.
        If the *path* parameter is not ``None``, the path given while instantiating the class will be overwritten.
        If the file was already loaded, it gets reloaded.

        Args:
            path (str): Absolute path to an ini file

        Returns:
            *Nothing*

        Raises:
            AssertionError: If internal path variable and parameter is ``None``. (No path given)
        """
        if path == None and self.__filename == None:
            raise AssertionError("No filename was given to load")
        if path:
            self.__filename = path

        self.read(self.__filename)
  
  
    def Reload(self):
        """
        This method just calls :meth:`~lib.cfg.config.Config.Load` without a path argument.
        """
        self.Load()
  
  
    def Save(self):
        """
        This method saves all set values back to the configuration file.

        .. attention:

            Calling this method removes all comments from the file.
            The used library recreates and reformates the whole file.

        Changing configuration can be prevented by setting the file attributes to read only.

        If writing fails not because of missing write permission, an exception gets raised.
        """
        try:
            with open(self.__filename, "w") as configfile:
                self.write(configfile)
        except IOError as e:
            if e[0] != 13:
                raise e # The user shall be able to forbid me messing up his config :D
  
  
    def OptionAvailable(self, section, option):
        """
        This method can be used to check if an option exists in the configuration file.

        Args:
            section (str): Name of the section
            option (str): Name of the option

        Returns:
            ``True`` if the option exists, otherwise ``False``
        """
        if self.has_option(section, option):
            return True
        else:
            return False

  
    # todo: auf allownonevalue eingegeh und dass None auch als default einfließen kann
    def Get(self, datatype, section, option, default=None, islist=False):
        """
        This method reads a value from the configuration.
        The values in the file are all stored as string.
        Using the *datatype* parameter will convert that string into a python data type.

        The default parameter can be used to define a value that shall be returned in case the option does not exist.
        This value can be of a different type than defined by the datatype parameter.

        If the value of an option is ``"None"``, and none type is allowed by calling :meth:`~lib.cfg.config.Config.AllowNoneValue`, ``None`` gets returned.

        If the *islist* parameter is set to ``True``, the read value gets interpreted as comma separated list and split.
        A list of the striped values (without leading or trailing spaces) gets returned casted to the data type given by the *datatype* parameter.

        Args:
            datatype: The data type of the value. This can be ``bool``, ``int``, ``float`` or ``str``.
            section (str): Name of the section to read from
            option (str): Name of the option to read
            default: Default value in case the option does not exist
            islist (bool): Interpret the value as a comma separated list

        Returns:
            The value of an option

        Example:

            .. code-block:: ini

                [test]
                integer = 1000
                list = 13, 23, 42

            .. code-block:: python

                cfg = Config("test.ini")

                x = cfg.Get(int, "test", "integer")
                print(x)    # 1000

                x = cfg.Get(int, "test", "list", [], True)
                print(x)    # [13, 23, 42]
                
                x = cfg.Get(int, "test", "noneexisting", 1337)
                print(x)    # 1337
        """
  
        if not self.has_option(section, option):
            return default
  
        try:
            if self.__allownonevalue == True:
                entry = self.get(section, option)
                if entry == "None":
                    return None
  
            if islist == True:
                entries = self.get(section, option)
                values  = [datatype(x.strip()) for x in entries.split(",")]
                return values
  
            #value = datatype(self.get(section, option))
            if datatype == bool:
                value = self.getboolean(section, option)
            elif datatype == int:
                value = self.getint(section, option)
            elif datatype == str:
                value = self.get(section, option)
            elif datatype == float:
                value = self.getfloat(section, option)
  
        except ValueError:
            return default
  
        return value
  
  
    def Set(self, section, option, value):
        """
        This method sets an option.
        The value gets casted to a string.
        If the section or option does not exist, it will be created.

        After setting the option, the :meth:`~lib.cfg.config.Config.Save` method gets called to store the changes.
        This is necessary because there is no reliable destructor in python to.

        Args:
            section (str): Section to write at
            option (str): Name of the option to set
            value: Value to store

        Returns:
            *Nothing*
        """
        if not self.has_section(section):
            self.add_section(section)
  
        self.set(section, option, str(value))
  
        try:
            secobj = getattr(self, section)
            setattr(secobj, option, value)
        except Exception as e:
            pass
  
        self.Save() # save after every change… necessary because there are no reliable destructors in python


if __name__ == "__main__":
    import sys

    try:
        filename = str(sys.argv[1])
        section  = str(sys.argv[2])
        item     = str(sys.argv[3])
    except:
        print("args: filename section item [default]")
        exit(1)
    
    default  = None
    try:
        default = str(sys.argv[4])
    except:
        pass
        
    try:
        config = Config(filename)
        value  = config.Get(str, section, item, default)
        print(value)
    except Exception as e:
        print(e, file=stderr)

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

