import json
from settings import *
from ultis import *
import random
import threading
import time

class GameState:
    
    def __init__(self):
        self.players = {}
        self.bullets = []
        self.knifes = []
        self.obtacles = []
        self.bullet_init_triger = []
        self.invalid_update_keys = ['hp', 'dead', 'stat']
        self.bullet_change = False
        self.nades = []
        self.message = []
        self.players_stat = {}
        self.round_time = 600
        self.end_time = time.time() + self.round_time
        self.on_reset = False
        
    
    def map_init(self):
        spawn_pos = import_csv_layout("./map/dust2/dust2.csv", [47, 48])
        self.t_spawn = []
        self.ct_spawn = []
        for row_index, row in enumerate(spawn_pos):
            for col_index, val in enumerate(row):
                x = col_index * 32
                y = row_index * 32
                if val == 48:
                    self.ct_spawn.append((x,y))
                if val == 47:
                    self.t_spawn.append((x,y))
    
    def init_player(self, player_id, team, first = True):
        self.players[player_id] = {
            'team' : team,
            'pos' : self.ct_spawn[random.randint(0,self.ct_spawn.__len__()-2)] 
                    if "ct" in team else
                    self.t_spawn[random.randint(0,self.t_spawn.__len__()-2)],
            'hp' : 100,
            'angle' : 90,
            'bullets' : [],
            'wp_index': 1,
            'sp_index': 0,
            'knife_sl': [],
            'leg_index' : 0,
            'nade':[],
            'dead': False,
            'firing': False,
        }  

    def init_stat(self, player_id):
        self.players_stat[player_id] = {
            'id' : player_id,
            'k' : 0,
            'd' : 0,
            'a' : 0,
            'KDR':0,
            'sc': 0,
        }
    
    def respawn_player(self, player_id):
        self.players[player_id]['dead'] = True
        timer = threading.Timer(3, self.init_player, (player_id, self.players[player_id]['team']))
        timer.start()
        
    def change_team(self, player_id, team):
        self.players[player_id]['dead'] = True
        timer = threading.Timer(3, self.init_player, (player_id, team))
        timer.start()
    
    def get_side_state_win(self):
        ct_score = 0
        t_score = 0
        for key, player in self.players_stat.items():
            if self.players[key]['team'][:-1] == 't':
                t_score += player['sc']
            else:
                ct_score += player['sc']

        if ct_score > t_score:
            return "ct"
        return "t"
    
    def reset_state(self):
        self.on_reset = False
        self.end_time = time.time() + self.round_time
        for key, player in self.players_stat.items():
            player['k'] = 0
            player['d'] = 0
            player['a'] = 0
            player['KDR'] = 0
            player['sc'] = 0
            
    def kill_handle(self,killer_id ,dead_id):
        print(f'{killer_id} killed {dead_id}')
        self.players_stat[killer_id]['k'] += 1
        self.players_stat[killer_id]['sc'] += 10
        self.players_stat[killer_id]['KDR'] = self.players_stat[killer_id]['k'] / self.players_stat[killer_id]['d'] if self.players_stat[killer_id]['d'] != 0 else self.players_stat[killer_id]['k']
        
        self.players_stat[dead_id]['d'] += 1
        self.players_stat[dead_id]['KDR'] = self.players_stat[dead_id]['k'] / self.players_stat[dead_id]['d'] if self.players_stat[dead_id]['d'] != 0 else self.players_stat[dead_id]['k']
        
        self.players[dead_id]['dead'] = True
        self.send_message(f"{killer_id} had killed {dead_id}");
        self.respawn_player(dead_id)
    
    def send_message(self, msg):
        self.message.append(msg)
        def on_delete_msg():
            self.message.remove(msg)
        timer = threading.Timer(3, on_delete_msg)
        timer.start()
        
    def bullet_handle(self):
        for (player_id, player_data) in self.players.items():
            if player_data['dead'] == True:
                continue
            hitbox_x, hitbox_y = player_data['pos']
            for (start_pos, end_pos, angle, dmg, id) in self.bullets:
                if self.players[id]['team'][:-1] == player_data['team'][:-1]:
                    continue
                if line_rectangle_collision( (start_pos, end_pos),
                                    (hitbox_x - PLAYER_HITBOX_SIZE / 2, hitbox_y - PLAYER_HITBOX_SIZE / 2, PLAYER_HITBOX_SIZE, PLAYER_HITBOX_SIZE)
                                    ):
                    player_data['hp'] -= dmg
                    print(f"{id} hit {player_id}")
                    if player_data['hp'] <= 0:
                        player_data['hp'] = 0
                        self.kill_handle(killer_id= id, dead_id= player_id)
                        break
        self.bullets.clear()
    
    def knife_slash_handle(self):
        for (player_id, player_data) in self.players.items():
            if player_data['dead'] == True:
                continue
            hitbox_x, hitbox_y = player_data['pos']
            for (x,y,w,h, id) in self.knifes:
                if self.players[id]['team'][:-1] == player_data['team'][:-1]:
                    continue
                if rectangle_collision((x,y,w,h), (hitbox_x - PLAYER_HITBOX_SIZE / 2, hitbox_y - PLAYER_HITBOX_SIZE / 2,
                                                   PLAYER_HITBOX_SIZE, PLAYER_HITBOX_SIZE)):
                    player_data['hp'] -= 50
                    print(f"{id} hit {player_id}")
                    if player_data['hp'] <= 0:
                        player_data['hp'] = 0
                        self.kill_handle(killer_id= id, dead_id= player_id)
                        break
        self.knifes.clear()     
    
    
    def nade_handle(self):
        for (player_id, player_data) in self.players.items():
            if player_data['dead'] == True:
                continue
            hitbox_x, hitbox_y = player_data['pos']
            for (x,y , id) in self.nades:
                dis = distance((x,y), (hitbox_x, hitbox_y))                    
                if dis <= 250:
                    player_data['hp'] -= (10 + (1 - (dis/250))*70)
                    print(f"{id} hit {player_id}")
                    if player_data['hp'] <= 0:
                        player_data['hp'] = 0
                        self.kill_handle(killer_id= id, dead_id= player_id)
                        break
        self.nades.clear()
                        
    def client_data_update(self, client_data):
            
        for key in client_data['player'].keys():
            if client_data['player']['dead'] == True and key == 'pos':
                continue
            if key not in self.invalid_update_keys:
                self.players[client_data['id']][key] = client_data['player'][key]
                
        for bullet in client_data['player']['bullets']:
            self.bullets.append(bullet)
        self.bullet_change = False
        
        if client_data['player']['bullets'].__len__() > 0:
            self.bullet_handle()
            
        if client_data['player']['knife_sl'].__len__() > 0:
            for knife_sl in client_data['player']['knife_sl']:
                self.knifes.append(knife_sl)
            self.knife_slash_handle()
            
        if client_data['player']['nade'].__len__() > 0:
            for nade in client_data['player']['nade']:
                self.nades.append(nade)
            self.nade_handle()
                
    
    def get_current_state(self, player_id):
        remaining_time = self.end_time - time.time()
        if remaining_time <= 0:
            curr_time = "00:00"
            win_team = self.get_side_state_win()
            if not self.on_reset:
                self.on_reset = True
                timer = threading.Timer(2.8, self.reset_state)
                timer.start()
                for id, player in self.players.items():
                    self.respawn_player(id)
                
        else:
            mins, secs = divmod(int(remaining_time), 60)
            curr_time = '{:02d}:{:02d}'.format(mins, secs)            
            win_team = None
        data = {
            'player'  : self.players,
            'stat' : self.players_stat,
            'msg' : self.message,
            'time' : curr_time,
            'win' : win_team,
        }
        return json.dumps(data)