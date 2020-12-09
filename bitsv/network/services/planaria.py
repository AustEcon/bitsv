import json
import requests

PLANARIA_TOKEN_VARNAME = 'PLANARIA_TOKEN'

class Planaria:
    def __init__(self, token):
        self.token = token
        self.headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'token': self.token
        }

    def _query(self, query):
        query = json.dumps(query)
        r = requests.post(
            'https://txo.bitsocket.network/crawl',
            data = query,
            headers = self.headers,
            stream = True
        )
        r.raise_for_status()

        result_hashes = set()

        for line in r.iter_lines():
            yield json.loads(line)
            result_hashes.add(hash(line))

        r = requests.post(
            'https://txo.bitbus.network/block',
            data = query,
            headers = self.headers,
            stream = True
        )
        r.raise_for_status()

        for line in r.iter_lines():
            if result_hashes is not None:
                if hash(line) in result_hashes:
                    continue
                result_hashes = None
            yield json.loads(line)

    # commented out because it doesn't return pre-fork transactions.
    #def get_transactions(self, address):
    #    query = {
    #        'v': 3,
    #        'q': {
    #            'find': {
    #                '$or': [{ 'in.e.a': address}, { 'out.e.a': address }]
    #            },
    #            'project': {
    #                'tx.h': 1
    #            }
    #        }
    #    }
    #    return (result['tx']['h'] for result in self._query(query))


    def get_bitcom_transactions(self, bitcom, address=None):
        query = {
            'v': 3,
            'q': {
                'find': {
                    '$or': [{ 'out.s1': bitcom }, { 'out.s2': bitcom }],
                },
                'project': {
                    'tx.h': 1
                }
            }
        }
        if address is not None:
            query['q']['find']['in.e.a'] = address
        return (result['tx']['h'] for result in self._query(query))
