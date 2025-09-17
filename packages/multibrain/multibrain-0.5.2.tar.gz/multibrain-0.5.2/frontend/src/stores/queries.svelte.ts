import { debugStore, debugInspect } from './debug.svelte';
import { createUndoRedoStore } from '../lib/undoRedo.svelte';
import type { QueryStore, Query, QueryResponse } from '../types';

const MAX_HISTORY = 100;

/**
 * Create a store for managing query history
 */
function createQueryStore(): QueryStore {
  // Use $state.raw for query history array to avoid deep reactivity overhead
  // This is more performant for large arrays that don't need deep mutation tracking
  let queries = $state.raw<Query[]>([]);
  let currentQuery = $state<Query | null>(null);
  
  // Create undo/redo system for query text
  const queryUndoRedo = createUndoRedoStore('', {
    maxHistory: 20,
    debounce: true,
    debounceDelay: 500
  });

  // Debug inspection - removed $effect as it can't be used in stores

  return {
    // Getters for reactive access
    get queries(): Query[] { return queries; },
    get currentQuery(): Query | null { return currentQuery; },
    
    // Undo/redo getters
    get queryText(): string { return queryUndoRedo.current; },
    get canUndo(): boolean { return queryUndoRedo.canUndo; },
    get canRedo(): boolean { return queryUndoRedo.canRedo; },
    
    // Add a new query to history
    addQuery(query: string): Query {
      const newQuery: Query = {
        id: crypto.randomUUID(),
        text: query,
        timestamp: new Date().toISOString(),
        responses: [],
        // Conversation support
        conversationId: crypto.randomUUID(),
        parentId: null,
        summaryContent: null,
        followUps: [],
        depth: 0
      };
      
      // With $state.raw, we must create a new array for updates
      queries = [newQuery, ...queries].slice(0, MAX_HISTORY);
      currentQuery = newQuery;
      
      // Add to undo/redo history
      queryUndoRedo.set(query);
      
      return newQuery;
    },
    
    // Add a follow-up query
    addFollowUpQuery(query: string, parentId: string, summaryContent: string): Query {
      const parentQuery = this.getQueryById(parentId);
      if (!parentQuery) {
        throw new Error('Parent query not found');
      }
      
      const newQuery: Query = {
        id: crypto.randomUUID(),
        text: query,
        timestamp: new Date().toISOString(),
        responses: [],
        // Conversation support
        conversationId: parentQuery.conversationId,
        parentId: parentId,
        summaryContent: null, // Will be set when this query completes
        followUps: [],
        depth: parentQuery.depth + 1
      };
      
      // Update parent query to include this follow-up
      queries = queries.map(q =>
        q.id === parentId
          ? { ...q, followUps: [...q.followUps, newQuery.id] }
          : q
      );
      
      // Add new query to the list
      queries = [newQuery, ...queries].slice(0, MAX_HISTORY);
      currentQuery = newQuery;
      
      // Add to undo/redo history
      queryUndoRedo.set(query);
      
      return newQuery;
    },
    
    // Update a query with response data
    updateQuery(queryId: string, updates: Partial<Query>): void {
      // With $state.raw, create a new array with updated items
      queries = queries.map(q =>
        q.id === queryId ? { ...q, ...updates } : q
      );
    },
    
    // Add a response to a query
    addResponse(queryId: string, response: QueryResponse): void {
      // With $state.raw, create a new array with updated items
      queries = queries.map(q =>
        q.id === queryId
          ? { ...q, responses: [...q.responses, response] }
          : q
      );
    },
    
    // Clear query history
    clearHistory(): void {
      // With $state.raw, assign a new empty array
      queries = [];
      currentQuery = null;
    },
    
    // Remove a specific query
    removeQuery(queryId: string): void {
      // With $state.raw, create a new filtered array
      queries = queries.filter(q => q.id !== queryId);
      if (currentQuery?.id === queryId) {
        currentQuery = null;
      }
    },
    
    // Undo/redo methods
    updateQueryText(text: string): void {
      queryUndoRedo.set(text);
    },
    
    undoQueryText(): void {
      queryUndoRedo.undo();
    },
    
    redoQueryText(): void {
      queryUndoRedo.redo();
    },
    
    // Get query by ID
    getQueryById(queryId: string): Query | undefined {
      return queries.find(q => q.id === queryId);
    },
    
    // Restore a previous query
    restoreQuery(queryId: string): string | null {
      const query = this.getQueryById(queryId);
      if (query) {
        queryUndoRedo.set(query.text);
        return query.text;
      }
      return null;
    }
  };
}

/**
 * Global query store instance
 */
export const queryStore: QueryStore = createQueryStore();