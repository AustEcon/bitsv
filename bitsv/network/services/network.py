from functools import wraps

import requests
import time
import collections
from .bitindex3 import BitIndex3

DEFAULT_TIMEOUT = 30
BSV_TO_SAT_MULTIPLIER = 100000000
DEFAULT_RETRY = 3
IGNORED_ERRORS = (ConnectionError,
                  requests.exceptions.ConnectionError,
                  requests.exceptions.Timeout,
                  requests.exceptions.ReadTimeout,
                  requests.HTTPError)


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


def set_service_retry(retry):
    global DEFAULT_RETRY
    DEFAULT_RETRY = retry


def retry_annotation(exception_to_check, tries=3, delay=1, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff,
    the default delay sequence is 1s, 2s, 4s, 8s...
    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry
    :param exception_to_check: the exception object to check. may be a tuple of exceptions to check
    :type exception_to_check: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    msg = "{}, Retrying in {} seconds...".format(str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


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

    @retry_annotation(IGNORED_ERRORS, tries=DEFAULT_RETRY)
    def retry_wrapper_call(self, api_call, param):
        return api_call(param)

    def invoke_api_call(self, call_list, param):
        """Tries to invoke all api, raise exception if all fail."""
        for api_call in call_list:
            try:
                return self.retry_wrapper_call(api_call, param)
            except IGNORED_ERRORS as e:
                if call_list[-1] == api_call:   # All api iterated.
                    raise ConnectionError('All APIs are unreachable, exception:' + str(e))

    def get_balance(self, address):
        """Gets the balance of an address in satoshis.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """
        return self.invoke_api_call(self.GET_BALANCE, address)

    def get_transactions(self, address):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """
        return self.invoke_api_call(self.GET_TRANSACTIONS, address)

    def get_transaction(self, txid):
        """Gets the full transaction details.

        :param txid: The transaction id in question.
        :type txid: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``Transaction``
        """
        return self.invoke_api_call(self.GET_TRANSACTION, txid)

    def get_unspents(self, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bitsv.network.meta.Unspent`
        """
        return self.invoke_api_call(self.GET_UNSPENTS, address)

    def broadcast_tx(self, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        self.invoke_api_call(self.BROADCAST_TX, tx_hex)
        return
