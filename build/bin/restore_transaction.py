from web3 import Web3
import rlp
import sys
import socket
import os
import random
import mongoAPI
import json
from pprint import pprint


# Settings
FULL_PORT = "8081"
SYNC_PORT = "8082"
READY_PORT = "8083"
EPOCH = 1024

# providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))
enode = fullnode.geth.admin.nodeInfo()['enode']

if __name__ == "__main__":
    f = open("./mapper.json", 'r')
    mapper = f.read()
    mapper = json.loads(mapper)
    f.close()

    for currentBlock, addresses in enumerate(mapper):
        latestCheckPoint = currentBlock - (currentBlock % EPOCH) - 1
        latestCheckPoint = 0 if latestCheckPoint < 0 else latestCheckPoint

        for address in addresses:
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

            print(currentBlock, proofs, targetBlocks)

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
            for proof in proofs:
                preRlp.append(1 if proof['isBloom'] else 0)
                if not proof['isBloom']:
                    pfs = proof['accountProof']
                    preRlp.append(len(pfs))
                    for pf in pfs:
                        preRlp.append(pf)

            print("> preRlp: ", preRlp)

            rlped = rlp.encode(preRlp)
            print("> rlped : ", rlped)

            sys.exit()
