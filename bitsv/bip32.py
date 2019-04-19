import pycoin

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

    def get_xpub(self):
        return self.node.public_copy()

    def address(self, use_uncompressed=False):
        """Return the public address representation of this key, if available.
        If use_uncompressed is not set, the preferred representation is returned."""
        return self.node.address(use_uncompressed)

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
        if self.node.is_private:
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


# Old Aliases planned for deprecation
class Bip32utils:
    """
    DEPRECATION WARNING: THIS CLASS WILL BE REMOVED FROM THIS LIBRARY IN THE VERY NEAR FUTURE.
    All functions (except for 'get_xprv_bip32_node()' and 'get_xpub_bip32_node()' constructors)
    use bip32 node objects as the input value rather than a string of the xprv or xpub keys"""
    # Functions for generating pycoin.key.BIP32Node objects
    get_xprv_bip32_node = pycoin.key.Key.from_text
    get_xpub_bip32_node = pycoin.key.Key.from_text

    @staticmethod
    def xpub_from_xprv(xprv):
        """DEPRECATION WARNING: THIS CLASS WILL BE REMOVED FROM THIS LIBRARY IN THE VERY NEAR FUTURE."""
        return xprv.public_copy()

    @staticmethod
    def get_addresses_from_xpub(xpub, derivation_path=DERIVATION_PATH_ELECTRUM_SV, index_start=0, index_end=20):
        """
        DEPRECATION WARNING: THIS CLASS WILL BE REMOVED FROM THIS LIBRARY IN THE VERY NEAR FUTURE.
        Specify the start and end indexes for generating addresses at derivation_path
        derivation_path = a string of indices e.g. "0" or "45/0/0"
        for handcash and electrum sv the default derivation path is m/0' therefore "0 is the default here" """
        addr_list = []
        for i in range(index_start, index_end):
            addr_list.append(xpub.subkey_for_path(derivation_path + '/{}.pub'.format(i)).address())
        return addr_list

    # Or can use xprv to get addresses (xprv or xpub --> pub address if path ends in ".pub")
    get_addresses_from_xprv = get_addresses_from_xpub

    @staticmethod
    def get_private_keys(xprv, derivation_path='0', index_start=0, index_end=20, wif_format=False):
        """
        DEPRECATION WARNING: THIS CLASS WILL BE REMOVED FROM THIS LIBRARY IN THE VERY NEAR FUTURE.
        wif format = True will output WIF format strings instead of private_key objects
        alternatively the private key objects have a wif() method to generate this later
        for use with bitsv transaction functions"""
        keys_list = []
        for i in range(index_start, index_end):
            keys_list.append(xprv.subkey_for_path(derivation_path + '/{}'.format(i)))
        if wif_format:
            keys_list = [x.wif() for x in keys_list]
        return keys_list

    get_addresses_from_xprv = get_addresses_from_xpub
