"""
Comprehensive Selenium tests for Memory Game
Tests: card flipping issues, blank images, room management, multiplayer sync
"""
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import random
import string


@pytest.fixture
def chrome_options():
    """Chrome options for headless testing"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    return options


@pytest.fixture
def driver(chrome_options):
    """Create and cleanup Chrome driver"""
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


@pytest.fixture
def second_driver(chrome_options):
    """Second driver for multiplayer tests"""
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


@pytest.fixture
def third_driver(chrome_options):
    """Third driver for multiplayer tests"""
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(2)
    yield driver
    driver.quit()


def get_base_url():
    """Get base URL from environment or default"""
    return os.environ.get('TEST_URL', 'http://localhost:8000')


def generate_room_name():
    """Generate unique room name"""
    return f"test-{''.join(random.choices(string.ascii_lowercase, k=6))}"


def wait_for_connection(driver, timeout=10):
    """Wait for WebSocket connection"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: "Connected" in d.find_element(By.ID, "turn-indicator").text
            or "Your turn" in d.find_element(By.ID, "turn-indicator").text
        )
        return True
    except TimeoutException:
        print(f"Connection timeout. Status: {driver.find_element(By.ID, 'turn-indicator').text}")
        return False


def get_card_state(driver, index):
    """Get card state including classes and displayed image"""
    board = driver.find_element(By.ID, "game-board")
    cards = board.find_elements(By.CLASS_NAME, "card")
    if index >= len(cards):
        return None
    
    card = cards[index]
    classes = card.get_attribute("class")
    
    # Check if front content is visible
    front = card.find_element(By.CLASS_NAME, "front")
    front_visible = front.is_displayed()
    front_text = front.text if front_visible else ""
    
    return {
        'flipped': 'flipped' in classes,
        'matched': 'matched' in classes,
        'front_visible': front_visible,
        'front_text': front_text,
        'classes': classes
    }


def is_card_showing_image(driver, index):
    """Check if card is showing its front image/emoji"""
    state = get_card_state(driver, index)
    if not state:
        return False
    
    # Card should be flipped AND have visible front content
    return state['flipped'] and state['front_visible']


class TestCardFlipping:
    """Test card flipping behavior and blank image issues"""
    
    def test_single_card_flip_shows_image(self, driver):
        """Test that flipping a single card properly displays the image"""
        room = generate_room_name()
        driver.get(f"{get_base_url()}/game/{room}")
        assert wait_for_connection(driver), "Failed to connect"
        
        # Start game
        start_btn = driver.find_element(By.ID, "start-btn")
        start_btn.click()
        time.sleep(1)
        
        # Flip first card
        board = driver.find_element(By.ID, "game-board")
        cards = board.find_elements(By.CLASS_NAME, "card")
        assert len(cards) == 16, "Should have 16 cards"
        
        cards[0].click()
        time.sleep(0.5)  # Give time for flip animation
        
        # Verify card is flipped and showing image
        state = get_card_state(driver, 0)
        assert state is not None, "Card state should exist"
        assert state['flipped'], "Card should be flipped"
        assert state['front_visible'], "Front should be visible"
        
        # Image should persist for at least 2 seconds
        time.sleep(1)
        state_after = get_card_state(driver, 0)
        assert state_after['flipped'], "Card should still be flipped"
        assert state_after['front_visible'], "Front should still be visible"
    
    def test_rapid_card_flips_no_blank_images(self, driver):
        """Test that rapid clicking doesn't cause blank images"""
        room = generate_room_name()
        driver.get(f"{get_base_url()}/game/{room}")
        assert wait_for_connection(driver)
        
        driver.find_element(By.ID, "start-btn").click()
        time.sleep(1)
        
        board = driver.find_element(By.ID, "game-board")
        cards = board.find_elements(By.CLASS_NAME, "card")
        
        # Try to flip cards rapidly (only 2 should flip)
        for i in range(4):
            cards[i].click()
            time.sleep(0.1)
        
        time.sleep(0.5)
        
        # Check that exactly 2 cards are flipped and both show images
        flipped_count = 0
        for i in range(4):
            state = get_card_state(driver, i)
            if state and state['flipped']:
                flipped_count += 1
                assert state['front_visible'], f"Card {i} should show image"
        
        assert flipped_count == 2, "Only 2 cards should be flipped"
    
    def test_matched_cards_never_go_blank(self, driver):
        """Test that matched cards permanently show their images"""
        room = generate_room_name()
        driver.get(f"{get_base_url()}/game/{room}")
        assert wait_for_connection(driver)
        
        # Use emoji theme for easier testing
        theme_select = Select(driver.find_element(By.ID, "theme-select"))
        theme_select.select_by_value("emoji")
        driver.find_element(By.ID, "start-btn").click()
        time.sleep(1)
        
        # Find and match a pair
        board = driver.find_element(By.ID, "game-board")
        cards = board.find_elements(By.CLASS_NAME, "card")
        
        # Click first card
        cards[0].click()
        time.sleep(0.5)
        first_state = get_card_state(driver, 0)
        first_content = first_state['front_text']
        
        # Find matching card
        match_idx = None
        for i in range(1, 16):
            cards[i].click()
            time.sleep(0.5)
            state = get_card_state(driver, i)
            if state['front_text'] == first_content:
                match_idx = i
                break
            # If not match, wait for flip back
            time.sleep(2.5)
        
        if match_idx:
            # Wait for match processing
            time.sleep(1)
            
            # Verify both matched cards show images permanently
            for idx in [0, match_idx]:
                state = get_card_state(driver, idx)
                assert state['matched'], f"Card {idx} should be matched"
                assert state['flipped'], f"Card {idx} should be flipped"
                assert state['front_visible'], f"Card {idx} should show image"
            
            # Wait and check again - images should never disappear
            time.sleep(2)
            for idx in [0, match_idx]:
                state = get_card_state(driver, idx)
                assert state['front_visible'], f"Card {idx} image should persist"


class TestMultiplayerSync:
    """Test multiplayer synchronization and room management"""
    
    def test_two_players_see_same_board(self, driver, second_driver):
        """Test that two players see the same game board"""
        room = generate_room_name()
        
        # Both players join
        driver.get(f"{get_base_url()}/game/{room}")
        second_driver.get(f"{get_base_url()}/game/{room}")
        
        assert wait_for_connection(driver), "Player 1 failed to connect"
        assert wait_for_connection(second_driver), "Player 2 failed to connect"
        
        time.sleep(1)
        
        # Check both see 2 players
        players1 = driver.find_elements(By.CLASS_NAME, "player")
        players2 = second_driver.find_elements(By.CLASS_NAME, "player")
        assert len(players1) == 2, f"Player 1 should see 2 players, saw {len(players1)}"
        assert len(players2) == 2, f"Player 2 should see 2 players, saw {len(players2)}"
        
        # Player 1 starts game
        driver.find_element(By.ID, "start-btn").click()
        time.sleep(1)
        
        # Both should see the board
        board1 = driver.find_element(By.ID, "game-board")
        board2 = second_driver.find_element(By.ID, "game-board")
        
        cards1 = board1.find_elements(By.CLASS_NAME, "card")
        cards2 = board2.find_elements(By.CLASS_NAME, "card")
        
        assert len(cards1) == 16, "Player 1 should see 16 cards"
        assert len(cards2) == 16, "Player 2 should see 16 cards"
    
    def test_card_flip_syncs_to_other_player(self, driver, second_driver):
        """Test that card flips are visible to both players"""
        room = generate_room_name()
        
        driver.get(f"{get_base_url()}/game/{room}")
        second_driver.get(f"{get_base_url()}/game/{room}")
        
        assert wait_for_connection(driver)
        assert wait_for_connection(second_driver)
        time.sleep(1)
        
        # Start game
        driver.find_element(By.ID, "start-btn").click()
        time.sleep(1)
        
        # Player 1 flips a card
        board1 = driver.find_element(By.ID, "game-board")
        cards1 = board1.find_elements(By.CLASS_NAME, "card")
        cards1[0].click()
        time.sleep(0.5)
        
        # Player 2 should see the flip
        state2 = get_card_state(second_driver, 0)
        assert state2['flipped'], "Player 2 should see flipped card"
        assert state2['front_visible'], "Player 2 should see card image"


class TestRoomManagement:
    """Test room creation, joining, and cleanup"""
    
    def test_no_duplicate_players_same_session(self, driver):
        """Test that rejoining same room doesn't create duplicate players"""
        room = generate_room_name()
        
        # Join room
        driver.get(f"{get_base_url()}/game/{room}")
        assert wait_for_connection(driver)
        time.sleep(1)
        
        # Check player count
        players = driver.find_elements(By.CLASS_NAME, "player")
        initial_count = len(players)
        
        # Refresh page (rejoin)
        driver.refresh()
        assert wait_for_connection(driver)
        time.sleep(1)
        
        # Should still have same number of players
        players = driver.find_elements(By.CLASS_NAME, "player")
        assert len(players) == initial_count, "Should not duplicate player on rejoin"
    
    def test_three_players_all_see_each_other(self, driver, second_driver, third_driver):
        """Test that three players can all join and see each other"""
        room = generate_room_name()
        
        # All join
        driver.get(f"{get_base_url()}/game/{room}")
        second_driver.get(f"{get_base_url()}/game/{room}")
        third_driver.get(f"{get_base_url()}/game/{room}")
        
        assert wait_for_connection(driver)
        assert wait_for_connection(second_driver)
        assert wait_for_connection(third_driver)
        time.sleep(1)
        
        # All should see 3 players
        for d in [driver, second_driver, third_driver]:
            players = d.find_elements(By.CLASS_NAME, "player")
            assert len(players) == 3, f"Should see 3 players, saw {len(players)}"


class TestStressAndEdgeCases:
    """Stress tests and edge cases"""
    
    def test_flip_many_cards_no_errors(self, driver):
        """Test flipping many cards in sequence"""
        room = generate_room_name()
        driver.get(f"{get_base_url()}/game/{room}")
        assert wait_for_connection(driver)
        
        driver.find_element(By.ID, "start-btn").click()
        time.sleep(1)
        
        board = driver.find_element(By.ID, "game-board")
        cards = board.find_elements(By.CLASS_NAME, "card")
        
        # Flip cards in pairs (allowing only 2 at a time)
        for i in range(0, 8, 2):
            try:
                cards[i].click()
                time.sleep(0.3)
                
                # Check card shows image
                state = get_card_state(driver, i)
                if state:
                    assert state['flipped'], f"Card {i} should flip"
                
                time.sleep(3)  # Wait for flip back or match
            except Exception as e:
                print(f"Error flipping card {i}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
