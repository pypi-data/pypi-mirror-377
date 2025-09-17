<!-- Svelte 5 Migration: ConfigModal.svelte - 2025-09-15 -->
<script lang="ts">
  import LLMConfigForm from './LLMConfigForm.svelte';
  import { configStore } from '../stores/config.svelte';
  import type { LLMConfig } from '../types';
  import type { Snippet } from 'svelte';
  
  interface ConfigModalProps {
    onclose?: () => void;
    headerSnippet?: Snippet;
    llmItemSnippet?: Snippet<[LLMConfig, (id: string) => void, (llm: LLMConfig) => void, (id: string) => void]>;
    emptyStateSnippet?: Snippet;
  }
  
  let {
    onclose,
    headerSnippet,
    llmItemSnippet,
    emptyStateSnippet
  }: ConfigModalProps = $props();
  
  let showAddForm = $state(false);
  let editingLLM = $state<LLMConfig | null>(null);
  
  // Add performance monitoring in development
  if (import.meta.env.DEV) {
    $inspect(configStore.llms).with((type, value) => {
      console.log('[ConfigModal] LLMs updated:', {
        type,
        count: value.length,
        enabledCount: value.filter(llm => llm.enabled).length,
        timestamp: new Date().toISOString()
      });
    });
  }
  
  /**
   * Close the modal
   */
  function handleClose(): void {
    onclose?.();
  }
  
  /**
   * Show the add LLM form
   */
  function handleAddLLM(): void {
    showAddForm = true;
    editingLLM = null;
  }
  
  /**
   * Edit an existing LLM
   */
  function handleEditLLM(llm: LLMConfig): void {
    editingLLM = llm;
    showAddForm = true;
  }
  
  /**
   * Delete an LLM configuration
   */
  async function handleDeleteLLM(id: string): Promise<void> {
    if (confirm('Are you sure you want to delete this LLM configuration?')) {
      await configStore.removeLLM(id);
    }
  }
  
  /**
   * Save LLM configuration (add or update)
   */
  async function handleSaveLLM(llmConfig: Omit<LLMConfig, 'id' | 'order'>): Promise<void> {
    console.log('[ConfigModal] Received LLM config to save:', llmConfig);
    
    if (editingLLM) {
      console.log('[ConfigModal] Updating existing LLM:', editingLLM.id);
      await configStore.updateLLM(editingLLM.id, llmConfig);
    } else {
      console.log('[ConfigModal] Adding new LLM');
      await configStore.addLLM(llmConfig);
    }
    
    console.log('[ConfigModal] After save, LLMs in store:', configStore.llms);
    
    showAddForm = false;
    editingLLM = null;
  }
  
  /**
   * Cancel the form and hide it
   */
  function handleCancelForm(): void {
    showAddForm = false;
    editingLLM = null;
  }
  
  /**
   * Toggle LLM enabled state
   */
  async function handleToggleLLM(id: string): Promise<void> {
    const llm = configStore.llms.find(l => l.id === id);
    if (llm) {
      await configStore.updateLLM(id, { ...llm, enabled: !llm.enabled });
    }
  }
  
  /**
   * Set the summary LLM
   */
  async function handleSetSummaryLLM(llm: LLMConfig): Promise<void> {
    await configStore.setSummaryLLM(llm);
  }
</script>

<!-- Default snippets for customizable rendering -->
{#snippet defaultHeader()}
  <h2 class="text-xl font-semibold">LLM Configuration</h2>
{/snippet}

{#snippet defaultLLMItem(llm)}
  <div class="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between">
    <div class="flex items-center gap-4">
      <input
        type="checkbox"
        checked={llm.enabled}
        onchange={() => handleToggleLLM(llm.id)}
        class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
      />
      <div>
        <h4 class="font-medium">{llm.name}</h4>
        <p class="text-sm text-gray-400">{llm.model} • {llm.url}</p>
      </div>
    </div>
    <div class="flex items-center gap-2">
      <button
        onclick={() => handleEditLLM(llm)}
        class="p-2 hover:bg-gray-600 rounded-lg transition-colors"
        title="Edit"
        aria-label="Edit LLM configuration"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
      </button>
      <button
        onclick={() => handleDeleteLLM(llm.id)}
        class="p-2 hover:bg-red-600/20 rounded-lg transition-colors text-red-400"
        title="Delete"
        aria-label="Delete LLM configuration"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
        </svg>
      </button>
    </div>
  </div>
{/snippet}

{#snippet defaultEmptyState()}
  <div class="text-center py-8 bg-gray-700/50 rounded-lg">
    <p class="text-gray-400">No LLMs configured yet</p>
    <p class="text-sm text-gray-500 mt-2">Add your first LLM to start querying</p>
  </div>
{/snippet}

<!-- Modal Backdrop -->
<div
  class="fixed inset-0 bg-black/50 z-40"
  onclick={handleClose}
  onkeydown={(e) => e.key === 'Escape' && handleClose()}
  role="button"
  tabindex="-1"
  aria-label="Close modal"
></div>

<!-- Modal Content -->
<div class="fixed inset-0 z-50 overflow-y-auto">
  <div class="flex min-h-full items-center justify-center p-4">
    <div
      class="bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      tabindex="-1"
    >
      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
        {#if headerSnippet}
          {@render headerSnippet()}
        {:else}
          {@render defaultHeader()}
        {/if}
        <button
          onclick={handleClose}
          class="p-2 hover:bg-gray-700 rounded-lg transition-colors"
          aria-label="Close modal"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      
      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-[calc(90vh-8rem)]">
        {#if showAddForm}
          <!-- Add/Edit Form -->
          <div class="mb-6">
            <h3 class="text-lg font-semibold mb-4">
              {editingLLM ? 'Edit LLM' : 'Add New LLM'}
            </h3>
            <LLMConfigForm
              llm={editingLLM}
              onsave={handleSaveLLM}
              oncancel={handleCancelForm}
            />
          </div>
        {:else}
          <!-- LLM List -->
          <div class="space-y-6">
            <!-- Response LLMs -->
            <div>
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-lg font-semibold">Response LLMs</h3>
                <button
                  onclick={handleAddLLM}
                  class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-2"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Add LLM
                </button>
              </div>
              
              {#if configStore.llms.length === 0}
                {#if emptyStateSnippet}
                  {@render emptyStateSnippet()}
                {:else}
                  {@render defaultEmptyState()}
                {/if}
              {:else}
                <div class="space-y-3">
                  {#each configStore.llms as llm (llm.id)}
                    {#if llmItemSnippet}
                      {@render llmItemSnippet(llm, handleToggleLLM, handleEditLLM, handleDeleteLLM)}
                    {:else}
                      {@render defaultLLMItem(llm)}
                    {/if}
                  {/each}
                </div>
              {/if}
            </div>
            
            <!-- Summary LLM -->
            <div>
              <h3 class="text-lg font-semibold mb-4">Summary LLM</h3>
              {#if configStore.summaryLLM}
                <div class="bg-blue-900/20 border border-blue-700/50 rounded-lg p-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <h4 class="font-medium text-blue-300">{configStore.summaryLLM.name}</h4>
                      <p class="text-sm text-gray-400">{configStore.summaryLLM.model} • {configStore.summaryLLM.url}</p>
                    </div>
                    <button
                      onclick={() => handleEditLLM(configStore.summaryLLM)}
                      class="p-2 hover:bg-gray-600 rounded-lg transition-colors"
                      title="Edit"
                      aria-label="Edit summary LLM configuration"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                  </div>
                </div>
              {:else}
                <div class="text-center py-8 bg-gray-700/50 rounded-lg">
                  <p class="text-gray-400">No summary LLM configured</p>
                  <p class="text-sm text-gray-500 mt-2">Select from your configured LLMs</p>
                </div>
              {/if}
              
              {#if configStore.llms.length > 0}
                <div class="mt-4">
                  <label for="summary-llm-select" class="block text-sm font-medium mb-2">Select Summary LLM:</label>
                  <select
                    id="summary-llm-select"
                    value={configStore.summaryLLM?.id || ''}
                    onchange={async (e) => {
                      const llm = configStore.llms.find(l => l.id === (e.target as HTMLSelectElement).value);
                      if (llm) await handleSetSummaryLLM(llm);
                    }}
                    class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500"
                  >
                    <option value="">None</option>
                    {#each configStore.llms as llm}
                      <option value={llm.id}>{llm.name} ({llm.model})</option>
                    {/each}
                  </select>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>