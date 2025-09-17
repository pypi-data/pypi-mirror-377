"""
Test suite for various LLM providers
Tests the compatibility with different OpenAI-compatible endpoints
"""

import asyncio
import json
import os
from typing import Dict, List
import httpx
from datetime import datetime

# Test configurations for various providers
TEST_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "url": "https://api.openai.com/v1",
        "models": ["gpt-3.5-turbo", "gpt-4"],
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "test_prompt": "Say 'Hello from OpenAI' in exactly 5 words.",
    },
    "anthropic": {
        "name": "Anthropic",
        "url": "https://api.anthropic.com/v1",
        "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229"],
        "headers": lambda key: {"X-API-Key": key, "anthropic-version": "2023-06-01"},
        "test_prompt": "Say 'Hello from Anthropic Claude' in exactly 5 words.",
    },
    "groq": {
        "name": "Groq",
        "url": "https://api.groq.com/openai/v1",
        "models": ["mixtral-8x7b-32768", "llama2-70b-4096"],
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "test_prompt": "Say 'Hello from Groq' in exactly 5 words.",
    },
    "ollama": {
        "name": "Ollama (Local)",
        "url": "http://localhost:11434/v1",
        "models": ["llama2", "mistral"],
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "test_prompt": "Say 'Hello from Ollama' in exactly 5 words.",
        "skip_if_no_env": True,  # Skip if no API key provided
    },
    "together": {
        "name": "Together AI",
        "url": "https://api.together.xyz/v1",
        "models": ["mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "headers": lambda key: {"Authorization": f"Bearer {key}"},
        "test_prompt": "Say 'Hello from Together' in exactly 5 words.",
    },
}


class LLMProviderTest:
    """Test class for LLM provider compatibility"""

    def __init__(self, provider_id: str, config: Dict):
        self.provider_id = provider_id
        self.config = config
        self.api_key = os.getenv(f"{provider_id.upper()}_API_KEY", "")
        self.results: List[Dict] = []

    async def test_connection(self) -> Dict:
        """Test basic connection to the provider"""
        if not self.api_key and self.config.get("skip_if_no_env"):
            return {
                "provider": self.provider_id,
                "test": "connection",
                "status": "skipped",
                "message": "No API key provided",
            }

        async with httpx.AsyncClient() as client:
            try:
                headers = self.config["headers"](self.api_key)
                response = await client.get(
                    f"{self.config['url']}/models", headers=headers, timeout=10.0
                )

                return {
                    "provider": self.provider_id,
                    "test": "connection",
                    "status": "success" if response.status_code == 200 else "failed",
                    "status_code": response.status_code,
                    "message": (
                        "Connected successfully"
                        if response.status_code == 200
                        else f"HTTP {response.status_code}"
                    ),
                }
            except Exception as e:
                return {
                    "provider": self.provider_id,
                    "test": "connection",
                    "status": "error",
                    "message": str(e),
                }

    async def test_completion(self, model: str) -> Dict:
        """Test chat completion with a specific model"""
        if not self.api_key:
            return {
                "provider": self.provider_id,
                "test": "completion",
                "model": model,
                "status": "skipped",
                "message": "No API key provided",
            }

        async with httpx.AsyncClient() as client:
            try:
                headers = self.config["headers"](self.api_key)
                headers["Content-Type"] = "application/json"

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": self.config["test_prompt"]}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.1,
                }

                start_time = datetime.now()
                response = await client.post(
                    f"{self.config['url']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                )
                elapsed = (datetime.now() - start_time).total_seconds()

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "provider": self.provider_id,
                        "test": "completion",
                        "model": model,
                        "status": "success",
                        "response": content,
                        "elapsed_seconds": elapsed,
                        "tokens": data.get("usage", {}),
                    }
                else:
                    return {
                        "provider": self.provider_id,
                        "test": "completion",
                        "model": model,
                        "status": "failed",
                        "status_code": response.status_code,
                        "message": response.text[:200],
                    }

            except Exception as e:
                return {
                    "provider": self.provider_id,
                    "test": "completion",
                    "model": model,
                    "status": "error",
                    "message": str(e),
                }

    async def test_streaming(self, model: str) -> Dict:
        """Test streaming chat completion"""
        if not self.api_key:
            return {
                "provider": self.provider_id,
                "test": "streaming",
                "model": model,
                "status": "skipped",
                "message": "No API key provided",
            }

        async with httpx.AsyncClient() as client:
            try:
                headers = self.config["headers"](self.api_key)
                headers["Content-Type"] = "application/json"

                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": "Count from 1 to 5 slowly."}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.1,
                    "stream": True,
                }

                chunks_received = 0
                full_response = ""
                start_time = datetime.now()

                async with client.stream(
                    "POST",
                    f"{self.config['url']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                ) as response:
                    if response.status_code != 200:
                        return {
                            "provider": self.provider_id,
                            "test": "streaming",
                            "model": model,
                            "status": "failed",
                            "status_code": response.status_code,
                        }

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        chunks_received += 1
                                        full_response += delta["content"]
                            except json.JSONDecodeError:
                                pass

                elapsed = (datetime.now() - start_time).total_seconds()

                return {
                    "provider": self.provider_id,
                    "test": "streaming",
                    "model": model,
                    "status": "success",
                    "chunks_received": chunks_received,
                    "response": full_response,
                    "elapsed_seconds": elapsed,
                }

            except Exception as e:
                return {
                    "provider": self.provider_id,
                    "test": "streaming",
                    "model": model,
                    "status": "error",
                    "message": str(e),
                }

    async def run_all_tests(self) -> List[Dict]:
        """Run all tests for this provider"""
        results = []

        # Test connection
        conn_result = await self.test_connection()
        results.append(conn_result)
        print(f"[{self.config['name']}] Connection: {conn_result['status']}")

        # Test each model
        for model in self.config["models"]:
            # Test completion
            comp_result = await self.test_completion(model)
            results.append(comp_result)
            print(
                f"[{self.config['name']}] Completion ({model}): {comp_result['status']}"
            )

            # Test streaming
            stream_result = await self.test_streaming(model)
            results.append(stream_result)
            print(
                f"[{self.config['name']}] Streaming ({model}): {stream_result['status']}"
            )

            # Small delay between tests
            await asyncio.sleep(1)

        return results


async def test_all_providers():
    """Test all configured providers"""
    print("=" * 60)
    print("MultiBrain LLM Provider Compatibility Test")
    print("=" * 60)
    print()

    all_results = {}

    for provider_id, config in TEST_PROVIDERS.items():
        print(f"\nTesting {config['name']}...")
        print("-" * 40)

        tester = LLMProviderTest(provider_id, config)
        results = await tester.run_all_tests()
        all_results[provider_id] = results

    # Generate summary report
    print("\n" + "=" * 60)
    print("SUMMARY REPORT")
    print("=" * 60)

    for provider_id, results in all_results.items():
        provider_name = TEST_PROVIDERS[provider_id]["name"]
        total_tests = len(results)
        successful = sum(1 for r in results if r["status"] == "success")
        failed = sum(1 for r in results if r["status"] == "failed")
        errors = sum(1 for r in results if r["status"] == "error")
        skipped = sum(1 for r in results if r["status"] == "skipped")

        print(f"\n{provider_name}:")
        print(f"  Total Tests: {total_tests}")
        print(f"  ✓ Successful: {successful}")
        if failed > 0:
            print(f"  ✗ Failed: {failed}")
        if errors > 0:
            print(f"  ⚠ Errors: {errors}")
        if skipped > 0:
            print(f"  - Skipped: {skipped}")

        # Show details for failures
        for result in results:
            if result["status"] in ["failed", "error"]:
                test_name = f"{result['test']} ({result.get('model', 'N/A')})"
                message = result.get("message", "Unknown error")
                print(f"    → {test_name}: {message}")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    with open(filename, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nDetailed results saved to: {filename}")


def main():
    """Main entry point"""
    # Check for API keys
    print("Checking for API keys in environment...")
    found_keys = []
    for provider_id in TEST_PROVIDERS:
        key_name = f"{provider_id.upper()}_API_KEY"
        if os.getenv(key_name):
            found_keys.append(provider_id)

    if not found_keys:
        print("\nNo API keys found in environment!")
        print("Please set one or more of the following environment variables:")
        for provider_id in TEST_PROVIDERS:
            print(f"  - {provider_id.upper()}_API_KEY")
        print("\nExample:")
        print("  export OPENAI_API_KEY=sk-...")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        return

    print(f"Found API keys for: {', '.join(found_keys)}")
    print()

    # Run tests
    asyncio.run(test_all_providers())


if __name__ == "__main__":
    main()
