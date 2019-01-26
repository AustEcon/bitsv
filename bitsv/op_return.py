from bitsv import utils


OP_PUSHDATA1 = b'\x4c'
OP_PUSHDATA2 = b'\x4d'
OP_PUSHDATA4 = b'\x4e'


def get_op_pushdata_code(data):
    length_data = len(data)
    if length_data <= 0x4c:  # (https://en.bitcoin.it/wiki/Script)
        return length_data.to_bytes(1, byteorder='little')
    elif length_data <= 0xff:
        return OP_PUSHDATA1 + length_data.to_bytes(1, byteorder='little')  # OP_PUSHDATA1 format
    elif length_data <= 0xffff:
        return OP_PUSHDATA2 + length_data.to_bytes(2, byteorder='little')  # OP_PUSHDATA2 format
    else:
        return OP_PUSHDATA4 + length_data.to_bytes(4, byteorder='little')  # OP_PUSHDATA4 format


def create_pushdata(lst_of_pushdata):
    """
    Creates encoded OP_RETURN pushdata as bytes Returns binary encoded OP_RETURN pushdata (automatically adds
    intervening OP_CODES specifying number of bytes in each pushdata element) 0x6a (i.e. OP_RETURN) is added in
    other, auxiliary functions; only pushdata is returned here. Max 220 bytes of pushdata

    Parameters
    ----------
    lst_of_pushdata : a list of tuples (pushdata, encoding) where encoding is either "hex" or "utf-8"

    Returns
    -------
    pushdata : bytes

    Examples
    --------

    lst_of_pushdata =  [('6d01', 'hex'),
                        ('bitPUSHER', 'utf-8')]

    as per memo.cash protocol @ https://memo.cash/protocol this results in a "Set name" action to "bitPUSHER"

    raw OP_RETURN will be:

        0e 6a 02 6d01 09 626974505553484552

            0e                  - 14 bytes to follow (in hex)
            6a                  - OP_RETURN
            02                  - 2 bytes of pushdata to follow
            6d01                - "communication channel" for memo.cash - "set name" action
            09                  - 9 bytes to follow
            626974505553484552  - "bitPUSHER" utf-8 encoded bytes --> hex representation

    Currently (this module) only allows up to 220 bytes maximum - as multiple OP_RETURNS in one transaction is
    considered non-standard."""

    pushdata = b''

    for i in range(len(lst_of_pushdata)):

        encoding = lst_of_pushdata[i][1]
        if encoding == 'utf-8':
            pushdata += get_op_pushdata_code(lst_of_pushdata[i][0]) + lst_of_pushdata[i][0].encode('utf-8')

        elif encoding == 'hex' and len(lst_of_pushdata[i][0]) % 2 != 0:
            raise ValueError(
                "hex encoded pushdata must have length = a multiple of two")

        elif encoding == 'hex' and len(lst_of_pushdata[i][0]) % 2 == 0:
            hex_data_as_bytes = utils.hex_to_bytes(lst_of_pushdata[i][0])
            pushdata += get_op_pushdata_code(hex_data_as_bytes) + hex_data_as_bytes

    # check for size
    if len(pushdata) > 220:
        raise ValueError(
            "Total bytes in OP_RETURN cannot exceed 220 bytes at present - apologies")

    return pushdata
