<!-- Svelte 5 Migration: QueryResponseContainer.svelte - 2025-09-15 -->
<script>
  import ResponseStream from './ResponseStream.svelte';
  import SummaryStream from './SummaryStream.svelte';
  import FollowUpInput from './FollowUpInput.svelte';
  import { streamStore, queryComplete } from '../stores/streams.svelte';
  import { queryStore } from '../stores/queries.svelte';
  
  let { queryId, queryText, timestamp , oncomplete, onremove, onFollowUp } = $props();
  let queryData = $derived(streamStore.queries[queryId] || { streams: [], summary: null, isStreaming: false, error: null });
  let isComplete = $derived(queryComplete(queryId));
  let showFollowUp = $state(false);
  let summaryContent = $state('');
  let hasCompletedOnce = $state(false);
  
  // Calculate overall query duration
  let queryDuration = $derived(() => {
    if (!queryData.streams || queryData.streams.length === 0) return null;
    
    // Find earliest start time
    let earliestStart = Math.min(...queryData.streams.map(s => s.metrics?.startTime || Infinity));
    
    // Find latest end time (when all streams are complete)
    if (!isComplete) return null;
    
    let latestEnd = Math.max(...queryData.streams.map(s => {
      if (s.metrics?.totalTime && s.metrics?.startTime) {
        return s.metrics.startTime + s.metrics.totalTime;
      }
      return 0;
    }));
    
    if (earliestStart === Infinity || latestEnd === 0) return null;
    
    return latestEnd - earliestStart;
  });
  
  $effect(() => {
    if (isComplete && !hasCompletedOnce) {
      hasCompletedOnce = true;
      oncomplete?.({ queryId });
      // Show follow-up input when summary is complete and has content
      if (queryData.summary?.status === 'complete' && queryData.summary?.content) {
        showFollowUp = true;
        summaryContent = queryData.summary.content;
        // Update the query with the summary content
        queryStore.updateQuery(queryId, { summaryContent: queryData.summary.content });
      }
    }
  });
  
  function handleAbort() {
    streamStore.abortQuery(queryId);
  }
  
  function handleRemove() {
    onremove?.({ queryId });
    streamStore.removeQuery(queryId);
  }
  
  function handleFollowUp(query, parentQueryId) {
    showFollowUp = false; // Hide the input after submission
    onFollowUp?.({ query, parentQueryId, summaryContent });
  }
</script>

<div class="bg-gray-800 rounded-lg p-4 mb-6 border border-gray-700">
  <!-- Query Header -->
  <div class="flex items-start justify-between mb-4">
    <div class="flex-1">
      <h3 class="text-lg font-semibold text-gray-200 mb-1">{queryText}</h3>
      <p class="text-sm text-gray-500">
        {new Date(timestamp).toLocaleString()}
        {#if queryData.isStreaming}
          <span class="ml-2 text-blue-400">• Processing...</span>
        {:else if isComplete}
          <span class="ml-2 text-green-400">• Complete</span>
          {#if queryDuration}
            <span class="ml-2 text-gray-400">• Query duration: {(queryDuration / 1000).toFixed(1)}s</span>
          {/if}
        {:else if queryData.error}
          <span class="ml-2 text-red-400">• Error</span>
        {/if}
      </p>
    </div>
    <div class="flex gap-2">
      {#if queryData.isStreaming}
        <button
          onclick={handleAbort}
          class="px-3 py-1 text-sm bg-red-600 hover:bg-red-700 rounded transition-colors"
          title="Abort query"
        >
          Abort
        </button>
      {/if}
      <button
        onclick={handleRemove}
        class="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 rounded transition-colors"
        title="Remove query"
      >
        ×
      </button>
    </div>
  </div>
  
  <!-- Error Display -->
  {#if queryData.error}
    <div class="mb-4 p-3 bg-red-900/20 border border-red-700 rounded text-red-400">
      {queryData.error}
    </div>
  {/if}
  
  <!-- Individual LLM Responses -->
  {#if queryData.streams.length > 0}
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
      {#each queryData.streams as stream (stream.id)}
        <ResponseStream {stream} />
      {/each}
    </div>
  {/if}
  
  <!-- Summary Response -->
  {#if queryData.summary}
    <div class="mt-4">
      <SummaryStream stream={queryData.summary} />
    </div>
  {/if}
  
  <!-- Follow-up Input -->
  {#if showFollowUp && !queryData.isStreaming && !queryData.error}
    <FollowUpInput
      parentQueryId={queryId}
      disabled={false}
      onsubmit={handleFollowUp}
    />
  {/if}
</div>