import json

import requests
from cashaddress import convert as cashaddress

from bitsv.network.meta import Unspent


class BitIndex3:
    """
    Implements version 3 of the BitIndex API
    """

    def __init__(self, api_key, network='main'):
        self.api_key = api_key
        self.network = network
        self.headers = self._get_headers()
        self.authorized_headers = self._get_authorized_headers()

    def _get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def _get_authorized_headers(self):
        headers = self._get_headers()
        headers['api_key'] = self.api_key
        return headers

    def get_uxto(self, address):
        """
        Gets utxo's for given legacy address
        """
        address = cashaddress.to_legacy_address(address)
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/addr/{address}/utxo',
            headers=self.headers,
        )
        return [Unspent(
            amount=tx['satoshis'],
            confirmations=tx['confirmations'],
            script=tx['scriptPubKey'],
            txid=tx['txid'],
            txindex=tx['vout'],
        ) for tx in r.json()]

    def get_balance(self, address):
        """
        Get address balances and transaction summary
        """
        address = cashaddress.to_legacy_address(address)
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/addr/{address}',
            headers=self.headers,
        )
        return r.json()

    def get_transactions(
        self,
        address,
        fromIndex=0,
        toIndex=0,
        noAsm=True,
        noScript=True,
        noSpent=True,
    ):
        """
        Retrieve transactions for an address
        """
        address = cashaddress.to_legacy_address(address)
        json_payload = json.dumps({
            "addrs": address,
            "fromIndex": fromIndex,
            "toIndex": toIndex,
            "noAsm": noAsm,
            "noScript": noScript,
            "noSpent": noSpent,
        })
        r = requests.post(
            f'https://api.bitindex.network/api/v3/{self.network}/addrs/txs',
            data=json_payload,
            headers=self.headers,
        )
        return r.json()

    def send_transaction(self, rawtx):
        """
        Sends a transaction to the network
        """
        json_payload = json.dumps({"rawtx": rawtx})
        r = requests.post(
            f'https://api.bitindex.network/api/v3/{self.network}/tx/send',
            data=json_payload,
            headers=self.headers,
        )
        return r.json()

    def get_transaction(self, txid):
        """
        Gets a single transaction
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/tx/{txid}',
            headers=self.headers,
        )
        return r.json()['data']

    def get_raw_transaction(self, txid):
        """
        Gets a single transaction as a raw string
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/rawtx/{txid}',
            headers=self.headers,
        )
        return r.json()['rawtx']

    def get_network_status(self, q='getInfo'):
        """
        Gets the network status

        :param q: The type of status to query.
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/status?q={q}',
            headers=self.headers,
        )
        return r.json()


class BitIndex3MainNet(BitIndex3):
    """
    Implements version 3 of the BitIndex API using the mainnet network
    """

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs, network='main')


class BitIndex3TestNet(BitIndex3):
    """
    Implements version 3 of the BitIndex API using the testnet network
    """

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs, network='test')


class BitIndex3STN(BitIndex3):
    """
    Implements version 3 of the BitIndex API using the STN network
    """

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs, network='stn')
