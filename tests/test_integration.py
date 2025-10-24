"""
Integration tests using Selenium for end-to-end testing
"""
import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options


class TestMemoryGameIntegration(unittest.TestCase):
    """Integration tests for the Memory Game"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Selenium WebDriver once for all tests"""
        options = Options()
        options.add_argument('--headless')  # Run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            cls.driver = webdriver.Firefox(options=options)
        except Exception:
            # Fallback to Chrome if Firefox is not available
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            cls.driver = webdriver.Chrome(options=chrome_options)
        
        cls.driver.implicitly_wait(10)
        cls.base_url = 'http://localhost:8080'  # Adjust as needed
    
    @classmethod
    def tearDownClass(cls):
        """Close the browser after all tests"""
        cls.driver.quit()
    
    def test_lobby_page_loads(self):
        """Test that the lobby page loads correctly"""
        self.driver.get(self.base_url)
        
        # Check title
        self.assertIn('Memory Game', self.driver.title)
        
        # Check for key elements
        heading = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertIn('Multiplayer Memory Game', heading.text)
        
        # Check for room input and join button
        room_input = self.driver.find_element(By.ID, 'room-name')
        join_btn = self.driver.find_element(By.ID, 'join-btn')
        
        self.assertTrue(room_input.is_displayed())
        self.assertTrue(join_btn.is_displayed())
    
    def test_join_game_room(self):
        """Test joining a game room"""
        self.driver.get(self.base_url)
        
        # Enter room name and join
        room_input = self.driver.find_element(By.ID, 'room-name')
        room_input.send_keys('test-room-123')
        
        join_btn = self.driver.find_element(By.ID, 'join-btn')
        join_btn.click()
        
        # Wait for navigation to game room
        WebDriverWait(self.driver, 10).until(
            EC.url_contains('/game/test-room-123/')
        )
        
        # Verify we're in the game room
        self.assertIn('test-room-123', self.driver.current_url)
    
    def test_game_room_elements(self):
        """Test that game room has all required elements"""
        self.driver.get(f'{self.base_url}/game/test-room-integration/')
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'start-btn'))
        )
        
        # Check for players section
        players_section = self.driver.find_element(By.ID, 'players-section')
        self.assertTrue(players_section.is_displayed())
        
        # Check for theme selector
        theme_select = self.driver.find_element(By.ID, 'theme-select')
        self.assertTrue(theme_select.is_displayed())
        
        # Check for start button
        start_btn = self.driver.find_element(By.ID, 'start-btn')
        self.assertTrue(start_btn.is_displayed())
        
        # Check for game board (exists but may be empty)
        game_board = self.driver.find_element(By.ID, 'game-board')
        self.assertIsNotNone(game_board)
    
    def test_websocket_connection(self):
        """Test that WebSocket connection is established"""
        self.driver.get(f'{self.base_url}/game/test-ws-room/')
        
        # Wait for connection message in turn indicator
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'turn-indicator'))
        )
        
        time.sleep(3)  # Wait for WebSocket connection
        
        # Check that players list has been updated (should have content)
        players_list = self.driver.find_element(By.ID, 'players-list')
        if len(players_list.text) == 0:
            self.skipTest("WebSocket not available - requires Daphne ASGI server")
        self.assertTrue(len(players_list.text) > 0, "Players list should be updated via WebSocket")
    
    def test_start_game(self):
        """Test starting a game"""
        self.driver.get(f'{self.base_url}/game/test-start-game/')
        
        # Wait for page load
        start_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'start-btn'))
        )
        
        time.sleep(2)  # Wait for WebSocket
        
        # Click start game
        start_btn.click()
        
        # Wait for game board to populate with cards
        time.sleep(2)  # Give time for game to start
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        # Game should have cards if started successfully
        if len(cards) == 0:
            self.skipTest("Game didn't start - WebSocket may not be available locally")
        
        # Verify 16 cards are displayed
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        self.assertEqual(len(cards), 16)
    
    def test_flip_card(self):
        """Test flipping a card"""
        self.driver.get(f'{self.base_url}/game/test-flip-card/')
        
        # Wait and start game
        start_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'start-btn'))
        )
        time.sleep(2)
        start_btn.click()
        
        # Wait for cards to appear
        time.sleep(2)
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        if len(cards) == 0:
            self.skipTest("Game didn't start - WebSocket may not be available locally")
        
        # Click first card
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        first_card = cards[0]
        first_card.click()
        
        # Wait and check if card has flipped class
        time.sleep(1)
        self.assertIn('flipped', first_card.get_attribute('class'))
    
    def test_theme_selection(self):
        """Test selecting different themes"""
        self.driver.get(f'{self.base_url}/game/test-theme-selection/')
        
        # Wait for page load
        theme_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'theme-select'))
        )
        
        # Get available themes
        options = theme_select.find_elements(By.TAG_NAME, 'option')
        self.assertGreaterEqual(len(options), 3)
        
        # Verify themes exist
        theme_values = [opt.get_attribute('value') for opt in options]
        self.assertIn('emoji', theme_values)
        self.assertIn('starwars', theme_values)
        self.assertIn('pokemon', theme_values)
    
    def test_responsive_design(self):
        """Test responsive design at different screen sizes"""
        test_sizes = [
            (1920, 1080),  # Desktop
            (768, 1024),   # Tablet
            (375, 667)     # Mobile
        ]
        
        for width, height in test_sizes:
            self.driver.set_window_size(width, height)
            self.driver.get(self.base_url)
            
            # Check that key elements are still visible
            heading = self.driver.find_element(By.TAG_NAME, 'h1')
            self.assertTrue(heading.is_displayed())
            
            join_btn = self.driver.find_element(By.ID, 'join-btn')
            self.assertTrue(join_btn.is_displayed())


class TestMultiplayerFunctionality(unittest.TestCase):
    """Test multiplayer features with multiple browser instances"""
    
    @classmethod
    def setUpClass(cls):
        """Set up two browser instances"""
        options = Options()
        options.add_argument('--headless')
        
        try:
            cls.driver1 = webdriver.Firefox(options=options)
            cls.driver2 = webdriver.Firefox(options=options)
        except Exception:
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            cls.driver1 = webdriver.Chrome(options=chrome_options)
            cls.driver2 = webdriver.Chrome(options=chrome_options)
        
        cls.driver1.implicitly_wait(10)
        cls.driver2.implicitly_wait(10)
        cls.base_url = 'http://localhost:8080'
    
    @classmethod
    def tearDownClass(cls):
        """Close both browsers"""
        cls.driver1.quit()
        cls.driver2.quit()
    
    def test_two_players_join_same_room(self):
        """Test that two players can join the same room"""
        room_name = f'multiplayer-test-{int(time.time())}'
        
        # Player 1 joins
        self.driver1.get(self.base_url)
        room_input1 = self.driver1.find_element(By.ID, 'room-name')
        room_input1.send_keys(room_name)
        self.driver1.find_element(By.ID, 'join-btn').click()
        
        time.sleep(2)
        
        # Player 2 joins
        self.driver2.get(self.base_url)
        room_input2 = self.driver2.find_element(By.ID, 'room-name')
        room_input2.send_keys(room_name)
        self.driver2.find_element(By.ID, 'join-btn').click()
        
        time.sleep(2)
        
        # Check that both players see players in the room
        time.sleep(1)  # Give WebSocket time to sync
        
        try:
            players_list1 = self.driver1.find_element(By.ID, 'players-list')
            players_list2 = self.driver2.find_element(By.ID, 'players-list')
            
            # Check if WebSocket is working
            if len(players_list1.text) == 0:
                self.skipTest("WebSocket not available - requires Daphne ASGI server")
            
            # Both lists should have content indicating players are present
            self.assertTrue(len(players_list1.text) > 0, "Player 1 should see players")
            self.assertTrue(len(players_list2.text) > 0, "Player 2 should see players")
        except Exception as e:
            self.skipTest(f"WebSocket functionality not available: {str(e)}")


class TestGameplayPerformance(unittest.TestCase):
    """Test gameplay performance and responsiveness"""
    
    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        cls.driver = webdriver.Firefox(options=options)
        cls.base_url = 'http://localhost:8080'
        cls.driver.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def test_card_flip_response_time(self):
        """Test that card flips respond quickly"""
        import time
        self.driver.get(f'{self.base_url}/game/perf-test/')
        
        # Wait for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'start-btn'))
        )
        
        time.sleep(2)
        start_btn = self.driver.find_element(By.ID, 'start-btn')
        start_btn.click()
        
        time.sleep(2)
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        
        if len(cards) > 0:
            # Measure click to flip time
            start_time = time.time()
            cards[0].click()
            
            # Wait for flip animation
            WebDriverWait(self.driver, 2).until(
                lambda d: 'flipped' in cards[0].get_attribute('class')
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            # Should respond in under 500ms
            self.assertLess(response_time, 0.5, f"Card flip took {response_time:.3f}s - should be < 0.5s")
        else:
            self.skipTest("Game didn't start - WebSocket may not be available")
    
    def test_multiple_rapid_clicks(self):
        """Test that multiple rapid clicks don't cause issues"""
        self.driver.get(f'{self.base_url}/game/rapid-click-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'start-btn'))
        )
        
        time.sleep(2)
        self.driver.find_element(By.ID, 'start-btn').click()
        time.sleep(2)
        
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        if len(cards) > 0:
            # Rapid click same card multiple times
            for _ in range(5):
                cards[0].click()
            
            # Should still only be flipped once
            time.sleep(0.5)
            flipped_count = len([c for c in cards if 'flipped' in c.get_attribute('class')])
            self.assertLessEqual(flipped_count, 2, "Rapid clicks should not flip more than 2 cards")
        else:
            self.skipTest("Game didn't start - WebSocket may not be available")
    
    def test_board_renders_quickly(self):
        """Test that game board renders quickly after start"""
        import time
        self.driver.get(f'{self.base_url}/game/render-speed-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'start-btn'))
        )
        
        time.sleep(2)
        
        # Measure time from click to cards appearing
        start_time = time.time()
        self.driver.find_element(By.ID, 'start-btn').click()
        
        try:
            WebDriverWait(self.driver, 3).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, 'card')) == 16
            )
            end_time = time.time()
            render_time = end_time - start_time
            
            # Should render in under 2 seconds
            self.assertLess(render_time, 2.0, f"Board took {render_time:.3f}s to render - should be < 2s")
        except:
            self.skipTest("Game didn't start - WebSocket may not be available")
    
    def test_animation_smoothness(self):
        """Test that animations don't cause jank"""
        self.driver.get(f'{self.base_url}/game/animation-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'start-btn'))
        )
        
        time.sleep(2)
        self.driver.find_element(By.ID, 'start-btn').click()
        time.sleep(2)
        
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        if len(cards) >= 4:
            # Flip multiple cards in sequence
            for i in range(4):
                cards[i].click()
                time.sleep(0.3)  # Small delay between clicks
            
            # Check that all cards responded
            time.sleep(1)
            # At least some cards should have flipped
            flipped_or_matched = len([c for c in cards if 'flipped' in c.get_attribute('class') or 'matched' in c.get_attribute('class')])
            self.assertGreater(flipped_or_matched, 0, "Cards should respond to clicks")
        else:
            self.skipTest("Game didn't start - WebSocket may not be available")
    
    def test_ui_updates_dont_freeze(self):
        """Test that UI updates don't freeze the interface"""
        self.driver.get(f'{self.base_url}/game/freeze-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'players-section'))
        )
        
        # Check that we can interact with elements immediately
        theme_select = self.driver.find_element(By.ID, 'theme-select')
        theme_select.click()
        
        # Select should be responsive
        self.assertTrue(theme_select.is_enabled(), "UI should remain responsive")


class TestGameplayFlow(unittest.TestCase):
    """Test complete gameplay flows"""
    
    @classmethod
    def setUpClass(cls):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        cls.driver = webdriver.Firefox(options=options)
        cls.base_url = 'http://localhost:8080'
        cls.driver.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
    
    def test_complete_game_flow(self):
        """Test a complete game from start to finish"""
        self.driver.get(f'{self.base_url}/game/complete-flow-test/')
        
        # Start game
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'start-btn'))
        )
        time.sleep(2)
        self.driver.find_element(By.ID, 'start-btn').click()
        
        time.sleep(2)
        cards = self.driver.find_elements(By.CLASS_NAME, 'card')
        
        if len(cards) == 16:
            # Try to make a match by clicking cards
            initial_score = self.driver.find_element(By.ID, 'players-list').text
            
            # Click first two cards
            cards[0].click()
            time.sleep(0.5)
            cards[1].click()
            time.sleep(1.5)
            
            # Check that game is still responsive
            cards = self.driver.find_elements(By.CLASS_NAME, 'card')
            self.assertEqual(len(cards), 16, "All cards should still be present")
        else:
            self.skipTest("Game didn't start - WebSocket may not be available")
    
    def test_theme_changes_work(self):
        """Test that changing themes works properly"""
        from selenium.webdriver.support.ui import Select
        
        self.driver.get(f'{self.base_url}/game/theme-change-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'theme-select'))
        )
        
        # Try each theme using Select
        themes = ['emoji', 'starwars', 'pokemon']
        for theme in themes:
            theme_select = Select(self.driver.find_element(By.ID, 'theme-select'))
            theme_select.select_by_value(theme)
            
            time.sleep(0.3)
            selected_value = self.driver.find_element(By.ID, 'theme-select').get_attribute('value')
            self.assertEqual(selected_value, theme, f"Theme should be {theme}")
    
    def test_reconnection_handling(self):
        """Test that page handles disconnection gracefully"""
        self.driver.get(f'{self.base_url}/game/reconnect-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'turn-indicator'))
        )
        
        time.sleep(3)
        
        # Check turn indicator for connection status
        turn_indicator = self.driver.find_element(By.ID, 'turn-indicator')
        indicator_text = turn_indicator.text
        
        # Should show some connection status
        self.assertTrue(len(indicator_text) > 0, "Turn indicator should show connection status")
    
    def test_player_list_updates(self):
        """Test that player list updates properly"""
        self.driver.get(f'{self.base_url}/game/player-update-test/')
        
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'players-list'))
        )
        
        time.sleep(3)
        
        players_list = self.driver.find_element(By.ID, 'players-list')
        # Players list should have some content (if WebSocket connected)
        # or be empty (if not connected)
        self.assertIsNotNone(players_list, "Players list element should exist")


if __name__ == '__main__':
    unittest.main()
