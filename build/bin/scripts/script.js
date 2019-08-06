personal.unlockAccount(eth.accounts[0], "1234", 0);
personal.newAccount()
personal.unlockAccount(eth.accounts[1], "1234", 0);
eth.sendTransaction({from:eth.accounts[0], to:eth.accounts[1], value: web3.toWei(0.05, "ether"), gas:21000});
miner.start()
while (eth.blockNumber <= 4) {}
eth.sendTransaction({from:eth.accounts[1], to:eth.accounts[0], value: web3.toWei(0.01, "ether"), gas:21000});
while (eth.blockNumber <= 14) {}
if (eth.blockNumber > 14) {
  miner.stop()
}
