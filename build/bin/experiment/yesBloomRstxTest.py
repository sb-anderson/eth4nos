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

#
# command to get all rstx data size for all the blocks
# $ python3 bloomRstxTest.py 7345600 8000000
#

# Log period
EPOCH = 172800

# Settings
FULL_PORT = "8081"
PASSWORD = "1234"

# Block numbers
START_BLOCK_NUM = int(sys.argv[1])
END_BLOCK_NUM = int(sys.argv[2])

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
enode = fullnode.geth.admin.nodeInfo()['enode']

# log file (log file lines mean -> blockNumber rlpedTxDataLength \n)
collectedDataPath = "./collectedData/"
logFileName = "test_rstx_data_size_log_yes_bloom"
logFile = open(collectedDataPath + logFileName + ".txt", "a+")
logFile.write("\n") # it means the start of this python file

# functions

def main():
    f = open("./mapper.json", 'r')
    mapper = f.read()
    mapper = json.loads(mapper)
    f.close()

    print("From block#", START_BLOCK_NUM, " to #", END_BLOCK_NUM)

    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)

    # get current block
    # startBlock = fullnode.eth.blockNumber
    # currentBlock = fullnode.eth.blockNumber

    # main loop for send txs
    for currentBlock in range(START_BLOCK_NUM-7000001, END_BLOCK_NUM-7000001+1):
        if currentBlock % 1000 == 0:
            print("current block number:", currentBlock)
        # transactions = mongoAPI.findMany('transactions_7ms', ['blockNum'], [i])
        # txNumber = len(transactions)
        # print("tx number: ", txNumber)

        # send txs for next block
        # print("CURRENT BLOCK #%07d" % currentBlock, end=', ')
        # print("NEXT DB_BLOCK #%07d" % i, end=', ')
        # print("TX #%05d" % txNumber, end=', ')
        # print("RESTORE #%05d" % len(mapper[currentBlock]))

        # for j in range(txNumber):
        #     to = transactions[j]['to']
        #     delegatedFrom = transactions[j]['from']
        #     sendTransaction(to, delegatedFrom)
        #     print("Send Tx# {0}".format(j), end="\r")

        # restore transaction
        if len(mapper[currentBlock]) == 0:
            # rstxCheck(currentBlock, 0, 0, 0)
            pass
        else:
            sendRestoreTx(currentBlock, mapper[currentBlock])



# def sendTransaction(to, delegatedFrom):
#     while True:
#         try:
#             syncnode.eth.sendTransaction(
#                 {'to': to, 'from': fullnode.eth.coinbase, 'value': '0', 'data': delegatedFrom, 'gas': '0'})
#             break
#         except:
#             continue



def sendRestoreTx(currentBlock, addresses):
    #print("send rstx")
    latestCheckPoint = currentBlock - (currentBlock % EPOCH) - 1
    latestCheckPoint = 0 if latestCheckPoint < 0 else latestCheckPoint

    rlpeds = list()
    for r, address in enumerate(addresses):
        proofs = list()
        targetBlocks = list(range(latestCheckPoint - EPOCH, 0, -EPOCH))
        for targetBlock in targetBlocks:
            proof = fullnode.eth.getProof(
                Web3.toChecksumAddress(address),
                [],
                block_identifier=targetBlock
            )
            proofs.append(proof)
            if proof['restored']:
                break

        #print(currentBlock, proofs, targetBlocks)
        print("currentBlock: ", currentBlock, "target address: ", address)
        for i in range(len(proofs)):
            print(" at block: ", targetBlocks[i] ," / isVoid: ", proofs[i]['IsVoid'], " / isBloom: ", proofs[i]['isBloom'])
 
        proofs.reverse()
        targetBlocks.reverse()

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
        if len(targetBlocks) == 0:
            #return  # no proofs, do not send rstx
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

        # TODO: write rxts data size log
        # print("type of tx data: ", type(rlped))
        print("	size of tx data: ", len(rlped))
        # print("block num: ", currentBlock, " / length: ", len(rlped))
        # print("isBlooms: ", isBlooms, "\n")
        log = str(currentBlock) + "," + str(len(rlped)) + "\n"
        logFile.write(log)

        # do not send tx, just get data size above
        #sendTransaction("0x0123456789012345678901234567890123456789", rlped)
        #print("Restore Tx# {0}".format(r), end="\r")

    # return min(rlpeds), max(rlpeds), np.average(rlpeds)


if __name__ == "__main__":
    main()
    print("DONE")
