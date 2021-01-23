

class Transaction:
    """Represents a transaction returned from the network."""

    __slots__ = ('txid', 'inputs', 'outputs')

    def __init__(self, txid, inputs, outputs):
        self.txid = txid
        self.inputs = inputs
        self.outputs = outputs

    def __repr__(self):
        return 'Transaction(txid={}, inputs={}, outputs={})'.format(
                repr(self.txid),
                len(self.inputs),
                len(self.outputs))


class TxInput:
    """
    Representation of a single input
    """

    def __init__(self, txid, index):
        self.txid = txid
        self.index = index

    def __repr__(self):
        return "Input(txid={}, index={})".format(self.txid, self.index)


class TxOutput:
    """
    Representation of a single output.
    """

    def __init__(self, scriptpubkey, amount):
        self.scriptpubkey = scriptpubkey
        self.amount = amount  # satoshis
        self.data_carrier = None

        if scriptpubkey is None:
            if scriptpubkey.startswith('006a'):
                self.data_carrier = True

    def __repr__(self):
        if self.scriptpubkey is None and self.data_carrier is not None:
            return "Output(OP_FALSE OP_RETURN, amount_burned={:.0f})".format(self.amount)
        else:
            return "Output(scriptpubkey={}, amount={})".format(self.scriptpubkey, self.amount)
