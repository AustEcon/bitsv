BitSV: Bitcoin made easy.
===============================


.. image:: https://img.shields.io/pypi/v/bitsv.svg?style=flat-square
    :target: https://pypi.org/project/bitsv

.. image:: https://img.shields.io/travis/AustEcon/bitsv.svg?branch=master&style=flat-square
    :target: https://travis-ci.org/AustEcon/bitsv

.. image:: https://img.shields.io/pypi/pyversions/bitsv.svg?style=flat-square
    :target: https://pypi.org/project/bitsv

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

-----

BitSV is Python's `fastest <https://austecon.github.io/bitsv/guide/intro.html>`_
Bitcoin SV library and was designed from the beginning to feel intuitive, be
effortless to use, and have readable source code. It is heavily inspired by
`Requests <https://github.com/kennethreitz/requests>`_ and
`Keras <https://github.com/fchollet/keras>`_.

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

Features
--------

- Python's fastest available implementation (100x faster than closest library)
- 100kb OP_RETURN transactions made very simple
- Fully supports 21 different currencies via BitcoinSVRates_ API
- First class support for storing data in the blockchain
- Compressed public keys by default
- Multiple representations of private keys; WIF, PEM, DER, etc.
- Standard P2PKH transactions

.. _BitcoinSVRates : http://bitcoinsv-rates.com/api/rates/

Extension libraries
-------------------
- polyglot_ for posting html, audio, images, video directly to the blockchain and much more to come...
- bsvbip32_ for hierarchical deterministic key support (as per BIP32 spec)

User Guide
----------

This section will tell you a little about the project, show how to install it,
and will then walk you through how to use BitSV with many examples and explanations
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
    guide/op_return
    guide/advanced

Community
---------

Here you will find everything you need to know about the development of BitSV
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

Up ahead is BitSV's API and a few notes about design decisions. Beware the
pedantry, or lack thereof.

.. toctree::
    :maxdepth: 2

    dev/api

Well done! There will be more soon, but right now you have nothing left to see.
Remember, `a watched pot never boils <https://www.youtube.com/watch?v=EPr-JrW-a8o>`_.

.. _polyglot : https://austecon.github.io/polyglot/
.. _bsvbip32 : https://github.com/AustEcon/bsvbip32
