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
    LIMIT = 150000
    EPOCH = 1024

    res = [0 for _ in range(LIMIT)]

    active_accounts = mongoAPI.findMany('active_accounts_15', [], [])
    for active_account in active_accounts:
        restore_blocks = active_account['restoreBlock']
        for restore_block in restore_blocks:
            if restore_block - BASE < 2 * EPOCH - 1:
                pass
            else:
                res[restore_block - BASE] = res[restore_block - BASE] + 1

    # print(res)
    with open("./restore_list.json", 'w') as f:
        f.write(json.dumps(res))

    print("DONE")
