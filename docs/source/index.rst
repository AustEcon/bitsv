Bitcash: BitcoinCash made easy.
=======================

Version |version|.

.. image:: https://img.shields.io/pypi/v/bitcash.svg?style=flat-square
    :target: https://pypi.org/project/bitcash

.. image:: https://img.shields.io/travis/ofek/bitcash.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/ofek/bitcash

.. image:: https://img.shields.io/codecov/c/github/ofek/bitcash.svg?style=flat-square
    :target: https://codecov.io/gh/ofek/bitcash

.. image:: https://img.shields.io/pypi/pyversions/bitcash.svg?style=flat-square
    :target: https://pypi.org/project/bitcash

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

-----

Bitcash is Python's `fastest <https://ofek.github.io/bitcash/guide/intro.html#why-bitcash>`_
BitcoinCash library and was designed from the beginning to feel intuitive, be
effortless to use, and have readable source code. It is heavily inspired by
`Requests <https://github.com/kennethreitz/requests>`_ and
`Keras <https://github.com/fchollet/keras>`_.

**Bitcash is so easy to use, in fact, you can do this:**

.. code-block:: python

    >>> from bitcash import Key
    >>>
    >>> my_key = Key(...)
    >>> my_key.get_balance('usd')
    '12.51'
    >>>
    >>> # Let's donate!
    >>> outputs = [
    >>>     # Wikileaks
    >>>     ('1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v', 0.0035, 'bsv'),
    >>>     # Internet Archive
    >>>     ('1Archive1n2C579dMsAu3iC6tWzuQJz8dN', 190, 'jpy'),
    >>>     # The Pirate Bay
    >>>     ('129TQVAroeehD9fZpzK51NdZGQT4TqifbG', 3, 'eur'),
    >>>     # xkcd
    >>>     ('14Tr4HaKkKuC1Lmpr2YMAuYVZRWqAdRTcr', 2.5, 'cad')
    >>> ]
    >>>
    >>> my_key.send(outputs)
    '9f59f5c6757ec46fdc7440acbeb3920e614c8d1d247ac174eb6781b832710c1c'

Here is the transaction `<https://blockchain.info/tx/9f59f5c6757ec46fdc7440acbeb3920e614c8d1d247ac174eb6781b832710c1c>`_.

Features
--------

- Python's fastest available implementation (100x faster than closest library)
- Seamless integration with existing server setups
- Supports keys in cold storage
- Fully supports 25 different currencies
- First class support for storing data in the blockchain
- Deterministic signatures via RFC 6979
- Access to the blockchain (and testnet chain) through multiple APIs for redundancy
- Exchange rate API, with optional caching
- Optimal transaction fee API, with optional caching
- Compressed public keys by default
- Multiple representations of private keys; WIF, PEM, DER, etc.
- Standard P2PKH transactions

If you are intrigued, continue reading. If not, continue all the same!

User Guide
----------

This section will tell you a little about the project, show how to install it,
and will then walk you through how to use Bitcash with many examples and explanations
of best practices.

.. toctree::
    :maxdepth: 2

    guide/intro
    guide/install
    guide/keys
    guide/network
    guide/transactions
    guide/rates
    guide/fees
    guide/advanced

Community
---------

Here you will find everything you need to know about the development of Bitcash
and the community surrounding it.

.. toctree::
    :maxdepth: 1

    community/faq
    community/support
    community/development
    community/contributing
    community/vulnerabilities
    community/updates
    community/authors

Dev Guide
---------

Up ahead is Bitcash's API and a few notes about design decisions. Beware the
pedantry, or lack thereof.

.. toctree::
    :maxdepth: 2

    dev/api

Well done! There will be more soon, but right now you have nothing left to see.
Remember, `a watched pot never boils <https://www.youtube.com/watch?v=EPr-JrW-a8o>`_.
