<!-- Svelte 5 Migration: SummaryStream.svelte - 2025-09-15 -->
<script>
  import { marked } from 'marked';
  
  let { stream } = $props();
  let content = $derived(stream.content);
  let isStreaming = $derived(stream.status === 'streaming');
  let hasError = $derived(stream.status === 'error');
  let isComplete = $derived(stream.status === 'complete');

  // Configure marked for better code highlighting
  marked.setOptions({
    breaks: true,
    gfm: true,
  });

  let htmlContent = $derived(marked(content));
</script>

<div class="bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg border border-blue-700/50 overflow-hidden">
  <!-- Header -->
  <div class="px-4 py-3 border-b border-blue-700/50 flex items-center justify-between bg-gray-800/50">
    <div class="flex items-center gap-2">
      <svg class="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
      </svg>
      <h3 class="font-semibold text-lg text-blue-300">Summary Analysis</h3>
      {#if isStreaming}
        <div class="flex items-center gap-1">
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <span class="text-sm text-gray-400">Analyzing...</span>
        </div>
      {:else if hasError}
        <div class="flex items-center gap-1">
          <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-sm text-red-500">Error</span>
        </div>
      {:else if isComplete}
        <div class="flex items-center gap-1">
          <svg class="w-4 h-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-sm text-green-500">Complete</span>
        </div>
      {/if}
    </div>
    <span class="text-xs text-gray-400">{stream.model}</span>
  </div>

  <!-- Content -->
  <div class="p-6 max-h-[600px] overflow-y-auto scrollbar-thin">
    {#if hasError}
      <div class="text-red-400">
        <p class="font-semibold mb-2">Error occurred:</p>
        <p class="text-sm">{stream.error || 'Unknown error'}</p>
      </div>
    {:else if content}
      <div class="markdown-content prose prose-invert max-w-none">
        {@html htmlContent}
      </div>
      {#if isStreaming}
        <span class="inline-block w-2 h-4 bg-blue-400 streaming-cursor ml-1"></span>
      {/if}
    {:else}
      <p class="text-gray-400 italic">Preparing summary analysis...</p>
    {/if}
  </div>

  <!-- Footer with metrics -->
  {#if stream.metrics}
    <div class="px-4 py-2 border-t border-blue-700/50 flex items-center justify-between text-xs text-gray-400 bg-gray-800/50">
      {#if stream.metrics.firstTokenTime}
        <span>First token: {stream.metrics.firstTokenTime}ms</span>
      {/if}
      {#if stream.metrics.totalTime}
        <span>Total time: {(stream.metrics.totalTime / 1000).toFixed(1)}s</span>
      {/if}
      {#if stream.metrics.tokensPerSecond}
        <span>{stream.metrics.tokensPerSecond.toFixed(1)} tokens/s</span>
      {/if}
    </div>
  {/if}
</div>

<style>
  :global(.markdown-content pre) {
    @apply bg-gray-900/80;
  }
  
  :global(.markdown-content code) {
    @apply bg-gray-900/80;
  }
</style>