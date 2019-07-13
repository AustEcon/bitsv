BitSV: Bitcoin SV made easy.
============================

Forked from Ofek's awesome Bit library: https://github.com/ofek/bit

.. image:: https://img.shields.io/pypi/v/bitsv.svg?style=flat-square
    :target: https://pypi.org/project/bitsv

.. image:: https://img.shields.io/travis/AustEcon/bitsv.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/AustEcon/bitsv

.. image:: https://img.shields.io/codecov/c/github/AustEcon/bitsv.svg?style=flat-square
    :target: https://codecov.io/gh/austecon/bitsv

.. image:: https://img.shields.io/pypi/pyversions/bitsv.svg?style=flat-square
    :target: https://pypi.org/project/bitsv

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License


Noticeboard:
------------

Legacy Addresses:

- Bitcoin SV will be reinstating legacy address format as the default standard
  (see: https://bitcoinsv.io/2019/07/12/bitcoin-sv-node-v0-2-1-released/).
  However, "cashaddress" is a great tool for conversions if needed. https://github.com/oskyk/cashaddress/

Default Fee = 1 sat/byte:

- The capacity of the Bitcoin SV network is such that 1 sat/byte virtually guarantees that
  your transaction will be included in the next block. This is therefore the default. However, it is
  trivial to specify a higher transaction fee by including this as an additional parameter to any
  of the transaction related functions.

Planned improvements
--------------------

- Improved coverage of testing modules (currently at 84%).
- Support for use of a local bitcoin full node instead of a Web-API.
  (paves the way for a RegTest environment for a rapid development cycle)
- Documentation.

----------------------------

Examples
--------

**BitSV is so easy to use:**

1. Simple payment:

.. code-block:: python

    >>> import bitsv
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')  # Defaults to "main" network
    >>> my_key.get_balance()
    10000000  # satoshis
    >>> # Can include a long list of tuples as outputs
    >>> outputs = [
    >>>     # Donate to AustEcon! (Currency conversion via api)
    >>>     ('1PdvVPTzXmo4cSs68HctLUxAdW917UZtC8', 0.10, 'usd'),  # $USD 0.10 as bsv
    >>>     ('1PdvVPTzXmo4cSs68HctLUxAdW917UZtC8', 0.0001, 'bsv')
    >>> ]
    >>> my_key.send(outputs)
    'dec895d1aa0e820984c5748984ba36854163ec3d6847c94e82a921765c5b23e1'

Here's the transaction `<https://whatsonchain.com/tx/dec895d1aa0e820984c5748984ba36854163ec3d6847c94e82a921765c5b23e1>`_.

2. OP_RETURN - 100kb size limit now supported:

.. code-block:: python

    >>> # One example usecase for OP_RETURN metadata (3 lines of code)
    >>> import bitsv
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> # input a list of tuples (data, encoding) pairs ("utf-8" or "hex" encoding)
    >>> # each tuple in the list is a pushdata element within the OP_RETURN.
    >>> list_of_pushdata = ([bytes.fromhex('6d01'),  # encode hex to bytes
                             'New_Name'.encode('utf-8')])  # encode string to utf-8 encoded bytes
    >>> # This sets memo.sv name (linked to this bitcoin address) to "New_Name"
    >>> # (as per https://memo.sv/protocol)
    >>> my_key.send_op_return(list_of_pushdata)  # default fee = 1 sat/byte

Features
--------

- Python's fastest available implementation (100x faster than closest library)
- 100kb OP_RETURN transactions made very simple
- Fully supports 21 different currencies via exchange rate API
- First class support for storing data in the blockchain
- Compressed public keys by default
- Multiple representations of private keys; WIF, PEM, DER, etc.
- Standard P2PKH transactions

Installation
------------

BitSV is distributed on `PyPI` as a universal wheel and is available on Linux/macOS
and Windows and supports Python 3.5+ and PyPy3.5-v5.7.1+. ``pip`` >= 8.1.2 is required.

.. code-block:: bash

    $ pip install bitsv  # pip3 if pip is Python 2 on your system.

Documentation
-------------
Docs are hosted by Github Pages and are automatically built and published by Travis after every successful commit to BitSV's master branch.


Credits
-------

- `ofek`_ for the original bit codebase.
- `teran-mckinney`_ for his work on the bitcash fork
- `joshua smith`_ for adding BitIndex3

.. _ofek: https://github.com/ofek/bit
.. _teran-mckinney: https://github.com/sporestack/bitcash
.. _joshua Smith: https://github.com/joshua-s

Donate
--------

- If you have found this library useful, please consider donating. It really helps.
- HandCash: $AustEcon
- 1PdvVPTzXmo4cSs68HctLUxAdW917UZtC8
