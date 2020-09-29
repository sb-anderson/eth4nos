import socket,os

# Port
FULL_PORT           = "8081"
FULL_READY_PORT     = "8084"
FULL_ADDR           = "147.46.115.21"

# Path
GENESIS_PATH   = "../genesis.json"
DB_PATH        = "/data/eth4nos_archive_30/db_full"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind((FULL_ADDR, int(FULL_READY_PORT)))  
sock.listen(5)

sync_boundaries = ["80703", "121023", "161343", "201663", "241983", "282303"]

while True:  
    print("WAIT....")
    connection, address = sock.accept()
    while True:
        print("connected!", "(connection:", connection, ", address:", address, ")")
        data = connection.recv(1024)
        if not data:
            print("no data")
            break
            #continue
        # decode to unicode string 
        message = str(data, 'utf8')
        if message in sync_boundaries:
            sync_boundary = message
    	    # run full node
            print("START FULL NODE! [ SyncBoundary : " , sync_boundary, "]")
            Cmd = "../geth --datadir \"" + DB_PATH + "\" --ethash.dagdir \"" + DB_PATH + "_ethash\" --keystore \"../keystore\" --gcmode archive --networkid 12345 --rpc --rpcaddr \"" + FULL_ADDR + "\" --rpcport \"" + FULL_PORT + "\" --rpccorsdomain \"*\" --port 30303 --rpcapi=\"admin,db,eth,debug,miner,net,shh,txpool,personal,web3\" --allow-insecure-unlock --syncboundary " + sync_boundary + " console"
            os.system(Cmd)
            print("FULL NODE DONE!")
        else:
            print("wrong message. do not run geth. re-wait. (messages = ", message, ")")
        break
