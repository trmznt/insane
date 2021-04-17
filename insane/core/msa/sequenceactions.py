__copyright__ = '''
sequenceactions.py - part of seqpy/InSAnE

(c) 2011-2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore, QtWidgets
from insane.core.main.actions import IMainActions
from insane.core.base.menu import CommonMenuBar
from insane.core.base.selections import BlockSelection, ColumnSelection
from insane.core.base.messagebox import alert
from seqpy.core import bioio

import formlayout

class SequencePaneActions( IMainActions ):

    def init_actions(self):
        super(SequencePaneActions, self).init_actions()

        self._RULERSETTING = self.create_action('Ruler Setting', self.set_ruler,
                None, 'set-ruler', 'Ruler setting')

        self._ADD_TRANSLATIONPANE = self.create_action('Add Translation Pane',
                self.add_translation_pane, None, 'add-translationpane',
                'Add translation pane')

        self._REMOVE_PANE = self.create_action('Remove Pane', self.remove_pane,
                None, 'remove-pane', 'Remove this pane')

        # context menu actions
        self._STAT = self.create_action('Stat Selection', self.stat,
                None, 'stat-select', 'Provide statistics on selection')

    def edit_copy(self):
        s = self.model().selection()
        if isinstance(s, BlockSelection) or isinstance(s, ColumnSelection):
            s.copy()


    def edit_paste(self):
        m = self.model()
        clipboard = QtWidgets.QApplication.clipboard()
        byte_data = clipboard.text().encode('UTF-8')  # forced to string, not unicode etc
        if byte_data and m.caret():
            lines = byte_data.split(b'\n')
            idx, pos = m.caret().coord()
            for i, line in enumerate(lines):
                m.insert_at(idx + i, pos, line)
            m.signals().ContentUpdated.emit()
            m.caret().move(0,0)

    def edit_cut(self):
        s = self.model().selection()
        s.cut()


    def set_ruler(self):
        p = self.pane()
        datalist = [ ('Ruler start at', p._ruler_startpos),
                        ('ATG start at', p._ruler_atgframe)
                    ]
        result = formlayout.fedit( datalist, title='Ruler setting')
        p._ruler_startpos = result[0]
        p._ruler_atgframe = result[1]
        p.update()


    def add_translation_pane(self):
        m = self.model()
        if m.type() != bioio.DNA:
            alert('Protein sequences cannot be translated')
            return
        from .translatedpane import TranslatedSequencePane, TranslatedSequenceView
        from .sequencepane import SequenceView, RulerView
        frame = self.get_mainwin().mainframe()
        pane = TranslatedSequencePane( self.pane(), TranslatedSequenceView )
        pane.set_env( frame.env() )
        pane.init_layout( header=RulerView(pane) )
        frame.insert_pane( pane )


    def remove_pane(self):
        p = self.pane()
        # XXX: set focus to first pane
        p.hide()
        p.destroy()
        del p

    def menu_layout(self):
        return [
                ( '&File',
                    [   self._NEW,
                        self._NEWDBSEQ,
                        self._OPEN,
                        self._SAVE,
                        self._SAVEAS,
                        None,
                        self._CLOSE,
                        self._EXIT,
                    ]),
                ( '&Edit',
                    [   self._UNDO,
                        self._REDO,
                        None,
                        self._COPY,
                        self._CUT,
                        self._PASTE,
                        None,
                        self._PREF
                    ]),

                ( '&View',
                    [   self._RULERSETTING,
                        self._ADD_TRANSLATIONPANE,
                        self._REMOVE_PANE,
                    ]),

                ( '&Help',
                    [   self._ABOUT,
                    ]),
            ]

    def contextmenu_layout(self):
        return [
            self._STAT
        ]

    def stat(self):
        stat_res = self.model().selection().stat()
        sorted_res = sorted(stat_res[0].items(), key = lambda x: x[1] )
        print(stat_res[0])
        print(stat_res[1][sorted_res[0][0]])
