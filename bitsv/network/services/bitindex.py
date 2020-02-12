import json

import requests

from bitsv.network import currency_to_satoshi
from bitsv.network.meta import Unspent


class BitIndex:

    @staticmethod
    def get_balance(address):
        """Gets utxos for given legacy address"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        r = requests.get('https://api.mattercloud.net/api/v2/addrs/balance?address={}'.format(address),
                         headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_txs(address):
        """Gets utxos for given legacy address"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        r = requests.get('https://api.mattercloud.net/api/v2/addrs/txs?address={}'.format(address), headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_tx(tx):
        """Gets utxos for given legacy address"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        r = requests.get('https://api.mattercloud.net/api/v2/tx/{}'.format(tx), headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_utxo(address):
        """gets utxos for given address BitIndex api"""
        json_payload = json.dumps({"addrs": address})

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post('https://api.mattercloud.net/api/addrs/utxo', data=json_payload, headers=headers)
        r.raise_for_status()
        return [Unspent(amount=currency_to_satoshi(tx['amount'], 'bsv'),
                        script=tx['scriptPubKey'],
                        txid=tx['txid'],
                        txindex=tx['vout'],
                        confirmations=tx['confirmations']) for tx in r.json()]

    @staticmethod
    def broadcast_rawtx(rawtx):
        """broadcasts a create_rawtx as hex to network via BitIndex api"""
        json_payload = json.dumps({"hex": rawtx})

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        r = requests.post('https://api.mattercloud.net/api/v2/tx/send', data=json_payload, headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def xpub_register(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.post('https://api.mattercloud.net/api/v2/xpub/register?xpub={}'.format(xpub),
                          headers=headers)
        return r

    @staticmethod
    def get_xpub_status(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.mattercloud.net/api/v2/xpub/status?xpub={}'.format(xpub),
                         headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_xpub_balance(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.mattercloud.net/api/v2/xpub/balance?xpub={}'.format(xpub),
                         headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_xpub_utxos(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.mattercloud.net/api/v2/xpub/utxos?xpub={}'.format(xpub),
                         headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def get_xpub_tx(xpub, api_key):
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'api_key': api_key
        }
        r = requests.get('https://api.mattercloud.net/api/v2/xpub/txs?xpub={}'.format(xpub),
                         headers=headers)
        r.raise_for_status()
        return r.json()
