import bitcoinx
from pycoin import key

# Popular derivation paths
DERIVATION_PATH_HANDCASH = '0'
DERIVATION_PATH_ELECTRUM_SV = '0'


class Bip32:
    """This is a wrapper for the pycoin Bip32 node constructor and takes either an xprv or xpub key string as
        and argument. If an xpub is used, hardened child keys and private keys for child addresses cannot be generated"""

    def __init__(self, extended_key):
        # pycoin.key.BIP32Node object
        self.node = key.Key.from_text(extended_key)
        self.bitcoinx_key = None

    def get_xpub(self):
        return self.node.as_text()

    def get_xprv(self):
        if self.node.is_private():
            return self.node.as_text(as_private=True)
        else:
            print("Your Bip32_Node is not derived from an xprv")

    def wif(self):
        return self.node.wif()

    def address(self, use_uncompressed=False):
        """Return the public address representation of this key, if available."""
        return self.node.address(use_uncompressed)

    def private_key(self, use_uncompressed=False):
        """Returns the private key for this extended private key"""
        if self.node.is_private():
            return self.node.wif(use_uncompressed)
        else:
            print("Your Bip32_Node is not derived from an xprv")

    def get_children(self, derivation_path=DERIVATION_PATH_ELECTRUM_SV, index_start=0, index_end=20):
        """Specify the start and end indexes for generating xpubs / xprv keys at the desired derivation_path.
        Default derivation path is m/0' for Handcash and Electrum SV wallets, therefore this is the default
        xprv --> xprv
        xpub --> xpub

        :param derivation_path: a path of subkeys denoted by numbers and slashes. Use H or p
        for private key derivation. End with .pub to force the key
        public.
        :type `str`
        :param index_start: Index to start deriving new children
        :param index_end: Index to stop deriving new children
        :rtype children: a `list` of `xprv` or `xpub` bip32 nodes at the derivation path specified """
        children = []
        for i in range(index_start, index_end):
            children.append(self.node.subkey_for_path(derivation_path + '/{}'.format(i)))
        return children

    def get_child_addresses(self, derivation_path=DERIVATION_PATH_ELECTRUM_SV, index_start=0, index_end=20):
        """Specify the start and end indexes for generating addresses at the desired derivation_path.
        For handcash and electrum sv the default derivation path is m/0' therefore "0 is the default here" """
        addr_list = []
        for i in range(index_start, index_end):
            addr_list.append(self.node.subkey_for_path(derivation_path + '/{}.pub'.format(i)).address())
        return addr_list

    def get_child_private_keys(self, derivation_path='0', index_start=0, index_end=20, wif_format=False):
        """wif format = True will output WIF format strings instead of private_key objects
        alternatively the private key objects have a wif() method to generate this later
        for use with bitsv transaction functions"""
        if self.node.is_private():
            try:
                keys_list = []
                for i in range(index_start, index_end):
                    keys_list.append(self.node.subkey_for_path(derivation_path + '/{}'.format(i)))
                if wif_format:
                    keys_list = [x.wif() for x in keys_list]
                return keys_list

            except ValueError as e:
                print(e)
        else:
            print("Your Bip32_Node is not derived from an xprv. xpub keys cannot be used to generate private keys")

    def sign_message(self, data, hasher=bitcoinx.double_sha256):
        """Returns a signature as bytes (65 bytes). Compatible with Bitcoind and Electrum SV
        for signature / verification"""
        if self.bitcoinx_key is None:  # computationally expensive - avoid repeating this for multiple signatures
            self.bitcoinx_key = bitcoinx.PrivateKey.from_WIF(self.wif())
        return self.bitcoinx_key.sign_message(data, hasher)

    def sign_message_to_base64(self, data, hasher=bitcoinx.double_sha256):
        """Returns signature as a base64 ASCII string. Compatible with Bitcoind and Electrum SV
        for signature / verification"""
        if self.bitcoinx_key is None:  # computationally expensive - avoid repeating this for multiple signatures
            self.bitcoinx_key = bitcoinx.PrivateKey.from_WIF(self.wif())
        return self.bitcoinx_key.sign_message_to_base64(data, hasher)

    def verify_data(self, data, sig, hasher=bitcoinx.double_sha256):
        """Return whether a signature is valid for data using this key."""
        if self.bitcoinx_key is None:  # computationally expensive - avoid repeating this for multiple signatures
            self.bitcoinx_key = bitcoinx.PrivateKey.from_WIF(self.wif())
        return self.bitcoinx_key.public_key.verify_message(sig, data, hasher)

    def verify_data_and_address(self, data, sig, address, hasher=bitcoinx.double_sha256):
        if self.bitcoinx_key is None:  # computationally expensive - avoid repeating this for multiple signatures
            self.bitcoinx_key = bitcoinx.PrivateKey.from_WIF(self.wif())
        return self.bitcoinx_key.public_key.verify_message_and_address(message_sig=sig, message=data, address=address,
                                                                       hasher=hasher)

    def chain_code(self):
        """32 byte chain code for xpub or xprv"""
        return self.node.chain_code()

    def fingerprint(self):
        return self.node.fingerprint()
