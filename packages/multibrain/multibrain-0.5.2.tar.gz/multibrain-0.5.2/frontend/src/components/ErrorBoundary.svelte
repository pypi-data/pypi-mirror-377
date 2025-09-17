<!-- Svelte 5 Migration: ErrorBoundary.svelte - 2025-09-15 -->
<script lang="ts">
  import { toastStore } from '../stores/toasts.svelte';
  import type { Snippet } from 'svelte';
  
  interface ErrorInfo {
    componentStack: string;
    timestamp: string;
    userAgent: string;
    url: string;
    retryCount: number;
  }
  
  interface ErrorBoundaryProps {
    error?: Error | null;
    reset?: () => void;
    onError?: (error: Error, info: ErrorInfo) => void;
    fallback?: boolean;
    children?: Snippet;
  }
  
  let {
    error = null,
    reset = () => {},
    onError,
    fallback = true,
    children
  }: ErrorBoundaryProps = $props();
  
  let showDetails = $state(false);
  let errorInfo = $state<ErrorInfo | null>(null);
  let retryCount = $state(0);
  const MAX_RETRIES = 3;
  
  /**
   * Collect error information for debugging
   */
  function collectErrorInfo(err: Error): ErrorInfo {
    return {
      componentStack: err.stack || 'No stack trace available',
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      retryCount
    };
  }
  
  /**
   * Log error to external service (placeholder)
   */
  function logError(err: Error, info: ErrorInfo): void {
    // In production, this would send to an error tracking service
    console.group('🚨 Error Boundary Caught Error');
    console.error('Error:', err);
    console.table(info);
    console.groupEnd();
    
    // Call parent error handler if provided
    onError?.(err, info);
  }
  
  $effect(() => {
    if (error) {
      errorInfo = collectErrorInfo(error);
      logError(error, errorInfo);
      
      // Show toast only for first error (not retries)
      if (retryCount === 0) {
        toastStore.error('An unexpected error occurred');
      }
    }
  });
  
  /**
   * Handle reset with retry logic
   */
  function handleReset() {
    if (retryCount < MAX_RETRIES) {
      retryCount++;
      error = null;
      showDetails = false;
      errorInfo = null;
      reset();
      toastStore.info(`Retrying... (${retryCount}/${MAX_RETRIES})`);
    } else {
      toastStore.error('Maximum retry attempts reached. Please refresh the page.');
    }
  }
  
  /**
   * Copy error details to clipboard
   */
  async function copyErrorDetails() {
    if (!error || !errorInfo) return;
    
    const details = `
Error: ${error.message}
Time: ${errorInfo.timestamp}
URL: ${errorInfo.url}
User Agent: ${errorInfo.userAgent}
Retry Count: ${errorInfo.retryCount}

Stack Trace:
${error.stack}
    `.trim();
    
    try {
      await navigator.clipboard.writeText(details);
      toastStore.success('Error details copied to clipboard');
    } catch (err) {
      toastStore.error('Failed to copy error details');
    }
  }
  
  /**
   * Report error to developers
   */
  function reportError() {
    // In production, this would open a bug report form or send an email
    const subject = encodeURIComponent(`MultiBrain Error: ${error?.message || 'Unknown error'}`);
    const body = encodeURIComponent(`
Please describe what you were doing when this error occurred:

[Your description here]

--- Error Details ---
${error?.message || 'Unknown error'}
${errorInfo ? `Time: ${errorInfo.timestamp}` : ''}
${errorInfo ? `URL: ${errorInfo.url}` : ''}
    `.trim());
    
    window.open(`mailto:support@multibrain.app?subject=${subject}&body=${body}`);
  }
</script>

{#if error && fallback}
  <div class="min-h-screen bg-gray-900 text-gray-100 flex items-center justify-center p-4">
    <div class="max-w-2xl w-full">
      <div class="bg-gray-800 rounded-lg shadow-xl p-8 text-center">
        <!-- Error Icon -->
        <div class="mb-6">
          <svg class="w-20 h-20 mx-auto text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
        </div>
        
        <!-- Error Message -->
        <h1 class="text-2xl font-bold mb-2">Oops! Something went wrong</h1>
        <p class="text-gray-400 mb-6">
          We encountered an unexpected error. Don't worry, your data is safe.
        </p>
        
        <!-- Retry indicator -->
        {#if retryCount > 0}
          <p class="text-sm text-yellow-400 mb-4">
            Retry attempt {retryCount} of {MAX_RETRIES}
          </p>
        {/if}
        
        <!-- Error Details (collapsible) -->
        {#if showDetails && errorInfo}
          <div class="mb-6 text-left">
            <div class="bg-gray-900 rounded-lg p-4 overflow-auto max-h-64">
              <div class="space-y-2">
                <p class="text-sm font-mono text-red-400">{error.message || 'Unknown error'}</p>
                <div class="text-xs text-gray-500">
                  <p>Time: {errorInfo.timestamp}</p>
                  <p>URL: {errorInfo.url}</p>
                  <p>Retries: {errorInfo.retryCount}</p>
                </div>
                {#if error.stack}
                  <details class="mt-2">
                    <summary class="cursor-pointer text-gray-400 hover:text-gray-300">Stack Trace</summary>
                    <pre class="text-xs text-gray-500 mt-2 overflow-x-auto">{error.stack}</pre>
                  </details>
                {/if}
              </div>
            </div>
          </div>
        {/if}
        
        <!-- Actions -->
        <div class="flex flex-col sm:flex-row gap-3 justify-center mb-4">
          <button
            onclick={handleReset}
            disabled={retryCount >= MAX_RETRIES}
            class="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            {retryCount >= MAX_RETRIES ? 'Max Retries Reached' : 'Try Again'}
          </button>
          
          <button
            onclick={() => window.location.reload()}
            class="px-6 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg transition-colors duration-200"
          >
            Refresh Page
          </button>
          
          <button
            onclick={() => showDetails = !showDetails}
            class="px-6 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5 transform transition-transform {showDetails ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
            </svg>
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
        </div>
        
        <!-- Additional Actions -->
        {#if showDetails}
          <div class="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onclick={copyErrorDetails}
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors duration-200 text-sm flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
              </svg>
              Copy Details
            </button>
            
            <button
              onclick={reportError}
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors duration-200 text-sm flex items-center justify-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
              </svg>
              Report Issue
            </button>
          </div>
        {/if}
      </div>
      
      <!-- Help Text -->
      <p class="text-center text-sm text-gray-500 mt-6">
        {#if retryCount >= MAX_RETRIES}
          Maximum retry attempts reached. Please refresh the page or contact support if the issue persists.
        {:else}
          If this problem persists, please check your browser console for more information.
        {/if}
      </p>
    </div>
  </div>
{:else}
  {@render children?.()}
{/if}