# Bitcoin SV has very low fees. 1 sat / byte is basically garaunteed
# to be included in the next block. Default is therefore set to 1 sat / byte
DEFAULT_FEE_FAST = 4
DEFAULT_FEE_MEDIUM = 2
DEFAULT_FEE_SLOW = 0.5

# FIXME: Need to add in a fees API. Issue #1
# URL = 'https://bitcoincashfees.earn.com/api/v1/fees/recommended'

FEE_SPEED_FAST = 'fast'
FEE_SPEED_MEDIUM = 'medium'
FEE_SPEED_SLOW = 'slow'


# FIXME: Not sure if this is better, bools are better, or creating its
# own type is better.
def get_fee(speed=FEE_SPEED_SLOW):
    """Gets the recommended satoshi per byte fee.

    :param speed: One of: 'fast', 'medium', 'slow'.
    :type speed: ``string``
    :rtype: ``float``
    """
    if speed == FEE_SPEED_FAST:
        return DEFAULT_FEE_FAST
    elif speed == FEE_SPEED_MEDIUM:
        return DEFAULT_FEE_MEDIUM
    elif speed == FEE_SPEED_SLOW:
        return DEFAULT_FEE_SLOW
    else:
        raise ValueError('Invalid speed argument.')
