var targetBlockNum = 10000;
var accountsNum = 500;
var activeAccountsNum = 50;
var sizeCheckEpoch = 1000;
var storageFolder = "/home/jmlee/go/src/github.com/eth4nos/go-ethereum/build/bin/dataa/geth/chaindata"
var epoch = 500;

var activeAccounts = []

const Web3 = require("web3");
const getSize = require('get-folder-size')

const provider = "http://localhost:8877";
const web3 = new Web3(provider);

console.log("start script")

async function foo(blockNum) {
  // # of tx in a block
  var txNum = 1

  // send transactions
  for (var i = 0; i < txNum; i++){
    await SendTransaction()
    //eth.sendTransaction({from:eth.accounts[0], to:eth.accounts[1], value: web3.toWei(0.05, "ether"), gas:21000}); // for test
  }

  // wait for mining
  console.log("waiting for mining")
  var mined = false
  while(true){
    
    await web3.eth.getBlockNumber(function (error, result) {
      if (error){
        console.log("get block number error: ", error)
      }

      if(!error) {
        console.log("block number: ", result);
        //res.send("It is me");
      }

      if (result >= blockNum){
        //console.log("block mined!")
        mined = true
      }
  
    })

    if (mined){
      console.log("block mined!")
      break
    }

  }




  // check storage size
  web3.eth.getBlockNumber(function (error, result) {
    if(!error) {
      console.log("block number: ", result);
      //res.send("It is me");
    }

    if (result % sizeCheckEpoch == 0){
      getSize(storageFolder, (err, size) => {
        if (err) { throw err; }
      
        console.log(size + ' bytes');
        console.log((size / 1024 / 1024).toFixed(2) + ' MB');
      });

    }

  })

  if (blockNum % epoch == 0){
    SetActiveAccounts()
  }
}

(async function() {
  // send transactions
  for (var blockNum = 2; blockNum <= targetBlockNum; blockNum++) {
    await foo(blockNum);
  }
})();




var activeIndex = 0

function SendTransaction(){
  return new Promise((resolve, reject) => {
    console.log("start send transaction")

    web3.eth.getAccounts().then(accounts => {
      console.log("accounts length: ", accounts.length)
      var address = accounts[0];
      var password = "1234"
      web3.eth.personal.unlockAccount(address, password, 0).then(() => {
        web3.eth.sendTransaction({
              from: address,
              to: "0x0123456789012345678901234567890123456999",
              value: 1,
              gas: 21000,
              //data: "0x" + toHexString(rlped),
          }, function (err, hash) {
              if(err) reject();
              console.log("> txHash   : ", hash);
              console.log("send random transaction")
          });
          resolve();
      });
    });
  })

  

  // increase activeIndex
  /*activeIndex++
  if (activeIndex > activeAccounts.length){
    activeIndex = 0
  }*/

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