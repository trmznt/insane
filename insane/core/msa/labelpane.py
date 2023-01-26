__copyright__ = '''
labelpane.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''


from insane import QtGui, QtCore, QtWidgets
from insane.core.base.windows import BasePane, BaseView
from insane.core.base.statusbar import IStatusBar
from insane.core.base.selections import LabelSelection, BlockSelection, ColumnSelection, get_clipboard_selection
from insane.core.base.dndviews import DNDLabel
from .labelactions import LabelPaneActions
from seqpy.core import bioio, funcs
from insane.core.base.debug import D, ALL


class LabelPane(BasePane):

    _PaneActions_ = LabelPaneActions

    def __init__(self, model, view_class, parent=None):
        super(LabelPane, self).__init__(model, view_class, parent)

        self._width_hint = -1
        self.set_statusbar( LabelPaneStatusBar(self) )

        # connect model signal to our slot font me
        self.model().signals().LabelSelectionUpdated.connect( self.update_label )
        self.model().signals().ContentUpdated.connect(self.update_view)


    def set_painter(self, painter=None):
        painter = painter or LabelPainter( self, self.env().fonts['label'] )
        super(LabelPane, self).set_painter( painter )

    def width_hint(self):
        if self._width_hint < 0 and len(self.model()) >= 1:
            label_width = max( [ len(x.label) for x in self.model() ] ) + 5
            p = self.painter()
            self._width_hint = p.fontmetrics().width( label_width * 'W' ) + \
                                p.offset_x() + p.margin()
        pagestep = self.width()
        hscrollbar = self.hscrollbar()
        hscrollbar.setPageStep( pagestep )
        hscrollbar.setMaximum( max(0, self._width_hint - pagestep) )
        return self._width_hint


    def update_label(self, indexes):
        # XXX: this need to be optimized
        self.update_view()

    def update_environment(self):
        self.set_painter()


class LabelPaneStatusBar( IStatusBar ):

    def prepare_statusbar(self):
        pass

    def show(self, statusbar):
        self._statusbar = statusbar
        self.init_statusbar()

    def hide(self, statusbar):
        pass

    def init_statusbar(self):
        self._statusbar.showMessage( 'LabelPane' )


class LabelPainter(object):

    def __init__(self, label_pane, label_font, offset_x = 0):

        self._label_pane = label_pane
        self._font = label_font
        self._fontmetrics = QtGui.QFontMetrics( label_font )
        self._offset_x = offset_x or self._fontmetrics.width('0000: ')
        self._margin = 5

    def font(self):
        return self._font

    def fontmetrics(self):
        return self._fontmetrics

    def offset_x(self):
        return self._offset_x

    def margin(self):
        return self._margin


    def draw_label(self, painter, idx, baseline, label, hilighted=False, selected=False):
        """ actual label drawing function, can be overriden by user """
        baseline = int(baseline)
        painter.drawText(self._margin, baseline, "%3d:" % idx)
        if selected:
            painter.setBackground( QtCore.Qt.blue )
            painter.setBrush( QtCore.Qt.blue )
            painter.setPen( QtCore.Qt.blue )
            painter.drawRect( self._offset_x - 2, 0, painter.viewport().width(),
                            self._label_pane.lineheight() )
            painter.setBackgroundMode( QtCore.Qt.OpaqueMode )
            painter.setPen( QtCore.Qt.white )
        if hilighted:
            painter.setBackground( QtCore.Qt.cyan )
            painter.setBrush( QtCore.Qt.cyan )
            painter.setPen( QtCore.Qt.cyan )
            painter.drawRect( self._offset_x - 2, 0, painter.viewport().width(),
                            self._label_pane.lineheight() )
            painter.setBackgroundMode( QtCore.Qt.OpaqueMode )
            painter.setPen( QtCore.Qt.black )
        painter.drawText(self._offset_x, baseline, label)


class LabelKeyController(object):

    def __init__(self, view):
        self._view = view

    def key_press(self, ev):
        #print 'key_press'
        k = ev.key()
        mod = ev.modifiers()
        self.process(k, mod)

    def process(self, k, mod):
        selection = self._view.model().selection()
        if not isinstance(selection, LabelSelection):
            return
        if k == QtCore.Qt.Key_Up:
            self.move_selection( selection, -1)
        elif k == QtCore.Qt.Key_Down:
            self.move_selection( selection, +1)
        elif k == QtCore.Qt.Key_Return:
            self._view.set_labelbox( selection._clicked_index )
        elif k == QtCore.Qt.Key_Escape:
            if self._view._labelbox and self._view._labelbox.isVisible():
                self._view._labelbox.hide()
                self._view._labelbox = None
                self._view.setFocus()
            elif selection:
                selection.clear()
        elif k == QtCore.Qt.Key_Home:
            self.move_selection( selection, - selection._clicked_index )
        elif k == QtCore.Qt.Key_End:
            self.move_selection(selection, len(self._view.model()) - selection._clicked_index)
        elif k == QtCore.Qt.Key_Delete:
            selection.delete()
        elif k == QtCore.Qt.Key_R:
            #print 'rev-comp'
            selection.apply( lambda x: bioutils.reverse_complement_s(x) )
        return


    def move_selection(self, selection, d_idx):
        clicked_index = selection._clicked_index
        m = self._view.model()
        idx = min( max(0, clicked_index + d_idx), len(m) - 1 )
        LabelSelection( self._view.model(), idx )
        if self._view._labelbox:
            self._view.set_labelbox( idx, save_changes=True )
        self._view.ensure_visible( idx, -1 )


class LabelBox(QtWidgets.QLineEdit):
    """ this class deals with label editing in label pane
    """

    y_off = 2

    def __init__(self, idx, parent=None):
        super(LabelBox, self).__init__(parent)
        self._idx = idx
        self.setFrame(False)
        self.setTextMargins(2, 0, 0, 0)
        self.setFixedHeight(self.parent().lineheight() + 7)     # set the height of the box
        self.setFixedWidth(self.parent().width())
        palette = self.palette()
        palette.setColor( self.backgroundRole(), QtCore.Qt.yellow )
        self.setPalette(palette)
        #self.hide()
        self.editingFinished.connect( self.editing_finished )
        self.returnPressed.connect( self.return_pressed )
        lp = self.parent().painter()
        self._margin = lp.margin() + 35
        self.setFont( lp.font() )
        self.set_index( idx )


    def set_index(self, idx):
        self._idx = idx
        m = self.parent().model()
        self.setText( m[idx].label ) #.decode('UTF-8') )
        lp = self.parent().painter()
        self.move( self._margin - 2, idx * self.parent().lineheight() - self.y_off )
        self.show()
        #D(ALL, "showing labelbox")
        self.setFocus()

    def editing_finished(self):
        # check if label is modified, and then set the modified label
        if self.isModified():
            self.parent().model().set_label( self._idx, self.text() )
            #D( ALL, 'sequence modified' )


    def return_pressed(self):
        #print "pressed"
        self.hide()
        self.parent().setFocus()


class LabelView(BaseView):
    """ only provides viewing label, hilight"""

    KeyController = LabelKeyController
    DNDHandler = DNDLabel

    def __init__(self, pane, idx, parent=None):
        super(LabelView, self).__init__( pane, parent )
        self.setFocusPolicy( QtCore.Qt.StrongFocus )

        self._dnd = DNDLabel( self )

        self._idx = idx
        self._text_off_x = -1

        self._cur_idx = -1
        self._hilight_idx = -1

        self._labelbox = None


    def paintEvent(self, ev):

        # get the rectanguler area of visible view
        r = ev.rect()
        x,y,w,h = r.x(), r.y(), r.width(), r.height()
        y_end = y + h

        # prepare painter & other variables
        p = QtGui.QPainter(self)
        model = self.model()
        lineheight = self.lineheight()
        lp = self.painter()

        # prepare font and painter state
        p.setFont(lp.font())
        baseline = (lineheight + lp.fontmetrics().ascent())/2
        
        # check the visible sequences
        start_idx, _ = self.xy2coord(0, y)
        stop_idx, _ = self.xy2coord(0, y_end)

        # iterate to paint the label
        selection = self.selection() if isinstance(self.selection(), LabelSelection) else None
        for i in range(max(0, start_idx - 1), min(stop_idx + 1, len(model))):
            p.save()
            p.translate(0, i * lineheight )
            if selection and i in selection:
                lp.draw_label( p, i, baseline, model[i].label, selected=True )
            else:
                lp.draw_label( p, i, baseline,  model[i].label )
            p.restore()

        #self.draw_region_aux(r, p)


    def draw_region_aux(self, rect, p):
        # this method currently is not being used anymore
        # draw hilight
        if self._hilight_idx >= 0:
            i = self._hilight_idx
            p.save()
            p.translate(0, i * self.lineheight() )
            lp.draw_label(p, i, (self.lineheight() + lp.fontmetrics().ascent())/2,
                                model[i].get_name(), hilight=True )
            p.restore()


    def coord2xy(self, idx, pos=0):
        return (0, idx * self.lineheight())

    def xy2coord(self, x, y):
        return (y // self.lineheight(), 0)


    def cursor_movement(self, idx, pos):
        self.vertical_cursor_movement( idx )

    def vertical_cursor_movement(self, idx):
        if idx != self._hilight_idx:
            self._hilight_idx = idx
            self.update()

    ## mouse events

    def mousePressEvent(self, ev):

        #print 'mousePresssEvent'

        idx, _ = self.xy2coord( 0, ev.y() )
        if ev.button() == QtCore.Qt.LeftButton:
            if isinstance(self.selection(), LabelSelection):
                if ev.modifiers() & QtCore.Qt.ShiftModifier:
                    self.selection().shift_click( idx )
                elif ev.modifiers() & QtCore.Qt.ControlModifier:
                    self.selection().ctrl_click( idx )
                else:
                    if idx not in self.selection():
                        LabelSelection( self.model(), idx )
            else:
                LabelSelection( self.model(), idx )
            self.dnd().prepare_drag( ev.pos() )
            self.update()

        elif ev.button() == QtCore.Qt.MiddleButton:
            if isinstance(self.selection(), LabelSelection):
                self.selection().ctrl_click( idx )
            else:
                LabelSelection( self.model(), idx )
            self.update()

        elif ev.button() == QtCore.Qt.RightButton:
            if not ( isinstance(self.selection(), LabelSelection)
                        and idx in self.selection() ):
                LabelSelection( self.model(), idx )
                self.update()

    def xxx_ContextMenuEvent(self, ev):
        menu = QtGui.QMenu()
        self.pane().custom_actions().populate_contextmenu( menu )
        menu.exec_(ev.globalPos())

    def set_labelbox(self, idx, save_changes=False):
        if self._labelbox:
            if save_changes:
                self._labelbox.editing_finished()
            self._labelbox.set_index( idx )
        else:
            self._labelbox = LabelBox(idx, self)


def test_labelpane():
    import sys
    import msa
    import ienv

    app = QtGui.QApplication( sys.argv )
    msa = msa.MSA()
    msa.open( sys.argv[1] )
    msa.set_type()

    pane = LabelPane( msa, LabelView )
    pane.set_env( ienv.IEnv() )
    pane.init_layout()
    pane.show()
    app.exec_()


if __name__ == '__main__':
    test_labelpane()
