import bitsv
from pycoin import key
import pytest

# BIP32 SEED FOR TESTING
ELECTRUMSV_MNEMONIC = "napkin economy fantasy once review problem spy check glass notable clever vivid"
MASTERPRIVATE = "xprv9s21ZrQH143K37qBWUa7HdFMZHVrN7N9jNH8CGFBS6RC8r9RVYHnGjhMHAUJu4ya2r4RQhgCcVFrDZk769U1E8puMZugTLAHLCYnwjfWNXz"
MASTERPRIVATEWIF = "L4x2ab2CQDgMSPKno1b6RUgoyQgPHfy6RtE7HF6UNL1SLg1h8QtL"
MASTERPUBLIC = "xpub661MyMwAqRbcFbuecW77emC67KLLma616bCizeenzRxB1eUa35c2pY1q8TUZCHE7ErNaxraAmbh7Jk8isPVqCsVzhahG4or257wAUMqGwmy"
ADDRESS = '1ERLwM8TjXtzCVkXqoFpp1EifSdUin4s62'
ADDRESS_UNCOMPRESSED = '1FPKMkt4N5Dvdcu6xTnYzgN47498cEh1Hb'

XPRV_FIRST_CHILD_REPR = "<bitsv.Bip32 obj from private_key for <xpub6B6u9rPc7hrhm3HPFWgg5vRP4zhdiT7PCExvRbUYS7yBnPSEqs6JTSYAKvUkH1Ftb8QmwHuaYzYFkCoFywdy2R9WZjaGxHoUdUbAvLgVmqu>>"
XPRV_SECOND_CHILD_REPR = "<bitsv.Bip32 obj from private_key for <xpub6B6u9rPc7hrhoz62yyyuRwZK9KWwafTqjjvJrSNs9v2jFdLw1EQztEBMBLdTcZe2Z1jpTxhXiMWbkpHa8ja1wchNQttVd8zULoVy5SXJFRp>>"
XPRV_THIRD_CHILD_REPR = "<bitsv.Bip32 obj from private_key for <xpub6B6u9rPc7hrhrBT5Ky81PXLqAG14wD9KpYBW8Zj3VGSRPhTrzvbdGDLhhLL3LmgdzVFjjosZtC9XdEGsntw8zA4R22zqYA1ZxEPHAa47bfs>>"
XPUB_FIRST_CHILD_REPR = '<bitsv.Bip32 obj from pubkey: <xpub6B6u9rPc7hrhm3HPFWgg5vRP4zhdiT7PCExvRbUYS7yBnPSEqs6JTSYAKvUkH1Ftb8QmwHuaYzYFkCoFywdy2R9WZjaGxHoUdUbAvLgVmqu>>'
XPUB_SECOND_CHILD_REPR = '<bitsv.Bip32 obj from pubkey: <xpub6B6u9rPc7hrhoz62yyyuRwZK9KWwafTqjjvJrSNs9v2jFdLw1EQztEBMBLdTcZe2Z1jpTxhXiMWbkpHa8ja1wchNQttVd8zULoVy5SXJFRp>>'
XPUB_THIRD_CHILD_REPR = '<bitsv.Bip32 obj from pubkey: <xpub6B6u9rPc7hrhrBT5Ky81PXLqAG14wD9KpYBW8Zj3VGSRPhTrzvbdGDLhhLL3LmgdzVFjjosZtC9XdEGsntw8zA4R22zqYA1ZxEPHAa47bfs>>'
CHILD_ADDRESSES = ['19nU1uDNXPbaEaYU8TKTuHy5wL8Y2eo3Gz',
                   '1AjgahPwTzyZEDKuAHiu67aUPt4YMBMZaC',
                   '1KdYRrt3zRNTD7Hz9dJvku48kv6VPyBciZ',
                   '1MNdZoh59n7KXKMoYwsXm2ecNh8yCbruqJ',
                   '1EiJeYdzXLV4A21VKJQJsprkpUSU2m4Km1']


class TestBip32:

    def test_init(self):
        b32 = bitsv.Bip32(MASTERPRIVATE)
        assert isinstance(b32.node, type(key.Key.from_text(MASTERPRIVATE)))  # matches pycoin class
        assert b32.bitcoinx_key is None  # object only created on an as-needed basis and only ever created once

    def test_get_xpub(self):
        b32_xprv = bitsv.Bip32(MASTERPRIVATE)
        b32_xpub = bitsv.Bip32(MASTERPUBLIC)
        assert b32_xprv.get_xpub() == MASTERPUBLIC
        assert b32_xpub.get_xpub() == MASTERPUBLIC

    def test_get_xprv(self):
        b32_xprv = bitsv.Bip32(MASTERPRIVATE)
        b32_xpub = bitsv.Bip32(MASTERPUBLIC)
        assert b32_xprv.get_xprv() == MASTERPRIVATE
        with pytest.raises(ValueError):
            b32_xpub.get_xprv()

    def test_wif(self):
        b32_xprv = bitsv.Bip32(MASTERPRIVATE)
        b32_xpub = bitsv.Bip32(MASTERPUBLIC)
        assert b32_xprv.wif() == MASTERPRIVATEWIF
        with pytest.raises(ValueError):
            b32_xpub.wif()

    def test_address(self):
        b32_xprv = bitsv.Bip32(MASTERPRIVATE)
        b32_xpub = bitsv.Bip32(MASTERPUBLIC)
        assert b32_xprv.address(use_uncompressed=False) == ADDRESS
        assert b32_xprv.address(use_uncompressed=True) == ADDRESS_UNCOMPRESSED
        assert b32_xpub.address(use_uncompressed=False) == ADDRESS
        assert b32_xpub.address(use_uncompressed=True) == ADDRESS_UNCOMPRESSED

    def test_get_children(self):
        b32_xprv = bitsv.Bip32(MASTERPRIVATE)
        b32_xpub = bitsv.Bip32(MASTERPUBLIC)
        # __repr__ not leaking xprv
        assert b32_xprv.get_children(derivation_path='0', index_start=0, index_end=1)[
                   0].__repr__() == XPRV_FIRST_CHILD_REPR
        assert b32_xprv.get_children(derivation_path='0', index_start=1, index_end=2)[
                   0].__repr__() == XPRV_SECOND_CHILD_REPR
        assert b32_xprv.get_children(derivation_path='0', index_start=2, index_end=3)[
                   0].__repr__() == XPRV_THIRD_CHILD_REPR
        # xpub __repr__
        assert b32_xpub.get_children(derivation_path='0', index_start=0, index_end=1)[
                   0].__repr__() == XPUB_FIRST_CHILD_REPR
        assert b32_xpub.get_children(derivation_path='0', index_start=1, index_end=2)[
                   0].__repr__() == XPUB_SECOND_CHILD_REPR
        assert b32_xpub.get_children(derivation_path='0', index_start=2, index_end=3)[
                   0].__repr__() == XPUB_THIRD_CHILD_REPR
        # check that addresses are correct for child xpub and xprv
        for i, key in enumerate(b32_xprv.get_children(derivation_path='0', index_start=0, index_end=3)):
            assert CHILD_ADDRESSES[i] == key.address()
        for i, key in enumerate(b32_xpub.get_children(derivation_path='0', index_start=0, index_end=3)):
            assert CHILD_ADDRESSES[i] == key.address()
