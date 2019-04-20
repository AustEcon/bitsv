import bitsv
from pycoin import key

# BIP32 SEED FOR TESTING
ELECTRUMSV_MNEMONIC = "napkin economy fantasy once review problem spy check glass notable clever vivid"
MASTERPRIVATE = "xprv9s21ZrQH143K37qBWUa7HdFMZHVrN7N9jNH8CGFBS6RC8r9RVYHnGjhMHAUJu4ya2r4RQhgCcVFrDZk769U1E8puMZugTLAHLCYnwjfWNXz"
MASTERPUBLICKEY = "xpub661MyMwAqRbcFbuecW77emC67KLLma616bCizeenzRxB1eUa35c2pY1q8TUZCHE7ErNaxraAmbh7Jk8isPVqCsVzhahG4or257wAUMqGwmy"
CHILD_ADDRESSES = ['19nU1uDNXPbaEaYU8TKTuHy5wL8Y2eo3Gz',
                   '1AjgahPwTzyZEDKuAHiu67aUPt4YMBMZaC',
                   '1KdYRrt3zRNTD7Hz9dJvku48kv6VPyBciZ',
                   '1MNdZoh59n7KXKMoYwsXm2ecNh8yCbruqJ',
                   '1EiJeYdzXLV4A21VKJQJsprkpUSU2m4Km1']


class TestBip32:
    def test_init(self):
        b32 = bitsv.Bip32(MASTERPRIVATE)

        assert isinstance(b32.node, type(key.Key.from_text(MASTERPRIVATE)))
        assert b32.bitcoinx_key is None



