from web3 import Web3
import sys
import socket
import os
import time

# Settings
FULL_PORT = "8084"
SYNC_PORT = "8085"
SYNC_READY_PORT = "8086"
FULL_READY_PORT = "8087"

# Sync settings for directory names
SYNC_CLIENT = sys.argv[1] # 1:Geth(Original) 2:Geth(No tx,receipts) 3:Eth4nos
SYNC_NUMBER = int(sys.argv[2])

# Boundaries and Path
sync_boundaries = [172863, 345663, 518463, 691263, 864063]

# Providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))

# Functions
def main():
    for i in range(len(sync_boundaries)):
        # run full node
        started = fullNode(sync_boundaries[i])
        while not started:
            started = fullNode(sync_boundaries[i])
        enode = fullnode.geth.admin.nodeInfo()['enode']
        # Create log directory
        dir_name = "log-" + SYNC_CLIENT + "-" + str(sync_boundaries[i]) + "-" + str(SYNC_NUMBER)
        print("Make directory [", dir_name, "]")
        Cmd = "mkdir " + dir_name
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
        Cmd = "fuser -k " + FULL_PORT + "/tcp"
        os.system(Cmd)


def fullNode(syncBoundary):
    print("Start Full Node For SyncBoundary : " + str(syncBoundary))
    try:
        # connecting to the full node ready server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect(("localhost", int(FULL_READY_PORT)))
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
    file_name = "log-" + SYNC_CLIENT + "-" + str(syncBoundary) + "-" + str(n)
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
