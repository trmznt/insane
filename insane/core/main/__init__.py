

from seqpy import cout, cerr
from seqpy.core import bioio #, traceio
from insane import QtGui, QtCore
from .mainwin import IMainWindow

app = None

def start_app(arg):
    global app
    cout("Starting GUI\n")

    if not app:
        app = QtGui.QApplication.instance()
        if not app:
            if type(arg) == list:
                app = QtGui.QApplication(arg)
            else:
                app = QtGui.QApplication(['__builtin__'])

    w = IMainWindow()

    if type(arg) == list and len(arg) >= 2:
        w.load( arg[1] )
    elif type(arg) == str:
        w.load( arg )
    else:
        cout('viewing...')
        w.view( arg )
        #w.setFocus()
    w.show()
    app.exec_()

    try:
        w.hide()
        del w
    except RuntimeError:
        pass
    
    
