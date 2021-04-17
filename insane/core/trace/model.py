__copyright__ = '''
trace.py - part of seqpy/InSAnE

(c) 2011 - 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from seqpy.core import traceio, bioio
from insane import QtCore
from insane.core.base.selections import BaseSelection
import os

class tracemodel_signals(QtCore.QObject):

    def __init__(self, parent):
        super(tracemodel_signals, self).__init__()
        self._parent = parent
    
    updateRange = QtCore.pyqtSignal( int, int )
    cursorMoved = QtCore.pyqtSignal( int )
    UpdatePosition = QtCore.pyqtSignal( int, int )
    TraceUpdated = QtCore.pyqtSignal( int, int )
    RegionUpdated = QtCore.pyqtSignal( object )
    ScaleChanged = QtCore.pyqtSignal()

class tracemodel(object):

    def __init__(self, tracedata):
        self._trace = tracedata
        self._cursor = None
        self._basepos = -1
        self._xscale = 1
        self._yscale = 0.05
        self._selection = None
        self._signals = tracemodel_signals( self )

    def set_selection(self, selection):
        self._selection = selection

    def selection(self):
        return self._selection

    def signals(self):
        return self._signals

    def filename(self):
        return self._trace.filename

    def name(self):
        return os.path.splitext( os.path.basename( self.filename() ) )[0]

    def __len__(self):
        return len(self._trace)

    def basepos(self):
        return self._trace.edit_basepos

    def traces(self):
        return self._trace.traces

    def bases(self):
        return self._trace.edit_bases

    def qualities(self):
        return self._trace.edit_qualities

    def basecalling(self):
        return self._trace.edit_basecalling

    def get_basecall_index(self, tp):
        return self._trace.get_basecall_index(tp)

    def set_xscale( self, value ):
        self._xscale = 0.1 * value
        self.signals().ScaleChanged.emit()

    def set_yscale( self, value ):
        self._yscale = 0.005 * value
        self.signals().ScaleChanged.emit()

    def boundaries(self, pos):
        l, r = self._trace.boundaries( pos )
        return l * self._xscale, r * self._xscale

    def insert_base(self, pos, base=b'n'):
        self._trace.insert_base(pos, base)
        self.signals().TraceUpdated.emit(pos, pos+2)

    def modify_base(self, pos, base):
        self._trace.modify_base(pos, base)
        self.signals().TraceUpdated.emit(pos, pos)

    def search_re(self, pattern):
        return self._trace.search_re( pattern )

    def as_scf(self):
        return self._trace.as_scf()



def open_trace( filename ):
    _t = traceio.read_trace( filename )
    #_t.set_filename( filename )
    return tracemodel( _t )


class TraceSelection(BaseSelection):
    """ selection on trace """

    def __init__(self, model, pos):
        super(TraceSelection, self).__init__( model )
        self._startpos = pos
        self._endpos = -1
        self._box = None

    def shift_click(self, pos):
        self._endpos = pos
        self._box = None
        self.emit_update_signal()

    def box(self, view):
        if self._box:
            return self._box

        left, _ = self.model().boundaries(self._startpos)
        _, right = self.model().boundaries(self._endpos)

        self._box =  QtCore.QRect( left, 0, right-left, view._scrollarea.height() )
        return self._box

    def emit_update_signal(self):
        self.model().signals().TraceUpdated.emit( self._startpos, self._endpos )


    def set_mimedata(self, qobj):
        """ responsible to fill the data """
        qobj.setText( self.model().bases()[self._startpos:self._endpos+1].decode('ASCII') )

    def get_sequence(self):
        m = self.model()
        return bioio.sequence( m.name(), m.bases()[self._startpos:self._endpos+1] )
