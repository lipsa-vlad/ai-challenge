"""
Unit tests for game logic functions
"""
import unittest
from app import get_cards, fetch_starwars_characters, fetch_pokemon


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
    
    def test_fetch_starwars_characters(self):
        """Test Star Wars API fetch returns 8 characters"""
        characters = fetch_starwars_characters()
        self.assertEqual(len(characters), 8)
        self.assertIsInstance(characters, list)
    
    def test_fetch_pokemon(self):
        """Test Pokemon API fetch returns 8 pokemon"""
        pokemon = fetch_pokemon()
        self.assertEqual(len(pokemon), 8)
        self.assertIsInstance(pokemon, list)


if __name__ == '__main__':
    unittest.main()
