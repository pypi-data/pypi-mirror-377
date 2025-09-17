import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import App from '../../App.svelte';

// Mock the API module
vi.mock('../../lib/api.js', () => ({
  validateLLMConfig: vi.fn().mockResolvedValue({ success: true, message: 'Valid configuration' })
}));

// Mock the streaming module
vi.mock('../../lib/streaming.js', () => ({
  streamMultipleQueries: vi.fn().mockImplementation(({ onUpdate }) => {
    // Simulate streaming responses
    setTimeout(() => {
      onUpdate({
        streamId: 'llm1',
        content: 'Hello from LLM 1',
        status: 'streaming',
        llm: { name: 'Test LLM 1', model: 'test-model-1' }
      });
    }, 100);
    
    setTimeout(() => {
      onUpdate({
        streamId: 'llm1',
        content: 'Hello from LLM 1. This is a test response.',
        status: 'complete',
        llm: { name: 'Test LLM 1', model: 'test-model-1' }
      });
    }, 200);
    
    return Promise.resolve();
  })
}));

describe('Main Application Flow', () => {
  let user;
  
  beforeEach(() => {
    user = userEvent.setup();
    // Clear localStorage before each test
    localStorage.clear();
    // Set welcome as seen to skip welcome guide
    localStorage.setItem('multibrain_welcome_seen', 'true');
  });

  it('should render the main application', async () => {
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByText('MultiBrain')).toBeInTheDocument();
    });
    
    // Check main elements
    expect(screen.getByText('Query multiple AI models simultaneously')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask a question to multiple LLMs...')).toBeInTheDocument();
    expect(screen.getByText('Configure LLMs')).toBeInTheDocument();
  });

  it('should handle the query input flow', async () => {
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Ask a question to multiple LLMs...')).toBeInTheDocument();
    });
    
    // Get the input field
    const input = screen.getByPlaceholderText('Ask a question to multiple LLMs...');
    
    // Type a query
    await user.type(input, 'What is Svelte 5?');
    
    // Verify the input value
    expect(input).toHaveValue('What is Svelte 5?');
    
    // The submit button should be enabled
    const submitButton = screen.getByRole('button', { name: /send query/i });
    expect(submitButton).not.toBeDisabled();
  });

  it('should show configuration modal when clicking Configure LLMs', async () => {
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByText('Configure LLMs')).toBeInTheDocument();
    });
    
    // Click the configure button
    const configButton = screen.getByText('Configure LLMs');
    await user.click(configButton);
    
    // Modal should appear
    await waitFor(() => {
      expect(screen.getByText('LLM Configuration')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Response LLMs')).toBeInTheDocument();
    expect(screen.getByText('Summary LLM')).toBeInTheDocument();
  });

  it('should handle keyboard shortcuts', async () => {
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Ask a question to multiple LLMs...')).toBeInTheDocument();
    });
    
    // Test Ctrl+K to focus input
    await user.keyboard('{Control>}k{/Control}');
    
    // Input should be focused
    const input = screen.getByPlaceholderText('Ask a question to multiple LLMs...');
    expect(document.activeElement).toBe(input);
  });

  it('should show warning when trying to query without configured LLMs', async () => {
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Ask a question to multiple LLMs...')).toBeInTheDocument();
    });
    
    // Type a query
    const input = screen.getByPlaceholderText('Ask a question to multiple LLMs...');
    await user.type(input, 'Test query');
    
    // Submit the query
    await user.keyboard('{Enter}');
    
    // Should show warning toast
    await waitFor(() => {
      expect(screen.getByText(/Please configure at least one LLM/i)).toBeInTheDocument();
    });
  });

  it('should handle the complete LLM configuration flow', async () => {
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByText('Configure LLMs')).toBeInTheDocument();
    });
    
    // Open configuration
    await user.click(screen.getByText('Configure LLMs'));
    
    // Wait for modal
    await waitFor(() => {
      expect(screen.getByText('Add LLM')).toBeInTheDocument();
    });
    
    // Click Add LLM
    await user.click(screen.getByText('Add LLM'));
    
    // LLM form should appear
    await waitFor(() => {
      expect(screen.getByText('LLM Provider')).toBeInTheDocument();
    });
    
    // Fill in the form
    const nameInput = screen.getByPlaceholderText(/GPT-4 Production/i);
    await user.type(nameInput, 'Test LLM');
    
    const urlInput = screen.getByPlaceholderText(/https:\/\/api\.openai\.com\/v1/i);
    await user.clear(urlInput);
    await user.type(urlInput, 'https://api.test.com/v1');
    
    const modelInput = screen.getByPlaceholderText(/gpt-4/i);
    await user.type(modelInput, 'test-model');
    
    const apiKeyInput = screen.getByPlaceholderText(/sk-\.\.\./i);
    await user.type(apiKeyInput, 'test-api-key');
    
    // Test connection button should be enabled
    const testButton = screen.getByText('Test Connection');
    expect(testButton).not.toBeDisabled();
  });

  it('should handle responsive design', async () => {
    // Set mobile viewport
    global.innerWidth = 375;
    global.innerHeight = 667;
    global.dispatchEvent(new Event('resize'));
    
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByText('MultiBrain')).toBeInTheDocument();
    });
    
    // Mobile layout should still show main elements
    expect(screen.getByPlaceholderText('Ask a question to multiple LLMs...')).toBeInTheDocument();
    expect(screen.getByText('Configure LLMs')).toBeInTheDocument();
  });

  it('should persist and load configuration', async () => {
    // Set up some configuration in localStorage
    const mockConfig = {
      llms: [
        {
          id: 'test-llm-1',
          name: 'Test LLM 1',
          url: 'https://api.test.com/v1',
          model: 'test-model',
          apiKey: 'test-key',
          enabled: true,
          order: 0
        }
      ],
      summaryLLM: null,
      settings: {
        maxConcurrent: 100,
        streamTimeout: 300000,
        retryAttempts: 3
      }
    };
    
    localStorage.setItem('multibrain_v2', JSON.stringify(mockConfig));
    
    render(App);
    
    // Wait for initialization
    await waitFor(() => {
      expect(screen.getByText('MultiBrain')).toBeInTheDocument();
    });
    
    // Should show LLM count
    await waitFor(() => {
      expect(screen.getByText('1 of 1 LLMs active')).toBeInTheDocument();
    });
  });

  it('should handle error states gracefully', async () => {
    // Mock console.error to avoid test output noise
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    // Mock localStorage to throw an error
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem');
    getItemSpy.mockImplementation(() => {
      throw new Error('Storage error');
    });
    
    render(App);
    
    // App should still render despite storage error
    await waitFor(() => {
      expect(screen.getByText('MultiBrain')).toBeInTheDocument();
    });
    
    // Restore mocks
    consoleSpy.mockRestore();
    getItemSpy.mockRestore();
  });
});