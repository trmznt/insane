
import time
from insane import QtGui, QtCore, QtWidgets

class ConsoleLog(QtWidgets.QMainWindow):

    """
    ConsoleLog - provides console window for logging purposes
    """

    def __init__(self, parent=None):
        super(ConsoleLog, self).__init__(parent)
        self.start_time = time.time()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Console Log ~ SeqPy/InSAnE")
        self.plaintextedit = QtWidgets.QPlainTextEdit()
        self.plaintextedit.setReadOnly(True)
        self.plaintextedit.setMaximumBlockCount(250)
        self.setCentralWidget( self.plaintextedit )
        self.write('console log created')

    def write(self, text):
        delta = time.time() - self.start_time
        self.plaintextedit.appendPlainText('[ %9.1f ] %s' % (delta, text) )

    def sizeHint(self):
        return QtCore.QSize(600,150)

    def closeEvent(self, ev):
        self.hide()
        ev.ignore()



_consolelog_ = None


def get_consolelog():
    global _consolelog_
    if not _consolelog_:
        _consolelog_ = ConsoleLog()
        _consolelog_.show()
    return _consolelog_


def writelog(txt):
    get_consolelog().write( txt )


def show_console():
    get_consolelog().show()

