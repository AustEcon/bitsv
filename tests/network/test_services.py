import pytest

import bitsv
from bitsv.network.services import NetworkAPI
from bitsv.network.services.network import set_service_timeout
from tests.utils import raise_connection_error

MAIN_ADDRESS_USED1 = '1L2JsXHPMYuAa9ugvHGLwkdstCPUDemNCf'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_USED3 = 'mpnrLMH4m4e6dS8Go84P1r2hWwTiFTXmtW'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'
TEST_TX = '9a987f7fec77c84e743e7bd4cbcb410e1f37dd600df78137b0d07629520161b3'

INVOKE_COUNTER = 0

def all_items_common(seq):
    initial_set = set(seq[0])
    intersection_lengths = [len(set(s) & initial_set) for s in seq]
    return all_items_equal(intersection_lengths)


def all_items_equal(seq):
    initial_item = seq[0]
    return all(item == initial_item for item in seq if item is not None)


def test_set_service_timeout():
    original = bitsv.network.services.network.DEFAULT_TIMEOUT
    set_service_timeout(3)
    updated = bitsv.network.services.network.DEFAULT_TIMEOUT

    assert original != updated
    assert updated == 3

    set_service_timeout(original)


def mock_get_balance(value):
    return ""


def mock_retry_get_transaction(value):
    """ It will success every 3 invokes.
    The return status order is: Exception, Exception, Success, Exception, ...
    """
    global INVOKE_COUNTER
    INVOKE_COUNTER = INVOKE_COUNTER + 1
    if INVOKE_COUNTER % 3 == 0:
        return ""
    else:
        raise_connection_error()


network_api_main = NetworkAPI('main')
network_api_test = NetworkAPI('test')
network_api_stn = NetworkAPI('stn')

mock_network_api_main = NetworkAPI('main')
mock_network_api_main.GET_BALANCE = [raise_connection_error]
mock_network_api_main.GET_TRANSACTIONS = [raise_connection_error]
mock_network_api_main.GET_TRANSACTION = [raise_connection_error]
mock_network_api_main.GET_UNSPENTS = [raise_connection_error]
mock_network_api_main.BROADCAST_TX = [raise_connection_error]

mock_network_api_test = NetworkAPI('test')
mock_network_api_test.GET_BALANCE = [raise_connection_error]
mock_network_api_test.GET_TRANSACTIONS = [raise_connection_error]
mock_network_api_test.GET_TRANSACTION = [raise_connection_error]
mock_network_api_test.GET_UNSPENTS = [raise_connection_error]
mock_network_api_test.BROADCAST_TX = [raise_connection_error]

mock_network_api_stn = NetworkAPI('stn')
mock_network_api_stn.GET_BALANCE = [raise_connection_error]
mock_network_api_stn.GET_TRANSACTIONS = [raise_connection_error]
mock_network_api_stn.GET_TRANSACTION = [raise_connection_error]
mock_network_api_stn.GET_UNSPENTS = [raise_connection_error]
mock_network_api_stn.BROADCAST_TX = [raise_connection_error]


class TestNetworkAPI:
    # Main
    def test_get_balance_main_equal(self):
        results = [call(MAIN_ADDRESS_USED2) for call in network_api_main.GET_BALANCE]
        assert all(result == results[0] for result in results)

    def test_get_balance_main_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_main.get_balance(MAIN_ADDRESS_USED1)

    def test_get_transactions_main_equal(self):
        results = [call(MAIN_ADDRESS_USED1) for call in network_api_main.GET_TRANSACTIONS]
        assert all_items_common(results[:100])

    def test_get_transactions_main_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_main.get_transactions(MAIN_ADDRESS_USED1)

    def test_get_unspents_main_equal(self):
        results = [call(MAIN_ADDRESS_USED2) for call in network_api_main.GET_UNSPENTS]
        assert all_items_equal(results)

    def test_get_unspents_main_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_main.get_unspents(MAIN_ADDRESS_USED1)

    # Test
    def test_get_balance_test_equal(self):
        results = [call(TEST_ADDRESS_USED2) for call in network_api_test.GET_BALANCE]
        assert all(result == results[0] for result in results)

    def test_get_balance_test_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_test.get_balance(TEST_ADDRESS_USED2)

    def test_get_transactions_test_equal(self):
        results = [call(TEST_ADDRESS_USED2)[:100] for call in network_api_test.GET_TRANSACTIONS]
        assert all_items_common(results)

    def test_get_transactions_test_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_test.get_transactions(TEST_ADDRESS_USED2)

    def test_get_unspents_test_equal(self):
        results = [call(TEST_ADDRESS_USED3) for call in network_api_test.GET_UNSPENTS]
        assert all_items_equal(results)

    def test_get_unspents_test_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_test.get_unspents(TEST_ADDRESS_USED2)

    # STN
    def test_get_balance_stn_equal(self):
        results = [call(TEST_ADDRESS_USED2) for call in network_api_stn.GET_BALANCE]
        assert all(result == results[0] for result in results)

    def test_get_balance_stn_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_stn.get_balance(TEST_ADDRESS_USED2)

    def test_get_transactions_stn_equal(self):
        results = [call(TEST_ADDRESS_USED2)[:100] for call in network_api_stn.GET_TRANSACTIONS]
        assert all_items_common(results)

    def test_get_transactions_stn_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_stn.get_transactions(TEST_ADDRESS_USED2)

    def test_get_unspents_stn_equal(self):
        results = [call(TEST_ADDRESS_USED3) for call in network_api_stn.GET_UNSPENTS]
        assert all_items_equal(results)

    def test_get_unspents_stn_failure(self):
        with pytest.raises(ConnectionError):
            mock_network_api_stn.get_unspents(TEST_ADDRESS_USED2)

    # Retry
    def test_switch_serivce(self):
        """ The invoke finally success after switch service. """
        network = NetworkAPI("main")
        network.GET_BALANCE = [raise_connection_error, mock_get_balance]
        assert "" == network.get_balance(TEST_ADDRESS_USED2)

    def test_retry_service(self):
        """ The invoke finally success after retry. """
        network = NetworkAPI("main")
        network.GET_TRANSACTION = [mock_retry_get_transaction]
        assert "" == network.get_transaction(TEST_TX)

