import socket,os

# Port
SYNC_PORT           = "8082"
READY_PORT          = "8083"

# Path
GENESIS_PATH        = "../genesis.json"
SYNC_DB_PATH        = "../db/db_sync/"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind(("localhost", int(READY_PORT)))  
sock.listen(5)

while True:  
    # Connection is done after the blockchain is constructed
    print("WAIT FAST SYNC....")
    connection, address = sock.accept()
    print("START FAST SYNC!")

    # remove old db
    Cmd = "rm -rf " + SYNC_DB_PATH
    os.system(Cmd)
    
    # init fast sync node
    Cmd = "../geth --datadir=\"" + SYNC_DB_PATH + "\" init " + GENESIS_PATH
    os.system(Cmd)

    # run fast sync node
    Cmd = "../geth --datadir \"" + SYNC_DB_PATH + "\" --syncmode \"fast\" --networkid 12345 --rpc --rpcport \"" + SYNC_PORT + "\" --rpccorsdomain \"*\" --port 30304 --nodiscover --rpcapi=\"admin,db,eth,debug,miner,net,shh,txpool,personal,web3\" --ipcdisable console"
    os.system(Cmd)
    print("FAST SYNC DONE!")
