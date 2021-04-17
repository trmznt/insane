__copyright__ = '''
commontoolbar.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

import sys, os
from insane import QtGui, QtCore, QtWidgets

class IToolBar( object ):

    def __init__( self, pane, title=None ):
        self._pane = pane
        self._toolbar = None
        self.prepare_toolbar(title)

    def prepare_toolbar(self, title):
        if title:
            self._toolbar = QtGui.QToolBar( title )
        else:
            self._toolbar = QtGui.QToolBar()
        self.init_toolbar()

    def pane(self):
        return self._pane

    def attach(self, mainwin):
        try:
            mainwin.addToolBar( self._toolbar )
        except RuntimeError:
            self.prepare_toolbar()
            mainwin.addToolBar( self._toolbar )

    def init_toolbar(self):
        pass

    def add_popup(self, text, popup):
        act = self._toolbar.addAction( text, popup._popup )
        popup.set_toolbutton( self._toolbar.widgetForAction( act ) )


class PopupSlider( QtWidgets.QFrame ):

    def __init__(self, parent=None, orientation=QtCore.Qt.Vertical, length=100):
        super(PopupSlider, self).__init__( parent, QtCore.Qt.Popup )
        self._slider = QtWidgets.QSlider(orientation)
        self._toolbutton = None
        if orientation == QtCore.Qt.Vertical:
            self.resize( self._slider.sizeHint().width(), 100 )
        else:
            self.resize( 100, self._slider.sizeHint().height() )

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget( self._slider, 0 )
        self.setLayout( layout )

    def toolbutton(self):
        return self._toolbutton

    def set_toolbutton(self, toolbutton):
        self._toolbutton = toolbutton

    def slider(self):
        return self._slider

    def add_as_popup(self, toolbar, text):
        act = toolbar.addAction( text, self._popup )
        self.set_toolbutton( toolbar.widgetForAction( act ) )

    def _popup(self):
        self.move(
            self._toolbutton.parent().mapToGlobal(self._toolbutton.geometry().bottomLeft()))
        self.show()

