import decimal
from binascii import hexlify
import string


class Decimal(decimal.Decimal):
    def __new__(cls, value):
        return super().__new__(cls, str(value))


def chunk_data(data, size):
    return (data[i:i + size] for i in range(0, len(data), size))


def int_to_unknown_bytes(num, byteorder='big'):
    """Converts an int to the least number of bytes as possible."""
    return num.to_bytes((num.bit_length() + 7) // 8 or 1, byteorder)


def bytes_to_hex(bytestr, upper=False):
    hexed = hexlify(bytestr).decode()
    return hexed.upper() if upper else hexed


def hex_to_bytes(hexed):

    if len(hexed) & 1:
        hexed = '0' + hexed

    return bytes.fromhex(hexed)


def int_to_hex(num, upper=False):
    """Ensures that there is an even number of characters in the hex string"""
    hexed = hex(num)[2:]
    if len(hexed) % 2 != 0:
        hexed = '0' + hexed
    return hexed.upper() if upper else hexed


def hex_to_int(hexed):
    return int(hexed, 16)


def flip_hex_byte_order(string):
    return bytes_to_hex(hex_to_bytes(string)[::-1])


def int_to_varint(val):

    if val < 253:
        return val.to_bytes(1, 'little')
    elif val <= 65535:
        return b'\xfd'+val.to_bytes(2, 'little')
    elif val <= 4294967295:
        return b'\xfe'+val.to_bytes(4, 'little')
    else:
        return b'\xff'+val.to_bytes(8, 'little')


def sort_utxos_by_txindex(utxos):
    return sorted(utxos, key=lambda utxo: utxo.txindex)


def sort_utxos_by_txid(utxos):
    return sorted(utxos, key=lambda utxo: utxo.txid)


def sort_utxos_by_amount(utxos):
    return sorted(utxos, key=lambda utxo: utxo.amount)


def sort_utxos_by_confirmations(utxos):
    return sorted(utxos, key=lambda utxo: utxo.confirmations)


def is_valid_hex(s):
    """Can only detect if something definitely is *not* hex (could still return true by
    coincidence).
    But in this case all asm op codes begin with "OP_" as per https://en.bitcoin.it/wiki/Script.
    So all return False. The only exception to this is for OP_PUSHDATA codes 1 - 75."""
    return all(c in string.hexdigits for c in s)


def asm_to_list(asm):
    """Takes in Bitcoin Script Assembly code and returns:
    - op_codes (with 'OP_' prefixes) as string
    - raw hex data as bytes.
    """
    asm_list = []
    for pushdata in asm.split(' '):
        if not is_valid_hex(pushdata):
            asm_list.append(pushdata)
        else:
            asm_list.append(hex_to_bytes(pushdata))
    return asm_list
