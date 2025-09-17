# MultiBrain Refactoring Plan: Streamlit to Svelte

## Executive Summary

This document outlines the plan to refactor MultiBrain from a Streamlit-based application to a modern Svelte application with enhanced features including real-time streaming from multiple LLMs, OpenAI-compatible API support, and user-configurable LLM endpoints. This is a "bring your own keys" application - users provide their own API credentials with no defaults.

## Current State Analysis

### Existing Architecture
- **Frontend**: Streamlit web app with synchronous query/response flow
- **Backend**: FastAPI server using Ollama client library
- **Configuration**: Static TOML file with hardcoded server endpoints
- **Limitations**: 
  - No streaming support (users wait for complete responses)
  - Locked to Ollama API format
  - No user-specific configurations
  - Maximum 16 response servers
  - No persistent user settings

## Requirements Verification

### Core Requirements
1. ✅ **Convert from Streamlit to Svelte** - Complete UI rewrite
2. ✅ **Stream simultaneous results** - Server-Sent Events (SSE) implementation
3. ✅ **OpenAI Compatible endpoints** - Standard `/v1/chat/completions` format
4. ✅ **Dynamic LLM count** - User-configurable, no hardcoded limits
5. ✅ **Custom LLM configuration** - URL, Model, API Key per LLM
6. ✅ **Separate initial/summary LLMs** - Independent configuration
7. ✅ **LocalStorage persistence** - Settings survive page refreshes

## Architecture Design

### Frontend Architecture

#### Technology Stack Decision: Svelte vs SvelteKit

**Svelte** (Chosen):
- ✅ Simpler setup for single-page applications
- ✅ Smaller bundle size (no SSR framework code)
- ✅ Faster initial development
- ✅ Direct deployment as static files
- ❌ No built-in routing (not needed for this SPA)
- ❌ No SSR/SSG capabilities

**SvelteKit** (Alternative):
- ✅ Built-in routing system
- ✅ SSR/SSG for better SEO
- ✅ API routes (we already have FastAPI)
- ❌ More complex setup
- ❌ Larger bundle with SSR runtime
- ❌ Overkill for a single-page app

**Decision**: Use plain Svelte since MultiBrain is a single-page application that doesn't need SEO, routing, or SSR capabilities.

**Final Stack**:
- **Svelte** - Component framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Marked** - Markdown rendering
- **EventSource API** - Native browser SSE support

#### Component Structure
```
src/
├── components/
│   ├── App.svelte              # Main application container
│   ├── QueryInput.svelte       # User query input
│   ├── ResponseContainer.svelte # Manages all response streams
│   ├── ResponseStream.svelte   # Individual LLM response
│   ├── SummaryStream.svelte    # Summary LLM response
│   ├── ConfigModal.svelte      # LLM configuration interface
│   └── LLMConfigForm.svelte    # Add/Edit LLM form
├── stores/
│   ├── config.js               # LLM configurations
│   ├── queries.js              # Query history
│   └── streams.js              # Active response streams
├── lib/
│   ├── api.js                  # API communication
│   ├── storage.js              # LocalStorage wrapper
│   └── streaming.js            # SSE handling
└── App.js                      # Entry point
```

### Backend Architecture

#### API Design Decisions

**API Call Architecture: Proxy Approach**

The backend will proxy all LLM calls for the following reasons:
- ✅ Avoids CORS issues with LLM providers
- ✅ Centralized error handling and retry logic
- ✅ Consistent request/response format
- ✅ Ability to add telemetry if needed
- ❌ Slightly higher latency (negligible with streaming)

**Note on API Keys**: While the backend proxies requests, users still enter their API keys in the browser. The keys are sent to our backend with each request, which then forwards them to the LLM providers. This is necessary for the "bring your own keys" model. The backend never stores these keys.

#### New API Endpoints

```
POST /api/query/stream
  Body: {
    query: string,
    llmConfigs: [{
      id: string,
      url: string,
      model: string,
      apiKey: string (encrypted)
    }],
    summaryConfig: {
      url: string,
      model: string,
      apiKey: string (encrypted)
    }
  }
  Response: SSE stream

POST /api/llm/validate
  Body: { url, model, apiKey }
  Response: { valid: boolean, error?: string }

POST /api/llm/models
  Body: { url, apiKey }
  Response: { models: string[] }
```

### Data Flow

1. User configures LLMs in UI → Stored in LocalStorage
2. User submits query → Frontend sends to backend with LLM configs
3. Backend validates configs and initiates parallel requests
4. Backend streams responses via SSE as they arrive
5. Frontend displays real-time streaming responses
6. When all responses complete, backend queries summary LLM
7. Summary streams to frontend in real-time

## Implementation Details

### LocalStorage Schema

```json
{
  "multibrain_v2": {
    "llms": [
      {
        "id": "uuid-v4",
        "name": "GPT-4",
        "url": "https://api.openai.com/v1",
        "model": "gpt-4",
        "apiKey": "encrypted",
        "enabled": true,
        "order": 0
      }
    ],
    "summaryLLM": {
      "id": "uuid-v4",
      "name": "Claude",
      "url": "https://api.anthropic.com/v1",
      "model": "claude-3-opus",
      "apiKey": "encrypted"
    },
    "settings": {
      "maxConcurrent": 100,
      "streamTimeout": 300000,
      "retryAttempts": 3
    }
  }
}
```

### Security Considerations

1. **API Key Storage**
   - Client-side encryption using Web Crypto API
   - Encryption key derived from a user-provided passphrase
   - Clear warnings about browser security limitations
   - Keys are never stored on the backend

   **Why Encryption over Base64**:
   - Provides basic protection against casual inspection
   - Prevents keys from being visible in browser dev tools
   - Adds a layer of security for shared computers
   - Note: This is not bulletproof - determined attackers with browser access can still extract keys

2. **CORS Handling**
   - Backend proxy eliminates CORS issues entirely
   - No need for domain whitelisting

3. **No Rate Limiting**
   - Users manage their own API quotas
   - No artificial limits imposed by MultiBrain

### Edge Cases & Error Handling

1. **Network Failures**
   - Automatic retry with exponential backoff
   - Graceful degradation (show partial results)
   - Clear error messages per LLM

2. **Streaming Issues**
   - Timeout handling (configurable)
   - Reconnection logic for interrupted streams
   - Partial response recovery

3. **Invalid Configurations**
   - Pre-flight validation before query
   - Test connection button
   - Clear error messages

4. **Performance**
   - High concurrent connection limit (default: 100)
   - Stream buffering for smooth UI
   - Lazy loading of historical queries
   - Browser typically supports 6-8 concurrent connections per domain, but with streaming and HTTP/2, 100 logical streams are feasible

5. **Provider Compatibility**
   - Support different auth methods (Bearer, X-API-Key)
   - Handle various error response formats
   - Flexible timeout configurations

## Implementation Strategy

### Phase 1: Backend Preparation (Week 1)
- Create new streaming endpoints
- Implement OpenAI-compatible proxy
- Add configuration validation
- Remove Ollama dependencies

### Phase 2: Frontend Development (Week 2-3)
- Set up Svelte project
- Implement core components
- Add LocalStorage management with encryption
- Basic streaming UI

### Phase 3: Integration (Week 4)
- Connect frontend to backend
- Test streaming functionality
- Handle edge cases
- Performance optimization

### Phase 4: Polish & Deploy (Week 5)
- UI/UX improvements
- Documentation
- Deployment configuration
- Testing with various LLM providers

## Technical Decisions

### Why Not Over-Engineered
- No unnecessary abstractions
- Simple component hierarchy
- Direct API calls (no GraphQL/tRPC)
- Standard browser APIs (EventSource)
- No state management library (Svelte stores sufficient)

### Why Not Under-Engineered
- Proper error boundaries
- Retry logic for reliability
- Configuration validation
- Streaming timeout handling
- Graceful degradation

## Success Metrics

1. **Performance**
   - First token latency < 500ms
   - Smooth streaming without UI freezes
   - Support 100+ concurrent LLM streams

2. **Reliability**
   - 99% successful query completion
   - Graceful handling of provider outages
   - No data loss on refresh

3. **Usability**
   - Configuration time < 2 minutes
   - Clear error messages
   - Intuitive UI for non-technical users

## Risks & Mitigations

1. **Risk**: API key exposure
   - **Mitigation**: Clear warnings, backend proxy option

2. **Risk**: Provider API changes
   - **Mitigation**: Adapter pattern, version detection

3. **Risk**: Browser connection limits
   - **Mitigation**: Connection pooling, queueing

4. **Risk**: Large response handling
   - **Mitigation**: Streaming, pagination, truncation options

## Future Enhancements

1. **Version 2.1**
   - Export/Import configurations
   - Response caching
   - Query templates

2. **Version 2.2**
   - Team sharing (backend storage)
   - API key vault integration
   - Advanced prompt engineering

3. **Version 3.0**
   - Plugin system for custom providers
   - Response comparison tools
   - Analytics dashboard

## Conclusion

This refactoring plan balances simplicity with robustness, addressing all core requirements while maintaining flexibility for future enhancements. The architecture supports the key goals of streaming multiple LLM responses, user configuration, and persistent settings while handling real-world edge cases effectively.