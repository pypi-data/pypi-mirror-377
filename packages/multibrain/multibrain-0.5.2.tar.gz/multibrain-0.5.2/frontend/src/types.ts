/**
 * Type definitions for MultiBrain application
 * This file contains all public APIs and types used throughout the application
 */

import type { Snippet } from 'svelte';

// ============================================================================
// Store Types
// ============================================================================

export interface LLMConfig {
  id: string;
  name: string;
  url: string;
  model: string;
  apiKey?: string;
  enabled: boolean;
  order: number;
  _optimistic?: boolean;
}

export interface Settings {
  maxConcurrent: number;
  streamTimeout: number;
  retryAttempts: number;
}

export interface ConfigStore {
  llms: LLMConfig[];
  summaryLLM: LLMConfig | null;
  settings: Settings;
  hasPendingUpdates: boolean;
  pendingUpdates: OptimisticUpdate[];
  load(): Promise<void>;
  addLLM(llm: Omit<LLMConfig, 'id' | 'order'>): Promise<void>;
  updateLLM(id: string, updates: Partial<LLMConfig>): Promise<void>;
  removeLLM(id: string): Promise<void>;
  setSummaryLLM(llm: LLMConfig | null): Promise<void>;
  updateSettings(newSettings: Partial<Settings>): Promise<void>;
  saveToLocalStorage(): void;
  loadFromLocalStorage(): Promise<void>;
}

export interface QueryResponse {
  llmId: string;
  llmName: string;
  content: string;
  status: string;
  error?: string;
}

export interface Query {
  id: string;
  text: string;
  timestamp: string;
  responses: QueryResponse[];
  // Conversation support
  conversationId: string;
  parentId: string | null;
  summaryContent: string | null;
  followUps: string[];
  depth: number;
}

export interface QueryStore {
  queries: Query[];
  currentQuery: Query | null;
  queryText: string;
  canUndo: boolean;
  canRedo: boolean;
  addQuery(query: string): Query;
  addFollowUpQuery(query: string, parentId: string, summaryContent: string): Query;
  updateQuery(queryId: string, updates: Partial<Query>): void;
  addResponse(queryId: string, response: QueryResponse): void;
  clearHistory(): void;
  removeQuery(queryId: string): void;
  updateQueryText(text: string): void;
  undoQueryText(): void;
  redoQueryText(): void;
  getQueryById(queryId: string): Query | undefined;
  restoreQuery(queryId: string): string | null;
}

export interface StreamMetrics {
  startTime: number;
  firstTokenTime: number | null;
  totalTime: number | null;
  tokensPerSecond: number | null;
}

export type StreamStatus = 'waiting' | 'streaming' | 'complete' | 'error' | 'aborted';

export interface Stream {
  id: string;
  llmId: string;
  llmName: string;
  model: string;
  content: string;
  status: StreamStatus;
  error: string | null;
  metrics: StreamMetrics;
}

export interface SummaryStream {
  id: 'summary';
  llmName: string;
  model: string;
  content: string;
  status: Exclude<StreamStatus, 'aborted'>;
  error: string | null;
  metrics: StreamMetrics;
}

export interface QueryStreamData {
  streams: Stream[];
  summary: SummaryStream | null;
  isStreaming: boolean;
  error: string | null;
  // Follow-up support
  context: string | null;
  isFollowUp: boolean;
}

export interface StreamStore {
  queries: Record<string, QueryStreamData>;
  isOnline: boolean;
  startStreaming(query: string, config: { llms: LLMConfig[]; summaryLLM: LLMConfig | null }, queryId: string): Promise<void>;
  startFollowUpStreaming(query: string, config: { llms: LLMConfig[]; summaryLLM: LLMConfig | null }, queryId: string, parentQueryId: string, context: string): Promise<void>;
  abortQuery(queryId: string): void;
  abortAll(): void;
  clearError(queryId: string): void;
  removeQuery(queryId: string): void;
}

export interface Conversation {
  id: string;
  rootQueryId: string;
  queryIds: string[];
  createdAt: string;
  lastUpdated: string;
}

export type ToastType = 'info' | 'success' | 'warning' | 'error';

export interface Toast {
  id: number;
  message: string;
  type: ToastType;
  duration: number;
}

export interface ToastStore {
  toasts: Toast[];
  show(message: string, type?: ToastType, duration?: number): number;
  info(message: string, duration?: number): number;
  success(message: string, duration?: number): number;
  warning(message: string, duration?: number): number;
  error(message: string, duration?: number): number;
  remove(id: number): void;
  clear(): void;
  destroy(): void;
}

export interface DebugMetrics {
  renderCount: number;
  storeUpdates: number;
  apiCalls: number;
  memoryUsage: number;
}

export interface DebugStore {
  enabled: boolean;
  showPanel: boolean;
  showInspector: boolean;
  logStoreUpdates: boolean;
  logApiCalls: boolean;
  metrics: DebugMetrics;
  stateHistory: any[];
  toggle(): void;
  togglePanel(): void;
  toggleInspector(): void;
  toggleStoreLogging(): void;
  toggleApiLogging(): void;
  reset(): void;
  updateMetric(key: keyof DebugMetrics, value: number): void;
  incrementMetric(key: keyof DebugMetrics): void;
  logStateChange(state: any): void;
  exportDebugData(): void;
  destroy(): void;
}

// ============================================================================
// Component Types
// ============================================================================

export interface ErrorBoundaryProps {
  error?: Error | null;
  reset?: () => void;
  onError?: (error: Error, info: any) => void;
  fallback?: boolean;
  children?: Snippet;
}

export interface QueryInputProps {
  disabled?: boolean;
  value?: string;
  placeholder?: string;
  onsubmit?: (query: string) => void;
}

export interface LLMFormData {
  name: string;
  url: string;
  model: string;
  apiKey: string;
  enabled: boolean;
}

// ============================================================================
// Utility Types
// ============================================================================

export interface StateConfig<T = any> {
  onEnter?: (context: T) => void;
  onExit?: (context: T) => void;
  transitions: Record<string, string | ((context: T) => string)>;
}

export interface StateMachine<T = any> {
  current: string;
  send(event: string, data?: any): boolean;
  can(state: string): boolean;
  subscribe(callback: (state: string) => void): () => void;
  reset(): void;
  getContext(): T;
  updateContext(updates: Partial<T>): void;
}

export interface UndoRedoOptions {
  maxHistory?: number;
  debounce?: boolean;
  debounceDelay?: number;
}

export interface UndoRedoSystem<T> {
  canUndo: boolean;
  canRedo: boolean;
  historySize: number;
  undo(): void;
  redo(): void;
  push(state: T): void;
  clear(): void;
  getCurrent(): T;
  subscribe(callback: (state: T) => void): () => void;
}

export interface OptimisticUpdate {
  id: string;
  type: 'create' | 'update' | 'delete';
  optimisticData: any;
  previousData: any;
  promise: Promise<any>;
  status: 'pending' | 'success' | 'error';
  error?: Error;
}

export interface ErrorContext {
  component: string;
  action: string;
  data?: any;
}

export interface ErrorLog {
  id: string;
  message: string;
  stack?: string;
  timestamp: string;
  level: 'error' | 'warning' | 'info';
  context?: ErrorContext;
  environment: any;
}

// ============================================================================
// API Types
// ============================================================================

export interface ValidationResult {
  success: boolean;
  message: string;
}

export interface StreamUpdate {
  type: string;
  streamId: string;
  content: string;
  status: string;
  error?: string;
  metrics?: StreamMetrics;
}

// ============================================================================
// Type Guards
// ============================================================================

export function isLLMConfig(value: any): value is LLMConfig {
  return value && 
    typeof value === 'object' &&
    typeof value.id === 'string' &&
    typeof value.name === 'string' &&
    typeof value.url === 'string' &&
    typeof value.model === 'string' &&
    typeof value.enabled === 'boolean';
}

export function isQuery(value: any): value is Query {
  return value &&
    typeof value === 'object' &&
    typeof value.id === 'string' &&
    typeof value.text === 'string' &&
    typeof value.timestamp === 'string' &&
    Array.isArray(value.responses);
}

export function isToast(value: any): value is Toast {
  return value &&
    typeof value === 'object' &&
    typeof value.id === 'number' &&
    typeof value.message === 'string' &&
    ['info', 'success', 'warning', 'error'].includes(value.type);
}

// ============================================================================
// State Machine Types
// ============================================================================

export type QueryState = 'idle' | 'preparing' | 'streaming' | 'summarizing' | 'complete' | 'error' | 'aborted' | 'viewing';

export interface QueryContext {
  queryId: string | null;
  query: string;
  error: string | null;
  retryCount: number;
}

export interface QueryStateMachine extends StateMachine<QueryContext> {
  current: QueryState;
}

// ============================================================================
// Library Types
// ============================================================================

export interface StorageAPI {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
  clear(): void;
}

export interface OptimisticUpdateManager {
  create<T>(data: T, operation: (data: T) => Promise<T>, options?: { onError?: (error: Error) => void }): Promise<void>;
  update<T>(data: T, operation: () => Promise<T>, options?: { onError?: (error: Error) => void }): Promise<void>;
  delete<T>(data: T, operation: () => Promise<any>, options?: { onError?: (error: Error) => void }): Promise<void>;
  subscribe(callback: (update: OptimisticUpdate, allUpdates: OptimisticUpdate[]) => void): () => void;
}