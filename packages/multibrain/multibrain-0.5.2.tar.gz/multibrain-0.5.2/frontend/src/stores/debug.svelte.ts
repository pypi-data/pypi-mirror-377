/**
 * Debug store for development tools and debugging features
 */

import type { DebugStore, DebugMetrics } from '../types';

/**
 * Create the debug store
 */
function createDebugStore(): DebugStore {
  // Check if debug mode should be enabled by default
  const urlParams = new URLSearchParams(window.location.search);
  const debugParam = urlParams.get('debug') === 'true';
  const storedDebug = localStorage.getItem('multibrain_debug') === 'true';
  
  // State
  let enabled = $state(import.meta.env.DEV && (debugParam || storedDebug));
  let showPanel = $state(false);
  let showInspector = $state(true);
  let logStoreUpdates = $state(true);
  let logApiCalls = $state(true);
  let metrics = $state<DebugMetrics>({
    renderCount: 0,
    storeUpdates: 0,
    apiCalls: 0,
    memoryUsage: 0
  });
  let stateHistory = $state<any[]>([]);
  const MAX_HISTORY = 100;
  
  // Update memory usage periodically
  let memoryInterval: number | undefined;
  
  function startMemoryMonitoring(): void {
    if ((performance as any).memory && !memoryInterval) {
      memoryInterval = window.setInterval(() => {
        metrics.memoryUsage = Math.round((performance as any).memory.usedJSHeapSize / 1048576);
      }, 1000);
    }
  }
  
  function stopMemoryMonitoring(): void {
    if (memoryInterval) {
      clearInterval(memoryInterval);
      memoryInterval = undefined;
    }
  }
  
  // Set up keyboard shortcut for debug panel
  let keyHandler: ((e: KeyboardEvent) => void) | null = null;
  function setupKeyboardShortcut(): void {
    if (!enabled) return;
    
    keyHandler = (e: KeyboardEvent) => {
      // Ctrl/Cmd + Shift + D to toggle debug panel
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
        e.preventDefault();
        showPanel = !showPanel;
      }
    };
    
    window.addEventListener('keydown', keyHandler);
  }
  
  // Initialize immediately if enabled
  if (enabled) {
    setupKeyboardShortcut();
    startMemoryMonitoring();
  }
  
  const store: DebugStore = {
    // Getters
    get enabled(): boolean { return enabled; },
    get showPanel(): boolean { return showPanel; },
    get showInspector(): boolean { return showInspector; },
    get logStoreUpdates(): boolean { return logStoreUpdates; },
    get logApiCalls(): boolean { return logApiCalls; },
    get metrics(): DebugMetrics { return metrics; },
    get stateHistory(): any[] { return stateHistory; },
    
    // Methods
    toggle(): void {
      enabled = !enabled;
      localStorage.setItem('multibrain_debug', enabled.toString());
      
      if (enabled) {
        setupKeyboardShortcut();
        startMemoryMonitoring();
      } else {
        showPanel = false;
        if (keyHandler) {
          window.removeEventListener('keydown', keyHandler);
          keyHandler = null;
        }
        stopMemoryMonitoring();
      }
    },
    
    togglePanel(): void {
      showPanel = !showPanel;
    },
    
    toggleInspector(): void {
      showInspector = !showInspector;
    },
    
    toggleStoreLogging(): void {
      logStoreUpdates = !logStoreUpdates;
    },
    
    toggleApiLogging(): void {
      logApiCalls = !logApiCalls;
    },
    
    reset(): void {
      metrics = {
        renderCount: 0,
        storeUpdates: 0,
        apiCalls: 0,
        memoryUsage: 0
      };
      stateHistory = [];
    },
    
    updateMetric(key: keyof DebugMetrics, value: number): void {
      if (key in metrics) {
        metrics[key] = value;
      }
    },
    
    incrementMetric(key: keyof DebugMetrics): void {
      if (key in metrics && typeof metrics[key] === 'number') {
        metrics[key]++;
      }
    },
    
    logStateChange(state: any): void {
      if (!enabled || !showInspector) return;
      
      const entry = {
        timestamp: new Date().toISOString(),
        state: structuredClone(state),
        id: crypto.randomUUID()
      };
      
      stateHistory = [entry, ...stateHistory].slice(0, MAX_HISTORY);
    },
    
    exportDebugData(): void {
      const data = {
        timestamp: new Date().toISOString(),
        metrics,
        stateHistory,
        environment: {
          userAgent: navigator.userAgent,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight
          },
          memory: (performance as any).memory ? {
            used: Math.round((performance as any).memory.usedJSHeapSize / 1048576),
            total: Math.round((performance as any).memory.totalJSHeapSize / 1048576),
            limit: Math.round((performance as any).memory.jsHeapSizeLimit / 1048576)
          } : null
        }
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `multibrain-debug-${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    },
    
    // Cleanup method
    destroy(): void {
      stopMemoryMonitoring();
      if (keyHandler) {
        window.removeEventListener('keydown', keyHandler);
      }
    }
  };
  
  return store;
}

// Create singleton instance
export const debugStore: DebugStore = createDebugStore();

/**
 * Helper to create debug-aware logging
 * Note: $inspect can only be used inside components, so we use console.log instead
 */
export function debugInspect<T>(value: T, label?: string): T {
  if (debugStore.enabled && debugStore.showInspector) {
    if (label) {
      console.log(`[${label}] Value:`, value);
    } else {
      console.log('Value:', value);
    }
    debugStore.incrementMetric('storeUpdates');
  }
  return value;
}