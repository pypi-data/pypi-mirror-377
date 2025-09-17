// Test utilities for Svelte 5 component testing
import { render } from '@testing-library/svelte';
import { vi } from 'vitest';

/**
 * Custom render function that includes common test setup
 * @param {import('svelte').Component} Component - The Svelte component to render
 * @param {object} options - Render options including props
 * @returns {object} - Testing library render result
 */
export function renderComponent(Component, options = {}) {
  return render(Component, {
    ...options,
  });
}

/**
 * Helper to create mock stores for testing
 * @param {any} initialValue - Initial value for the store
 * @returns {object} - Mock store with subscribe, set, and update methods
 */
export function createMockStore(initialValue) {
  let value = initialValue;
  const subscribers = new Set();

  return {
    subscribe: vi.fn((fn) => {
      fn(value);
      subscribers.add(fn);
      return () => subscribers.delete(fn);
    }),
    set: vi.fn((newValue) => {
      value = newValue;
      subscribers.forEach(fn => fn(value));
    }),
    update: vi.fn((updater) => {
      value = updater(value);
      subscribers.forEach(fn => fn(value));
    }),
  };
}

/**
 * Helper to wait for async operations in tests
 * @param {number} ms - Milliseconds to wait
 * @returns {Promise} - Promise that resolves after the specified time
 */
export function wait(ms = 0) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Helper to create mock API responses
 * @param {any} data - Response data
 * @param {number} delay - Response delay in milliseconds
 * @returns {Promise} - Promise that resolves with the data after delay
 */
export function mockApiResponse(data, delay = 100) {
  return new Promise(resolve => {
    setTimeout(() => resolve(data), delay);
  });
}

/**
 * Helper to test component props migration from Svelte 4 to Svelte 5
 * Useful for testing components during migration
 * @param {object} oldProps - Props in Svelte 4 format
 * @returns {object} - Props in Svelte 5 format
 */
export function migrateProps(oldProps) {
  // This is a placeholder - actual implementation would depend on specific migration needs
  return oldProps;
}

/**
 * Helper to test event handler migration
 * @param {string} oldEvent - Old event name (e.g., 'on:click')
 * @returns {string} - New event name (e.g., 'onclick')
 */
export function migrateEventName(oldEvent) {
  if (oldEvent.startsWith('on:')) {
    return 'on' + oldEvent.slice(3);
  }
  return oldEvent;
}

/**
 * Create a mock for Svelte 5 $state
 * @param {any} initialValue - Initial state value
 * @returns {object} - Mock state object
 */
export function createMockState(initialValue) {
  let value = initialValue;
  return {
    get current() { return value; },
    set current(newValue) { value = newValue; },
  };
}

/**
 * Create a mock for Svelte 5 $derived
 * @param {Function} deriveFn - Function to derive value
 * @returns {object} - Mock derived object
 */
export function createMockDerived(deriveFn) {
  return {
    get current() { return deriveFn(); },
  };
}

/**
 * Helper to test component lifecycle
 * @param {import('svelte').Component} Component - Component to test
 * @param {object} props - Component props
 * @returns {object} - Object with lifecycle tracking methods
 */
export function trackComponentLifecycle(Component, props = {}) {
  const lifecycle = {
    mounted: false,
    destroyed: false,
    updates: 0,
  };

  const { unmount, rerender, ...rest } = render(Component, { props });

  lifecycle.mounted = true;

  return {
    ...rest,
    lifecycle,
    unmount: () => {
      unmount();
      lifecycle.destroyed = true;
    },
    rerender: (newProps) => {
      lifecycle.updates++;
      return rerender(newProps);
    },
  };
}

// Re-export commonly used testing utilities
export { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/svelte';
export { userEvent } from '@testing-library/user-event';
export { vi, expect, describe, it, beforeEach, afterEach } from 'vitest';