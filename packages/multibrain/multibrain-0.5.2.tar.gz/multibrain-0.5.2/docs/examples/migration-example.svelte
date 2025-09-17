<!-- 
  Svelte 5 Migration Example
  This file demonstrates the key changes when migrating from Svelte 4 to Svelte 5
-->

<!-- ============================================ -->
<!-- BEFORE: Svelte 4 Style Component -->
<!-- ============================================ -->

<script>
  // --- Svelte 4 Style ---
  
  // Props using export let
  export let title = 'Default Title';
  export let count = 0;
  export let disabled = false;
  
  // Event dispatcher
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  
  // Local state
  let inputValue = '';
  let isLoading = false;
  
  // Reactive declarations
  $: doubled = count * 2;
  $: isEven = count % 2 === 0;
  $: buttonText = isLoading ? 'Loading...' : 'Submit';
  
  // Reactive statements
  $: if (count > 10) {
    console.log('Count is high!');
  }
  
  $: {
    if (inputValue.length > 0) {
      console.log('Input changed:', inputValue);
    }
  }
  
  // Event handlers
  function handleClick() {
    dispatch('increment', { amount: 1 });
  }
  
  function handleSubmit() {
    if (inputValue.trim()) {
      dispatch('submit', { value: inputValue });
      inputValue = '';
    }
  }
</script>

<div class="example">
  <h2>{title}</h2>
  
  <p>Count: {count}</p>
  <p>Doubled: {doubled}</p>
  <p>Is even: {isEven}</p>
  
  <!-- Event handlers with on: syntax -->
  <button 
    on:click={handleClick}
    disabled={disabled}
  >
    Increment
  </button>
  
  <form on:submit|preventDefault={handleSubmit}>
    <input 
      bind:value={inputValue}
      on:input={() => console.log('typing...')}
      placeholder="Enter text"
    />
    <button type="submit" disabled={isLoading}>
      {buttonText}
    </button>
  </form>
  
  <!-- Slots -->
  <div class="content">
    <slot name="header">
      <h3>Default Header</h3>
    </slot>
    <slot>Default content</slot>
    <slot name="footer" {count} />
  </div>
</div>

<!-- ============================================ -->
<!-- AFTER: Svelte 5 Style Component -->
<!-- ============================================ -->

<script>
  // --- Svelte 5 Style ---
  
  // Props using $props() rune
  let { 
    title = 'Default Title', 
    count = 0, 
    disabled = false,
    onincrement,
    onsubmit 
  } = $props();
  
  // Local state using $state() rune
  let inputValue = $state('');
  let isLoading = $state(false);
  
  // Reactive values using $derived() rune
  let doubled = $derived(count * 2);
  let isEven = $derived(count % 2 === 0);
  let buttonText = $derived(isLoading ? 'Loading...' : 'Submit');
  
  // Side effects using $effect() rune
  $effect(() => {
    if (count > 10) {
      console.log('Count is high!');
    }
  });
  
  $effect(() => {
    if (inputValue.length > 0) {
      console.log('Input changed:', inputValue);
    }
  });
  
  // Event handlers (now just regular functions)
  function handleClick() {
    onincrement?.({ amount: 1 });
  }
  
  function handleSubmit(e) {
    e.preventDefault();
    if (inputValue.trim()) {
      onsubmit?.({ value: inputValue });
      inputValue = '';
    }
  }
</script>

<div class="example">
  <h2>{title}</h2>
  
  <p>Count: {count}</p>
  <p>Doubled: {doubled}</p>
  <p>Is even: {isEven}</p>
  
  <!-- Event handlers with new syntax -->
  <button 
    onclick={handleClick}
    {disabled}
  >
    Increment
  </button>
  
  <form onsubmit={handleSubmit}>
    <input 
      bind:value={inputValue}
      oninput={() => console.log('typing...')}
      placeholder="Enter text"
    />
    <button type="submit" disabled={isLoading}>
      {buttonText}
    </button>
  </form>
  
  <!-- Snippets instead of slots -->
  <div class="content">
    {#snippet header()}
      <h3>Default Header</h3>
    {/snippet}
    
    {#snippet footer({ count })}
      <p>Footer with count: {count}</p>
    {/snippet}
    
    {@render header()}
    {@render children?.() || 'Default content'}
    {@render footer({ count })}
  </div>
</div>

<!-- ============================================ -->
<!-- KEY MIGRATION CHANGES SUMMARY -->
<!-- ============================================ -->

<!--
1. Props Migration:
   - Before: export let propName = defaultValue;
   - After: let { propName = defaultValue } = $props();

2. Event Handlers:
   - Before: on:click={handler}
   - After: onclick={handler}
   - Event modifiers (|preventDefault) must be handled in the function

3. Event Dispatching:
   - Before: createEventDispatcher() and dispatch('event', detail)
   - After: Callback props like onincrement, onsubmit

4. State Management:
   - Before: let value = initialValue;
   - After: let value = $state(initialValue);

5. Reactive Declarations:
   - Before: $: derived = someExpression;
   - After: let derived = $derived(someExpression);

6. Reactive Statements/Effects:
   - Before: $: { /* side effect code */ }
   - After: $effect(() => { /* side effect code */ });

7. Slots to Snippets:
   - Before: <slot name="header">Default</slot>
   - After: {#snippet header()}Default{/snippet} and {@render header()}

8. Component Instantiation (not shown here):
   - Before: new Component({ target, props })
   - After: mount(Component, { target, props })

9. Store Usage (not shown here):
   - Before: $storeName
   - After: Direct property access with reactive stores in .svelte.js files
-->

<style>
  .example {
    padding: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin: 1rem 0;
  }
  
  .content {
    margin-top: 1rem;
    padding: 1rem;
    background-color: #f5f5f5;
  }
  
  button {
    margin: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid #007bff;
    background-color: #007bff;
    color: white;
    border-radius: 4px;
    cursor: pointer;
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  input {
    padding: 0.5rem;
    margin: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
</style>