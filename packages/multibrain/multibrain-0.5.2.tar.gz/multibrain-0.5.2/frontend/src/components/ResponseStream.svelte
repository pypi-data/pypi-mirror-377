<!-- Svelte 5 Migration: ResponseStream.svelte - 2025-09-15 -->
<script>
  import { marked } from 'marked';
  import { sanitizeContent } from '../lib/errorHandling';
  
  /**
   * @typedef {import('../stores/streams.svelte.js').Stream} Stream
   */
  
  /**
   * Component props
   * @type {{ stream: Stream }}
   */
  let { stream } = $props();
  let contentElement = $state();
  let shouldAutoScroll = $state(true);
  let renderedContent = $state('');
  let lastRenderedLength = $state(0);
  
  // Use raw state for metrics to prevent unnecessary re-renders
  let metrics = $state.raw(stream.metrics || {});

  let content = $derived(stream.content);
  let isStreaming = $derived(stream.status === 'streaming');
  let hasError = $derived(stream.status === 'error');
  let isComplete = $derived(stream.status === 'complete');
  
  // Update frozen metrics when stream metrics change
  // Only update if metrics actually changed to avoid unnecessary updates
  $effect(() => {
    if (stream.metrics && stream.metrics !== metrics) {
      metrics = stream.metrics;
    }
  });

  // Configure marked for better code highlighting
  marked.setOptions({
    breaks: true,
    gfm: true,
    sanitize: false, // We'll sanitize ourselves
  });

  /**
   * Render markdown content with sanitization
   * @param {string} text - Raw markdown text
   */
  const renderMarkdown = (text) => {
    const sanitized = sanitizeContent(text);
    renderedContent = marked(sanitized);
    requestAnimationFrame(scrollToBottom);
  };

  // Update rendered content when stream content changes
  // Use $effect.pre for DOM measurements before updates
  $effect.pre(() => {
    if (contentElement && shouldAutoScroll) {
      // Capture scroll position before DOM updates
      const { scrollTop, scrollHeight, clientHeight } = contentElement;
      shouldAutoScroll = scrollTop + clientHeight >= scrollHeight - 50;
    }
  });
  
  $effect(() => {
    if (content) {
      // For streaming, render immediately
      if (isStreaming && content.length > lastRenderedLength) {
        renderMarkdown(content);
        lastRenderedLength = content.length;
      } else if (!isStreaming && lastRenderedLength !== content.length) {
        // When complete or error, render final content only if changed
        renderMarkdown(content);
        lastRenderedLength = content.length;
      }
    }
  });

  /**
   * Check if auto-scroll should be enabled based on scroll position
   */
  function checkAutoScroll() {
    if (contentElement) {
      const { scrollTop, scrollHeight, clientHeight } = contentElement;
      shouldAutoScroll = scrollTop + clientHeight >= scrollHeight - 50;
    }
  }

  /**
   * Scroll to bottom of content if auto-scroll is enabled
   */
  function scrollToBottom() {
    if (contentElement && shouldAutoScroll && isStreaming) {
      contentElement.scrollTop = contentElement.scrollHeight;
    }
  }

  // Auto-scroll is enabled by default (set in initial state)
</script>

<div class="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
  <!-- Header -->
  <div class="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
    <div class="flex items-center gap-2">
      <h3 class="font-semibold text-lg">{stream.llmName}</h3>
      {#if isStreaming}
        <div class="flex items-center gap-1">
          <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
          <span class="text-sm text-gray-400">Streaming...</span>
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
    <span class="text-xs text-gray-500">{stream.model}</span>
  </div>

  <!-- Content -->
  <div
    bind:this={contentElement}
    onscroll={checkAutoScroll}
    class="p-4 max-h-96 overflow-y-auto scrollbar-thin"
  >
    {#if hasError}
      <div class="text-red-400">
        <p class="font-semibold mb-2">Error occurred:</p>
        <p class="text-sm">{stream.error || 'Unknown error'}</p>
      </div>
    {:else if content || renderedContent}
      <div class="markdown-content prose prose-invert max-w-none">
        {@html renderedContent}
      </div>
      {#if isStreaming}
        <span class="inline-block w-2 h-4 bg-blue-400 streaming-cursor ml-1"></span>
      {/if}
    {:else}
      <p class="text-gray-500 italic">Waiting for response...</p>
    {/if}
  </div>

  <!-- Footer with metrics -->
  {#if metrics && Object.keys(metrics).length > 0}
    <div class="px-4 py-2 border-t border-gray-700 flex items-center justify-between text-xs text-gray-500">
      {#if metrics.firstTokenTime}
        <span>First token: {metrics.firstTokenTime}ms</span>
      {/if}
      {#if metrics.totalTime}
        <span>Total time: {(metrics.totalTime / 1000).toFixed(1)}s</span>
      {/if}
      {#if metrics.tokensPerSecond}
        <span>{metrics.tokensPerSecond.toFixed(1)} tokens/s</span>
      {/if}
    </div>
  {/if}
</div>

<style>
  :global(.markdown-content pre) {
    @apply bg-gray-900 rounded p-3 overflow-x-auto;
  }
  
  :global(.markdown-content code) {
    @apply bg-gray-900 px-1 py-0.5 rounded text-sm;
  }
  
  :global(.markdown-content pre code) {
    @apply p-0;
  }
  
  .streaming-cursor {
    animation: blink 1s infinite;
  }
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
  
  .scrollbar-thin {
    scrollbar-width: thin;
    scrollbar-color: #4b5563 #1f2937;
  }
  
  .scrollbar-thin::-webkit-scrollbar {
    width: 8px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-track {
    background: #1f2937;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb {
    background: #4b5563;
    border-radius: 4px;
  }
  
  .scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background: #6b7280;
  }
</style>