<!-- Svelte 5 Migration: LoadingSpinner.svelte - 2025-09-15 -->
<script lang="ts">
  type Size = 'small' | 'medium' | 'large';
  type Color = 'blue' | 'gray' | 'white';
  
  interface LoadingSpinnerProps {
    size?: Size;
    color?: Color;
  }
  
  let { size = 'medium', color = 'blue' }: LoadingSpinnerProps = $props();
  
  const sizeClasses: Record<Size, string> = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };
  
  const colorClasses: Record<Color, string> = {
    blue: 'text-blue-500',
    gray: 'text-gray-500',
    white: 'text-white'
  };
</script>

<div class="inline-flex items-center justify-center">
  <svg 
    class="animate-spin {sizeClasses[size]} {colorClasses[color]}" 
    xmlns="http://www.w3.org/2000/svg" 
    fill="none" 
    viewBox="0 0 24 24"
  >
    <circle 
      class="opacity-25" 
      cx="12" 
      cy="12" 
      r="10" 
      stroke="currentColor" 
      stroke-width="4"
    ></circle>
    <path 
      class="opacity-75" 
      fill="currentColor" 
      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
    ></path>
  </svg>
</div>