<!-- Svelte 5 Migration: ResponseContainer.svelte - 2025-09-15 -->
<script>
  import QueryResponseContainer from './QueryResponseContainer.svelte';
  import { queryStore } from '../stores/queries.svelte';
  import { streamStore } from '../stores/streams.svelte';

  let { oncomplete, onFollowUp, emptyStateSnippet, queryItemSnippet } = $props();

  // Get active queries (those with streaming data)
  // Optimize by creating a Set for O(1) lookup instead of O(n) with includes
  let activeQueryIds = $derived(Object.keys(streamStore.queries));
  let activeQueryIdSet = $derived(new Set(activeQueryIds));
  let queries = $derived(queryStore.queries.filter(q => activeQueryIdSet.has(q.id)));
  
  function handleQueryComplete(detail) {
    oncomplete?.(detail);
  }
  
  function handleQueryRemove(detail) {
    // Query removal is handled by the QueryResponseContainer
  }
  
  function handleFollowUp(detail) {
    onFollowUp?.(detail);
  }
</script>

<!-- Default empty state snippet -->
{#snippet defaultEmptyState()}
  <div class="text-center py-12">
    <svg class="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
    </svg>
    <p class="text-gray-500">Ask a question to get responses from multiple LLMs</p>
  </div>
{/snippet}

<!-- Default query item snippet -->
{#snippet defaultQueryItem(query)}
  <QueryResponseContainer
    queryId={query.id}
    queryText={query.text}
    timestamp={query.timestamp}
    oncomplete={handleQueryComplete}
    onremove={handleQueryRemove}
    onFollowUp={handleFollowUp}
  />
{/snippet}

<div class="space-y-6">
  {#if queries.length === 0}
    {#if emptyStateSnippet}
      {@render emptyStateSnippet()}
    {:else}
      {@render defaultEmptyState()}
    {/if}
  {:else}
    <!-- Display all active queries -->
    {#each queries as query (query.id)}
      {#if queryItemSnippet}
        {@render queryItemSnippet(query, handleQueryComplete, handleQueryRemove)}
      {:else}
        {@render defaultQueryItem(query)}
      {/if}
    {/each}
  {/if}
</div>