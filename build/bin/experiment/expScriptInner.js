targetBlockNum = 10000;
personal.unlockAccount(eth.accounts[0], "1234", 0);

// make blockchain
for (var blockNum = 1; blockNum <= targetBlockNum; blockNum++) {

  // # of tx in a block
  var txNum = 1

  // wait for tx
  console.log("wait for txs")
  var ptxCount = 0
  while(eth.pendingTransactions.length < txNum) {
    if (eth.pendingTransactions.length>ptxCount){
      ptxCount = eth.pendingTransactions.length
      console.log("pending tx count: ", ptxCount)
    }
  }
  console.log("tx received. start mining")

  // make 1 block
  miner.start()
  while(eth.blockNumber < blockNum) {}
  miner.stop()
  console.log("successfully mined a block")
}
