import decimal
from binascii import hexlify


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
