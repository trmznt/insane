__copyright__ = '''
commonstatusbar.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

import sys, os
from insane import QtGui, QtCore, QtWidgets

class IStatusBar( object ):

    def __init__(self, pane):
        self._pane = pane
        self._statusbar = None
        self.prepare_statusbar()


    def prepare_statusbar(self, ):
        self._statusbar = QtGui.QStatusBar()
        self.init_statusbar()

    def attach(self, mainwin):
        self.set_mainwin( mainwin )
        if mainwin.statusBar() == self._statusbar:
            return
        try:
            mainwin.setStatusBar( self._statusbar )
        except RuntimeError:
            self.prepare_statusbar()
            mainwin.setStatusBar( self._statusbar )

    def mainwin(self):
        return self._mainwin

    def set_mainwin(self, mainwin):
        self._mainwin = mainwin

    def show(self, statusbar):
        raise NotImplementedError('Please provide implementation in inherited class')

    def hide(self, statusbar):
        raise NotImplementedError('Please provide implementation in inherited class')

    def init_statusbar(self):
        """ this can be overloaded by child """
        raise NotImplementedError('Please provide implementation in inherited class')




