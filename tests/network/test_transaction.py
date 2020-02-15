from bitsv.network.transaction import Transaction, TxInput, TxOutput


class TestTransaction:
    def test_init(self):
        inputs = [TxInput(txid='txid', index=1)]
        outputs = [TxOutput(scriptpubkey='spk', amount=100000000)]

        transaction = Transaction(txid='txid', inputs=inputs, outputs=outputs)
        assert transaction.txid == 'txid'
        assert transaction.inputs == inputs
        assert transaction.outputs == outputs
        assert repr(transaction) == "Transaction(txid='txid', inputs=1, outputs=1)"
        assert repr(transaction.inputs) == "[Input(txid=txid, index=1)]"
        assert repr(transaction.outputs) == "[Output(scriptpubkey=spk, amount=100000000)]"
