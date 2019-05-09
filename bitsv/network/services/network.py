import requests

from .bitindex3 import BitIndex3

BSV_TO_SAT_MULTIPLIER = 100000000
DEFAULT_TIMEOUT = 30
DEFAULT_APIS = {
    'BitIndex3': None,
    #'Whatsonchain': None
}


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class NetworkAPI:
    """
    A Class for handling network API redundancy.

    :param apis: A dictionary of {api_name : api_keys} in order of preference for redundancy. (Python 3.6 dicts ordered)
    :type apis: ``dict`` of ``str`` : ``str``
    :param network: 'main', 'test' or 'stn' --> feeds into the bitsv.network.NetworkAPI class for redundancy
    :type network: ``str``
    """

    IGNORED_ERRORS = (ConnectionError,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout,
                      requests.exceptions.ReadTimeout)

    def __init__(self, apis, network):

        if not apis:
            apis = DEFAULT_APIS
        self.apis = apis
        self.network = network
        self.bitindex3 = BitIndex3(apis['BitIndex3'], network=self.network)
        #self.whatsonchain = Whatsonchain(apis['Whatsonchain'], network=network)  # api not built yet on server side...

        self.GET_BALANCE = [self.bitindex3.get_balance]
        self.GET_TRANSACTIONS = [self.bitindex3.get_transactions]
        self.GET_TRANSACTION = [self.bitindex3.get_transaction]
        self.GET_UNSPENTS = [self.bitindex3.get_utxos]
        self.BROADCAST_TX = [self.bitindex3.send_transaction]

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
                pass

        raise ConnectionError('All APIs are unreachable.')

    def get_transactions(self, address, from_index=0, to_index=0):
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
                return api_call(address, from_index=from_index, to_index=to_index)
            except self.IGNORED_ERRORS:
                pass

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
                pass

        raise ConnectionError('All APIs are unreachable.')

    def get_unspents(self, address, sort=None):
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
                return api_call(address, sort)
            except self.IGNORED_ERRORS:
                pass

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
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
