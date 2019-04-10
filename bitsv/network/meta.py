TX_TRUST_LOW = 1
TX_TRUST_MEDIUM = 6
TX_TRUST_HIGH = 30


class Unspent:
    """Represents an unspent transaction output (UTXO)."""
    __slots__ = ('amount', 'script', 'txid', 'txindex', 'confirmations')

    def __init__(self, amount, script, txid, txindex, confirmations):
        self.amount = amount
        self.script = script
        self.txid = txid
        self.txindex = txindex
        self.confirmations = confirmations

    def to_dict(self):
        return {attr: getattr(self, attr) for attr in Unspent.__slots__}

    @classmethod
    def from_dict(cls, d):
        return Unspent(**{attr: d[attr] for attr in Unspent.__slots__})

    def __eq__(self, other):
        return (self.amount == other.amount and
                self.script == other.script and
                self.txid == other.txid and
                self.txindex == other.txindex and
                self.confirmations == other.confirmations)

    def __repr__(self):
        return 'Unspent(amount={}, script={}, txid={}, txindex={}, confirmations={})'.format(
            repr(self.amount),
            repr(self.script),
            repr(self.txid),
            repr(self.txindex),
            repr(self.confirmations)
        )
