import socket
import json
import sys
import threading
import time
from settings import *
from gamestate import GameState

# HOST = '192.168.1.27'
HOST = '192.168.1.9'
PORT = 5555


class ProxyServer:
    def __init__(self, host, port, max_client):
        self.host = host
        self.port = port
        self.max_client = max_client
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        self.servers = []  
        self.shut_down = False

    def create_new_game_server(self, name):
        new_port = self.port + len(self.servers) + 1
        game_server = Server(self.host, new_port, 12)
        
        server_thread = threading.Thread(target=game_server.run,args=(self.servers,), daemon=True)
        server_thread.start()

        
        self.servers.append([name, HOST, new_port, 0])
        print(f"Created new game server on port {new_port}")
        return (HOST, new_port)

    def forward_to_server(self, data, addr, server):
        try:
            server.socket.sendto(data, (server.host, server.port))
            print(f"Forwarded data from {addr} to server {server.port}")
        except Exception as e:
            print(f"Error forwarding data to server: {e}")

    def process_client_connection(self, data, addr):
        try:
            client_data = json.loads(data.decode())
            if client_data['flag'] == 1:
                response = json.dumps(self.servers).encode()
                self.socket.sendto(response, addr) 
                
            if client_data['flag'] == 2:
                address = self.create_new_game_server(client_data['name'])
                response = json.dumps(address).encode()
                self.socket.sendto(response, addr) 
            
            if client_data['flag'] == 3:
                port = client_data['port']
                for server in self.servers:
                    if server[2] == port:
                        server[3] += 1
        
        except Exception as e:
            print(f"Error: {e}")

    def run(self):
        print(f"Proxy server started on {self.host}:{self.port}")
        try:
            while not self.shut_down:
                data, addr = self.socket.recvfrom(MAX_DATA_SIZE)
                self.process_client_connection(data, addr)

        except KeyboardInterrupt:
            print("\nShutting down the proxy server...")
            self.shut_down = True
        finally:
            self.socket.close()
            sys.exit(0)
            print("Proxy server closed.")


def addr_to_str(addr):
    host, port = addr
    return host + ":"+  str(port)

class Server:
    def __init__(self, host, port, max_client):
        self.host = host
        self.port = port
        self.max_client = max_client
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Change to UDP
        self.socket.bind((self.host, self.port))
        self.clients = {}
        self.state = GameState()
        self.shut_down = False
        self.is_first_created = True
        self.unique_id = {
        }
    
    def process_client_data(self, data, addr):
        try:
            client_data = json.loads(data.decode())
            if addr_to_str(addr) in self.unique_id.keys():
                player_id = self.unique_id[addr_to_str(addr)]
            
            
            if client_data['flag'] == 1:
                if client_data['id'] in self.unique_id.values():
                    self.unique_id[addr_to_str(addr)] = client_data['id'] + "1"
                else:
                    self.unique_id[addr_to_str(addr)] = client_data['id']
                player_id = self.unique_id[addr_to_str(addr)]
                
                self.clients[addr] = player_id   
                self.state.init_player(player_id, client_data['team'])
                self.state.init_stat(player_id)
                self.state.send_message(f"{player_id} had connected")
                print(f"{player_id} had connected from {addr}")
                response = json.dumps(self.state.players[player_id]['pos']).encode()
                self.socket.sendto(response, addr)
                self.is_first_created = False
                
            elif client_data['flag'] == 2:
                self.state.client_data_update(client_data)
                response = self.state.get_current_state(client_data['id']).encode()
                self.socket.sendto(response, addr) 
                
            elif client_data['flag'] == 3:
                # Handle player respawn
                self.state.respawn_player(player_id)
                
            elif client_data['flag'] == 4:
                self.state.change_team(player_id, client_data['team'])
                
            elif client_data['flag'] == -1:
                self.state.send_message(f"{player_id} had disconnected")
                self.state.players.pop(self.clients[addr])
                self.clients.pop(addr)
                print(f"{player_id} had disconnected")
                if self.clients.__len__() == 0 and not self.is_first_created:
                    self.shut_down = True
        
        except Exception as e:
            print(f"Error on server {self.host}:{self.port}: {e}")
        
    def run(self, servers_list):
        print(f"Server started on {self.host}:{self.port}")
        self.state.map_init()
        try:
            while not self.shut_down:
                data, addr = self.socket.recvfrom(MAX_DATA_SIZE)
                if addr not in self.clients:
                    print(f"New connection from {addr}")
                self.process_client_data(data, addr)
                
            for server in servers_list:
                if server[2] == self.port:
                    servers_list.remove(server)                
        except KeyboardInterrupt:
            print("\nShutting down the server...")
            self.shut_down = True
        except Exception as e:
            print("game server error" ,e)
        finally:
            self.socket.close()
            print("Server closed.")

    

server = ProxyServer(HOST, PORT, 20)
server.run()

