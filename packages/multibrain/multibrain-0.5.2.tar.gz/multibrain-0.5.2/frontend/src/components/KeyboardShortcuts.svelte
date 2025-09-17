<!-- Svelte 5 Migration: KeyboardShortcuts.svelte - 2025-09-15 -->
<script>
  
  let { onopenConfig, onfocusQuery, onsubmitQuery, oncloseModal } = $props();
  
  // Define keyboard shortcuts
  const shortcuts = [
    { key: 'k', ctrl: true, action: 'openConfig', description: 'Open configuration' },
    { key: '/', ctrl: true, action: 'focusQuery', description: 'Focus query input' },
    { key: 'Enter', ctrl: true, action: 'submitQuery', description: 'Submit query' },
    { key: 'Escape', action: 'closeModal', description: 'Close modal' },
    { key: '?', shift: true, action: 'showHelp', description: 'Show keyboard shortcuts' }
  ];
  
  let showHelp = $state(false);
  
  function handleKeydown(event) {
    // Check if we're in an input field
    const isInputField = ['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName);
    
    for (const shortcut of shortcuts) {
      const keyMatch = event.key === shortcut.key || event.key.toLowerCase() === shortcut.key.toLowerCase();
      const ctrlMatch = !shortcut.ctrl || (event.ctrlKey || event.metaKey);
      const shiftMatch = !shortcut.shift || event.shiftKey;
      
      if (keyMatch && ctrlMatch && shiftMatch) {
        // Don't trigger shortcuts when typing in input fields (except Escape)
        if (isInputField && shortcut.key !== 'Escape') {
          continue;
        }
        
        event.preventDefault();
        
        if (shortcut.action === 'showHelp') {
          showHelp = !showHelp;
        } else {
          // Call the appropriate callback based on the action
          switch (shortcut.action) {
            case 'openConfig':
              onopenConfig?.();
              break;
            case 'focusQuery':
              onfocusQuery?.();
              break;
            case 'submitQuery':
              onsubmitQuery?.();
              break;
            case 'closeModal':
              oncloseModal?.();
              break;
          }
        }
        
        break;
      }
    }
  }
  
  $effect(() => {
    window.addEventListener('keydown', handleKeydown);
    
    return () => {
      window.removeEventListener('keydown', handleKeydown);
    };
  });
</script>

{#if showHelp}
  <div
    class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
    onclick={() => showHelp = false}
    onkeydown={(e) => e.key === 'Escape' && (showHelp = false)}
    role="button"
    tabindex="-1"
    aria-label="Close help dialog"
  >
    <div
      class="bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6"
      onclick={(e) => e.stopPropagation()}
      onkeydown={(e) => e.stopPropagation()}
      role="dialog"
      aria-modal="true"
      aria-labelledby="shortcuts-title"
      tabindex="-1"
    >
      <h3 id="shortcuts-title" class="text-lg font-semibold mb-4 flex items-center justify-between">
        <span>Keyboard Shortcuts</span>
        <button
          onclick={() => showHelp = false}
          class="p-1 hover:bg-gray-700 rounded transition-colors"
          aria-label="Close help dialog"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </h3>
      
      <div class="space-y-2">
        {#each shortcuts as shortcut}
          <div class="flex items-center justify-between py-2">
            <span class="text-sm text-gray-300">{shortcut.description}</span>
            <kbd class="px-2 py-1 bg-gray-700 rounded text-xs font-mono">
              {#if shortcut.ctrl}
                <span class="text-gray-400">Ctrl+</span>
              {/if}
              {#if shortcut.shift}
                <span class="text-gray-400">Shift+</span>
              {/if}
              {shortcut.key}
            </kbd>
          </div>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  kbd {
    box-shadow: 0 2px 0 1px rgba(0, 0, 0, 0.2);
  }
</style>