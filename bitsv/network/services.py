import json

import requests
from cashaddress import convert as cashaddress
from decimal import Decimal

from bitsv.network import currency_to_satoshi
from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxPart
from bitsv.network.services.bitindex3 import (
    BitIndex3, BitIndex3MainNet, BitIndex3TestNet, BitIndex3STN
)

DEFAULT_TIMEOUT = 30

BSV_TO_SAT_MULTIPLIER = 100000000


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class BitIndex:

    @staticmethod
    def get_balance(address):
        """Gets utxos for given legacy address"""
        address = cashaddress.to_legacy_address(address)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        r = requests.get('https://api.bitindex.network/api/v2/addrs/balance?address={}'.format(address),
                         headers=headers)
        return r.json()

    @staticmethod
    def get_txs(address):
        """Gets utxos for given legacy address"""
        address = cashaddress.to_legacy_address(address)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        r = requests.get('https://api.bitindex.network/api/v2/addrs/txs?address={}'.format(address), headers=headers)
        return r.json()

    @staticmethod
    def get_tx(tx):
        """Gets utxos for given legacy address"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        r = requests.get('https://api.bitindex.network/api/v2/tx/{}'.format(tx), headers=headers)
        return r.json()

    @staticmethod
    def get_utxo(address):
        """gets utxos for given address BitIndex api"""
        address = cashaddress.to_legacy_address(address)
        json_payload = json.dumps({"addrs": address})

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post('https://api.bitindex.network/api/addrs/utxo', data=json_payload, headers=headers)
        return [Unspent(amount=currency_to_satoshi(tx['amount'], 'bsv'),
                        script=tx['scriptPubKey'],
                        txid=tx['txid'],
                        txindex=tx['vout'],
                        confirmations=tx['confirmations']) for tx in r.json()]

    @staticmethod
    def broadcast_rawtx(rawtx):
        """broadcasts a create_rawtx as hex to network via BitIndex api"""
        json_payload = json.dumps({"hex": rawtx})

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post('https://api.bitindex.network/api/v2/tx/send', data=json_payload, headers=headers)
        return r.json()

    @staticmethod
    def xpub_register(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.post('https://api.bitindex.network/api/v2/xpub/register?xpub={}'.format(xpub),
                          headers=headers)
        return r

    @staticmethod
    def get_xpub_status(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.bitindex.network/api/v2/xpub/status?xpub={}'.format(xpub),
                         headers=headers)
        return r.json()

    @staticmethod
    def get_xpub_balance(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.bitindex.network/api/v2/xpub/balance?xpub={}'.format(xpub),
                         headers=headers)
        return r.json()

    @staticmethod
    def get_xpub_utxos(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.bitindex.network/api/v2/xpub/utxos?xpub={}'.format(xpub),
                         headers=headers)
        return r.json()

    @staticmethod
    def get_xpub_tx(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.bitindex.network/api/v2/xpub/txs?xpub={}'.format(xpub),
                         headers=headers)
        return r.json()


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
            part = TxPart(txin['addr'], txin['valueSat'], txin['scriptSig']['asm'])
            tx.add_input(part)

        for txout in response['vout']:
            addr = None
            if 'addresses' in txout['scriptPubKey'] and txout['scriptPubKey']['addresses'] is not None:
                addr = txout['scriptPubKey']['addresses'][0]

            part = TxPart(addr,
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


class WhatsonchainAPI:
    """Only Testnet supported currently. STN may be added soon. Mainnet too."""

    # Whatsonchain for all testnet functions
    TESTNET = 'https://api.whatsonchain.com/v1/bsv/{}'.format('test')
    TESTNET_WOC_STATUS = TESTNET + '/woc'
    TESTNET_GET_BLOCK_BY_HASH = TESTNET + 'block/hash/{}'
    TESTNET_GET_BLOCK_BY_HEIGHT = TESTNET + '/block/height/{}'
    TESTNET_GET_BLOCK_BY_HASH_BY_PAGE = TESTNET + '/block/hash/{}/page/{}'  # Needs .format(hash,page_number)
    TESTNET_GET_TRANSACTION_BY_HASH = TESTNET + '/tx/hash/{}'
    TESTNET_POST_RAWTX = TESTNET+ '/tx/raw'  # json payload = {"txHex": "hex..."}

    @classmethod
    def get_woc_status_testnet(cls):
        """returns 'what's on chain' if online"""
        r = requests.get(cls.TESTNET_WOC_STATUS, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.text

    @classmethod
    def get_block_by_hash_testnet(cls, _hash):
        r = requests.get(cls.TESTNET_GET_BLOCK_BY_HASH.format(_hash), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_block_by_height_testnet(cls, _height):
        r = requests.get(cls.TESTNET_GET_BLOCK_BY_HEIGHT.format(_height), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_block_by_hash_by_page_testnet(cls, _hash, page_number):
        """Only to be used for large blocks > 1000 txs. Allows paging through lists of transactions.
        Returns Null if there are not more than 1000 transactions in the block"""
        r = requests.get(cls.TESTNET_GET_BLOCK_BY_HASH_BY_PAGE.format(_hash, page_number), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transaction_by_hash_testnet(cls, _hash):
        r = requests.get(cls.TESTNET_GET_TRANSACTION_BY_HASH.format(_hash), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def broadcast_rawtx_testnet(cls, rawtx):
        # FIXME not actually tested yet
        """Broadcasts a rawtx to testnet"""
        json_payload = json.dumps({"txHex": rawtx})
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post(cls.TESTNET_POST_RAWTX, data=json_payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    # Whatsonchain STN endpoints
    STN = 'https://api.whatsonchain.com/v1/bsv/{}'.format('stn')
    STN_WOC_STATUS = STN + '/woc'
    STN_GET_BLOCK_BY_HASH = STN + 'block/hash/{}'
    STN_GET_BLOCK_BY_HEIGHT = STN + '/block/height/{}'
    STN_GET_BLOCK_BY_HASH_BY_PAGE = STN + '/block/hash/{}/page/{}'  # Needs .format(hash,page_number)
    STN_GET_TRANSACTION_BY_HASH = STN + '/tx/hash/{}'
    STN_POST_RAWTX = STN + '/tx/raw'  # json payload = {"txHex": "hex..."}

    # Whatsonchain mainnet endpoints (included here as may come in handy later)
    MAINNET = 'https://api.whatsonchain.com/v1/bsv/{}'.format('main')
    MAINNET_WOC_STATUS = MAINNET + '/woc'
    MAINNET_GET_BLOCK_BY_HASH = MAINNET + 'block/hash/{}'
    MAINNET_GET_BLOCK_BY_HEIGHT = MAINNET + '/block/height/{}'
    MAINNET_GET_BLOCK_BY_HASH_BY_PAGE = MAINNET + '/block/hash/{}/page/{}'  # Needs .format(hash,page_number)
    MAINNET_GET_TRANSACTION_BY_HASH = MAINNET + '/tx/hash/{}'
    MAINNET_POST_RAWTX = STN + '/tx/raw'  # json payload = {"txHex": "hex..."}


class NetworkAPI:
    """
    A Class for handling network API redundancy.

    FIXME network API redundancy and RegTesting / Testnet - see Issue section on github"""

    IGNORED_ERRORS = (ConnectionError,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout,
                      requests.exceptions.ReadTimeout)

    # BitIndex for all mainnet functions
    GET_BALANCE_MAIN = [BitIndex.get_balance]
    GET_TRANSACTIONS_MAIN = [BitIndex.get_txs]
    GET_UNSPENT_MAIN = [BitIndex.get_utxo]
    BROADCAST_TX_MAIN = [BitIndex.broadcast_rawtx]
    GET_TX_MAIN = [BitIndex.get_tx]

    @classmethod
    def get_balance(cls, address):
        """Gets the balance of an address in satoshis.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in cls.GET_BALANCE_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transactions(cls, address):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in cls.GET_TRANSACTIONS_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transaction(cls, txid):
        """Gets the full transaction details.

        :param txid: The transaction id in question.
        :type txid: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``Transaction``
        """

        for api_call in cls.GET_TX_MAIN:
            try:
                return api_call(txid)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_tx_amount(cls, txid, txindex):
        """Gets the amount of a given transaction output.

        :param txid: The transaction id in question.
        :type txid: ``str``
        :param txindex: The transaction index in question.
        :type txindex: ``int``
        :raises ConnectionError: If all API services fail.
        :rtype: ``Decimal``
        """

        for api_call in cls.GET_TX_AMOUNT_MAIN:
            try:
                return api_call(txid, txindex)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_unspent(cls, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bitcash.network.meta.Unspent`
        """

        for api_call in cls.GET_UNSPENT_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        success = None

        for api_call in cls.BROADCAST_TX_MAIN:
            try:
                success = api_call(tx_hex)
                if not success:
                    continue
                return
            except cls.IGNORED_ERRORS:
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
