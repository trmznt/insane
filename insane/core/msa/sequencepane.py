__copyright__ = '''
sequencepane.py - part of seqpy/InSAnE

(c) 2011, 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets
from insane.core.base.debug import D, ALL
from insane.core.base.windows import BaseView, BasePane
from insane.core.base.statusbar import IStatusBar
from insane.core.base.selections import BlockSelection, ColumnSelection
from insane.core.base.messagebox import alert
from .sequenceactions import SequencePaneActions
from seqpy import cerr, cout
from seqpy.core import bioio


class SequencePane(BasePane):

    _PaneActions_ = SequencePaneActions

    def __init__(self, model, view_class, parent=None):
        super(SequencePane, self).__init__( model, view_class )

        self._ruler_startpos = 1
        self._ruler_atgframe = 1

        #self.set_menubar( SequencePaneMenu(self) )
        self.set_statusbar( SequencePaneStatusBar(self) )

        # connect model signals to our slots
        self.model().signals().BlockSelectionUpdated.connect( self.update_block )
        self.model().signals().ColumnSelectionUpdated.connect( self.update_column )
        self.model().signals().SequenceUpdated.connect( self.update_sequence )
        self.model().signals().ContentUpdated.connect( self.update_view )
        self.model().signals().SequenceTypeChanged.connect( self.set_painter )


    def ruler_startpos(self):
        return self._ruler_startpos

    def ruler_atgframe(self):
        return self._ruler_atgframe

    def set_painter(self, painter=None):
        painter = painter or SeqPainter.from_model( self.model(), self.env() )
        super(SequencePane, self).set_painter( painter )

    def width_hint(self):
        max_seqlen = self.model().max_seqlen() + 3
        pagestep = self.width() // self.charwidth() - 1
        hscrollbar = self.hscrollbar()
        hscrollbar.setPageStep( pagestep )
        hscrollbar.setMaximum( max(0, max_seqlen - pagestep) )
        return max(max_seqlen * self.charwidth(), self.env().MINPANEWIDTH)

    def hslide(self, hval):
        """ horizontal slide, with hval as base/character position instead of y """
        super(SequencePane, self).hslide( hval * self.charwidth() )

    # slots

    def update_block(self, begin, end):
        #print "update_block"
        # XXX: this thing needs to be optimized
        self.update_view()

    def update_column(self, columns):
        #print "update_column"
        # XXX: this thing needs to be optimized
        self.update_view()

    def update_sequence(self, idx, pos=0):
        # XXX: this thing needs to be optimized
        self.update_view()

    def update_environment(self):
        self.set_painter()
        self.update_view()


class SequencePaneStatusBar( IStatusBar ):

    def prepare_statusbar(self):
        self._idx = self._pos = None
        self._caretpos = self._msg = self._status = None

       # connecting signals
        self._pane.model().signals().CaretMoved.connect( self.set_caretpos )
        self._pane.model().signals().CaretStopped.connect( self.reset_caretpos )


    def show(self, statusbar):
        self._statusbar = statusbar
        self.init_statusbar()

    def hide(self, statusbar):
        self._caretpos.close()
        self._msg.close()
        self._status.close()
        self._caretpos = self._msg = self._status = None

    def init_statusbar(self):
        # divide by 3 parts
        self._caretpos = QtWidgets.QLabel('')
        self._msg = QtWidgets.QLabel("Sequence Pane")
        self._status = QtWidgets.QLabel("Status indicator")
        self._statusbar.addPermanentWidget(self._msg, 1)
        self._statusbar.addPermanentWidget(self._status, 1)
        self._statusbar.addPermanentWidget(self._caretpos, 2)


    def set_caretpos(self, idx, pos, pane):
        if self._pane != pane: return
        if not self._caretpos: return
        m = self._pane.model()
        try:
            s = m[idx]
            rel_pos = s.relative_pos(pos)
            self._caretpos.setText("Pos: %6d [%6d] Seq: %s" %
                    (pos + self._pane._ruler_startpos, -1 if rel_pos < 0 else rel_pos + 1,
                    s.label))
        except IndexError:
            pass

    def reset_caretpos(self, pane):
        if self._pane != pane: return
        if not self._caretpos: return
        self._caretpos.setText('')


class SeqFont(object):
    """ This class provides the necessary information related to font for
        sequence drawing.
    """

    def __init__(self,  typeface = 'Monospace',
                        fontsize = 6,
                        charwidth = 8,
                        lineheight = 12):
        self.typeface = typeface
        self.fontsize = fontsize
        self.charwidth = charwidth
        self.lineheight = lineheight
        self.font = QtGui.QFont( typeface, fontsize )
        self.fontmetrics = QtGui.QFontMetrics( self.font )


class SeqPainter(object):
    """ This class is responsible for drawing the sequence from its picture map
    """

    def __init__(self, seq_font, color_scheme, shaded=True):
        self.seqfont = seq_font
        self.color_scheme = color_scheme
        self.shaded = shaded
        self.char_map = {}

        # initialize map
        self.initialize_map()

    def charwidth(self):
        return self.seqfont.charwidth

    def lineheight(self):
        return self.seqfont.lineheight

    def initialize_map(self):
        for c in self.color_scheme:
            if c in [ '_unk_' ]: continue
            c1, c2 = ord(c.lower()), ord(c.upper())
            self.char_map[c1] = self._create_image(c1, self.color_scheme[c])
            if c1 != c2:
                self.char_map[c2] = self._create_image(c2, self.color_scheme[c])

    def paint_sequence(self, seq, start, end, p, ref_seq=None):
        """ @p -> Qt painter which has been set-up with correct y translation """
        cw = self.charwidth()
        try:
            for i in range(start, end):
                if ref_seq and ref_seq[i] == seq[i]:
                    p.drawPixmap(i * cw, 0, self['.'])
                else:
                    p.drawPixmap(i * cw, 0, self[seq[i]])
        except IndexError:
            pass

    def draw_sequence(self, seq, x, w, p, ref_seq=None):
        start = x // self.charwidth()
        end = w // self.charwidth()
        self.paint_sequence(seq, max(0, start-2), start + end + 2, p, ref_seq)


    def _create_image(self, c, color):
        p = QtGui.QPixmap(self.charwidth(), self.lineheight())
        painter = QtGui.QPainter(p)
        #painter.translate(0, self.font_height - 2)
        if self.shaded:
            fg_color = QtGui.QColor(*color[1])
            bg_color = QtGui.QColor(*color[0])
        else:
            fg_color = QtGui.QColor(*color[0])
            bg_color = QtGui.QColor(255,255,255)
        bg_brush = QtGui.QBrush(bg_color)
        painter.setBackground(bg_brush)
        painter.setBrush(bg_brush)
        painter.setPen(bg_color)
        painter.drawRect(0, 0, self.charwidth(), self.lineheight())
        painter.setPen( fg_color )
        painter.setFont( self.seqfont.font )
        painter.drawText(1, (self.lineheight() + self.seqfont.fontmetrics.ascent())/2, chr(c))
        painter.end()
        return p

    def __getitem__(self, c):
        try:
            return self.char_map[c]
        except KeyError:
            self.char_map[c] = self._create_image(c, self.color_scheme['_unk_'])
            return self.char_map[c]


    @staticmethod
    def from_model(model, env):
        if model.type() in [ bioio.DNA, bioio.RNA ]:
            scheme = env.na_scheme()
        else:
            scheme = env.aa_scheme()

        typeface, fontsize = env.fonts['sequence']
        return SeqPainter( SeqFont(typeface = typeface, fontsize = fontsize,
                                    charwidth = env.charwidth(),
                                    lineheight = env.lineheight()),
                            scheme.hex )


class SequenceCaret( QtCore.QObject ):
    """ provide basic caret functionality """
    # XXX: need to relate with ContentUpdated signals, so cursor's display is sync

    def __init__(self, view, blink=True):
        super(SequenceCaret, self).__init__()
        cout('SequenceCaret.__init__() executed!')
        assert view._caret is None

        # set the view which we are anchoring to
        self._view = view

        # cursor idx, pos coordinate
        self.cur_idx = -1
        self.cur_pos = -1
        self.next_idx = -1
        self.next_pos = -1

        # cursor x,y coordinate
        self.cur_x = -1     # translate from pos
        self.cur_y = -1     # translate from idx

        # cursor size
        self.w = -1
        self.h = -1

        # blinking purposes
        self._blink = blink
        self._counter = 0
        self._timerid = None
        self._visible = False
        self._revimg = None
        self._norimg = None


    def coord(self):
        return self.cur_idx, self.cur_pos

    def set_coord( self, idx, pos ):
        if self.cur_idx >= 0 and self.cur_pos >= 0:
            self.reset()
        self.cur_idx = idx
        self.cur_pos = pos
        self.cur_x, self.cur_y = self._view.coord2xy( idx, pos )
        self.prepare_cursor( idx, pos )
        self.show()
        #self.update()
        if self._blink:
            self.start()
        self._view.model().signals().CaretMoved.emit(idx, pos, self._view.pane())


    def reset(self):
        """ reset caret """
        if self._blink:
            self.stop()
        self.hide()
        self._view.model().signals().CaretStopped.emit( self._view.pane() )


    def move(self, d_idx, d_pos):
        m = self._view.model()
        # check next position
        next_idx = min( max(0, self.cur_idx + d_idx), len(m) - 1 )
        next_pos = min( max(0, self.cur_pos + d_pos), len(m[next_idx]) )
        # inform that we need to show this position
        self._view.ensure_visible( next_idx, next_pos )
        self.set_coord(next_idx, next_pos)


    def show(self):
        """ show caret """
        self._visible = True
        self.update()

    def hide(self):
        """ show caret """
        self._visible = False
        self.update()

    def image(self):
        if self._visible:
            # return the reversed char
            return self._revimg
        else:
            return self._norimg

    def visible(self):
        return self._visible

    def prepare_cursor(self, idx, pos):
        try:
            self.set_image( self._view.painter()[self._view.model()[idx][pos] ] )
        except IndexError:
            self.set_image( self._view.painter()[32] )

    def set_image(self, img):
        self._norimg = img
        bitmap = img.toImage()
        bitmap.invertPixels()
        self._revimg = QtGui.QPixmap.fromImage(bitmap)
        self.w = self._view.painter().charwidth()
        self.h = self._view.painter().lineheight()


    # event timer for blinking purposes

    def start(self):
        """ start blinking only if position has been set """
        if self.cur_idx < 0 and self.cur_pos < 0:
            return
        self._counter = 1
        self._timerid = self.startTimer(300)
        self._view.model().signals().CaretMoved.emit( self.cur_idx, self.cur_pos,
                    self._view.pane() )

    def stop(self):
        if self._timerid is not None:
            self.killTimer( self._timerid )
            self._timerid = None


    def timerEvent(self, ev):
        if self._counter == 1:
            self.show()
        elif self._counter == 3:
            self._counter = 0
            self.hide()
        self._counter += 1


    def update(self):
        """ update only the caret region """
        if self._view is not None:
        	self._view.update( self.cur_x, self.cur_y, self.w, self.h )


    def draw(self, p):
        p.drawPixmap( self.cur_x, self.cur_y, self.image() )


    def insert(self, chars):
        m = self._view.model()
        #m[self.cur_idx].insert(self.cur_pos, chars)
        m.insert_at(self.cur_idx, self.cur_pos, chars)
        self.cur_pos += len(chars)
        self.move(0, 0)
        m.signals().SequenceUpdated.emit( self.cur_idx, self.cur_pos )


    def backspace(self):
        if self.cur_pos > 0:
            m = self._view.model()
            m.delete_at(self.cur_idx, self.cur_pos - 1)
            self.move(0, -1)
            m.signals().SequenceUpdated.emit( self.cur_idx, self.cur_pos )


    def delete(self):
        m = self._view.model()
        m.delete_at(self.cur_idx, self.cur_pos)
        self.move(0, 0)
        m.signals().SequenceUpdated.emit( self.cur_idx, self.cur_pos )


    def set_home(self):
        self.move(  0, -self.cur_pos )

    def set_end(self):
        self.move( 0, len( self._view.model()[self.cur_idx] ) - self.cur_pos )



class NavKeyController( object ):

    def __init__(self, view):
        self._view = view

    def key_press(self, ev):
        k = ev.key()
        mod = ev.modifiers()
        self.process(k, mod, ev)

    def process(self, k, mod, ev=None):
        if k == QtCore.Qt.Key_Right:
            if mod == QtCore.Qt.ControlModifier:
                self._view.caret().move(0, 10)
            else:
                self._view.caret().move(0, 1)
        elif k == QtCore.Qt.Key_Left:
            if mod == QtCore.Qt.ControlModifier:
                self._view.caret().move(0, -10)
            else:
                self._view.caret().move(0, -1)
        elif k == QtCore.Qt.Key_Up:
            self._view.caret().move(-1, 0)
        elif k == QtCore.Qt.Key_Down:
            self._view.caret().move(1, 0)
        elif k == QtCore.Qt.Key_Home:
            self._view.caret().set_home()
        elif k == QtCore.Qt.Key_End:
            self._view.caret().set_end()
        elif k == QtCore.Qt.Key_Backspace:
            s = self._view.model().selection()
            if s:
                s.backspace()
            else:
                self._view.caret().backspace()
        elif k == QtCore.Qt.Key_Delete:
            s = self._view.model().selection()
            if s:
                _, pos = s.upper_corner()
                idx, _ = self._view.caret().coord()
                s.delete()
                self._view.caret().set_coord(idx, pos)
            else:
                self._view.caret().delete()
        elif k == QtCore.Qt.Key_Shift:
            cerr('shift pressed')
        elif k == QtCore.Qt.Key_Alt:
            cerr('alt pressed')
        elif k == QtCore.Qt.Key_Control:
            cerr('ctrl pressed')
        else:
            c = bytes(ev.text(), 'ASCII')
            if c:
                if b' ' in c:
                    c.replace(b' ', b'-')
                m = self._view.model()
                s = m.selection()
                if s:
                    s.insert(c)
                    self._view.caret().move(0, len(c))
                else:
                    self._view.caret().insert( c )


class SequenceView(BaseView):
    """ SequenceView

        Non-editable sequence viewer; only drawing screen, set scrolling and status bar
    """

    KeyController = NavKeyController

    def __init__(self, pane, idx, parent=None):
        super(SequenceView, self).__init__(pane, idx, parent)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )

        self._caret = None
        self._painter = None
        self._mouse_doubleclick = False
        self._openhand_idx = -1
        self._openhand_pos = -1
        self._openhand_x = -1
        self._openhand_y = -1

        self._caret = SequenceCaret( self )


    def __del__(self):
    	c = self.caret()
    	c.stop()
    	c._view = None    # to avoid segfault


    def caret(self):
        return self._caret


    def paintEvent(self, ev):

        r = ev.rect()
        x, y, w, h = r.x(), r.y(), r.width(), r.height()
        evrect = (x, y, w, h)

        p = QtGui.QPainter( self )

        # drawing sequence
        self.draw_region( evrect, p, self.caret() )

        # drawing auxiliary region (such as selection, markers, etc)
        self.draw_region_aux( r, p )


    def draw_region(self, evrect, p, caret):

        x,y,w,h = evrect

        c = self.caret()
        if c.cur_x == x and c.cur_y == y and c.w == w and c.h == h:
            # we are only drawing caret, let's just make it
            c.draw( p )

        else:
            # we draw all sequences
            self.draw_sequences(p, evrect)

            if c.visible():
                c.draw( p )


    def draw_region_aux(self, rect, p):
        """ draw auxiliary stuff, such as selection """

        ## drawing selections

        if isinstance( self.selection(), BlockSelection ):

            box = self.selection().intersect( rect, self )
            if box:
                # draw shaded rectangle
                #print 'draw box'
                #p.setPen( self.env().pens['sequence-selection'] )
                #p.setBrush( self.env().brushes['sequence-selection'] )
                p.setCompositionMode( p.CompositionMode_Xor )
                p.fillRect( box, self.env().brushes['sequence-selection'] )

        elif isinstance( self.selection(), ColumnSelection ):
            # find the position, and create fillRect
            for x in self.selection().intersect( rect, self ):
                p.setCompositionMode( p.CompositionMode_Xor )
                p.fillRect( x, 0, self.charwidth(), p.viewport().height(),
                                self.env().brushes['sequence-selection'] )


    def draw_sequences(self, p, evrect):
        sp = self.painter()
        m = self.model()
        x,y,w,h = evrect

        y_offset = 0
        y_end = y + h
        lh = self.lineheight()
        p.save()
        idx_start = max(0, y // lh - 1 )
        idx_end = min( len(m), y_end // lh + 1 )
        p.translate(0, idx_start * lh)

        for i in range(idx_start, idx_end):
            sp.draw_sequence( m[i], x, w, p)
            p.translate(0, lh)
            y_offset += lh
        p.restore()


    # Event processing

    def mousePressEvent(self, ev):

        if ev.button() == QtCore.Qt.LeftButton:
            idx, pos = self.xy2coord( ev.x(), ev.y() )

            #if self.selection() and not isinstance( self.selection(), BlockSelection ):
                # remove current selection first
            #    self.selection().clear()

            if ev.modifiers() & QtCore.Qt.ShiftModifier:
                # shift modifier is pressed

                if not isinstance(self.selection(), BlockSelection):
                    # not a block selection, so we need to create a block selection
                    # if caret is already in proper coordinate
                    begin_idx, begin_pos = self.caret().coord()
                    if begin_idx >= 0 and begin_pos >= 0:
                        BlockSelection( self.model(), begin_idx, begin_pos )

                if self.selection():
                    # already a block selection, we just need to update the end corners
                    old_box = self.selection().box( self )
                    self.selection().shift_click(idx, pos)
                    if old_box:
                        # if some region has been shaded, update that region first
                        self.update( old_box )

            elif ev.modifiers() & QtCore.Qt.ControlModifier:
                pass

            else:
                if self.selection():
                    self.selection().clear()

            self.caret().set_coord(idx, pos)

        elif ev.button() == QtCore.Qt.MidButton:
            # change cursor appearance to open hand
            # can use QWidget.setCursor or QApplication:setOverrideCursor
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self._openhand_idx, self._openhand_pos = self.xy2coord( ev.x(), ev.y() )
            self._openhand_x = ev.x()
            self._openhand_y = ev.y()

        elif ev.button() == QtCore.Qt.RightButton:
            pass

    def mouseReleaseEvent(self, ev):

        if ev.button() == QtCore.Qt.LeftButton:
            pass
        elif ev.button() == QtCore.Qt.MidButton:
            pass
        elif ev.button() == QtCore.Qt.RightButton:
            pass

        self.unsetCursor()

    def mouseMoveEvent(self, ev):
        # mouseMoveEvent is only triggered when dragging (ie a mouse button is pressed)
        # print "move event"

        # if this is middlebutton, scroll the area
        if (ev.buttons() & QtCore.Qt.MidButton):
            idx, pos = self.xy2coord( ev.x(), ev.y() )
            d_pos = pos - self._openhand_pos
            x, y = ev.x(), ev.y()
            dy = y - self._openhand_y
            if d_pos != 0:
                self.pane().hscrollbar().setValue( self.pane().hscrollbar().value() - d_pos )
            if abs(dy) > 5:
                self.pane().ContentSlideEvent.emit( -dy, self._idx )


    def mouseDoubleClickEvent(self, ev):
        pass

    def focusInEvent(self, ev):
        super(SequenceView, self).focusInEvent( ev )
        if self.selection() and not isinstance(self.selection(), BlockSelection):
            self.selection().clear()
        self.caret().start()
        self.model().set_caret( self.caret() )

    def focusOutEvent(self, ev):
        super(SequenceView, self).focusOutEvent( ev )
        self.caret().reset()


    def ensure_visible(self, idx, pos, hwin=-1, vwin=-1):

        # check the horizontal pos
        x = pos * self.charwidth()

        if hwin < 0:
            hwin = int( 0.5 * self._scrollarea.width() / self.charwidth() )

        if self.x() + x > self._scrollarea.width() - self.charwidth():
            self.pane().hscrollbar().setValue( pos - self._scrollarea.width()/self.charwidth() + hwin )
        elif self.x() + x < 0:
            self.pane().hscrollbar().setValue( pos - hwin )

        # check vertical index
        super(SequenceView, self).ensure_visible( idx, pos, hwin, vwin)


class RulerKeyController(object):

    def __init__(self, view):
        self._view = view

    def key_press(self, ev):
        k = ev.key()
        mod = ev.modifiers()
        self.process(k, mod, ev)

    def process(self, k, mod, ev=None):
        if k == QtCore.Qt.Key_Delete:
            s = self._view.model().selection()
            if s:
                s.delete()
        else:
            c = bytes(ev.text(), 'ASCII')
            m = self._view.model()
            s = m.selection()
            if s and c:
                s.insert(c)


class RulerView(BaseView):

    smalltick = 3
    bigtick = 6
    minheight = 30

    KeyController = RulerKeyController

    def __init__(self, pane, parent=None):
        super(RulerView, self).__init__(pane, parent)
        self.setFocusPolicy( QtCore.Qt.StrongFocus )

        self._font = QtGui.QFont('Monospace', 7)
        self._fontmetrics = QtGui.QFontMetrics( self._font )

    def minimum_height(self):
        """ return the minimum height for this ruler, in anticipation for dynamic height """
        return self.minheight

    def paintEvent(self, ev):
        # print '<RulerView>.paintEvent'
        r = ev.rect()
        x, w = r.x(), r.width()
        height = self.height()

        # print x,w,height

        model = self.model()

        p = QtGui.QPainter(self)

        cw = self.pane().charwidth()
        start = x // cw
        end = start + w // cw
        midl = cw // 2
        p.setFont( self._font )
        p.translate(0, height - 4)
        # print "ruler from %d -> %d" % (start, end)

        # print ticks
        for i in range(start - 10, end + 10):
            pos = i + self.pane().ruler_startpos()
            line_x = i * cw + midl

            if self.pane().ruler_atgframe() > 0:
                if pos % 3 == self.pane().ruler_atgframe():
                    p.setPen( QtCore.Qt.red )
                else:
                    p.setPen( QtCore.Qt.black )

            if pos % 5 == 0:
                if pos % 10 == 0:
                    text = str(pos)
                    tw = self._fontmetrics.width( text )
                    p.setPen( QtCore.Qt.black )
                    p.drawText( line_x - tw - 2, - self.smalltick - 3, text )
                    p.drawLine( line_x, 0, line_x, - 13 )
                else:
                    p.drawLine( line_x, 0, line_x, - self.bigtick)

            else:
                p.drawLine( line_x, 0, line_x, - self.smalltick)

    def sizeHint(self):
        #D(ALL, "ruler height: %d" % self.pane().header_height())
        return QtCore.QSize( self.pane().width_hint(), self.pane().header_height() )


    def mousePressEvent(self, ev):

        if ev.button() == QtCore.Qt.LeftButton:
            #print "left clicked! at %d, %d" % ( ev.x(), ev.y() )
            _, pos = self.xy2coord( ev.x(), 0 )
            if ev.modifiers() & QtCore.Qt.ShiftModifier and isinstance( self.selection(),
                        ColumnSelection ):
                self.selection().shift_click( pos )
            else:
                if self.selection():
                    self.selection().clear()
                #print "create ColumnSelection"
                ColumnSelection(self.model(), pos)

    def focusInEvent(self, ev):
        super(RulerView, self).focusInEvent( ev )
        if self.selection() and not isinstance(self.selection(), ColumnSelection):
            self.selection().clear()



# testing module

def test_sequencepane():
    import sys
    import msa
    import ienv

    app = QtGui.QApplication( sys.argv )
    msa = msa.MSA()
    msa.open( sys.argv[1] )
    msa.set_type()

    pane = SequencePane( msa, SequenceView )
    pane.set_env( ienv.IEnv() )
    pane.init_layout( header=RulerView(pane) )
    pane.show()
    app.exec_()


if __name__ == '__main__':
    test_sequencepane()
