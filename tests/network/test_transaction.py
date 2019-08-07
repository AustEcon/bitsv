from bitsv.network.transaction import Transaction

import pytest


class TestTransaction:
    def test_init(self):
        transaction = Transaction(txid='txid', amount_in=10000, amount_out=9000)
        assert transaction.amount_in == 10000
        assert transaction.amount_out == 9000
        assert transaction.fee == 1000
        assert transaction.txid == 'txid'
        # More output than input
        with pytest.raises(ArithmeticError):
            Transaction(txid='txid', amount_in=10000, amount_out=10001)
