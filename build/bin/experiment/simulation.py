from web3 import Web3
import sys,socket,os,random
import mongoAPI

# Log period
SIZE_CHECK_PERIOD   = 5
FAST_SYNC_PERIOD    = 1023

# Path
DB_PATH             = "../db/db_full/"
SYNC_DB_PATH        = "../db/db_sync/"
DB_LOG_PATH         = "./sizelog"
SYNC_LOG_PATH       = "./synclog"

# Settings
FULL_PORT           = "8081"
SYNC_PORT           = "8082"
READY_PORT          = "8083"
PASSWORD            = "1234"

# Block numbers
START_BLOCK_NUM     = int(sys.argv[1])
END_BLOCK_NUM       = int(sys.argv[2])

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))
enode = fullnode.geth.admin.nodeInfo()['enode']

# functions
def main():
    print("From block#", START_BLOCK_NUM, " to #", END_BLOCK_NUM)
    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 9223372036)
    # get current block
    startBlock = fullnode.eth.blockNumber
    currentBlock = fullnode.eth.blockNumber
    # main loop for send txs
    for i in range(START_BLOCK_NUM, END_BLOCK_NUM+1):
        transactions = mongoAPI.findMany('transactions_test', i)
        txNumber = len(transactions)
        # send txs for next block
        print("CURRENT BLOCK #", currentBlock, "NEXT DB_BLOCK #", i, ", TX #", txNumber)
        for j in range(txNumber):
            to = transactions[j]['to']
            delegatedFrom = transactions[j]['from']
            sendTransaction(to, delegatedFrom)
            print("\tSend Tx#", j)
        # start mining
        fullnode.geth.miner.start(1)
        # wait for mining
        while (currentBlock <= startBlock+i-START_BLOCK_NUM):
            currentBlock = fullnode.eth.blockNumber
        # stop mining
        fullnode.geth.miner.stop()
        # size check
        if currentBlock % SIZE_CHECK_PERIOD == 0:
            sizeCheck(currentBlock)
        # fast sync
        if currentBlock % FAST_SYNC_PERIOD == 0:
            fastSync(currentBlock)

def sendTransaction(to, delegatedFrom):
    fullnode.eth.sendTransaction({'to': to, 'from': fullnode.eth.coinbase, 'value': '1', 'data': delegatedFrom, 'gas': '210000'})

def sizeCheck(n):
    # (LOG: block# db_size)
    Cmd = "printf \"" + str(n) + " \" >> " + DB_LOG_PATH
    os.system(Cmd)
    Cmd = "du -sc " + DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + DB_LOG_PATH
    os.system(Cmd)

def fastSync(n):
    print("FAST SYNC START!")
    # connecting to the fast sync server 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.connect(("localhost", int(READY_PORT)))
    # check syncnode provider connection
    connected = syncnode.isConnected()
    while not connected:
        connected = syncnode.isConnected()
    # start sync
    syncnode.geth.admin.addPeer(enode)
    # wait until start sync
    syncdone = syncnode.eth.syncing
    while syncdone is False:
        syncdone = syncnode.eth.syncing
    # wait until state sync done
    while syncdone.knownStates != syncdone.pulledStates or syncdone.knownStates == 0:
        syncdone = syncnode.eth.syncing
    print("[FAST SYNC] STATE SYNC DONE!")
    # after state sync done (LOG: block# pulled-states state_db_size total_db_size)
    Cmd = "printf \"" + str(n) + " \" >> " + SYNC_LOG_PATH
    os.system(Cmd)
    Cmd = "printf \"" + str(syncdone.pulledStates) + " \" >> " + SYNC_LOG_PATH
    os.system(Cmd)
    Cmd = "du -sc " + SYNC_DB_PATH + "geth/chaindata | cut -f1 | head -n 1 | tr -d '\n' >> " + SYNC_LOG_PATH
    os.system(Cmd)
    Cmd = "printf \" \" >> " + SYNC_LOG_PATH
    os.system(Cmd)
    # wait until whole fast sync done and terminate
    while connected:
        connected = syncnode.isConnected()
    # after whole fast sync done (LOG: total_db_size)
    Cmd = "du -sc " + SYNC_DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + SYNC_LOG_PATH
    os.system(Cmd)
    print("[FAST SYNC] BLOCK SYNC DONE!")

if __name__ == "__main__":
    main()
    print("DONE")
