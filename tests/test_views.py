"""
Unit tests for Django views
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from memory_game.consumers import GameConsumer


class TestViews(TestCase):
    """Test Django views"""
    
    def setUp(self):
        self.client = Client()
        # Clear any existing games
        GameConsumer.games.clear()
    
    def test_lobby_view(self):
        """Test lobby page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Multiplayer Memory Game')
        self.assertContains(response, 'Join Game')
        self.assertContains(response, 'Active Rooms')
    
    def test_lobby_view_has_room_list(self):
        """Test lobby contains room list section"""
        response = self.client.get('/')
        self.assertContains(response, 'rooms-list')
        self.assertContains(response, 'refresh-btn')
    
    def test_game_room_view(self):
        """Test game room page loads successfully"""
        response = self.client.get('/game/testroom/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Memory Game')
        self.assertContains(response, 'testroom')
        self.assertContains(response, 'Start Game')
    
    def test_game_room_with_special_characters(self):
        """Test game room with special characters in name"""
        response = self.client.get('/game/test-room_123/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test-room_123')
    
    def test_game_room_has_required_elements(self):
        """Test game room has all required UI elements"""
        response = self.client.get('/game/testroom/')
        self.assertContains(response, 'players-section')
        self.assertContains(response, 'theme-select')
        self.assertContains(response, 'start-btn')
        self.assertContains(response, 'game-board')
    
    def test_list_rooms_api_empty(self):
        """Test list rooms API returns empty list when no rooms"""
        response = self.client.get('/api/rooms')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('rooms', data)
        self.assertEqual(len(data['rooms']), 0)
    
    def test_list_rooms_api_with_active_rooms(self):
        """Test list rooms API with active games"""
        # Simulate active games
        GameConsumer.games['room1'] = {
            'players': {
                'player1': {'name': 'Player 1', 'score': 0, 'connected': True}
            },
            'cards': [],
            'flipped': [],
            'matched': [],
            'current_player': 'player1',
            'theme': 'emoji',
            'started': False
        }
        GameConsumer.games['room2'] = {
            'players': {
                'player1': {'name': 'Player 1', 'score': 2, 'connected': True},
                'player2': {'name': 'Player 2', 'score': 1, 'connected': True}
            },
            'cards': ['🎮'] * 16,
            'flipped': [],
            'matched': [0, 1],
            'current_player': 'player1',
            'theme': 'starwars',
            'started': True
        }
        
        response = self.client.get('/api/rooms')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(len(data['rooms']), 2)
        
        # Check room1
        room1 = next(r for r in data['rooms'] if r['name'] == 'room1')
        self.assertEqual(room1['players'], 1)
        self.assertEqual(room1['theme'], 'emoji')
        self.assertFalse(room1['started'])
        
        # Check room2
        room2 = next(r for r in data['rooms'] if r['name'] == 'room2')
        self.assertEqual(room2['players'], 2)
        self.assertEqual(room2['theme'], 'starwars')
        self.assertTrue(room2['started'])
    
    def test_new_game_api_default_theme(self):
        """Test new game API with default theme"""
        response = self.client.get('/api/new-game')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('cards', data)
        self.assertIn('theme', data)
        self.assertEqual(data['theme'], 'emoji')
        self.assertEqual(len(data['cards']), 16)
    
    def test_new_game_api_emoji_theme(self):
        """Test new game API with emoji theme"""
        response = self.client.get('/api/new-game?theme=emoji')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['theme'], 'emoji')
        self.assertEqual(len(data['cards']), 16)
    
    def test_new_game_api_starwars_theme(self):
        """Test new game API with Star Wars theme"""
        response = self.client.get('/api/new-game?theme=starwars')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['theme'], 'starwars')
        self.assertEqual(len(data['cards']), 16)
    
    def test_new_game_api_pokemon_theme(self):
        """Test new game API with Pokemon theme"""
        response = self.client.get('/api/new-game?theme=pokemon')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(data['theme'], 'pokemon')
        self.assertEqual(len(data['cards']), 16)
    
    def test_new_game_api_invalid_theme(self):
        """Test new game API with invalid theme defaults to emoji"""
        response = self.client.get('/api/new-game?theme=invalid')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['cards']), 16)
    
    def test_static_files_accessible(self):
        """Test that static files are accessible"""
        response = self.client.get('/static/style.css')
        self.assertEqual(response.status_code, 200)
        # Check content type instead of content for file responses
        self.assertIn('text/css', response.get('Content-Type', ''))
        
        response = self.client.get('/static/game.js')
        self.assertEqual(response.status_code, 200)
    
    def test_404_on_invalid_url(self):
        """Test that invalid URLs return 404"""
        response = self.client.get('/invalid/url/')
        self.assertEqual(response.status_code, 404)
    
    def test_multiple_concurrent_rooms(self):
        """Test handling multiple game rooms simultaneously"""
        # Create 5 different rooms
        for i in range(5):
            GameConsumer.games[f'room{i}'] = {
                'players': {f'player{j}': {'name': f'Player {j}', 'score': 0, 'connected': True} for j in range(i+1)},
                'cards': [],
                'flipped': [],
                'matched': [],
                'current_player': 'player0',
                'theme': ['emoji', 'starwars', 'pokemon'][i % 3],
                'started': i % 2 == 0
            }
        
        response = self.client.get('/api/rooms')
        data = json.loads(response.content)
        self.assertEqual(len(data['rooms']), 5)


if __name__ == '__main__':
    unittest.main()
