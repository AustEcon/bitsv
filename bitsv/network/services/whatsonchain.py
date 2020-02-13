from typing import List

from whatsonchain.api import Whatsonchain

from bitsv.constants import BSV
from bitsv.network.meta import Unspent
from bitsv.network.transaction import TxInput, TxOutput, Transaction


def woc_tx_to_transaction(response):
    tx_inputs = []
    for vin in response['vin']:
        tx_input = TxInput(txid=vin['txid'], index=vin['vout'])
        tx_inputs.append(tx_input)

    tx_outputs = []
    for vout in response['vout']:
        tx_output = TxOutput(scriptpubkey=vout['scriptPubKey']['hex'],
                             amount=int(vout['value']*BSV))
        tx_outputs.append(tx_output)
    tx = Transaction(response['txid'], tx_inputs, tx_outputs)

    return tx


def woc_utxos_to_unspents(woc_utxos, block_height):
    utxos = []
    for utxo in woc_utxos:
        u = Unspent(amount=utxo['value'],
                    confirmations=0 if utxo['height'] in [0, -1] else block_height-utxo['height']+1,
                    txid=utxo['tx_hash'],
                    txindex=utxo['tx_pos'])
        utxos.append(u)
    return utxos


class WhatsonchainNormalised(Whatsonchain):
    """A wrapper for https://pypi.org/project/whatsonchain/ to return bitsv-compatible types."""

    def __init__(self, network, *args, **kwargs):
        super().__init__(network, *args, **kwargs)

    def get_balance(self, address: str) -> int:
        result = super().get_balance(address)
        return result['confirmed'] + result['unconfirmed']

    def get_transactions(self, address: str) -> List[str]:
        hist = self.get_history(address)
        return [tx['tx_hash'] for tx in hist]

    def get_transaction(self, txid: str) -> Transaction:
        response = self.get_transaction_by_hash(txid)
        return woc_tx_to_transaction(response)

    def get_unspents(self, address: str) -> List[Unspent]:
        block_height = self.get_chain_info()['blocks']
        utxos = self.get_utxos(address)
        return woc_utxos_to_unspents(utxos, block_height)

    def send_transaction(self, tx_hex: str) -> str:
        return self.broadcast_rawtx(tx_hex)
