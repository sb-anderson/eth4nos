var targetBlockNum = 10000;

// transaction counts per block (hard coded) (from block 3,000,000 ~ to block 3,000,100)
var txNums = [6,0,0,7,0,2,2,5,8,0,0,14,2,2,0,10,4,0,8,0,6,1,2,2,3,2,6,3,3,1,4,2,0,0,1,4,0,0,14,0,12,0,0,5,2,0,0,3,0,0,15,13,0,10,0,4,2,0,0,0,0,0,0,0,29,4,13,4,3,0,0,18,0,0,11,0,2,1,1,10,2,3,2,0,8,0,5,0,0,0,32,16,0,0,7,1,12,1,6,0,5]

// make blockchain
for (var blockNum = 1; blockNum <= targetBlockNum; blockNum++) {

  // # of tx in a block
  var txNum = txNums[blockNum-1]

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
