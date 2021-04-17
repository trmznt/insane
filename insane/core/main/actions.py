__copyright__ = '''
actions.py - part of seqpy/InSAnE

(c) 2011 - 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

_version_ = '0.3.1'


from insane import QtGui, QtCore, QtWidgets
from insane.core.base.actions import CommonPaneActions
from insane.core.base.messagebox import progress, alert
from seqpy import cout, cerr
from seqpy.core import bioio, traceio
import os, time

class IMainActions(CommonPaneActions):

    def file_new(self):
        obj = bioio.multisequence()
        obj.set_filename('untitled')
        self.view( obj )

    def file_newdbseq(self):
        pass

    def file_open(self, filename=None):

        if not filename:
            filename, file_filter = QtWidgets.QFileDialog.getOpenFileName( self.pane(),
                    "Open project, alignment or trace file" )

        if not filename:
            return

        cout("Loading file %s" % filename)
        if not os.path.exists( filename ):
            alert('File %s does not exists. Please check your filename!' % filename)
            return

        b = progress('Opening ' + filename)
        b.repaint()
        obj = bioio.load( filename )
        b.hide()
        del b

        if obj:
            self.view(obj)
        else:
            alert('Error reading file ' + filename +'\nUnknown file format!')

    def edit_undo(self):
        print("undo")
        self.model().undo()
      
    def edit_redo(self):
        self.model().redo()

    def view(self, obj):

        frame_class = None
        m = None

        print(obj)
        if hasattr(obj, 'edit_bases'):
            print(obj)

            from insane.core.trace.frame import TraceFrame
            from insane.core.trace.model import tracemodel
            m = tracemodel(obj)
            frame_class = TraceFrame

        elif hasattr(obj, 'type'):

            from insane.core.msa.frame import SequenceFrame
            from insane.core.msa.model import MSA
            m = MSA( obj )
            frame_class = SequenceFrame
            cout('MSA prepared')

        if frame_class and m is not None:
            frame = frame_class( self.get_mainwin().default_env, m)
            cout('Frame created')
            win = self.get_mainwin()
            if win.mainframe() is None:
                win.setWindowTitle( m.filename() + ' - seqpy/InSAnE' )
                win.show_centralwidget( frame )
            else:
                from insane.core.main.mainwin import IMainWindow
                w = IMainWindow()
                w.setWindowTitle( m.filename() + ' - seqpy/InSAnE' )
                w.show_centralwidget( frame )
                w.show()


    def file_saveas(self):
        filename, file_filter = QtWidgets.QFileDialog.getSaveFileName( self.pane(),
                "Save alignment as" )
        print(filename)
        if filename:
            m = self.model()
            m.save( filename )
            self.get_mainwin().setWindowTitle( m.filename() + ' ~ seqpy/InSAnE' )


    def file_save(self):
        m = self.model()
        m.save( m.filename() )


    def file_exit(self):
        app = QtGui.QApplication.instance()
        app.quit()


    def edit_preference(self):
        pass


    def help_about(self):
        QtGui.QMessageBox.about(self.pane(), 
            "About SeqPy/InSAnE",
            'seqpy/InSAnE (Integrated Sequence Alignment and Editor)\n'
            'Version ' + _version_ + '\n\n'
            'Copyright \N{COPYRIGHT SIGN} 2009-2012 Hidayat Trimarsanto\n\n'
            'This program is part of SeqPy, a Python library for sequence processing.'
            )


    def menu_layout(self):
        return [
               ( '&File',
                    [   self._NEW, self._NEWDBSEQ, None, self._OPEN, None, self._EXIT ] ),
                ( '&Edit',
                    [   self._PREF ] ),
                ( '&Window',
                    [   self._SHOWCONSOLE ]),
                ( '&Help',
                    [   self._ABOUT ] ),
            ]




