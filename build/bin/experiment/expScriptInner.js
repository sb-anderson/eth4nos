targetBlockNum = 10000;

// make blockchain
for (var blockNum = 1; blockNum <= targetBlockNum; blockNum++) {

  // # of tx in a block
  var txNum = 1

  // wait for tx
  while(eth.pendingTransactions.length < txNum) {}

  // make 1 block
  miner.start()
  while(eth.blockNumber < blockNum) {}
  miner.stop()

}
