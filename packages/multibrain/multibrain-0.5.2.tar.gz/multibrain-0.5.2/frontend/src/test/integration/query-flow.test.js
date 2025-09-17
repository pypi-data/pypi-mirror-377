import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import App from '../../App.svelte';
import QueryInput from '../../components/QueryInput.svelte';
import QueryResponseContainer from '../../components/QueryResponseContainer.svelte';
import { queryStore } from '../../stores/queries.svelte.js';
import { streamStore } from '../../stores/streams.svelte.js';
import { configStore } from '../../stores/config.svelte.js';

describe('Query Flow Integration Tests', () => {
  let mockEventSource;
  
  beforeEach(() => {
    // Reset stores
    queryStore.queries.length = 0;
    queryStore.currentQuery = null;
    streamStore.clearAll();
    
    // Setup test LLMs
    configStore.llms = [
      {
        id: 'llm1',
        name: 'Test LLM 1',
        url: 'https://api.test1.com',
        model: 'test-model-1',
        apiKey: 'key1',
        enabled: true
      },
      {
        id: 'llm2',
        name: 'Test LLM 2',
        url: 'https://api.test2.com',
        model: 'test-model-2',
        apiKey: 'key2',
        enabled: true
      }
    ];
    
    configStore.summaryLLM = {
      id: 'summary',
      name: 'Summary LLM',
      url: 'https://api.summary.com',
      model: 'summary-model',
      apiKey: 'summary-key'
    };
    
    // Mock EventSource
    mockEventSource = {
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      readyState: 1 // OPEN
    };
    
    global.EventSource = vi.fn(() => mockEventSource);
  });
  
  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('QueryInput Component', () => {
    it('should handle query submission', async () => {
      const user = userEvent.setup();
      const onsubmit = vi.fn();
      
      render(QueryInput, { props: { onsubmit } });
      
      const textarea = screen.getByPlaceholderText(/ask a question/i);
      const submitButton = screen.getByRole('button');
      
      // Button should be disabled initially
      expect(submitButton).toBeDisabled();
      
      // Type a query
      await user.type(textarea, 'What is the meaning of life?');
      
      // Button should now be enabled
      expect(submitButton).not.toBeDisabled();
      
      // Submit the query
      await fireEvent.click(submitButton);
      
      // Callback should be called with the query
      expect(onsubmit).toHaveBeenCalledWith('What is the meaning of life?');
      
      // Input should be cleared
      expect(textarea.value).toBe('');
    });

    it('should handle Enter key submission', async () => {
      const user = userEvent.setup();
      const onsubmit = vi.fn();
      
      render(QueryInput, { props: { onsubmit } });
      
      const textarea = screen.getByPlaceholderText(/ask a question/i);
      
      // Type and press Enter
      await user.type(textarea, 'Test query');
      await user.keyboard('{Enter}');
      
      expect(onsubmit).toHaveBeenCalledWith('Test query');
    });

    it('should handle Shift+Enter for new line', async () => {
      const user = userEvent.setup();
      const onsubmit = vi.fn();
      
      render(QueryInput, { props: { onsubmit } });
      
      const textarea = screen.getByPlaceholderText(/ask a question/i);
      
      // Type and press Shift+Enter
      await user.type(textarea, 'Line 1');
      await user.keyboard('{Shift>}{Enter}{/Shift}');
      await user.type(textarea, 'Line 2');
      
      // Should not submit
      expect(onsubmit).not.toHaveBeenCalled();
      
      // Should have multiline text
      expect(textarea.value).toBe('Line 1\nLine 2');
    });

    it('should support two-way binding', async () => {
      const user = userEvent.setup();
      let value = 'Initial value';
      
      const { rerender } = render(QueryInput, { 
        props: { 
          value,
          onsubmit: vi.fn() 
        } 
      });
      
      const textarea = screen.getByPlaceholderText(/ask a question/i);
      expect(textarea.value).toBe('Initial value');
      
      // Update from outside
      value = 'Updated value';
      await rerender({ 
        props: { 
          value,
          onsubmit: vi.fn() 
        } 
      });
      
      expect(textarea.value).toBe('Updated value');
    });
  });

  describe('Query Response Container', () => {
    it('should display query history', () => {
      // Add some queries to history
      queryStore.addQuery('First query');
      queryStore.addQuery('Second query');
      
      render(QueryResponseContainer, { props: {} });
      
      expect(screen.getByText('First query')).toBeInTheDocument();
      expect(screen.getByText('Second query')).toBeInTheDocument();
    });

    it('should show active streaming indicators', async () => {
      // Add a query and start streaming
      const queryId = queryStore.addQuery('Test query');
      streamStore.startStream(queryId, 'llm1', 'Test LLM 1', 'test-model-1');
      
      render(QueryResponseContainer, { props: {} });
      
      // Should show streaming indicator
      await waitFor(() => {
        expect(screen.getByText('Streaming...')).toBeInTheDocument();
      });
    });

    it('should handle query selection', async () => {
      const user = userEvent.setup();
      
      // Add multiple queries
      queryStore.addQuery('Query 1');
      const queryId2 = queryStore.addQuery('Query 2');
      
      render(QueryResponseContainer, { props: {} });
      
      // Click on second query
      const query2Element = screen.getByText('Query 2');
      await fireEvent.click(query2Element);
      
      // Should set as current query
      expect(queryStore.currentQuery).toBe(queryId2);
    });
  });

  describe('Full Query Flow', () => {
    it('should complete full query submission and streaming flow', async () => {
      const user = userEvent.setup();
      
      // Mock fetch for API validation
      global.fetch = vi.fn(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({})
        })
      );
      
      render(App);
      
      // Wait for app to initialize
      await waitFor(() => {
        expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
      });
      
      // Find and fill query input
      const queryInput = screen.getByPlaceholderText(/ask a question/i);
      await user.type(queryInput, 'What is AI?');
      
      // Submit query
      const submitButton = screen.getByRole('button', { name: /submit/i });
      await fireEvent.click(submitButton);
      
      // Verify query was added to store
      expect(queryStore.queries).toHaveLength(1);
      expect(queryStore.queries[0].text).toBe('What is AI?');
      
      // Verify streaming started
      expect(global.EventSource).toHaveBeenCalled();
      
      // Simulate streaming data
      const messageHandler = mockEventSource.addEventListener.mock.calls
        .find(call => call[0] === 'message')[1];
      
      // Send some streaming data
      messageHandler({
        data: JSON.stringify({
          queryId: queryStore.queries[0].id,
          llmId: 'llm1',
          content: 'AI stands for Artificial Intelligence...',
          status: 'streaming'
        })
      });
      
      // Verify content appears
      await waitFor(() => {
        expect(screen.getByText(/AI stands for Artificial Intelligence/)).toBeInTheDocument();
      });
      
      // Complete the stream
      messageHandler({
        data: JSON.stringify({
          queryId: queryStore.queries[0].id,
          llmId: 'llm1',
          status: 'complete'
        })
      });
      
      // Verify completion
      await waitFor(() => {
        expect(screen.getByText('Complete')).toBeInTheDocument();
      });
    });

    it('should handle streaming errors', async () => {
      render(App);
      
      // Submit a query
      const queryId = queryStore.addQuery('Test error query');
      streamStore.startStream(queryId, 'llm1', 'Test LLM', 'model');
      
      // Simulate error event
      const errorHandler = mockEventSource.addEventListener.mock.calls
        .find(call => call[0] === 'error')[1];
      
      errorHandler(new Event('error'));
      
      // Should show error state
      await waitFor(() => {
        const stream = streamStore.getStream(queryId, 'llm1');
        expect(stream.status).toBe('error');
      });
    });

    it('should handle abort functionality', async () => {
      const user = userEvent.setup();
      
      render(App);
      
      // Submit a query
      const queryInput = screen.getByPlaceholderText(/ask a question/i);
      await user.type(queryInput, 'Long running query');
      await fireEvent.click(screen.getByRole('button', { name: /submit/i }));
      
      // Find abort button (assuming it appears during streaming)
      const abortButton = await screen.findByText(/abort|stop|cancel/i);
      await fireEvent.click(abortButton);
      
      // Verify EventSource was closed
      expect(mockEventSource.close).toHaveBeenCalled();
      
      // Verify streams were aborted
      const streams = streamStore.getStreamsForQuery(queryStore.queries[0].id);
      streams.forEach(stream => {
        expect(stream.status).toBe('aborted');
      });
    });
  });

  describe('Summary Generation', () => {
    it('should generate summary after all streams complete', async () => {
      render(App);
      
      const queryId = queryStore.addQuery('Test summary query');
      
      // Start streams for all LLMs
      streamStore.startStream(queryId, 'llm1', 'LLM 1', 'model1');
      streamStore.startStream(queryId, 'llm2', 'LLM 2', 'model2');
      
      // Complete both streams
      streamStore.updateStream(queryId, 'llm1', {
        content: 'Response from LLM 1',
        status: 'complete'
      });
      
      streamStore.updateStream(queryId, 'llm2', {
        content: 'Response from LLM 2',
        status: 'complete'
      });
      
      // Mark query as complete
      streamStore.queryComplete(queryId);
      
      // Should start summary generation
      await waitFor(() => {
        const summaryStream = streamStore.getStream(queryId, 'summary');
        expect(summaryStream).toBeTruthy();
        expect(summaryStream.status).toBe('streaming');
      });
    });
  });

  describe('Keyboard Shortcuts', () => {
    it('should focus query input with Ctrl+K', async () => {
      const user = userEvent.setup();
      
      render(App);
      
      const queryInput = screen.getByPlaceholderText(/ask a question/i);
      
      // Input should not be focused initially
      expect(document.activeElement).not.toBe(queryInput);
      
      // Press Ctrl+K
      await user.keyboard('{Control>}k{/Control}');
      
      // Input should now be focused
      expect(document.activeElement).toBe(queryInput);
    });

    it('should clear query with Escape', async () => {
      const user = userEvent.setup();
      
      render(App);
      
      const queryInput = screen.getByPlaceholderText(/ask a question/i);
      
      // Type something
      await user.type(queryInput, 'Test query');
      expect(queryInput.value).toBe('Test query');
      
      // Press Escape
      await user.keyboard('{Escape}');
      
      // Input should be cleared
      expect(queryInput.value).toBe('');
    });
  });

  describe('Performance', () => {
    it('should handle large number of queries efficiently', async () => {
      const startTime = performance.now();
      
      // Add 100 queries
      for (let i = 0; i < 100; i++) {
        queryStore.addQuery(`Query ${i}`);
      }
      
      render(QueryResponseContainer, { props: {} });
      
      // Should render within reasonable time
      const renderTime = performance.now() - startTime;
      expect(renderTime).toBeLessThan(1000); // 1 second
      
      // Should display all queries
      expect(screen.getByText('Query 0')).toBeInTheDocument();
      expect(screen.getByText('Query 99')).toBeInTheDocument();
    });

    it('should handle rapid streaming updates', async () => {
      render(App);
      
      const queryId = queryStore.addQuery('Performance test');
      streamStore.startStream(queryId, 'llm1', 'Test LLM', 'model');
      
      // Simulate rapid updates
      const messageHandler = mockEventSource.addEventListener.mock.calls
        .find(call => call[0] === 'message')[1];
      
      let content = '';
      for (let i = 0; i < 100; i++) {
        content += `Word ${i} `;
        messageHandler({
          data: JSON.stringify({
            queryId,
            llmId: 'llm1',
            content,
            status: 'streaming'
          })
        });
      }
      
      // Should handle all updates without crashing
      await waitFor(() => {
        expect(screen.getByText(/Word 99/)).toBeInTheDocument();
      });
    });
  });
});