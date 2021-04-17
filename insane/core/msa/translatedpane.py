__copyright__ = '''
translatedpane.py - part of seqpy/InSAnE

(c) 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

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


class NonEditableNavKeyController( object ):

    def __init__(self, view):
        pass

    def key_press(self, ev):
        print('pressed')

class TranslatedMSA(MSA):

    def __init__(self, dna_msa, start_atg, msa_signals=None):
        super(TranslatedMSA, self).__init__(bioio.multisequence())

        self._src_msa = dna_msa
        self._start_atg = start_atg
        self._na = False

        self.retranslate()

    def retranslate(self, idx=None):
        if not idx:
            self.clear()
            for idx in range( len( self._src_msa ) ):
                self.append(
                    bioio.biosequence('', funcs.translated( self._src_msa[idx].seq,
                                    start_pos = self._start_atg )) )
                print(self[-1].seq)
        else:
            self[idx].seq = funcs.translated( self._src_msa[idx].seq,
                                start_pos = self._start_atg )

    def is_dna(self, nocache=None):
        return self._na



class TranslatedSequencePane(SequencePane):

    def __init__(self, dna_pane, view_class, parent=None):
        self._connected_pane = dna_pane
        m = TranslatedMSA( dna_pane.model(), dna_pane._ruler_atgframe, qt_msasignals() )
        super(TranslatedSequencePane, self).__init__( m, view_class )


class CodonSequenceCaret(SequenceCaret):
    """ This is a caret with 3 base size """

    def set_coord(self, idx, pos):
        super(CodonSequenceCaret, self).set_coord( idx, pos )

    def prepare_cursor(self, idx, pos):
        s = self._view.mode()[idx]
        p = self._view.painter()
        self.set_image( p[ s[pos] ], p[ s[pos+1] ], p[ s[pos+2] ] )

    def set_image(self, img1, img2, img3):
        pass


class TranslatedSequenceCaret(SequenceCaret):

    def set_coord(self, idx, pos):
        pass

class TranslatedSequenceView(SequenceView):

    KeyController = NonEditableNavKeyController


