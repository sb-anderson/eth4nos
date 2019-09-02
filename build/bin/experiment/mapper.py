from web3 import Web3
import sys,socket,os,random
import mongoAPI
from pprint import pprint
import json


if __name__ == "__main__":
    # transaction = mongoAPI.findMany(
    #     'transactions_15',
    #     ['blockNum', 'transactionIndex'],
    #     [7000001, 1]
    # )
    # pprint(transaction)

    # active_account = mongoAPI.findMany(
    #     'active_accounts_15',
    #     ['address'],
    #     ['0xFBb1b73C4f0BDa4f67dcA266ce6Ef42f520fBB98']
    # )
    # pprint(active_account)

    BASE = 7000001
    LIMIT = 1000000
    EPOCH = 172800

    res = [[] for _ in range(LIMIT)]

    active_accounts = mongoAPI.findMany('activeaccounts_7ms', [], [])
    for active_account in active_accounts:
        restore_blocks = active_account['restoreBlocks']
        for restore_block in restore_blocks:
            if restore_block - BASE < 2 * EPOCH - 1:
                pass
            else:
                res[restore_block - BASE].append(active_account['address'])

    # print(res)
    with open("./mapper.json", 'w') as f:
        f.write(json.dumps(res))

    print("DONE")
