__copyright__ = '''
commonmenu.py - part of seqpy/InSAnE

(c) 2011 - 2012, Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

import sys, os
from insane import QtGui, QtCore, QtWidgets

Instances = set()

class CustomMenuBar(QtWidgets.QMenuBar):

    pass

class CustomMenu(QtWidgets.QMenu):

    def __init__(self, label='', parent=None):
        super(CustomMenu, self).__init__(label, parent)
        self._submenus = []
        self._pane = None

    def xxx_pane(self):
        return self.parent().pane()

    def xxx_model(self):
        return self.pane().model()

    def mainwin(self):
        return self._container.mainwin()

    def add_actions(self, actions):
        if type(actions) != list:
            actions = [ actions ]
        for action_item in actions:
            if action_item is None:
                self.addSeparator()
            elif type(action_item) == tuple or type(action_item) == list:
                submenu = CustomMenu( action_item[0], self )
                submenu.add_actions( action_item[1] )
                self.addMenu( submenu )
                # below is necessary for preventing from garbage-collected!
                self._submenus.append( submenu )
            else:
                self.addAction(action_item)




class MenuContainer_XXX( object ):

    def __init__(self, pane):
        self._pane = pane
        self._menubar = None
        self._menu_list = []
        self.prepare_menu()

    def prepare_menu(self):
        self._menubar = QtGui.QMenuBar()
        self.init_menu()

    def attach(self, mainwin):
        if mainwin.menuBar() == self._menubar:
            return
        try:
            mainwin.setMenuBar( self._menubar )
        except RuntimeError:
            self.prepare_menu()
            mainwin.setMenuBar( self._menubar )

    def populate_menu(self, menulist):
        for menu_label, menu_items in menulist:
            m = CustomMenu( menu_label )
            self._menubar.addMenu( m )
            m.add_actions( menu_items )

    def pane(self):
        return self._pane

    def custom_actions(self):
        return self.pane().custom_actions()

    def menubar(self):
        # XXX: this should create NEW menubar because the underlying C/C++ object
        # will be deleted after MainWindow unrelease this 8-(
        return self._menubar

    def init_menu(self):
        pass

    def get_mainwin(self):
        """ traversal to get root window / mainwindow """
        widget = self.pane()
        while widget != None:
            if isinstance(widget, QtGui.QMainWindow):
                return widget
            widget = widget.parent()
        return None


class CommonMenuBar(QtWidgets.QMenuBar):

    def __init__(self, pane=None):
        super(CommonMenuBar, self).__init__()
        self._pane = pane
        self.init_menu()

    def set_pane(self, pane):
        self._pane = pane

    def init_menu(self):
        pass

    def custom_actions_XXX(self):
        return self._pane.custom_actions()

    def populate_menu_XXX(self, menulist):
        for menu_label, menu_items in menulist:
            m = CustomMenu( menu_label, self )
            self.addMenu( m )
            m.add_actions( menu_items )


class IMenuBar(QtWidgets.QMenuBar):

    def __init__(self, parent=None):
        super(IMenuBar, self).__init__( parent )
        self.setAcceptDrops(True)
        print("IMenuBar.__init__()")

    def dropEvent(self, ev):
        print("Dropping here...")

    def addMenu(self, m):
        super(IMenuBar, self).addMenu( m )
        #print("Adding menu...")
