BitSV: Bitcoin SV made easy
============================

Forked from Ofek's awesome Bit library: https://github.com/ofek/bit

.. image:: https://img.shields.io/pypi/v/bitcash.svg?style=flat-square
    :target: https://pypi.org/project/bitcash

.. image:: https://img.shields.io/travis/sporestack/bitcash.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/sporestack/bitcash

.. image:: https://img.shields.io/codecov/c/github/sporestack/bitcash.svg?style=flat-square
    :target: https://codecov.io/gh/sporestack/bitcash

.. image:: https://img.shields.io/pypi/pyversions/bitcash.svg?style=flat-square
    :target: https://pypi.org/project/bitcash

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License


Note: Legacy Addresses
----------------------

Bitcoin SV will be reinstating legacy address format as the default standard for ease of use. However,
"cashaddress" is a great tool for conversions if needed. https://github.com/oskyk/cashaddress/


Note: Default Fee = 1 sat/byte
------------------------------
The capacity of the Bitcoin SV network is such that 1 sat/byte virtually guarantees that
your transaction will be included in the next block. This is therefore the default. However, it is
trivial to specify a higher transaction fee by including this as an additional parameter to any
of the transaction related functions.


What needs fixing
-----------------

- Testing modules / coverage
- Testnet api
- Documentation page and examples

----------------------------

Examples
--------

**BitSV is so easy to use:**

1. Simple payment:

.. code-block:: python

    >>> import bitsv
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> my_key.get_balance()
    10000000  # satoshis
    >>> # Can include a long list of tuples as outputs
    >>> outputs = [
    >>>     # Donate to AustEcon! (Currency conversion via api)
    >>>     ('1PdvVPTzXmo4cSs68HctLUxAdW917UZtC8', 0.10, 'usd')  # $USD 0.10 as bsv
    >>>     ('1PdvVPTzXmo4cSs68HctLUxAdW917UZtC8', 0.0001, 'bsv')
    >>> ]
    >>> my_key.send(outputs)
    'dec895d1aa0e820984c5748984ba36854163ec3d6847c94e82a921765c5b23e1'

Here's the transaction `<https://bchsvexplorer.com/tx/dec895d1aa0e820984c5748984ba36854163ec3d6847c94e82a921765c5b23e1>`_.

2. OP_RETURN - 100kb size limit now supported:

.. code-block:: python

    >>> # One example usecase for OP_RETURN metadata (3 lines of code)
    >>> import bitsv
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> # input a list of tuples (data, encoding) pairs ("utf-8" or "hex" encoding)
    >>> # each tuple in the list is a pushdata element within the OP_RETURN.
    >>> lst_of_pushdata = [('6d01', 'hex'), ('new_name', 'utf-8')]
    >>> # This sets memo.sv name (linked to this bitcoin address) to "new_name"
    >>> # (as per https://memo.sv/protocol)
    >>> my_key.send_op_return(lst_of_pushdata)  # default fee = 1 sat/byte


Features
--------

- Python's fastest available implementation (100x faster than closest library)
- 100kb OP_RETURN transactions made very simple
- Seamless integration with existing server setups
- Supports keys in cold storage
- Fully supports 21 different currencies via exchange rate API
- First class support for storing data in the blockchain
- Optimal transaction fee API
- Compressed public keys by default
- Multiple representations of private keys; WIF, PEM, DER, etc.
- Standard P2PKH transactions

Installation
------------

BitSV is distributed on `PyPI` as a universal wheel and is available on Linux/macOS
and Windows and supports Python 3.5+ and PyPy3.5-v5.7.1+. ``pip`` >= 8.1.2 is required.

.. code-block:: bash

    $ pip install bitsv  # pip3 if pip is Python 2 on your system.


Credits
-------

- `ofek`_ for the original bit codebase.
- `teran-mckinney`_ for his work on the bitcash fork
- `bjarnemagnussen`_ for his segwit code for the necessary BIP-143 support.

.. _ofek: https://github.com/ofek/bit
.. _teran-mckinney: https://github.com/sporestack/bitcash
.. _bjarnemagnussen: https://github.com/bjarnemagnussen/bitcash/tree/segwit

Donate
--------

- If you have found this library useful, please consider donating. It really helps.
- HandCash: $AustEcon
- 1HvuVG6TJ3uVyNHpWuDD59mFT9j23cabXj
