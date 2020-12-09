


class Block:
    """Represents a block returned from the network."""

    __slots__ = ('hash', 'height', 'prev', 'next', 'txs')

    def __init__(self, hash, height, prev, next, txs):
        self.hash = hash
        self.height = height
        self.prev = prev
        self.next = next
        self.txs = txs

    def __eq__(self, other):
        return (self.hash == other.hash and
                self.height == other.height and
                self.prev == other.prev and
                self.next == other.next and
                self.txs == other.txs)

    def __repr__(self):
        return 'Block(hash={}, height={}, txs={}, prev={}, next={})'.format(
            repr(self.hash),
            self.height,
            len(self.txs),
            repr(self.prev),
            repr(self.next))
