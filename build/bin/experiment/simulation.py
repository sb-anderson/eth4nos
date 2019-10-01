from web3 import Web3
import sys
import socket
import os
import random
import mongoAPI
import json
import rlp
import time

# Log period
SIZE_CHECK_PERIOD = 100
EPOCH = 40320 #1024

# Path
DB_PATH = "../data/db_full_geth/"
SYNC_DB_PATH = "../data/db_sync_geth/"
DB_LOG_PATH = "./sizelog_geth"
SYNC_LOG_PATH = "./synclog_geth"

# Settings
FULL_PORT = "8084"
SYNC_PORT = "8085"
READY_PORT = "8086"
PASSWORD = "1234"

# Block numbers
START_BLOCK_NUM = int(sys.argv[1])
END_BLOCK_NUM = int(sys.argv[2])

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))
enode = fullnode.geth.admin.nodeInfo()['enode']

# functions
def main():
    print("From block#", START_BLOCK_NUM, " to #", END_BLOCK_NUM)

    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)

    # get current block
    startBlock = fullnode.eth.blockNumber
    currentBlock = fullnode.eth.blockNumber

    # main loop for send txs
    for i in range(START_BLOCK_NUM, END_BLOCK_NUM+1):
        transactions = mongoAPI.findMany('transactions_7ms', ['blockNum'], [i])
        #transactions = mongoAPI.findMany('transactions_15', ['blockNum'], [i])
        txNumber = len(transactions)
        
	# send txs for next block
        print("CURRENT BLOCK #%07d" % currentBlock, end=', ')
        print("NEXT DB_BLOCK #%07d" % i, end=', ')
        print("TX #%05d" % txNumber)

        for j in range(txNumber):
            to = transactions[j]['to']
            delegatedFrom = transactions[j]['from']
            sendTransaction(to, delegatedFrom)
            print("Send Tx# {0}".format(j), end="\r")

        # mining
        fullnode.geth.miner.start(1) # start mining
        while (currentBlock <= startBlock+i-START_BLOCK_NUM):
            currentBlock = fullnode.eth.blockNumber # wait for mining
        fullnode.geth.miner.stop() # stop mining

        # size check
        if currentBlock % SIZE_CHECK_PERIOD == 0:
            sizeCheck(currentBlock)

        # fast sync
        pivotBlockMod = abs(currentBlock-64) % EPOCH
        if pivotBlockMod == EPOCH-1:
            start_sync = time.time()
            synced = fastSync(currentBlock)
            while not synced:
                # try to keep fast sync while 1 hour
                if time.time() - start_sync >= 3600:
                    break
                synced = fastSync(currentBlock)


def sendTransaction(to, delegatedFrom):
    fullnode.eth.sendTransaction(
        {'to': to, 'from': fullnode.eth.coinbase, 'value': '0', 'data': delegatedFrom, 'gas': '0'})


def sizeCheck(n):
    # (LOG: block# db_size)
    Cmd = "printf \"" + str(n) + " \" >> " + DB_LOG_PATH
    os.system(Cmd)
    Cmd = "du -sc " + DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + DB_LOG_PATH
    os.system(Cmd)


def fastSync(n):
    print("FAST SYNC START!")
    try:
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
        while syncdone.knownStates != syncdone.pulledStates or syncdone.knownStates == 0 or syncdone.currentBlock < syncdone.highestBlock - 64:
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
        return True
    except:
        return False

if __name__ == "__main__":
    main()
    print("DONE")
