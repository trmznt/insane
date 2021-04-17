__copyright__ = '''
ienv.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''


from insane import QtGui
from seqpy.core.funcs.colors import EasyNA, AESSN3



# default values

LINEHEIGHT = 15
CHARWIDTH = 8

# IENV ~ InSAnE
class IEnv(object):
    """ class for holding global configuration/environment for each main window """

    MINPANEWIDTH = 600

    def __init__(self):
        super(IEnv, self).__init__()
        self._lineheight = LINEHEIGHT           # global lineheight
        self._charwidth = CHARWIDTH             # global charwidth
        self._nascheme = EasyNA()               # default NA scheme
        self._aascheme = AESSN3()               # default AA scheme
        self._header = True
        self._footer = False
        self._split = 1
        self._panesplit = 1
        self._activeview = None
        self._tracesplit = 4

        # basic preference
        self.fonts = {
            'sequence': ('Monospace', 7 ),
            'label': QtGui.QFont('Monospace', 8 )
        }

        # colors
        self.colors = {
            'general-background': QtGui.QColor( 244, 244, 232 ),
            'sequence-selection': QtGui.QColor( 191, 191, 191, 64 ),
            'trace-selection': QtGui.QColor( 'lightblue' ),
        }

        # brush
        self.brushes = {
            'sequence-selection': QtGui.QBrush( self.colors['sequence-selection'] ),
            'trace-selection': QtGui.QBrush( self.colors['trace-selection'] ),
        }

        # pens
        self.pens = {
            'sequence-selection': QtGui.QPen( self.brushes['sequence-selection'], 0 )
        }

    def set_lineheight(self, lineheight):
        self._lineheight = lineheight
#        if self._model:
#            self._model.set_lineheight( lineheight )

    def lineheight(self):
        return self._lineheight

    def set_charwidth(self, charwidth):
        self._charwidth = charwidth

    def charwidth(self):
        return self._charwidth

    def na_scheme(self):
        return self._nascheme

    def aa_scheme(self):
        return self._aascheme

    def split(self):
        return self._split

    def set_split(self, split_no):
        self._split = split_no

    def tracesplit(self):
        return self._tracesplit

    def set_tracesplit(self, split_no):
        self._tracesplit = split_no 

    def activeview(self):
        return self._activeview

    def set_activeview(self, win):
        self._activeview = win
