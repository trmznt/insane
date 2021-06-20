__copyright__ = '''
seqframe.py - part of seqpy/InSAnE

(c) 2011 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane.core.base.windows import BaseFrame, BlankHeader
from .vscrollbarpane import VerticalScrollbarPane
from .labelpane import LabelPane, LabelView
from .sequencepane import SequencePane, SequenceView, RulerView


class SequenceFrame(BaseFrame):
    """ BaseFrame

        This class manage the communication and layout between various panes. Main pane
        where main model resides is the self._vscrollbarpane
    """

    def __init__(self, env, model, parent=None):
        super(SequenceFrame, self).__init__( env )

        # prepares vscrollbarpane an use it as our main panel
        vscrollbarpane = VerticalScrollbarPane( model )
        vscrollbarpane.set_env( self.env() )
        vscrollbarpane.init_layout()
        vscrollbarpane.init_signals()
        self.init_vscrollbarpane( vscrollbarpane )

        self.init_layout()

        header_cls, view_cls, footer_cls = get_pane_components( model )

        # adding panes

        pane = LabelPane( self.model(), LabelView )
        pane.set_env( self.env() )
        pane.set_mainframe( self )
        pane.init_layout( header=BlankHeader(pane) )
        self.insert_pane( pane )

        for i in range(self.env()._panesplit):
            pane = SequencePane( self.model(), SequenceView )
            pane.set_env( self.env() )
            pane.init_layout( header=RulerView(pane) )
            self.insert_pane( pane )


    def model(self):
        return self._vscrollbarpane.model()


def get_pane_components(obj):
    """ return header class, viewer class and footer class """

    return ( RulerView, SequenceView, None )


def test_sequenceframe():

    import sys
    import msa
    import ienv

    app = QtGui.QApplication(sys.argv)

    e = ienv.IEnv()

    m = msa.MSA()
    m.open( sys.argv[1] )
    m.set_type()


    vscrollbarpane = VerticalScrollbarPane( m )
    vscrollbarpane.set_env( e )
    vscrollbarpane.init_layout()
    vscrollbarpane.init_signals()

    frame = SequenceFrame(e, m)
    frame.init_vscrollbarpane( vscrollbarpane )
    frame.init_layout()

    pane = SequencePane( m )
    pane.set_env( e )
    pane.init_layout(header=RulerView(pane))
    frame.insert_pane( pane )

    pane2 = SequencePane( m )
    pane2.set_env( e )
    pane2.init_layout(header=RulerView(pane2))
    frame.insert_pane( pane2 )

    frame.show()
    app.exec_()


if __name__ == '__main__':
    test_sequenceframe()
