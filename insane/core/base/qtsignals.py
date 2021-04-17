__copyright__ = '''
qtsignals.py - part of seqpy/InSAnE

(c) 2011 - 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtCore

class qt_msasignals(QtCore.QObject):

    def __init__(self):
        super(qt_msasignals, self).__init__()


    RegionUpdated = QtCore.pyqtSignal( object )
    # coordinate region update; signature ( QRect )

    BlockSelectionUpdated = QtCore.pyqtSignal( object, object )
    # block selection update; signature ( (idx1, pos1), (idx2, pos2) )

    ColumnSelectionUpdated = QtCore.pyqtSignal( object )
    # column selection update; signature( [col1, col2, ...] )

    LabelSelectionUpdated = QtCore.pyqtSignal( object )


    SelectionUpdated = QtCore.pyqtSignal()
    # general selection being updated

    SelectionReset = QtCore.pyqtSignal()
    # general selection being reset

    SequenceUpdated = QtCore.pyqtSignal( int, int )
    # sequence update; signature: idx, pos

    ContentUpdated = QtCore.pyqtSignal()
    # whole content updated
    
    CaretMoved = QtCore.pyqtSignal(int, int, object)
    # caret movement

    CaretStopped = QtCore.pyqtSignal(object)
    # caret hidden


    SequenceTypeChanged = QtCore.pyqtSignal(object)
    # sequence type has been changed
