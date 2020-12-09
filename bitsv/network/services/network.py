import os
from functools import wraps

import requests
import time
import collections
import logging

from .whatsonchain import WhatsonchainNormalised

from .mattercloud import MatterCloud, MATTERCLOUD_API_KEY_VARNAME
from .bsvbookguarda import BSVBookGuardaAPI

DEFAULT_TIMEOUT = 30
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


def retry_annotation(exception_to_check, tries=3, delay=1, backoff=2):
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
                    logging.warning(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


class NetworkAPI:
    """
    A Class for handling network API redundancy.

    :param network: 'main', 'test' or 'stn' --> feeds into the bitsv.network.NetworkAPI class for redundancy
    :type network: ``str``
    """

    def __init__(self, network):

        self.network = network

        # Instantiate Normalized apis
        self.bchsvexplorer = BSVBookGuardaAPI  # classmethods, mainnet only
        self.whatsonchain = WhatsonchainNormalised(network=self.network)

        # Allows extra apis for 'main' that may not support testnet (e.g. blockchair)
        if network == 'main':
            self.list_of_apis = collections.deque([self.whatsonchain, self.bchsvexplorer])
        elif network == 'test':
            self.list_of_apis = collections.deque([self.whatsonchain])
        elif network == 'stn':
            self.list_of_apis = collections.deque([self.whatsonchain])
        else:
            raise ValueError("network must be either 'main', 'test' or 'stn'")

        mattercloud_api_key = os.environ.get(MATTERCLOUD_API_KEY_VARNAME, None)
        if mattercloud_api_key:
            self.bitindex3 = MatterCloud(api_key=mattercloud_api_key, network=self.network)
            self.list_of_apis.appendleft(self.bitindex3)

    @retry_annotation(IGNORED_ERRORS, tries=DEFAULT_RETRY)
    def retry_wrapper_call(self, api_call, *params):
        return api_call(*params)

    def invoke_api_call(self, call_list, *params):
        """Tries to invoke all api, raise exception if all fail."""
        for api_call in call_list:
            try:
                return self.retry_wrapper_call(api_call, *params)
            except IGNORED_ERRORS as e:
                # TODO: Write a log here to notify the system has changed the default service.
                self.list_of_apis.rotate(-1)
                if call_list[-1] == api_call:   # All api iterated.
                    raise ConnectionError('All APIs are unreachable, exception:' + str(e))

    def get_balance(self, address):
        """Gets the balance of an address in satoshis.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """
        call_list = [api.get_balance for api in self.list_of_apis]
        return self.invoke_api_call(call_list, address)

    def get_transactions(self, address):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """
        call_list = [api.get_transactions for api in self.list_of_apis]
        return self.invoke_api_call(call_list, address)

    def get_transaction(self, txid):
        """Gets the full transaction details.

        :param txid: The transaction id in question.
        :type txid: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``Transaction``
        """
        call_list = [api.get_transaction for api in self.list_of_apis]
        return self.invoke_api_call(call_list, txid)

    def get_unspents(self, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bitsv.network.meta.Unspent`
        """
        call_list = [api.get_unspents for api in self.list_of_apis]
        return self.invoke_api_call(call_list, address)

    def get_bestblockhash(self):
        """Gets the hash of the tip block on the main chain.
        :raises ConnectionError: If all API services fail.
        :rtype: ``str``
        """
        call_list = [api.get_bestblockhash for api in self.list_of_apis]
        return self.invoke_api_call(call_list)

    def get_block(self, blockhash):
        """Gets the block details.

        :param blockhash: The block hash in question.
        :type blockhash: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``Block``
        """
        call_list = [api.get_block for api in self.list_of_apis]
        return self.invoke_api_call(call_list, blockhash)

    def broadcast_tx(self, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        call_list = [api.send_transaction for api in self.list_of_apis]
        tx_id = self.invoke_api_call(call_list, tx_hex)
        return tx_id
