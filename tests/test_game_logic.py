"""
Unit tests for game logic functions
"""
import unittest
from unittest.mock import patch, MagicMock
from app import get_cards, fetch_starwars_characters, fetch_pokemon
import requests


class TestGameLogic(unittest.TestCase):
    """Test core game logic functions"""
    
    def test_get_cards_emoji_theme(self):
        """Test that emoji theme returns 16 cards (8 pairs)"""
        cards = get_cards('emoji')
        self.assertEqual(len(cards), 16)
        
        # Check that there are exactly 8 unique items (pairs)
        unique_cards = set(cards)
        self.assertEqual(len(unique_cards), 8)
        
        # Check that each item appears exactly twice
        for card in unique_cards:
            self.assertEqual(cards.count(card), 2)
    
    def test_get_cards_starwars_theme(self):
        """Test that Star Wars theme returns 16 cards"""
        cards = get_cards('starwars')
        self.assertEqual(len(cards), 16)
        
        unique_cards = set(cards)
        self.assertEqual(len(unique_cards), 8)
        
        # Verify cards are strings (character names)
        for card in cards:
            self.assertIsInstance(card, str)
    
    def test_get_cards_pokemon_theme(self):
        """Test that Pokemon theme returns 16 cards"""
        cards = get_cards('pokemon')
        self.assertEqual(len(cards), 16)
        
        unique_cards = set(cards)
        self.assertEqual(len(unique_cards), 8)
        
        # Verify cards are strings (pokemon names)
        for card in cards:
            self.assertIsInstance(card, str)
    
    def test_cards_are_shuffled(self):
        """Test that cards are randomized"""
        cards1 = get_cards('emoji')
        cards2 = get_cards('emoji')
        
        # While there's a tiny chance they could be the same, it's extremely unlikely
        # This tests that shuffling is happening
        self.assertNotEqual(cards1, cards2, "Cards should be shuffled randomly")
    
    def test_get_cards_invalid_theme_defaults_to_emoji(self):
        """Test that invalid theme defaults to emoji"""
        cards = get_cards('invalid_theme')
        self.assertEqual(len(cards), 16)
        # Should return emoji cards by default
        unique_cards = set(cards)
        self.assertEqual(len(unique_cards), 8)
    
    def test_get_cards_none_theme_defaults_to_emoji(self):
        """Test that None theme defaults to emoji"""
        cards = get_cards(None)
        self.assertEqual(len(cards), 16)
    
    def test_get_cards_empty_string_defaults_to_emoji(self):
        """Test that empty string theme defaults to emoji"""
        cards = get_cards('')
        self.assertEqual(len(cards), 16)
    
    def test_fetch_starwars_characters(self):
        """Test Star Wars API fetch returns 8 characters"""
        characters = fetch_starwars_characters()
        self.assertEqual(len(characters), 8)
        self.assertIsInstance(characters, list)
        # All should be non-empty strings
        for char in characters:
            self.assertTrue(len(char) > 0)
    
    def test_fetch_pokemon(self):
        """Test Pokemon API fetch returns 8 pokemon"""
        pokemon = fetch_pokemon()
        self.assertEqual(len(pokemon), 8)
        self.assertIsInstance(pokemon, list)
        # All should be non-empty strings
        for poke in pokemon:
            self.assertTrue(len(poke) > 0)
    
    @patch('app.requests.get')
    def test_fetch_starwars_api_failure_fallback(self, mock_get):
        """Test that Star Wars API failure returns fallback data"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        characters = fetch_starwars_characters()
        self.assertEqual(len(characters), 8)
        self.assertIsInstance(characters, list)
    
    @patch('app.requests.get')
    def test_fetch_pokemon_api_failure_fallback(self, mock_get):
        """Test that Pokemon API failure returns fallback data"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        pokemon = fetch_pokemon()
        self.assertEqual(len(pokemon), 8)
        self.assertIsInstance(pokemon, list)
    
    def test_card_pairs_are_properly_shuffled(self):
        """Test that pairs are distributed throughout the deck"""
        cards = get_cards('emoji')
        # Check that the same card doesn't appear consecutively (very unlikely with proper shuffle)
        consecutive_count = sum(1 for i in range(len(cards)-1) if cards[i] == cards[i+1])
        # With proper shuffling, consecutive matches should be rare
        self.assertLess(consecutive_count, 3, "Too many consecutive pairs - shuffle may be broken")
    
    def test_all_themes_return_valid_data(self):
        """Test that all themes return valid card data"""
        themes = ['emoji', 'starwars', 'pokemon']
        for theme in themes:
            with self.subTest(theme=theme):
                cards = get_cards(theme)
                self.assertEqual(len(cards), 16)
                self.assertEqual(len(set(cards)), 8)
                # All cards should be non-empty
                for card in cards:
                    self.assertTrue(len(card) > 0)


if __name__ == '__main__':
    unittest.main()
