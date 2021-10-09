#!/usr/bin/env python

import re
import sys
from musicdb.musicdb import main

if __name__ == "__main__":
    print("\033[1;33m     " + "▰"*31)
    print("\033[1;31m !☠! \033[1;33mTest Run from Source Repository\033[1;31m !☠! \033[0m")
    print("\033[1;33m     " + "▰"*31)
    sys.argv[0] = re.sub(r"(-script\.pyw|\.exe)?$", "", sys.argv[0])
    sys.exit(main())
