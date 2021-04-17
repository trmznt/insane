__copyright__ = '''
messagebox.py - part of seqpy/InSAnE

(c) 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets

def alert(msg):
    msgbox = QtWidgets.QMessageBox()
    msgbox.setWindowTitle('Error')
    msgbox.setText(msg)
    msgbox.exec_()

def progress(msg, maxvalue=10):
    msgbox = QtWidgets.QProgressDialog(msg, 'Cancel', 0, maxvalue)
    #msgbox.setWindowTitle('')
    #msgbox.setText(msg)
    #msgbox.setStandardButtons(QtGui.QMessageBox.NoButton)
    msgbox.setModal(True)
    msgbox.show()
    msgbox.setValue(0)
    QtWidgets.qApp.processEvents()
    return msgbox

