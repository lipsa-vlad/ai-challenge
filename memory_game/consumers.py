import json
import logging
import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from app import get_cards

logger = logging.getLogger(__name__)

class GameConsumer(AsyncWebsocketConsumer):
    redis_client = None
    
    @classmethod
    async def get_redis(cls):
        """Get or create Redis connection"""
        if cls.redis_client is None:
            cls.redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        return cls.redis_client
    
    async def get_game(self, room_name):
        """Get game state from Redis"""
        r = await self.get_redis()
        data = await r.get(f'game:{room_name}')
        if data:
            return json.loads(data)
        return None
    
    async def set_game(self, room_name, game_state):
        """Save game state to Redis"""
        r = await self.get_redis()
        await r.set(f'game:{room_name}', json.dumps(game_state))
    
    async def delete_game(self, room_name):
        """Delete game from Redis"""
        r = await self.get_redis()
        await r.delete(f'game:{room_name}')
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'
        
        # Use session ID if available, otherwise fall back to channel_name
        session_id = self.scope.get('session', {}).get('session_key')
        self.player_id = session_id if session_id else self.channel_name
        
        logger.info(f"WebSocket connecting to room: {self.room_name}, player_id: {self.player_id}")
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"✅ WebSocket accepted for room: {self.room_name}, channel: {self.channel_name}")
        
        # Get or create game from Redis
        game = await self.get_game(self.room_name)
        if game is None:
            game = {
                'players': {},
                'cards': [],
                'flipped': [],
                'matched': [],
                'current_player': None,
                'theme': 'emoji',
                'started': False,
                'channel_to_player': {}  # Map channels to player IDs
            }
        
        # Ensure channel_to_player mapping exists
        if 'channel_to_player' not in game:
            game['channel_to_player'] = {}
        
        # Map this channel to the player ID
        game['channel_to_player'][self.channel_name] = self.player_id
        
        # Only add player if not already in the game (prevent duplicates)
        if self.player_id not in game['players']:
            # Reassign player numbers based on current count
            player_number = len(game['players']) + 1
            game['players'][self.player_id] = {
                'name': f'Player {player_number}',
                'score': 0,
                'connected': True
            }
            logger.info(f"➕ Added new player: Player {player_number} (player_id: {self.player_id})")
        else:
            # Mark existing player as connected (reconnection)
            game['players'][self.player_id]['connected'] = True
            logger.info(f"🔄 Reconnected player: {game['players'][self.player_id]['name']} (player_id: {self.player_id})")
        
        if game['current_player'] is None or game['current_player'] not in game['players']:
            game['current_player'] = self.player_id
        
        # Save to Redis
        await self.set_game(self.room_name, game)
        
        player_name = game['players'][self.player_id]['name']
        logger.info(f"👥 Room {self.room_name} now has {len(game['players'])} players: {[p['name'] for p in game['players'].values()]}")
        
        # Notify all players about player joined/reconnected
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'player_name': player_name
            }
        )
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update'
            }
        )
    
    async def disconnect(self, close_code):
        logger.info(f"🔌 WebSocket disconnecting from room: {self.room_name}, channel: {self.channel_name}, close_code: {close_code}")
        
        game = await self.get_game(self.room_name)
        if game:
            # Get channel_to_player mapping
            channel_to_player = game.get('channel_to_player', {})
            player_id = channel_to_player.get(self.channel_name, self.channel_name)
            
            # Remove channel mapping
            if self.channel_name in channel_to_player:
                del channel_to_player[self.channel_name]
            
            # Check if this player has other active channels
            player_has_other_channels = player_id in channel_to_player.values()
            
            if player_id in game['players']:
                player_name = game['players'][player_id]['name']
                
                # Only remove player if they have no other active channels
                if not player_has_other_channels:
                    del game['players'][player_id]
                    logger.info(f"👋 Player {player_name} (player_id: {player_id}) removed from room {self.room_name}")
                    logger.info(f"📊 Remaining players in room {self.room_name}: {len(game['players'])}")
                    
                    # Update current player if needed
                    if game['current_player'] == player_id:
                        connected_players = list(game['players'].keys())
                        game['current_player'] = connected_players[0] if connected_players else None
                        logger.info(f"🔄 Current player updated to: {game['current_player']}")
                    
                    should_notify = True
                else:
                    logger.info(f"🔗 Player {player_name} still has other active connections, not removing")
                    should_notify = False
                
                # If no players left, delete the game from Redis completely
                if len(game['players']) == 0:
                    await self.delete_game(self.room_name)
                    logger.info(f"🧹 Room {self.room_name} deleted from Redis (no players remaining)")
                else:
                    # Save updated game state
                    await self.set_game(self.room_name, game)
                    logger.info(f"💾 Game state saved for room {self.room_name}")
                    
                    if should_notify:
                        # Notify about player leaving
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'player_left',
                                'player_name': player_name
                            }
                        )
                        
                        # Broadcast update to all remaining players
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'game_update'
                            }
                        )
            else:
                logger.warning(f"⚠️ Player ID {player_id} not found in game players for room {self.room_name}")
        else:
            logger.warning(f"⚠️ No game found for room {self.room_name} during disconnect")
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"✅ Cleanup complete for channel {self.channel_name}")
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        game = await self.get_game(self.room_name)
        
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
            
            # Save to Redis
            await self.set_game(self.room_name, game)
            
            # Broadcast game state to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update'
                }
            )
        
        elif action == 'flip_card':
            if game['current_player'] != self.player_id:
                return
            
            index = data.get('index')
            if index in game['matched'] or index in game['flipped']:
                return
            
            game['flipped'].append(index)
            
            # Save to Redis
            await self.set_game(self.room_name, game)
            
            # Broadcast the flip immediately to all players
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_update'
                }
            )
            
            # Check for match if two cards are flipped
            if len(game['flipped']) == 2:
                # Don't block here - let client handle the delay
                idx1, idx2 = game['flipped']
                if game['cards'][idx1] == game['cards'][idx2]:
                    game['matched'].extend(game['flipped'])
                    game['players'][self.player_id]['score'] += 1
                    
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'match_found',
                            'indices': [idx1, idx2],
                            'player': game['players'][self.player_id]['name']
                        }
                    )
                    
                    # Clear flipped after notifying
                    game['flipped'] = []
                    
                    # Save to Redis
                    await self.set_game(self.room_name, game)
                    
                    # Send updated state
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_update'
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
                    await asyncio.sleep(2.0)
                    
                    player_ids = list(game['players'].keys())
                    current_idx = player_ids.index(game['current_player'])
                    game['current_player'] = player_ids[(current_idx + 1) % len(player_ids)]
                    game['flipped'] = []
                    
                    # Save to Redis
                    await self.set_game(self.room_name, game)
                
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_update'
                        }
                    )
    
    async def game_update(self, event):
        """Send game update with personalized is_you and is_your_turn flags"""
        game = await self.get_game(self.room_name)
        if game:
            # Serialize with this player's perspective
            personalized_game = self.serialize_game(game, self.player_id)
            await self.send(text_data=json.dumps({
                'type': 'game_update',
                'game': personalized_game
            }))
        else:
            logger.warning(f"No game found in Redis for room {self.room_name}")
    
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
    
    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player_name': event['player_name']
        }))
    
    async def player_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'player_name': event['player_name']
        }))
    
    def serialize_game(self, game, current_player_id=None):
        """Serialize game state. If current_player_id is None, don't set is_you flags."""
        return {
            'players': [
                {
                    'id': pid,
                    'name': p['name'],
                    'score': p['score'],
                    'connected': p['connected'],
                    'is_current': game['current_player'] == pid,
                    'is_you': pid == current_player_id if current_player_id else False
                }
                for pid, p in game['players'].items()
            ],
            'cards': game['cards'] if game['started'] else [],
            'matched': game['matched'],
            'flipped': game['flipped'],
            'current_player': game['players'][game['current_player']]['name'] if game['current_player'] and game['current_player'] in game['players'] else 'Player 1',
            'theme': game['theme'],
            'started': game['started'],
            'is_your_turn': game['current_player'] == current_player_id if current_player_id else False
        }
