__copyright__ = '''
main.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

import sys

from seqpy import set_cout, cout
from insane import QtGui, QtCore, QtWidgets
from insane.core.base import ienv
from insane.core.base.windows import BaseMainwin
from insane.core.base.menu import CommonMenuBar
from insane.core.base.messagebox import progress, alert
from insane.core.base.consolelog import writelog
from .actions import IMainActions

class IMainWindow(BaseMainwin):

    def __init__(self, parent=None):
        super(IMainWindow, self).__init__( parent )

        self.default_env = ienv.IEnv()
        self._actions = IMainActions( self )

        self.custom_actions().populate_menubar( self.menuBar() )

    def custom_actions(self):
        return self._actions

    def load(self, filename):
        """ open a file and set up appropriate frame """
        self._actions.file_open(filename)

    def view(self, obj):
        self._actions.view( obj )

    def focusInEvent(self, ev):
        self.setWindowTitle('seqpy/InSAnE')


def main():

    app = QtWidgets.QApplication(sys.argv)

    # patching seqpy.cout
    set_cout( writelog )
    cout('console log ready..')

    try:
        infile = sys.argv[1]
    except IndexError:
        infile = None

    w = IMainWindow()
    w.show()

    if infile:
        # allow all windows to be drawn
        QtCore.QTimer.singleShot(100, lambda: w.load( infile ))
    else:
        w.setFocus()
    app.exec_()


if __name__ == '__main__':
    main()
