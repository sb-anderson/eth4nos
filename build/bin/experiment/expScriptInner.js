var targetBlockNum = 100000;

// transaction counts per block (hard coded) (from block 7,000,001 ~ to block 7,100,000)
loadScript('./experiment/transactionCountPerBlock_7000001_7100000.json') // same as var txNums = [...]

// make blockchain
for (var blockNum = 1; blockNum <= targetBlockNum; blockNum++) {

  // # of tx in a block
  var txNum = txNums[blockNum-1]

  // wait for tx
  console.log("wait for txs")
  var ptxCount = 0
  /*while(eth.pendingTransactions.length < txNum) {
    if (eth.pendingTransactions.length>ptxCount){
      ptxCount = eth.pendingTransactions.length
      console.log("pending tx count: ", ptxCount)
    }
  }*/
  while(txpool.status.pending < txNum) {
    if (txpool.status.pending > ptxCount){
      ptxCount = txpool.status.pending
      //console.log("InnerJS: at block", blockNum, ", wait for transactions (", txpool.status.pending, "/", txNum, ")")
    }
  }
  console.log("all tx received. start mining")

  // make 1 block
  miner.start()
  while(eth.blockNumber < blockNum) {}
  miner.stop()
  console.log("successfully mined a block")
}

