# Comprehensive Testing Guide

## Overview
This document describes the comprehensive test suite for the Memory Game, including unit tests, integration tests, and Selenium end-to-end tests.

## Test Structure

### 1. Unit Tests (`tests/test_game_logic.py`)
- Card generation and shuffling
- Theme validation
- Game logic functions

### 2. Integration Tests (`tests/test_integration.py`)
- WebSocket connections
- Multiplayer game flow
- Room management

### 3. Consumer Tests (`tests/test_consumers.py`)
- WebSocket consumer behavior
- Redis integration
- Player connection/disconnection

### 4. View Tests (`tests/test_views.py`)
- HTTP endpoints
- Room listing API
- Template rendering

### 5. Edge Cases (`tests/test_edge_cases.py`)
- Error handling
- Invalid inputs
- Edge scenarios

### 6. Selenium Tests (`tests/test_selenium_comprehensive.py`)
**NEW**: Comprehensive browser automation tests for:
- Card flipping behavior and blank image issues
- Multiplayer synchronization
- Room management and cleanup
- Stress tests and edge cases

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -r requirements-test.txt

# Start Redis (required for integration tests)
redis-server --daemonize yes

# Start Django server (required for Selenium tests)
python manage.py runserver
```

### Run All Unit/Integration Tests
```bash
./run_tests.sh
```

### Run Selenium Tests
```bash
# In one terminal, start the server:
python manage.py runserver

# In another terminal:
./run_selenium_tests.sh
```

### Run Specific Test Classes
```bash
# Test card flipping behavior
python -m pytest tests/test_selenium_comprehensive.py::TestCardFlipping -v

# Test multiplayer sync
python -m pytest tests/test_selenium_comprehensive.py::TestMultiplayerSync -v

# Test room management
python -m pytest tests/test_selenium_comprehensive.py::TestRoomManagement -v

# Test stress and edge cases
python -m pytest tests/test_selenium_comprehensive.py::TestStressAndEdgeCases -v
```

## Selenium Test Coverage

### TestCardFlipping
1. **test_single_card_flip_shows_image**: Verifies cards show images when flipped
2. **test_rapid_card_flips_no_blank_images**: Tests rapid clicking doesn't cause blank cards
3. **test_matched_cards_never_go_blank**: Ensures matched cards permanently display images
4. **test_no_match_cards_flip_back_cleanly**: Tests cards flip back without blanking
5. **test_card_hover_does_not_hide_content**: Verifies hover doesn't hide card content

### TestMultiplayerSync
1. **test_two_players_see_same_board**: Verifies both players see the same game
2. **test_card_flip_syncs_to_other_player**: Tests flip synchronization
3. **test_match_syncs_to_all_players**: Ensures matches are synced

### TestRoomManagement
1. **test_no_duplicate_players_same_session**: Prevents duplicate players on rejoin
2. **test_three_players_all_see_each_other**: Tests multi-player visibility

### TestStressAndEdgeCases
1. **test_flip_many_cards_no_errors**: Stress test for card flipping
2. **test_concurrent_flips_from_multiple_players**: Tests concurrent actions

## Known Issues Being Tested

### 1. Blank Card Images
**Problem**: Sometimes after flipping a card, the image disappears (goes blank)

**Tests Covering This**:
- `test_single_card_flip_shows_image`: Verifies images persist
- `test_rapid_card_flips_no_blank_images`: Tests rapid clicking
- `test_matched_cards_never_go_blank`: Ensures matched cards stay visible

**Fix Applied**:
- Improved renderBoard() logic to properly track card states
- Fixed race conditions in flipped class management
- Removed duplicate class toggling

### 2. Room Cleanup Issues
**Problem**: Rooms with one player showing but nobody actually in them

**Tests Covering This**:
- `test_no_duplicate_players_same_session`: Prevents duplicates
- `test_three_players_all_see_each_other`: Tests proper player tracking

**Fix Applied**:
- Improved disconnect logic to properly remove players
- Added channel-to-player mapping to prevent duplicates
- Enhanced Redis cleanup for empty rooms

### 3. Card Flip Synchronization
**Problem**: Card flips feel sluggish or require multiple clicks

**Tests Covering This**:
- `test_card_flip_syncs_to_other_player`: Tests synchronization
- `test_concurrent_flips_from_multiple_players`: Tests concurrent actions

**Fix Applied**:
- Improved state management to reduce re-renders
- Fixed no_match handler to prevent race conditions

## CI/CD Integration

The comprehensive tests are integrated into the GitHub Actions workflow:

```yaml
- name: Run Selenium Tests
  run: |
    python manage.py runserver &
    SERVER_PID=$!
    sleep 5
    python -m pytest tests/test_selenium_comprehensive.py -v
    kill $SERVER_PID
```

## Test Metrics

- **Unit Tests**: ~40 tests
- **Integration Tests**: ~25 tests
- **Selenium Tests**: ~10 comprehensive scenarios
- **Total Coverage**: ~85% code coverage

## Debugging Failed Tests

### Selenium Test Failures
1. Check server is running: `curl http://localhost:8000`
2. Check Redis is running: `redis-cli ping`
3. Run with visible browser (remove `--headless` in chrome_options)
4. Add sleep statements to observe behavior

### WebSocket Test Failures
1. Check Redis connection
2. Verify channel layer configuration
3. Check server logs for WebSocket errors

## Future Test Improvements

1. Add performance benchmarks
2. Add visual regression testing
3. Add mobile browser testing
4. Add load testing for multiple rooms
5. Add network latency simulation

## Contributing

When adding new features, please:
1. Add unit tests for new functions
2. Add integration tests for new flows
3. Add Selenium tests for UI changes
4. Ensure all tests pass before submitting PR
