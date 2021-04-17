__copyright__ = '''
labelactions.py - part of seqpy/InSAnE

(c) 2011-2012 Hidayat Trimarsanto <anto@eijkman.go.id> / <trimarsanto@gmail.com>

All right reserved.
This software is licensed under GPL v3 or later version.
Please read the README.txt of this software.
'''

from insane import QtGui, QtCore
from insane.core.main.actions import IMainActions
from insane.core.base.menu import CommonMenuBar
from insane.core.base.selections import LabelSelection, ColumnSelection, BlockSelection, get_clipboard_selection
from insane.core.base.debug import D, ALL, INFO
from insane.core.base.messagebox import progress, alert
from seqpy.core import bioio, funcs
from io import BytesIO

class LabelPaneActions( IMainActions ):

    def init_actions(self):
        super(LabelPaneActions, self).init_actions()
        self._SELECT_ALL = self.create_action('Select all', self.select_all,
                None, 'select-all', 'Select all sequences')

        self._DESELECT_ALL = self.create_action('Deselect all', self.deselect_all,
                None, 'deselect-all', 'Deselect all sequences'),

        self._NEW_SEQUENCE = self.create_action('New sequence', self.new_sequence,
                'Ctrl+I', 'new-sequence', 'Insert a new sequence')

        self._SORT_AZ = self.create_action('Sort A-Z', self.sort_az,
                None, 'sort-az', 'Sort label alphabetically')

        self._SORT_ZA = self.create_action('Sort Z-A', self.sort_za,
                None, 'sort-za', 'Sort label Z-A')

        self._SORT_LEN = self.create_action('Sort by length', self.sort_len,
                None, 'sort-len', 'Sort by sequence length')

        self._CONS_50 = self.create_action('50%', self.make_consensus_50,
                None, 'cons-50', 'Create 50% consensus')

        self._CONS_75 = self.create_action('75%', self.make_consensus_75,
                None, 'cons-75', 'Create 75% consensus')

        self._CONS_90 = self.create_action('90%', self.make_consensus_90,
                None, 'cons-90', 'Create 90% consensus')

        self._CONS_95 = self.create_action('95%', self.make_consensus_95,
                None, 'cons-95', 'Create 95% consensus')

        self._CONS_99 = self.create_action('99%', self.make_consensus_99,
                None, 'cons-99', 'Create 99% consensus')

        self._CONS_ALL = self.create_action('ALL', self.make_consensus_all,
                None, 'cons-all', 'Create all consensus')

        self._CONS_MARKER = self.create_action('MARKER', self.make_consensus_marker,
                None, 'cons-marker', 'Create marker consensus')

        self._REVERSE_COMPLEMENT = self.create_action('&Reverse complement',
                self.reverse_complement, 'Ctrl+R',
                'rev-comp', 'Reverse complement DNA sequence')

        self._DEGAP = self.create_action('&Degap sequence',
                self.degap, 'Ctrl+D',
                'degap', 'Remove gap(s) in sequence')

        self._DEFLATE = self.create_action('Deflate alignment',
                self.deflate, None, 'deflate',
                'Remove empty (dash-only) sequence from alignment')

        self._CONDENSE = self.create_action('Condense alignment',
                self.condense, None, 'condense',
                'Remove non-polymorphic column')

        self._SHRINK_GAP = self.create_action('Shrink gaps of alignment',
                self.shrink_gap, None, 'shrink-gap',
                'Remove gap-only column from alignment')

        self._OLIGO_MATCH = self.create_action('Primer and oligo match',
                self.oligo_match, None, 'oligo-match',
                        'Hybridize oligonucleotides')

        self._PWALIGN_GLOCAL = self.create_action('Global-local',
                self.pwalign_glocal, None, 'pwalign-glocal',
                'Global/local pairwise alignment')

        self._PWALIGN_GLOBAL = self.create_action('Global', self.pwalign_global,
                None, 'pwalign-global', 'Global pairwise alignment')

        self._PWALIGN_LOCAL = self.create_action('Local', self.pwalign_local,
                None, 'pwalign-local', 'Local pairwise alignment')

        self._ADD_PANE = self.create_action('Add pane', self.add_pane,
                None, 'add-pane', 'Add new sequence pane')

        self._ADD_SPLITTER = self.create_action('Add splitter', self.add_splitter,
                None, 'add-splitter', 'Add another view splitter')

        self._REMOVE_SPLITTER = self.create_action('Remove splitter',
                self.del_splitter, None, 'del-splitter', 'Remove additional splitter')

        self._SET_DNA = self.create_action('DNA',
                self.set_DNA, None, 'DNA-type', 'Set sequence type to DNA')

        self._SET_RNA = self.create_action('RNA',
                self.set_RNA, None, 'RNA-type', 'Set sequence type to RNA')

        self._SET_PROTEIN = self.create_action('Protein/AA',
                self.set_protein, None, 'AA-type', 'Set sequence type to protein')

        self._REPORT_LEN = self.create_action('Report Length',
                self.report_len, None, 'report-len', 'Report sequence length stats')


    def edit_copy(self):
        s = self.model().selection()
        if isinstance(s, LabelSelection):
            s.copy()

    def edit_cut(self):
        s = self.model().selection()
        s.cut()
        self.model().set_selection( None )
        LabelSelection( self.model(), -1)
            

    def edit_paste(self):
        selection = self.model().selection()
        if selection is None:
            selection = LabelSelection( self.model(), -1 )
        selection.paste()
        return

        p = self.pane()
        m_dst = self.model()
        clipboard = QtGui.QApplication.clipboard()

        # check whether we are the owner of clipboard content
        if clipboard.ownsClipboard():
            D(ALL, "should perform direct copying")
            # access the global selection
            selection = get_clipboard_selection()
            if hasattr(selection, 'get_sequence'):
                seq = selection.get_sequence()
                m_dst.append( seq )
                m_dst.signals().ContentUpdated.emit()
            elif isinstance( selection, LabelSelection ):
                m_src = selection.model()
                m_dst = p.model()
                for i in selection._index_selections:
                    m_dst.append( m_src[i] )
                m_dst.signals().ContentUpdated.emit()
            elif isinstance( selection, BlockSelection ):
                pass
            elif isinstance( selection, ColumnSelection ):
                p.model().add( selection.copy_to_msa() )
                p.model().signals().ContentUpdated.emit()
                    
        else:
            text_data = str(clipboard.text())   # forced to string, not unicode etc
            if text_data.startswith('>'):
                # we assume it is FASTA format for now
                mseqs = bioio.read_fasta_stream( BytesIO(text_data) )
                p.model().add( mseqs )
                p.model().signals().ContentUpdated.emit()
            else:
                print( 'Unknown paste format' )
                
    def select_all(self):
        m = self.model()
        selection = LabelSelection(m, 0)
        selection.shift_click( len(m) )
        
    
    def deselect_all(self):
        m = self.model()
        s = m.selection()
        if isinstance(s, LabelSelection):
            s.clear()

    def add_pane(self):
        from .sequencepane import SequencePane, SequenceView, RulerView
        frame = self.get_mainwin().mainframe()
        pane = SequencePane( self.model(), SequenceView )
        pane.set_env( frame.env() )
        pane.init_layout( header=RulerView(pane) )
        frame.insert_pane( pane )
        
    def add_splitter(self):
        frame = self.get_mainwin().mainframe()
        split = frame.vsplit()
        frame.set_vsplit( split + 1)
        
    def del_splitter(self):
        frame = self.get_mainwin().mainframe()
        split = frame.vsplit()
        if split > 1:
            frame.set_vsplit( split - 1)

    def new_sequence(self):
        n = bioio.biosequence('~new~', b'')
        m = self.model()
        s = m.selection()
        if s is not None:
            idx = max( s.indices() )
            m.insert( idx, n )
        else:
            m.append(n)
        m.signals().ContentUpdated.emit()

    def sort_az(self):
        #print "sort A-Z"
        m = self.model()
        m.sort( lambda x: x.label )

    def sort_za(self):
        m = self.model()
        m.sort( lambda x: x.label, reverse=True )

    def sort_len(self):
        m = self.model()
        m.sort( lambda x: len(x), reverse=True )

    def sort_custom(self, func):
        pass
    
    def make_consensus(self, thresholds = [ 0.5, 0.75, 0.90, 0.95, 0.99] ):
        from seqpy.core.funcs.profiles import na_profile, aa_profile
        m = self.model()
        if isinstance(m.selection(), LabelSelection):
            msa = m.selection().copy_to_msa()
        else:
            msa = m
        if m.type() == bioio.PROTEIN:
            profile = aa_profile(msa)
        else:
            profile = na_profile(msa)
        for th in thresholds:
            m.append(bioio.biosequence('CONS-%3.2f' % th, profile.consensus(th)))
        m.signals().ContentUpdated.emit()

    def make_consensus_50(self):
        self.make_consensus( [ 0.50 ] )
    def make_consensus_75(self):
        self.make_consensus( [ 0.75 ] )
    def make_consensus_90(self):
        self.make_consensus( [ 0.90 ] )
    def make_consensus_95(self):
        self.make_consensus( [ 0.95 ] )
    def make_consensus_99(self):
        self.make_consensus( [ 0.99 ] )
    def make_consensus_all(self):
        self.make_consensus()

    def make_consensus_marker(self):
        from seqpy.core.funcs.profiles import na_profile, aa_profile
        m = self.model()
        if isinstance(m.selection(), LabelSelection):
            msa = m.selection().copy_to_msa()
        else:
            msa = m
        if m.type() == bioio.PROTEIN:
            profile = aa_profile(msa)
        else:
            profile = na_profile(msa)

        cons_seq = bytearray()
        cons = profile.mat
        for i in range(0, len(cons)):
            max_pos = cons[i].argmax()
            if cons[i, max_pos] < 0.99:
                cons_seq.append( 42 )
                print(i)
            else:
                cons_seq.append( 32 )
        m.append(bioio.biosequence('CONS-MARKER', cons_seq))
        m.signals().ContentUpdated.emit()

    def reverse_complement(self):
        m = self.model()
        if isinstance(m.selection(), LabelSelection):
            m.selection().apply( lambda x: x.set_sequence(funcs.reverse_complemented(x)) )
        else:
            m.apply( lambda x: x.set_sequence(funcs.reverse_complemented(x) ) )

    def degap(self):
        m = self.model()
        if isinstance(m.selection(), LabelSelection):
            m.selection().apply( lambda x: x.set_sequence(funcs.degapped(x)) )
        else:
            m.apply( lambda x: x.set_sequence(funcs.degapped(x)) )

    def deflate(self):
        m = self.model()
        m.deflate()

    def oligo_match(self):
        pass

    def pwalign_global(self):
        self.pwalign(method='global')
        
    def pwalign_local(self):
        self.pwalign(method='local')
        
    def pwalign_glocal(self):
        self.pwalign(method='global_cfe')

    def pwalign(self, method):
        m = self.model()
        s = m.selection()
        if isinstance(s, LabelSelection) and len(s) == 2:
            box = progress("Alignment in progress...")
            box.setValue(5)
            box.wasCanceled()
            m.align( s.indices(), method )
            box.setValue(10)
            m.signals().ContentUpdated.emit()
        else:
            alert('You must select exactly two sequences for pairwise alignment')

    def condense(self):
        m = self.model()
        c = funcs.condensed(m._msa)
        c.set_filename('~')
        self.view(c)

    def shrink_gap(self):
        m = self.model()
        m.shrink_gap()

    def dot_plot(self):
        m = self.model()
        if isinstance(m.selection(), LabelSelection):
            s = m.selection()
            if len(s) == 2:
                pass
                
    def matrix_identity(self):
        m = self.model()
        if isinstance(m.selection(), LabelSelection):
            s = m.selection()
            if len(s) >= 2:
                pass

    def set_auto(self):
        m = self.model()
        m.type()

    def set_DNA(self):
        self.model().set_type(bioio.DNA)

    def set_RNA(self):
        cerr("ERR: set_RNA() hasn't been implemented")

    def set_protein(self):
        self.model().set_type(bioio.PROTEIN)

    def report_len(self):
        m = self.model()
        lengths = [ (len(s), i) for i, s in enumerate(m) ]
        lengths.sort()
        print('Max len: %d at %d' % (lengths[-1][0], lengths[-1][1]))
        print('Min len: %d at %d' % (lengths[0][0], lengths[0][1]))

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
                        self._EXIT
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

                ( '&Sequence',
                    [   self._NEW_SEQUENCE,
                        self._DEGAP,
                        None,
                        self._DEFLATE,
                        self._CONDENSE,
                        self._SHRINK_GAP,
                        None,
                        ( 'Type',
                            [   self._SET_DNA,
                                self._SET_RNA,
                                self._SET_PROTEIN
                            ]),
                        ( 'Sort',
                            [   self._SORT_AZ,
                                self._SORT_ZA,
                                self._SORT_LEN
                            ]),
                        ( 'Align',
                            [   self._PWALIGN_GLOCAL,
                                self._PWALIGN_GLOBAL,
                                self._PWALIGN_LOCAL
                            ]),
                        ( 'Consensus',
                            [   self._CONS_50,
                                self._CONS_75,
                                self._CONS_90,
                                self._CONS_95,
                                self._CONS_99,
                                self._CONS_ALL,
                                self._CONS_MARKER
                            ]),
                        ( 'DNA',
                            [   self._REVERSE_COMPLEMENT,
                                self._OLIGO_MATCH,
                            ]),
                        ( 'Reports',
                            [   self._REPORT_LEN,
                            ]),
                    ]),

                ( '&View',
                    [   self._ADD_PANE,
                        ( 'Vertical splitter',
                            [   self._ADD_SPLITTER,
                                self._REMOVE_SPLITTER,
                            ]),
                    ]),

                ( '&Help',
                    [   self._ABOUT,
                    ])
            ] 

    def contextmenu_layout(self):
        return [
            self._COPY,
            self._CUT,
            self._PASTE,
            None,
            self._NEW_SEQUENCE,
            self._DEGAP,
            None,
            self._DEFLATE,
            None,
            ( 'DNA',
                [   self._REVERSE_COMPLEMENT,
                    self._OLIGO_MATCH,
                ]),
            ( 'Align',
                [   self._PWALIGN_GLOCAL,
                    self._PWALIGN_GLOBAL,
                    self._PWALIGN_LOCAL
                ]),

        ]

    def selectionmenu_layout(self):
        pass


