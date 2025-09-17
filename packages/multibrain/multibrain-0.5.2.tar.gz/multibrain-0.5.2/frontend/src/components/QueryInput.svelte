<!-- Svelte 5 Migration: QueryInput.svelte - 2025-09-15 -->
<script lang="ts">
  import { onMount } from 'svelte';
  
  interface QueryInputProps {
    disabled?: boolean;
    value?: string;
    placeholder?: string;
    onsubmit?: (query: string) => void;
  }
  
  let {
    disabled = false,
    value = $bindable(''),
    placeholder = 'Ask a question to multiple LLMs...',
    onsubmit
  }: QueryInputProps = $props();
  
  let textarea = $state<HTMLTextAreaElement>();
  let showUndoRedoHint = $state(false);

  /**
   * Handle form submission
   */
  function handleSubmit(event: Event): void {
    event.preventDefault();
    if (value && value.trim() && !disabled) {
      onsubmit?.(value);
      value = '';
    }
  }

  /**
   * Handle keyboard shortcuts
   */
  function handleKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSubmit(event);
    }
    
    // Show undo/redo hint on Ctrl/Cmd press
    if (event.ctrlKey || event.metaKey) {
      showUndoRedoHint = true;
    }
  }
  
  function handleKeyup(event: KeyboardEvent): void {
    if (!event.ctrlKey && !event.metaKey) {
      showUndoRedoHint = false;
    }
  }
  
  // Auto-adjust textarea height based on content
  $effect(() => {
    if (textarea && value) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  });
  
  /**
   * Focus the textarea
   * @public
   */
  export function focus(): void {
    textarea?.focus();
  }
  
  /**
   * Programmatically submit the query
   * @public
   */
  export function submit(): void {
    if (value && value.trim() && !disabled) {
      handleSubmit(new Event('submit'));
    }
  }
</script>

<form onsubmit={handleSubmit} class="w-full">
  <div class="relative">
    <textarea
      bind:this={textarea}
      bind:value
      onkeydown={handleKeydown}
      onkeyup={handleKeyup}
      {placeholder}
      {disabled}
      class="w-full px-4 py-3 pr-12 bg-gray-800 border border-gray-700 rounded-lg resize-none focus:outline-none focus:border-blue-500 transition-colors duration-200 placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
      rows="1"
    ></textarea>
    <button
      type="submit"
      disabled={disabled || !value?.trim()}
      class="absolute right-2 bottom-2 p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-colors duration-200"
      title="Send query"
      aria-label="Send query"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
      </svg>
    </button>
  </div>
  {#if disabled}
    <p class="mt-2 text-sm text-gray-500">Processing query...</p>
  {/if}
</form>

<style>
  textarea {
    min-height: 48px;
    max-height: 200px;
  }
</style>