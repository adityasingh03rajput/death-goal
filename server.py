# server.py
import socket
import threading
import json
import sys
from protocols import Protocols

SERVER_IP = input("Enter server IP address (leave blank for local): ")
if SERVER_IP == "":
    SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 55555
clients = []
players_data = {}
ball_data = {'ball': [400,300,[0,0]]}
player_count = 0
WIDTH, HEIGHT = 800, 600
goalposts = [pygame.Rect(0, HEIGHT // 3, 10, HEIGHT // 3), pygame.Rect(WIDTH - 10, HEIGHT // 3, 10, HEIGHT // 3)]

def handle_client(client_socket, player_id):
    global clients, players_data, ball_data, player_count

    try:
        while True:
            data = client_socket.recv(4096).decode("ascii")
            if not data:
                break
            message = json.loads(data)
            r_type = message.get("type")
            data = message.get("data")

            if r_type == Protocols.Request.PLAYER_UPDATE:
                players_data[player_id] = data['player']
                ball_data['ball'] = data['ball']

                other_player_id = 1 - player_id # Assuming 2 players, 0 and 1
                if other_player_id in players_data:
                    client_socket.sendall(json.dumps({"type": Protocols.Response.PLAYER_DATA, "data": {"player": players_data[other_player_id]}}).encode("ascii"))
                    client_socket.sendall(json.dumps({"type": Protocols.Response.BALL_DATA, "data": {"ball": ball_data['ball']}}).encode("ascii"))

    except (socket.error, json.JSONDecodeError) as e:
        print(f"Client disconnected: {e}")
    finally:
        clients.remove(client_socket)
        del players_data[player_id]
        client_socket.close()
        player_count -= 1
        for client in clients:
            try:
                client.sendall(json.dumps({"type": Protocols.Response.OPPONENT_LEFT}).encode("ascii"))
            except socket.error:
                pass

def start_server():
    global player_count, clients, players_data
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print(f"Error binding server: {e}")
        sys.exit()
    server_socket.listen(2)
    print(f"Server listening on {SERVER_IP}:{SERVER_PORT}")

    while player_count < 2:
        try:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            players_data[player_count] = None
            print(f"Accepted connection from {addr}")
            client_socket.send(str(player_count).encode())
            client_thread = threading.Thread(target=handle_client, args=(client_socket, player_count))
            client_thread.daemon = True
            client_thread.start()
            player_count += 1
        except socket.error as e:
            print(f"Error accepting connection: {e}")
            break
    print(" All players connected.")

start_server()
