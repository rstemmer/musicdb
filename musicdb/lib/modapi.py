import argparse

class MDBModule(object):

    @staticmethod
    def MDBM_CreateArgumentParser(parserset, modulename):
        parser = parserset.add_parser(modulename, help="FATAL: MISSING IMPLEMENTATION MDBM_CreateArgumentParser(parserset, modulename)")
        parser.set_defaults(module=modulename)

    # return exit-code
    def MDBM_Main(self, args):
        print("FATAL: MISSING IMPLEMENTATION MDBM_Main(self, args)")
        return 1

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

