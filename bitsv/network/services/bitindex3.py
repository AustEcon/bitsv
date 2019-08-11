import json
import requests

from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxInput, TxOutput
from decimal import Decimal

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

    def get_unspents(self, address, sort=False, sort_direction='asc'):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: Address to get utxos for
        :type address: ``str``
        :param sort_direction: 'desc' or 'asc' to sort unspents by descending/ascending order respectively
        :param sort: True or False indicates if unspents should be sorted unsorted (ignores sort_direction parameter)
        :rtype: ``list`` of :class:`~bitsv.network.meta.Unspent`
        """
        if sort and sort_direction == 'asc':
            params = {'sort': 'value:asc'}
        elif sort and sort_direction == 'desc':
            params = {'sort': 'value:desc'}
        else:
            params = {'sort': None}

        r = requests.post(
            'https://api.bitindex.network/api/v3/{}/addrs/utxo'.format(self.network),
            params=params,
            data=json.dumps({'addrs': address}),
            headers=self.headers,
        )
        r.raise_for_status()
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
            'https://api.bitindex.network/api/v3/{}/addr/{}'.format(self.network, address),
            headers=self.headers,
        )
        r.raise_for_status()
        return r.json()['balanceSat']

    def get_transactions(self, address):
        """
        Get a list of txids for a given address

        :param address: Address to get balances for
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/addr/{}'.format(self.network, address),
            headers=self.headers,
        )
        r.raise_for_status()
        return r.json()['transactions']

    def get_transactions_detailed(
        self,
        address,
        from_index=0,
        to_index=0,
        no_asm=True,
        no_script=True,
        no_spent=True,
    ):
        """
        Retrieve detailed information about transaction history for an address

        :param address: Address to get transactions for
        :param from_index:
        :param to_index:
        :param no_asm: Default: True
        :param no_script: Default: True
        :param no_spent: Default: True
        """
        r = requests.post(
            'https://api.bitindex.network/api/v3/{}/addrs/txs'.format(self.network),
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
        r.raise_for_status()
        return r.json()

    def send_transaction(self, raw_transaction):
        """
        Sends a transaction to the network

        :param raw_transaction: The raw transaction
        """
        r = requests.post(
            'https://api.bitindex.network/api/v3/{}/tx/send'.format(self.network),
            data=json.dumps({'rawtx': raw_transaction}),
            headers=self.headers,
        )
        r.raise_for_status()
        return r.json()

    def get_transaction(self, transaction_id):
        """
        Gets a single transaction

        :param transaction_id: The transaction ID
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/tx/{}'.format(self.network, transaction_id),
            headers=self.headers,
        )
        r.raise_for_status()
        response = r.json()
        response_vin = response['vin']
        response_vout = response['vout']

        # get txid
        txid = response['txid']

        # get amount_in
        running_total_vin = 0
        for i in response_vin:
            running_total_vin += int(i['valueSat'])
        amount_in = running_total_vin

        # get amount_out
        running_total_vout = 0
        for i in response_vout:
            running_total_vout += int(i['valueSat'])
        amount_out = running_total_vout

        tx = Transaction(txid,
                         amount_in,
                         amount_out)

        # add TxInputs
        for txin in response_vin:
            part = TxInput(txin['addr'], txin['valueSat'])
            tx.add_input(part)

        # add TxOutputs
        for txout in response_vout:
            addr = None
            if 'addresses' in txout['scriptPubKey'] and \
                    txout['scriptPubKey']['addresses'] is not None:
                addr = txout['scriptPubKey']['addresses'][0]

            part = TxOutput(addr,
                            txout['valueSat'],
                            txout['scriptPubKey']['asm'])
            tx.add_output(part)

        return tx

    def raw_get_transaction(self, transaction_id):
        """raw version of get_transaction(). Gives un-altered return value of API
        (useful for debugging)"""
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/tx/{}'.format(self.network, transaction_id),
            headers=self.headers,
        )
        r.raise_for_status()
        return r.json()

    def get_raw_transaction(self, transaction_id):
        """
        Gets a single transaction as a raw string

        :param transaction_id: The transaction ID
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/rawtx/{}'.format(self.network, transaction_id),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_network_status(self, query=None):
        """
        Gets the network status

        :param query: The type of status to query. Can be 'getInfo', 'getDifficulty', 'getBestBlockHash', or 'getLastBlockHash'.
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/status'.format(self.network),
            params={'q': query},
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_block_hash_by_height(self, height):
        """
        Get block hash by height

        :param height: Block height
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/block-index/{}'.format(self.network, height),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_block(self, block_hash):
        """
        Get block

        :param block_hash: Block hash
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/block/{}'.format(self.network, block_hash),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_raw_block(self, block_hash):
        """
        Get raw block

        :param block_hash: Block hash
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/rawblock/{}'.format(self.network, block_hash),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_next_address(self, xpub, reserve_time=None):
        """
        Get next unused address pair for xpub

        :param xpub: Xpub to query utxos
        :param reserve_time: Time in seconds to reserve xpub before it will be handed out again (optional)
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/xpub/{}/addrs/next'.format(self.network, xpub),
            params={'reserveTime': reserve_time},
            headers=self.authorized_headers,
        )
        r.raise_for_status()
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
            'https://api.bitindex.network/api/v3/{self.network}/xpub/{xpub}/addrs'.format(self.network, xpub),
            params={
                'offset': offset,
                'limit': limit,
                'order': order,
                'address': address,
            },
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_xpub_status(self, xpub):
        """
        Get status and balance for xpub

        :param xpub: Xpub to query utxos
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/xpub/{}/status'.format(self.network, xpub),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_xpub_utxos(self, xpub, sort=None):
        """
        Get utxos for xpub

        :param xpub: Xpub to query utxos
        :param sort: Format is 'field:asc' such as 'value:desc' to sort by value descending
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/xpub/{}/utxo'.format(self.network, xpub),
            params={'sort': sort},
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_xpub_transactions(self, xpub):
        """
        Get transaction history for xpub

        :param xpub: Xpub to query utxos
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/xpub/{}/txs'.format(self.network, xpub),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_webhook_config(self):
        """
        Get the configured webhook endpoint
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/webhook/endpoint'.format(self.network),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def update_webhook_config(self, url, enabled, secret):
        """
        Update webhook endpoint confirmation

        :param url: Url to callback when monitored address or xpub has a payment
        :param enabled: Whether webhooks are enabled or disabled
        :param secret: Secret parameter passed back to your API for security purposes
        """
        r = requests.put(
            'https://api.bitindex.network/api/v3/{}/webhook/endpoint'.format(self.network),
            data=json.dumps({
                'url': url,
                'enabled': enabled,
                'secret': secret,
            }),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def get_webhook_monitored_addresses(self):
        """
        Get monitored addresses and xpubs
        """
        r = requests.get(
            'https://api.bitindex.network/api/v3/{}/webhook/monitored_addrs'.format(self.network),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
        return r.json()

    def update_webhook_monitored_addresses(self, address):
        """
        Update monitored addresses and xpubs

        :param address: Address or xpub key to track and monitor
        """
        r = requests.put(
            'https://api.bitindex.network/api/v3/{}/webhook/monitored_addrs'.format(self.network),
            data=json.dumps({'addr': address}),
            headers=self.authorized_headers,
        )
        r.raise_for_status()
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
