__copyright__ = '''
pane.py - part of seqpy/InSAnE

(c) 2011-2020 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets
from insane.core.base.windows import BasePane, BaseView, IFixedSplitter
from insane.core.base.actions import CommonPaneActions
from insane.core.base.menu import CustomMenu, CommonMenuBar
from insane.core.main.actions import IMainActions
from insane.core.base.statusbar import IStatusBar
from insane.core.base.toolbar import IToolBar, PopupSlider
from insane.core.base.debug import D, INFO, ALL

from .model import tracemodel, TraceSelection
#from selections import TraceSelection


trace_set = 'ACGT'

class TracePaneActions( IMainActions ):

    def init_actions(self):
        super(TracePaneActions, self).init_actions()

        self._INSERT_BASE = self.create_action( 'Insert base', self.insert_base,
                    None, 'insert-base', "Insert a base" )

        self._ALIGN_BLASTN = self.create_action( 'BLASTN', self.align_blastn,
                    None, 'align-blastn', 'Align with BLASTN' )

        self._ALIGN_SEQ = self.create_action( 'Sequence', self.align_seq,
                    None, 'align-seq', 'Align with sequence' )

        self._ALIGN_NCBI = self.create_action('NCBI Nucleotide', self.align_ncbi,
                    None, 'align-ncbi', 'Align with NCBI sequence')
        
    def file_save(self):
        pass

    def file_saveas(self):
        pathname, ext_filter = QtWidgets.QFileDialog.getSaveFileName( self.pane(), 'Save as (in SCF)')
        if not pathname.endswith('.scf'):
            pathname += '.scf'
        try:
            f = open(pathname, 'wb')
            f.write( self.model().as_scf() )
        except RuntimeError:
            QtGui.QMessageBox.critical(self.mainwin(), "Saving Error",
                "ERROR: cannot save your edited trace." )
        finally:
            f.close()

    def edit_copy(self):
        selection = self.model().selection()
        if isinstance(selection, TraceSelection):
            selection.copy()

    def insert_base(self):
        pos = self.caret().curpos()
        self.model().insert_base(pos)
        self.caret().set_pos(pos+1)
        self.pane().update_tracepoint(pos, pos+2)

    def align_blastn(self):
        pass

    def align_seq(self):
        pass

    def align_ncbi(self):
        pass


    def menu_layout(self):
        return  [
                ( '&File',
                    [   self._NEW,
                        self._NEWDBSEQ,
                        self._OPEN,
                        self._SAVE,
                        self._SAVEAS,
                        None,
                        self._CLOSE,
                        self._EXIT
                    ]),
                ( '&Edit',
                    [   self._UNDO,
                        self._REDO,
                        None,
                        self._COPY,
                        self._INSERT_BASE,
                        None,
                        self._PREF
                    ]),

                ( '&Analysis',
                    [   ( 'Align', [ self._ALIGN_BLASTN, self._ALIGN_SEQ, self._ALIGN_NCBI ] ),
                    ]),

                ( '&Help',
                    [   self._ABOUT,
                    ])
            ]


    def init_toolbar(self):

        # x-scale slider
        self._xscale_slider = PopupSlider( orientation = QtCore.Qt.Horizontal )
        xslider = self._xscale_slider.slider()
        xslider.setRange(2, 42)
        xslider.setSingleStep(1)
        xslider.valueChanged.connect( self.set_xscale )
        xslider.setValue(10)

        # y-scale slider
        self._yscale_slider = PopupSlider( orientation = QtCore.Qt.Vertical )
        yslider = self._yscale_slider.slider()
        yslider.setRange(1, 21)
        yslider.setSingleStep(1)
        yslider.valueChanged.connect( self.set_yscale )
        yslider.setValue(10)

        self._searchbox = QtWidgets.QLineEdit('Search')
        self._searchbox.setMaxLength(32)
        self._searchbox.returnPressed.connect( self.do_search )


        self._panesplit = QtWidgets.QSpinBox()
        self._panesplit.setRange(1, 8)
        self._panesplit.setSingleStep(1)
        self._panesplit.valueChanged.connect( self.set_split )
        self._panesplit.setValue( 4 )


    def set_yscale(self, value):
        self.pane().model().set_yscale( value )

    def set_xscale(self, value):
        self.pane().model().set_xscale( value )

    def set_split(self, value):
        if self.pane().mainframe():
            self.pane().mainframe().set_vsplit( value )

    def do_search(self):
        value = bytes(self._searchbox.text(), 'ASCII')
        self._searchresults = self.pane().model().search_re( value )
        self._currentsearch = -1
        self._prevsearch.setEnabled(False)
        self._nextsearch.setEnabled(False)
        if self._searchresults:
            self._nextsearch.setEnabled(True)
            self.do_nextsearch()

    def do_prevsearch(self):
        self._currentsearch -= 1
        if self._currentsearch <= 0:
            self._prevsearch.setEnabled(False)
        selection = TraceSelection( self.pane().model(),
                self._searchresults[self._currentsearch][0] )
        selection.shift_click( self._searchresults[self._currentsearch][1] - 1 )
        if self._currentsearch < len( self._searchresults) - 1:
            self._nextsearch.setEnabled(True)

    def do_nextsearch(self):
        self._currentsearch += 1
        if self._currentsearch >= len( self._searchresults) - 1:
            self._nextsearch.setEnabled(False)
        selection = TraceSelection( self.pane().model(),
                self._searchresults[self._currentsearch][0] )
        selection.shift_click( self._searchresults[self._currentsearch][1] - 1 )
        if self._currentsearch > 0:
            self._prevsearch.setEnabled(True)


    def tracebutton_changed(self, state, button_no):
        p = self.pane().painter()
        if p._show[button_no]:
            p._show[button_no] = False
            self._peaks[button_no].setDown(False)
        else:
            p._show[button_no] = True
            self._peaks[button_no].setDown(True)
        self.pane().update_view()


    def populate_toolbar(self, toolbar):
        super(TracePaneActions, self).populate_toolbar( toolbar )
        self._xscale_slider.add_as_popup( toolbar, '\u2194' )
        self._yscale_slider.add_as_popup( toolbar, '\u2195' )
        toolbar.addWidget( self._searchbox )

        self._prevsearch = toolbar.addAction( '\u226a', self.do_prevsearch)
        self._prevsearch.setEnabled(False)
        self._nextsearch = toolbar.addAction( '\u226b', self.do_nextsearch)
        self._nextsearch.setEnabled(False)

        toolbar.addWidget( self._panesplit )

        self._peaks = {}
        for i in range(len(trace_set)):
            tb = QtWidgets.QToolButton()
            tb.setText(trace_set[i])
            tb.setDown(True)
            toolbar.addWidget( tb )
            self._peaks[i] = tb
            tb.clicked.connect( lambda x, button_no = i: self.tracebutton_changed( x, button_no ) )



class TracePane(BasePane):

    splitter_class = IFixedSplitter
    _PaneActions_ = TracePaneActions

    def __init__(self, model, view_class, parent=None):
        super(TracePane, self).__init__(model, view_class)

        self._width_hint = -1
        self._singlemodel = True
        self._caret = None

        #self.set_menubar( TracePaneMenu(self) )
        #self.set_statusbar( TracePaneStatusBar(self) )
        #self.set_toolbar( TracePaneToolBar(self) )

        # connect model signals
        self.model().signals().ScaleChanged.connect( self.update_scale )
        self.model().signals().RegionUpdated.connect( self.update_content )
        self.model().signals().TraceUpdated.connect( self.update_tracepoint )

    def caret(self):
        return self._caret

    def set_painter(self, painter=None):
        painter = painter or TracePainter()
        super(TracePane, self).set_painter( painter )

    def width_hint(self):
        if self._width_hint >= 0:
            return self._width_hint
        #print "!!! WIDTH HINT CALCULATION !!!"

        m = self.model()
        w = m._xscale * len( m.traces()[0] )
        pagestep = self.width()
        hscrollbar = self.hscrollbar()
        hscrollbar.setPageStep( pagestep )
        if not self._singlemodel:
            hscrollbar.setMaximum( max(0, w - pagestep) )
        else:
            hscrollbar.setMaximum( max(0, w - pagestep * self.split() ) )
        self._width_hint = w
        if self.hscrollbar():
            self.hslide( self.hscrollbar().value() )
        return self._width_hint

    def hslide(self, hval):
        if self._singlemodel:
            pane_width = self.width() - 2
            for i in range(0, self._layout.count()-1):
                w = self._layout.itemAt(i).widget()
                if w == self._splitter:
                    for j in range(0, self._splitter.count()):
                        self._splitter.widget(j).horizontalScrollBar().setValue(
                                pane_width * j + hval )
                else:
                    w.horizontalScrollBar().setValue( hval )
        else:
            super(TracePane, self).hslide( hval )

    def resizeEvent(self, ev):
        self._width_hint = -1
        selection = self.model().selection()
        if isinstance(selection, TraceSelection):
            selection._box = None
        if self._singlemodel:
            if self._caret:
                self._caret._box = None
        else:
            for j in range(0, self._splitter.count()):
                c = self._splitter.widget(i).caret()
                if c:
                    c._box = None

    
    def update_tracepoint(self, start, end):
        """ start & end is position, not tracepoint """
        l, _ = self.model().boundaries(start)
        _, r = self.model().boundaries(end)
        self.update_content( QtCore.QRect( l, 0, r-l, self._splitter.widget(0).height()) )

    def update_scale(self):
        self.resizeEvent(None)
        self.update_view()


class TracePaneStatusBar( IStatusBar ):
    pass


class TracePaneToolBar( IToolBar ):

    def __init__(self, pane):
        super(TracePaneToolBar, self).__init__(pane)
        self._searchresults = []
        self._currentsearch = -1

    def init_toolbar(self):
        self._xscale_slider = PopupSlider( orientation = QtCore.Qt.Horizontal )
        xslider = self._xscale_slider.slider()
        xslider.setRange(2, 42)
        xslider.setSingleStep(1)
        xslider.valueChanged.connect( self.set_xscale )
        xslider.setValue(10)
        self.add_popup( '\u2194', self._xscale_slider )

        self._yscale_slider = PopupSlider( orientation = QtCore.Qt.Vertical )
        yslider = self._yscale_slider.slider()
        yslider.setRange(1, 21)
        yslider.setSingleStep(1)
        yslider.valueChanged.connect( self.set_yscale )
        yslider.setValue(10)
        self.add_popup( '\u2195', self._yscale_slider )

        self._searchbox = QtGui.QLineEdit('Search')
        self._searchbox.setMaxLength(32)
        self._searchbox.returnPressed.connect( self.do_search )
        self._toolbar.addWidget( self._searchbox )

        self._prevsearch = self._toolbar.addAction( '\u226a', self.do_prevsearch)
        self._prevsearch.setEnabled(False)
        self._nextsearch = self._toolbar.addAction( '\u226b', self.do_nextsearch)
        self._nextsearch.setEnabled(False)

        self._panesplit = QtGui.QSpinBox()
        self._panesplit.setRange(1, 8)
        self._panesplit.setSingleStep(1)
        self._panesplit.valueChanged.connect( self.set_split )
        self._panesplit.setValue( 4 )
        self._toolbar.addWidget( self._panesplit )

        self._peaks = {}
        for i in range(len(trace_set)):
            tb = QtGui.QToolButton()
            tb.setText(trace_set[i])
            tb.setDown(True)
            self._toolbar.addWidget( tb )
            self._peaks[i] = tb
            tb.clicked.connect( lambda x, button_no = i: self.tracebutton_changed( x, button_no ) )

    def set_yscale(self, value):
        self.pane().model().set_yscale( value )

    def set_xscale(self, value):
        self.pane().model().set_xscale( value )

    def set_split(self, value):
        if self.pane().mainframe():
            self.pane().mainframe().set_vsplit( value )

    def do_search(self):
        value = self._searchbox.text()
        self._searchresults = self.pane().model().search_re( value )
        self._currentsearch = -1
        self._prevsearch.setEnabled(False)
        self._nextsearch.setEnabled(False)
        if self._searchresults:
            self._nextsearch.setEnabled(True)
            self.do_nextsearch()

    def do_prevsearch(self):
        self._currentsearch -= 1
        if self._currentsearch <= 0:
            self._prevsearch.setEnabled(False)
        selection = TraceSelection( self.pane().model(),
                self._searchresults[self._currentsearch][0] )
        selection.shift_click( self._searchresults[self._currentsearch][1] - 1 )
        if self._currentsearch < len( self._searchresults) - 1:
            self._nextsearch.setEnabled(True)

    def do_nextsearch(self):
        self._currentsearch += 1
        if self._currentsearch >= len( self._searchresults) - 1:
            self._nextsearch.setEnabled(False)
        selection = TraceSelection( self.pane().model(),
                self._searchresults[self._currentsearch][0] )
        selection.shift_click( self._searchresults[self._currentsearch][1] - 1 )
        if self._currentsearch > 0:
            self._prevsearch.setEnabled(True)


    def tracebutton_changed(self, state, button_no):
        p = self.pane().painter()
        if p._show[button_no]:
            p._show[button_no] = False
            self._peaks[button_no].setDown(False)
        else:
            p._show[button_no] = True
            self._peaks[button_no].setDown(True)
        self.pane().update_view()


class TracePainter(object):

    def __init__(self):

        # for A, C, G, T, N
        self.base_colors = [    QtGui.QColor(x) for x in ('forestgreen', 'blue', ' black',
                                    'red', 'grey') ]

        self.trace_pens = [ QtGui.QPen(x, 1) for x in self.base_colors ]
        self.quality_pens = [ QtGui.QPen(
                    QtGui.QColor(*x), 5, QtCore.Qt.SolidLine, QtCore.Qt.FlatCap )
                    for x in ( (255,20,255), (255,25,25), (20,155,20) ) ]

        self.ruler_pen = QtGui.QPen( QtGui.QColor('black'))
        self.ruler_font = QtGui.QFont('Monospace', 8)
        self.ruler_fontmetrics = QtGui.QFontMetrics( self.ruler_font )
        self.ruler_fontmetrics_halfwidth = self.ruler_fontmetrics.width('A')/2

        self._show = [ True, True, True, True ]


    def draw_region( self, trace, x, w, h, p ):

        self.draw_trace( trace, x, w, h, p )
        self.draw_ruler( trace, x, w, h, p )


    def draw_trace( self, trace, x, w, h, p ):
        """ paint the trace to paint device p, starting from x to w, with height h
            and trace T
        """
        scale_x = trace._xscale
        scale_y = trace._yscale
        # convert screen coordinate to trace position
        minTp = int(x/scale_x) 
        maxTp = minTp + int(w/scale_x)
        #print "painting from %d to %d" % (minTp, maxTp)

        p.save()
        p.translate(0, h-5)
        p.scale(1.0, -1.0)
        for i in range(4):
            if self._show[i]:
                self.draw_single_trace(minTp, maxTp, trace.traces()[i], self.trace_pens[i],
                        p, scale_x, scale_y)
        p.restore()


    def draw_single_trace(self, minTp, maxTp, data, pen, p, scaleX, scaleY):

        p.setPen( pen )
        points = [ QtCore.QPoint( x * scaleX, data[x] * scaleY)
                        for x in range(max(0, minTp - 5), min(maxTp+5, len(data))) ]
        p.drawPolyline( QtGui.QPolygon(points) )


    def draw_ruler( self, trace, x, w, h, p ):
        """ paint the ruler to paint device p, starting from x to w, with height h
            and trace T
        """
        scale_x = trace._xscale
        minTp = int(x/scale_x)
        maxTp = minTp + int(w/scale_x)
        minTp = max(0, minTp - 2)
        maxTp = min( len(trace), maxTp + 2 )
        minBp = max(0, trace.get_basecall_index(minTp) - 2)
        maxBp = min( len(trace.bases()), trace.get_basecall_index(maxTp) + 2 )

        p.save()
        p.setPen( self.ruler_pen )
        p.setFont( self.ruler_font )

        # draw ruler
        p.translate(0, 15)
        p.drawLine( minTp * scale_x, 0, maxTp * scale_x, 0 )

        bases = ( [], [], [], [], [] )

        # prepare bases
        for bp in range(minBp, maxBp):
            p.setPen( self.ruler_pen )
            xp = int(trace.basecalling()[bp] * scale_x)

            # draw ticks
            if (bp % 10) == 9:
                label = str(bp + 1)
                w = self.ruler_fontmetrics.width(label)
                p.drawText( xp - w//2 - 2, 33, label)
                p.drawLine( xp, 0, xp, 8 )
            else:
                p.drawLine( xp, 0, xp, 4 )

            base = trace.bases()[bp]
            if base == 65 or base == 97:    # base A
                bases[0].append( (xp, base) )
            elif base == 67 or base == 99:  # base C
                bases[1].append( (xp, base) )
            elif base == 71 or base == 103: # base G
                bases[2].append( (xp, base) )
            elif base == 84 or base == 116: # base T
                bases[3].append( (xp, base) )
            else:
                bases[4].append( (xp, base) )

        # print bases
        for i in range(0, 5):
            p.setPen( self.trace_pens[i] )
            for (xp, base) in bases[i]:
                p.drawText(int(xp - self.ruler_fontmetrics_halfwidth), 20, chr(base))

        # prepare qualities
        qualities = ( [], [], [] )

        if trace.qualities().any():
            for bp in range(minBp, maxBp):
                xp = trace.basecalling()[bp] * scale_x
                q = trace.qualities()[bp] + 2
                if q < 17:
                    qualities[0].append( (xp, q) )
                elif q < 25:
                    qualities[1].append( (xp, q) )
                else:
                    qualities[2].append( (xp, q) )

        # draw qualities
        for i in range(0, 3):
            p.setPen( self.quality_pens[i] )
            for xp, q in qualities[i]:
                p.drawLine(xp, 0, xp, -(q * 0.25))

        p.restore()


class TraceCaret(QtCore.QObject):

    def __init__(self, view):
        super(TraceCaret, self).__init__()

        self._view = view

        self._curpos = -1
        self._box = None

    def set_pos(self, pos):
        self._curpos = pos
        if self._box:
            oldbox = self._box
            self._box = None
            self._view.model().signals().RegionUpdated.emit( oldbox )
        else:
            self._box = None
        self._view.model().signals().RegionUpdated.emit( self.box() )

    def curpos(self):
        return self._curpos

    def box(self):
        if self._box:
            return self._box

        curpos = self.curpos()
        if curpos < 0:
            return None

        left, right = self._view.model().boundaries(curpos)

        self._box = QtCore.QRect( left, 0, right - left, self._view._scrollarea.height() )
        return self._box

    def move(self, dx, dy):
        if self.curpos() < 0:
            self.set_pos(0)
        else:
            curpos = self.curpos()
            if dx > 0:
                self.set_pos( min( curpos + 1, len(self._view.model().bases()) ) )
            elif dx < 0:
                self.set_pos( max( curpos - 1, 0) )


class TraceKeyController( object ):

    def __init__(self, view):
        self._view = view

    def key_press(self, ev):
        k = ev.key()
        mod = ev.modifiers()

        if k == QtCore.Qt.Key_Right:
            self._view.caret().move(1, 0)
        elif k == QtCore.Qt.Key_Left:
            self._view.caret().move(-1, 0)
        elif QtCore.Qt.Key_A <= k <= QtCore.Qt.Key_Z or k == QtCore.Qt.Key_Minus:
            c = str(ev.text())
            if c in 'actgnACTGN-':
                bases = self._view.model().bases
                caret = self._view.caret()
                curpos = caret.curpos()
                if curpos < 0:
                    return
                self._view.model().modify_base(curpos, c)
                caret.move(1, 0)


class TraceView(BaseView):
    """ TraceView

        Trace viewer in a single lane
    """

    KeyController = TraceKeyController

    def __init__(self, pane, idx, parent=None):
        super(TraceView, self).__init__(pane, idx, parent)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )
        if self.pane()._singlemodel:
            #print "going single model"
            if self.pane()._caret is None:
                #print "set _caret for singlemodel"
                self.pane()._caret = TraceCaret( self )
        else:
            self._caret = TraceCaret( self )

    def caret(self):
        if self.pane()._singlemodel:
            return self.pane()._caret
        return self._caret


    def paintEvent(self, ev):

        r = ev.rect()
        x,y,w,h = r.x(), r.y(), r.width(), r.height()

        D(INFO, "(%s) -> [%d,%d,%d,%d]" % ( self, x,y,w,h ) )
        p = QtGui.QPainter(self)
        
        # below makes the trace pretty, but consume more time to display
        p.setRenderHint( QtGui.QPainter.Antialiasing )
        p.setRenderHint( QtGui.QPainter.TextAntialiasing )

        caret_box = self.caret().box()
        if caret_box:
            intersection = r.intersected( caret_box )
            p.fillRect( intersection, self.env().brushes['trace-selection'] )

        selection = self.selection()
        if selection:
            intersection = r.intersected( selection.box(self) )
            p.fillRect( intersection, self.env().brushes['trace-selection'] )

        height = self._scrollarea.height()
        self.painter().draw_region( self.model(), x, w, height, p )

        # draw auxiliary stuff here


    def xy2coord(self, x, y):
        raise NotImplemented('xy2coord() is not suitable for trace')

    def coord2xy(self, idx, pos):
        raise NotImplemented('coord2xy() is not suitable for trace')

    def x2tracepoint(self, x):
        return int( x / self.model()._xscale )

    def x2base(self, x):
        tp = self.x2tracepoint( x )
        m = self.model()
        current_bp = m.get_basecall_index( tp )
        if current_bp >= len(m.bases()):
            return -1
        left_tp = m.basecalling()[current_bp -1]
        right_tp = m.basecalling()[current_bp]
        if (tp - left_tp) < (right_tp - tp): current_bp += -1
        return current_bp


    def mousePressEvent(self, ev):

        if ev.button() == QtCore.Qt.LeftButton:
            clicked_pos = self.x2base( ev.x() )
            if ev.modifiers() & QtCore.Qt.ShiftModifier:
                if not isinstance(self.selection(), TraceSelection):
                    pos = self.caret().curpos()
                    if pos >= 0:
                        TraceSelection( self.model(), pos )

                if self.selection():
                    old_box = self.selection().box( self )
                    self.selection().shift_click( clicked_pos )
                    if old_box:
                        self.model().signals().RegionUpdated.emit( old_box )

            else:
                if self.selection():
                    self.selection().clear()
            #print 'set caret at pos:', clicked_pos
            self.caret().set_pos( clicked_pos )

    def focusOutEvent_XXX(self, ev):
        super(TraceView, self).focusOutEvent( ev )
        self.caret().set_pos(-1)

    def focusInEvent(self, ev):
        self.pane().ActiveViewChanged.emit( self )


def test_tracepane():
    import sys
    import ienv

    app = QtGui.QApplication( sys.argv )
    tracedata = trace.open_trace( sys.argv[1] ).tracedata()

    pane = TracePane( tracedata, TraceView )
    pane.set_env( ienv.IEnv() )
    pane.init_layout()
    pane.set_split(4)
    pane.show()
    app.exec_()

if __name__ == '__main__':
    test_tracepane()
