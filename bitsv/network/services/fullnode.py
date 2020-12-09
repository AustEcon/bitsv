import platform
import os
from functools import wraps
from bitcoinrpc.authproxy import AuthServiceProxy
from bitsv.constants import BSV
from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxInput, TxOutput
from .standardrpcmethods import standard_methods

BSV_TO_SAT_MULTIPLIER = BSV

bitsv_methods = [
    'get_balance',
    'get_transaction',
    'get_unspents',
    'broadcast_tx',
    'rpc_connect',
    'rpc_reconnect'
]


class FullNode:

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

        if network == 'regtest':
            conf_dir = os.path.join(conf_dir, 'regtest')
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

        self.network = network
        self.conf_dir = conf_dir
        self.uri = uri
        self.rpc = AuthServiceProxy(self.uri)
        self.rpcport = rpcport
        self.rpchost = rpchost
        self.network = network

        rpcnet = self.rpc.getblockchaininfo()['chain']
        if rpcnet != network:
            raise ValueError("rpc server is on '%s' network, you passed '%s'" % (rpcnet, network))

    def __getattr__(self, rpc_method):
        return RPCMethod(rpc_method, self)

    def __dir__(self):
        fulllist = []
        fulllist.extend(bitsv_methods)
        fulllist.extend(standard_methods)
        fulllist.extend(self.__dict__.keys())
        return fulllist

    def rpc_connect(self):
        return AuthServiceProxy(self.uri)

    def rpc_reconnect(self):
        self.rpc = AuthServiceProxy(self.uri)

    class Decorators:

        @classmethod
        def handle_broken_pipe(cls, f):
            @wraps(f)
            def reconnect_if_needed(self, *args, **kwargs):
                try:
                    return f(self, *args, **kwargs)
                except BrokenPipeError:
                    self.rpc_reconnect()  # reconnect and try again
                    return f(self, *args)

            return reconnect_if_needed

    @Decorators.handle_broken_pipe
    def get_balance(self, address):
        return sum(unspent.amount for unspent in self.get_unspents(address))

    @Decorators.handle_broken_pipe
    def get_transaction(self, txid):
        rawtx = self.rpc.getrawtransaction(txid)
        txjson = self.rpc.decoderawtransaction(rawtx)
        inputs = []
        outputs = []
        amount_in = 0
        amount_out = 0
        for vin in txjson['vin']:
            if vin.get('coinbase'):
                raise NotImplementedError("Handling of coinbase transaction inputs not implemented")
            else:
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

    @Decorators.handle_broken_pipe
    def get_unspents(self, address):
        unspents = self.rpc.listunspent(0, 9999999, [address], True)
        return [Unspent(
            amount=int((tx['amount'] * BSV_TO_SAT_MULTIPLIER).normalize()),
            confirmations=tx['confirmations'],
            txid=tx['txid'],
            txindex=tx['vout']
        ) for tx in unspents]

    @Decorators.handle_broken_pipe
    def get_bestblockhash(self):
        tips = self.rpc.getchaintips()
        return self.rpc.getblockchaininfo()['bestblockhash']

    @Decorators.handle_broken_pipe
    def get_block(self, hash):
        block = self.rpc.getblock(1)
        return Block(block['hash'], block['height'], block['previousblockhash'], block['nextblockhash'], block['tx'])

    @Decorators.handle_broken_pipe
    def broadcast_tx(self, tx_hex):
        return self.rpc.sendrawtransaction(tx_hex, True)


class RPCMethod:
    def __init__(self, rpc_method, host):
        self._rpc_method = rpc_method
        self._host = host

    def __getattr__(self, rpc_method):
        if rpc_method in standard_methods:
            return RPCMethod(rpc_method, self._host)
        else:
            raise AttributeError("No such method: {} exists".format(rpc_method))

    def __call__(self, *args):
        try:
            result = getattr(self._host.rpc, self._rpc_method)(*args)
            return result
        except BrokenPipeError:  # TODO add logging
            self._host.rpc = self._host.rpc_connect()  # reconnect and try again
            result = getattr(self._host.rpc, self._rpc_method)(*args)
            return result
