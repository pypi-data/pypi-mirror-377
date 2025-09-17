import { debugStore, debugInspect } from './debug.svelte';
import type { ToastStore, Toast, ToastType } from '../types';

/**
 * Create a store for managing toast notifications
 */
function createToastStore(): ToastStore {
  // State using $state rune
  let toasts = $state<Toast[]>([]);
  let nextId = 1;
  
  // Map to track active timeouts
  const timeouts = new Map<number, number>();
  
  // Debug inspection - removed $effect as it can't be used in stores
  
  // Function to cleanup all timeouts
  function cleanupTimeouts(): void {
    timeouts.forEach(timeout => clearTimeout(timeout));
    timeouts.clear();
  }
  
  return {
    // Getter for reactive access
    get toasts(): Toast[] { return toasts; },
    
    show(message: string, type: ToastType = 'info', duration: number = 3000): number {
      const id = nextId++;
      const toast: Toast = { id, message, type, duration };
      
      toasts = [...toasts, toast];
      
      if (duration > 0) {
        const timeout = window.setTimeout(() => {
          this.remove(id);
        }, duration);
        timeouts.set(id, timeout);
      }
      
      return id;
    },
    
    info(message: string, duration?: number): number {
      return this.show(message, 'info', duration);
    },
    
    success(message: string, duration?: number): number {
      return this.show(message, 'success', duration);
    },
    
    warning(message: string, duration?: number): number {
      return this.show(message, 'warning', duration);
    },
    
    error(message: string, duration?: number): number {
      return this.show(message, 'error', duration);
    },
    
    remove(id: number): void {
      toasts = toasts.filter(t => t.id !== id);
      
      // Clear timeout if exists
      const timeout = timeouts.get(id);
      if (timeout) {
        clearTimeout(timeout);
        timeouts.delete(id);
      }
    },
    
    clear(): void {
      toasts = [];
      
      // Clear all timeouts
      cleanupTimeouts();
    },
    
    // Cleanup method to be called when store is destroyed
    destroy(): void {
      cleanupTimeouts();
    }
  };
}

/**
 * Global toast store instance
 */
export const toastStore: ToastStore = createToastStore();