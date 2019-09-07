import platform, os
from bitcoinrpc.authproxy import AuthServiceProxy

from .insight import BSV_TO_SAT_MULTIPLIER
from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxInput, TxOutput
from pathlib import Path

bitsv_methods = [
    'get_balance',
    'get_transactions',
    'get_transaction',
    'get_unspents',
    'send_transaction'
]

BASE_DIR = Path(__file__).resolve().parent
path_to_standardrpcmethods = Path.joinpath(BASE_DIR, "standardrpcmethods").with_suffix('.txt')

with open(path_to_standardrpcmethods.as_posix(), 'r') as f:
    standardmethods = [lines.strip() for lines in f]


class FullNode:

    # TODO - add exception handling for "BrokenPipeError" --> to reconnect and try once again.

    def __init__(self, conf_dir=None, rpcuser=None, rpcpassword=None, rpcport=None, rpchost='127.0.0.1', network="main"):
        if rpcport is None:
            rpcport = {'main':8332,'test':18332,'stn':9332, 'regtest':18332}[network]
        if conf_dir is None:
            if platform.system() == 'Darwin':
                conf_dir = os.path.expanduser('~/Library/Application Support/Bitcoin/')
            elif platform.system() == 'Windows':
                conf_dir = os.path.join(os.environ['APPDATA'], 'Bitcoin')
            else:
                conf_dir = os.path.expanduser('~/.bitcoin')
        if network == 'test':
            conf_dir = os.path.join(conf_dir, 'testnet3')
        elif network == 'stn':
            conf_dir = os.path.join(conf_dir, 'stn')
        if rpcuser is None:
            cookie = os.path.join(conf_dir, '.cookie')
            with open(cookie) as f:
                rpcuserpass = f.read()

        # Use cookie if no rpcuser specified
        if rpcuser:
            uri = "http://{}:{}@{}:{}".format(rpcuser, rpcpassword, rpchost, rpcport)
        else:
            uri = "http://{}@{}:{}".format(rpcuserpass, rpchost, rpcport)

        self.rpc = AuthServiceProxy(uri)

        rpcnet = self.rpc.getblockchaininfo()['chain']
        if rpcnet != network:
            raise ValueError("rpc server is on '%s' network, you passed '%s'" % (rpcnet, network))
        self.network = network
        self.conf_dir = conf_dir

    def __dir__(self):
        all_methods = []
        all_methods.extend(bitsv_methods)
        all_methods.extend(standardmethods)
        return all_methods

    def __getattr__(self, attr):
        if attr in bitsv_methods:
            return attr
        if attr in standardmethods:
            return getattr(self.rpc, attr)

    def get_balance(self, address):
        return sum(unspent.amount for unspent in self.get_unspents(address))

    def get_transactions(self, address):
        acct = self.rpc.getaccount(address)
        txs = self.rpc.listtransactions(acct)
        txids = (tx['txid'] for tx in txs)
        txids = list(txids)
        return txids

    def get_transaction(self, txid):
        rawtx = self.rpc.getrawtransaction(txid)
        txjson = self.rpc.decoderawtransaction(rawtx)
        inputs = []
        outputs = []
        amount_in = 0
        amount_out = 0
        for vin in txjson['vin']:
            src = self.rpc.getrawtransaction(vin['txid'], True)
            src = self.rpc.decoderawtransaction(src['hex'])
            src = src['vout'][vin['vout']]
            addr = None
            if 'addresses' in src['scriptPubKey']:
                addr = src['scriptPubKey']['addresses'][0]
            amount = int((src['value'] * BSV_TO_SAT_MULTIPLIER).normalize())
            amount_in += amount
            part = TxInput(addr, amount)
            inputs += [part]

        for vout in txjson['vout']:
            addr = None
            if 'addresses' in vout['scriptPubKey']:
                addr = vout['scriptPubKey']['addresses'][0]
            amount = int((vout['value'] * BSV_TO_SAT_MULTIPLIER).normalize())
            amount_out += amount
            part = TxOutput(addr, amount, asm=vout['scriptPubKey']['asm'])
            outputs += [part]

        tx = Transaction(txjson['txid'], amount_in, amount_out)
        for part in inputs:
            tx.add_input(part)
        for part in outputs:
            tx.add_output(part)
        return tx

    def get_unspents(self, address):
        unspents = self.rpc.listunspent(0, 9999999, [address], True)
        return [Unspent(
            amount=int((tx['amount'] * BSV_TO_SAT_MULTIPLIER).normalize()),
            confirmations=tx['confirmations'],
            script=tx['scriptPubKey'],
            txid=tx['txid'],
            txindex=tx['vout']
        ) for tx in unspents]

    def send_transaction(self, tx_hex):
        return self.rpc.sendrawtransaction(tx_hex, True)
