import json

import requests
from cashaddress import convert as cashaddress
from decimal import Decimal

from bitsv.network import currency_to_satoshi
from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxPart

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
    def get_utxo(address):
        """gets utxos for given address BitIndex api"""
        address = cashaddress.to_legacy_address(address)
        json_payload = json.dumps({"addrs": address})

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post('https://api.bitindex.network/api/addrs/utxo', data=json_payload, headers=headers)
        return [Unspent(amount = currency_to_satoshi(tx['amount'], 'bsv'),
             script = tx['scriptPubKey'],
             txid = tx['txid'],
             txindex = tx['vout']) for tx in r.json()]

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


class BchSVExplorerDotComAPI(InsightAPI):
    """
    Simple bitcoin SV REST API --> uses Legacy address format
    - get_balance
    - get_transactions
    - get_unspent
    Testnet untested
    """
    MAIN_ENDPOINT = 'https://bchsvexplorer.com/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'api/addr/{}'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + '/balance'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '/utxo'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + '/tx/send'
    MAIN_TX_API = MAIN_ENDPOINT + '/tx/{}'
    MAIN_TX_AMOUNT_API = MAIN_TX_API
    TX_PUSH_PARAM = 'create_rawtx'

    @classmethod
    def get_address_info(cls, address):
        address = cashaddress.to_legacy_address(address)
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_balance(cls, address):
        address = cashaddress.to_legacy_address(address)
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        address = cashaddress.to_legacy_address(address)
        r = requests.get(cls.MAIN_ADDRESS_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['transactions']

    @classmethod
    def get_unspent(cls, address):
        address = cashaddress.to_legacy_address(address)
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


class NetworkAPI:
    IGNORED_ERRORS = (ConnectionError,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout,
                      requests.exceptions.ReadTimeout)

    # Version 5.4 - BitIndex for balance, broadcast and utxos (keeps these critical functions in sync with one another)
    GET_BALANCE_MAIN = [BitIndex.get_balance]
    GET_TRANSACTIONS_MAIN = [BchSVExplorerDotComAPI.get_transactions]
    GET_UNSPENT_MAIN = [BitIndex.get_utxo]
    BROADCAST_TX_MAIN = [BitIndex.broadcast_rawtx]
    GET_TX_MAIN = [BchSVExplorerDotComAPI.get_transaction]
    GET_TX_AMOUNT_MAIN = [BchSVExplorerDotComAPI.get_tx_amount]

    # Version 5.3
    '''
    GET_BALANCE_MAIN = [BchSVExplorerDotComAPI.get_balance]
    GET_TRANSACTIONS_MAIN = [BchSVExplorerDotComAPI.get_transactions]
    GET_UNSPENT_MAIN = [BchSVExplorerDotComAPI.get_unspent]
    BROADCAST_TX_MAIN = [BchSVExplorerDotComAPI.broadcast_tx]
    GET_TX_MAIN = [BchSVExplorerDotComAPI.get_transaction]
    GET_TX_AMOUNT_MAIN = [BchSVExplorerDotComAPI.get_tx_amount]
    '''

    '''
    GET_BALANCE_TEST = [BchSVExplorerDotComAPI.get_balance_testnet]
    GET_TRANSACTIONS_TEST = [BchSVExplorerDotComAPI.get_transactions_testnet]
    GET_UNSPENT_TEST = [BchSVExplorerDotComAPI.get_unspent_testnet]
    BROADCAST_TX_TEST = [BchSVExplorerDotComAPI.broadcast_tx_testnet]
    GET_TX_TEST = [BchSVExplorerDotComAPI.get_transaction_testnet]
    GET_TX_AMOUNT_TEST = [BchSVExplorerDotComAPI.get_tx_amount_testnet]
    '''

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
