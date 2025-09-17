<!-- Debug Panel Component for Development -->
<script>
  import { fade, slide } from 'svelte/transition';
  import { debugStore } from '../stores/debug.svelte';
  import { configStore } from '../stores/config.svelte';
  import { queryStore } from '../stores/queries.svelte';
  import { streamStore } from '../stores/streams.svelte';
  
  let activeTab = $state('metrics');
  let errorHistory = $state([]);
  let showRawState = $state(false);
  
  // Calculate derived metrics
  let activeStreams = $derived(
    Object.values(streamStore.queries).filter(q => q.isStreaming).length
  );
  
  let totalQueries = $derived(queryStore.queries.length);
  let enabledLLMs = $derived(configStore.llms.filter(llm => llm.enabled).length);
  
  function formatBytes(bytes) {
    if (!bytes) return '0 MB';
    return `${(bytes / 1048576).toFixed(1)} MB`;
  }
  
  function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
  }
  
  function clearErrors() {
    errorHistory = [];
  }
</script>

{#if debugStore.enabled && debugStore.showPanel}
  <div 
    class="fixed bottom-0 right-0 w-96 max-h-[60vh] bg-gray-900 border border-gray-700 rounded-tl-lg shadow-2xl z-50 flex flex-col"
    transition:slide={{ duration: 300 }}
  >
    <!-- Header -->
    <div class="bg-gray-800 px-4 py-2 flex items-center justify-between border-b border-gray-700">
      <h3 class="font-semibold text-sm flex items-center gap-2">
        <span class="text-green-400">●</span>
        Debug Panel
      </h3>
      <div class="flex items-center gap-2">
        <button
          onclick={() => debugStore.exportDebugData()}
          class="p-1 hover:bg-gray-700 rounded transition-colors"
          title="Export debug data"
          aria-label="Export debug data"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
        </button>
        <button
          onclick={() => debugStore.togglePanel()}
          class="p-1 hover:bg-gray-700 rounded transition-colors"
          aria-label="Close debug panel"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- Tabs -->
    <div class="flex border-b border-gray-700">
      <button
        onclick={() => activeTab = 'metrics'}
        class="px-4 py-2 text-sm font-medium transition-colors {activeTab === 'metrics' ? 'bg-gray-800 text-blue-400 border-b-2 border-blue-400' : 'hover:bg-gray-800'}"
      >
        Metrics
      </button>
      <button
        onclick={() => activeTab = 'state'}
        class="px-4 py-2 text-sm font-medium transition-colors {activeTab === 'state' ? 'bg-gray-800 text-blue-400 border-b-2 border-blue-400' : 'hover:bg-gray-800'}"
      >
        State
      </button>
      <button
        onclick={() => activeTab = 'errors'}
        class="px-4 py-2 text-sm font-medium transition-colors relative {activeTab === 'errors' ? 'bg-gray-800 text-blue-400 border-b-2 border-blue-400' : 'hover:bg-gray-800'}"
      >
        Errors
        {#if errorHistory.length > 0}
          <span class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center">
            {errorHistory.length}
          </span>
        {/if}
      </button>
      <button
        onclick={() => activeTab = 'settings'}
        class="px-4 py-2 text-sm font-medium transition-colors {activeTab === 'settings' ? 'bg-gray-800 text-blue-400 border-b-2 border-blue-400' : 'hover:bg-gray-800'}"
      >
        Settings
      </button>
    </div>
    
    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-4">
      {#if activeTab === 'metrics'}
        <div class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <div class="bg-gray-800 rounded p-3">
              <div class="text-xs text-gray-400">Memory Usage</div>
              <div class="text-lg font-semibold">{formatBytes(debugStore.metrics.memoryUsage * 1048576)}</div>
            </div>
            <div class="bg-gray-800 rounded p-3">
              <div class="text-xs text-gray-400">Store Updates</div>
              <div class="text-lg font-semibold">{debugStore.metrics.storeUpdates}</div>
            </div>
            <div class="bg-gray-800 rounded p-3">
              <div class="text-xs text-gray-400">API Calls</div>
              <div class="text-lg font-semibold">{debugStore.metrics.apiCalls}</div>
            </div>
            <div class="bg-gray-800 rounded p-3">
              <div class="text-xs text-gray-400">Render Count</div>
              <div class="text-lg font-semibold">{debugStore.metrics.renderCount}</div>
            </div>
          </div>
          
          <div class="border-t border-gray-700 pt-3">
            <h4 class="text-sm font-medium mb-2">Application State</h4>
            <div class="space-y-1 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-400">Active Streams:</span>
                <span>{activeStreams}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Total Queries:</span>
                <span>{totalQueries}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Enabled LLMs:</span>
                <span>{enabledLLMs} / {configStore.llms.length}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-400">Connection:</span>
                <span class="{streamStore.isOnline ? 'text-green-400' : 'text-red-400'}">
                  {streamStore.isOnline ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </div>
          
          <button
            onclick={() => debugStore.reset()}
            class="w-full px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded text-sm transition-colors"
          >
            Reset Metrics
          </button>
        </div>
      {:else if activeTab === 'state'}
        <div class="space-y-3">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-medium">State Inspector</h4>
            <button
              onclick={() => showRawState = !showRawState}
              class="text-xs text-blue-400 hover:text-blue-300"
            >
              {showRawState ? 'Hide' : 'Show'} Raw
            </button>
          </div>
          
          {#if showRawState}
            <div class="bg-gray-800 rounded p-3 overflow-x-auto">
              <pre class="text-xs">{JSON.stringify({
                config: {
                  llms: configStore.llms.length,
                  summaryLLM: configStore.summaryLLM?.name || 'none'
                },
                queries: {
                  total: queryStore.queries.length,
                  current: queryStore.currentQuery?.id
                },
                streams: {
                  active: Object.keys(streamStore.queries).length,
                  isOnline: streamStore.isOnline
                }
              }, null, 2)}</pre>
            </div>
          {:else}
            <div class="space-y-2">
              {#each debugStore.stateHistory.slice(0, 10) as entry}
                <div class="bg-gray-800 rounded p-2 text-xs">
                  <div class="flex justify-between text-gray-400 mb-1">
                    <span>{formatTime(entry.timestamp)}</span>
                    <span class="font-mono">{entry.id.slice(0, 8)}</span>
                  </div>
                  <pre class="text-gray-300 overflow-x-auto">{JSON.stringify(entry.state, null, 2)}</pre>
                </div>
              {/each}
              
              {#if debugStore.stateHistory.length === 0}
                <p class="text-sm text-gray-500 text-center py-4">No state changes recorded</p>
              {/if}
            </div>
          {/if}
        </div>
      {:else if activeTab === 'errors'}
        <div class="space-y-3">
          <div class="flex items-center justify-between mb-2">
            <h4 class="text-sm font-medium">Error Log</h4>
            {#if errorHistory.length > 0}
              <button
                onclick={clearErrors}
                class="text-xs text-red-400 hover:text-red-300"
              >
                Clear All
              </button>
            {/if}
          </div>
          
          {#if errorHistory.length > 0}
            <div class="space-y-2">
              {#each errorHistory as error}
                <div class="bg-gray-800 rounded p-3 text-xs border-l-4 {error.level === 'error' ? 'border-red-500' : error.level === 'warning' ? 'border-yellow-500' : 'border-blue-500'}">
                  <div class="flex items-start justify-between mb-1">
                    <span class="font-medium {error.level === 'error' ? 'text-red-400' : error.level === 'warning' ? 'text-yellow-400' : 'text-blue-400'}">
                      {error.level.toUpperCase()}
                    </span>
                    <span class="text-gray-500">{formatTime(error.timestamp)}</span>
                  </div>
                  <p class="text-gray-300 mb-1">{error.message}</p>
                  {#if error.context}
                    <div class="text-gray-500">
                      <span>{error.context.component}</span>
                      {#if error.context.action}
                        <span> • {error.context.action}</span>
                      {/if}
                    </div>
                  {/if}
                  {#if error.stack}
                    <details class="mt-2">
                      <summary class="cursor-pointer text-gray-400 hover:text-gray-300">Stack trace</summary>
                      <pre class="mt-1 text-gray-500 overflow-x-auto">{error.stack}</pre>
                    </details>
                  {/if}
                </div>
              {/each}
            </div>
          {:else}
            <p class="text-sm text-gray-500 text-center py-8">No errors logged</p>
          {/if}
        </div>
      {:else if activeTab === 'settings'}
        <div class="space-y-3">
          <h4 class="text-sm font-medium mb-3">Debug Settings</h4>
          
          <label class="flex items-center justify-between p-2 hover:bg-gray-800 rounded cursor-pointer">
            <span class="text-sm">Show State Inspector</span>
            <input
              type="checkbox"
              checked={debugStore.showInspector}
              onchange={() => debugStore.toggleInspector()}
              class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
            />
          </label>
          
          <label class="flex items-center justify-between p-2 hover:bg-gray-800 rounded cursor-pointer">
            <span class="text-sm">Log Store Updates</span>
            <input
              type="checkbox"
              checked={debugStore.logStoreUpdates}
              onchange={() => debugStore.toggleStoreLogging()}
              class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
            />
          </label>
          
          <label class="flex items-center justify-between p-2 hover:bg-gray-800 rounded cursor-pointer">
            <span class="text-sm">Log API Calls</span>
            <input
              type="checkbox"
              checked={debugStore.logApiCalls}
              onchange={() => debugStore.toggleApiLogging()}
              class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
            />
          </label>
          
          <div class="border-t border-gray-700 pt-3">
            <p class="text-xs text-gray-500 mb-2">
              Press <kbd class="px-1 py-0.5 bg-gray-800 rounded text-xs">Ctrl+Shift+D</kbd> to toggle this panel
            </p>
            
            <button
              onclick={() => debugStore.toggle()}
              class="w-full px-3 py-2 bg-red-600 hover:bg-red-700 rounded text-sm transition-colors"
            >
              Disable Debug Mode
            </button>
          </div>
        </div>
      {/if}
    </div>
  </div>
{/if}

<!-- Debug mode indicator -->
{#if debugStore.enabled && !debugStore.showPanel}
  <button
    onclick={() => debugStore.togglePanel()}
    class="fixed bottom-4 right-4 w-12 h-12 bg-gray-800 hover:bg-gray-700 rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-110 z-40"
    title="Open debug panel (Ctrl+Shift+D)"
    aria-label="Open debug panel"
    transition:fade={{ duration: 200 }}
  >
    <svg class="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path>
    </svg>
  </button>
{/if}

<style>
  kbd {
    font-family: monospace;
  }
  
  details summary::-webkit-details-marker {
    display: none;
  }
  
  details summary::before {
    content: '▶';
    display: inline-block;
    margin-right: 0.25rem;
    transition: transform 0.2s;
  }
  
  details[open] summary::before {
    transform: rotate(90deg);
  }
</style>