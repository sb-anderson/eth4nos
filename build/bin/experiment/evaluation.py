from web3 import Web3
import os

# Log period
SIZE_CHECK_PERIOD   = 5
FAST_SYNC_PERIOD    = 10

# Path
DB_PATH             = "../db/db_full/"
SYNC_DB_PATH        = "../db/db_fast_sync/"
DB_LOG_PATH         = "./sizelog"
SYNC_LOG_PATH       = "./synclog"
SYNC_SCRIPT_PATH    = "./fastsync.js"

# Settings
FULL_PORT           = "8081"
SYNC_PORT           = "8082"
PASSWORD            = "1234"

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))

# This list's length becomes target block number
numOfTx = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]

# functions
def main():
    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD)
    # get starting block number
    startBlock = fullnode.eth.blockNumber
    currentBlock = fullnode.eth.blockNumber
    # main loop for send txs
    for i, n in enumerate(numOfTx[startBlock:]):
        print("i : ", i)
        # send txs for next block
        print("NEXT BLOCK NUM #", currentBlock+1, ", TX #", n)
        for j in range(n):
            sendTransaction()
            #print("\tSend Tx#", j)
        # start mining
        fullnode.geth.miner.start(1)
        # wait for mining
        while (currentBlock <= startBlock+i):
            currentBlock = fullnode.eth.blockNumber
        # stop mining
        fullnode.geth.miner.stop()
        # size check
        if currentBlock % SIZE_CHECK_PERIOD == 0:
            sizeCheck(currentBlock)
        # fast sync
        if currentBlock % FAST_SYNC_PERIOD == 0:
            fastSync(currentBlock)

def sendTransaction():
    # FIXME: data becomes from address???
    fullnode.eth.sendTransaction({'to': '0xd3CdA913deB6f67967B99D67aCDFa1712C293601', 'from': fullnode.eth.coinbase, 'value': '1', 'data': fullnode.eth.coinbase, 'gas': '210000'})

def sizeCheck(n):
    Cmd = "printf \"" + str(n) + " \" >> " + DB_LOG_PATH
    os.system(Cmd)
    Cmd = "du -sc " + DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + DB_LOG_PATH
    os.system(Cmd)

def fastSync(n):
    # remove old db
    Cmd = "rm -rf " + SYNC_DB_PATH
    os.system(Cmd)
    # init fast sync node
    Cmd = "../geth --datadir \"" + SYNC_DB_PATH + "\" init ../genesis.json"
    os.system(Cmd)
    # run fast sync node
    Cmd = "../geth --datadir \"" + SYNC_DB_PATH + "\" --syncmode \"fast\" --networkid 12345 --rpc --rpcport \"" + SYNC_PORT + "\" --rpccorsdomain \"*\" --port 30304 --nodiscover --rpcapi=\"admin,db,eth,debug,miner,net,shh,txpool,personal,web3\" --ipcdisable --preload \"" + SYNC_SCRIPT_PATH + "\" > " + SYNC_LOG_PATH + str(n)
    os.system(Cmd)

if __name__ == "__main__":
    main()
    print("DONE")
