Release History
===============

Unreleased (see `master <https://github.com/AustEcon/bitsv>`_)
--------------------------------------------------------------

- Add a get_transaction() function to network services that
  returns an instance of a new Transaction class which
  contains some common details of the transaction.

- Allow raw byte string to be used as transaction OP_RETURN
  message: automatic detection assumes a byte-like object when
  message does not have an encode() function. Increase message
  size to 220 bytes.

- NetworkAPI.get_tx_amount() is now working and properly handles
  backends returning string or decimal values.

0.5.2 (2018-05-16)
------------------

- bccblock.info is offline, replace with cashexplorer.bitcoin.com.
  Hard fork happened yesterday. Not sure if bccblock.info was even ready
  for that.

0.5.1 (2018-03-11)
------------------

- Fix fee calculation with combined=False.
- Also lower fees since we can. Couple little tweaks.
- Delete a .orig file I had added before by mistake.

0.5.0 (2018-02-03)
------------------

- Breaking change! Add cashaddr support, return .address as
  cashaddr. That hopefully is all that breaks.

0.4.3 (2017-12-20)
------------------

- Switch from Bitpay to BCCBlock.info.
  Bitpay API is unusable with their address format, unless we
  switch over. Not interested in doing that in the near future so
  I found another block explorer.

0.4.2 (2017-12-20)
------------------

- Raise exception when using pay2sh addresses.

0.4.1 (2017-11-01)
------------------

- Removed ``blockr.io`` network backend as `Coinbase <https://www.coinbase.com>`_ has shut it down.

0.4.0 (2017-04-19)
------------------

- Changed elliptic curve backend from OpenSSL to libsecp256k1. This results
  in an order of magnitude faster key creation and signing/verifying.
- Improved performance of base58 encoding/decoding.
- **Breaking:** Dropped support for Python 3.3 & 3.4.
- **Breaking:** :func: `~bitsv.verify_sig` now returns ``False`` for invalid
  signatures instead of raising an exception. Also, ``strict`` is no longer
  a parameter as BIP-62 compliance is now required.

0.3.1 (2017-03-21)
------------------

- **Fixed** :ref: `cold storage <coldstorage>` workflow.
- Improved performance of private key instantiation.

0.3.0 (2017-03-20)
------------------

- Implemented a way to use private keys in :ref: `cold storage <coldstorage>`.
- Changed the default timeout of services from 5 to 10 seconds.
- Fixed network service redundancy by failing if response code is not 200.

0.2.0 (2017-03-17)
------------------

- Improved stability of network tests.
- Added :func: `~bitsv.verify_sig`.
- Refactored crypto to yield over an order of magnitude faster hashing.

0.1.0 (2017-03-15)
------------------

- Initial release.
