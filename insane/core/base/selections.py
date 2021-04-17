__copyright__ = '''
selections.py - part of seqpy/InSAnE

(c) 2011, 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtCore, QtGui, QtWidgets
from seqpy.core import bioio
from seqpy.core.bioio import parser
from .debug import D, ALL

from io import BytesIO

clipboard_selection = None

def set_clipboard_selection(selection):
    global clipboard_selection
    clipboard_selection = selection

def get_clipboard_selection():
    return clipboard_selection


class BaseSelection(object):
    """ BaseSelection is class for holding selection information """

    def __init__(self, model):
        self._model = model
        if model.selection():
            model.selection().clear()
        self.model().set_selection( self )

    def model(self):
        return self._model

    def copy(self):
        # copy to clipboard
        clipboard = QtWidgets.QApplication.clipboard()
        self.set_mimedata( clipboard )
        set_clipboard_selection( self )

    def cut(self):
        # cut to clipboard
        print("CUT")
        self.copy()
        self.delete(clear=False)

    def delete(self, clear=False):
        """ set clear to True for clearing model
        """
        pass

    def paste(self):
        clipboard = QtWidgets.QApplication.clipboard()
        self.paste_to_selection( clipboard )

    def all(self):
        pass

    def reverse(self):
        pass

    def clear(self):
        self.model().set_selection( None )
        self.emit_update_signal()
        self._model = None
        del self

    def shift_click(self):
        pass

    def ctrl_click(self):
        pass

    def selected(self):
        # return selected objects
        raise NotImplementedError

    def is_selected(self, val):
        # return True is val is selected
        raise NotImplementedError

    def __contains__(self, val):
        # return True is val is selected, shortcut for is_selected
        raise NotImplementedError

    def update(self, view):
        pass

    def emit_update_signal(self):
        pass

    def set_mimedata(self):
        raise NotImplementedError("set_mimedata()")

    def paste_to_selection(self, clipboard):
        raise NotImplementedError("paste_to_selection()")


class LabelSelection(BaseSelection):
    """ sequence selection from label """

    def __init__(self, model, start_idx):
        super(LabelSelection, self).__init__( model )
        self._index_selections = set( (start_idx, ) )
        self._clicked_index = start_idx
        self._inverted = False
        self._selected = None
        self.emit_update_signal()

    def __contain__(self, val):
        return (val in self._index_selections)

    def indices(self):
        return self._index_selections

    def selected(self):
        return self._selected

    def shift_click(self, second_idx):
        start_idx = self._clicked_index
        if start_idx > second_idx:
            items = range(second_idx, start_idx)
        else:
            items = range(start_idx, second_idx+1)
        if self._inverted:
            self._index_selections -= set(items)
        else:
            self._index_selections.update( items )
        self.emit_update_signal()

    def ctrl_click(self, idx):
        if idx in self._index_selections:
            self._index_selections.discard( idx )
            self._inverted = True
        else:
            self._index_selections.add( idx )
            self._inverted = False
        self._clicked_index = idx
        self.emit_update_signal()

    def copy(self):
        super(LabelSelection, self).copy()
        D(ALL, "copy sequences to clipboard as fasta stream")

    def set_mimedata(self, qobj):
        """ responsible to fill the data """
        self._selected = self.copy_to_msa()
        text_stream = BytesIO()
        parser.write_fasta( text_stream, self._selected )
        qobj.setText( text_stream.getvalue().decode('utf-8') )
        
    def copy_to_msa(self):
        msa = bioio.multisequence()
        indices = list(self._index_selections)
        indices.sort()
        for idx in indices:
            msa.append( self.model()[idx] )
        return msa

    def paste_to_selection(self, clipboard):
        dst = self.model()
        idx = max( self.indices() )

        if clipboard.ownsClipboard():
            D(ALL, "performing direct copying")
            # access the global selection
            selection = get_clipboard_selection()
            if hasattr(selection, 'get_sequence'):
                dst.insert( idx, selection.get_sequence() )
            elif hasattr(selection, 'selected'):
                src = selection.selected()
                if idx >= 0:
                    for s in src:
                        print('>> insert at %d' % idx)
                        dst.insert( idx, s )
                        idx += 1
                else:
                    dst.extend( src )
            elif isinstance( selection, LabelSelection ):
                src = selection.model()
                for i in selection.indices():
                    dst.insert( idx, src[i] )
                    idx += 1
            elif isinstance( selection, BlockSelection ):
                pass
            elif isinstance( selection, ColumnSelection ):
                pass
            else:
                raise RuntimeError('Can not paste data because unknown protocol/data')
            dst.signals().ContentUpdated.emit()

        else:
            text_data = clipboard.text().encode('UTF-8').strip()
            if text_data.startswith(b'>'):
                # assuming FASTA format
                multiseq = bioio.parser.read_fasta( BytesIO(text_data) )
                for s in multiseq:
                    dst.insert( idx, s )
                    idx += 1
                dst.signals().ContentUpdated.emit()
            else:
                raise RuntimeError('Unknown paste data format')

    def __contains__(self, idx):
        return (idx in self._index_selections)

    def __len__(self):
        return len(self._index_selections)

    def as_list(self):
        return list(self._index_selections)

    def emit_update_signal(self):
        #print "emit LabelSelectionUpdated signals "
        self.model().signals().LabelSelectionUpdated.emit(self._index_selections)

    def delete(self, clear=True):
        self.model().delete( list(self._index_selections) )
        if clear:
            self.clear()
        
    def apply(self, func):
        m = self.model()
        for idx in self._index_selections:
            func( m[idx] )
        m.signals().ContentUpdated.emit()


class BlockSelection(BaseSelection):
    """ selection on sequence area """

    def __init__(self, model, idx, pos):
        super(BlockSelection, self).__init__( model )
        self._begin = (idx, pos)
        self._end = None

    def shift_click(self, idx, pos):
        self._end = (idx, pos)
        self.emit_update_signal()

    def intersect(self, rect, view):
        if not self._end:
            return None
        box = self.box(view)
        if box.intersects( rect ):
            return box.intersected( rect )
        return None

    def box(self, view, margin=0):
        if not self._end:
            return None
        idx1,pos1 = self._begin
        idx2,pos2 = self._end
        start_corner = (min(idx1, idx2), min(pos1, pos2))
        end_corner = (max(idx1, idx2), max(pos1, pos2))
        lineheight = view.lineheight()
        charwidth = view.charwidth()
        x1 = start_corner[1] * charwidth
        y1 = start_corner[0] * lineheight
        x2 = (end_corner[1] + 1) * charwidth
        y2 = (end_corner[0] + 1) * lineheight
        return QtCore.QRect(x1, y1, x2-x1, y2-y1)

    def emit_update_signal(self):
        #print "emit BlockSelectionUpdated signal"
        self.model().signals().BlockSelectionUpdated.emit( self._begin, self._end )

    def delete(self, clear=None):
        m = self.model()
        idx1, pos1 = self._begin
        idx2, pos2 = self._end
        start_pos = min(pos1, pos2)
        length = max(pos1, pos2) - start_pos + 1
        for idx in range(min(idx1,idx2), max(idx1,idx2) + 1):
            del m[idx][start_pos:start_pos+length]
        m.signals().ContentUpdated.emit()
        self.clear()

    def backspace(self):
        pass

    def insert(self, chars):
        m = self.model()
        idx1, pos1 = self._begin
        idx2, pos2 = self._end
        start_pos = min(pos1, pos2)
        for idx in range(min(idx1,idx2), max(idx1,idx2) + 1):
            m[idx].insert(start_pos, chars)
        l = len(chars)
        self._begin = idx1, pos1 + l
        self._end = idx2, pos2 + l
        m.signals().ContentUpdated.emit()

    def set_mimedata(self, qobj):
        print('BlockSelectio.set_mimedata()')
        lines = []
        m = self.model()
        idx1, pos1 = self._begin
        idx2, pos2 = self._end
        start_pos, end_pos = min(pos1, pos2), max(pos1, pos2)
        for idx in range(min(idx1,idx2), max(idx1,idx2) + 1):
            lines.append( m[idx][start_pos:end_pos + 1] )
        qobj.setText( b'\n'.join(lines).decode('utf-8') )
        
    def width(self):
        idx1, pos1 = self._begin
        idx2, pos2 = self._end
        return (max(pos1, pos2) - min(pos1, pos2) + 1)

    def upper_corner(self):
        idx1, pos1 = self._begin
        idx2, pos2 = self._end
        return (min(idx1, idx2), min(pos1, pos2))
        
    def lower_corner(self):
        idx1, pos1 = self._begin
        idx2, pos2 = self._end
        return (max(idx1, idx2), max(pos1, pos2))


class ColumnSelection(BaseSelection):
    """ selection on column, from ruler """

    def __init__(self, view, pos):

        super(ColumnSelection, self).__init__( view )
        self._position_selections = set( (pos, ) )
        self._clicked_pos = pos
        self._selected = None
        self.emit_update_signal()

    def shift_click(self, pos):
        self._position_selections = set(
                range(min(self._clicked_pos, pos), max(self._clicked_pos, pos) + 1) )
        self.emit_update_signal()


    def ctrl_click(self, pos):
        if pos in self._position_selections:
            self._position_selections.discard( pos )
        else:
            self._position_selections.add( pos )

    def intersect(self, rect, view):
        x, w = rect.x(), rect.width()
        pos1 = x / view.charwidth()
        pos2 = (x + w) / view.charwidth()
        positions = []
        for p in self._position_selections:
            if pos1 <= p <= pos2:
                positions.append( p * view.charwidth() )
        #print pos1, pos2, positions, self._position_selections
        return positions

    def box(self):
        return None

    def emit_update_signal(self):
        self.model().signals().ColumnSelectionUpdated.emit( self._position_selections )

    def delete(self):
        segments = self.normalize_position()
        m = self.model()
        for (e,b) in segments:
            for s in m:
                del s[b:e+1]
        self.model().signals().ContentUpdated.emit()
        self.clear()

    def selected(self):
        return self._selected

    def copy_to_msa(self):
        segments = self.normalize_position()
        src_mseqs = self.model()
        dest_mseqs = bioio.multisequence()
        #print segments
        for s in src_mseqs:
            dest_mseqs.append(
                s.clone().set_sequence(b''.join([ s[x:y+1] for (y,x) in segments])) )
        return dest_mseqs

    def set_mimedata(self, qobj):
        """ responsible to fill the data """
        self._selected = self.copy_to_msa()
        text_stream = BytesIO()
        parser.write_fasta( text_stream, self._selected )
        qobj.setText( text_stream.getvalue().decode('utf-8') )
        #print "COPY"

    def normalize_position(self):
        positions = list(self._position_selections)
        positions.sort()
        positions.reverse()
        # optimize this bit
        segments = []
        last_post = (positions[0], positions[0])
        for i in positions[1:]:
            if i == last_post[1] - 1:
                last_post = (last_post[0], i)
            else:
                segments.append( last_post )
                last_post = (i, i)
        segments.append( last_post )
        return segments

    def backspace(self):
        pass

    def insert(self, chars):
        if len(self._position_selections) == 1:
            pos = self._position_selections.pop()
            for s in self.model():
                s.insert(pos, chars)
            self._position_selections = set( (pos + len(chars), ) )
        self.model().signals().ContentUpdated.emit()

    def stat(self):
        segments = self.normalize_position()
        m = self.model()
        d = {}
        p = {}
        for (e,b) in segments:
            for i, s in enumerate(m):
                try:
                    d[ chr(s[b]) ] += 1
                    p[ chr(s[b]) ].append(i)
                except KeyError:
                    d[ chr(s[b]) ] = 1
                    p[ chr(s[b]) ] = [i]
        return d, p




