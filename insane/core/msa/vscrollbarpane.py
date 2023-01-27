__copyright__ = '''
vscrollbarpane.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets
from insane.core.base.windows import BasePane, BlankHeader, BlankFooter
from insane.core.base.debug import D, INFO


class IVerticalScrollBar(QtWidgets.QScrollBar):

    def __init__(self, pane, idx):
        super(IVerticalScrollBar, self).__init__( QtCore.Qt.Vertical )
        self._idx = idx
        self.setMinimumHeight(50)
        self._pane = pane
        self.valueChanged.connect( self.value_changed )

    def resizeEvent(self, ev):
        height = self._pane.height_hint()
        pagestep = self.height()
        if self.pageStep() != pagestep:
            self.setPageStep( pagestep )
        max_height = max(0, height - pagestep)
        if self.maximum() != max_height:
            self.setMaximum( max_height )

    def slideEvent(self, delta):
        """ when this vbar needed to be slide for a particular value """
        self.setValue( self.value() + delta )

    # cascading signal

    def value_changed(self, val):
        #self.emit( sig.VScrollSplitter, val, self._idx )
        self.VScrollSplitter.emit( val, self._idx )

    def wheelEvent(self, ev):
        offset = ev.angleDelta().y() / 5
        self.setValue(int(self.value() - offset))
        ev.accept()


    def widget(self):
        return self

    def setMaximum(self, val):
        super(IVerticalScrollBar, self).setMaximum( val )

    ##
    ## SIGNALS

    # this signal is emitted when the value of a particular vbar at index idx changes its value
    # signature: new_value, index
    VScrollSplitter = QtCore.pyqtSignal( int, int )


class VerticalScrollbarPane( BasePane ):

    have_hscrollbar = False
    __width_hint = -1

    def width_hint(self):
        """ return the width of vertical scroll bar """
        if self.__width_hint < 0:
            self.__width_hint = QtGui.QScrollBar( QtCore.Qt.Vertical ).sizeHint().width()
        return self.__width_hint

    def set_split(self, n):
        count = self._splitter.count()
        if n > count:
            for i in range(count, n):
                vbar = IVerticalScrollBar(self, i)
                self._splitter.addWidget( vbar )
                # connect vertical scrollbar VScrollSplitter signal to our vscroll_splitter
                vbar.VScrollSplitter.connect(self.vscroll_splitter)
        elif n < count:
            for i in range(count-1, n-1, -1):
                w = self._splitter.widget(i)
                w.hide()
                w.setParent(None)
                w.destroy()
                del w
        self._nsplit = n

    def connect_pane(self, p):
        """ connect pane p to this vertical scrollbar pane """
        self.VScrollSplitter.connect( p.vscroll_splitter )
        self.ContentSplitterMoved.connect( p.move_content_splitter )
        p.ContentSplitterMoved.connect( self.move_content_splitter )
        p.ContentWheelEvent.connect( self.move_wheel )
        p.ContentSlideEvent.connect( self.slide )

    def vscroll_splitter(self, val, idx):
        """ propagate VScrollSplitter signal to all receiving splitter in all pane """
        self.VScrollSplitter.emit( val, idx )

    def move_content_splitter(self, pos, idx, pane):
        """ try to move content splitter, and propagates to all pane """
        super(VerticalScrollbarPane, self).move_content_splitter(pos, idx, pane)
        self.ContentSplitterMoved.emit(pos, idx, pane )

    def move_wheel(self, ev, idx):
        self._splitter.widget(idx).wheelEvent(ev)

    def slide(self, delta, idx):
        """ performs horizontal scroll on particular vbar at index idx """
        self._splitter.widget(idx).slideEvent( delta )


    ## Layout helpers

    def resizeEvent(self, ev):
        """ during resizeEvent, layout is rechecked again """
        header_height = self.header_height()
        if header_height > 0:
            # a pane has header, so we should add a blank header
            if self.header() is None:
                self.set_header( BlankHeader( self ) )



