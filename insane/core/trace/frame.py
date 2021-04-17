__copyright__ = '''
traceframe.py - part of seqpy/InSAnE

(c) 2011, 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane.core.base.windows import BaseFrame
from .pane import TracePane, TraceView


class TraceFrame(BaseFrame):
    """ TraceFrame

    """

    def __init__(self, env, model, parent=None):
        super(TraceFrame, self).__init__( env )

        self._model = model
        self._vsplit = self.env().tracesplit()

        self.init_layout()

        pane = TracePane( self._model, TraceView )
        pane.set_env( self.env() )
        pane.init_layout()
        self.insert_pane( pane )


    def model(self):
        return self._model


def test_traceframe():

    import sys
    import ienv
    import trace

    app = QtGui.QApplication(sys.argv)
    e = ienv.IEnv()

    m = trace.open_trace(sys.argv[1])





        
