import { streamMultipleQueries } from '../lib/streaming';
import { ConnectionMonitor } from '../lib/errorHandling';
import { debugStore, debugInspect } from './debug.svelte';
import type { StreamStore, Stream, SummaryStream, QueryStreamData, LLMConfig } from '../types';

interface StreamUpdate {
  type?: string;
  streamId?: string;
  llm?: LLMConfig;
  content?: string;
  status?: string;
  error?: string | null;
  metrics?: any;
}

/**
 * Create a store for managing streaming responses
 */
function createStreamStore(): StreamStore & { destroy(): void } {
  // Use $state.raw for queries object to avoid deep reactivity overhead
  // This is more performant for large objects with response data
  let queries = $state.raw<Record<string, QueryStreamData>>({}); // Map of queryId -> { streams, summary, isStreaming, error }
  let isOnline = $state(true);
  
  // Abort controllers map (not reactive, just internal state)
  const abortControllers = new Map<string, AbortController>(); // Map of queryId -> AbortController
  
  // Monitor connection status
  let connectionMonitor: ConnectionMonitor | null = null;
  
  // Debug inspection - removed $effect as it can't be used in stores
  
  // Initialize connection monitor
  connectionMonitor = new ConnectionMonitor((online: boolean) => {
    isOnline = online;
    if (!online) {
      // With $state.raw, create a new object for updates
      const updatedQueries: Record<string, QueryStreamData> = { ...queries };
      Object.keys(updatedQueries).forEach(queryId => {
        if (updatedQueries[queryId].isStreaming) {
          updatedQueries[queryId] = {
            ...updatedQueries[queryId],
            error: 'Internet connection lost. Please check your connection.'
          };
        }
      });
      queries = updatedQueries;
    }
  });

  return {
    // Getters for reactive access
    get queries(): Record<string, QueryStreamData> { return queries; },
    get isOnline(): boolean { return isOnline; },
    
    // Start streaming from all configured LLMs
    async startStreaming(query: string, config: { llms: LLMConfig[]; summaryLLM: LLMConfig | null }, queryId: string): Promise<void> {
      // Check connection first
      if (!navigator.onLine) {
        // With $state.raw, create a new object
        queries = {
          ...queries,
          [queryId]: {
            streams: [],
            summary: null,
            isStreaming: false,
            error: 'No internet connection. Please check your connection and try again.'
          }
        };
        return;
      }
      
      // Initialize query state with $state.raw
      queries = {
        ...queries,
        [queryId]: {
          streams: [],
          summary: null,
          isStreaming: true,
          error: null,
          context: null,
          isFollowUp: false
        }
      };
      
      // Create abort controller for this query
      const abortController = new AbortController();
      abortControllers.set(queryId, abortController);
      
      // Get enabled LLMs
      const enabledLLMs = config.llms.filter(llm => llm.enabled);
      
      if (enabledLLMs.length === 0) {
        // With $state.raw, create a new object
        queries = {
          ...queries,
          [queryId]: {
            streams: [],
            summary: null,
            isStreaming: false,
            error: 'No LLMs are enabled. Please configure at least one LLM.'
          }
        };
        return;
      }
      
      // Create stream objects for each LLM
      const streamObjects: Stream[] = enabledLLMs.map(llm => ({
        id: llm.id,
        llmId: llm.id,
        llmName: llm.name,
        model: llm.model,
        content: '',
        status: 'waiting', // waiting, streaming, complete, error
        error: null,
        metrics: {
          startTime: Date.now(),
          firstTokenTime: null,
          totalTime: null,
          tokensPerSecond: null
        }
      }));
      
      // Update store with initial stream objects using $state.raw
      queries = {
        ...queries,
        [queryId]: {
          ...queries[queryId],
          streams: streamObjects
        }
      };
      
      // Start streaming using the unified endpoint
      try {
        await streamMultipleQueries({
          query,
          llms: enabledLLMs,
          summaryLLM: config.summaryLLM,
          onUpdate: (updateData: StreamUpdate) => {
            // Handle global errors with $state.raw
            if (updateData.type === 'global_error') {
              queries = {
                ...queries,
                [queryId]: {
                  ...queries[queryId],
                  isStreaming: false,
                  error: updateData.error || 'An error occurred'
                }
              };
              return;
            }
            
            // Handle stream updates
            const { streamId, ...streamData } = updateData;
            
            if (streamId === 'summary') {
              // Update summary stream with $state.raw
              const currentSummary = queries[queryId].summary;
              
              // For streaming content, append instead of replace
              let newContent = streamData.content || '';
              if (currentSummary && streamData.status === 'streaming' && streamData.content) {
                newContent = currentSummary.content + streamData.content;
              } else if (currentSummary && !streamData.content) {
                newContent = currentSummary.content;
              }
              
              // Update metrics
              const metrics = currentSummary?.metrics || {
                startTime: Date.now(),
                firstTokenTime: null,
                totalTime: null,
                tokensPerSecond: null
              };
              
              if (streamData.status === 'streaming' && (!currentSummary || currentSummary.content === '') && streamData.content) {
                metrics.firstTokenTime = Date.now() - metrics.startTime;
              }
              
              // Calculate total time if summary is completing
              if (streamData.status === 'complete' || streamData.status === 'error') {
                metrics.totalTime = Date.now() - metrics.startTime;
              }
              
              // Calculate total time if summary is completing
              if (streamData.status === 'complete' || streamData.status === 'error') {
                metrics.totalTime = Date.now() - metrics.startTime;
              }
              
              queries = {
                ...queries,
                [queryId]: {
                  ...queries[queryId],
                  summary: {
                    id: 'summary',
                    llmName: streamData.llm?.name || currentSummary?.llmName || 'Summary',
                    model: streamData.llm?.model || currentSummary?.model || '',
                    content: newContent,
                    status: (streamData.status || currentSummary?.status || 'waiting') as SummaryStream['status'],
                    error: streamData.error !== undefined ? streamData.error : (currentSummary?.error || null),
                    metrics: streamData.metrics || metrics
                  }
                }
              };
            } else if (streamId) {
              // Update individual LLM stream with $state.raw
              const currentQuery = queries[queryId];
              const updatedStreams = currentQuery.streams.map(s => {
                if (s.id === streamId) {
                  // For streaming content, append instead of replace
                  const newContent = streamData.status === 'streaming' && streamData.content
                    ? s.content + streamData.content
                    : streamData.content || s.content;
                  
                  // Update first token time if this is the first content
                  const metrics = { ...s.metrics };
                  if (streamData.status === 'streaming' && s.content === '' && streamData.content) {
                    metrics.firstTokenTime = Date.now() - s.metrics.startTime;
                  }
                  
                  // Calculate total time if stream is completing
                  if (streamData.status === 'complete' || streamData.status === 'error') {
                    metrics.totalTime = Date.now() - s.metrics.startTime;
                  }
                  
                  // Calculate total time if stream is completing
                  if (streamData.status === 'complete' || streamData.status === 'error') {
                    metrics.totalTime = Date.now() - s.metrics.startTime;
                  }
                  
                  return {
                    ...s,
                    content: newContent,
                    status: (streamData.status || s.status) as Stream['status'],
                    error: streamData.error !== undefined ? streamData.error : s.error,
                    metrics: streamData.metrics || metrics
                  };
                }
                return s;
              });
              
              queries = {
                ...queries,
                [queryId]: {
                  ...currentQuery,
                  streams: updatedStreams
                }
              };
            }
          },
          onError: (error: Error) => {
            console.error('Streaming error:', error);
            // With $state.raw, create a new object
            queries = {
              ...queries,
              [queryId]: {
                ...queries[queryId],
                error: error.message || 'An unexpected error occurred',
                isStreaming: false
              }
            };
          },
          signal: abortController.signal
        });
      } catch (error: any) {
        console.error('Streaming error:', error);
        // With $state.raw, create a new object
        queries = {
          ...queries,
          [queryId]: {
            ...queries[queryId],
            error: error.message || 'Failed to start streaming',
            isStreaming: false
          }
        };
      } finally {
        // Mark streaming as complete with $state.raw
        const currentQuery = queries[queryId];
        if (currentQuery) {
          // Ensure summary is marked as complete if it exists and isn't already in error state
          const updatedSummary = currentQuery.summary && currentQuery.summary.status === 'streaming'
            ? { ...currentQuery.summary, status: 'complete' as const }
            : currentQuery.summary;
          
          queries = {
            ...queries,
            [queryId]: {
              ...currentQuery,
              isStreaming: false,
              summary: updatedSummary
            }
          };
        }
        // Clean up abort controller
        abortControllers.delete(queryId);
      }
    },
    
    // Abort streams for a specific query
    abortQuery(queryId: string): void {
      const controller = abortControllers.get(queryId);
      if (controller) {
        controller.abort();
        abortControllers.delete(queryId);
      }
      
      const queryData = queries[queryId];
      if (queryData) {
        // With $state.raw, create a new object
        queries = {
          ...queries,
          [queryId]: {
            ...queryData,
            isStreaming: false,
            streams: queryData.streams.map(s =>
              s.status === 'streaming'
                ? { ...s, status: 'aborted' as const, error: 'Stream aborted by user' }
                : s
            )
          }
        };
      }
    },
    
    // Start streaming for follow-up query with context
    async startFollowUpStreaming(query: string, config: { llms: LLMConfig[]; summaryLLM: LLMConfig | null }, queryId: string, parentQueryId: string, context: string): Promise<void> {
      // Check connection first
      if (!navigator.onLine) {
        queries = {
          ...queries,
          [queryId]: {
            streams: [],
            summary: null,
            isStreaming: false,
            error: 'No internet connection. Please check your connection and try again.',
            context: context,
            isFollowUp: true
          }
        };
        return;
      }
      
      // Initialize query state with context
      queries = {
        ...queries,
        [queryId]: {
          streams: [],
          summary: null,
          isStreaming: true,
          error: null,
          context: context,
          isFollowUp: true
        }
      };
      
      // Create abort controller for this query
      const abortController = new AbortController();
      abortControllers.set(queryId, abortController);
      
      // Get enabled LLMs
      const enabledLLMs = config.llms.filter(llm => llm.enabled);
      
      if (enabledLLMs.length === 0) {
        queries = {
          ...queries,
          [queryId]: {
            ...queries[queryId],
            isStreaming: false,
            error: 'No LLMs are enabled. Please configure at least one LLM.'
          }
        };
        return;
      }
      
      // Create stream objects for each LLM
      const streamObjects: Stream[] = enabledLLMs.map(llm => ({
        id: llm.id,
        llmId: llm.id,
        llmName: llm.name,
        model: llm.model,
        content: '',
        status: 'waiting',
        error: null,
        metrics: {
          startTime: Date.now(),
          firstTokenTime: null,
          totalTime: null,
          tokensPerSecond: null
        }
      }));
      
      // Update store with initial stream objects
      queries = {
        ...queries,
        [queryId]: {
          ...queries[queryId],
          streams: streamObjects
        }
      };
      
      // Start streaming using the unified endpoint with context
      try {
        await streamMultipleQueries({
          query,
          llms: enabledLLMs,
          summaryLLM: config.summaryLLM,
          context: context,
          isFollowUp: true,
          parentQueryId: parentQueryId,
          onUpdate: (updateData: StreamUpdate) => {
            // Handle updates same as regular streaming
            if (updateData.type === 'global_error') {
              queries = {
                ...queries,
                [queryId]: {
                  ...queries[queryId],
                  isStreaming: false,
                  error: updateData.error || 'An error occurred'
                }
              };
              return;
            }
            
            const { streamId, ...streamData } = updateData;
            
            if (streamId === 'summary') {
              const currentSummary = queries[queryId].summary;
              
              let newContent = streamData.content || '';
              if (currentSummary && streamData.status === 'streaming' && streamData.content) {
                newContent = currentSummary.content + streamData.content;
              } else if (currentSummary && !streamData.content) {
                newContent = currentSummary.content;
              }
              
              const metrics = currentSummary?.metrics || {
                startTime: Date.now(),
                firstTokenTime: null,
                totalTime: null,
                tokensPerSecond: null
              };
              
              if (streamData.status === 'streaming' && (!currentSummary || currentSummary.content === '') && streamData.content) {
                metrics.firstTokenTime = Date.now() - metrics.startTime;
              }
              
              queries = {
                ...queries,
                [queryId]: {
                  ...queries[queryId],
                  summary: {
                    id: 'summary',
                    llmName: streamData.llm?.name || currentSummary?.llmName || 'Summary',
                    model: streamData.llm?.model || currentSummary?.model || '',
                    content: newContent,
                    status: (streamData.status || currentSummary?.status || 'waiting') as SummaryStream['status'],
                    error: streamData.error !== undefined ? streamData.error : (currentSummary?.error || null),
                    metrics: streamData.metrics || metrics
                  }
                }
              };
            } else if (streamId) {
              const currentQuery = queries[queryId];
              const updatedStreams = currentQuery.streams.map(s => {
                if (s.id === streamId) {
                  const newContent = streamData.status === 'streaming' && streamData.content
                    ? s.content + streamData.content
                    : streamData.content || s.content;
                  
                  const metrics = { ...s.metrics };
                  if (streamData.status === 'streaming' && s.content === '' && streamData.content) {
                    metrics.firstTokenTime = Date.now() - s.metrics.startTime;
                  }
                  
                  return {
                    ...s,
                    content: newContent,
                    status: (streamData.status || s.status) as Stream['status'],
                    error: streamData.error !== undefined ? streamData.error : s.error,
                    metrics: streamData.metrics || metrics
                  };
                }
                return s;
              });
              
              queries = {
                ...queries,
                [queryId]: {
                  ...currentQuery,
                  streams: updatedStreams
                }
              };
            }
          },
          onError: (error: Error) => {
            console.error('Follow-up streaming error:', error);
            queries = {
              ...queries,
              [queryId]: {
                ...queries[queryId],
                error: error.message || 'An unexpected error occurred',
                isStreaming: false
              }
            };
          },
          signal: abortController.signal
        });
      } catch (error: any) {
        console.error('Follow-up streaming error:', error);
        queries = {
          ...queries,
          [queryId]: {
            ...queries[queryId],
            error: error.message || 'Failed to start streaming',
            isStreaming: false
          }
        };
      } finally {
        // Mark streaming as complete with $state.raw
        const currentQuery = queries[queryId];
        if (currentQuery) {
          // Ensure summary is marked as complete if it exists and isn't already in error state
          const updatedSummary = currentQuery.summary && currentQuery.summary.status === 'streaming'
            ? { ...currentQuery.summary, status: 'complete' as const }
            : currentQuery.summary;
          
          queries = {
            ...queries,
            [queryId]: {
              ...currentQuery,
              isStreaming: false,
              summary: updatedSummary
            }
          };
        }
        abortControllers.delete(queryId);
      }
    },
    
    // Abort all active streams
    abortAll(): void {
      abortControllers.forEach((controller, queryId) => {
        controller.abort();
      });
      abortControllers.clear();
      
      // With $state.raw, create a new object
      const updatedQueries: Record<string, QueryStreamData> = {};
      Object.entries(queries).forEach(([queryId, queryData]) => {
        updatedQueries[queryId] = {
          ...queryData,
          isStreaming: false,
          streams: queryData.streams.map(s =>
            s.status === 'streaming'
              ? { ...s, status: 'aborted' as const, error: 'Stream aborted by user' }
              : s
          )
        };
      });
      queries = updatedQueries;
    },
    
    // Clear error for a specific query
    clearError(queryId: string): void {
      if (queries[queryId]) {
        // With $state.raw, create a new object
        queries = {
          ...queries,
          [queryId]: {
            ...queries[queryId],
            error: null
          }
        };
      }
    },
    
    // Remove a query from the store
    removeQuery(queryId: string): void {
      // Abort if still streaming
      const controller = abortControllers.get(queryId);
      if (controller) {
        controller.abort();
        abortControllers.delete(queryId);
      }
      
      // With $state.raw, create a new object without the removed query
      const { [queryId]: removed, ...rest } = queries;
      queries = rest;
    },
    
    // Cleanup method to be called when store is destroyed
    destroy(): void {
      if (connectionMonitor) {
        connectionMonitor.destroy();
      }
      // Abort all active streams
      this.abortAll();
    }
  };
}

/**
 * Global stream store instance
 */
export const streamStore = createStreamStore();

/**
 * Check if all streams are complete for a specific query
 */
export function queryComplete(queryId: string): boolean {
  const queryData = streamStore.queries[queryId];
  if (!queryData || queryData.streams.length === 0) return false;
  
  const allStreamsComplete = queryData.streams.every(
    s => s.status === 'complete' || s.status === 'error'
  );
  
  const summaryComplete = !queryData.summary ||
    queryData.summary.status === 'complete' ||
    queryData.summary.status === 'error';
  
  return allStreamsComplete && summaryComplete && !queryData.isStreaming;
}