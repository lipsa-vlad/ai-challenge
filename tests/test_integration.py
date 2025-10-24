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
        
        # Check for game board
        game_board = self.driver.find_element(By.ID, 'game-board')
        self.assertTrue(game_board.is_displayed())
    
    def test_websocket_connection(self):
        """Test that WebSocket connection is established"""
        self.driver.get(f'{self.base_url}/game/test-ws-room/')
        
        # Wait for connection message in turn indicator
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'turn-indicator'))
        )
        
        time.sleep(2)  # Wait for WebSocket connection
        
        # Check browser console logs (if available)
        logs = self.driver.get_log('browser')
        connection_log = any('Connected to game room' in log['message'] for log in logs)
        
        # If logs not available, check that players list is populated
        players_list = self.driver.find_element(By.ID, 'players-list')
        self.assertTrue(len(players_list.find_elements(By.CLASS_NAME, 'player')) > 0)
    
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
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.find_elements(By.CLASS_NAME, 'card')) == 16
        )
        
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
        WebDriverWait(self.driver, 10).until(
            lambda driver: len(driver.find_elements(By.CLASS_NAME, 'card')) == 16
        )
        
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
        
        # Check that both players see 2 players in the room
        players_list1 = self.driver1.find_element(By.ID, 'players-list')
        players_list2 = self.driver2.find_element(By.ID, 'players-list')
        
        players1 = players_list1.find_elements(By.CLASS_NAME, 'player')
        players2 = players_list2.find_elements(By.CLASS_NAME, 'player')
        
        self.assertEqual(len(players1), 2)
        self.assertEqual(len(players2), 2)


if __name__ == '__main__':
    unittest.main()
