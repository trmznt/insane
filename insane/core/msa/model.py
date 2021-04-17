
from insane.core.base.qtsignals import qt_msasignals
from seqpy.core import bioio, funcs

class DummySignals(object):

    def __init__(self, model):
        pass

class MSA(object):

    def __init__(self, multisequences, signals=None):
        self._msa = multisequences
        self._signals = signals or qt_msasignals()
        self._selection = None
        self._caret = None
        self._nt = None

        self._cmds = []
        self._cmd_idx = -1

    def caret(self):
        return self._caret

    def set_caret(self, caret):
        self._caret = caret

    def signals(self):
        return self._signals

    def filename(self):
        return self._msa.filename

    def selection(self):
        return self._selection

    def set_selection(self, selection):
        self._selection = selection

    def __getitem__(self, idx):
        return self._msa[idx]

    def __setitem__(self, idx, val):
        self._msa[idx] = val

    def __len__(self):
        return len(self._msa)

    def max_seqlen(self):
        return self._msa.max_seqlen()

    #
    # multisequence modifying method

    def insert(self, idx, sequence):
        self.insert_cmd( InsertSequence(self, idx, sequence) )

    def multiple_insert(self, idx, sequences):
        pass

    def delete(self, idx):
        self.insert_cmd( DeleteSequence(self, idx) )

    def move(self, srcidx, dstidx):
        self._msa.move(srcidx, dstidx)

    def append(self, sequence):
        self._msa.append( sequence )

    def extend(self, mseqs):
        return self._msa.extend( mseqs )

    #
    # sequence editing method

    def insert_at(self, idx, pos, segment):
        self.insert_cmd( InsAtSeq( self, idx, pos, segment ) )

    def delete_at(self, idx, pos):
        self.insert_cmd( DelAtSeq( self, idx, pos ) )

    #
    # label editing

    def set_label(self, idx, label):
        self.insert_cmd( ReplaceSequenceLabel( self, idx, label ) )
        

    #
    # misc methods

    def add_control(self, key, value):
        self._msa.add_control(key, value)

    def is_nucleotide(self):
        raise NotImplementedError
        return self._msa.is_nucleotide()

    def type(self):
        return self._msa.type()

    def set_type(self, msa_type):
        self._msa.set_type(msa_type)
        self.signals().SequenceTypeChanged.emit(None)
        self.signals().ContentUpdated.emit()

    def save(self, filename):
        bioio.save(self._msa, filename)

    def pop(self, idx):
        return self._msa.pop(idx)

    def clear(self):
        self._msa.clear()

    def deflate(self):
        self._msa.deflate()
        self.signals().ContentUpdated.emit()

    def shrink_gap(self):
        self._msa.shrink_gap()
        self.signals().ContentUpdated.emit()

    # process

    def align(self, *args):
        self._msa.align( *args )

    def sort(self, key=None, reverse=False):
        self._msa.sort(key, reverse)
        self._signals.ContentUpdated.emit()

    # undo/redo

    def insert_cmd(self, cmd):
        print('INSERT CMD')
        if self._cmd_idx != -1:
            del self._cmds[self._cmd_idx:]
            self._cmd_idx = -1
        cmd.redo()
        self._cmds.append( cmd )

    def undo(self):
        try:
            self._cmds[ self._cmd_idx ].undo()
            self._cmd_idx += -1
        except IndexError:
            print('Nothing to undo')

    def redo(self):
        pass


class _Cmd(object):

    def __init__(self, obj, *params):
        pass

    def redo(self):
        pass

    def undo(self):
        pass


class InsAtSeq(_Cmd):

    def __init__(self, model, idx, pos, sequence):
        self._model = model
        self._idx = idx
        self._pos = pos
        self._sequence = sequence

    def redo(self):
        print('inserting segment')
        self._model[self._idx][self._pos : self._pos] = self._sequence
        self._model.signals().ContentUpdated.emit()

    def undo(self):
        print('undo-ing InsAtSeq')
        del self._model[self._idx][self._pos : self._pos + len(self._sequence)]
        self._model.signals().ContentUpdated.emit()


class RepAtSeq(_Cmd):
    pass


class DelAtSeq(_Cmd):

    def __init__(self, model, idx, pos):
        self._model = model
        self._idx = idx
        self._pos = pos
        self._char = self._model[self._idx][self._pos:self._pos]

    def redo(self):
        del self._model[self._idx][ self._pos : self._pos + 1]

    def undo(self):
        print(self._model[self._idx])
        print("char:",self._char)
        self._model[self._idx][ self._pos : self._pos ] = self._char
        print(self._model[self._idx])


class InsertSequence(_Cmd):

    def __init__(self, model, idx, sequence):
        self._model = model
        self._idx = idx
        self._sequence = sequence

    def redo(self):
        self._model._msa.insert(self._idx, self._sequence)
        self._model.signals().ContentUpdated.emit()

    def undo(self):
        self._model._msa.delete(self._idx)
        self._model.signals().ContentUpdated.emit()


class DeleteSequence(_Cmd):

    def __init__(self, model, indices):
        self._model = model
        if type(indices) == int:
            self._indices = [ indices ]
        else:
            self._indices = sorted(indices)
        self._seqs = [ model[i] for i in self._indices ]

    def redo(self):
        self._model._msa.delete(self._indices)
        self._model.signals().ContentUpdated.emit()

    def undo(self):
        for i,s in reversed( list(zip(self._indices, self._seqs)) ):
            self._model._msa.insert( i, s )
        self._model.signals().ContentUpdated.emit()


class ReplaceSequenceContent(_Cmd):

    def __init__(self, model, idx, new_sequence):
        self._model = model
        self._idx = idx
        self._oldseq = self._model[idx].seq
        self._newseq = new_sequence

    def redo(self):
        seq = self._model[self._idx]
        seq.set_sequence( self._newseq )

    def undo(self):
        seq = self._model[self._idx]
        seq.set_sequence( self._oldseq )


class ReplaceSequenceLabel(_Cmd):

    def __init__(self, model, idx, label):
        print("Replace sequence label")
        self._model = model
        self._idx = idx
        self._oldlabel = self._model[self._idx].label
        self._newlabel = label

    def redo(self):
        seq = self._model[self._idx]
        seq.set_label( self._newlabel )
        # XXX: shouldn't we have LabelUpdated.emit()

    def undo(self):
        seq = self._model[self._idx]
        seq.set_label( self._oldlabel )


class InsertSequences(_Cmd):

    def __init__(self, model, idx, msa):
        pass


class DeleteSequences(_Cmd):

    def __init__(self, model, indices):
        pass


