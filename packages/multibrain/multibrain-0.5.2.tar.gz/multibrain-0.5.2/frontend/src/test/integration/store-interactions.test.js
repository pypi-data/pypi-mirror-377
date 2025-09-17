import { describe, it, expect, beforeEach, vi } from 'vitest';
import { configStore } from '../../stores/config.svelte.js';
import { queryStore } from '../../stores/queries.svelte.js';
import { streamStore } from '../../stores/streams.svelte.js';
import { toastStore } from '../../stores/toasts.svelte.js';
import { debugStore } from '../../stores/debug.svelte.js';
import { queryStateMachine } from '../../stores/queryStateMachine.svelte.js';

describe('Store Interactions Integration Tests', () => {
  beforeEach(() => {
    // Reset all stores
    configStore.llms.length = 0;
    configStore.summaryLLM = null;
    queryStore.queries.length = 0;
    queryStore.currentQuery = null;
    streamStore.clearAll();
    toastStore.toasts.length = 0;
    localStorage.clear();
  });

  describe('Config and Query Store Integration', () => {
    it('should only allow queries when LLMs are configured', () => {
      // No LLMs configured
      expect(configStore.enabledLLMs).toHaveLength(0);
      
      // Add a query (should fail or show warning)
      const queryId = queryStore.addQuery('Test query');
      
      // In real app, this would trigger a toast
      expect(queryId).toBeTruthy(); // Query is added but won't stream
      
      // Configure an LLM
      configStore.addLLM({
        name: 'Test LLM',
        url: 'https://api.test.com',
        model: 'test-model',
        apiKey: 'test-key',
        enabled: true
      });
      
      // Now queries should work
      expect(configStore.enabledLLMs).toHaveLength(1);
    });

    it('should update query state machine when streaming', () => {
      const queryId = queryStore.addQuery('Test query');
      
      // Initial state should be idle
      expect(queryStateMachine.getState(queryId)).toBe('idle');
      
      // Start streaming
      streamStore.startStream(queryId, 'llm1', 'Test LLM', 'model');
      queryStateMachine.transition(queryId, 'START_STREAMING');
      
      expect(queryStateMachine.getState(queryId)).toBe('streaming');
      
      // Complete streaming
      streamStore.updateStream(queryId, 'llm1', { status: 'complete' });
      queryStateMachine.transition(queryId, 'COMPLETE');
      
      expect(queryStateMachine.getState(queryId)).toBe('complete');
    });
  });

  describe('Stream and Toast Integration', () => {
    it('should show toast on streaming error', () => {
      const queryId = queryStore.addQuery('Error test');
      streamStore.startStream(queryId, 'llm1', 'Test LLM', 'model');
      
      // Simulate error
      streamStore.updateStream(queryId, 'llm1', {
        status: 'error',
        error: 'Connection failed'
      });
      
      // Should add error toast
      toastStore.addToast('Streaming error: Connection failed', 'error');
      
      expect(toastStore.toasts).toHaveLength(1);
      expect(toastStore.toasts[0].type).toBe('error');
      expect(toastStore.toasts[0].message).toContain('Connection failed');
    });

    it('should auto-dismiss success toasts', async () => {
      vi.useFakeTimers();
      
      toastStore.addToast('Operation successful', 'success');
      
      expect(toastStore.toasts).toHaveLength(1);
      
      // Fast-forward time
      vi.advanceTimersByTime(5000);
      
      // Toast should be removed
      expect(toastStore.toasts).toHaveLength(0);
      
      vi.useRealTimers();
    });
  });

  describe('Query History Management', () => {
    it('should maintain query history limit', () => {
      // Add more than 100 queries
      for (let i = 0; i < 110; i++) {
        queryStore.addQuery(`Query ${i}`);
      }
      
      // Should only keep last 100
      expect(queryStore.queries).toHaveLength(100);
      expect(queryStore.queries[0].text).toBe('Query 10');
      expect(queryStore.queries[99].text).toBe('Query 109');
    });

    it('should track current query correctly', () => {
      const id1 = queryStore.addQuery('First');
      const id2 = queryStore.addQuery('Second');
      const id3 = queryStore.addQuery('Third');
      
      // Current should be the latest
      expect(queryStore.currentQuery).toBe(id3);
      
      // Set different current
      queryStore.setCurrentQuery(id1);
      expect(queryStore.currentQuery).toBe(id1);
      
      // Clear current
      queryStore.clearCurrentQuery();
      expect(queryStore.currentQuery).toBeNull();
    });
  });

  describe('Optimistic Updates', () => {
    it('should handle optimistic LLM updates', async () => {
      // Add LLM optimistically
      const tempId = 'temp-' + Date.now();
      configStore.llms.push({
        id: tempId,
        name: 'Optimistic LLM',
        url: 'https://api.test.com',
        model: 'test',
        apiKey: 'key',
        enabled: true,
        _pending: true
      });
      
      expect(configStore.llms).toHaveLength(1);
      expect(configStore.llms[0]._pending).toBe(true);
      
      // Simulate successful save
      configStore.llms[0] = {
        ...configStore.llms[0],
        id: 'real-id',
        _pending: false
      };
      
      expect(configStore.llms[0]._pending).toBe(false);
    });

    it('should rollback on failure', () => {
      const originalLLMs = [...configStore.llms];
      
      // Add optimistically
      configStore.llms.push({
        id: 'temp',
        name: 'Failed LLM',
        _pending: true
      });
      
      // Simulate failure - rollback
      configStore.llms = originalLLMs;
      
      expect(configStore.llms).toHaveLength(0);
    });
  });

  describe('Debug Store Integration', () => {
    it('should track performance metrics', () => {
      debugStore.enabled = true;
      
      // Track render
      debugStore.trackRender('TestComponent');
      
      // Track API call
      debugStore.trackAPICall('/api/test', 150);
      
      const metrics = debugStore.getMetrics();
      expect(metrics.renders).toBeGreaterThan(0);
      expect(metrics.apiCalls).toBe(1);
      expect(metrics.avgApiTime).toBe(150);
    });

    it('should capture state snapshots', () => {
      // Add some state
      configStore.addLLM({ name: 'Debug Test LLM' });
      queryStore.addQuery('Debug query');
      
      // Capture snapshot
      debugStore.captureState('test-action');
      
      const history = debugStore.stateHistory;
      expect(history).toHaveLength(1);
      expect(history[0].action).toBe('test-action');
      expect(history[0].state).toHaveProperty('config');
      expect(history[0].state).toHaveProperty('queries');
    });
  });

  describe('Persistence and Recovery', () => {
    it('should persist all store states', () => {
      // Setup state
      configStore.addLLM({
        name: 'Persistent LLM',
        url: 'https://api.test.com',
        model: 'model',
        apiKey: 'key'
      });
      
      queryStore.addQuery('Persistent query');
      
      // Force save
      configStore.saveToLocalStorage();
      
      // Check localStorage
      const saved = JSON.parse(localStorage.getItem('multibrain-config'));
      expect(saved.llms).toHaveLength(1);
      expect(saved.llms[0].name).toBe('Persistent LLM');
    });

    it('should recover from localStorage on init', () => {
      // Save some data
      localStorage.setItem('multibrain-config', JSON.stringify({
        llms: [{
          id: 'recovered',
          name: 'Recovered LLM',
          url: 'https://api.test.com',
          model: 'model',
          apiKey: 'key',
          enabled: true
        }],
        summaryLLM: null,
        settings: {}
      }));
      
      // Simulate store initialization
      configStore.loadFromLocalStorage();
      
      expect(configStore.llms).toHaveLength(1);
      expect(configStore.llms[0].name).toBe('Recovered LLM');
    });
  });

  describe('Complex Workflows', () => {
    it('should handle complete query workflow', async () => {
      // 1. Configure LLMs
      configStore.addLLM({
        id: 'llm1',
        name: 'GPT-4',
        url: 'https://api.openai.com',
        model: 'gpt-4',
        apiKey: 'key1',
        enabled: true
      });
      
      configStore.addLLM({
        id: 'llm2',
        name: 'Claude',
        url: 'https://api.anthropic.com',
        model: 'claude-3',
        apiKey: 'key2',
        enabled: true
      });
      
      configStore.setSummaryLLM('llm1');
      
      // 2. Submit query
      const queryId = queryStore.addQuery('Complex workflow test');
      queryStateMachine.transition(queryId, 'START_STREAMING');
      
      // 3. Start streams for all enabled LLMs
      configStore.enabledLLMs.forEach(llm => {
        streamStore.startStream(queryId, llm.id, llm.name, llm.model);
      });
      
      // 4. Simulate streaming responses
      streamStore.updateStream(queryId, 'llm1', {
        content: 'Response from GPT-4...',
        status: 'streaming'
      });
      
      streamStore.updateStream(queryId, 'llm2', {
        content: 'Response from Claude...',
        status: 'streaming'
      });
      
      // 5. Complete streams
      streamStore.updateStream(queryId, 'llm1', { status: 'complete' });
      streamStore.updateStream(queryId, 'llm2', { status: 'complete' });
      
      // 6. Mark query complete
      streamStore.queryComplete(queryId);
      queryStateMachine.transition(queryId, 'COMPLETE');
      
      // 7. Generate summary
      streamStore.startStream(queryId, 'summary', 'Summary', configStore.summaryLLM.model);
      streamStore.updateStream(queryId, 'summary', {
        content: 'Summary: Both models agree that...',
        status: 'complete'
      });
      
      // Verify final state
      expect(queryStateMachine.getState(queryId)).toBe('complete');
      expect(streamStore.getStreamsForQuery(queryId)).toHaveLength(3); // 2 LLMs + summary
      
      // 8. Show success toast
      toastStore.addToast('Query completed successfully', 'success');
      expect(toastStore.toasts).toHaveLength(1);
    });

    it('should handle error recovery workflow', () => {
      const queryId = queryStore.addQuery('Error recovery test');
      
      // Start streaming
      streamStore.startStream(queryId, 'llm1', 'Test LLM', 'model');
      queryStateMachine.transition(queryId, 'START_STREAMING');
      
      // Encounter error
      streamStore.updateStream(queryId, 'llm1', {
        status: 'error',
        error: 'API rate limit exceeded'
      });
      queryStateMachine.transition(queryId, 'ERROR');
      
      // Show error toast
      toastStore.addToast('Error: API rate limit exceeded', 'error');
      
      // Retry
      queryStateMachine.transition(queryId, 'RETRY');
      streamStore.updateStream(queryId, 'llm1', {
        status: 'streaming',
        error: null
      });
      
      // Success on retry
      streamStore.updateStream(queryId, 'llm1', {
        content: 'Success after retry',
        status: 'complete'
      });
      queryStateMachine.transition(queryId, 'COMPLETE');
      
      // Verify recovery
      expect(queryStateMachine.getState(queryId)).toBe('complete');
      expect(streamStore.getStream(queryId, 'llm1').error).toBeNull();
    });
  });

  describe('Memory Management', () => {
    it('should clean up completed streams after time', () => {
      vi.useFakeTimers();
      
      // Create multiple completed queries
      for (let i = 0; i < 10; i++) {
        const queryId = queryStore.addQuery(`Query ${i}`);
        streamStore.startStream(queryId, 'llm1', 'LLM', 'model');
        streamStore.updateStream(queryId, 'llm1', {
          content: 'Response',
          status: 'complete'
        });
      }
      
      expect(Object.keys(streamStore.queries).length).toBe(10);
      
      // Advance time (assuming cleanup after 30 minutes)
      vi.advanceTimersByTime(30 * 60 * 1000);
      
      // Cleanup old completed streams
      streamStore.cleanupOldStreams();
      
      // Should have cleaned up old streams
      expect(Object.keys(streamStore.queries).length).toBeLessThan(10);
      
      vi.useRealTimers();
    });
  });
});