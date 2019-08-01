/* 
 * Values for Ethereum Linear Model
 */
const S = 0.01; // Scale factor
const ACCOUNTS_NUM = 50000 * S, BLOCK_NUM = 1000000 * S; // Number of final accounts, block number
const BIG_EPOCH = 50000 * S, SMALL_EPOCH = 1000 * S; // Epoch model
const EPOCH = BIG_EPOCH; // Choosed epoch
const SIZE_CHECK_EPOCH = EPOCH / 100 // Size check epoch

const A = ACCOUNTS_NUM / BLOCK_NUM; // Gradient of linear block-accounts model (y = Ax)
const B = EPOCH * A; // Number of newly active accounts for unit epoch 
const C = 2 * B; // Number of total active accounts (y = C) for unit epoch

const PATH = "../db/db_full/geth/chaindata"; // DB directory

/*
 * Initialize Requirements & Variable
 */
const Web3 = require("web3");
const { exec } = require("child_process");
const provider = "http://localhost:8081";
const web3 = new Web3(provider);

var activeCount = B; // initial start index
var currentBlockNum = 0; // current block number
var activeAccounts = []; // Array for active accounts
SetActiveAccounts(); // Initialize



/*
 * Functions
 */

// Run experiment
(async function() {
  // check start block number
  await web3.eth.getBlockNumber(function (error, result) {
    if (error) {
      console.log("get block number error: ", error)
    }
    else {
      currentBlockNum = result
    }
  });

  // send transactions
  console.log("START BLOCK NUM : #", currentBlockNum)
  while (currentBlockNum <= BLOCK_NUM) {
    await sendAndWait(currentBlockNum);
  }
})();

// Experiment function
async function sendAndWait(blockNum) {
  var txNum = 1 // # of tx in a block
  
  // send transactions
  for (var i = 0; i < txNum; i++) {
    await SendTransaction()
  }

  // wait for mining
  console.log("waiting for mining")
  var mined = false
  while(true){
    await web3.eth.getBlockNumber(function (error, result) {
      if (error) {
        console.log("get block number error: ", error)
      }
      else {
        //console.log("block number : ", result)
      }

      if (result > blockNum){
	currentBlockNum = result // Update current block number
        mined = true
      }
    }) 
    if (mined) {
      console.log("block #", currentBlockNum, " mined!")
      break;
    }
  }

  // Set active accounts right before sweeping
  if (currentBlockNum % EPOCH == EPOCH-1) {
    SetActiveAccounts()
  }
      
  // Check storage size every epoch before sweeping
  if (currentBlockNum % SIZE_CHECK_EPOCH == 0) {
    exec('printf \"#' + currentBlockNum + '	\" >> log')
    exec('du -sch ' + PATH + ' | cut -f1 | head -n 1 >> log')
  }
}


function SendTransaction(){
  return new Promise((resolve, reject) => {
    console.log("start send transaction")

    // Pick random `from` and random `to` in activeAccounts array
    var randFromIndex = 0, randToIndex = 0;
    while (randToIndex == randFromIndex) {
      randFromIndex = activeAccounts[Math.floor((Math.random() * (C-1)))]; // range 0 to C-1
      randToIndex = activeAccounts[Math.floor((Math.random() * (C-1)))]; // range 0 to C-1
    }

    // Send Transaction
    web3.eth.getAccounts().then(accounts => {
      //var fromAddress = accounts[randFromIndex];
      var fromAddress = accounts[0];
      var toAddress = accounts[randToIndex];
      var password = "1234"
      console.log("From ", fromAddress, " to ", toAddress)
      web3.eth.personal.unlockAccount(fromAddress, password, 0).then(() => {
        web3.eth.sendTransaction({
            from: fromAddress,
            to: toAddress,
            value: 1,
            gas: 21000,
        }, function (err, hash) {
	    if (err) {
              console.log(err)
              reject()
	    }
	    console.log("> txHash   : ", hash);
        });
            resolve();
      });
    });
  })
}

function SetActiveAccounts(){
  activeAccounts = [] // Reset array

  // Add previous accounts
  for (var i = 0; i < B; i++) {
   activeAccounts.push(i)
  }

  // Add new accounts
  for (var i = activeCount; i < activeCount + B; i++) {
    activeAccounts.push(i)
  }

  // Update activeCount value
  activeCount += B
}

function toHexString(byteArray) {
  return Array.from(byteArray, function (byte) {
    return ('0' + (byte & 0xFF).toString(16)).slice(-2);
  }).join('')
}
