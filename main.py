import socket
import json
import sys
from _thread import *
from settings import *
from room import *
from gamestate import GameState

HOST = '0.0.0.0'
PORT = 5555


class Server:
    
    def __init__(self, host, port, max_client):
        self.host = host
        self.port = port
        self.max_client = max_client
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.max_client)
        self.clients = []
        self.state = GameState()
    
    
    
    def thread_client(self, sock_client):  
        self.clients.append(sock_client) 
        player_id = ""
        while True:
            try:
                data = sock_client.recv(MAX_DATA_SIZE).decode()
                if not data:
                    print(f'client {player_id} had disconnected')
                    break
                client_data = json.loads(data)
                
                if client_data['flag'] == 1:
                    player_id = client_data['id']
                    self.state.init_player(player_id, client_data['team'])
                    print(f"{player_id} had connected to server")
                    
                elif client_data['flag'] == 2:                    
                    self.state.client_data_update(client_data)
                    sock_client.send(self.state.get_json_string().encode())
                    self.state.clear_client_online_bullets(player_id) #* to make sure not send a bullet mutiple time to same client
                    
                elif client_data['flag'] == 3:
                    self.state.respawn_player(client_data['id'], client_data['pos'])
        
                # self.state.bullet_handle()
                # self.state.bullets.clear()
            except Exception as e:
                print(f"Error: {e}")
                break

        sock_client.close()
        self.clients.remove(sock_client)
        self.state.players.pop(player_id)    
        
    def run(self):
        try:
            while True:
                conn, addr = self.socket.accept()
                print(f"Connected to: {addr}")
                start_new_thread(self.thread_client, (conn,))
        except KeyboardInterrupt:
            print("\nShutting down the server...")

        finally:
            self.socket.close()
            for client in self.clients:
                client.close()
            print("Server closed.")
            sys.exit(0)
    

server = Server(HOST, PORT, 10)
server.run()

