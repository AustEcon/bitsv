import json
import requests

DEFAULT_TIMEOUT = 30


class WhatsonchainAPI:
    """Only Testnet supported currently. STN may be added soon. Mainnet too."""

    # Whatsonchain for all testnet functions
    TESTNET = 'https://api.whatsonchain.com/v1/bsv/{}'.format('test')
    TESTNET_WOC_STATUS = TESTNET + '/woc'
    TESTNET_GET_BLOCK_BY_HASH = TESTNET + 'block/hash/{}'
    TESTNET_GET_BLOCK_BY_HEIGHT = TESTNET + '/block/height/{}'
    TESTNET_GET_BLOCK_BY_HASH_BY_PAGE = TESTNET + '/block/hash/{}/page/{}'  # Needs .format(hash,page_number)
    TESTNET_GET_TRANSACTION_BY_HASH = TESTNET + '/tx/hash/{}'
    TESTNET_POST_RAWTX = TESTNET + '/tx/raw'  # json payload = {"txHex": "hex..."}

    @classmethod
    def get_woc_status_testnet(cls):
        """returns 'what's on chain' if online"""
        r = requests.get(cls.TESTNET_WOC_STATUS, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.text

    @classmethod
    def get_block_by_hash_testnet(cls, _hash):
        r = requests.get(cls.TESTNET_GET_BLOCK_BY_HASH.format(_hash), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_block_by_height_testnet(cls, _height):
        r = requests.get(cls.TESTNET_GET_BLOCK_BY_HEIGHT.format(_height), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_block_by_hash_by_page_testnet(cls, _hash, page_number):
        """Only to be used for large blocks > 1000 txs. Allows paging through lists of transactions.
        Returns Null if there are not more than 1000 transactions in the block"""
        r = requests.get(cls.TESTNET_GET_BLOCK_BY_HASH_BY_PAGE.format(_hash, page_number), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transaction_by_hash_testnet(cls, _hash):
        r = requests.get(cls.TESTNET_GET_TRANSACTION_BY_HASH.format(_hash), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def broadcast_rawtx_testnet(cls, rawtx):
        # FIXME not actually tested yet
        """Broadcasts a rawtx to testnet"""
        json_payload = json.dumps({"txHex": rawtx})
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post(cls.TESTNET_POST_RAWTX, data=json_payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    # Whatsonchain STN endpoints
    STN = 'https://api.whatsonchain.com/v1/bsv/{}'.format('stn')
    STN_WOC_STATUS = STN + '/woc'
    STN_GET_BLOCK_BY_HASH = STN + 'block/hash/{}'
    STN_GET_BLOCK_BY_HEIGHT = STN + '/block/height/{}'
    STN_GET_BLOCK_BY_HASH_BY_PAGE = STN + '/block/hash/{}/page/{}'  # Needs .format(hash,page_number)
    STN_GET_TRANSACTION_BY_HASH = STN + '/tx/hash/{}'
    STN_POST_RAWTX = STN + '/tx/raw'  # json payload = {"txHex": "hex..."}

    # Whatsonchain mainnet endpoints (included here as may come in handy later)
    MAINNET = 'https://api.whatsonchain.com/v1/bsv/{}'.format('main')
    MAINNET_WOC_STATUS = MAINNET + '/woc'
    MAINNET_GET_BLOCK_BY_HASH = MAINNET + 'block/hash/{}'
    MAINNET_GET_BLOCK_BY_HEIGHT = MAINNET + '/block/height/{}'
    MAINNET_GET_BLOCK_BY_HASH_BY_PAGE = MAINNET + '/block/hash/{}/page/{}'  # Needs .format(hash,page_number)
    MAINNET_GET_TRANSACTION_BY_HASH = MAINNET + '/tx/hash/{}'
    MAINNET_POST_RAWTX = STN + '/tx/raw'  # json payload = {"txHex": "hex..."}
