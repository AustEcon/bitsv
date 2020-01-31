Release History
===============

Unreleased (see `master <https://github.com/AustEcon/bitsv>`_)
--------------------------------------------------------------
- No new changes since 0.10.2 yet.

0.10.3 (2019-01-31)
-------------------
- Allow transaction fee less than 1 sat/byte (i.e. float) c/o `gitzhou <https://github.com/gitzhou>`_

0.10.2 (2019-11-28)
-------------------
- Fixed broken API endpoint for foreign currency conversions.

0.10.1 (2019-11-24)
-------------------

- Added new Fullnode class for connecting to local bitcoin node via JSON-RPC (thanks goes to https://github.com/xloem for the initial legwork).
- Fullnode class works for Mainnet, Testnet, Scaling-testnet and RegTest (local mock blockchain).
- Reordered outputs to always have 'false return' metadata included in the **first** output instead of the last. This will fix a new issue that arose with rendering of images etc. on bico.media.
- Prepend OP_FALSE to OP_RETURN in preparation for Genesis upgrade coming in February.
- Add 'sweep' function to PrivateKey class for sending all coins to a given address.
- 0.10.1 includes a patch for rpc methods list

0.9.0 (2019-08-11)
------------------

- **breaking** Bitcoin Cash addressees are no longer supported.
- Added bchsvexplorer for redundancy on mainnet.
- PrivateKey.get_transaction() now returns a ``Transaction`` object with ``TxInput`` and ``TxOutput`` objects within it.
- Metadata is represented in ``TxOutput.data`` as a list of ``pushdata`` fields.

0.8.0 (2019-7-13)
-----------------
- **breaking** ``PrivateKeyTest`` no longer exists (is now merged with ``PrivateKey`` class)
- **breaking** bip32.py no longer exists (is now moved to a new repo: https://github.com/AustEcon/bsvbip32)

    - Maintains modularity of codebase.
    - Bip32 deserves it's own repo as an extension to bitsv.
- Added ``BitIndex3`` (with main, test, stn support) - teething issues still on server side for stn due to very large volumes and requirement for server upgrades.
- **breaking** Refactored network services.py into separate modules (within services **folder**). (Only an issue for those who use these APIs directly rather than via PrivateKey)
- **breaking** Refactored ``NetworkAPI`` class to be accessed via object instantiation rather than via classmethods. (Only an issue for those who access ``NetworkAPI`` class directly rather than via ``PrivateKey``).

    - Allows for naming and testing of 5 prime function calls to be the same across all three networks (main/test/stn) and minimizes duplication of code and potential for errors.
    - Also allows for custom implementations of the ``NetworkAPI`` used by the ``PrivateKey`` on a case-by-case basis if necessary.
- Added main / test / stn network to ``NetworkAPI`` class (and therefore ``PrivateKey``) and normalization process for diverse (future) APIs.
- Improved the syntax for the send_op_return() function to accept a simple list
  of encoded bytes (old syntax still supported)
- Fixed a bug where a network error would result from leaving behind an amount < ``DUST`` (courtesy Carpemer)
- Added retry wrapper for 400 and 500 errors (courtesy Carpemer)

    - will come into play when throttled to e.g. 3 requests per second by the new BitIndex API.
- Added redundancy to the rates API (because the https://bitcoinsv-rates.com/api/rates/
  endpoint went down for several days). Therefore added a ``Bitfinex`` replacement in series:

    - Bitfinex endpoint "https://api.bitfinex.com/v1/pubticker/bsvusd" (for BSV/USD) combined with
    - FreeForexAPI endpoint "https://www.freeforexapi.com/api/live?pairs=" (for foreign currency pairs)
- send_op_return() will now **not** consolidate utxos by default. (i.e. combine=False is default parameter)
- restored python3.5 and pypy3 compatibility

0.7.1 (2019-4-20)
-----------------
- Legacy address now default __repr__
- Added documentation page for op_return related functionality see: https://austecon.github.io/bitsv/guide/op_return.html
  added Python3.7 to travis CI testing
- Bip32 feature set - have refactored and added functions (no documentation yet - coming soon).
- **Breaking**: Bip32 feature set refactored:

    - File renamed from bip32utils.py --> bip32.py and
    - **Deprecation warning**: Changed class name from bip32utils --> "Bip32" (basically wrapping pycoin.key.Key functions):
    - New functions: get_xpub, get_xprv, address, private_key, get_children, get_child_addresses, get_child_private_keys, sign, verify, chain_code, fingerprint
    - **Deprecation warning**: old class "bip32utils" is retained as an alias temporarily but will be removed with the next release.

0.6.1 (2019-4-15)
-----------------
- Fixed documentation --> now hosted on gh-pages at https://austecon.github.io/bitsv/
- Added "confirmations" field back into Unspents / UTXOs
- Fixed tests --> achieving coverage of 87% (needs new tests for new features added recently)
- Fixed badges on ReadMe for coverage: https://codecov.io/gh/austecon/bitsv and travis CI: https://travis-ci.org/AustEcon/bitsv

0.6.0 (2019-4-7)
----------------
- **New Feature**: Added Hierarchical deterministic wallet support (in bip32.py).

    - Can use xprv key to generate Electrum SV or Handcash list of address / private key pairs
    - Can use xpub key to generate list of addresses for viewing only

- Added BitIndex functions for dealing with extended public keys

0.5.6 (2019-3-30)
-----------------
- PyPi ReadMe rendering issues.

0.5.5 (2019-3-29)
-----------------
- Default fee set to 1 sat/byte for all transaction types.
- Updated ReadMe to include changes in 0.5.4 and updated examples.

0.5.4 (2019-03-25)
------------------
- Added 100kb OP_RETURN capability (fixed a bug).
- Fixed currency conversion courtesy "http://bitcoinsv-rates.com/api/rates/" api.
- Fixed issue with different APIs getting utxos out of sync with rapid transaction broadcasting.
- Fixed some tests and removed deprecated ones.

0.5.3 (2019-01-27)
------------------
- Port code base over to Bitcoin SV
- Allow raw byte string to be used as transaction OP_RETURN
  message. Increase message maximum OP_RETURN size to 220 bytes.
- Add a get_transaction() function to network services that
  returns an instance of a new Transaction class which
  contains some common details of the transaction.

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
