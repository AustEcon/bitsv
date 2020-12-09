import requests
import json
from decimal import Decimal

from bitsv.network import currency_to_satoshi
from bitsv.network.meta import Unspent

# left here as a reminder to normalize get_transaction()
from bitsv.network.transaction import Transaction, TxInput, TxOutput
from bitsv.network.block import Block
from bitsv.constants import BSV

DEFAULT_TIMEOUT = 30
BSV_TO_SAT_MULTIPLIER = BSV


class BSVBookGuardaAPI:
    """
    Simple bitcoin SV REST API --> uses base58 address format (addresses start with "1")
    - get_address_info
    - get_balance
    - get_transactions
    - get_transaction
    - get_unspent
    - broadcast_tx
    """
    MAIN_ENDPOINT = 'https://bsvbook.guarda.co/'
    MAIN_STATUS_API = MAIN_ENDPOINT + 'api'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'api/v2/address/{}'
    MAIN_BALANCE_API = MAIN_ADDRESS_API
    MAIN_TX_PULL_API = MAIN_ADDRESS_API + '?page={}'
    MAIN_UNSPENT_API = MAIN_ENDPOINT + 'api/v2/utxo/{}'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'api/v2/sendtx'
    MAIN_TX_API = MAIN_ENDPOINT + 'api/v2/tx/{}'
    MAIN_TX_AMOUNT_API = MAIN_TX_API
    MAIN_BLOCK_API = MAIN_ENDPOINT + 'api/v2/block/{}?page={}'

    @classmethod
    def get_address_info(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return r.json()

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()  # pragma: no cover
        return int(r.json()['balance'])

    @classmethod
    def get_transactions(cls, address):
        page = 1
        while True:
            r = requests.get(cls.MAIN_TX_PULL_API.format(address, page), timeout=DEFAULT_TIMEOUT)
            r.raise_for_status()  # pragma: no cover
            response = r.json(parse_float=Decimal)
            for txid in response['txids']:
                yield txid
            if page == response['totalPages']:
                break
            page += 1

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
            tx_output = TxOutput(scriptpubkey=vout['hex'], amount=vout['value'])
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
            Unspent(amount=currency_to_satoshi(utxo['value'], 'satoshi'),
                    confirmations=utxo['confirmations'],
                    txid=utxo['txid'],
                    txindex=utxo['vout'])
            for utxo in r.json()
        ]
        return sorted(utxos, key=lambda utxo: (-utxo.confirmations, utxo.amount))

    @classmethod
    def send_transaction(cls, rawtx):  # pragma: no cover
        r = requests.post(
            MAIN_TX_PUSH_API,
            data=rawx
        )
        r.raise_for_status()
        response = r.json()
        if 'error' in response:
            raise ValueError(response['error']['message'])
        return response['result']

    @classmethod
    def get_bestblockhash(cls):
        r = requests.get(cls.MAIN_STATUS_API)
        r.raise_for_status()
        response = r.json()
        return response['backend']['bestBlockHash']

    @classmethod
    def get_block(cls, hash: str):
        txids = []
        page = 1
        while True:
            r = requests.get(cls.MAIN_BLOCK_API.format(hash, page))
            r.raise_for_status()
            response = r.json()
            txids.extend((tx["txid"] for tx in response["txs"]))
            if page == response["totalPages"]:
                break
        return Block(response['hash'], response['height'], response['previousBlockHash'], response['nextBlockHash'], txids)
