.. _network:

OP_RETURN
=========

Version 5.3 added feature
-------------------------

In version 0.5.3 the ability to have more fine control over pushdata elements inside
of the op_return was added.

This was done by adding the "custom_pushdata" = True / False parameter as a "switch" to the
:func:`~bitsv.PrivateKey.send` function and the
:func:`~bitsv.PrivateKey.create_transaction` functions.

Prior to this change, the only functionality was to simply send one string
of utf-8 encoded text as a "*message*".

Custom_pushdata = False
-----------------------

If custom_pushdata = False (default for backwards compatibility), the *message*
parameter is treated as per the original version and is expected to be a **string**.
As follows:

.. code-block:: python

    >>> import bitsv
    >>>
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> my_key.send(outputs = [],
                    message = "Hello")

Custom_pushdata = True
-----------------------

If custom_pushdata = True, the *message* parameter is expected to be a **list of bytes**
(explained below).

This example broadcasts a transaction with op_return data that in turn changes
your online memo_ social network name (linked to the private key) to "New_Name"
as per the memo protocol_.

Input a list of bytes.
Each byte array in the list becomes a push_data_ element within the OP_RETURN.

.. _push_data : https://en.bitcoin.it/wiki/Script#Constants
.. _memo : https://memo.sv/posts/ranked
.. _protocol : https://memo.sv/protocol

.. code-block:: python

    >>> import bitsv
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> list_of_pushdata = [bytes.fromhex('6d01'), # encode hex to bytes
                            'New_Name'.encode('utf-8')]  # encode string to utf-8 encoded bytes]
    >>> my_key.send(outputs = [],
                    message = list_of_pushdata,
                    custom_pushdata = True)

This gives a universally applicable way to send any kind of op_return data that you may need
with the additional option of adding payments to the list of outputs.

Note: Currently, multiple outputs containing op_returns for a **single** transaction are
considered "non-standard" by miners and are not currently supported by this library.

Send_op_return()
----------------

With the explosion of creativity on Bitcoin SV since the OP_RETURN limit was raised to 100kb,
it makes sense to have a *convenience* function for creating and sending OP_RETURN data.
The :func:`~bitsv.PrivateKey.send_op_return` function offers the most straight-forward
way to send op_return data onto the blockchain.

The way this function simplifies the process of sending op_return data is by taking the
more general purpose function, :func:`~bitsv.PrivateKey.send` and selecting sensible default
values. So the example above becomes:

.. code-block:: python

    >>> import bitsv
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> list_of_pushdata = [bytes.fromhex('6d01'),
                            'New_Name'.encode('utf-8')]
    >>> my_key.send_op_return(lst_of_pushdata)

Note: This function and the :func:`~bitsv.PrivateKey.create_op_return functions` by default
will **not consolidate your utxos** (keeps them split).
This differs to the default behaviour of the standard :func:`~bitsv.PrivateKey.send` and
:func:`~bitsv.PrivateKey.create_transaction` functions - and can be useful if you
are for example working with BCAT protocol (and require many small utxos with >= 1 confirmation).

Have a go! Even testing this stuff out on mainnet is super cheap. Make your mark on the world!
