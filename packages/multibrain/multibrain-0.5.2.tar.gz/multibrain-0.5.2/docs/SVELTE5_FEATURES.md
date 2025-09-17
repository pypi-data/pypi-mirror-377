# Svelte 5 Features in MultiBrain

This document outlines the Svelte 5 features implemented in the MultiBrain application after the migration from Svelte 4.

## Table of Contents
- [Overview](#overview)
- [Runes API](#runes-api)
- [Component Props](#component-props)
- [State Management](#state-management)
- [Effects and Lifecycle](#effects-and-lifecycle)
- [Performance Improvements](#performance-improvements)
- [Migration Patterns](#migration-patterns)

## Overview

MultiBrain has been fully migrated to Svelte 5, leveraging the new runes API for improved performance, better type safety, and a more intuitive developer experience. The migration was completed on 2025-09-15.

## Runes API

### $state
The `$state` rune replaces the traditional `let` declarations for reactive state:

```javascript
// Before (Svelte 4)
let count = 0;

// After (Svelte 5)
let count = $state(0);
```

**Examples in MultiBrain:**
- `QueryInput.svelte`: Input field state management
- `ConfigModal.svelte`: Modal visibility and form state
- `ToastContainer.svelte`: Toast notifications array

### $derived
The `$derived` rune replaces reactive statements (`$:`) for computed values:

```javascript
// Before (Svelte 4)
$: doubled = count * 2;

// After (Svelte 5)
let doubled = $derived(count * 2);
```

**Examples in MultiBrain:**
- `App.svelte`: Active LLM count calculation
- `ResponseContainer.svelte`: Response status derivation
- `DebugPanel.svelte`: Debug information formatting

### $effect
The `$effect` rune replaces reactive statements for side effects:

```javascript
// Before (Svelte 4)
$: {
  console.log('Count changed:', count);
  localStorage.setItem('count', count);
}

// After (Svelte 5)
$effect(() => {
  console.log('Count changed:', count);
  localStorage.setItem('count', count);
});
```

**Examples in MultiBrain:**
- `QueryInput.svelte`: Auto-resize textarea based on content
- `ConfigModal.svelte`: Focus management
- `WelcomeGuide.svelte`: Progress tracking

## Component Props

### $props()
All components now use the `$props()` rune for prop declarations:

```javascript
// Before (Svelte 4)
export let value = '';
export let disabled = false;
export let onSubmit;

// After (Svelte 5)
let {
  value = '',
  disabled = false,
  onsubmit
} = $props();
```

### $bindable
Two-way binding is now explicit with the `$bindable` rune:

```javascript
// Component definition
let {
  value = $bindable(''),
  checked = $bindable(false)
} = $props();

// Parent usage remains the same
<Component bind:value={myValue} bind:checked={myChecked} />
```

**Examples in MultiBrain:**
- `QueryInput.svelte`: Bindable input value
- `LLMConfigForm.svelte`: Form field bindings
- `ConfigModal.svelte`: Modal visibility binding

## State Management

### Store Files (.svelte.js)
All stores have been migrated to `.svelte.js` files using runes:

```javascript
// stores/counter.svelte.js
let count = $state(0);

export function getCount() {
  return count;
}

export function increment() {
  count++;
}

export function reset() {
  count = 0;
}
```

**MultiBrain Stores:**
- `config.svelte.js`: LLM configuration management
- `queries.svelte.js`: Query history and state
- `streams.svelte.js`: Real-time streaming responses
- `toasts.svelte.js`: Toast notification system
- `debug.svelte.js`: Debug mode and logging
- `queryStateMachine.svelte.js`: Query workflow state machine

### Store Patterns

1. **Encapsulation**: All state is private, exposed through functions
2. **Type Safety**: Better TypeScript integration with explicit return types
3. **Reactivity**: Automatic reactivity without manual subscriptions
4. **Performance**: More efficient updates with fine-grained reactivity

## Effects and Lifecycle

### onMount
Still available and used for initialization:

```javascript
import { onMount } from 'svelte';

onMount(() => {
  // Initialize component
  return () => {
    // Cleanup
  };
});
```

### $effect with Cleanup
Effects can return cleanup functions:

```javascript
$effect(() => {
  const handler = (e) => console.log(e);
  window.addEventListener('resize', handler);
  
  return () => {
    window.removeEventListener('resize', handler);
  };
});
```

### $effect.pre
For effects that need to run before DOM updates:

```javascript
$effect.pre(() => {
  // Runs before DOM updates
  measureElement();
});
```

## Performance Improvements

### Fine-grained Reactivity
Svelte 5's runes provide more precise reactivity:

1. **Selective Updates**: Only components that actually use changed values re-render
2. **Reduced Memory**: No need for subscription management
3. **Faster Compilation**: Improved compiler optimizations

### Bundle Size
The migration to Svelte 5 resulted in:
- Smaller runtime overhead
- Better tree-shaking
- More efficient component code

### Reactivity Performance
- Faster state updates
- Reduced unnecessary re-renders
- Better handling of large lists and complex state

## Migration Patterns

### Common Patterns Used

1. **Reactive Statements to $derived**:
```javascript
// Before
$: isValid = name && email && password;

// After
let isValid = $derived(name && email && password);
```

2. **Reactive Blocks to $effect**:
```javascript
// Before
$: {
  if (user) {
    loadUserData(user.id);
  }
}

// After
$effect(() => {
  if (user) {
    loadUserData(user.id);
  }
});
```

3. **Store Subscriptions to Direct Access**:
```javascript
// Before
import { config } from './stores/config.js';
let configValue;
const unsubscribe = config.subscribe(value => {
  configValue = value;
});

// After
import { getConfig } from './stores/config.svelte.js';
// Direct access, automatically reactive
let config = $derived(getConfig());
```

### Component Structure
All components follow this structure:

```javascript
<script>
  import { onMount } from 'svelte';
  
  // Props declaration
  let {
    prop1 = 'default',
    prop2 = $bindable(false),
    onEvent
  } = $props();
  
  // State declarations
  let localState = $state(initialValue);
  
  // Derived values
  let computed = $derived(calculateValue(localState));
  
  // Effects
  $effect(() => {
    // Side effects
  });
  
  // Lifecycle
  onMount(() => {
    // Initialization
  });
  
  // Methods
  function handleAction() {
    // Handle actions
  }
</script>
```

## Best Practices

1. **Use $state for all reactive values**: Even simple primitives benefit from explicit reactivity
2. **Prefer $derived over $effect**: Use derived values when possible for better performance
3. **Keep effects minimal**: Effects should only handle side effects, not compute values
4. **Explicit bindings**: Use $bindable for two-way bindings to make data flow clear
5. **Encapsulate store logic**: Keep store state private and expose only necessary functions

## Conclusion

The migration to Svelte 5 has resulted in:
- Cleaner, more maintainable code
- Better performance characteristics
- Improved developer experience
- Enhanced type safety
- More predictable reactivity

All components and stores in MultiBrain now fully leverage Svelte 5's features, providing a solid foundation for future development.