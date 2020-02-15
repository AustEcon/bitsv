import requests
import json
from decimal import Decimal

from bitsv.network import currency_to_satoshi
from bitsv.network.meta import Unspent

# left here as a reminder to normalize get_transaction()
from bitsv.network.transaction import Transaction, TxInput, TxOutput
from bitsv.constants import BSV

DEFAULT_TIMEOUT = 30
BSV_TO_SAT_MULTIPLIER = BSV


class BCHSVExplorerAPI:
    """
    Simple bitcoin SV REST API --> uses base58 address format (addresses start with "1")
    - get_address_info
    - get_balance
    - get_transactions
    - get_transaction
    - get_unspent
    - broadcast_tx
    """
    MAIN_ENDPOINT = 'https://bchsvexplorer.com/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'api/addr/{}'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + '/balance'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '/utxo'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'api/tx/send/'
    MAIN_TX_API = MAIN_ENDPOINT + 'api/tx/{}'
    MAIN_TX_AMOUNT_API = MAIN_TX_API
    TX_PUSH_PARAM = 'create_rawtx'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    @classmethod
    def get_address_info(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()['transactions']

    @classmethod
    def get_transaction(cls, txid):
        r = requests.get(cls.MAIN_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        response = r.json(parse_float=Decimal)

        tx_inputs = []
        for vin in response['vin']:
            tx_input = TxInput(vin['txid'], vin['vout'])
            tx_inputs.append(tx_input)

        tx_outputs = []
        for vout in response['vout']:
            tx_output = TxOutput(scriptpubkey=vout['scriptPubKey']['hex'], amount=vout['valueSat'])
            tx_outputs.append(tx_output)
        tx = Transaction(response['txid'], tx_inputs, tx_outputs)

        return tx

    @classmethod
    def raw_get_transaction(cls, txid):
        """un-altered return value from API - useful for debugging"""
        r = requests.get(cls.MAIN_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()

    @classmethod
    def get_unspents(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        utxos = [
            Unspent(amount=currency_to_satoshi(utxo['amount'], 'bsv'),
                    confirmations=utxo['confirmations'],
                    txid=utxo['txid'],
                    txindex=utxo['vout'])
            for utxo in r.json()
        ]
        return sorted(utxos, key=lambda utxo: (-utxo.confirmations, utxo.amount))

    @classmethod
    def send_transaction(cls, rawtx):  # pragma: no cover
        r = requests.post(
            'https://bchsvexplorer.com/api/tx/send',
            data=json.dumps({'rawtx': rawtx}),
            headers=cls.headers,
        )
        r.raise_for_status()
        return r.json()['txid']
