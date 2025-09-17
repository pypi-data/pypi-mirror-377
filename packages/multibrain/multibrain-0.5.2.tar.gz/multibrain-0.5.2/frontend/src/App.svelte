<!-- Svelte 5 Migration: App.svelte - 2025-09-15 -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import QueryInput from './components/QueryInput.svelte';
  import ResponseContainer from './components/ResponseContainer.svelte';
  import ConfigModal from './components/ConfigModal.svelte';
  import ToastContainer from './components/ToastContainer.svelte';
  import LoadingSpinner from './components/LoadingSpinner.svelte';
  import KeyboardShortcuts from './components/KeyboardShortcuts.svelte';
  import WelcomeGuide from './components/WelcomeGuide.svelte';
  import ErrorBoundary from './components/ErrorBoundary.svelte';
  import DebugPanel from './components/DebugPanel.svelte';
  import { configStore, loadConfig } from './stores/config.svelte';
  import { queryStore } from './stores/queries.svelte';
  import { streamStore } from './stores/streams.svelte';
  import { toastStore } from './stores/toasts.svelte';
  import { debugStore, debugInspect } from './stores/debug.svelte';
  import { createContextLogger } from './lib/errorLogger';

  let showConfig = $state(false);
  let isInitializing = $state(true);
  let queryInputRef = $state<QueryInput>();
  let showWelcome = $state(false);
  let appError = $state<Error | null>(null);
  let queryValue = $state('');
  
  // Create context-aware logger for App component
  const logger = createContextLogger('App');
  
  // Development debugging with debug store
  $effect(() => {
    if (debugStore.enabled) {
      debugInspect(showConfig, 'App.showConfig');
      debugInspect(isInitializing, 'App.isInitializing');
      debugInspect(showWelcome, 'App.showWelcome');
    }
  });

  onMount(async () => {
    try {
      logger.info('Starting initialization', 'init');
      await loadConfig();
      isInitializing = false;
      logger.info('Initialization complete', 'init');
      
      // Check if this is the first visit
      const hasSeenWelcome = localStorage.getItem('multibrain_welcome_seen');
      
      // Show welcome guide for first-time users
      if (!hasSeenWelcome) {
        showWelcome = true;
      } else if (configStore.llms.length === 0) {
        // Show toast for returning users without config
        setTimeout(() => {
          toastStore.info('Welcome back! Click "Configure LLMs" to get started.', 5000);
        }, 500);
      }
    } catch (error) {
      logger.error(error, 'init-failed');
      isInitializing = false;
      toastStore.error('Failed to load configuration');
    }
  });

  function handleQuery(query: string): void {
    try {
      if (!query || !query.trim()) return;

      // Check if any LLMs are configured
      if (configStore.llms.filter(llm => llm.enabled).length === 0) {
        toastStore.warning('Please configure at least one LLM before querying');
        return;
      }

      // Add query to history
      const queryRecord = queryStore.addQuery(query);
      logger.info('Query submitted', 'query', { queryId: queryRecord.id, length: query.length });

      // Start streaming from all configured LLMs with query ID
      streamStore.startStreaming(query, configStore, queryRecord.id);
      toastStore.info('Starting query...');
    } catch (error) {
      logger.error(error, 'query-failed');
      toastStore.error('Failed to process query');
    }
  }

  function handleStreamComplete(detail: { queryId: string }): void {
    const { queryId } = detail;
    toastStore.success(`Query completed successfully!`);
  }
  
  function handleFollowUp(detail: { query: string; parentQueryId: string; summaryContent: string }): void {
    try {
      const { query, parentQueryId, summaryContent } = detail;
      
      if (!query || !query.trim()) return;

      // Check if any LLMs are configured
      if (configStore.llms.filter(llm => llm.enabled).length === 0) {
        toastStore.warning('Please configure at least one LLM before querying');
        return;
      }

      // Add follow-up query to history with parent reference
      const queryRecord = queryStore.addFollowUpQuery(query, parentQueryId, summaryContent);
      logger.info('Follow-up query submitted', 'follow-up', {
        queryId: queryRecord.id,
        parentId: parentQueryId,
        depth: queryRecord.depth
      });

      // Start streaming with context
      streamStore.startFollowUpStreaming(query, configStore, queryRecord.id, parentQueryId, summaryContent);
      toastStore.info('Processing follow-up question...');
    } catch (error) {
      logger.error(error, 'follow-up-failed');
      toastStore.error('Failed to process follow-up question');
    }
  }

  function toggleConfig(): void {
    showConfig = !showConfig;
  }
  
  function handleOpenConfig(): void {
    showConfig = true;
  }
  
  function handleFocusQuery(): void {
    queryInputRef?.focus();
  }
  
  function handleSubmitQuery(): void {
    queryInputRef?.submit();
  }
  
  function handleCloseModal(): void {
    if (showConfig) {
      showConfig = false;
    }
  }
  
  function handleWelcomeComplete(): void {
    showWelcome = false;
    localStorage.setItem('multibrain_welcome_seen', 'true');
    // Open config after welcome
    setTimeout(() => {
      showConfig = true;
    }, 300);
  }

  // Handle streaming errors
  $effect(() => {
    // Check for errors in any active queries
    Object.entries(streamStore.queries).forEach(([queryId, queryData]) => {
      if (queryData.error) {
        logger.error(new Error(queryData.error), 'stream-error', { queryId });
        toastStore.error(queryData.error);
        streamStore.clearError(queryId);
      }
    });
  });
  
  /**
   * Handle global app errors
   */
  function handleAppError(error: Error, info: any): void {
    logger.error(error, 'app-error', info);
    // Could implement additional error handling here
  }
  
  /**
   * Reset app after error
   */
  function resetApp(): void {
    appError = null;
    // Could implement additional reset logic here
  }
</script>

<ErrorBoundary error={appError} reset={resetApp} onError={handleAppError}>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <!-- Header -->
    <header class="bg-gray-800 border-b border-gray-700 sticky top-0 z-30 backdrop-blur-sm bg-gray-800/95">
    <div class="container mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <h1 class="text-2xl font-bold text-blue-400">MultiBrain</h1>
          <span class="text-sm text-gray-500">Query multiple AI models simultaneously</span>
        </div>
        <div class="flex items-center gap-3">
          {#if configStore.llms.length > 0}
            <span class="text-sm text-gray-400">
              {configStore.llms.filter(llm => llm.enabled).length} of {configStore.llms.length} LLMs active
            </span>
          {/if}
          <button
            onclick={toggleConfig}
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-all duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            Configure LLMs
          </button>
        </div>
      </div>
    </div>
  </header>

  <!-- Main Content -->
  <main class="container mx-auto px-4 py-6">
    {#if isInitializing}
      <div class="flex items-center justify-center py-20">
        <div class="text-center">
          <LoadingSpinner size="large" />
          <p class="mt-4 text-gray-400">Initializing MultiBrain...</p>
        </div>
      </div>
    {:else}
      <div in:fade={{ duration: 300 }}>
        <!-- Query Input -->
        <div class="mb-6">
          <QueryInput
            bind:this={queryInputRef}
            bind:value={queryValue}
            onsubmit={handleQuery}
          />
        </div>

        <!-- Response Container -->
        <ResponseContainer
          oncomplete={handleStreamComplete}
          onFollowUp={handleFollowUp}
        />
      </div>
    {/if}
  </main>

  <!-- Configuration Modal -->
  {#if showConfig}
    <ConfigModal onclose={() => showConfig = false} />
  {/if}

  <!-- Toast Container -->
  <ToastContainer />
  
  <!-- Keyboard Shortcuts -->
  <KeyboardShortcuts
    onopenConfig={handleOpenConfig}
    onfocusQuery={handleFocusQuery}
    onsubmitQuery={handleSubmitQuery}
    oncloseModal={handleCloseModal}
  />
  
    <!-- Welcome Guide -->
    {#if showWelcome}
      <WelcomeGuide oncomplete={handleWelcomeComplete} />
    {/if}
    
    <!-- Debug Panel -->
    <DebugPanel />
  </div>
</ErrorBoundary>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  :global(*) {
    box-sizing: border-box;
  }

  :global(::selection) {
    background-color: #3b82f6;
    color: white;
  }
</style>