import socket,os

# Port
FULL_PORT          = "8081"
FULL_KILL_PORT     = "8086"
FULL_ADDR          = "147.46.115.21"

# Path
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
sock.bind((FULL_ADDR, int(FULL_KILL_PORT)))  
sock.listen(5)

while True:  
    print("WAIT CONNECTION")
    connection, address = sock.accept()
    while True:
        print("connected!", "(connection:", connection, ", address:", address, ")")
        data = connection.recv(1024)
        if not data:
            print("no data")
            break
        # decode to unicode string 
        message = str(data, 'utf8')
        print("signal received : ", message)
        if message == "kill":
            # kill port here
            Cmd = "fuser -k " + FULL_PORT + "/tcp"
            os.system(Cmd)
            print("killed")
        else:
            print("wrong message. not kill. re-wait.")
        break
