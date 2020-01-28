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

#
# command to get all rstx data size for all the blocks
# $ python3 noBloomRstxTest.py | tee noBloomLog.txt
#

# Log period
EPOCH = 40320

# Settings
FULL_PORT = "8082"
PASSWORD = "1234"

# Block numbers
# START_BLOCK_NUM = int(sys.argv[1]) + 7000000
# END_BLOCK_NUM = int(sys.argv[2]) + 7000000

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))

# log file
collectedDataPath = "./collectedData/eth4nos_archive_30/"
logFileName = "test_rstx_data_size_log_no_bloom"
logFile = open(collectedDataPath + logFileName + ".txt", "a+")
logFile.write("\nStart logging (targetBlock, targetAddress, txDataSize, proofCount, falsePositiveProofCount)\n") # logging method (false positive count is meaningless in no bloom setting)
logFile.write(str(datetime.now())) 
logFile.write("\n\n") 

# functions

def main():
   
    # read restore tx json (restoreAddrs['blockNum'] = address_list)
    f = open("./eth4nos_archive_30_restore_tx.json", 'r')
    restoreAddrs = f.read()
    restoreAddrs = json.loads(restoreAddrs)
    f.close()

    # unlock coinbase
    fullnode.geth.personal.unlockAccount(fullnode.eth.coinbase, PASSWORD, 0)

    # iterate all rstx
    for targetBlock in restoreAddrs:
        print("target Block:", targetBlock)
        print("rstx num to send:", len(restoreAddrs[targetBlock]))
        print("restore target block:", int(targetBlock)-7000000)
        sendRestoreTx(int(targetBlock)-7000000, restoreAddrs[targetBlock])

    print("\n")
    print(datetime.now())
    print("All rstx is sended")
    logFile.write("\nFinished\n") 
    logFile.write(str(datetime.now())) 



# def sendTransaction(to, delegatedFrom):
#     while True:
#         try:
#             syncnode.eth.sendTransaction(
#                 {'to': to, 'from': fullnode.eth.coinbase, 'value': '0', 'data': delegatedFrom, 'gas': '0'})
#             break
#         except:
#             continue



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
            proofs.append(proof)
            if proof['restored']:
                break

        proofs.reverse()
        targetBlocks.reverse()

        #print(currentBlock, proofs, targetBlocks)
        print("\ntarget block:", currentBlock, "target address:", address)
        print(" not compact proof")
        for i in range(len(proofs)):
            print(" at block:", targetBlocks[i] ,"/ isVoid:", proofs[i]['IsVoid'], "/ isBloom:", proofs[i]['isBloom'])

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

        # count bloom filter false positive case
        proofCount = len(proofs)
        falsePositiveCount = 0
        print(" compact proof")
        for i in range(len(proofs)):
            # if isVoid: True && isBloom: False ==> bloom false positive case
            print(" at block:", targetBlocks[i] ,"/ isVoid:", proofs[i]['IsVoid'], "/ isBloom:", proofs[i]['isBloom'])
            if proofs[i]['IsVoid'] == True and proofs[i]['isBloom'] == False:
                falsePositiveCount = falsePositiveCount + 1
                print("false positive case!")
        print("proof count:", proofCount, "/ false positive count:", falsePositiveCount)

        # write rxts's info log
        print("	size of tx data:", len(rlped))
        log = str(currentBlock) + "," + address + "," + str(len(rlped)) + "," + str(proofCount) + "," + str(falsePositiveCount) + "\n"
        logFile.write(log)

        # do not send tx, just get data size above
        #sendTransaction("0x0123456789012345678901234567890123456789", rlped)
        #print("Restore Tx# {0}".format(r), end="\r")

    # return min(rlpeds), max(rlpeds), np.average(rlpeds)


if __name__ == "__main__":
    main()
    print("DONE")
