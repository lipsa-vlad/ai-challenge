"""
Unit tests for WebSocket consumers
"""
import unittest
import json
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from memory_game.consumers import GameConsumer
from memory_game.routing import websocket_urlpatterns
import pytest


@pytest.mark.asyncio
class TestGameConsumer(unittest.IsolatedAsyncioTestCase):
    """Test WebSocket consumer functionality"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        GameConsumer.games.clear()
        self.room_name = 'test_room'
    
    async def test_connect_to_room(self):
        """Test connecting to a game room"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Should receive game state update
        response = await communicator.receive_json_from()
        self.assertEqual(response['type'], 'game_update')
        self.assertIn('game', response)
        
        await communicator.disconnect()
    
    async def test_player_joins_room(self):
        """Test player joining creates proper game state"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        await communicator.connect()
        
        response = await communicator.receive_json_from()
        game_state = response['game']
        
        # Check player was added
        self.assertEqual(len(game_state['players']), 1)
        self.assertEqual(game_state['players'][0]['name'], 'Player 1')
        self.assertFalse(game_state['started'])
        
        await communicator.disconnect()
    
    async def test_start_game(self):
        """Test starting a game"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # Initial state
        
        # Send start game message
        await communicator.send_json_to({
            'action': 'start_game',
            'theme': 'emoji'
        })
        
        response = await communicator.receive_json_from()
        game_state = response['game']
        
        # Check game started
        self.assertTrue(game_state['started'])
        self.assertEqual(game_state['theme'], 'emoji')
        self.assertEqual(len(game_state['cards']), 16)
        
        await communicator.disconnect()
    
    async def test_flip_card(self):
        """Test flipping a card"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        await communicator.connect()
        await communicator.receive_json_from()
        
        # Start game
        await communicator.send_json_to({
            'action': 'start_game',
            'theme': 'emoji'
        })
        await communicator.receive_json_from()
        
        # Flip a card
        await communicator.send_json_to({
            'action': 'flip_card',
            'index': 0
        })
        
        response = await communicator.receive_json_from()
        game_state = response['game']
        
        # Card should be flipped
        self.assertIn(0, game_state['flipped'])
        
        await communicator.disconnect()
    
    async def test_match_found(self):
        """Test matching two cards"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        await communicator.connect()
        await communicator.receive_json_from()
        
        # Start game
        await communicator.send_json_to({
            'action': 'start_game',
            'theme': 'emoji'
        })
        start_response = await communicator.receive_json_from()
        cards = start_response['game']['cards']
        
        # Find two matching cards
        first_card = cards[0]
        second_index = cards.index(first_card, 1)
        
        # Flip first card
        await communicator.send_json_to({
            'action': 'flip_card',
            'index': 0
        })
        await communicator.receive_json_from()
        
        # Flip matching card
        await communicator.send_json_to({
            'action': 'flip_card',
            'index': second_index
        })
        
        # Should receive match notification
        match_response = await communicator.receive_json_from()
        self.assertEqual(match_response['type'], 'match_found')
        
        await communicator.disconnect()
    
    async def test_disconnect_removes_player(self):
        """Test disconnecting removes player from room"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        await communicator.connect()
        await communicator.receive_json_from()
        
        # Room should exist
        self.assertIn(self.room_name, GameConsumer.games)
        
        await communicator.disconnect()
        
        # Room should be cleaned up
        self.assertNotIn(self.room_name, GameConsumer.games)
    
    async def test_multiple_players_same_room(self):
        """Test multiple players in same room"""
        comm1 = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        comm2 = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        
        await comm1.connect()
        await comm1.receive_json_from()
        
        await comm2.connect()
        # Both should receive updates
        response1 = await comm1.receive_json_from()
        response2 = await comm2.receive_json_from()
        
        # Check both see 2 players
        self.assertEqual(len(response1['game']['players']), 2)
        self.assertEqual(len(response2['game']['players']), 2)
        
        await comm1.disconnect()
        await comm2.disconnect()
    
    async def test_turn_based_gameplay(self):
        """Test turn-based mechanics"""
        comm1 = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        comm2 = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        
        await comm1.connect()
        await comm1.receive_json_from()
        await comm2.connect()
        await comm1.receive_json_from()
        await comm2.receive_json_from()
        
        # Player 1 starts game
        await comm1.send_json_to({
            'action': 'start_game',
            'theme': 'emoji'
        })
        
        # Both receive start
        await comm1.receive_json_from()
        response = await comm2.receive_json_from()
        
        # Player 1 should have the turn
        self.assertTrue(response['game']['players'][0]['is_current'])
        
        await comm1.disconnect()
        await comm2.disconnect()
    
    async def test_room_cleanup_on_last_disconnect(self):
        """Test room is cleaned up when last player leaves"""
        comm = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        
        await comm.connect()
        await comm.receive_json_from()
        
        self.assertIn(self.room_name, GameConsumer.games)
        
        await comm.disconnect()
        
        # Room should be deleted
        self.assertNotIn(self.room_name, GameConsumer.games)
    
    async def test_invalid_action_ignored(self):
        """Test invalid actions are ignored gracefully"""
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            f"/ws/game/{self.room_name}/"
        )
        await communicator.connect()
        await communicator.receive_json_from()
        
        # Send invalid action
        await communicator.send_json_to({
            'action': 'invalid_action'
        })
        
        # Should not crash, timeout means no response (as expected)
        try:
            response = await communicator.receive_json_from(timeout=1)
            # If we get here, check it's not an error
            self.assertNotIn('error', response)
        except:
            # Timeout is expected for invalid actions
            pass
        
        await communicator.disconnect()
    
    async def test_theme_selection(self):
        """Test different theme selection"""
        for theme in ['emoji', 'starwars', 'pokemon']:
            with self.subTest(theme=theme):
                room = f'test_room_{theme}'
                communicator = WebsocketCommunicator(
                    GameConsumer.as_asgi(),
                    f"/ws/game/{room}/"
                )
                await communicator.connect()
                await communicator.receive_json_from()
                
                await communicator.send_json_to({
                    'action': 'start_game',
                    'theme': theme
                })
                
                response = await communicator.receive_json_from()
                self.assertEqual(response['game']['theme'], theme)
                
                await communicator.disconnect()


if __name__ == '__main__':
    unittest.main()
