from web3 import Web3
import sys
import socket
import os
import random
import mongoAPI
import json
import rlp
import time
import binascii
import numpy as np
from datetime import datetime

# Log period
#SIZE_CHECK_PERIOD = 100
EPOCH = 40320

# Path
#DB_PATH = "~/data/db_full/"
#DB_LOG_PATH = "./sizelog"
#RSTX_PATH = "./rstxlog"

# Settings
FULL_PORT = "8081"
PASSWORD = "1234"

# Block numbers
START_BLOCK_NUM = int(sys.argv[1]) + 7000000
END_BLOCK_NUM = int(sys.argv[2]) + 7000000

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))

# print now time
#print(datetime.now())

# functions

def main():

    # read restore tx json (restoreAddrs['blockNum'] = address_list)
    f = open("./eth4nos_archive_30_restore_tx.json", 'r')
    restoreAddrs = f.read()
    restoreAddrs = json.loads(restoreAddrs)
    f.close()

    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)

    # set correct START_BLOCK_NUM
    START_BLOCK_NUM = fullnode.eth.blockNumber + 7000001
    print("send transactions to make block", START_BLOCK_NUM, "~", END_BLOCK_NUM)

    # send transactions for each block
    for blockNum in range(START_BLOCK_NUM, END_BLOCK_NUM+1):

        # wait for the block to be mined
        while blockNum > fullnode.eth.blockNumber+7000001:
            pass
        fullnode.geth.miner.stop() # stop mining

        transactions = mongoAPI.findMany('transactions_', ['blockNum'], [blockNum])
        txNumber = len(transactions)

        print("\n")
        print(datetime.now())
        print("block num to send tx:", blockNum)
        print("tx num to send:", txNumber)

        # send txs for next block
        for j in range(txNumber):
            to = transactions[j]['to']
            delegatedFrom = transactions[j]['from']
            #print("send tx -> from:", delegatedFrom, "/ to:", to)
            sendTransaction(to, delegatedFrom)

        # send restore tx
        bn = str(blockNum)
        if bn in restoreAddrs:
            print("rstx num to send:", len(restoreAddrs[bn]))
            print("restore target block:", blockNum-7000000)
            sendRestoreTx(blockNum-7000000, restoreAddrs[bn])
            # for addr in restoreAddrs[bn]:
            #     print("restore tx -> target:", addr)

        # start mining
        fullnode.geth.miner.start(1)

    # wait for the last block to be mined
    while END_BLOCK_NUM != fullnode.eth.blockNumber+7000000:
        pass
    fullnode.geth.miner.stop()
    print("\n")
    print(datetime.now())
    print("All block is mined!")



def sendTransaction(to, delegatedFrom):
    #print("send tx -> from:", delegatedFrom, "/ to:", to)
    while True:
        try:
            fullnode.eth.sendTransaction(
                {'to': to, 'from': fullnode.eth.coinbase, 'value': '0', 'data': delegatedFrom, 'gas': '0'})
            break
        except:
            continue

# def rstxCheck(n, s1, s2, s3):
#     Cmd = "printf \"" + str(n) + " \" >> " + RSTX_PATH
#     os.system(Cmd)
#     Cmd = "printf \"" + str(s1) + " \" >> " + RSTX_PATH
#     os.system(Cmd)
#     Cmd = "printf \"" + str(s2) + " \" >> " + RSTX_PATH
#     os.system(Cmd)
#     Cmd = "printf \"" + str(s3) + "\n\" >> " + RSTX_PATH
#     os.system(Cmd)

# def sizeCheck(n):
#     # (LOG: block# db_size)
#     Cmd = "printf \"" + str(n) + " \" >> " + DB_LOG_PATH
#     os.system(Cmd)
#     Cmd = "du -sc " + DB_PATH + "geth/chaindata | cut -f1 | head -n 1 >> " + DB_LOG_PATH
#     os.system(Cmd)

def sendRestoreTx(currentBlock, addresses):
    latestCheckPoint = currentBlock - (currentBlock % EPOCH) - 1
    latestCheckPoint = 0 if latestCheckPoint < 0 else latestCheckPoint

    rlpeds = list()
    for r, address in enumerate(addresses):
        proofs = list()
        targetBlocks = list(range(latestCheckPoint - EPOCH, 0, -EPOCH))
        print(" restore target address:", address, "/ target blocks:", targetBlocks)
        for targetBlock in targetBlocks:
            proof = fullnode.eth.getProof(
                Web3.toChecksumAddress(address),
                [],
                block_identifier=targetBlock
            )
            # print(" target block num:", targetBlock, "/ raw proof:", proof)
            proofs.append(proof)
            if proof['restored']:
                break

        #print(currentBlock, proofs, targetBlocks)

        # if break when restored = true -> cut out targetBlocks too
        if len(proofs) != len(targetBlocks):
            print("set targetblocks correctly when restored = true")
            targetBlocks = targetBlocks[:len(proofs)]

        proofs.reverse()
        targetBlocks.reverse()

        print("\ntarget block:", currentBlock, "target address:", address)
        print(" print proof before to be compact")
        for i in range(len(proofs)):
            print(" at block:", targetBlocks[i] ,"/ isExist:", not proofs[i]['IsVoid'], "/ isBloom:", proofs[i]['isBloom'])

        """
        Compact Form Proof
        """
        tmps = proofs[:]  # deep copy
        for tmp in tmps:
            if tmp['IsVoid']:
                proofs.pop(0)
                targetBlocks.pop(0)
            else:
                break

        tmps = proofs[:]
        for i, tmp in enumerate(tmps):
            try:
                if (tmps[i + 1])['IsVoid']:
                    break
                else:
                    proofs.pop(0)
                    targetBlocks.pop(0)
            except:
                pass

        preRlp = list()
        preRlp.append(address)
        preRlp.append(0 if len(targetBlocks) == 0 else targetBlocks[0])
        if len(targetBlocks) == 0: # this can happen -> just send target address & 0
            print(" no target block")
            pass

        isBlooms = list()
        for proof in proofs:
            preRlp.append(1 if proof['isBloom'] else 0)
            isBlooms.append(1 if proof['isBloom'] else 0)
            if not proof['isBloom']:
                pfs = proof['accountProof']
                preRlp.append(len(pfs))
                for pf in pfs:
                    preRlp.append(pf)

        # print("> preRlp: ", preRlp)

        rlped = rlp.encode(preRlp)
        # print("> rlped : ", rlped)
        rlpeds.append(len(binascii.hexlify(rlped)))

        print(" print compact proof")
        for i in range(len(proofs)):
            print(" at block:", targetBlocks[i] ,"/ isExist:", not proofs[i]['IsVoid'], "/ isBloom:", proofs[i]['isBloom'])

        sendTransaction("0x0123456789012345678901234567890123456789", rlped)
        print("Restore Tx# {0}".format(r), end="\r")

    return min(rlpeds), max(rlpeds), np.average(rlpeds)


if __name__ == "__main__":
    main()
    print("DONE")
