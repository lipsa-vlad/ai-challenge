import json
from channels.generic.websocket import AsyncWebsocketConsumer
from app import get_cards

class GameConsumer(AsyncWebsocketConsumer):
    games = {}
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        
        print(f"WebSocket connecting to room: {self.room_name}")
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"WebSocket accepted for room: {self.room_name}")
        
        if self.room_name not in self.games:
            self.games[self.room_name] = {
                'players': {},
                'cards': [],
                'flipped': [],
                'matched': [],
                'current_player': None,
                'theme': 'emoji',
                'started': False
            }
        
        game = self.games[self.room_name]
        
        # Clean up disconnected players before adding new one
        disconnected_players = [pid for pid, p in game['players'].items() if not p['connected']]
        for pid in disconnected_players:
            del game['players'][pid]
            print(f"Removed disconnected player: {pid}")
        
        # Reassign player numbers after cleanup
        player_id = self.channel_name
        player_number = len(game['players']) + 1
        game['players'][player_id] = {
            'name': f'Player {player_number}',
            'score': 0,
            'connected': True
        }
        
        if game['current_player'] is None or game['current_player'] not in game['players']:
            game['current_player'] = player_id
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game': self.serialize_game(game, player_id)
            }
        )
    
    async def disconnect(self, close_code):
        if self.room_name in self.games:
            game = self.games[self.room_name]
            if self.channel_name in game['players']:
                # Remove player immediately instead of marking as disconnected
                del game['players'][self.channel_name]
                print(f"Player {self.channel_name} removed from room {self.room_name}")
                
                # Update current player if needed
                if game['current_player'] == self.channel_name:
                    connected_players = [p for p in game['players'].keys() if game['players'][p]['connected']]
                    game['current_player'] = connected_players[0] if connected_players else None
                
                # If no players left, clean up the game
                if len(game['players']) == 0:
                    del self.games[self.room_name]
                    print(f"Room {self.room_name} cleaned up (no players)")
                else:
                    # Notify remaining players
                    for player_id in game['players'].keys():
                        await self.channel_layer.send(
                            player_id,
                            {
                                'type': 'game_update',
                                'game': self.serialize_game(game, player_id)
                            }
                        )
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        game = self.games.get(self.room_name)
        
        if not game:
            return
        
        if action == 'start_game':
            theme = data.get('theme', 'emoji')
            game['theme'] = theme
            game['cards'] = get_cards(theme)
            game['matched'] = []
            game['flipped'] = []
            game['started'] = True
            
            for player in game['players'].values():
                player['score'] = 0
            
            # Send game state to each player with their perspective
            for player_id in game['players'].keys():
                await self.channel_layer.send(
                    player_id,
                    {
                        'type': 'game_update',
                        'game': self.serialize_game(game, player_id)
                    }
                )
        
        elif action == 'flip_card':
            if game['current_player'] != self.channel_name:
                return
            
            index = data.get('index')
            if index in game['matched'] or index in game['flipped']:
                return
            
            game['flipped'].append(index)
            
            # Broadcast the flip immediately to all players
            for player_id in game['players'].keys():
                await self.channel_layer.send(
                    player_id,
                    {
                        'type': 'game_update',
                        'game': self.serialize_game(game, player_id)
                    }
                )
            
            # Check for match if two cards are flipped
            if len(game['flipped']) == 2:
                # Don't block here - let client handle the delay
                idx1, idx2 = game['flipped']
                if game['cards'][idx1] == game['cards'][idx2]:
                    game['matched'].extend(game['flipped'])
                    game['players'][self.channel_name]['score'] += 1
                    game['flipped'] = []
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'match_found',
                            'indices': [idx1, idx2],
                            'player': game['players'][self.channel_name]['name']
                        }
                    )
                else:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'no_match',
                            'indices': [idx1, idx2]
                        }
                    )
                    
                    # Wait for client-side delay before clearing flipped cards
                    import asyncio
                    await asyncio.sleep(1.5)
                    
                    player_ids = [p for p in game['players'].keys() if game['players'][p]['connected']]
                    current_idx = player_ids.index(game['current_player'])
                    game['current_player'] = player_ids[(current_idx + 1) % len(player_ids)]
                    game['flipped'] = []
                
                    for player_id in game['players'].keys():
                        await self.channel_layer.send(
                            player_id,
                            {
                                'type': 'game_update',
                                'game': self.serialize_game(game, player_id)
                            }
                        )
    
    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'game': event['game']
        }))
    
    async def match_found(self, event):
        await self.send(text_data=json.dumps({
            'type': 'match_found',
            'indices': event['indices'],
            'player': event['player']
        }))
    
    async def no_match(self, event):
        await self.send(text_data=json.dumps({
            'type': 'no_match',
            'indices': event['indices']
        }))
    
    def serialize_game(self, game, current_player_id):
        return {
            'players': [
                {
                    'id': pid,
                    'name': p['name'],
                    'score': p['score'],
                    'connected': p['connected'],
                    'is_current': game['current_player'] == pid,
                    'is_you': pid == current_player_id
                }
                for pid, p in game['players'].items()
            ],
            'cards': game['cards'] if game['started'] else [],
            'matched': game['matched'],
            'flipped': game['flipped'],
            'current_player': game['players'][game['current_player']]['name'] if game['current_player'] else None,
            'theme': game['theme'],
            'started': game['started'],
            'is_your_turn': game['current_player'] == current_player_id
        }
