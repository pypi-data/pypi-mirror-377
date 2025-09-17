<!-- Svelte 5 Migration: Toast.svelte - 2025-09-15 -->
<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import type { ToastType } from '../types';
  
  interface ToastProps {
    message?: string;
    type?: ToastType;
    duration?: number;
    onClose?: () => void;
  }
  
  let { message = '', type = 'info', duration = 3000, onClose = () => {} }: ToastProps = $props();
  
  const typeStyles: Record<ToastType, string> = {
    info: 'bg-blue-600 text-white',
    success: 'bg-green-600 text-white',
    warning: 'bg-yellow-600 text-white',
    error: 'bg-red-600 text-white'
  };
  
  const icons: Record<ToastType, string> = {
    info: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>`,
    success: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>`,
    warning: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
    </svg>`,
    error: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>`
  };
  
  $effect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  });
</script>

<div
  in:fly={{ y: -50, duration: 300 }}
  out:fade={{ duration: 200 }}
  class="fixed top-4 right-4 z-50 max-w-md"
>
  <div class="{typeStyles[type]} rounded-lg shadow-lg p-4 flex items-start gap-3">
    <div class="flex-shrink-0">
      {@html icons[type]}
    </div>
    <div class="flex-1">
      <p class="text-sm font-medium">{message}</p>
    </div>
    <button
      onclick={onClose}
      class="flex-shrink-0 ml-2 hover:opacity-75 transition-opacity"
      aria-label="Close notification"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>
  </div>
</div>