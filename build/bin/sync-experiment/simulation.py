from web3 import Web3
import sys
import socket
import os
import time

# Settings
FULL_PORT = "8081"
SYNC_PORT = "8084"
SYNC_READY_PORT = "8085"
FULL_READY_PORT = "8084"
FULL_KILL_PORT  = "8086"
FULL_ADDR = "147.46.115.21"
DB_PATH = "/data/eth4nos_300000/db_fast/"

# Sync settings for directory names
SYNC_CLIENT = sys.argv[1] # prefix for db directory name. e.g. "eth4nos_fast", "eth4nos_compact"
SYNC_NUMBER = int(sys.argv[2])

# Boundaries and Path
#sync_boundaries = [40383, 80703, 121023, 161343, 201663, 241983, 282303]
sync_boundaries = [161343, 201663, 241983, 282303]

# Providers
fullnode = Web3(Web3.HTTPProvider("http://" + FULL_ADDR + ":" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))

# Functions
def main():
    for i in range(len(sync_boundaries)):
        # run full node
        started = fullNode(sync_boundaries[i])
        while not started:
            started = fullNode(sync_boundaries[i])
        enode = fullnode.geth.admin.nodeInfo()['enode']
        while enode.find("127.0.0.1") != -1:
            enode = fullnode.geth.admin.nodeInfo()['enode']
        # Create log directory
        dir_name = SYNC_CLIENT + "_" + str(sync_boundaries[i])
        print("Make directory [", DB_PATH + dir_name + "_log", "]")
        Cmd = "mkdir -p " + DB_PATH + dir_name + "_log"
        os.system(Cmd)
        # Fast sync for SYNC_NUMBER times
        for j in range(SYNC_NUMBER):
            start_sync = time.time()
            synced = fastSync(enode, dir_name, sync_boundaries[i],j)
            while not synced:
                # try to keep fast sync while 3 hour
                if time.time() - start_sync >= 10800:
                    break
                synced = fastSync(enode, dir_name, sync_boundaries[i],j)
        # kill full node
        killed = killFullNode("kill")
        while not killed:
            killed = killFullNode(sync_boundaries[i])
        #Cmd = "fuser -k " + FULL_PORT + "/tcp"
        #os.system(Cmd)

def killFullNode(message):
    print("Send kill signal to full node")
    try:
        # connecting to the full node ready server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("147.46.115.21", int(FULL_KILL_PORT)))
        s.send(bytes(str(message), 'utf8'))
        return True
    except Exception as e:
        print(e)
        return False

def fullNode(syncBoundary):
    print("Start Full Node For SyncBoundary : " + str(syncBoundary))
    try:
        # connecting to the full node ready server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect((FULL_ADDR, int(FULL_READY_PORT)))
        s.send(bytes(str(syncBoundary), 'utf8'))
        # check fullnode provider connection
        connected = fullnode.isConnected()
        while not connected:
            connected = fullnode.isConnected()
        return True
    except Exception as e:
        print(e)
        return False

def fastSync(enode, dirName, syncBoundary, n):
    print("Start "+ str(n) + "th fast sync")
    file_name = SYNC_CLIENT + "_" + str(syncBoundary) + "_" + str(n)
    try:
        # connecting to the fast sync server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect(("localhost", int(SYNC_READY_PORT)))
        s.send(bytes(dirName + "," + file_name + "," + str(syncBoundary), 'utf8'))
        # check syncnode provider connection
        connected = syncnode.isConnected()
        while not connected:
            connected = syncnode.isConnected()
	# wait until start sync
        syncnode.geth.admin.addPeer(enode)
        syncdone = syncnode.eth.syncing
        while syncdone is False:
            syncnode.geth.admin.addPeer(enode)
            syncdone = syncnode.eth.syncing
        # wait until whole fast sync done and terminate
        while connected:
            connected = syncnode.isConnected()
        return True
    except Exception as e:
        print(e)
        return False

if __name__ == "__main__":
    main()
    print("DONE")
