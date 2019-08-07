import requests
from decimal import Decimal

from bitsv.network import currency_to_satoshi
from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxInput, TxOutput
from bitsv.constants import BSV

DEFAULT_TIMEOUT = 30
BSV_TO_SAT_MULTIPLIER = BSV

# This module is no longer actually used by anything but I don't mind keeping it here for the moment


class InsightAPI:
    """
    Generic Insight API template
    """
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_BALANCE_API = ''
    MAIN_UNSPENT_API = ''
    MAIN_TX_PUSH_API = ''
    MAIN_TX_API = ''
    MAIN_TX_AMOUNT_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['transactions']

    @classmethod
    def get_transaction(cls, txid):
        r = requests.get(cls.MAIN_TX_API.format(txid), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json(parse_float=Decimal)

        tx = Transaction(response['txid'],
                         response['blockheight'],
                         (Decimal(response['valueIn']) * BSV_TO_SAT_MULTIPLIER).normalize(),
                         (Decimal(response['valueOut']) * BSV_TO_SAT_MULTIPLIER).normalize(),
                         (Decimal(response['fees']) * BSV_TO_SAT_MULTIPLIER).normalize())

        for txin in response['vin']:
            part = TxInput(txin['addr'], txin['valueSat'], txin['scriptSig']['asm'])
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
    def get_tx_amount(cls, txid, txindex):
        r = requests.get(cls.MAIN_TX_AMOUNT_API.format(txid), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        response = r.json(parse_float=Decimal)
        return (Decimal(response['vout'][txindex]['value']) * BSV_TO_SAT_MULTIPLIER).normalize()

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'bsv'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, json={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False
