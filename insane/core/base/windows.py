__copyright__ = '''
windows.py - part of seqpy/InSAnE

(c) 2011, 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

"""
This module sets up the communication between various window segments:
  - MainWindow
  - Frame
  - Pane
  - View
"""

from insane import QtGui, QtCore, QtWidgets
from .menu import CommonMenuBar, CustomMenu, IMenuBar
from .debug import D, ALL, INFO
import sys




class ISplitterHandle(QtWidgets.QSplitterHandle):

    def __init__(self, orient, parent=None):
        super(ISplitterHandle, self).__init__( orient, parent )


class ISplitter(QtWidgets.QSplitter):

    def __init__(self, orient, parent=None):
        super(ISplitter, self).__init__( orient, parent )
        self.setHandleWidth(1)

    def createHandle(self):
        return ISplitterHandle( self.orientation(), self )


class IFixedSplitterHandle(QtWidgets.QSplitterHandle):

    def __init__(self, orient, parent=None):
        super(IFixedSplitterHandle, self).__init__( orient, parent )
        self.setDisabled(True)

    def paintEvent(self, ev):
        return

class IFixedSplitter(QtWidgets.QSplitter):

    def __init__(self, orient, parent=None):
        super(IFixedSplitter, self).__init__( orient, parent )
        self.setHandleWidth(1)

    def createHandle(self):
        return IFixedSplitterHandle( self.orientation(), self )

    def paintEvent(self, ev):
        return


class BaseMainwin(QtWidgets.QMainWindow):
    """ BaseMainwin

        This class holds single main frame as well as universal menubar
    """

    _instances = set()

    def __init__(self, parent=None):
        super(BaseMainwin, self).__init__( parent )
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self._instances.add( self )

        self._menu = None
        self._mainframe = None
        self._model = None          # main model
        self._activepane = None     # currently active pane
        self.setMenuBar( IMenuBar() )
        self._menubar = self.menuBar()
        self._toolbar = self.addToolBar("ToolBar")


    def mainframe(self):
        """ return mainframe
        """
        return self._mainframe

    def set_model(self, model):
        self._model = model

    def model(self):
        return self._model

    def show_centralwidget(self, mainframe):
        """ prepare central widget, set to self._mainframe and set to central widget and
            set menubar to frame's default menubar
        """
        self._mainframe = mainframe
        #self._mainframe.installEventFilter( self._resizefilter )
        self.setCentralWidget( self._mainframe )
        # XXX: need to attach menubar, statusbar & toolbar before showing mainframe
        self._mainframe.menupane().focus_pane()


    def delete_centralwidget(self):
        """ hide and delete central widget
        """
        self._mainframe.hide()
        del sef._mainframe
        self._mainframe = None


    def sizeHint(self):
        return QtCore.QSize(800, 600)


    def closeEvent(self, ev):
        self._instances.remove( self )
        if len(self._instances) == 0:
            # we are the last mainwindow, so just exit as well
            sys.exit(0)


    def set_activepane(self, pane):
        if self._activepane != pane:

            # instead of replacing the menubar, toolbar & statusbar which will surely
            # redrawing the main window (2X, deleting the old one and adding the new one),
            # we just simply clear the content of current bar and re-populate it with new
            # content.
            pane.custom_actions().populate_menubar( self._menubar )
            pane.custom_actions().populate_toolbar( self._toolbar )

            statusbar = self.statusBar()
            new_statusbar = pane.statusbar()
            if self._activepane:
                old_statusbar = self._activepane.statusbar()
                if old_statusbar:
                    old_statusbar.hide( statusbar )
            if new_statusbar:
                new_statusbar.show( statusbar )

            self._activepane = pane


class BaseFrame(QtWidgets.QFrame):
    """ BaseFrame

        This class holds single main pane (usually LabelPane), multiple other panes
        (mostly SequencePane), and single vertical scrollbar pane within single horizontal
        splitter.
        
        Main pane, where model is kept, is the vscrollbarpane 8-). Obviously,
        the only thing that will relatively remain the same for the whole evolution of thi
        software.

        Each pane can hold its own model so that it would be possible for different pane
        to have different model, e.g. a TranslatedSequencePane to have a translatedmodel.

    """

    def __init__(self, env, parent=None):
        super(BaseFrame, self).__init__( parent )

        self._env = env
        self._vsplit = self.env().split()
        self._panes = []
        self._vscrollbarpane = None
        self._layout = None
        self._splitter = ISplitter( QtCore.Qt.Horizontal )
        self._block_resize_event = False


    def mainpane(self):
        return self._vscrollbarpane


    def menupane(self):
        return self._panes[0]


    def model(self):
        return self.mainpane().model()


    def set_env(self, env):
        self._env = env


    def env(self):
        if not self._env:
            raise RuntimeError( "env has not been set!" )
        return self._env


    def lineheight(self):
        return self.env().lineheight()


    def set_lineheight(self, height):
        self.env().set_lineheight( height )


    def vsplit(self):
        return self._vsplit

    def set_vsplit(self, n):
        #print "set split"
        self._vsplit = n
        for p in self._panes:
            p.set_split( n )
        if self._vscrollbarpane:
            self._vscrollbarpane.set_split( n )


    def insert_pane(self, pane, idx=-1):
        if pane.env() is None:
            # if no env has been set up for the pane, get from this frame
            pane.set_env( self.env() )
        pane.set_mainframe( self )
        pane.set_split( self.vsplit() )
        if idx == -1:
            self._panes.append( pane )
            self._splitter.addWidget( pane )
        else:
            raise NotImplemented('inserting pane at arbitrary position is not supported yet')

        if self._vscrollbarpane:
            # connect all signal/slot to VScrollbarPane
            self._vscrollbarpane.connect_pane( pane )

        # connect the rest of signal/slot
        pane.ActiveViewChanged.connect( self.set_activeview )


    def init_layout(self):
        self._layout = QtWidgets.QHBoxLayout()
        self._layout.setContentsMargins( 0,0,0,0 )
        self._layout.setSpacing( 0 )
        self._layout.addWidget( self._splitter, 1 )
        if self._vscrollbarpane:
            self._layout.addWidget( self._vscrollbarpane, 0)
        self.setLayout( self._layout )

    def init_vscrollbarpane(self, pane):
        self._vscrollbarpane = pane
        self._vscrollbarpane.set_split( self.vsplit() )


    # slots

    def set_activeview(self, view):
        self.parent().set_activepane( view.pane() )


class BasePane(QtWidgets.QFrame):
    """ BasePane

        This class holds model, individual env, horizontal splitter, pane-sensitive
        statusbar and menubar

        Layout:
        _layout ->  header
                    splitter (n)
                    footer

    """

    have_hscrollbar = True
    splitter_class = ISplitter
    #_MenuBar_ = None
    _ToolBar_ = None
    _StatusBar_ = None
    _PaneActions_ = None

    def __init__(self, model, view_class=None, parent=None):
        super(BasePane, self).__init__(parent)
        #self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)


        self._model = model
        self._env = None
        self._painter = None                # class responsible for actual painting/drawing
        self._hscrollbar = None             # horizontal scroll bar
        self._actions = None                # pane-sensitive actions
        self._menubar = None                # pane-sensitive menubar
        self._statusbar = None              # pane-sensitive statusbar
        self._toolbar = None                # pane-sensitive toolbar
        self._layout = None
        self._header = None
        self._footer = None

        self._view_class = view_class
        self._mainframe = None

        self._splitter = self.splitter_class(QtCore.Qt.Vertical)


        if self._PaneActions_:
            self.set_custom_actions( self._PaneActions_( self ) )
        
        #    if self._MenuBar_:
        #        self._menubar = self._MenuBar_( self )
        #    if self._ToolBar_:
        #        self._toolbar = self._ToolBar_( self )

        if self._StatusBar_:
            self.set_statusbar( self._StatusBar_( self ) )


    def model(self):
        return self._model

    def env(self):
        assert self._env
        return self._env

    def custom_actions(self):
        return self._actions

    def set_custom_actions(self, actions):
        self._actions = actions

    def set_env(self, env):
        self._env = env

    def layout(self):
        assert self._layout
        return self._layout

    def mainframe(self):
        return self._mainframe

    def set_mainframe(self, mainframe):
        self._mainframe = mainframe

    def menubar(self):
        return self._MenuBar_(self)

    def set_menubar(self, menubar):
        self._menubar = menubar

    def statusbar(self):
        return self._statusbar

    def set_statusbar(self, statusbar):
        self._statusbar = statusbar

    def toolbar(self):
        return self._toolbar

    def set_toolbar(self, toolbar):
        self._toolbar = toolbar

    def painter(self):
        return self._painter

    def set_painter(self, painter=None):
        self._painter = painter

    def add_mainwidget(self, w):
        self._splitter.addWidget( w )

    def lineheight(self):
        return self.env().lineheight()

    def charwidth(self):
        return self.env().charwidth()

    def hscrollbar(self):
        return self._hscrollbar

    def split(self):
        return self._splitter.count()


    def init_hscrollbar(self):
        """ this function initialize horizontal scrollbar, further setting up of
            the scrollbar will be performed during resizeEvent by width_hint()
        """
        if self.have_hscrollbar:
            self._hscrollbar = QtWidgets.QScrollBar( QtCore.Qt.Horizontal )
            self._layout.addWidget( self._hscrollbar )
        else:
            self._layout.addSpacing(
                    QtWidgets.QScrollBar( QtCore.Qt.Horizontal ).sizeHint().height() )


    def init_layout(self, header=None, footer=None):
        """ initialize the layout; this function needs to be called before everything else
        """
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins( 0,0,0,0 )
        self._layout.setSpacing( 0 )
        self._layout.addWidget( self._splitter, 1 )
        self.setLayout( self._layout )

        self.init_hscrollbar()
        if header:
            self.set_header( header )
        if footer:
            self.set_footer( footer )
        self.init_signals()
        self.set_painter()

        # split is set to 1, but will be adjusted when this pane is inserted to frame
        self.set_split(1)


    def init_signals(self):
        """ connect all necessary signals """
        if self._hscrollbar:
            #self._hscrollbar.actionTriggered.connect( self.action_triggered )
            self._hscrollbar.valueChanged.connect( self.hslide )
        self._splitter.splitterMoved.connect( self.splitter_moved )


    def header(self):
        return self._header

    def set_header(self, header):
        if self._header is not None:
            self._layout.deleteWidget(0)
            del self._header

        self._header = header
        scrollarea = header.widget()
        scrollarea.setFixedHeight( header.sizeHint().height() )
        self._layout.insertWidget( 0, scrollarea, 0 )


    def footer(self):
        return self._footer

    def set_footer(self, footer):
        if self._footer is not None:
            self._layout.deleteWidget( 2 )
            del self._footer

        self._footer = footer
        scrollarea = footer.widget()
        scrollarea.setFixedHeight( footer.sizeHint().height() )
        self._layout.insertWidget( 2, scrollarea, 0 )

    def set_split(self, n):
        count = self._splitter.count()
        if n > count:
            for i in range(count, n):
                # create the view instance, and add its widget (scrollarea) to splitter
                # as well as the index
                c = self._view_class(self, i)
                w = c.widget()
                self._splitter.addWidget(w)
        elif n < count:
            for i in range(count-1, n-1, -1):
                w = self._splitter.widget(i)
                w.hide()
                w.setParent(None)
                w.destroy()
                del w


    # SLOTS

    def action_triggered(self, action):
        pass

    def hslide(self, hval):
        """ Slide all views in this pane manually by setting their respective
            horizontalScrollBar. This function is not meant to be called directly, only
            pane's viewable horizontal bar should call this function.
        """

        for i in range(0, self._layout.count()-1):
            w = self._layout.itemAt(i).widget()
            if w == self._splitter:
                for j in range(0, self._splitter.count()):
                    self._splitter.widget(j).horizontalScrollBar().setValue(hval)
            else:
                w.horizontalScrollBar().setValue(hval)

    def move_content_splitter(self, pos, idx, pane):
        """ only move our content splitter at particular idx to pos when we are not the
            sender, ie. not the one receiving focus/mouse movement
        """
        # XXX: refactor by using self.sender, eg: if self.sender() == self:
        if pane != self:
            self._splitter.blockSignals(True)
            self._splitter.moveSplitter(pos, idx)
            self._splitter.blockSignals(False)

    def splitter_moved(self, pos, idx):
        self.ContentSplitterMoved.emit( pos, idx, self )

    def update_view(self):
        for i in range(0, self._splitter.count()):
            w = self._splitter.widget(i)
            w.widget().update()

    def update_content(self, rect):
        if rect:
            #print rect.size()
            for i in range(0, self._splitter.count()):
                #print self._splitter.widget(i).widget()
                self._splitter.widget(i).widget().update( rect )

    def update_scale(self):
        for i in range(0, self._splitter.count()):
            self._splitter.widget(i).widget().update_scale()

    def vscroll_splitter(self, val, idx):
        """ vertically scroll a particular view within splitter;
            idx -> view index, val -> new value
        """
        self._splitter.widget(idx).verticalScrollBar().setValue( val )

    def focus_pane(self):
        self._splitter.widget(0).widget().setFocus()

    def setFocus(self, reason=None):
        if reason:
            super(BasePane, self).setFocus( reason )
        else:
            super(BasePane, self).setFocus()
        self.ActiveViewChanged.emit( self._splitter.widget(0).widget() )

    # HELPERS

    def width_hint(self):
        """ this function is mostly called by view's sizeHint when view is triggered
            with resizeEvent, must be implemented by deriving class
        """
        raise NotImplemented( 'width_hint() must be provided by class derived from BasePane' )

    def length_hint(self):
        raise NotImplemented( 'use width_hint() instead of length_hint()' )

    def height_hint(self):
        """ calculate the height for displaying all data in view; warning: this function
            seems to be called excessively, probably need to provide a caching-based solution
        """
        return (len(self._model) + 2) * self.lineheight()

    def header_height(self):
        """ this function gets the synchronized height of all headers in all panes """
        # XXX: for now, just return a number
        return 30


    ##
    ## SIGNALS
    ##

    # vscrollsplitter is emitted when vertical scroll bar in VScrollbarPane is moved
    # signature: ?
    VScrollSplitter = QtCore.pyqtSignal( int, int )

    # ContentWheelEvent is emitted when mouse wheel event occured in this pane
    # signature: ?
    ContentWheelEvent = QtCore.pyqtSignal( object, int )

    # ContentSlideEvent is emitted when a view needs to be vertically scrolled
    # signature: delta_slide, splitter_index
    ContentSlideEvent = QtCore.pyqtSignal( int, int )

    # ContentSplitterMoved is emitted when a splitter with idx is moved
    # signature: pos, splitter_idx, sender_pane
    ContentSplitterMoved = QtCore.pyqtSignal( int, int, object )

    # ActiveViewChanged is emitted when a particular view gets a focus
    ActiveViewChanged = QtCore.pyqtSignal( object )

    # CursorMoved is emitted when caret / cursor is moved
    # signature: idx, pos
    CursorMoved = QtCore.pyqtSignal( int, int )
    HorizontalCursorMoved = QtCore.pyqtSignal( int )
    VerticalCursorMoved = QtCore.pyqtSignal( int )

    # update screen of view
    ContentUpdated = QtCore.pyqtSignal( object )


    @classmethod
    def set_menuclass(cls, impl):
        cls._MenuBar_ = impl

    @classmethod
    def set_statusbarclass(cls, impl):
        cls._StatusBar_ = impl

    @classmethod
    def set_paneactionclass(cls, impl):
        cls._PaneActions_ = impl

class DummyKeyCtrl(object):

    def __init__(self, view):
        self._view = view

    def key_press(self, ev):
        pass

class DummyDNDHdl(object):
    
    def __init__(self, view): pass
    def dragEnterEvent(self, ev): pass
    def dragMoveEvent(self, ev): pass
    def dropEvent(self, ev): pass
    def startDrag(self): pass
    def dragging(self, ev): pass


class IScrollArea(QtWidgets.QScrollArea):

    minimum_height = 75

    def __init__(self, parent=None):
        super(IScrollArea, self).__init__(parent)
        self.setMinimumHeight( self.minimum_height )


class BaseView(QtWidgets.QLabel):

    KeyController = DummyKeyCtrl
    DNDHandler = DummyDNDHdl
    ContextMenu = None

    def __init__(self, pane, idx, parent=None):
        super(BaseView, self).__init__(parent)

        self._scrollarea = None
        self._pane = None
        self._dnd = self.DNDHandler(self)
        self._keyctrl = self.KeyController(self)
        self._contextmenu = None

        # _idx is the position of this view within a splitter, necessarily for sending
        # the signals to the right view across different panes
        self._idx = idx

        self.set_pane( pane )

        # connect signals at pane to our slots
        self.pane().CursorMoved.connect( self.cursor_movement )
        self.pane().HorizontalCursorMoved.connect( self.horizontal_cursor_movement )
        self.pane().VerticalCursorMoved.connect( self.vertical_cursor_movement )


    def set_pane(self, pane):
        """ only set pane iff pane has been properly prepared """
        assert pane._env
        assert pane._model is not None
        self._pane = pane


    def dnd(self):
        return self._dnd

    def env(self):
        """ view gets its env from pane """
        return self._pane.env()

    def model(self):
        """ view gets its model from pane """
        return self._pane.model()

    def pane(self):
        """ get pane """
        return self._pane

    def menubar(self):
        return self.pane().menubar()

    def statusbar(self):
        return self.pane().statusbar()

    def toolbar(self):
        return self.pane().toolbar()

    def xxx_set_selection(self, selection):
        self.pane().set_selection( selection )

    def selection(self):
        return self.model().selection()

    def lineheight(self):
        return self.pane().lineheight()

    def charwidth(self):
        return self.pane().charwidth()

    def painter(self):
        return self.pane().painter()

    def widget(self):
        """ return the scrollarea of this window """
        if self._scrollarea is None:
            scrollarea = IScrollArea()
            scrollarea.setBackgroundRole(QtGui.QPalette.Light)
            scrollarea.setWidget(self)
            scrollarea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            scrollarea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            scrollarea.setWidgetResizable(True)
            self._scrollarea = scrollarea
        return self._scrollarea

    def sizeHint(self):
        """ provides hint for widget size, usually caled during resizeEvent """
        # ask this container pane for calculating width & height of data
        return QtCore.QSize( self.pane().width_hint(), self.pane().height_hint() )

    def minimumSizeHint(self):
        return self.sizeHint()

    def maximumSizeHint(self):
        return self.sizeHint()

    # event processing

    def keyPressEvent(self, ev):
        self._keyctrl.key_press( ev )

    def focusInEvent(self, ev):
        super(BaseView, self).focusInEvent( ev )
        self.pane().ActiveViewChanged.emit( self )

    def focusOutEvent(self, ev):
        super(BaseView, self).focusOutEvent( ev )

    def wheelEvent(self, ev):
        self.pane().ContentWheelEvent.emit( ev, self._idx )

    def mouseMoveEvent(self, ev):
        if not (ev.buttons() & QtCore.Qt.LeftButton):
            return

        self.dnd().dragging(ev)

    def contextMenuEvent(self, ev):
        menu = CustomMenu()
        self.pane().custom_actions().populate_contextmenu( menu )
        menu.exec_( ev.globalPos() )

    # helpers

    def xy2coord(self, x, y):
        idx = y // self.lineheight()
        pos = x // self.painter().charwidth()
        # sane checking
        if idx > len(self.model()):
            idx = -1
        return ( idx, pos )

    def coord2xy(self, idx, pos):
        y = idx * self.lineheight()
        x = pos * self.painter().charwidth()
        return (x, y)

    def xy_in_selection(self, x, y):
        raise NotImplementedError

    def ensure_visible(self, idx, pos, hwin=-1, vwin = -1):
        """ ensure that (idx, pos) is visible, if not then scroll as necessarily
            if hwin or vwin is -1, then ensure that either position is in central view
        """

        #D(INFO, "Enter")

        # we only check for vertical index (y axis), let derived windows do horizontal pos
        y = idx * self.lineheight()

        if vwin < 0:
            vwin = int(0.5 * self._scrollarea.height() // self.lineheight())

        delta = 0
        if self.y() + y > self._scrollarea.height() - self.lineheight():
            # y is below the viewport, we need to scroll down
            delta = y + self.y() - self._scrollarea.height() + vwin * self.lineheight()
        elif self.y() + y < 0:
            # y is above the viewport, we need to scroll up
            delta = y + self.y() - vwin * self.lineheight()

        if delta != 0:
            #print 'delta:', delta, self._idx
            self.pane().ContentSlideEvent.emit( delta, self._idx )


    def cursor_movement(self, idx, pos):
        pass

    def horizontal_cursor_movement(self, pos):
        pass

    def vertical_cursor_movement(self, idx):
        pass

    # DND functionality

    def dragEnterEvent(self, ev):
        self.dnd().dragEnterEvent( ev )

    def dragMoveEvent(self, ev):
        self.dnd().dragMoveEvent( ev )

    def dropEvent(self, ev):
        self.dnd().dropEvent( ev )

    def startDrag(self):
        self.dnd().startDrag()



##
## Blank view for blank header & footer
##

class BlankView(QtWidgets.QWidget):

    def __init__(self, pane, parent=None):
        super(BlankView, self).__init__(parent)
        self._pane = pane

    def widget(self):
        return self

    def horizontalScrollBar(self):
        return self

    def setValue(self, val):
        pass

    def min_height(self):
        return 

    def sizeHint(self):
        return QtCore.QSize( 100, 100 )


class BlankHeader(BlankView):

    def sizeHint(self):
        return QtCore.QSize( 0, self._pane.header_height() )


class BlankFooter(BlankView):

    def sizeHint(self):
        return QtCore.QSize( 0, self._pane.footer_height() )




