import json

from bitsv.crypto import ECPrivateKey
from bitsv.curve import Point
from bitsv.format import (
    bytes_to_wif, public_key_to_address, public_key_to_coords, wif_to_bytes,
    address_to_public_key_hash
)
from bitsv.network import NetworkAPI, get_fee, satoshi_to_currency_cached
from bitsv.network.meta import Unspent
from bitsv.transaction import (
    calc_txid, create_p2pkh_transaction, sanitize_tx_data,
    OP_CHECKSIG, OP_DUP, OP_EQUALVERIFY, OP_HASH160, OP_PUSH_20
    )
from bitsv import op_return

# Instantiate Main, Test and STN NetworkAPI instances for use by all PrivateKey[Test]'s
network_api_main = NetworkAPI('main')
network_api_test = NetworkAPI('test')
network_api_stn = NetworkAPI('stn')


def wif_to_key(wif, network=None):
    """This function can read the 'prefix' byte of a wif and instatiate the appropriate PrivateKey object.
    see: https://en.bitcoin.it/wiki/List_of_address_prefixes
    The prefix byte is the same for testnet and scaling-testnet.
    So to use scaling-testnet you must give as a parameter: network='stn'
    :param wif: A private key serialized to the Wallet Import Format.
    :type wif: ``str``
    :param network: 'main', 'test' or 'stn'
    :type network: ``str``
    """
    private_key_bytes, compressed, prefix = wif_to_bytes(wif)

    wif_network_mismatch = "WIF prefix: '{}' does not match network: '{}'".format(prefix, network)

    if network == 'main':
        if prefix != 'main':
            raise ValueError(wif_network_mismatch)
    elif network in ['test', 'stn']:
        if prefix != 'test':
            raise ValueError(wif_network_mismatch)
    elif network is None:
        if prefix == 'main':
            network = 'main'
        elif prefix == 'test':
            network = 'test'
        else:
            raise Exception('bitsv issue, please open a bug report!')
    else:
        raise ValueError('network must be one of: main, test, stn')

    if compressed:
        return PrivateKey.from_bytes(private_key_bytes, network=network)
    else:
        return PrivateKey(wif, network=network)


class BaseKey:
    """This class represents a point on the elliptic curve secp256k1 and
    provides all necessary cryptographic functionality. You shouldn't use
    this class directly.

    :param wif: A private key serialized to the Wallet Import Format. If the
                argument is not supplied, a new private key will be created.
                The WIF compression flag will be adhered to, but the prefix
                byte is disregarded. Compression will be used by all new keys.
    :type wif: ``str``
    :raises TypeError: If ``wif`` is not a ``str``.
    """
    def __init__(self, wif=None):
        if wif:
            if isinstance(wif, str):
                private_key_bytes, compressed, prefix = wif_to_bytes(wif)
                self._pk = ECPrivateKey(private_key_bytes)
            elif isinstance(wif, ECPrivateKey):
                self._pk = wif
                compressed = True
            else:
                raise TypeError('Wallet Import Format must be a string.')
        else:
            self._pk = ECPrivateKey()
            compressed = True

        self._public_point = None
        self._public_key = self._pk.public_key.format(compressed=compressed)

    @property
    def public_key(self):
        """The public point serialized to bytes."""
        return self._public_key

    @property
    def public_point(self):
        """The public point (x, y)."""
        if self._public_point is None:
            self._public_point = Point(*public_key_to_coords(self._public_key))
        return self._public_point

    def sign(self, data):
        """Signs some data which can be verified later by others using
        the public key.

        :param data: The message to sign.
        :type data: ``bytes``
        :returns: A signature compliant with BIP-62.
        :rtype: ``bytes``
        """
        return self._pk.sign(data)

    def verify(self, signature, data):
        """Verifies some data was signed by this private key.

        :param signature: The signature to verify.
        :type signature: ``bytes``
        :param data: The data that was supposedly signed.
        :type data: ``bytes``
        :rtype: ``bool``
        """
        return self._pk.public_key.verify(signature, data)

    def to_hex(self):
        """:rtype: ``str``"""
        return self._pk.to_hex()

    def to_bytes(self):
        """:rtype: ``bytes``"""
        return self._pk.secret

    def to_der(self):
        """:rtype: ``bytes``"""
        return self._pk.to_der()

    def to_pem(self):
        """:rtype: ``bytes``"""
        return self._pk.to_pem()

    def to_int(self):
        """:rtype: ``int``"""
        return self._pk.to_int()

    def is_compressed(self):
        """Returns whether or not this private key corresponds to a compressed
        public key.

        :rtype: ``bool``
        """
        return True if len(self.public_key) == 33 else False

    def __eq__(self, other):
        return self.to_int() == other.to_int()


class PrivateKey(BaseKey):
    """This class represents a Bitcoin SV private key. ``Key`` is an alias.
    Select from network = 'main', 'test' or 'stn' for mainnet, testnet or scaling-testnet respectively.
    Defaults to mainnet.

    :param wif: A private key serialized to the Wallet Import Format. If the
                argument is not supplied, a new private key will be created.
                The WIF compression flag will be adhered to, but the prefix
                byte is disregarded. Compression will be used by all new keys.
    :type wif: ``str``
    :raises TypeError: If ``wif`` is not a ``str``.
    :param network: 'main', 'test' or 'stn'
    :type network: ``str``
    """

    def __init__(self, wif=None, network='main'):
        super().__init__(wif=wif)

        self._address = None
        self._scriptcode = None

        self.balance = 0
        self.unspents = []
        self.transactions = []
        self.network = network

        # Standard network_api_main/test/stn objects are instantiated at top of this file as globals.
        # Avoids multiple unnecessary instances of these in the case of many Keys
        if network == 'main':
            self.network_api = network_api_main
            self.prefix = 'main'
        elif network == 'test':
            self.network_api = network_api_test
            self.prefix = 'test'
        elif network == 'stn':
            self.network_api = network_api_stn
            # Scaling-testnet has the same "prefix" as testnet (https://bitcoinscaling.io/)
            self.prefix = 'test'

    @property
    def address(self):
        """The public address you share with others to receive funds."""
        if self._address is None:
            self._address = public_key_to_address(self._public_key, prefix=self.prefix)

        return self._address

    @property
    def scriptcode(self):
        self._scriptcode = (OP_DUP + OP_HASH160 + OP_PUSH_20 +
                            address_to_public_key_hash(self.address) +
                            OP_EQUALVERIFY + OP_CHECKSIG)
        return self._scriptcode

    def to_wif(self):
        return bytes_to_wif(
            self._pk.secret,
            prefix=self.prefix,
            compressed=self.is_compressed()
        )

    def balance_as(self, currency):
        """Returns your balance as a formatted string in a particular currency.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        return satoshi_to_currency_cached(self.balance, currency)

    def get_balance(self, currency='satoshi'):
        """Fetches the current balance.
        :func:`~bitsv.PrivateKey.get_unspents` and returns it using
        :func:`~bitsv.PrivateKey.balance_as`.

        :param currency: One of the :ref:`supported currencies`.
        :type currency: ``str``
        :rtype: ``str``
        """
        self.get_unspents()
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.balance_as(currency)

    def get_unspents(self):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :param address: Address to get utxos for
        :param sort: 'value:desc' or 'value:asc' to sort unspents by descending/ascending order respectively
        :rtype: ``list`` of :class:`~bitsv.network.meta.Unspent`
        """
        self.unspents[:] = self.network_api.get_unspents(self.address)
        self.balance = sum(unspent.amount for unspent in self.unspents)
        return self.unspents

    def get_transactions(self):
        """Fetches transaction history.
        :param from_index: First index from transactions list to start collecting from
        :param to_index: Final index to finish collecting transactions from
        :rtype: ``list`` of ``str`` transaction IDs
        """
        self.transactions = self.network_api.get_transactions(self.address)
        return self.transactions

    def get_transaction(self, txid):
        """Gets a single transaction.
        :param txid: txid for transaction you want information about
        :type txid: ``str``
        """
        transaction = self.network_api.get_transaction(txid)
        return transaction

    def create_transaction(self, outputs, fee=None, leftover=None, combine=True,
                           message=None, unspents=None, custom_pushdata=False):  # pragma: no cover
        """Creates a signed P2PKH transaction.

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    BitSV will use a fee of 1 sat/byte.
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default BitSV will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not BitSV should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default BitSV will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 100kb.
        :type message: ``str`` if custom_pushdata = False; ``list`` of ``tuple`` if custom_pushdata = True
        :param unspents: The UTXOs to use as the inputs. By default BitSV will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bitsv.network.meta.Unspent`
        :param custom_pushdata: Adds control over push_data elements inside of the op_return by adding the
                                "custom_pushdata" = True / False parameter as a "switch" to the
                                :func:`~bitsv.PrivateKey.send` function and the
                                :func:`~bitsv.PrivateKey.create_transaction` functions.
        :type custom_pushdata: ``bool``
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """

        unspents, outputs = sanitize_tx_data(
            unspents or self.unspents,
            outputs,
            fee or get_fee(),
            leftover or self.address,
            combine=combine,
            message=message,
            compressed=self.is_compressed(),
            custom_pushdata=custom_pushdata
        )

        return create_p2pkh_transaction(self, unspents, outputs, custom_pushdata=custom_pushdata)

    def create_op_return_tx(self, list_of_pushdata, outputs=None, fee=1, unspents=None, leftover=None, combine=False):
        """Creates a rawtx with OP_RETURN metadata ready for broadcast.

        Parameters
        ----------
        list_of_pushdata : a list of tuples (pushdata, encoding) where encoding is either "hex" or "utf-8"
        fee : sat/byte (defaults to 1 satoshi per byte)

        Returns
        -------
        rawtx

        Examples
        --------

        list_of_pushdata =  [('6d01', 'hex'),
                            ('bitPUSHER', 'utf-8')]

        as per memo.cash protocol @ https://memo.cash/protocol this results in a "Set name" action to "bitPUSHER"

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    BitSV will use a fee of 1 sat/byte
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default BitSV will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not BitSV should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default BitSV will consolidate UTXOs.
        :type combine: ``bool``
        :param unspents: The UTXOs to use as the inputs. By default BitSV will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bitsv.network.meta.Unspent`
        :param list_of_pushdata: List indicating pushdata to be included in op_return as e.g.:
                                [('6d01', 'hex'),
                                 ('hello', 'utf-8')]
        :type list_of_pushdata:`list` of `tuples`
        """
        if not outputs:
            outputs = []

        pushdata = op_return.create_pushdata(list_of_pushdata)
        rawtx = self.create_transaction(outputs,
                                        fee=fee,
                                        message=pushdata,
                                        custom_pushdata=True,
                                        combine=combine,
                                        unspents=unspents or self.unspents,
                                        leftover=leftover or self.address)

        return rawtx

    def send_op_return(self, list_of_pushdata, outputs=None, fee=1, unspents=None, leftover=None, combine=False):
        """Sends a rawtx with OP_RETURN metadata ready for broadcast.

        Parameters
        ----------
        list_of_pushdata : a list of tuples (pushdata, encoding) where encoding is either "hex" or "utf-8"
        fee : sat/byte (defaults to 1 satoshi per byte)

        Returns
        -------
        rawtx

        Examples
        --------

        list_of_pushdata =  [('6d01', 'hex'),
                            ('bitPUSHER', 'utf-8')]

        as per memo.cash protocol @ https://memo.cash/protocol this results in a "Set name" action to "bitPUSHER"

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    BitSV will use a fee of 1 sat/byte
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default BitSV will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not BitSV should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default BitSV will consolidate UTXOs.
        :type combine: ``bool``
        :param unspents: The UTXOs to use as the inputs. By default BitSV will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bitsv.network.meta.Unspent`
        :param list_of_pushdata: List indicating pushdata to be included in op_return as e.g.:
                                [('6d01', 'hex'),
                                 ('hello', 'utf-8')]
        :type list_of_pushdata:`list` of `tuples`
        """
        if not outputs:
            outputs = []

        self.get_unspents()
        pushdata = op_return.create_pushdata(list_of_pushdata)
        tx_hex = self.create_transaction(outputs=outputs, fee=fee, message=pushdata, custom_pushdata=True,
                                         combine=combine, unspents=unspents, leftover=leftover
                                         )

        self.network_api.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    def send(self, outputs, fee=None, leftover=None, combine=True,
             message=None, unspents=None, custom_pushdata=False):  # pragma: no cover
        """Creates a signed P2PKH transaction and attempts to broadcast it on
        the blockchain. This accepts the same arguments as
        :func:`~bitsv.PrivateKey.create_transaction`.

        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    BitSV will use a fee of 1 sat/byte.
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default BitSV will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not BitSV should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default BitSV will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 100kb.
        :type message: ``str`` if custom_pushdata = False; ``list`` of ``tuple`` if custom_pushdata = True
        :param unspents: The UTXOs to use as the inputs. By default BitSV will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bitsv.network.meta.Unspent`
        :param custom_pushdata: Adds control over push_data elements inside of the op_return by adding the
                                "custom_pushdata" = True / False parameter as a "switch" to the
                                :func:`~bitsv.PrivateKey.send` function and the
                                :func:`~bitsv.PrivateKey.create_transaction` functions.
        :type custom_pushdata: ``bool``
        :returns: The transaction ID.
        :rtype: ``str``
        """
        self.get_unspents()
        tx_hex = self.create_transaction(
            outputs, fee=fee, leftover=leftover, combine=combine,
            message=message, unspents=unspents, custom_pushdata=custom_pushdata
        )

        self.network_api.broadcast_tx(tx_hex)

        return calc_txid(tx_hex)

    def prepare_transaction(self, address, outputs, compressed=True, fee=None, leftover=None,
                            combine=True, message=None, unspents=None, custom_pushdata=False):  # pragma: no cover
        """Prepares a P2PKH transaction for offline signing.

        :param address: The address the funds will be sent from.
        :type address: ``str``
        :param outputs: A sequence of outputs you wish to send in the form
                        ``(destination, amount, currency)``. The amount can
                        be either an int, float, or string as long as it is
                        a valid input to ``decimal.Decimal``. The currency
                        must be :ref:`supported <supported currencies>`.
        :type outputs: ``list`` of ``tuple``
        :param compressed: Whether or not the ``address`` corresponds to a
                           compressed public key. This influences the fee.
        :type compressed: ``bool``
        :param fee: The number of satoshi per byte to pay to miners. By default
                    BitSV will use a fee of 1 sat/byte
        :type fee: ``int``
        :param leftover: The destination that will receive any change from the
                         transaction. By default BitSV will send any change to
                         the same address you sent from.
        :type leftover: ``str``
        :param combine: Whether or not BitSV should use all available UTXOs to
                        make future transactions smaller and therefore reduce
                        fees. By default BitSV will consolidate UTXOs.
        :type combine: ``bool``
        :param message: A message to include in the transaction. This will be
                        stored in the blockchain forever. Due to size limits,
                        each message will be stored in chunks of 100kb bytes.
        :type message: ``str`` if custom_pushdata = False; ``list`` of ``tuple`` if custom_pushdata = True
        :param unspents: The UTXOs to use as the inputs. By default BitSV will
                         communicate with the blockchain itself.
        :type unspents: ``list`` of :class:`~bitsv.network.meta.Unspent`
        :param custom_pushdata: Adds control over push_data elements inside of the op_return by adding the
                                "custom_pushdata" = True / False parameter as a "switch" to the
                                :func:`~bitsv.PrivateKey.send` function and the
                                :func:`~bitsv.PrivateKey.create_transaction` functions.
        :type custom_pushdata: ``bool``
        :returns: JSON storing data required to create an offline transaction.
        :rtype: ``str``
        """
        unspents, outputs = sanitize_tx_data(
            unspents or self.network_api.get_unspents(address),
            outputs,
            fee or get_fee(),
            leftover or address,
            combine=combine,
            message=message,
            compressed=compressed,
            custom_pushdata=custom_pushdata
        )

        data = {
            'unspents': [unspent.to_dict() for unspent in unspents],
            'outputs': outputs
        }

        return json.dumps(data, separators=(',', ':'))

    def sign_transaction(self, tx_data):  # pragma: no cover
        """Creates a signed P2PKH transaction using previously prepared
        transaction data.

        :param tx_data: Output of :func:`~bitsv.PrivateKey.prepare_transaction`.
        :type tx_data: ``str``
        :returns: The signed transaction as hex.
        :rtype: ``str``
        """
        data = json.loads(tx_data)

        unspents = [Unspent.from_dict(unspent) for unspent in data['unspents']]
        outputs = data['outputs']

        return create_p2pkh_transaction(self, unspents, outputs)

    @classmethod
    def from_hex(cls, hexed, network='main'):
        """
        :param hexed: A private key previously encoded as hex.
        :type hexed: ``str``
        :param network: 'main', 'test' or 'stn'
        :type network: ``str``
        :rtype: :class:`~bitsv.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_hex(hexed), network=network)

    @classmethod
    def from_bytes(cls, bytestr, network='main'):
        """
        :param bytestr: A private key previously encoded as hex.
        :type bytestr: ``bytes``
        :param network: 'main', 'test' or 'stn'
        :type network: ``str``
        :rtype: :class:`~bitsv.PrivateKey`
        """
        return PrivateKey(ECPrivateKey(bytestr), network=network)

    @classmethod
    def from_der(cls, der, network='main'):
        """
        :param der: A private key previously encoded as DER.
        :type der: ``bytes``
        :param network: 'main', 'test' or 'stn'
        :type network: ``str``
        :rtype: :class:`~bitsv.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_der(der), network=network)

    @classmethod
    def from_pem(cls, pem, network='main'):
        """
        :param pem: A private key previously encoded as PEM.
        :type pem: ``bytes``
        :param network: 'main', 'test' or 'stn'
        :type network: ``str``
        :rtype: :class:`~bitsv.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_pem(pem), network=network)

    @classmethod
    def from_int(cls, num, network='main'):
        """
        :param num: A private key in raw integer form.
        :type num: ``int``
        :param network: 'main', 'test' or 'stn'
        :type network: ``str``
        :rtype: :class:`~bitsv.PrivateKey`
        """
        return PrivateKey(ECPrivateKey.from_int(num), network=network)

    def __repr__(self):
        return '<PrivateKey: {}>'.format(self.address)


Key = PrivateKey
