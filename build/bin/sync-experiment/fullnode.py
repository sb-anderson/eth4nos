import socket,os

# Port
FULL_PORT           = "8081"
FULL_READY_PORT     = "8084"

# Path
GENESIS_PATH   = "../genesis.json"
DB_PATH        = "/home/jaeykim/data/geth_300000/db_archive"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind(("localhost", int(FULL_READY_PORT)))  
sock.listen(5)
dir_name = ""
file_name = ""

while True:  
    print("WAIT....")
    connection, address = sock.accept()
    while True:
        print("wait")
        data = connection.recv(1024)
        if not data:
            print("no data")
            continue
        # decode to unicode string 
        sync_boundary = str(data, 'utf8')
        print("done")
        break
    print("START FULL NODE! [ SyncBoundary : " , sync_boundary, "]")

    # run full node
    Cmd = "../geth --datadir \"" + DB_PATH + "\" --ethash.dagdir \"" + DB_PATH + "_ethash\" --keystore \"../keystore\" --gcmode archive --networkid 12345 --rpc --rpcport \"" + FULL_PORT + "\" --rpccorsdomain \"*\" --port 30303 --nodiscover --rpcapi=\"admin,db,eth,debug,miner,net,shh,txpool,personal,web3\" --allow-insecure-unlock --syncboundary " + sync_boundary + " console"
    os.system(Cmd)
    print("FULL NODE DONE!")
