#!/bin/bash
# Script to run comprehensive Selenium tests
# Requires: Redis, Django server running, Chrome/Chromium browser

set -e

echo "🧪 Comprehensive Selenium Test Runner"
echo "======================================"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running. Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

echo "✅ Redis is running"

# Check if server is running on port 8000
if ! curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "❌ Django server is not running on port 8000"
    echo "Please start the server in another terminal:"
    echo "  python manage.py runserver"
    exit 1
fi

echo "✅ Django server is running"

# Check for Chrome/Chromium
if ! command -v google-chrome > /dev/null 2>&1 && ! command -v chromium > /dev/null 2>&1; then
    echo "⚠️  Chrome/Chromium not found - tests may fail"
fi

echo ""
echo "🚀 Running Selenium tests..."
echo ""

# Set test URL
export TEST_URL="http://localhost:8000"

# Run tests with verbose output
python -m pytest tests/test_selenium_comprehensive.py -v -s --tb=short

echo ""
echo "✅ Tests complete!"
