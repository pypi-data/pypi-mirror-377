import { createQueryStateMachine } from '../lib/stateMachine';
import { queryStore } from './queries.svelte';
import { streamStore } from './streams.svelte';
import { configStore } from './config.svelte';
import { toastStore } from './toasts.svelte';
import { debugStore } from './debug.svelte';
import type { QueryStateMachine, QueryState, QueryContext } from '../types';

interface QueryStateMachineStore {
  state: QueryState;
  context: QueryContext;
  canSubmit: boolean;
  isStreaming: boolean;
  hasError: boolean;
  submitQuery(query: string): Promise<void>;
  abortQuery(): Promise<void>;
  retryQuery(): Promise<void>;
  reset(): void;
  machine: QueryStateMachine;
}

/**
 * Create a reactive store wrapper around the query state machine
 */
function createQueryStateMachineStore(): QueryStateMachineStore {
  const machine = createQueryStateMachine();
  
  // Reactive state
  let state = $state<QueryState>(machine.current as QueryState);
  let context = $state<QueryContext>(machine.getContext());
  
  // Subscribe to state machine changes
  machine.subscribe((newState: string) => {
    state = newState as QueryState;
    context = machine.getContext();
    
    // Log state transitions in debug mode
    if (debugStore.enabled) {
      debugStore.logStateChange({
        type: 'query-state',
        from: state,
        to: newState,
        context: machine.getContext()
      });
    }
  });
  
  // Derived states
  let canSubmit = $derived(
    state === 'idle' || 
    state === 'complete' || 
    state === 'aborted' || 
    state === 'viewing'
  );
  
  let isStreaming = $derived(state === 'streaming');
  let hasError = $derived(state === 'error');
  
  return {
    // Getters
    get state(): QueryState { return state; },
    get context(): QueryContext { return context; },
    get canSubmit(): boolean { return canSubmit; },
    get isStreaming(): boolean { return isStreaming; },
    get hasError(): boolean { return hasError; },
    
    // Methods
    async submitQuery(query: string): Promise<void> {
      if (!canSubmit) {
        toastStore.warning('Please wait for the current query to complete');
        return;
      }
      
      // Validate query
      await machine.send('SUBMIT', { query, queryId: crypto.randomUUID() });
      
      // Check if we have enabled LLMs
      const enabledLLMs = configStore.llms.filter(llm => llm.enabled);
      if (enabledLLMs.length === 0) {
        await machine.send('INVALID', { reason: 'No LLMs configured' });
        toastStore.warning('Please configure at least one LLM before querying');
        return;
      }
      
      if (!query.trim()) {
        await machine.send('INVALID', { reason: 'Empty query' });
        toastStore.warning('Please enter a query');
        return;
      }
      
      // Query is valid, proceed to streaming
      await machine.send('VALID');
      
      try {
        // Add to query history
        const queryRecord = queryStore.addQuery(query);
        machine.updateContext({ queryId: queryRecord.id });
        
        // Start streaming
        await streamStore.startStreaming(query, configStore, queryRecord.id);
        
        // Monitor streaming progress
        const checkInterval = setInterval(() => {
          const queryData = streamStore.queries[queryRecord.id];
          
          if (!queryData) {
            clearInterval(checkInterval);
            return;
          }
          
          // Check for errors
          if (queryData.error) {
            clearInterval(checkInterval);
            machine.send('ERROR', { error: queryData.error });
            return;
          }
          
          // Check if complete
          if (!queryData.isStreaming) {
            const allComplete = queryData.streams.every(
              s => s.status === 'complete' || s.status === 'error'
            );
            
            if (allComplete) {
              clearInterval(checkInterval);
              machine.send('COMPLETE');
              toastStore.success('Query completed successfully!');
            }
          }
          
          // Send update event
          machine.send('UPDATE', { 
            streams: queryData.streams,
            summary: queryData.summary 
          });
        }, 100);
        
      } catch (error: any) {
        await machine.send('ERROR', { error: error.message });
        toastStore.error('Failed to process query');
      }
    },
    
    async abortQuery(): Promise<void> {
      if (!isStreaming) return;
      
      const queryId = context.queryId;
      if (queryId) {
        streamStore.abortQuery(queryId);
      }
      
      await machine.send('ABORT');
      toastStore.info('Query aborted');
    },
    
    async retryQuery(): Promise<void> {
      if (!hasError || !context.query) return;
      
      await machine.send('RETRY');
      await this.submitQuery(context.query);
    },
    
    reset(): void {
      machine.reset();
    },
    
    // Expose machine for advanced usage
    get machine(): QueryStateMachine { return machine as QueryStateMachine; }
  };
}

// Create singleton instance
export const queryStateMachine = createQueryStateMachineStore();

/**
 * Hook to use query state machine in components
 */
export function useQueryStateMachine() {
  return {
    state: queryStateMachine.state,
    context: queryStateMachine.context,
    canSubmit: queryStateMachine.canSubmit,
    isStreaming: queryStateMachine.isStreaming,
    hasError: queryStateMachine.hasError,
    submitQuery: queryStateMachine.submitQuery.bind(queryStateMachine),
    abortQuery: queryStateMachine.abortQuery.bind(queryStateMachine),
    retryQuery: queryStateMachine.retryQuery.bind(queryStateMachine),
    reset: queryStateMachine.reset.bind(queryStateMachine)
  };
}