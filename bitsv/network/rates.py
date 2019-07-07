from collections import OrderedDict
from decimal import ROUND_DOWN
from functools import wraps
from time import time

import requests

from bitsv.utils import Decimal

DEFAULT_CACHE_TIME = 60

# Constant for use in deriving exchange
# rates when given in terms of 1 BSV.
ONE = Decimal(1)

# https://en.bitcoin.it/wiki/Units
SATOSHI = 1
uBSV = 10 ** 2
mBSV = 10 ** 5
BSV = 10 ** 8

SUPPORTED_CURRENCIES = OrderedDict([
    ('satoshi', 'Satoshi'),
    ('ubsv', 'Microbitcoincash'),
    ('mbsv', 'Millibitcoincash'),
    ('bsv', 'BitcoinCash'),
    ('usd', 'United States Dollar'),
    ('eur', 'Eurozone Euro'),
    ('gbp', 'Pound Sterling'),
    ('jpy', 'Japanese Yen'),
    ('cny', 'Chinese Yuan'),
    ('cad', 'Canadian Dollar'),
    ('aud', 'Australian Dollar'),
    ('nzd', 'New Zealand Dollar'),
    ('rub', 'Russian Ruble'),
    ('brl', 'Brazilian Real'),
    ('chf', 'Swiss Franc'),
    ('sek', 'Swedish Krona'),
    ('dkk', 'Danish Krone'),
    ('isk', 'Icelandic Krona'),
    ('pln', 'Polish Zloty'),
    ('hkd', 'Hong Kong Dollar'),
    ('krw', 'South Korean Won'),
    ('sgd', 'Singapore Dollar'),
    ('thb', 'Thai Baht'),
    ('twd', 'New Taiwan Dollar'),
    ('clp', 'Chilean Peso')
])

# https://en.wikipedia.org/wiki/ISO_4217
CURRENCY_PRECISION = {
    'satoshi': 0,
    'ubsv': 2,
    'mbsv': 5,
    'bsv': 8,
    'usd': 2,
    'eur': 2,
    'gbp': 2,
    'jpy': 0,
    'cny': 2,
    'cad': 2,
    'aud': 2,
    'nzd': 2,
    'rub': 2,
    'brl': 2,
    'chf': 2,
    'sek': 2,
    'dkk': 2,
    'isk': 2,
    'pln': 2,
    'hkd': 2,
    'krw': 0,
    'sgd': 2,
    'thb': 2,
    'twd': 2,
    'clp': 0
}

PAIRS = {
    'eur': "USDEUR",
    'gbp': "USDGBP",
    'jpy': "USDJPY",
    'cny': "USDCNY",
    'cad': "USDCAD",
    'aud': "USDAUD",
    'nzd': "USDNZD",
    'rub': "USDRUB",
    'brl': "USDBRL",
    'chf': "USDCHF",
    'sek': "USDSEK",
    'dkk': "USDDKK",
    'isk': "USDISK",
    'pln': "USDPLN",
    'hkd': "USDHKD",
    'krw': "USDKRW",
    'sgd': "USDSGD",
    'thb': "USDTHB",
    'twd': "USDTWD",
    'clp': "USDCLP"
}

def set_rate_cache_time(seconds):
    global DEFAULT_CACHE_TIME
    DEFAULT_CACHE_TIME = seconds


def satoshi_to_satoshi():
    return SATOSHI


def ubsv_to_satoshi():
    return uBSV


def mbsv_to_satoshi():
    return mBSV


def bsv_to_satoshi():
    return BSV


def get_satoshi_to_fiat_rate(usd_per_bsv):
    rate = Decimal(100000000) / Decimal(usd_per_bsv)
    return rate


class BitcoinSVRates:
    # Will use the usd price from Bitfinex to then calculate the foreign exchange rates with another api:
    BITFINEX_BSVUSD_ENDPOINT = "https://api.bitfinex.com/v1/pubticker/bsvusd"
    FREEFOREXAPI_ENDPOINT = "https://www.freeforexapi.com/api/live?pairs="

    @classmethod
    def currency_to_satoshi(cls, currency):
        if currency == 'usd':
            return cls.usd_to_satoshi()
        else:
            satoshis_per_usd_rate = cls.usd_to_satoshi()

            # Get usd / fx_rate --> satoshis_per_fx_rate
            r = requests.get(cls.FREEFOREXAPI_ENDPOINT + PAIRS[currency])
            if r.status_code != 200:
                raise requests.exceptions.ConnectionError
            fx_rate = r.json()['rates'][PAIRS[currency]]['rate']

            satoshis_per_fx_rate = Decimal(satoshis_per_usd_rate) * Decimal(1) / Decimal(fx_rate)
            return satoshis_per_fx_rate

    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover
        # Special case - Uses Bitfinex to get the USD rate
        r = requests.get("https://api.bitfinex.com/v1/pubticker/bsvusd")
        if r.status_code != 200:
            raise requests.exceptions.ConnectionError
        usdbsv = r.json()['mid']
        return get_satoshi_to_fiat_rate(usdbsv)

    @classmethod
    def eur_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('eur')

    @classmethod
    def gbp_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('gbp')

    @classmethod
    def jpy_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('jpy')

    @classmethod
    def cny_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('cny')

    @classmethod
    def hkd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('hkd')

    @classmethod
    def cad_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('cad')

    @classmethod
    def aud_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('aud')

    @classmethod
    def nzd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('nzd')

    @classmethod
    def rub_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('rub')

    @classmethod
    def brl_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('brl')

    @classmethod
    def chf_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('chf')

    @classmethod
    def sek_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('sek')

    @classmethod
    def dkk_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('dkk')

    @classmethod
    def isk_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('isk')

    @classmethod
    def pln_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('pln')

    @classmethod
    def krw_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('krw')

    @classmethod
    def clp_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('clp')

    @classmethod
    def sgd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('sgd')

    @classmethod
    def thb_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('thb')

    @classmethod
    def twd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('twd')


class RatesAPI:
    """Each method converts exactly 1 unit of the currency to the equivalent
    number of satoshi.
    """
    IGNORED_ERRORS = (requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout)

    USD_RATES = [BitcoinSVRates.usd_to_satoshi]
    EUR_RATES = [BitcoinSVRates.eur_to_satoshi]
    GBP_RATES = [BitcoinSVRates.gbp_to_satoshi]
    JPY_RATES = [BitcoinSVRates.jpy_to_satoshi]
    CNY_RATES = [BitcoinSVRates.cny_to_satoshi]
    HKD_RATES = [BitcoinSVRates.hkd_to_satoshi]
    CAD_RATES = [BitcoinSVRates.cad_to_satoshi]
    AUD_RATES = [BitcoinSVRates.aud_to_satoshi]
    NZD_RATES = [BitcoinSVRates.nzd_to_satoshi]
    RUB_RATES = [BitcoinSVRates.rub_to_satoshi]
    BRL_RATES = [BitcoinSVRates.brl_to_satoshi]
    CHF_RATES = [BitcoinSVRates.chf_to_satoshi]
    SEK_RATES = [BitcoinSVRates.sek_to_satoshi]
    DKK_RATES = [BitcoinSVRates.dkk_to_satoshi]
    ISK_RATES = [BitcoinSVRates.isk_to_satoshi]
    PLN_RATES = [BitcoinSVRates.pln_to_satoshi]
    KRW_RATES = [BitcoinSVRates.krw_to_satoshi]
    CLP_RATES = [BitcoinSVRates.clp_to_satoshi]
    SGD_RATES = [BitcoinSVRates.sgd_to_satoshi]
    THB_RATES = [BitcoinSVRates.thb_to_satoshi]
    TWD_RATES = [BitcoinSVRates.twd_to_satoshi]

    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.USD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def eur_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.EUR_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def gbp_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.GBP_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def jpy_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.JPY_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def cny_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CNY_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def hkd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.HKD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def cad_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CAD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def aud_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.AUD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def nzd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.NZD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def rub_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.RUB_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def brl_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.BRL_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def chf_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CHF_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def sek_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.SEK_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def dkk_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.DKK_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def isk_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.ISK_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def pln_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.PLN_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def krw_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.KRW_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def clp_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.CLP_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def sgd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.SGD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def thb_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.THB_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def twd_to_satoshi(cls):  # pragma: no cover

        for api_call in cls.TWD_RATES:
            try:
                return api_call()
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')


EXCHANGE_RATES = {
    'satoshi': satoshi_to_satoshi,
    'ubsv': ubsv_to_satoshi,
    'mbsv': mbsv_to_satoshi,
    'bsv': bsv_to_satoshi,
    'usd': RatesAPI.usd_to_satoshi,
    'eur': RatesAPI.eur_to_satoshi,
    'gbp': RatesAPI.gbp_to_satoshi,
    'jpy': RatesAPI.jpy_to_satoshi,
    'cny': RatesAPI.cny_to_satoshi,
    'cad': RatesAPI.cad_to_satoshi,
    'aud': RatesAPI.aud_to_satoshi,
    'nzd': RatesAPI.nzd_to_satoshi,
    'rub': RatesAPI.rub_to_satoshi,
    'brl': RatesAPI.brl_to_satoshi,
    'chf': RatesAPI.chf_to_satoshi,
    'sek': RatesAPI.sek_to_satoshi,
    'dkk': RatesAPI.dkk_to_satoshi,
    'isk': RatesAPI.isk_to_satoshi,
    'pln': RatesAPI.pln_to_satoshi,
    'hkd': RatesAPI.hkd_to_satoshi,
    'krw': RatesAPI.krw_to_satoshi,
    'sgd': RatesAPI.sgd_to_satoshi,
    'thb': RatesAPI.thb_to_satoshi,
    'twd': RatesAPI.twd_to_satoshi,
    'clp': RatesAPI.clp_to_satoshi
}


def currency_to_satoshi(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    satoshis = EXCHANGE_RATES[currency]()
    return int(satoshis * Decimal(amount))


class CachedRate:
    __slots__ = ('satoshis', 'last_update')

    def __init__(self, satoshis, last_update):
        self.satoshis = satoshis
        self.last_update = last_update


def currency_to_satoshi_local_cache(f):
    start_time = time()

    cached_rates = dict([
        (currency, CachedRate(None, start_time)) for currency in EXCHANGE_RATES.keys()
    ])

    @wraps(f)
    def wrapper(amount, currency):
        now = time()

        cached_rate = cached_rates[currency]

        if not cached_rate.satoshis or now - cached_rate.last_update > DEFAULT_CACHE_TIME:
            cached_rate.satoshis = EXCHANGE_RATES[currency]()
            cached_rate.last_update = now

        return int(cached_rate.satoshis * Decimal(amount))

    return wrapper


@currency_to_satoshi_local_cache
def currency_to_satoshi_local_cached():
    pass  # pragma: no cover


def currency_to_satoshi_cached(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`. Results are cached
    using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    return currency_to_satoshi_local_cached(amount, currency)


def satoshi_to_currency(num, currency):
    """Converts a given number of satoshi to another currency as a formatted
    string rounded down to the proper number of decimal places.

    :param num: The number of satoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(EXCHANGE_RATES[currency]())
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )


def satoshi_to_currency_cached(num, currency):
    """Converts a given number of satoshi to another currency as a formatted
    string rounded down to the proper number of decimal places. Results are
    cached using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param num: The number of satoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(currency_to_satoshi_cached(1, currency))
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )
