<!-- Svelte 5 Migration: LLMConfigForm.svelte - 2025-09-15 -->
<script lang="ts">
  import { validateLLMConfig } from '../lib/api';
  import { toastStore } from '../stores/toasts.svelte';
  import LoadingSpinner from './LoadingSpinner.svelte';
  import type { LLMConfig } from '../types';
  
  interface LLMFormData extends Omit<LLMConfig, 'id' | 'order'> {
    name: string;
    url: string;
    model: string;
    apiKey: string;
    enabled: boolean;
  }
  
  interface LLMPreset {
    name: string;
    url: string;
    models: string[];
    placeholder: string;
  }
  
  interface TestResult {
    success: boolean;
    message: string;
  }
  
  interface LLMConfigFormProps {
    llm?: LLMConfig | null;
    onsave?: (data: LLMFormData) => void;
    oncancel?: () => void;
  }
  
  let { llm = null, onsave, oncancel }: LLMConfigFormProps = $props();
  let name = $state(llm?.name || '');
  let url = $state(llm?.url || '');
  let model = $state(llm?.model || '');
  let apiKey = $state(llm?.apiKey || '');
  let testing = $state(false);
  let testResult = $state<TestResult | null>(null);
  
  /**
   * Common LLM presets with more options
   */
  const presets: LLMPreset[] = [
    {
      name: 'OpenAI',
      url: 'https://api.openai.com/v1',
      models: ['gpt-4-turbo-preview', 'gpt-4', 'gpt-3.5-turbo'],
      placeholder: 'sk-...'
    },
    {
      name: 'Anthropic',
      url: 'https://api.anthropic.com/v1',
      models: ['claude-3-opus-20240229', 'claude-3-sonnet-20240229', 'claude-3-haiku-20240307'],
      placeholder: 'sk-ant-...'
    },
    {
      name: 'Local Ollama',
      url: 'http://localhost:11434/v1',
      models: ['llama2', 'mistral', 'codellama', 'mixtral'],
      placeholder: 'not-required'
    },
    {
      name: 'Groq',
      url: 'https://api.groq.com/openai/v1',
      models: ['mixtral-8x7b-32768', 'llama2-70b-4096'],
      placeholder: 'gsk_...'
    },
    {
      name: 'Custom',
      url: '',
      models: [],
      placeholder: 'Enter API key'
    }
  ];
  
  // Determine initial preset based on URL if editing
  let selectedPreset = $state(() => {
    if (llm) {
      const matchingPreset = presets.find(p => p.url === llm.url);
      return matchingPreset ? matchingPreset.name : 'Custom';
    }
    return 'OpenAI';
  });
  
  // Initialize with preset if new LLM
  $effect(() => {
    if (!llm && selectedPreset !== 'Custom') {
      const preset = presets.find(p => p.name === selectedPreset);
      if (preset) {
        url = preset.url;
        if (preset.models.length > 0) {
          model = preset.models[0];
        }
      }
    }
  });
  
  /**
   * Handle preset selection change
   */
  function handlePresetChange(event: Event): void {
    selectedPreset = (event.target as HTMLSelectElement).value;
    const preset = presets.find(p => p.name === selectedPreset);
    if (preset && preset.name !== 'Custom') {
      name = preset.name;
      url = preset.url;
      if (preset.models.length > 0) {
        model = preset.models[0];
      }
      testResult = null;
    }
  }
  
  /**
   * Test the LLM connection with current configuration
   */
  async function handleTest(): Promise<void> {
    if (!url || !model || !apiKey) {
      testResult = { success: false, message: 'Please fill in all fields' };
      toastStore.warning('Please fill in all required fields');
      return;
    }
    
    testing = true;
    testResult = null;
    
    try {
      const result = await validateLLMConfig({ url, model, apiKey });
      testResult = result;
      if (result.success) {
        toastStore.success('Connection successful!');
      } else {
        toastStore.error(result.message);
      }
    } catch (error) {
      testResult = { success: false, message: (error as Error).message };
      toastStore.error('Connection test failed: ' + (error as Error).message);
    } finally {
      testing = false;
    }
  }
  
  /**
   * Save the LLM configuration
   */
  function handleSave(): void {
    if (!name || !url || !model || !apiKey) {
      toastStore.warning('Please fill in all required fields');
      return;
    }
    
    const formData = {
      name,
      url,
      model,
      apiKey,
      enabled: true
    };
    
    console.log('[LLMConfigForm] Saving LLM with data:', formData);
    onsave?.(formData);
    
    toastStore.success(`LLM "${name}" ${llm ? 'updated' : 'added'} successfully`);
  }
  
  /**
   * Cancel the form and close
   */
  function handleCancel(): void {
    oncancel?.();
  }
  
  let currentPreset = $derived(presets.find(p => p.url === url));
  let availableModels = $derived(currentPreset?.models || []);
  let apiKeyPlaceholder = $derived(currentPreset?.placeholder || presets.find(p => p.name === selectedPreset)?.placeholder || 'Enter API key');
</script>

<form onsubmit={(e) => { e.preventDefault(); handleSave(); }} class="space-y-4">
  <!-- Preset Selection -->
  <div>
    <label for="llm-provider" class="block text-sm font-medium mb-2">LLM Provider</label>
    <select
      id="llm-provider"
      value={selectedPreset}
      onchange={handlePresetChange}
      class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
    >
      {#each presets as preset}
        <option value={preset.name}>{preset.name}</option>
      {/each}
    </select>
  </div>
  
  <!-- Name -->
  <div>
    <label for="display-name" class="block text-sm font-medium mb-2">
      Display Name <span class="text-red-400">*</span>
    </label>
    <input
      id="display-name"
      type="text"
      bind:value={name}
      placeholder="e.g., GPT-4 Production"
      class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
      required
    />
  </div>
  
  <!-- URL -->
  <div>
    <label for="api-url" class="block text-sm font-medium mb-2">
      API URL <span class="text-red-400">*</span>
    </label>
    <input
      id="api-url"
      type="url"
      bind:value={url}
      placeholder="https://api.openai.com/v1"
      class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
      required
    />
    <p class="text-xs text-gray-400 mt-1">OpenAI-compatible endpoint URL</p>
  </div>
  
  <!-- Model -->
  <div>
    <label for="model-select" class="block text-sm font-medium mb-2">
      Model <span class="text-red-400">*</span>
    </label>
    {#if availableModels.length > 0}
      <select
        id="model-select"
        bind:value={model}
        class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
        required
      >
        <option value="">Select a model</option>
        {#each availableModels as m}
          <option value={m}>{m}</option>
        {/each}
      </select>
    {:else}
      <input
        id="model-select"
        type="text"
        bind:value={model}
        placeholder="e.g., gpt-4"
        class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
        required
      />
    {/if}
  </div>
  
  <!-- API Key -->
  <div>
    <label for="api-key" class="block text-sm font-medium mb-2">
      API Key <span class="text-red-400">*</span>
    </label>
    <div class="relative">
      <input
        id="api-key"
        type="password"
        bind:value={apiKey}
        placeholder={apiKeyPlaceholder}
        class="w-full px-3 py-2 pr-10 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:border-blue-500 transition-colors"
        required
      />
      {#if testResult?.success}
        <div class="absolute right-2 top-1/2 transform -translate-y-1/2">
          <svg class="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
      {/if}
    </div>
    <p class="text-xs text-gray-400 mt-1">Your API key is encrypted and stored locally</p>
  </div>
  
  <!-- Test Connection -->
  <div>
    <button
      type="button"
      onclick={handleTest}
      disabled={testing || !url || !model || !apiKey}
      class="px-4 py-2 bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-all duration-200 flex items-center gap-2"
    >
      {#if testing}
        <LoadingSpinner size="small" color="white" />
        <span>Testing...</span>
      {:else}
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>Test Connection</span>
      {/if}
    </button>
    
    {#if testResult}
      <div class="mt-2 p-3 rounded-lg flex items-start gap-2 {testResult.success ? 'bg-green-900/20 border border-green-700/50' : 'bg-red-900/20 border border-red-700/50'}">
        <svg class="w-5 h-5 flex-shrink-0 mt-0.5 {testResult.success ? 'text-green-400' : 'text-red-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {#if testResult.success}
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          {:else}
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          {/if}
        </svg>
        <p class="text-sm {testResult.success ? 'text-green-400' : 'text-red-400'}">
          {testResult.message}
        </p>
      </div>
    {/if}
  </div>
  
  <!-- Actions -->
  <div class="flex gap-3 pt-4 border-t border-gray-700">
    <button
      type="submit"
      disabled={!name || !url || !model || !apiKey}
      class="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
      </svg>
      <span>{llm ? 'Update' : 'Add'} LLM</span>
    </button>
    <button
      type="button"
      onclick={handleCancel}
      class="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-500 rounded-lg transition-all duration-200"
    >
      Cancel
    </button>
  </div>
</form>