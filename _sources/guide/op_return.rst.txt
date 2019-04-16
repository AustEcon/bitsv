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

If custom_pushdata = True, the *message* parameter is expected to be a **list of tuples**
(explained below).

This example broadcasts a transaction with op_return data that in turn changes
your online memo_ social network name (linked to the private key) to "new_name"
as per the memo protocol_.

Input a list of tuples ('data', 'encoding') with "utf-8" or "hex" encoding.
Each tuple in the list becomes a push_data_ element within the OP_RETURN.

.. _push_data : https://en.bitcoin.it/wiki/Script#Constants
.. _memo : https://memo.sv/posts/ranked
.. _protocol : https://memo.sv/protocol

.. code-block:: python

    >>> import bitsv
    >>>
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> lst_of_pushdata = [('6d01', 'hex'), ('new_name', 'utf-8')]
    >>> my_key.send(outputs = [],
                    message = lst_of_pushdata,
                    custom_pushdata = True)

This gives a universally applicable way to send any kind of op_return data that you may need
with the additional option of adding payments to the list of outputs.

Note: Currently, multiple outputs containing op_returns for a **single** transaction are
considered "non-standard" by miners and are not currently supported by this library
(as of 16/04/19).

Send_op_return()
----------------

I have however, added an additional *convenience* function, :func:`~bitsv.PrivateKey.send_op_return`
which offers the most straight forward way to send op_return data onto the blockchain.

The way this function simplifies the process of sending op_return data is by taking the
more general purpose function, :func:`~bitsv.PrivateKey.send` and selecting sensible default
values.

.. code-block:: python

    >>> import bitsv
    >>>
    >>> my_key = bitsv.Key('YourPrivateKeyGoesHere')
    >>> lst_of_pushdata = [('6d01', 'hex'), ('new_name', 'utf-8')]
    >>> my_key.send_op_return(lst_of_pushdata)

Have a go! Testing this stuff out on mainnet is super cheap. Make your mark on the world.
