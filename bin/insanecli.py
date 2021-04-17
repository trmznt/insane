#!/usr/bin/env python3

__copyright__ = '''
spcli - part of seqpy

(c) 2011-2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

##
## insane.py - insane start up
##

import sys, os

# prepare path to insane
os.environ['QT_API'] = 'pyqt5'
sys.path.append( os.path.split( os.path.split(__file__)[0] )[0] )

import insane

def greet():
    seqpy.cerr('insane - Integrated Sequence Alignment and Editor')
    seqpy.cerr('(C) 2011-2012 Hidayat Trimarsanto <trimarsanto@gmail.com>')

def usage():
    seqpy.cerr('  usage:')
    seqpy.cerr('    insane [-e scriptfile] [CMD PARAMS]')
    sys.exit(1)

def main():

    insane.main()
    sys.exit(1)

    greet()
    if len(sys.argv) == 1:
        usage()

    if sys.argv[1] == '-e':
        # will execute a script file
        pass

    else:
        from seqpy import cmds
        cmds.execute( sys.argv[1:] )
        


if __name__ == '__main__':
    main()



