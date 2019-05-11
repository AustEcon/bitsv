import requests
import collections
from .bitindex3 import BitIndex3

DEFAULT_TIMEOUT = 30
BSV_TO_SAT_MULTIPLIER = 100000000


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class BitIndex3Normalized(BitIndex3):

    def __init__(self, api_key=None, network="main"):
        self.api_key = api_key
        self.network = network
        self.headers = self._get_headers()
        self.authorized_headers = self._get_authorized_headers()

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _get_authorized_headers(self):
        headers = self._get_headers()
        headers['api_key'] = self.api_key
        return headers

    def get_transactions(self, address):
        # override "get_transactions" namespace to return a list of txids only to keep all apis the same
        return self.get_balance(address)['transactions']

    def get_unspents(self, address, sort=None):
        # rename to "get_unspents" to keep all apis the same name
        return self.get_utxos(address, sort=sort)


class NetworkAPI:
    """
    A Class for handling network API redundancy.

    :param network: 'main', 'test' or 'stn' --> feeds into the bitsv.network.NetworkAPI class for redundancy
    :type network: ``str``
    """

    def __init__(self, network):

        self.network = network

        # Instantiate Normalized apis
        self.bitindex3 = BitIndex3Normalized(api_key=None, network=self.network)
        #Example: self.whatsonchain = WhatsonchainNormalized(network=network) - https://developers.whatsonchain.com/
        #Example: self.blockchair = BlockchairNormalized(network=network) - https://github.com/Blockchair/Blockchair.Support

        # Allows extra apis for 'main' that may not support testnet (e.g. blockchair)
        if network == 'main':
            self.list_of_apis = collections.deque([self.bitindex3])
        elif network == 'test':
            self.list_of_apis = collections.deque([self.bitindex3])
        elif network == 'stn':
            self.list_of_apis = collections.deque([self.bitindex3])
        else:
            raise ValueError("network must be either 'main', 'test' or 'stn'")

        self.GET_BALANCE = [api.get_balance for api in self.list_of_apis]
        self.GET_TRANSACTIONS = [api.get_transactions for api in self.list_of_apis]
        self.GET_TRANSACTION = [api.get_transaction for api in self.list_of_apis]
        self.GET_UNSPENTS = [api.get_unspents for api in self.list_of_apis]
        self.BROADCAST_TX = [api.send_transaction for api in self.list_of_apis]

        self.IGNORED_ERRORS = (ConnectionError,
                               requests.exceptions.ConnectionError,
                               requests.exceptions.Timeout,
                               requests.exceptions.ReadTimeout)

    def get_balance(self, address):
        """Gets the balance of an address in satoshis.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in self.GET_BALANCE:
            try:
                return api_call(address)
            except self.IGNORED_ERRORS:
                self.list_of_apis.rotate(-1)  # failed api --> back of the que for next time (across all api calls)

        raise ConnectionError('All APIs are unreachable.')

    def get_transactions(self, address):
        """Gets the ID of all transactions related to an address.

        :param from_index: First index from transactions list to start collecting from
        :param to_index: Final index to finish collecting transactions from
        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in self.GET_TRANSACTIONS:
            try:
                return api_call(address)
            except self.IGNORED_ERRORS:
                self.list_of_apis.rotate(-1)  # failed api --> back of the que for next time (across all api calls)

        raise ConnectionError('All APIs are unreachable.')

    def get_transaction(self, txid):
        """Gets the full transaction details.

        :param txid: The transaction id in question.
        :type txid: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``Transaction``
        """

        for api_call in self.GET_TRANSACTION:
            try:
                return api_call(txid)
            except self.IGNORED_ERRORS:
                self.list_of_apis.rotate(-1)  # failed api --> back of the que for next time (across all api calls)

        raise ConnectionError('All APIs are unreachable.')

    def get_unspents(self, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :param address: Address to get utxos for
        :param sort: 'value:desc' or 'value:asc' to sort unspents by descending/ascending order respectively
        :rtype: ``list`` of :class:`~bitsv.network.meta.Unspent`
        """

        for api_call in self.GET_UNSPENTS:
            try:
                return api_call(address)
            except self.IGNORED_ERRORS:
                self.list_of_apis.rotate(-1)  # failed api --> back of the que for next time (across all api calls)

        raise ConnectionError('All APIs are unreachable.')

    def broadcast_tx(self, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        success = None

        for api_call in self.BROADCAST_TX:
            try:
                success = api_call(tx_hex)
                if not success:
                    continue
                return
            except self.IGNORED_ERRORS:
                self.list_of_apis.rotate(-1)  # failed api --> back of the que for next time (across all api calls)

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
