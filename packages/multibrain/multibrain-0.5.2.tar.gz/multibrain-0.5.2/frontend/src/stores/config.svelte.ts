import { loadFromStorage, saveToStorage } from '../lib/storage';
import { debugStore, debugInspect } from './debug.svelte';
import { createOptimisticUpdateManager } from '../lib/optimisticUpdate.svelte';
import type { ConfigStore, LLMConfig, Settings, OptimisticUpdate } from '../types';

const STORAGE_KEY = 'multibrain_v2';

/**
 * Create the config store using runes
 */
function createConfigStore(): ConfigStore {
  // State using $state rune
  let llms = $state<LLMConfig[]>([]);
  let summaryLLM = $state<LLMConfig | null>(null);
  let settings = $state<Settings>({
    maxConcurrent: 100,
    streamTimeout: 300000,
    retryAttempts: 3
  });
  
  // Optimistic update manager
  const optimisticManager = createOptimisticUpdateManager();
  let pendingUpdates = $state<OptimisticUpdate[]>([]);
  
  // Subscribe to optimistic updates
  optimisticManager.subscribe((update, allUpdates) => {
    pendingUpdates = allUpdates;
  });

  // Debug inspection - removed $effect as it can't be used in stores
  
  // Function to save state to localStorage
  let previousConfigHash = '';
  
  function saveToLocalStorage(): void {
    // Create a snapshot of the current state
    const config = {
      llms,
      summaryLLM,
      settings
    };
    
    // Only save if we have actual data (not initial empty state)
    if (llms.length > 0 || summaryLLM !== null) {
      // Create a simple hash to detect changes
      const configHash = JSON.stringify({
        llmCount: llms.length,
        llmIds: llms.map(l => l.id).sort(),
        summaryId: summaryLLM?.id,
        settings
      });
      
      // Only save if configuration actually changed
      if (configHash !== previousConfigHash) {
        console.log('[ConfigStore] Auto-saving state:', config);
        console.log('[ConfigStore] LLMs being saved:', llms.map(l => ({
          id: l.id,
          name: l.name,
          url: l.url,
          model: l.model,
          hasApiKey: !!l.apiKey,
          enabled: l.enabled
        })));
        saveToStorage(STORAGE_KEY, config);
        previousConfigHash = configHash;
      }
    }
  }

  return {
    // Getters for reactive access
    get llms(): LLMConfig[] { return llms; },
    get summaryLLM(): LLMConfig | null { return summaryLLM; },
    get settings(): Settings { return settings; },
    
    // Load configuration from localStorage
    async load(): Promise<void> {
      console.log('[ConfigStore] Loading configuration...');
      try {
        const stored = await loadFromStorage(STORAGE_KEY);
        if (stored) {
          console.log('[ConfigStore] Loaded config:', stored);
          if (stored.llms) llms = stored.llms;
          if (stored.summaryLLM !== undefined) summaryLLM = stored.summaryLLM;
          if (stored.settings) settings = { ...settings, ...stored.settings };
        } else {
          console.log('[ConfigStore] No stored config found');
        }
      } catch (error) {
        console.error('[ConfigStore] Error loading config:', error);
      }
    },
    
    // Getters for optimistic state
    get hasPendingUpdates(): boolean { return pendingUpdates.length > 0; },
    get pendingUpdates(): OptimisticUpdate[] { return pendingUpdates; },
    
    // Add a new LLM with optimistic update
    async addLLM(llm: Omit<LLMConfig, 'id' | 'order'>): Promise<void> {
      // Ensure all required fields are present
      const newLLM: LLMConfig = {
        id: crypto.randomUUID(),
        order: llms.length,
        name: llm.name,
        url: llm.url,
        model: llm.model,
        apiKey: llm.apiKey,
        enabled: llm.enabled ?? true,
        _optimistic: true
      };
      
      // Apply optimistic update immediately
      llms = [...llms, newLLM];
      console.log('[ConfigStore] Optimistically added LLM:', newLLM);
      
      // Simulate async validation/save
      return optimisticManager.create(newLLM, async (optimisticLLM) => {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Remove optimistic flag and ensure all fields are preserved
        const finalLLM: LLMConfig = {
          id: optimisticLLM.id,
          order: optimisticLLM.order,
          name: optimisticLLM.name,
          url: optimisticLLM.url,
          model: optimisticLLM.model,
          apiKey: optimisticLLM.apiKey,
          enabled: optimisticLLM.enabled
        };
        
        // Update with final data
        llms = llms.map(l => l.id === optimisticLLM.id ? finalLLM : l);
        
        // Save after successful add
        saveToLocalStorage();
        
        return finalLLM;
      }, {
        onError: (error) => {
          // Rollback on error
          llms = llms.filter(l => l.id !== newLLM.id);
          console.error('[ConfigStore] Failed to add LLM:', error);
        }
      });
    },
    
    // Update an existing LLM with optimistic update
    async updateLLM(id: string, updates: Partial<LLMConfig>): Promise<void> {
      const currentLLM = llms.find(l => l.id === id);
      if (!currentLLM) throw new Error('LLM not found');
      
      // Apply optimistic update immediately, ensuring all fields are preserved
      const optimisticLLM: LLMConfig = {
        id: currentLLM.id,
        order: currentLLM.order,
        name: updates.name ?? currentLLM.name,
        url: updates.url ?? currentLLM.url,
        model: updates.model ?? currentLLM.model,
        apiKey: updates.apiKey ?? currentLLM.apiKey,
        enabled: updates.enabled ?? currentLLM.enabled,
        _optimistic: true
      };
      
      llms = llms.map(llm =>
        llm.id === id ? optimisticLLM : llm
      );
      
      // Also update summaryLLM if it's the one being updated
      if (summaryLLM?.id === id) {
        summaryLLM = optimisticLLM;
      }
      
      console.log('[ConfigStore] Optimistically updated LLM:', id, updates);
      console.log('[ConfigStore] Updated LLM data:', optimisticLLM);
      
      // Execute async update
      return optimisticManager.update(optimisticLLM, async () => {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Create final LLM without optimistic flag
        const finalLLM: LLMConfig = {
          id: optimisticLLM.id,
          order: optimisticLLM.order,
          name: optimisticLLM.name,
          url: optimisticLLM.url,
          model: optimisticLLM.model,
          apiKey: optimisticLLM.apiKey,
          enabled: optimisticLLM.enabled
        };
        
        // Update with final data
        llms = llms.map(l => l.id === id ? finalLLM : l);
        if (summaryLLM?.id === id) {
          summaryLLM = finalLLM;
        }
        
        // Save after successful update
        saveToLocalStorage();
        
        return finalLLM;
      }, {
        onError: (error) => {
          // Rollback on error
          llms = llms.map(l => l.id === id ? currentLLM : l);
          if (summaryLLM?.id === id) {
            summaryLLM = currentLLM;
          }
          console.error('[ConfigStore] Failed to update LLM:', error);
        }
      });
    },
    
    // Remove an LLM with optimistic update
    async removeLLM(id: string): Promise<void> {
      const currentLLM = llms.find(l => l.id === id);
      if (!currentLLM) return;
      
      const wasSummaryLLM = summaryLLM?.id === id;
      
      // Apply optimistic removal immediately
      llms = llms.filter(llm => llm.id !== id);
      
      // Clear summaryLLM if it's the one being removed
      if (wasSummaryLLM) {
        summaryLLM = null;
      }
      
      console.log('[ConfigStore] Optimistically removed LLM:', id);
      
      // Execute async removal
      return optimisticManager.delete(currentLLM, async () => {
        // In a real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Save after successful removal
        saveToLocalStorage();
        
        return id;
      }, {
        onError: (error) => {
          // Rollback on error
          llms = [...llms, currentLLM].sort((a, b) => a.order - b.order);
          if (wasSummaryLLM) {
            summaryLLM = currentLLM;
          }
          console.error('[ConfigStore] Failed to remove LLM:', error);
        }
      });
    },
    
    // Set the summary LLM
    async setSummaryLLM(llm: LLMConfig | null): Promise<void> {
      summaryLLM = llm;
      console.log('[ConfigStore] Set summary LLM:', llm);
      saveToLocalStorage();
    },
    
    // Update settings
    async updateSettings(newSettings: Partial<Settings>): Promise<void> {
      settings = { ...settings, ...newSettings };
      console.log('[ConfigStore] Updated settings:', newSettings);
      saveToLocalStorage();
    },
    
    // Expose save function for manual saves
    saveToLocalStorage,
    
    // Load from localStorage (for recovery)
    loadFromLocalStorage(): Promise<void> {
      return this.load();
    }
  };
}

// Create the store instance
export const configStore: ConfigStore = createConfigStore();

/**
 * Get only the enabled LLMs from the configuration
 */
export function getEnabledLLMs(): LLMConfig[] {
  return configStore.llms.filter(llm => llm.enabled);
}

/**
 * Helper function to load config on app start
 */
export async function loadConfig(): Promise<void> {
  await configStore.load();
}