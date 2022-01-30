import argparse
from musicdb.lib.modapi         import MDBModule
from musicdb.lib.cfg.musicdb    import MusicDBConfig
from musicdb.lib.db.musicdb     import MusicDatabase

class module(MDBModule):
    def __init__(self, config, database):
        MDBModule.__init__(self)


    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="This is an example module")
        parser.set_defaults(module=modulename)


    # return exit-code
    def MDBM_Main(self, args):

        # execute command
        try:
            print("Hello from MusicDB")
            return 0
        except:
            return 1

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

