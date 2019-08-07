

class Transaction:
    """Represents a transaction returned from the network."""

    __slots__ = ('txid', 'amount_in', 'amount_out', 'fee', 'inputs', 'outputs')

    def __init__(self, txid, amount_in, amount_out):
        self.txid = txid
        self.fee = amount_in - amount_out

        if amount_in != amount_out + self.fee:
            raise ArithmeticError("amount in is not equal to amount out + fee.")

        self.amount_in = amount_in
        self.amount_out = amount_out

        self.inputs = []
        self.outputs = []

    def add_input(self, part):
        self.inputs.append(part)

    def add_output(self, part):
        self.outputs.append(part)

    def __repr__(self):
        return 'Transaction(txid={}, amount_in={}, amount_out={}, ' \
               'fee={}, inputs={}, outputs={})'.format(
                repr(self.txid),
                repr(self.amount_in),
                repr(self.amount_out),
                repr(self.fee),
                len(self.inputs),
                len(self.outputs))


class TxInput:
    """
    Representation of a single input or output.
    """

    def __init__(self, address, amount):
        self.address = address
        self.amount = amount

    def __repr__(self):
        return "Input(address={}, amount={:.0f})".format(self.address, self.amount)


class TxOutput:
    """
    Representation of a single input or output.
    """

    def __init__(self, address, amount, asm=None):
        self.address = address
        self.amount = amount
        self.op_return = None

        if address is None and asm is not None:
            if asm.startswith('OP_RETURN '):
                self.op_return = asm[10:]
            elif asm.startswith('return ['):
                self.op_return = asm[8:-1]

    def message(self):
        """Attempt to decode the op_return value (if there is one) as a UTF-8 string."""

        if self.op_return is None:
            return None

        return bytearray.fromhex(self.op_return).decode('utf-8')

    def __repr__(self):
        if self.address is None and self.op_return is not None:
            return "Output(OP_RETURN={}, amount_burned={})".format(self.message(), self.amount)
        else:
            return "Output(address={}, amount={:.0f})".format(self.address, self.amount)
