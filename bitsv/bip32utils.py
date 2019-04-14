import pycoin


# Popular derivation paths
DERIVATION_PATH_HANDCASH = '0'
DERIVATION_PATH_ELECTRUM_SV = '0'


class Bip32utils:
    """All functions (except for 'get_xprv_bip32_node()' and 'get_xpub_bip32_node()' constructors)
    use bip32 node objects as the input value rather than a string of the xprv or xpub keys"""
    # Functions for generating pycoin.key.BIP32Node objects
    get_xprv_bip32_node = pycoin.key.Key.from_text
    get_xpub_bip32_node = pycoin.key.Key.from_text

    @staticmethod
    def xpub_from_xprv(xprv):
        return xprv.public_copy()

    @staticmethod
    def get_addresses_from_xpub(xpub, derivation_path=DERIVATION_PATH_ELECTRUM_SV, index_start=0, index_end=20):
        """Specify the start and end indexes for generating addresses at derivation_path
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
        """wif format = True will output WIF format strings instead of private_key objects
        alternatively the private key objects have a wif() method to generate this later
        for use with bitsv transaction functions"""
        keys_list = []
        for i in range(index_start, index_end):
            keys_list.append(xprv.subkey_for_path(derivation_path + '/{}'.format(i)))
        if wif_format:
            keys_list = [x.wif() for x in keys_list]
        return keys_list

    get_addresses_from_xprv = get_addresses_from_xpub  # If path ends in ".pub", function always returns a pub (but takes either xprv or xpub as input)
