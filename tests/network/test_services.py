import pytest

import bitsv
from bitsv.network.services import NetworkAPI
from bitsv.network.services.network import set_service_timeout
from tests.utils import (
    catch_errors_raise_warnings, decorate_methods, raise_connection_error
)

MAIN_ADDRESS_USED1 = '1L2JsXHPMYuAa9ugvHGLwkdstCPUDemNCf'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_USED3 = 'mpnrLMH4m4e6dS8Go84P1r2hWwTiFTXmtW'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'


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
