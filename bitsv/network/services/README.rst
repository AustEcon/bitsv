"Full node" connectivity
========================

This feature has been added by popular demand. Pull requests for refinement are welcome.
However, do bear in mind that the wallet functionality of the bitcoin node will soon be removed
so this feature may not be of much use long-term.

.. code-block:: python

    >>> from bitsv import Fullnode
    >>> fullnode = FullNode(
            conf_dir='/home/username/.bitcoin/regtest.conf',
            rpcuser='user',
            rpcpassword='password',
            network='regtest')

note: wallet features of the node software will soon be deprecated. However, possible use cases may include

    - Rapid transaction broadcasting ~ 200tx/sec):
    - Regtesting of app in AzurePipelines or Travis CI for example.

The fullnode object has a complete internal list of all JSON-RPC methods added to __dict__ for code completion:

.. figure:: images/obj_dict.png

Example RegTest functionality:

.. code-block:: python

    >>> address = fullnode.getaccountaddress("my_account")
    >>> fullnode.generate(200)  # mine 200 blocks on regtest network
    >>> fullnode.sendtoaddress(address, 10)
    'd4574b01471d95e63d218885324996d7d6c8fd4180a5fd024e48b5c27b956ca6'
    >>> # usual bitsv network_api functions also available:
    >>> fullnode.get_balance(address)
    1000000000
    >>> fullnode.get_unspents(address)
    [Unspent(amount=1000000000, confirmations=0, script='76a9141d03bffd36f5adab7c892255a703d032616146c488ac',
    txid='d4574b01471d95e63d218885324996d7d6c8fd4180a5fd024e48b5c27b956ca6', txindex=1)]
     >>> fullnode.get_transaction("d4574b01471d95e63d218885324996d7d6c8fd4180a5fd024e48b5c27b956ca6")
     Transaction(txid='d4574b01471d95e63d218885324996d7d6c8fd4180a5fd024e48b5c27b956ca6',
     amount_in=5000000000, amount_out=4999996160, fee=3840, inputs=1, outputs=2)
    >>> fullnode.dumpprivkey(address)
    "cTW5PD5ZVcRTzSL3QByiQDdCvAffpRVjEdhPe6VQPKC9pYjGFsyp"
    >>> import bitsv
    >>> my_regtest_key = bitsv.PrivateKey("cTW5PD5ZVcRTzSL3QByiQDdCvAffpRVjEdhPe6VQPKC9pYjGFsyp")
    >>> rawtx = my_regtest_key.create_op_return_tx([b"Hello"], unspents=fullnode.get_unspents(address))
    >>> rawtx
    '0100000001a66c957bc2b5484e02fda58041fdc8d6d79649328588213de6951d47014b57d4010000006b48304502210'
    '0ba39a87afe9417141dae2bf8835710bdf801915a017ed11a51ba43f239d4839f02203f6385f7d87504d97dd94533eb'
    '26d2bc45ad82ede08cfd15d96c30ebc703aab7412102eac16d7d16ae1427802650d05e91616a76378bf64a3993a8b33'
    '22bcda060f4c3ffffffff02000000000000000008006a0548656c6c6f2fc99a3b000000001976a9141d03bffd36f5ad'
    'ab7c892255a703d032616146c488ac00000000'
    >>> fullnode.broadcast_tx(rawtx)
    "2588b60aef1cf82e78f558bf868de6001bc36f822ec18375cc260d5f233b707d"

Another use case is simply for manufacturing scenarios to learn from.
For example, try the create_op_return_tx() + broadcast_tx() repeatedly > 25x and observe the
"JSONRPCException: -26: 64: too-long-mempool-chain" error. Then observe it going away after
generating a new block... on RegTest there is no waiting 10 minutes for confirmations to
reproduce this kind of error, useful for an accelerated development cycle.