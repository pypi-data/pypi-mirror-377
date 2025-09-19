#!/usr/bin/env python3
"""
grblhub: a command line tool to handle grbl code.
"""

import os
import sys
import atexit
import argparse
import readline
from grblhud import __version__
from grblhud.grblhudloop import grblhudloop
from grblhud.grblhudloop import GRBLHUDCOMMANDS

try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        print("Import error: either 'toml' must be installed (pip install toml) or python version must be 3.11 or higher!")
        sys.exit(1)

import readline

class LineinputCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            if text:  # cache matches (entries that start with entered text)
                self.matches = [s for s in self.options
                                    if s and s.startswith(text)]
            else:  # no text entered, all matches possible
                self.matches = self.options[:]

        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None

config_file = os.path.expanduser(f"~/.config/{os.path.basename(sys.argv[0])}.toml")

def create_parser():
    """
    grblhud argument(s) parser
    """
    # defaults
    cfg = {
        "serial_default" : "/dev/ttyUSB0",
    }

    if os.path.exists(config_file):
        print(f"read settings from: {config_file}")
        with open(config_file, 'rb') as f:
            cfg.update({k + '_default': v for k,v in tomllib.load(f).items()})

    parser = argparse.ArgumentParser( description="Interactive grbl1.1 control center.\n"
                                                  "  Type 'grblhud file' to stream file(s) to your machine\n"
                                                  "  Type 'grblhud<enter>' to start the interactive 'hud'."
                                      , formatter_class=argparse.RawTextHelpFormatter )

    parser.add_argument('--serial', default=cfg["serial_default"], metavar="<default:" + str(cfg["serial_default"])+">", help='serial device of your machine (115200 baud)')
    parser.add_argument('gcode', type=argparse.FileType('r'),nargs='*', help='gcode file(s) to stream to your machine')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s ' + __version__, help="show version number and exit")

    return parser

def main():
    """
    grblhud main
    """
    # command history handling
    histfile = os.path.join(os.path.expanduser("~"), ".grblhud_history")
    try:
        readline.read_history_file(histfile)
        # default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    #completer = MyCompleter([ "help", "exit", "OS", "os", "stream", "load", "run", "listgcode", "showgcode", "setLOOP", "S+", "S-",
    #                          "F+", "F-", "softstop", "softreset", "hardreset", "sleep", "Zprobe", "origin", "Bbox", "bbox" ])
    completer = LineinputCompleter(GRBLHUDCOMMANDS)
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')

    atexit.register(readline.write_history_file, histfile)

    # get commandline arguments
    args = create_parser().parse_args()

    grblhudloop(args)

if __name__ == '__main__':
    main()
