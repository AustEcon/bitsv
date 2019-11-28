from collections import OrderedDict
from decimal import ROUND_DOWN
from functools import wraps
from time import time

import requests

from bitsv.utils import Decimal
from bitsv.constants import SATOSHI, uBSV, mBSV, BSV

DEFAULT_CACHE_TIME = 60

# Constant for use in deriving exchange
# rates when given in terms of 1 BSV.
ONE = Decimal(1)

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

# "https://www.freeforexapi.com/api/live" - 208 supported currencies at this api. Only 20 of the main ones listed here.
USD_PAIRS = {
    'eur': "EUR",
    'gbp': "GBP",
    'jpy': "JPY",
    'cny': "CNY",
    'cad': "CAD",
    'aud': "AUD",
    'nzd': "NZD",
    'rub': "RUB",
    'brl': "BRL",
    'chf': "CHF",
    'sek': "SEK",
    'dkk': "DKK",
    'isk': "ISK",
    'pln': "PLN",
    'hkd': "HKD",
    'krw': "KRW",
    'sgd': "SGD",
    'thb': "THB",
    'twd': "TWD",
    'clp': "CLP"
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


class BitcoinSVRates:
    # Would be better if this were HTTPS as rate information can be used
    # maliciously.
    SINGLE_RATE = 'http://bitcoinsv-rates.com/api/rates/'

    @classmethod
    def currency_to_satoshi(cls, currency):
        r = requests.get(cls.SINGLE_RATE + currency)
        r.raise_for_status()
        rate = r.json()['value']
        return int(ONE / Decimal(rate) * BSV)

    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover
        return cls.currency_to_satoshi('usd')

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


class Bitfinex(BitcoinSVRates):

    # Will use the usd/bsv rate from Bitfinex to then calculate the foreign exchange (fx) rates using another api:
    BITFINEX_BSVUSD_ENDPOINT = "https://api.bitfinex.com/v1/pubticker/bsvusd"
    EXCHANGERATEAPI_ENDPOINT = "https://api.exchangerate-api.com/v4/latest/USD"

    # Overwrites BitcoinSVRates method
    @classmethod
    def currency_to_satoshi(cls, currency):
        if currency == 'usd':
            return cls.usd_to_satoshi()
        # Get satoshi / usd rate
        satoshis_per_usd = cls.usd_to_satoshi()

        # Get fx rate / usd rate
        r = requests.get(cls.EXCHANGERATEAPI_ENDPOINT)
        r.raise_for_status()
        fx_rate = r.json()['rates'][USD_PAIRS[currency]]

        # calculate satoshis / fx rate
        satoshis_per_fx_rate = Decimal(satoshis_per_usd) * (Decimal(1) / Decimal(fx_rate))
        return satoshis_per_fx_rate

    # Overwrite BitcoinSVRates method
    @classmethod
    def usd_to_satoshi(cls):  # pragma: no cover
        # Special case - Uses Bitfinex to get the USD rate
        r = requests.get(cls.BITFINEX_BSVUSD_ENDPOINT)
        r.raise_for_status()
        usdbsv = r.json()['mid']
        # Get satoshis per usd
        rate = Decimal(BSV) / Decimal(usdbsv)
        return rate


class RatesAPI:
    """Each method converts exactly 1 unit of the currency to the equivalent
    number of satoshi.
    """
    IGNORED_ERRORS = (requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout)

    USD_RATES = [Bitfinex.usd_to_satoshi]
    EUR_RATES = [Bitfinex.eur_to_satoshi]
    GBP_RATES = [Bitfinex.gbp_to_satoshi]
    JPY_RATES = [Bitfinex.jpy_to_satoshi]
    CNY_RATES = [Bitfinex.cny_to_satoshi]
    HKD_RATES = [Bitfinex.hkd_to_satoshi]
    CAD_RATES = [Bitfinex.cad_to_satoshi]
    AUD_RATES = [Bitfinex.aud_to_satoshi]
    NZD_RATES = [Bitfinex.nzd_to_satoshi]
    RUB_RATES = [Bitfinex.rub_to_satoshi]
    BRL_RATES = [Bitfinex.brl_to_satoshi]
    CHF_RATES = [Bitfinex.chf_to_satoshi]
    SEK_RATES = [Bitfinex.sek_to_satoshi]
    DKK_RATES = [Bitfinex.dkk_to_satoshi]
    ISK_RATES = [Bitfinex.isk_to_satoshi]
    PLN_RATES = [Bitfinex.pln_to_satoshi]
    KRW_RATES = [Bitfinex.krw_to_satoshi]
    CLP_RATES = [Bitfinex.clp_to_satoshi]
    SGD_RATES = [Bitfinex.sgd_to_satoshi]
    THB_RATES = [Bitfinex.thb_to_satoshi]
    TWD_RATES = [Bitfinex.twd_to_satoshi]

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
