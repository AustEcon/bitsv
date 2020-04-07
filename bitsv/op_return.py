OP_PUSHDATA1 = b'\x4c'
OP_PUSHDATA2 = b'\x4d'
OP_PUSHDATA4 = b'\x4e'

MESSAGE_LIMIT = 100000  # The real limiting factor seems to be total transaction size


def get_op_pushdata_code(data):
    length_data = len(data)
    if length_data < 0x4c:  # (https://en.bitcoin.it/wiki/Script)
        return length_data.to_bytes(1, byteorder='little')
    elif length_data <= 0xff:
        return OP_PUSHDATA1 + length_data.to_bytes(1, byteorder='little')  # OP_PUSHDATA1 format
    elif length_data <= 0xffff:
        return OP_PUSHDATA2 + length_data.to_bytes(2, byteorder='little')  # OP_PUSHDATA2 format
    else:
        return OP_PUSHDATA4 + length_data.to_bytes(4, byteorder='little')  # OP_PUSHDATA4 format


def create_pushdata(list_of_pushdata):
    '''
    Adds the correct 'op_pushdata' op_codes for each pushdata element to include in op_return as one bytestream.
    :param list_of_pushdata: Can be either a list of bytes (new syntax) or a list of tuples (old syntax for deprecation)
    :param list_of_pushdata: ``list`` of ``bytes``
    :return: bytes

    if list of tuples is passed:
    - is of the form:
    [('Hello', 'utf-8'),
    ('deadbeef', 'hex'),
    (b'')]
    '''

    assert isinstance(list_of_pushdata, list), "list_of_pushdata must be of type: list"
    assert isinstance(list_of_pushdata[0], bytes) or isinstance(list_of_pushdata[0], tuple), \
        "must provide either a) a list of bytes or b) a list of tuples"

    # New syntax -  simple list of bytes
    if isinstance(list_of_pushdata[0], bytes):
        pushdata = b''
        for data in list_of_pushdata:
            pushdata += get_op_pushdata_code(data) + data
        return pushdata

    # Old syntax - list of tuples
    elif isinstance(list_of_pushdata[0], tuple):

        pushdata = b''

        for i in range(len(list_of_pushdata)):

            encoding = list_of_pushdata[i][1]
            if encoding == 'utf-8':
                assert isinstance(list_of_pushdata[i][0], str), "must be of type: string"
                pushdata += get_op_pushdata_code(list_of_pushdata[i][0]) + list_of_pushdata[i][0].encode('utf-8')

            elif encoding == 'hex':
                if len(list_of_pushdata[i][0]) % 2 != 0:
                    raise ValueError(
                        "hex encoded pushdata must have length = a multiple of two. May need to add a leading zero")

                elif len(list_of_pushdata[i][0]) % 2 == 0:
                    assert isinstance(list_of_pushdata[i][0], str), "must be of type: string"
                    hex_as_bytes = bytes.fromhex(list_of_pushdata[i][0])
                    pushdata += get_op_pushdata_code(hex_as_bytes) + hex_as_bytes

            elif encoding == 'bytes':
                assert isinstance(list_of_pushdata[i][0], bytes), "must be of type: bytes"
                pushdata += get_op_pushdata_code(list_of_pushdata[i][0]) + list_of_pushdata[i][0]

        # Size limit now 100kb on SV - aka "the unfuckening of OP_RETURN"
        # Courtesy Steve Shadders and SV miners 24th Jan 2019
        # https://www.yours.org/content/the-unfuckening-of-op_return-b10d2c4b52da
        if len(pushdata) > MESSAGE_LIMIT:
            raise ValueError(
                "Total bytes in OP_RETURN cannot exceed 100kb at present - apologies")

        return pushdata
