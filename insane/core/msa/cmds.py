

class EditingCommand(object):

    def __init__(self, model, params=None):
        pass

    def redo(self):
        pass

    def undo(self):
        pass


class InsertSequences(EditingCommand):
    pass

class DeleteSequences(EditingCommand):
    pass

class ReplaceSequences(EditingCommand):
    pass

class InsertAtSequence(EditingCommand):

    def __init__(self, seq, pos, segment):
        self._seq = seq
        self._pos = pos
        self._segment = segment

    def redo(self):
        self._seq[pos : pos] = segment

    def undo(self):
        del self._seq[pos : pos + len(self._segment)]

    def append(self, intchar):
        self._seqment.append(intchar)

class DeleteAtSequence(EditingCommand):
    pass

class ReplaceAtSequence(EditingCommand):
    pass

class InsertColumn(EditingCommand):
    pass

class DeleteColumn(EditingCommand):
    pass

