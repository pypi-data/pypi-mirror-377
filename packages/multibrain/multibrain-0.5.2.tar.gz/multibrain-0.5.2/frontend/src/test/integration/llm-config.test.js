import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import ConfigModal from '../../components/ConfigModal.svelte';
import LLMConfigForm from '../../components/LLMConfigForm.svelte';
import { configStore } from '../../stores/config.svelte.js';

describe('LLM Configuration Integration Tests', () => {
  beforeEach(() => {
    // Reset config store before each test
    configStore.llms.length = 0;
    configStore.summaryLLM = null;
    localStorage.clear();
  });

  describe('ConfigModal Integration', () => {
    it('should open and close the configuration modal', async () => {
      const onclose = vi.fn();
      render(ConfigModal, { props: { onclose } });

      // Modal should be visible
      expect(screen.getByText('LLM Configuration')).toBeInTheDocument();

      // Close button should work
      const closeButton = screen.getAllByRole('button').find(btn => 
        btn.querySelector('svg path[d*="M6 18L18 6M6 6l12 12"]')
      );
      await fireEvent.click(closeButton);
      expect(onclose).toHaveBeenCalled();
    });

    it('should show empty state when no LLMs configured', () => {
      render(ConfigModal, { props: { onclose: vi.fn() } });
      
      expect(screen.getByText('No LLMs configured yet')).toBeInTheDocument();
      expect(screen.getByText('Add your first LLM to get started')).toBeInTheDocument();
    });

    it('should toggle add LLM form', async () => {
      render(ConfigModal, { props: { onclose: vi.fn() } });
      
      // Form should not be visible initially
      expect(screen.queryByText('LLM Provider')).not.toBeInTheDocument();
      
      // Click add button
      const addButton = screen.getByText('Add LLM');
      await fireEvent.click(addButton);
      
      // Form should now be visible
      expect(screen.getByText('LLM Provider')).toBeInTheDocument();
    });
  });

  describe('LLMConfigForm Integration', () => {
    it('should add a new LLM with OpenAI preset', async () => {
      const user = userEvent.setup();
      const oncancel = vi.fn();
      const onsave = vi.fn();
      
      render(LLMConfigForm, { props: { oncancel, onsave } });
      
      // Select OpenAI preset
      const providerSelect = screen.getByRole('combobox');
      await user.selectOptions(providerSelect, 'OpenAI');
      
      // Check preset values are applied
      expect(screen.getByDisplayValue('https://api.openai.com/v1/chat/completions')).toBeInTheDocument();
      expect(screen.getByDisplayValue('gpt-4')).toBeInTheDocument();
      
      // Fill in remaining fields
      await user.type(screen.getByPlaceholderText('Enter display name'), 'My OpenAI');
      await user.type(screen.getByPlaceholderText('Enter API key'), 'sk-test-key');
      
      // Save the form
      const saveButton = screen.getByText('Add LLM');
      await fireEvent.click(saveButton);
      
      // Check that save was called
      expect(onsave).toHaveBeenCalled();
      
      // Verify LLM was added to store
      expect(configStore.llms).toHaveLength(1);
      expect(configStore.llms[0].name).toBe('My OpenAI');
      expect(configStore.llms[0].model).toBe('gpt-4');
    });

    it('should validate required fields', async () => {
      const user = userEvent.setup();
      render(LLMConfigForm, { props: { oncancel: vi.fn(), onsave: vi.fn() } });
      
      // Try to save without filling required fields
      const saveButton = screen.getByText('Add LLM');
      expect(saveButton).toBeDisabled();
      
      // Fill in some fields
      await user.type(screen.getByPlaceholderText('Enter display name'), 'Test LLM');
      expect(saveButton).toBeDisabled(); // Still disabled
      
      // Fill all required fields
      await user.type(screen.getByPlaceholderText('Enter API URL'), 'https://api.test.com');
      await user.type(screen.getByPlaceholderText('Enter model name'), 'test-model');
      await user.type(screen.getByPlaceholderText('Enter API key'), 'test-key');
      
      expect(saveButton).not.toBeDisabled();
    });

    it('should test LLM connection', async () => {
      const user = userEvent.setup();
      
      // Mock fetch for testing
      global.fetch = vi.fn(() => 
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ choices: [{ message: { content: 'Test successful' } }] })
        })
      );
      
      render(LLMConfigForm, { props: { oncancel: vi.fn(), onsave: vi.fn() } });
      
      // Fill in all fields
      await user.type(screen.getByPlaceholderText('Enter display name'), 'Test LLM');
      await user.type(screen.getByPlaceholderText('Enter API URL'), 'https://api.test.com');
      await user.type(screen.getByPlaceholderText('Enter model name'), 'test-model');
      await user.type(screen.getByPlaceholderText('Enter API key'), 'test-key');
      
      // Click test button
      const testButton = screen.getByText('Test Connection');
      await fireEvent.click(testButton);
      
      // Should show testing state
      expect(screen.getByText('Testing...')).toBeInTheDocument();
      
      // Wait for test to complete
      await waitFor(() => {
        expect(screen.getByText('✓ Connection successful!')).toBeInTheDocument();
      });
    });
  });

  describe('Full Configuration Flow', () => {
    it('should complete full LLM configuration flow', async () => {
      const user = userEvent.setup();
      const onclose = vi.fn();
      
      render(ConfigModal, { props: { onclose } });
      
      // 1. Open add form
      await fireEvent.click(screen.getByText('Add LLM'));
      
      // 2. Fill in LLM details
      await user.selectOptions(screen.getByRole('combobox'), 'Anthropic');
      await user.type(screen.getByPlaceholderText('Enter display name'), 'Claude 3');
      await user.type(screen.getByPlaceholderText('Enter API key'), 'sk-ant-test');
      
      // 3. Save LLM
      await fireEvent.click(screen.getByText('Add LLM'));
      
      // 4. Verify LLM appears in list
      await waitFor(() => {
        expect(screen.getByText('Claude 3')).toBeInTheDocument();
        expect(screen.getByText('claude-3-opus-20240229')).toBeInTheDocument();
      });
      
      // 5. Set as summary LLM
      const summarySelect = screen.getByRole('combobox', { name: /select summary llm/i });
      await user.selectOptions(summarySelect, configStore.llms[0].id);
      
      // 6. Verify summary LLM is set
      expect(configStore.summaryLLM).toBeTruthy();
      expect(configStore.summaryLLM.name).toBe('Claude 3');
    });

    it('should edit existing LLM', async () => {
      const user = userEvent.setup();
      
      // Add an LLM first
      configStore.addLLM({
        name: 'Original Name',
        url: 'https://api.test.com',
        model: 'test-model',
        apiKey: 'test-key'
      });
      
      render(ConfigModal, { props: { onclose: vi.fn() } });
      
      // Click edit button
      const editButton = screen.getByRole('button', { name: /edit/i });
      await fireEvent.click(editButton);
      
      // Update name
      const nameInput = screen.getByDisplayValue('Original Name');
      await user.clear(nameInput);
      await user.type(nameInput, 'Updated Name');
      
      // Save changes
      await fireEvent.click(screen.getByText('Update LLM'));
      
      // Verify update
      await waitFor(() => {
        expect(screen.getByText('Updated Name')).toBeInTheDocument();
        expect(configStore.llms[0].name).toBe('Updated Name');
      });
    });

    it('should delete LLM', async () => {
      // Add an LLM first
      configStore.addLLM({
        name: 'To Delete',
        url: 'https://api.test.com',
        model: 'test-model',
        apiKey: 'test-key'
      });
      
      render(ConfigModal, { props: { onclose: vi.fn() } });
      
      expect(screen.getByText('To Delete')).toBeInTheDocument();
      
      // Click delete button
      const deleteButton = screen.getByRole('button', { name: /delete/i });
      
      // Mock window.confirm
      window.confirm = vi.fn(() => true);
      
      await fireEvent.click(deleteButton);
      
      // Verify deletion
      expect(screen.queryByText('To Delete')).not.toBeInTheDocument();
      expect(configStore.llms).toHaveLength(0);
    });
  });

  describe('Persistence', () => {
    it('should persist LLM configuration to localStorage', async () => {
      const user = userEvent.setup();
      
      render(ConfigModal, { props: { onclose: vi.fn() } });
      
      // Add an LLM
      await fireEvent.click(screen.getByText('Add LLM'));
      await user.type(screen.getByPlaceholderText('Enter display name'), 'Persistent LLM');
      await user.type(screen.getByPlaceholderText('Enter API URL'), 'https://api.test.com');
      await user.type(screen.getByPlaceholderText('Enter model name'), 'test-model');
      await user.type(screen.getByPlaceholderText('Enter API key'), 'test-key');
      await fireEvent.click(screen.getByText('Add LLM'));
      
      // Check localStorage
      const saved = JSON.parse(localStorage.getItem('multibrain-config'));
      expect(saved.llms).toHaveLength(1);
      expect(saved.llms[0].name).toBe('Persistent LLM');
    });
  });
});