<!-- Svelte 5 Follow-Up Input Component -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  
  interface FollowUpInputProps {
    disabled?: boolean;
    parentQueryId: string;
    onsubmit?: (query: string, parentQueryId: string) => void;
  }
  
  let {
    disabled = false,
    parentQueryId,
    onsubmit
  }: FollowUpInputProps = $props();
  
  let value = $state('');
  let textarea = $state<HTMLTextAreaElement>();
  let isFocused = $state(false);
  
  /**
   * Handle form submission
   */
  function handleSubmit(event: Event): void {
    event.preventDefault();
    if (value && value.trim() && !disabled) {
      onsubmit?.(value, parentQueryId);
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
  }
  
  // Auto-adjust textarea height based on content
  $effect(() => {
    if (textarea && value) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  });
  
  // Auto-focus on mount
  onMount(() => {
    textarea?.focus();
  });
  
  /**
   * Focus the textarea
   * @public
   */
  export function focus(): void {
    textarea?.focus();
  }
</script>

<div class="follow-up-container" in:fade={{ duration: 300 }}>
  <div class="follow-up-header">
    <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
    </svg>
    <span class="text-sm text-gray-400">Ask a follow-up question</span>
  </div>
  
  <form onsubmit={handleSubmit} class="follow-up-form">
    <div class="relative">
      <textarea
        bind:this={textarea}
        bind:value
        onfocus={() => isFocused = true}
        onblur={() => isFocused = false}
        onkeydown={handleKeydown}
        placeholder="Ask a follow-up question..."
        {disabled}
        class="follow-up-input"
        class:focused={isFocused}
        rows="1"
      ></textarea>
      <button
        type="submit"
        disabled={disabled || !value?.trim()}
        class="follow-up-submit"
        title="Send follow-up"
        aria-label="Send follow-up question"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
        </svg>
      </button>
    </div>
    {#if disabled}
      <p class="mt-2 text-xs text-gray-500">Processing follow-up...</p>
    {/if}
  </form>
</div>

<style>
  .follow-up-container {
    margin-top: 1rem;
    padding: 1rem;
    background-color: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 0.5rem;
  }
  
  .follow-up-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
  }
  
  .follow-up-form {
    width: 100%;
  }
  
  .follow-up-input {
    width: 100%;
    padding: 0.625rem 2.5rem 0.625rem 0.875rem;
    background-color: rgba(31, 41, 55, 0.8);
    border: 1px solid rgba(75, 85, 99, 0.5);
    border-radius: 0.375rem;
    resize: none;
    color: #e5e7eb;
    font-size: 0.875rem;
    transition: all 0.2s;
    min-height: 38px;
    max-height: 120px;
  }
  
  .follow-up-input:focus {
    outline: none;
    border-color: #3b82f6;
    background-color: rgba(31, 41, 55, 1);
  }
  
  .follow-up-input.focused {
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
  }
  
  .follow-up-input::placeholder {
    color: #9ca3af;
  }
  
  .follow-up-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .follow-up-submit {
    position: absolute;
    right: 0.5rem;
    bottom: 0.5rem;
    padding: 0.375rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .follow-up-submit:hover:not(:disabled) {
    background-color: #2563eb;
    transform: scale(1.05);
  }
  
  .follow-up-submit:disabled {
    background-color: #4b5563;
    cursor: not-allowed;
    opacity: 0.5;
  }
</style>