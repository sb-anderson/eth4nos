from web3 import Web3
import socket,os

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
READY_PORT          = "8083"
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
    print("Start from block#", startBlock)
    # main loop for send txs
    for i, n in enumerate(numOfTx[startBlock:]):
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
    fullnode.eth.sendTransaction({'to': '0xd3CdA913deB6f67967B99D67aCDFa1712C293601', 'from': fullnode.eth.coinbase, 'value': '1', 'data': fullnode.eth.coinbase, 'gas': '210000'})

def sizeCheck(n):
    # (LOG: block# db_size)
    Cmd = "printf \"" + str(n) + " \" >> " + DB_LOG_PATH
    os.system(Cmd)
    Cmd = "du -sc " + DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + DB_LOG_PATH
    os.system(Cmd)

def fastSync(n):
    # connecting to the fast sync server 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect(("localhost", int(READY_PORT)))
    # check syncnode provider connection
    syncdone = None
    while syncdone is None:
        try:
            syncdone = syncnode.eth.syncing
        except:
            pass
    while syncdone is False:
        syncdone = syncnode.eth.syncing
    print("SYNC DONE!")
    # after sync done (LOG: block# total_db_size)
    Cmd = "printf \"" + str(n) + " \" >> " + SYNC_LOG_PATH
    os.system(Cmd)
    Cmd = "du -sc " + SYNC_DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + SYNC_LOG_PATH
    os.system(Cmd)
    # TODO:terminate fast sync node

if __name__ == "__main__":
    main()
    print("DONE")
