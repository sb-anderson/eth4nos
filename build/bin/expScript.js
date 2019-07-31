targetBlockNum = 5;
accountsNum = 1;
sizeCheckEpoch = 1;
//storageFolder = "/home/jmlee/go/src/github.com/eth4nos/go-ethereum/build/bin/dataa/geth/chaindata"
//import getSize from 'get-folder-size';

// unlock accounts (until exit geth)
for (var i = 0; i < accountsNum; i++) {
  personal.unlockAccount(eth.accounts[i], "1234", 0);
}

// create and unlock account for test (TODO: delete this)
personal.newAccount()
personal.unlockAccount(eth.accounts[1], "1234", 0);

// make blockchain
for (var blockNum = 1; blockNum <= targetBlockNum; blockNum++) {
  //var txNum = GetBlockTxNum(blockNum)
  var txNum = blockNum // for test

  // send transactions
  for (var i = 0; i < txNum; i++){
    //SendTransaction()
    eth.sendTransaction({from:eth.accounts[0], to:eth.accounts[1], value: web3.toWei(0.05, "ether"), gas:21000}); // for test
    console.log("pending transaction count:", eth.pendingTransactions.length)
  }

  // make block
  miner.start()
  while(eth.blockNumber < blockNum) {}
  miner.stop()

  // TODO: check storage size
  /*if (blockNum % sizeCheckEpoch == 0) {
    getSize(storageFolder, (err, size) => {
      if (err) { throw err; }
     
      console.log(size + ' bytes');
      console.log((size / 1024 / 1024).toFixed(2) + ' MB');
    });
  }*/

}
