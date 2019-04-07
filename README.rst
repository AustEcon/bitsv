BitSV: Bitcoin SV made easy.
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

- A few more additions to BitIndex api
- Documentation and examples
- Make new repos (powered by bitsv) for interfacing with BitPaste api and others
- Testing modules / coverage
- Testnet api

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
    >>> lst_of_pushdata = [('6d01', 'hex'), ('new_name', 'utf-8')]
    >>> # This sets memo.sv name (linked to this bitcoin address) to "new_name"
    >>> # (as per https://memo.sv/protocol)
    >>> my_key.send_op_return(lst_of_pushdata)  # default fee = 1 sat/byte


3. Hierarchical Deterministic wallet functions (added 7/04/19):

.. code-block:: python

    >>> import bitsv
    >>> xprv = bitsv.Bip32utils.get_xprv_bip32_node("xprv9s21ZrQH143K4Un4SHjdvXpzzdQjpm7vVhQ79BMi5V58nptUo4NGqytwH68XAVj5LkDxjSqdVjdDinFCT8WqfBT7zigdtaGcrffTmBdwFH5")
    >>> # Receiving addresses
    >>> bitsv.Bip32utils.get_addresses_from_xprv(xprv, derivation_path='0', index_end=3)
    ['1PPro3nLxMB7A1BJXfZkRDHCRugj8z4d7R',
    '169YSZGMvtHvKbRHTpYCQZWx1phfJp2DCe',
    '1PhGu2V5T5g26bHi6qKg2KmxpUQLuNwyKT']
    >>> # Change addresses
    >>> bitsv.Bip32utils.get_addresses_from_xprv(xprv, derivation_path='1', index_end=3)
    ['1FUT1Yn7RcsXADpkfweiVrfkPurkFBDfuU',
    '1M126MVQst5XGGqV6gVuXxCAwTGkwwgspk',
    '1BX2BzUhuWCod14BMLYUFyMiXX2qhJbNX5']
    >>> # Receiving address private key objects (have a wif() function to return Base58 key)
    >>> bitsv.Bip32utils.get_private_keys(xprv, derivation_path='0', index_end=3)
    [private_for <xpub6AJDyEAwA8V7aVsF4dU3Kfdp9dH7W85F8iaWqgXqoeXEGWKBP3e7PeW2s76FM4krswNPkuHHUxaDPLD8aYG3CGyYU539MpHUsWCXk2W4pfV>,
     private_for <xpub6AJDyEAwA8V7ec7QFow54ssKpgtys6JY2gUzmpKQnDGvs6UoqYbpuu1a9JYxWJZ4UkWoZLAsRF2w8QA2pxDpMjyuzHDmYMTB7mpuPk5bpM5>,
     private_for <xpub6AJDyEAwA8V7ho8mZJyWFcz9kWzb8QcCSizGLsHgjKZj4eFT9LeuhUFyRXNzCzZJCPfmR2fXG9VXhHKVWJa9ZPUWK89rmjdkhTbQDUTTLfA>]
    >>> # Change address private key objects (have a wif() function to return Base58 key)
    >>> bitsv.Bip32utils.get_private_keys(xprv, derivation_path='1', index_end=3)
    [private_for <xpub6BWD9MXYKixkSVevXDmDqFbG9TxKPEaCddPVCeNYMHQtQAZrppDBZjbspf31PNoosbfqdq2Db6FS1hQcPe5RaCxH7D2M91smfXhigkMPKd2>,
     private_for <xpub6BWD9MXYKixkWH7pdjuUgkwMnQgq3Pndiynz6fP8FpgSLo7GLvYWALgvmy5eY35z95yVST455jAsKrUEF2WkGhfxX5i8WEUSEffYf1wiP13>,
     private_for <xpub6BWD9MXYKixkYkmyDGYQSkR4YdQzQqfkafw4zLCof9XYfp6pLSPrEvuNZftfHgcdxj57AzKQ7AgXMz1LDbyeTnzw3FjuCGf962TWipBydgR>]
    >>> # WIF Format keys for use in bitsv.PrivateKey() to access related functions for each respective address
    >>> bitsv.Bip32utils.get_private_keys(xprv, derivation_path='1', index_end=3, wif_format=True)
    ['L5ieGMBFteTHJTdA4ERA6eBbvojXqpbNHBqiSDAeFdXxZDnjNtkF',
     'KyGbQzXanN84fTrNrm2uvtw3qK1bHRLVMp7dT5Dnp5TcRsW6newc',
     'Kzt26jcyzQtiPjaxcTSjRCYxSg8gLV7tV3w2tuBVHejYwgpsBBxx']
    >>> # If you only have xpub key you can still generate the addresses to "view only"
    >>> # Use the BitIndex api to query the network directly for xpub total balance etc.
    >>> # xpub queries on BitIndex require an API key from https://www.bitindex.network/#get-api-key

Features
--------

- Python's fastest available implementation (100x faster than closest library)
- 100kb OP_RETURN transactions made very simple
- Hierarchical deterministic key support (thanks to pycoin)
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


Credits
-------

- `ofek`_ for the original bit codebase.
- `teran-mckinney`_ for his work on the bitcash fork
- `richardkiss`_ for his work on pycoin (for Hierarchical Deterministic wallet functions)

.. _ofek: https://github.com/ofek/bit
.. _teran-mckinney: https://github.com/sporestack/bitcash
.. _richardkiss: https://github.com/richardkiss/pycoin

Donate
--------

- If you have found this library useful, please consider donating. It really helps.
- HandCash: $AustEcon
- 1PdvVPTzXmo4cSs68HctLUxAdW917UZtC8
