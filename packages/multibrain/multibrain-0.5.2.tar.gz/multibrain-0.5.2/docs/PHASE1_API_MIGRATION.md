# Phase 1 API Migration Guide

## Overview

Phase 1 of the MultiBrain refactoring introduces new streaming API endpoints that support:
- Server-Sent Events (SSE) for real-time streaming
- OpenAI-compatible API format
- Dynamic LLM configuration
- User-provided API keys (bring your own keys)

## New API Endpoints

### 1. Stream Query Endpoint
**POST** `/api/query/stream`

Streams responses from multiple LLMs in real-time using Server-Sent Events.

**Request Body:**
```json
{
  "query": "Your question here",
  "llmConfigs": [
    {
      "id": "unique-id",
      "name": "GPT-4",
      "url": "https://api.openai.com/v1",
      "model": "gpt-4",
      "apiKey": "your-api-key",
      "enabled": true
    }
  ],
  "summaryConfig": {
    "id": "summary-id",
    "name": "Claude",
    "url": "https://api.anthropic.com/v1",
    "model": "claude-3-opus",
    "apiKey": "your-api-key"
  }
}
```

**Response:** Server-Sent Events stream with the following event types:
- `llm_start` - Indicates an LLM has started processing
- `llm_chunk` - Contains a chunk of text from an LLM response
- `llm_complete` - Indicates an LLM has finished responding
- `llm_error` - Contains error information if an LLM fails
- `summary_start` - Indicates summary generation has started
- `summary_chunk` - Contains a chunk of the summary text
- `summary_complete` - Indicates summary generation is complete
- `query_complete` - Indicates the entire query process is complete

**Example SSE Event:**
```
data: {"type": "llm_chunk", "llm_id": "unique-id", "content": "Paris is", "timestamp": "2024-01-15T10:30:00Z"}
```

### 2. Validate LLM Configuration
**POST** `/api/llm/validate`

Tests if an LLM configuration is valid by making a test request.

**Request Body:**
```json
{
  "url": "https://api.openai.com/v1",
  "model": "gpt-3.5-turbo",
  "apiKey": "your-api-key"
}
```

**Response:**
```json
{
  "valid": true
}
```
or
```json
{
  "valid": false,
  "error": "HTTP 401: Invalid API key"
}
```

### 3. List Available Models
**POST** `/api/llm/models`

Fetches available models from an LLM provider.

**Request Body:**
```json
{
  "url": "https://api.openai.com/v1",
  "apiKey": "your-api-key"
}
```

**Response:**
```json
{
  "models": ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"]
}
```

## Legacy Endpoint (Deprecated)

The original `/query` endpoint is maintained for backward compatibility but is marked as deprecated. It now uses OpenAI-compatible format instead of Ollama.

## Migration Steps

### 1. Update Dependencies

Remove `ollama` from your dependencies and add:
```toml
httpx = "^0.24.0"
sse-starlette = "^1.6.0"
pydantic = "^2.0.0"
```

### 2. Update Configuration Format

Old format (config.toml):
```toml
[[response_servers]]
host = "http://localhost:11434"
model = "llama2"
color = "blue-box"
```

New format (sent with each request):
```json
{
  "id": "server-1",
  "name": "Local Llama",
  "url": "http://localhost:11434/v1",
  "model": "llama2",
  "apiKey": "",
  "enabled": true
}
```

### 3. Handle Streaming Responses

Example JavaScript client:
```javascript
const response = await fetch('/api/query/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'Your question',
    llmConfigs: [...],
    summaryConfig: {...}
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  
  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      // Handle different event types
      switch (data.type) {
        case 'llm_chunk':
          console.log(`LLM ${data.llm_id}: ${data.content}`);
          break;
        // ... handle other event types
      }
    }
  }
}
```

## Supported LLM Providers

The new API supports any OpenAI-compatible endpoint, including:
- OpenAI (https://api.openai.com/v1)
- Anthropic Claude (https://api.anthropic.com/v1)
- Local Ollama with OpenAI compatibility (http://localhost:11434/v1)
- Azure OpenAI
- Any other OpenAI-compatible service

## Authentication

Different providers use different authentication methods:
- **OpenAI**: Bearer token in Authorization header
- **Anthropic**: X-API-Key header
- **Local services**: Often no authentication required

The API automatically detects and uses the appropriate authentication method based on the URL.

## Error Handling

Errors are returned as SSE events with type `llm_error`:
```
data: {"type": "llm_error", "llm_id": "unique-id", "error": "Connection timeout", "timestamp": "2024-01-15T10:30:00Z"}
```

The streaming continues even if individual LLMs fail, allowing partial results.

## Testing

Use the provided `test_streaming_api.py` script to test the new endpoints:
```bash
python test_streaming_api.py
```

Remember to update the API keys in the test script before running.

## Next Steps

Phase 2 will introduce:
- Svelte frontend with real-time streaming UI
- LocalStorage for configuration persistence
- Enhanced error handling and retry logic
- Performance optimizations for 100+ concurrent LLMs