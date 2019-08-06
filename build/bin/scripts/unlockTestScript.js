// unlock accounts (until exit geth)
  console.log("unlock 0")
  personal.unlockAccount(eth.accounts[0], "1234", 0);
  console.log("unlock 999")
  personal.unlockAccount(eth.accounts[999], "1234", 0);

// send transactions
  blockNum = eth.blockNumber+1
  console.log("Send from 0 to 999")
  eth.sendTransaction({from:eth.accounts[0], to:eth.accounts[999], value: web3.toWei(0.05, "ether"), gas:21000}); // for test

// mining
  miner.start()
  while(eth.blockNumber < blockNum) {}
  miner.stop()

// send transactions
  blockNum = eth.blockNumber+1
  console.log("Send from 999 to 998")
  eth.sendTransaction({from:eth.accounts[999], to:eth.accounts[998], value: web3.toWei(0.01, "ether"), gas:21000}); // for test

// mining
  miner.start()
  while(eth.blockNumber < blockNum) {}
  miner.stop()
