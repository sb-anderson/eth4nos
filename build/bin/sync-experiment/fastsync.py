import socket,os

# Port
SYNC_PORT           = "8082"
READY_PORT          = "8083"

# Path
GENESIS_PATH   = "../genesis.json"
DB_PATH        = "../data/"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind(("localhost", int(READY_PORT)))  
sock.listen(5)
dir_name = ""
file_name = ""

while True:  
    print("WAIT FAST SYNC....")
    connection, address = sock.accept()
    while True:
        print("wait")
        data = connection.recv(1024)
        if not data:
            print("no data")
            continue
        # decode to unicode string 
        strings = str(data, 'utf8')
        dir_name, file_name = strings.split(",")
        print("done")
        break
    print("START FAST SYNC! [" , file_name, "]")

    # remove old db
    Cmd = "rm -rf " + DB_PATH + dir_name
    os.system(Cmd)
    
    # init fast sync node
    Cmd = "../geth --datadir=\"" + DB_PATH + dir_name + "\" init " + GENESIS_PATH
    os.system(Cmd)

    # run fast sync node
    Cmd = "../geth --datadir \"" + DB_PATH + dir_name + "\" --syncmode \"fast\" --networkid 12345 --rpc --rpcport \"" + SYNC_PORT + "\" --rpccorsdomain \"*\" --port 30304 --nodiscover --rpcapi=\"admin,db,eth,debug,miner,net,shh,txpool,personal,web3\" --ipcdisable console 2>&1 | tee " + dir_name + "/" + file_name + ".txt"
    os.system(Cmd)
    print("FAST SYNC DONE!")
