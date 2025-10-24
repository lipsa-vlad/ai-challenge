"""
Unit tests for Django views
"""
import json
from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    """Test Django views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_lobby_view(self):
        """Test lobby page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Multiplayer Memory Game')
        self.assertContains(response, 'Join Game')
    
    def test_game_room_view(self):
        """Test game room page loads successfully"""
        response = self.client.get('/game/testroom/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Memory Game')
        self.assertContains(response, 'testroom')
        self.assertContains(response, 'Start Game')
    
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
    
    def test_static_files_accessible(self):
        """Test that static files are accessible"""
        response = self.client.get('/static/style.css')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/static/game.js')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
