__copyright__ = '''
dndviews.py - part of seqpy/InSAnE

(c) 2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets
from seqpy.core import bioio
import time, os


class DNDLabel(object):

    def __init__(self, v):
        self._view = v
        v.setAcceptDrops(True)
        self._startpos = None
        self._clicktime = None
        self._drag_idx = -1
        #print 'DNDLabel()'

    def prepare_drag(self, pos):
        #print 'prepare_drag'
        self._startpos = pos
        self._clicktime = time.time()

    def drag_position(self):
        return self._startpos

    def model(self):
        return self._view.model()

    def dragging(self, ev):
        #print 'check dragging at', time.time() - self._clicktime
        if self._startpos and ( time.time() - self._clicktime > 0.25) and ( (ev.pos() - self._startpos).manhattanLength() <
                QtWidgets.QApplication.startDragDistance() ):
            self.startDrag()

    def check_mimetype(self, ev):
        mimedata = ev.mimeData()
        if ( mimedata.hasUrls() or
                mimedata.hasFormat("application/x-fasta") or
                mimedata.hasText() ):
            return True
        return False

    def dragEnterEvent(self, ev):
        if self.check_mimetype( ev ):
            ev.accept()
        else:
            ev.ignore()

    def dragMoveEvent(self, ev):
        #print "dragMoveEvent"
        if self.check_mimetype( ev ):
            ev.setDropAction(QtCore.Qt.CopyAction)
            idx, _ = self._view.xy2coord(0, ev.pos().y())
            #self.set_hilight( idx )
            ev.accept()
        else:
            ev.ignore()

    def dropEvent(self, ev):
        #print 'Source:', ev.source()
        #D( ALL, "drop source: %s" % str(ev.source()) )
        if ev.mimeData().hasUrls():
            url = str(ev.mimeData().urls()[0].path())
            #D( ALL, "url: %s" % url )
            #print "will open:", str(ev.mimeData().urls()[0])
            if True:
                #filename = url[7:]
                filename = url
                obj = bioio.load( filename )
                if hasattr(obj, 'get_sequence'):
                    self.model().append( obj.get_sequence() )
                else:
                    self.model().add( obj )

                self.model().signals().ContentUpdated.emit()
                return

                if filename.endswith('.scf') or filename.endswith('.ab1'):
                    # this is a trace file, just grab the sequence data
                    from seqpy.traceio import read_trace
                    trace = bioio.load( filename )
                    self.model().append(
                        bioio.sequence( trace.name(), trace.bases() ) )
                else:
                    #D( ALL, "opening file: %s" % filename )
                    mseq = bioio.read_sequences( filename )
                    self.model().add( mseq )
                self._view.model().signals().ContentUpdated.emit()


        elif ev.source() == self._view:
            idx, _ = self._view.xy2coord(0, ev.pos().y())
            seq = self.model()[self._dragidx]
            if idx < self._dragidx:
                self.model().delete(self._dragidx)
                self.model().insert(idx, seq)
            elif idx > self._dragidx:
                self.model().insert(idx, seq)
                self.model().delete(self._dragidx)

            #self.model().conn().contentUpdated.emit()

        elif isinstance(ev.source(), type(self._view)):
            src = ev.source()
            idx, _ = self._view.xy2coord(0, ev.pos().y())

            if src.model() == self.model():
                # the same model, then just use model's move method
                if src.dnd()._dragidx != idx:
                    self.model().move( src.dnd()._dragidx, idx)
                    self.model().signals().ContentUpdated.emit()
            else:
                seq = src.model().pop(src.dnd()._dragidx)
                #src.model().delete(src.dnd()._dragidx)
                self.model().insert(idx, seq)
                src.model().signals().ContentUpdated.emit()
                self.model().signals().ContentUpdated.emit()

            #self.model().signals().contentUpdated.emit()
            #src.model().signals().contentUpdated.emit()

        else:
            D( ALL, "drop event with unknown type" )
            


    def startDrag(self):
        """ this method is called whenever a user start to drag one of the label """

        #D( ALL, "dragging started..." )
        v = self._view
        lp = v.painter()
        fm = lp.fontmetrics()
        idx, _ = v.xy2coord( 0, self._startpos.y() )
        self._dragidx = idx
        label = self.model()[idx].label
        lineheight = v.lineheight()
        baseline = (lineheight + fm.ascent())/2
        width = fm.width(label)
        hotspot = QtCore.QPoint( width/2, lineheight/2 )
        drag = QtGui.QDrag(v)

        pixmap = QtGui.QPixmap(width, lineheight)
        p = QtGui.QPainter(pixmap)
        p.fillRect(pixmap.rect(), QtGui.QColor(191, 191, 127))
        p.setPen( QtCore.Qt.white )
        p.setFont( lp.font() )
        p.drawText(0, baseline, label)
        p.end()
        
        # fill in the data
        seq = self.model()[idx]
        mimedata = QtCore.QMimeData()
        text_data = ">%s\n%s\n" % (seq.label, seq.seq)
        mimedata.setText( text_data )
        mimedata.setData("application/x-fasta", text_data.encode('UTF-8'))

        drag.setMimeData(mimedata)
        drag.setPixmap(pixmap)
        drag.setHotSpot(hotspot)
        drag.exec_(QtCore.Qt.CopyAction)


