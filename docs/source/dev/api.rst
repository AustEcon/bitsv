.. _api:

Developer Interface
===================

.. module:: bitsv

.. _keysapi:

Keys
----

.. autoclass:: bitsv.Key

.. autoclass:: bitsv.PrivateKey
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bitsv.PrivateKeyTestnet
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bitsv.wallet.BaseKey
    :members:
    :undoc-members:

Network
-------

.. autoclass:: bitsv.network.NetworkAPI
    :members:
    :undoc-members:

.. autoclass:: bitsv.network.services.BitIndex
    :members:
    :undoc-members:
    :inherited-members:

.. autoclass:: bitsv.network.meta.Unspent
    :members:
    :undoc-members:

Exchange Rates
--------------

.. autofunction:: bitsv.network.currency_to_satoshi
.. autofunction:: bitsv.network.currency_to_satoshi_cached
.. autofunction:: bitsv.network.satoshi_to_currency
.. autofunction:: bitsv.network.satoshi_to_currency_cached

.. autoclass:: bitsv.network.rates.BitcoinSVRates
    :members:
    :undoc-members:
Fees
----

.. autofunction:: bitsv.network.get_fee
.. autofunction:: bitsv.network.get_fee_cached

Utilities
---------

.. autofunction:: bitsv.verify_sig

Exceptions
----------

.. autoexception:: bitsv.exceptions.InsufficientFunds
