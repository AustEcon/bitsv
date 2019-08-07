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


class BchSVExplorerDotComAPI:
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

        tx = Transaction(response['txid'],
                         (Decimal(response['valueIn']) * BSV_TO_SAT_MULTIPLIER).normalize(),
                         (Decimal(response['valueOut']) * BSV_TO_SAT_MULTIPLIER).normalize())

        for txin in response['vin']:
            part = TxInput(txin['addr'], txin['valueSat'])
            tx.add_input(part)

        for txout in response['vout']:
            addr = None
            if 'addresses' in txout['scriptPubKey'] and txout['scriptPubKey']['addresses'] is not None:
                addr = txout['scriptPubKey']['addresses'][0]

            part = TxOutput(addr,
                          (Decimal(txout['value']) * BSV_TO_SAT_MULTIPLIER).normalize(),
                          txout['scriptPubKey']['asm'])
            tx.add_output(part)

        return tx

    @classmethod
    def get_unspents(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'bsv'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def send_transaction(cls, rawtx):  # pragma: no cover
        r = requests.post(
            'https://bchsvexplorer.com/api/tx/send',
            data=json.dumps({'rawtx': rawtx}),
            headers=cls.headers,
        )
        r.raise_for_status()
        return r.json()['txid']
