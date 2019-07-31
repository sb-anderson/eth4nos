targetBlockNum = 10000;
accountsNum = 500;
activeAccountsNum = 50;
sizeCheckEpoch = 1000;
storageFolder = "/home/jmlee/go/src/github.com/eth4nos/go-ethereum/build/bin/dataa/geth/chaindata"
epoch = 500;

activeAccounts = []

const Web3 = require("web3");
const getSize = require('get-folder-size')
var exec = require("child_process").exec, child;

const provider = "http://localhost:8877";
const web3 = new Web3(provider);

// unlock accounts (until exit geth)
/*for (var i = 0; i < accountsNum; i++) {
  personal.unlockAccount(eth.accounts[i], "1234", 0);
}*/

// send transactions
for (var blockNum = 1; blockNum <= targetBlockNum; blockNum++) {

  // # of tx in a block
  var txNum = 1



  // send transactions
  for (var i = 0; i < txNum; i++){
    SendTransaction()
    //eth.sendTransaction({from:eth.accounts[0], to:eth.accounts[1], value: web3.toWei(0.05, "ether"), gas:21000}); // for test
  }

  // check storage size
  web3.eth.getBlockNumber(function (error, result) {
    if(!error) {
      console.log(result);
      res.send("It is me");
    }

    if (result % sizeCheckEpoch == 0){
      /*getSize(storageFolder, (err, size) => {
        if (err) { throw err; }
       
        console.log(size + ' bytes');
        console.log((size / 1024 / 1024).toFixed(2) + ' MB');
      });*/

      child = exec('df -h',
      function (error, stdout, stderr) {
          console.log('stdout: ' + stdout);
          console.log('stderr: ' + stderr);
          if (error !== null) {
              console.log('exec error: ' + error);
          }
      });
      child();



    }

  })

  if (blockNum % epoch == 0){
    SetActiveAccounts()
  }


}

var activeIndex = 0

function SendTransaction(){


  web3.eth.getAccounts().then(accounts => {
    var address = accounts[0];
    var password = "1234"
    web3.eth.personal.unlockAccount(address, password, 0).then(() => {
      web3.eth.sendTransaction({
            from: address,
            to: "0x0123456789012345678901234567890123456789",
            value: 1,
            gas: 21000000,
            data: "0x" + toHexString(rlped),
        }, function (err, hash) {
            console.log("> txHash   : ", hash);
        });
    });
  });

  // increase activeIndex
  activeIndex++
  if (activeIndex > activeAccounts.length){
    activeIndex = 0
  }

}

var activeCount = 25
function SetActiveAccounts(){
  activeAccounts = []
  
  for (var i = 0; i < 25; i++){
   activeAccounts.splice(-1,0,i)
  }

  for (var i = activeCount; i < activeCount+25; i++){
    activeAccounts.splice(-1,0,i)
   }

   activeCount += 25
}