#!/bin/bash

# Run all tests for the Memory Game application

echo "🧪 Running Memory Game Tests..."
echo "================================"

# Install test dependencies
echo "📦 Installing test dependencies..."
pip install -q -r requirements-test.txt

# Run unit tests
echo ""
echo "🔬 Running Unit Tests..."
python -m pytest tests/test_game_logic.py tests/test_views.py -v -m "not integration"

# Run Django tests
echo ""
echo "🌐 Running Django Tests..."
python manage.py test --verbosity=2

# Check if Selenium tests should run (requires browser driver)
if command -v geckodriver &> /dev/null || command -v chromedriver &> /dev/null; then
    echo ""
    echo "🌍 Running Integration Tests with Selenium..."
    echo "⚠️  Note: This requires a running instance at http://localhost:8080"
    echo "    You can start one with: python manage.py runserver 8080"
    read -p "Press Enter to continue with integration tests or Ctrl+C to skip..."
    python -m pytest tests/test_integration.py -v -m integration
else
    echo ""
    echo "⚠️  Skipping Selenium tests (no browser driver found)"
    echo "    Install with: brew install geckodriver  OR  brew install chromedriver"
fi

# Generate coverage report
echo ""
echo "📊 Generating Coverage Report..."
coverage report
coverage html
echo "📁 HTML coverage report generated in htmlcov/index.html"

echo ""
echo "✅ All tests completed!"
