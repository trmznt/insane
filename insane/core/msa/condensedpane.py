__copyright__ = '''
translatedpane.py - part of seqpy/InSAnE

(c) 2013 Hidayat Trimarsanto <anto@eijkman.go.id> / <hidayat.trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore
from insane.core.base.debug import D, ALL
from insane.core.base.windows import BaseView, BasePane
from insane.core.msa.sequencepane import SequencePane, SequenceCaret, SequenceView
from insane.core.msa.model import MSA
from insane.core.base.qtsignals import qt_msasignals
from seqpy.core import funcs, bioio


class CondensedMSA(MSA):

    def __init__(self, msa, msa_signals=None):
        if 'positions' not in msa._controls:
            cmsa = funcs.condensed(msa)
        else:
            cmsa = msa
        super().__init__( cmsa, msa_signals )


class CondensedSequencePane(SequencePane):

    def __init__(self, dna_pane, view_class, parent=None):
        pass

class CondensedRulerView(RulerView):

    def __init__(self, pane, parent=None):
        super().__init__(pane, parent)

        self._font = QtGui.QFont('Monospace', 4)
        self._fontmetrics = QtGui.QFontMetrics( self._font )


    def paintEvent(self, ev):
        r = ev.rect()
        x, w = r.x(), r.width()
        height = self.height()

        model = self.model()

        p = QtGui.QPainter()
        
        start = max(0, x // cw - 1)
        end = min( len(model[0]), start + w // cw + 1 )
        midl = cw // 2
        p.setFont( self._font )
        p.translate(0, height - 4)
        p.rotate(90)

        th = self._fontmetrics.height('0')

        for i in range(start, end):
            line_y = i * cw + midl

            text = str(i)
            p.setPen( QtCore.Qt.black )
            p.drawText( 0, line_y - th -2, text )

        


        
