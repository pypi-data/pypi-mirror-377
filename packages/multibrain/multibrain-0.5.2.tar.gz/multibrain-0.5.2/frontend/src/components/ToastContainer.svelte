<!-- Svelte 5 Migration: ToastContainer.svelte - 2025-09-15 -->
<script lang="ts">
  import { toastStore } from '../stores/toasts.svelte';
  import Toast from './Toast.svelte';
  import { flip } from 'svelte/animate';
  import type { Snippet } from 'svelte';
  import type { Toast as ToastType } from '../types';
  
  interface ToastContainerProps {
    toastSnippet?: Snippet<[ToastType, () => void]>;
  }
  
  // Allow custom toast rendering via snippet
  let { toastSnippet }: ToastContainerProps = $props();
  
  // Add performance monitoring in development
  if (import.meta.env.DEV) {
    $inspect(toastStore.toasts).with((type, value) => {
      console.log('[ToastContainer] toasts updated:', {
        type,
        count: value.length,
        timestamp: new Date().toISOString()
      });
    });
  }
  
</script>

<!-- Default toast rendering snippet -->
{#snippet defaultToast(toast)}
  <Toast
    message={toast.message}
    type={toast.type}
    duration={0}
    onClose={() => toastStore.remove(toast.id)}
  />
{/snippet}

<div class="fixed top-4 right-4 z-50 space-y-2">
  {#each toastStore.toasts as toast (toast.id)}
    <div animate:flip={{ duration: 200 }}>
      {#if toastSnippet}
        {@render toastSnippet(toast, () => toastStore.remove(toast.id))}
      {:else}
        {@render defaultToast(toast)}
      {/if}
    </div>
  {/each}
</div>