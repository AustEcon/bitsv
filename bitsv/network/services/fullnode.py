import platform, os

from bitcoinrpc.authproxy import AuthServiceProxy
from cashaddress import convert as cashaddress

from .insight import BSV_TO_SAT_MULTIPLIER
from bitsv.network.meta import Unspent
from bitsv.network.transaction import Transaction, TxPart

class FullNode:

    def __init__(self, conf_dir=None, rpcuserpass=None, rpcport=None, rpchost='127.0.0.1', network="main"):
        if rpcport is None:
            rpcport = {'main':8332,'test':18332,'stn':9332}[network]
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
        if rpcuserpass is None:
            cookie = os.path.join(conf_dir, '.cookie')
            with open(cookie) as f:
                rpcuserpass = f.read()

        uri = "http://%s@%s:%s" % (rpcuserpass, rpchost, rpcport)
        self.rpc = AuthServiceProxy(uri)
        rpcnet = self.rpc.getblockchaininfo()['chain']
        if rpcnet != network:
            raise ValueError("rpc server is on '%s' network, you passed '%s'" % (rpcnet, network))
        self.network = network
        self.conf_dir = conf_dir

    def get_balance(self, address):
        print('get_balance')
        return sum(unspent.amount for unspent in self.get_unspents(address))

    def get_transactions(self, address):
        acct = self.rpc.getaccount(address)
        txs = self.rpc.listtransactions(acct)

        txs = filter(
            lambda tx: 'address' in tx and
                cashaddress.to_legacy_address(tx['address']) == address,
            txs)
        txids = (tx['txid'] for tx in txs)
        txids = list(dict.fromkeys(txids))
        txids.reverse()
        return txids

    def get_transaction(self, txid):
        txsum = self.rpc.gettransaction(txid, True)
        txdet = self.rpc.decoderawtransaction(txsum['hex'])
        inputs = []
        outputs = []
        amtin = 0
        amtout = 0
        for vin in txdet['vin']:
            src = self.rpc.gettransaction(vin['txid'], True)
            src = self.rpc.decoderawtransaction(src['hex'])
            src = src['vout'][vin['vout']]
            addr = None
            if 'addresses' in src['scriptPubKey']:
                addr = cashaddress.to_legacy_address(src['scriptPubKey']['addresses'][0])
            amt = int((src['value'] * BSV_TO_SAT_MULTIPLIER).normalize()),
            amtin += amt
            part = TxPart(addr, amt, asm=vin['scriptSig']['asm'])
            inputs += [part]
        for vout in txdet['vout']:
            addr = None
            if 'addresses' in vout['scriptPubKey']:
                addr = cashaddress.to_legacy_address(vout['scriptPubKey']['addresses'][0])
            amt = int((vout['value'] * BSV_TO_SAT_MULTIPLIER).normalize()),
            amtout -= amt
            part = TxPart(addr, amt, asm=vout['scriptPubKey']['asm'])
            outputs += [part]
        tx = Transaction(txjson['txid'], txjson['blockhash'], amtin, amtout, amtin - amtout)
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
