import json
import requests

from bitsv.network.meta import Unspent


class BitIndex3:
    """
    Implements version 3 of the BitIndex API

    :param network: select 'main', 'test', or 'stn'
    :type network: ``str``
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

    def get_utxos(self, address, sort=True, sort_direction='desc'):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: Address to get utxos for
        :type address: ``str``
        :param sort_direction: 'desc' or 'asc' to sort unspents by descending/ascending order respectively
        :param sort: True or False indicates if unspents should be sorted unsorted (ignores sort_direction parameter)
        :rtype: ``list`` of :class:`~bitsv.network.meta.Unspent`
        """
        if sort and sort_direction is 'desc':
            params = {'sort': 'value:desc'}
        elif sort and sort_direction is 'asc':
            params = {'sort': 'value:asc'}
        else:
            params = {'sort': None}

        r = requests.post(
            f'https://api.bitindex.network/api/v3/{self.network}/addrs/utxo',
            params=params,
            data=json.dumps({'addrs': address}),
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

        :param address: Address to get balances for
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/addr/{address}',
            headers=self.headers,
        )
        return r.json()

    def get_transactions(
        self,
        address,
        from_index=0,
        to_index=0,
        no_asm=True,
        no_script=True,
        no_spent=True,
    ):
        """
        Retrieve transactions for an address

        :param address: Address to get transactions for
        :param from_index:
        :param to_index:
        :param no_asm: Default: True
        :param no_script: Default: True
        :param no_spent: Default: True
        """
        r = requests.post(
            f'https://api.bitindex.network/api/v3/{self.network}/addrs/txs',
            data=json.dumps({
                "addrs": address,
                "fromIndex": from_index,
                "toIndex": to_index,
                "noAsm": no_asm,
                "noScript": no_script,
                "noSpent": no_spent,
            }),
            headers=self.headers,
        )
        return r.json()

    def send_transaction(self, raw_transaction):
        """
        Sends a transaction to the network

        :param raw_transaction: The raw transaction
        """
        r = requests.post(
            f'https://api.bitindex.network/api/v3/{self.network}/tx/send',
            data=json.dumps({'rawtx': raw_transaction}),
            headers=self.headers,
        )
        return r.json()

    def get_transaction(self, transaction_id):
        """
        Gets a single transaction

        :param transaction_id: The transaction ID
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/tx/{transaction_id}',
            headers=self.headers,
        )
        return r.json()

    def get_raw_transaction(self, transaction_id):
        """
        Gets a single transaction as a raw string

        :param transaction_id: The transaction ID
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/rawtx/{transaction_id}',
            headers=self.authorized_headers,
        )
        return r.json()

    def get_network_status(self, query=None):
        """
        Gets the network status

        :param query: The type of status to query. Can be 'getInfo', 'getDifficulty', 'getBestBlockHash', or 'getLastBlockHash'.
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/status',
            params={'q': query},
            headers=self.authorized_headers,
        )
        return r.json()

    def get_block_hash_by_height(self, height):
        """
        Get block hash by height

        :param height: Block height
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/block-index/{height}',
            headers=self.authorized_headers,
        )
        return r.json()

    def get_block(self, block_hash):
        """
        Get block

        :param block_hash: Block hash
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/block/{block_hash}',
            headers=self.authorized_headers,
        )
        return r.json()

    def get_raw_block(self, block_hash):
        """
        Get raw block

        :param block_hash: Block hash
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/rawblock/{block_hash}',
            headers=self.authorized_headers,
        )
        return r.json()

    def get_next_address(self, xpub, reserve_time=None):
        """
        Get next unused address pair for xpub

        :param xpub: Xpub to query utxos
        :param reserve_time: Time in seconds to reserve xpub before it will be handed out again (optional)
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/xpub/{xpub}/addrs/next',
            params={'reserveTime': reserve_time},
            headers=self.authorized_headers,
        )
        return r.json()

    def get_xpub_addresses(
        self,
        xpub,
        offset=None,
        limit=1000,
        order='desc',
        address=None,
    ):
        """
        Get addresses for xpub

        :param xpub: Xpub to query utxos
        :param offset: Pagination offset
        :param limit: Pagination size. Default: 1000.
        :param order: Sort order: 'asc' or 'desc'. Default: 'desc'.
        :param address: Filter by a specific address in the xpub
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/xpub/{xpub}/addrs',
            params={
                'offset': offset,
                'limit': 1000,
                'order': order,
                'address': address,
            },
            headers=self.authorized_headers,
        )
        return r.json()

    def get_xpub_status(self, xpub):
        """
        Get status and balance for xpub

        :param xpub: Xpub to query utxos
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/xpub/{xpub}/status',
            headers=self.authorized_headers,
        )
        return r.json()

    def get_xpub_utxos(self, xpub, sort=None):
        """
        Get utxos for xpub

        :param xpub: Xpub to query utxos
        :param sort: Format is 'field:asc' such as 'value:desc' to sort by value descending
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/xpub/{xpub}/utxo',
            params={'sort': sort},
            headers=self.authorized_headers,
        )
        return r.json()

    def get_xpub_transactions(self, xpub):
        """
        Get transaction history for xpub

        :param xpub: Xpub to query utxos
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/xpub/{xpub}/txs',
            headers=self.authorized_headers,
        )
        return r.json()

    def get_webhook_config(self):
        """
        Get the configured webhook endpoint
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/webhook/endpoint',
            headers=self.authorized_headers,
        )
        return r.json()

    def update_webhook_config(self, url, enabled, secret):
        """
        Update webhook endpoint confirmation

        :param url: Url to callback when monitored address or xpub has a payment
        :param enabled: Whether webhooks are enabled or disabled
        :param secret: Secret parameter passed back to your API for security purposes
        """
        r = requests.put(
            f'https://api.bitindex.network/api/v3/{self.network}/webhook/endpoint',
            data=json.dumps({
                'url': url,
                'enabled': enabled,
                'secret': secret,
            }),
            headers=self.authorized_headers,
        )
        return r.json()

    def get_webhook_monitored_addresses(self):
        """
        Get monitored addresses and xpubs
        """
        r = requests.get(
            f'https://api.bitindex.network/api/v3/{self.network}/webhook/monitored_addrs',
            headers=self.authorized_headers,
        )
        return r.json()

    def update_webhook_monitored_addresses(self, address):
        """
        Update monitored addresses and xpubs

        :param address: Address or xpub key to track and monitor
        """
        r = requests.put(
            f'https://api.bitindex.network/api/v3/{self.network}/webhook/monitored_addrs',
            data=json.dumps({'addr': address}),
            headers=self.authorized_headers,
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
