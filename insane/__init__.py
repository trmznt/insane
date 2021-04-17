
from PyQt5 import QtGui, QtCore, QtWidgets

import sys, os

# prepare seqpy/extlib path to sys.path
sys.path.append( os.path.join(os.path.split( os.path.split(__file__)[0] )[0], 'insane/extlib' ))

def main():
    from insane.core.main import mainwin
    mainwin.main()


