#!/usr/bin/env python3
"""Test script to verify API endpoints are working correctly"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"


def test_endpoint(name, url, method="GET", data=None):
    """Test an endpoint and print the result"""
    print(f"\nTesting {name}: {method} {url}")
    print("-" * 50)

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=data, headers=headers)
        elif method == "HEAD":
            response = requests.head(url)

        print(f"Status Code: {response.status_code}")
        if response.headers.get("content-type", "").startswith("application/json"):
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response: {response.text[:200]}")

        return response.status_code < 400
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all endpoint tests"""
    print("Testing MultiBrain API Endpoints")
    print("=" * 50)

    # Test health endpoints
    test_endpoint("Root Health", f"{BASE_URL}/health")
    test_endpoint("API Health", f"{BASE_URL}/api/health")
    test_endpoint("API Health (HEAD)", f"{BASE_URL}/api/health", method="HEAD")

    # Test API root
    test_endpoint("API Root", f"{BASE_URL}/api")

    # Test validation endpoint (will fail without valid credentials)
    test_data = {
        "url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "apiKey": "test-key",
    }
    test_endpoint(
        "Validate LLM", f"{BASE_URL}/api/validate-llm", method="POST", data=test_data
    )

    # Test streaming endpoint (will fail without valid config)
    stream_data = {
        "query": "Hello",
        "llmConfigs": [
            {
                "id": "test-1",
                "name": "Test LLM",
                "url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo",
                "apiKey": "test-key",
                "enabled": True,
            }
        ],
    }
    test_endpoint(
        "Stream Query", f"{BASE_URL}/api/stream", method="POST", data=stream_data
    )

    print("\n" + "=" * 50)
    print("Testing complete!")


if __name__ == "__main__":
    main()
