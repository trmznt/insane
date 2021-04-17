__copyright__ = '''
commonactions.py - part of seqpy/InSAnE

(c) 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets
from insane.core.base.menu import CustomMenu
from insane.core.base.consolelog import show_console
import sys, os


class CustomActions(object):
    """ This class holds actions for both menubar, context menu and toolbar """

    def __init__(self, pane):
        self._pane = pane

        self.init_actions()
        self.init_toolbar()

    def pane(self):
        return self._pane

    def model(self):
        return self._pane.model()

    def selection(self):
        return self.model().selection()

    def caret(self):
        return self._pane.caret()

    def create_action(self, text, slot=None, shortcut=None, icon=None,
                tip=None, checkable=False):
        action = QtWidgets.QAction(text, self.pane())
        if icon is not None:
            action.setIcon( QtGui.QIcon(":/images%s.png" % icon) )
        if shortcut is not None:
            action.setShortcut( shortcut )
        if tip is not None:
            action.setToolTip( tip )
            action.setStatusTip( tip )
        if slot is not None:
            action.triggered.connect( slot )
        if checkable:
            action.setCheckable( True )
        return action

    def init_actions(self):
        pass

    def populate_menubar(self, menubar):
        """ this is necessary so that main page drawing won't occur when we change
            menubar content
        """
        menubar.clear()
        for menu_label, menu_items in self.menu_layout():
            m = CustomMenu( menu_label, menubar )
            menubar.addMenu( m )
            m.add_actions( menu_items )

    def populate_contextmenu(self, menu):
        for menu_items in self.contextmenu_layout():
            menu.add_actions( menu_items )

    def populate_toolbar(self, toolbar):
        """ this is necessary so that main page drawing won't occur when we change
            toolbar content
        """
        toolbar.clear()


    def menu_layout(self):
        raise NotImplementedError

    def contextmenu_layout(self):
        raise NotImplementedError

    def selectionmenu_layout(self):
        raise NotImplementedError

    def toolbar_layout(self):
        raise NotImplementedError

    def statusbar_layout(self):
        raise NotImplementedError


    # TOOLBAR UTILITIES
    
    def init_toolbar(self):
        pass



class CommonPaneActions(CustomActions):


    def init_actions(self):

        ## FILE ACTIONS

        self._NEW = self.create_action( "&New", self.file_new,
                            QtGui.QKeySequence.New, "new", "Create a new alignment")

        self._NEWDBSEQ = self.create_action( 'New dbSeq', self.file_newdbseq,
                            None, None, None )

        self._OPEN = self.create_action( "&Open", self.file_open,
                            QtGui.QKeySequence.Open, "open", "Open alignment file")

        self._SAVE = self.create_action( "&Save", self.file_save,
                            QtGui.QKeySequence.Save, "save", "Save alignment" )

        self._SAVEAS = self.create_action( "Save &as", self.file_saveas,
                            QtGui.QKeySequence.SaveAs, "saveas", "Save alignment as")

        self._CLOSE = self.create_action( "&Close", self.file_close,
                            "Ctrl+Q", "close", "Close alignment")

        self._EXIT = self.create_action( "&Exit", self.file_exit,
                            "Ctrl+E", "exit", "Exit application")

        self._EXPORT = self.create_action( "Export", self.file_export,
                            None, "export", "Export to")

        self._IMPORT = self.create_action( "Import", self.file_import,
                            None, "import", "Import from")

        ## EDIT ACTIONS

        self._UNDO = self.create_action( "&Undo", self.edit_undo,
                    QtGui.QKeySequence.Undo, "undo", "Undo last action")

        self._REDO = self.create_action( "&Redo", self.edit_redo,
                    QtGui.QKeySequence.Redo, "redo", "Redo last action")

        self._COPY = self.create_action( "Copy", self.edit_copy,
                    QtGui.QKeySequence.Copy, "copy", "Copy sequence(s)")

        self._CUT = self.create_action( "Cut", self.edit_cut,
                    QtGui.QKeySequence.Cut, "cut", "Cut sequence(s)")

        self._PASTE = self.create_action( "Paste", self.edit_paste,
                    QtGui.QKeySequence.Paste, "paste", "Paste sequence(s)")

        self._PASTESPECIAL = None

        self._PREF = self.create_action( "Preference", self.edit_preference,
                    None, None, None )

        ## WINDOW ACTIONS

        self._SHOWCONSOLE = self.create_action("Show Console", self.window_showconsole,
                    None, None, None )

        ## HELP ACTIONS

        self._ABOUT = self.create_action( 'About', self.help_about,
                    None, 'about', 'About seqpy/InSAnE')


    ## ACTION SLOTS
    
    def file_new(self):
        pass

    def file_newdbseq(self):
        pass

    def file_open(self):
        pass

    def file_save(self):
        pass

    def file_saveas(self):
        pass

    def file_import(self):
        pass

    def file_export(self):
        pass

    def file_close(self):
        if len(self._mainwin.Instances) > 1:
            self._mainwin.close()
        else:
            self._mainwin.delete_centralwidget()

    def file_exit(self):
        sys.exit()

    def load_file(self, filename):
        pass

    def edit_undo(self):
        pass

    def edit_redo(self):
        pass

    def edit_copy(self):
        pass

    def edit_paste(self):
        pass

    def edit_cut(self):
        pass

    def edit_preference(self):
        pass

    def window_showconsole(self):
        show_console()

    def help_about(self):
        pass

    def get_mainwin(self):
        """ traversal to get root window / mainwindow """
        widget = self.pane()
        while widget != None:
            if isinstance(widget, QtWidgets.QMainWindow):
                return widget
            widget = widget.parent()
        return None

