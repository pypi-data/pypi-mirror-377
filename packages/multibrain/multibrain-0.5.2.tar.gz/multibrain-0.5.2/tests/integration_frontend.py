"""
Frontend integration tests for MultiBrain
Tests the complete flow from frontend to backend with multiple LLMs
"""

import asyncio
import json
import time
from typing import Dict, List, Any
import httpx
from datetime import datetime

# Test configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# Sample test configurations
TEST_CONFIGS: List[Dict[str, Any]] = [
    {
        "name": "Basic Query Test",
        "query": "What is 2+2?",
        "llms": [
            {
                "id": "test-openai",
                "name": "Test OpenAI",
                "url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo",
                "apiKey": "test-key",
                "enabled": True,
            }
        ],
        "expected_events": ["llm_start", "llm_chunk", "llm_complete", "query_complete"],
    },
    {
        "name": "Multiple LLMs Test",
        "query": "Explain quantum computing in one sentence.",
        "llms": [
            {
                "id": "test-llm-1",
                "name": "Test LLM 1",
                "url": "https://api.openai.com/v1",
                "model": "gpt-3.5-turbo",
                "apiKey": "test-key-1",
                "enabled": True,
            },
            {
                "id": "test-llm-2",
                "name": "Test LLM 2",
                "url": "https://api.anthropic.com/v1",
                "model": "claude-3-haiku",
                "apiKey": "test-key-2",
                "enabled": True,
            },
        ],
        "summaryLLM": {
            "id": "test-summary",
            "name": "Test Summary",
            "url": "https://api.openai.com/v1",
            "model": "gpt-4",
            "apiKey": "test-key-summary",
        },
        "expected_events": [
            "llm_start",
            "llm_chunk",
            "llm_complete",
            "summary_start",
            "summary_chunk",
            "summary_complete",
            "query_complete",
        ],
    },
]


class FrontendIntegrationTest:
    """Test class for frontend-backend integration"""

    def __init__(self):
        self.results = []

    async def test_health_check(self) -> Dict:
        """Test API health check endpoint"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{API_BASE_URL}/health")
                return {
                    "test": "health_check",
                    "status": "success" if response.status_code == 200 else "failed",
                    "response": (
                        response.json() if response.status_code == 200 else None
                    ),
                }
            except Exception as e:
                return {"test": "health_check", "status": "error", "message": str(e)}

    async def test_cors_headers(self) -> Dict:
        """Test CORS headers for frontend access"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.options(
                    f"{API_BASE_URL}/api/query/stream",
                    headers={
                        "Origin": FRONTEND_URL,
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "content-type",
                    },
                )

                cors_headers = {
                    "allow_origin": response.headers.get("access-control-allow-origin"),
                    "allow_methods": response.headers.get(
                        "access-control-allow-methods"
                    ),
                    "allow_headers": response.headers.get(
                        "access-control-allow-headers"
                    ),
                }

                return {
                    "test": "cors_headers",
                    "status": "success" if response.status_code == 200 else "failed",
                    "cors_headers": cors_headers,
                }
            except Exception as e:
                return {"test": "cors_headers", "status": "error", "message": str(e)}

    async def test_streaming_query(self, test_config: Dict) -> Dict:
        """Test streaming query with SSE"""
        result = {
            "test": "streaming_query",
            "name": test_config["name"],
            "events_received": [],
            "chunks": {},
            "timing": {},
        }

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            try:
                # Prepare request payload
                payload = {
                    "query": test_config["query"],
                    "llmConfigs": test_config["llms"],
                }

                if "summaryLLM" in test_config:
                    payload["summaryConfig"] = test_config["summaryLLM"]

                # Make streaming request
                async with client.stream(
                    "POST",
                    f"{API_BASE_URL}/api/query/stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"},
                    timeout=60.0,
                ) as response:

                    if response.status_code != 200:
                        result["status"] = "failed"
                        result["status_code"] = response.status_code
                        result["error"] = await response.aread()
                        return result

                    # Process SSE stream
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break

                            try:
                                event = json.loads(data)
                                event_type = event.get("type")
                                result["events_received"].append(event_type)

                                # Track chunks per LLM
                                if event_type == "llm_chunk":
                                    llm_id = event.get("llm_id")
                                    if llm_id not in result["chunks"]:
                                        result["chunks"][llm_id] = ""
                                    result["chunks"][llm_id] += event.get("content", "")

                                # Track timing
                                if event_type == "llm_start":
                                    llm_id = event.get("llm_id")
                                    result["timing"][f"{llm_id}_start"] = (
                                        time.time() - start_time
                                    )
                                elif event_type == "llm_complete":
                                    llm_id = event.get("llm_id")
                                    result["timing"][f"{llm_id}_complete"] = (
                                        time.time() - start_time
                                    )

                            except json.JSONDecodeError:
                                result["events_received"].append("invalid_json")

                result["status"] = "success"
                result["total_time"] = time.time() - start_time

                # Verify expected events
                expected = set(test_config.get("expected_events", []))
                received = set(result["events_received"])
                result["missing_events"] = list(expected - received)
                result["unexpected_events"] = list(received - expected)

            except Exception as e:
                result["status"] = "error"
                result["message"] = str(e)

        return result

    async def test_validation_endpoint(self) -> Dict:
        """Test LLM validation endpoint"""
        async with httpx.AsyncClient() as client:
            try:
                # Test with invalid configuration
                response = await client.post(
                    f"{API_BASE_URL}/api/llm/validate",
                    json={
                        "url": "https://invalid.example.com",
                        "model": "invalid-model",
                        "apiKey": "invalid-key",
                    },
                )

                return {
                    "test": "validation_endpoint",
                    "status": "success" if response.status_code == 200 else "failed",
                    "response": (
                        response.json() if response.status_code == 200 else None
                    ),
                }
            except Exception as e:
                return {
                    "test": "validation_endpoint",
                    "status": "error",
                    "message": str(e),
                }

    async def test_concurrent_queries(self) -> Dict:
        """Test multiple concurrent queries"""
        result: Dict[str, Any] = {
            "test": "concurrent_queries",
            "queries_sent": 3,
            "queries_completed": 0,
            "errors": [],
        }

        async def run_query(query_num: int):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{API_BASE_URL}/api/query/stream",
                        json={
                            "query": f"Test query {query_num}",
                            "llmConfigs": [
                                {
                                    "id": f"test-{query_num}",
                                    "name": f"Test LLM {query_num}",
                                    "url": "https://api.openai.com/v1",
                                    "model": "gpt-3.5-turbo",
                                    "apiKey": "test-key",
                                    "enabled": True,
                                }
                            ],
                        },
                        timeout=30.0,
                    )

                    if response.status_code == 200:
                        # Just read the response to completion
                        await response.aread()
                        return True
                    else:
                        if isinstance(result["errors"], list):
                            result["errors"].append(
                                f"Query {query_num}: HTTP {response.status_code}"
                            )
                        return False
            except Exception as e:
                if isinstance(result["errors"], list):
                    result["errors"].append(f"Query {query_num}: {str(e)}")
                return False

        # Run concurrent queries
        tasks = [run_query(i) for i in range(1, 4)]
        results = await asyncio.gather(*tasks)
        result["queries_completed"] = sum(1 for r in results if r)
        result["status"] = "success" if result["queries_completed"] == 3 else "partial"

        return result

    async def run_all_tests(self) -> List[Dict]:
        """Run all integration tests"""
        results = []

        # Test health check
        print("Testing health check...")
        health_result = await self.test_health_check()
        results.append(health_result)
        print(f"  Status: {health_result['status']}")

        # Test CORS headers
        print("Testing CORS headers...")
        cors_result = await self.test_cors_headers()
        results.append(cors_result)
        print(f"  Status: {cors_result['status']}")

        # Test validation endpoint
        print("Testing validation endpoint...")
        validation_result = await self.test_validation_endpoint()
        results.append(validation_result)
        print(f"  Status: {validation_result['status']}")

        # Test streaming queries
        for config in TEST_CONFIGS:
            print(f"\nTesting: {config['name']}...")
            stream_result = await self.test_streaming_query(config)
            results.append(stream_result)
            print(f"  Status: {stream_result['status']}")
            print(f"  Events: {len(stream_result.get('events_received', []))}")
            if stream_result.get("missing_events"):
                print(f"  Missing events: {stream_result['missing_events']}")

        # Test concurrent queries
        print("\nTesting concurrent queries...")
        concurrent_result = await self.test_concurrent_queries()
        results.append(concurrent_result)
        print(f"  Status: {concurrent_result['status']}")
        print(
            f"  Completed: {concurrent_result['queries_completed']}/{concurrent_result['queries_sent']}"
        )

        return results


async def main():
    """Main test runner"""
    print("=" * 60)
    print("MultiBrain Frontend Integration Tests")
    print("=" * 60)
    print()
    print(f"API URL: {API_BASE_URL}")
    print(f"Frontend URL: {FRONTEND_URL}")
    print()

    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5.0)
            if response.status_code != 200:
                print("ERROR: API server is not responding!")
                print("Please start the API server with: multibrain-api")
                return
    except Exception as e:
        print(f"ERROR: Cannot connect to API server: {e}")
        print("Please start the API server with: multibrain-api")
        return

    print("API server is running ✓")
    print()

    # Run tests
    tester = FrontendIntegrationTest()
    results = await tester.run_all_tests()

    # Generate summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_tests = len(results)
    successful = sum(1 for r in results if r.get("status") == "success")
    failed = sum(1 for r in results if r.get("status") == "failed")
    errors = sum(1 for r in results if r.get("status") == "error")

    print(f"\nTotal Tests: {total_tests}")
    print(f"✓ Successful: {successful}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
    if errors > 0:
        print(f"⚠ Errors: {errors}")

    # Show details for failures
    failures = [r for r in results if r.get("status") in ["failed", "error"]]
    if failures:
        print("\nFailure Details:")
        for result in failures:
            print(f"  - {result['test']}: {result.get('message', 'Unknown error')}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"integration_test_results_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {filename}")

    # Return exit code
    return 0 if failed == 0 and errors == 0 else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
