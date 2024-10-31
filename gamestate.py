import json
from settings import *
from ultis import *

class GameState:
    
    def __init__(self):
        self.players = {}
        self.bullets = []
        self.obtacles = []
        self.bullet_init_triger = []
        self.invalid_update_keys = ['online_bullets', 'hp', 'dead']
    
    def init_player(self, player_id, team):
        self.players[player_id] = {
            'team' : team,
            'pos' : (0,0),
            'hp' : 100,
            'angle' : 90,
            'online_bullets' : [],
            'local_bullets' : [],
            'wp_index': 1,
            'sp_index': 0,
            'dead': False,
        }  

    def respawn_player(self, player_id, pos):
        self.players[player_id] = {
            'team' : self.players[player_id]['team'],
            'pos' : pos,
            'hp' : 100,
            'angle' : 90,
            'online_bullets' : [],
            'local_bullets' : [],
            'wp_index': 1,
            'sp_index': 0,
            'dead': False,
        }

    def kill_handle(self,killer_id ,dead_id):
        print(f'{killer_id} killed {dead_id}')
        self.players[dead_id]['dead'] = True
        pass
        
    def bullet_handle(self):
        for (player_id, player_data) in self.players.items():
            hitbox_x, hitbox_y = player_data['pos']
            for (start_pos, end_pos, angle, dmg, id) in self.bullets:
                if id == player_id:
                    continue
                if line_rectangle_collision( (start_pos, end_pos),
                                       (hitbox_x, hitbox_y, PLAYER_HITBOX_SIZE, PLAYER_HITBOX_SIZE)
                                       ):
                    player_data['hp'] -= dmg
                    print(f"{id} hit {player_id}")
                    if player_data['hp'] <= 0:
                        self.kill_handle(killer_id= id, dead_id= player_id)
        self.bullets.clear()
                    
                     
                        
    def client_data_update(self, client_data):
        # self.players[client_data['id']] = client_data['player']
        for key in client_data['player'].keys():
            if key not in self.invalid_update_keys:
                self.players[client_data['id']][key] = client_data['player'][key]
        for bullet in client_data['player']['local_bullets']:
            self.bullets.append(bullet)
        if self.bullets.__len__() > 0:
            self.bullet_handle()
        self.update_online_bullets(client_data['id'],client_data['player']['local_bullets'])
    
    def update_online_bullets(self,client_id ,bullets):
        if bullets == []:
            return
        for player_id in self.players.keys():
            if player_id != client_id:
                print(bullets)
                self.players[player_id]['online_bullets'] += bullets
                print(self.players[player_id]['online_bullets'])

    def clear_client_online_bullets(self, client_id):
        self.players[client_id]['online_bullets'].clear()
                
    
    def get_json_string(self):
        data = {
            'player'  : self.players,
            # 'bullets' : self.bullets
        }
        return json.dumps(data)

            
        