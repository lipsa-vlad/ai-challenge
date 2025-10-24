# Testing Documentation

## Overview

The Memory Game includes comprehensive test coverage with unit tests, integration tests, and Selenium end-to-end tests.

## Test Structure

```
tests/
├── __init__.py
├── test_game_logic.py      # Unit tests for game logic
├── test_views.py            # Django view tests
└── test_integration.py      # Selenium integration tests
```

## Running Tests

### Quick Start

```bash
# Run all unit tests
./run_tests.sh
```

### Individual Test Suites

```bash
# Unit tests only
python -m pytest tests/test_game_logic.py -v

# Django view tests
python -m pytest tests/test_views.py -v

# Integration tests (requires running server)
python manage.py runserver 8080 &
python -m pytest tests/test_integration.py -v -m integration
```

### With Coverage

```bash
# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# View HTML coverage report
open htmlcov/index.html
```

## Test Categories

### 1. Unit Tests (`test_game_logic.py`)

Tests core game logic functions:
- ✅ Card generation for all themes (emoji, Star Wars, Pokemon)
- ✅ Card shuffling randomization
- ✅ API data fetching (SWAPI, PokeAPI)
- ✅ Proper card pairing (8 pairs = 16 cards)

**Example:**
```bash
python -m pytest tests/test_game_logic.py::TestGameLogic::test_get_cards_emoji_theme -v
```

### 2. Django View Tests (`test_views.py`)

Tests HTTP endpoints and views:
- ✅ Lobby page rendering
- ✅ Game room creation
- ✅ API endpoints for new games
- ✅ Static file serving
- ✅ All theme variations

**Example:**
```bash
python -m pytest tests/test_views.py::TestViews::test_new_game_api_emoji_theme -v
```

### 3. Integration Tests (`test_integration.py`)

Selenium-based end-to-end tests:
- ✅ Full user workflows
- ✅ WebSocket connections
- ✅ Card flipping interactions
- ✅ Multi-player functionality
- ✅ Responsive design verification

**Requirements:**
- Firefox with geckodriver OR Chrome with chromedriver
- Running server instance

**Example:**
```bash
# Install browser driver
brew install geckodriver  # or brew install chromedriver

# Start server
python manage.py runserver 8080 &

# Run integration tests
python -m pytest tests/test_integration.py -v
```

## Test Markers

Tests are organized with pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Continuous Integration

GitHub Actions automatically runs tests on:
- Every push to main/develop branches
- All pull requests
- Multiple Python versions

See `.github/workflows/test.yml` for CI configuration.

## Coverage Goals

Current coverage: **42%** (unit + view tests)

Target areas for improvement:
- WebSocket consumers (currently 0%)
- ASGI application (currently 0%)
- URL routing edge cases

## Adding New Tests

### Unit Test Template

```python
def test_new_feature(self):
    """Test description"""
    # Arrange
    input_data = {...}
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    self.assertEqual(result, expected_value)
```

### Integration Test Template

```python
def test_new_user_flow(self):
    """Test description"""
    self.driver.get(f'{self.base_url}/page')
    
    # Find elements
    element = self.driver.find_element(By.ID, 'element-id')
    
    # Interact
    element.click()
    
    # Verify
    self.assertIn('expected', self.driver.page_source)
```

## Troubleshooting

### Common Issues

**Import errors:**
```bash
pip install -r requirements-test.txt
```

**Database errors:**
Settings already configured with in-memory SQLite for tests.

**Selenium errors:**
```bash
# Install browser driver
brew install geckodriver

# Or use headless mode (default in tests)
```

**WebSocket connection fails:**
Ensure Redis is running for integration tests:
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

## Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests fast** - unit tests should run in <5 seconds
3. **Use fixtures** for common setup
4. **Mock external APIs** in unit tests
5. **Test edge cases** and error conditions
6. **Maintain >80% coverage** for critical code paths

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Django testing](https://docs.djangoproject.com/en/4.2/topics/testing/)
- [Selenium Python docs](https://selenium-python.readthedocs.io/)
- [Coverage.py docs](https://coverage.readthedocs.io/)
