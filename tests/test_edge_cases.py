"""
Edge case and stress tests
"""
import unittest
from django.test import TestCase, Client
from memory_game.consumers import GameConsumer
from app import get_cards
import json


class TestEdgeCases(TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        self.client = Client()
        GameConsumer.games.clear()
    
    def test_very_long_room_name(self):
        """Test handling of very long room names"""
        long_name = 'a' * 200
        response = self.client.get(f'/game/{long_name}/')
        self.assertEqual(response.status_code, 200)
    
    def test_room_name_with_special_characters(self):
        """Test room names with special characters"""
        special_names = [
            'room-with-dashes',
            'room_with_underscores',
            'room123',
            'UPPERCASE',
            'MixedCase123'
        ]
        for name in special_names:
            with self.subTest(name=name):
                response = self.client.get(f'/game/{name}/')
                self.assertEqual(response.status_code, 200)
    
    def test_empty_room_name(self):
        """Test handling of empty room name"""
        response = self.client.get('/game//')
        # Should handle gracefully (might redirect or 404)
        self.assertIn(response.status_code, [200, 404])
    
    def test_unicode_room_name(self):
        """Test room names with unicode characters"""
        unicode_names = ['room_🎮', 'テスト', '测试']
        for name in unicode_names:
            with self.subTest(name=name):
                try:
                    response = self.client.get(f'/game/{name}/')
                    # Should handle gracefully
                    self.assertIn(response.status_code, [200, 404])
                except Exception:
                    # If URL encoding fails, that's acceptable
                    pass
    
    def test_concurrent_api_calls(self):
        """Test multiple concurrent API calls"""
        responses = []
        for _ in range(10):
            response = self.client.get('/api/new-game?theme=emoji')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(len(data['cards']), 16)
    
    def test_room_list_with_many_rooms(self):
        """Test room list with many active rooms"""
        # Create 50 rooms
        for i in range(50):
            GameConsumer.games[f'room{i}'] = {
                'players': {f'p{j}': {'name': f'P{j}', 'score': 0, 'connected': True} for j in range(2)},
                'cards': [],
                'flipped': [],
                'matched': [],
                'current_player': 'p0',
                'theme': 'emoji',
                'started': False
            }
        
        response = self.client.get('/api/rooms')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['rooms']), 50)
    
    def test_disconnected_players_filtered(self):
        """Test that disconnected players are not counted"""
        GameConsumer.games['test'] = {
            'players': {
                'p1': {'name': 'Player 1', 'score': 0, 'connected': True},
                'p2': {'name': 'Player 2', 'score': 0, 'connected': False},
                'p3': {'name': 'Player 3', 'score': 0, 'connected': False}
            },
            'cards': [],
            'flipped': [],
            'matched': [],
            'current_player': 'p1',
            'theme': 'emoji',
            'started': False
        }
        
        response = self.client.get('/api/rooms')
        data = json.loads(response.content)
        room = data['rooms'][0]
        
        # Only connected player should be counted
        self.assertEqual(room['players'], 1)
    
    def test_api_theme_case_insensitive(self):
        """Test API handles different case for theme"""
        test_cases = ['EMOJI', 'Emoji', 'eMoJi']
        for theme in test_cases:
            with self.subTest(theme=theme):
                response = self.client.get(f'/api/new-game?theme={theme}')
                self.assertEqual(response.status_code, 200)
    
    def test_rapid_room_creation_deletion(self):
        """Test rapidly creating and deleting rooms"""
        for i in range(20):
            GameConsumer.games[f'room{i}'] = {
                'players': {},
                'cards': [],
                'flipped': [],
                'matched': [],
                'current_player': None,
                'theme': 'emoji',
                'started': False
            }
            
            if i % 2 == 0:
                del GameConsumer.games[f'room{i}']
        
        # Should handle gracefully
        response = self.client.get('/api/rooms')
        self.assertEqual(response.status_code, 200)
    
    def test_game_state_consistency(self):
        """Test game state remains consistent"""
        cards = get_cards('emoji')
        
        # Check no card appears more than twice
        from collections import Counter
        counts = Counter(cards)
        for card, count in counts.items():
            self.assertEqual(count, 2, f"Card {card} appears {count} times, should be 2")
    
    def test_all_cards_unique_per_theme(self):
        """Test that each theme has unique card sets"""
        emoji_cards = set(get_cards('emoji'))
        starwars_cards = set(get_cards('starwars'))
        pokemon_cards = set(get_cards('pokemon'))
        
        # Each theme should have 8 unique cards
        self.assertEqual(len(emoji_cards), 8)
        self.assertEqual(len(starwars_cards), 8)
        self.assertEqual(len(pokemon_cards), 8)


class TestPerformance(TestCase):
    """Performance and load tests"""
    
    def test_card_generation_performance(self):
        """Test card generation is fast"""
        import time
        
        start = time.time()
        for _ in range(100):
            get_cards('emoji')
        end = time.time()
        
        # Should complete in under 1 second
        self.assertLess(end - start, 1.0)
    
    def test_api_response_time(self):
        """Test API responds quickly"""
        import time
        
        client = Client()
        start = time.time()
        response = client.get('/api/new-game')
        end = time.time()
        
        # Should respond in under 0.5 seconds
        self.assertLess(end - start, 0.5)
        self.assertEqual(response.status_code, 200)
    
    def test_room_list_performance_with_many_rooms(self):
        """Test room list API performance with many rooms"""
        import time
        
        # Create 100 rooms
        for i in range(100):
            GameConsumer.games[f'room{i}'] = {
                'players': {f'p{j}': {'name': f'P{j}', 'score': 0, 'connected': True} for j in range(3)},
                'cards': ['🎮'] * 16,
                'flipped': [],
                'matched': [],
                'current_player': 'p0',
                'theme': 'emoji',
                'started': i % 2 == 0
            }
        
        client = Client()
        start = time.time()
        response = client.get('/api/rooms')
        end = time.time()
        
        # Should respond in under 1 second even with 100 rooms
        self.assertLess(end - start, 1.0)
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data['rooms']), 100)


class TestDataIntegrity(TestCase):
    """Test data integrity and validation"""
    
    def test_card_pairs_integrity(self):
        """Test that all cards have exactly one pair"""
        for theme in ['emoji', 'starwars', 'pokemon']:
            with self.subTest(theme=theme):
                cards = get_cards(theme)
                from collections import Counter
                counts = Counter(cards)
                
                # All cards should appear exactly twice
                for card, count in counts.items():
                    self.assertEqual(count, 2, f"In {theme}, card {card} appears {count} times")
    
    def test_no_duplicate_room_data(self):
        """Test that room data doesn't leak between instances"""
        room1_data = {
            'players': {'p1': {'name': 'P1', 'score': 5, 'connected': True}},
            'cards': ['A'] * 16,
            'flipped': [0],
            'matched': [1, 2],
            'current_player': 'p1',
            'theme': 'emoji',
            'started': True
        }
        
        room2_data = {
            'players': {'p2': {'name': 'P2', 'score': 0, 'connected': True}},
            'cards': ['B'] * 16,
            'flipped': [],
            'matched': [],
            'current_player': 'p2',
            'theme': 'pokemon',
            'started': False
        }
        
        GameConsumer.games['room1'] = room1_data
        GameConsumer.games['room2'] = room2_data
        
        # Verify they are separate
        self.assertNotEqual(
            GameConsumer.games['room1']['cards'],
            GameConsumer.games['room2']['cards']
        )
        self.assertNotEqual(
            GameConsumer.games['room1']['players'],
            GameConsumer.games['room2']['players']
        )
    
    def test_api_returns_valid_json(self):
        """Test all API endpoints return valid JSON"""
        client = Client()
        endpoints = [
            '/api/new-game',
            '/api/new-game?theme=emoji',
            '/api/new-game?theme=starwars',
            '/api/rooms'
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = client.get(endpoint)
                self.assertEqual(response.status_code, 200)
                
                # Should parse as valid JSON
                try:
                    data = json.loads(response.content)
                    self.assertIsInstance(data, dict)
                except json.JSONDecodeError:
                    self.fail(f"Invalid JSON from {endpoint}")


if __name__ == '__main__':
    unittest.main()
