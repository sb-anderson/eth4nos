from web3 import Web3
import sys
import socket
import os
import time

# Settings
FULL_PORT = "8081"
SYNC_PORT = "8082"
READY_PORT = "8083"

# Sync settings for directory names
SYNC_CLIENT = sys.argv[1] # 1:Geth(Original) 2:Geth(No tx,receipts) 3:Eth4nos
SYNC_BOUNDARY = sys.argv[2]
SYNC_NUMBER = int(sys.argv[3])

# Paths
DIR_NAME = "log-" + SYNC_CLIENT + "-" + SYNC_BOUNDARY + "-" + str(SYNC_NUMBER)

# Providers
fullnode = Web3(Web3.HTTPProvider("http://localhost:" + FULL_PORT))
syncnode = Web3(Web3.HTTPProvider("http://localhost:" + SYNC_PORT))
enode = fullnode.geth.admin.nodeInfo()['enode']

# Functions
def main():
    # Create log directory
    print("Make directory [", DIR_NAME, "]")
    Cmd = "mkdir " + DIR_NAME
    os.system(Cmd)

    # Fast sync for SYNC_NUMBER times
    for i in range(SYNC_NUMBER):
        start_sync = time.time()
        synced = fastSync(i)
        while not synced:
            # try to keep fast sync while 3 hour
            if time.time() - start_sync >= 10800:
                break
            synced = fastSync(i)

def fastSync(n):
    print("Start "+ str(n) + "th fast sync")
    file_name = "log-" + SYNC_CLIENT + "-" + SYNC_BOUNDARY + "-" + str(n)
    try:
        # connecting to the fast sync server 
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.connect(("localhost", int(READY_PORT)))
        s.send(bytes(DIR_NAME + "," + file_name + "," + SYNC_BOUNDARY, 'utf8'))
        # check syncnode provider connection
        connected = syncnode.isConnected()
        while not connected:
            connected = syncnode.isConnected()
        # start sync
        syncnode.geth.admin.addPeer(enode)
        # wait until whole fast sync done and terminate
        while connected:
            connected = syncnode.isConnected()
        return True
    except:
        return False

if __name__ == "__main__":
    main()
    print("DONE")
