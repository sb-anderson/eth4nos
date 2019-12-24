from web3 import Web3
import sys
#import socket
#import random
#import json
#import rlp
#import time
#import binascii
#import numpy as np
import os,binascii

# Settings
FULL_PORT = "8085"
PASSWORD = "1234"

# Account number
ACCOUNT_NUM = int(sys.argv[1])
TX_PER_BLOCK = 3

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))

# functions
def main():
    print("Insert ", ACCOUNT_NUM, " accounts")

    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)

    # get current block
    currentBlock = fullnode.eth.blockNumber

    print("start sending transactions")
    # main loop for send txs
    accountCnt = 3
    blockNum = 1
    for i in range(int(ACCOUNT_NUM / TX_PER_BLOCK)):

	    # send transactions
        print("send transactions in block ", blockNum)
        blockNum += 1
        for j in range(TX_PER_BLOCK):
            to = Web3.toChecksumAddress(hex(accountCnt*2)[2:].zfill(40))
            print(" address: ", to)
            accountCnt = accountCnt + 1
            sendTransaction(to)
            #print("Send Tx# {0}".format(j), end="\r")
        print("\n")


        # mining
        fullnode.geth.miner.start(1)  # start mining
        while (fullnode.eth.blockNumber == currentBlock):
            pass # just wait for mining
        currentBlock = fullnode.eth.blockNumber
        fullnode.geth.miner.stop()  # stop mining



def sendTransaction(to):
    #print("to: ", to, "/ from: ", fullnode.eth.coinbase)
    delegatedFrom = fullnode.eth.coinbase
    while True:
        try:
            fullnode.eth.sendTransaction(
                {'to': to, 'from': fullnode.eth.coinbase, 'value': '0', 'gas': '0', 'data': delegatedFrom})
            break
        except:
            continue



def makeRandHex():
	randHex = binascii.b2a_hex(os.urandom(20))
	return Web3.toChecksumAddress("0x" + randHex.decode('utf-8'))



if __name__ == "__main__":

    """
    for i in range(1,5):
        addrStr = hex(i)
        print("addrStr: ", addrStr)
        addrStr = addrStr[2:].zfill(40)
        print("addrStr zfill: ", addrStr)
        addr = Web3.toChecksumAddress(addrStr)
        print("addr: ", addr)
    """
    main()
    print("DONE")



