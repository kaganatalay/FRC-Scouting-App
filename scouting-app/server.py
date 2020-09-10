import socket
import threading
import time
import pickle

FORMAT = "UTF-8"
PORT = 5555
HEADER = 64
SERVER = ''
ADDR = (SERVER, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = []

data = {}
teams = []
for i in range(14):
    teams.append(f"Team {i+1}")

for team in teams:
    data[team] = ["Waiting For Input", "und", " "]

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    # init
    msg = pickle.dumps(data)
    sendable = bytes(f'{len(msg):<{HEADER}}', FORMAT) + msg
    conn.send(sendable)

    connected = True
    while connected:
        time.sleep(0.5)

        msg = pickle.dumps(data)
        sendable = bytes(f'{len(msg):<{HEADER}}', FORMAT) + msg
        conn.send(sendable)
    conn.close()

def watch_response(conn, addr):
    connected = True
    while connected:
        incoming = conn.recv(1000)
        if incoming:
            incoming_data = pickle.loads(incoming)
            
            for item in incoming_data:
                if(incoming_data[item][1] == "sta"):
                    data[item][0] = incoming_data[item][0]
                elif(incoming_data[item][1] == "val"):
                    data[item] = incoming_data[item]

    conn.close()

def start():
    server.listen()

    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        connection, adress = server.accept()
        clients.append(connection)
        send_ = threading.Thread(target=handle_client, args=(connection, adress))
        send_.start()

        watch_ = threading.Thread(target=watch_response, args=(connection, adress))
        watch_.start()
        print(f"\n[ACTIVE CONNECTIONS] {len(clients)}")

print("[STARTING] server is starting...")
start()