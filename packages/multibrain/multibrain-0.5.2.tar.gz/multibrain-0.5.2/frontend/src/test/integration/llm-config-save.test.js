import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/svelte';
import { configStore } from '../../stores/config.svelte';
import ConfigModal from '../../components/ConfigModal.svelte';
import LLMConfigForm from '../../components/LLMConfigForm.svelte';

// Mock the API
vi.mock('../../lib/api', () => ({
  validateLLMConfig: vi.fn().mockResolvedValue({
    success: true,
    message: 'Connection successful'
  })
}));

describe('LLM Configuration Saving', () => {
  beforeEach(() => {
    // Reset the config store
    configStore.llms = [];
    configStore.summaryLLM = null;
  });

  it('should save new LLM configuration with all fields', async () => {
    const { getByLabelText, getByText, getByRole } = render(LLMConfigForm, {
      props: {
        onsave: (data) => {
          // Verify the data structure
          expect(data).toEqual({
            name: 'Test OpenAI',
            url: 'https://api.openai.com/v1',
            model: 'gpt-4',
            apiKey: 'test-api-key',
            enabled: true
          });
        }
      }
    });

    // Fill in the form
    const nameInput = getByLabelText(/display name/i);
    const urlInput = getByLabelText(/api url/i);
    const modelInput = getByLabelText(/model/i);
    const apiKeyInput = getByLabelText(/api key/i);

    await fireEvent.input(nameInput, { target: { value: 'Test OpenAI' } });
    await fireEvent.input(urlInput, { target: { value: 'https://api.openai.com/v1' } });
    await fireEvent.input(modelInput, { target: { value: 'gpt-4' } });
    await fireEvent.input(apiKeyInput, { target: { value: 'test-api-key' } });

    // Submit the form
    const submitButton = getByText(/add llm/i);
    await fireEvent.click(submitButton);
  });

  it('should properly handle preset selection when editing', async () => {
    const existingLLM = {
      id: '123',
      name: 'My OpenAI',
      url: 'https://api.openai.com/v1',
      model: 'gpt-4',
      apiKey: 'existing-key',
      enabled: true,
      order: 0
    };

    const { getByLabelText, getByDisplayValue } = render(LLMConfigForm, {
      props: {
        llm: existingLLM
      }
    });

    // Check that the preset is correctly detected as OpenAI
    const providerSelect = getByLabelText(/llm provider/i);
    expect(providerSelect.value).toBe('OpenAI');

    // Check that all fields are populated
    expect(getByDisplayValue('My OpenAI')).toBeTruthy();
    expect(getByDisplayValue('https://api.openai.com/v1')).toBeTruthy();
    expect(getByDisplayValue('gpt-4')).toBeTruthy();
  });

  it('should save LLM to config store through ConfigModal', async () => {
    const { getByText, getByLabelText } = render(ConfigModal);

    // Click Add LLM button
    const addButton = getByText(/add llm/i);
    await fireEvent.click(addButton);

    // Fill in the form
    await waitFor(() => {
      const nameInput = getByLabelText(/display name/i);
      fireEvent.input(nameInput, { target: { value: 'Test LLM' } });
    });

    const urlInput = getByLabelText(/api url/i);
    const modelInput = getByLabelText(/model/i);
    const apiKeyInput = getByLabelText(/api key/i);

    await fireEvent.input(urlInput, { target: { value: 'https://api.openai.com/v1' } });
    await fireEvent.input(modelInput, { target: { value: 'gpt-4' } });
    await fireEvent.input(apiKeyInput, { target: { value: 'test-key' } });

    // Submit the form
    const submitButton = getByText(/add llm/i);
    await fireEvent.click(submitButton);

    // Verify the LLM was added to the store
    await waitFor(() => {
      expect(configStore.llms).toHaveLength(1);
      expect(configStore.llms[0]).toMatchObject({
        name: 'Test LLM',
        url: 'https://api.openai.com/v1',
        model: 'gpt-4',
        apiKey: 'test-key',
        enabled: true
      });
    });
  });

  it('should update existing LLM configuration', async () => {
    // Add an initial LLM
    await configStore.addLLM({
      name: 'Original Name',
      url: 'https://api.openai.com/v1',
      model: 'gpt-3.5-turbo',
      apiKey: 'original-key',
      enabled: true
    });

    const llmId = configStore.llms[0].id;

    // Update the LLM
    await configStore.updateLLM(llmId, {
      name: 'Updated Name',
      model: 'gpt-4'
    });

    // Verify the update
    await waitFor(() => {
      const updatedLLM = configStore.llms.find(l => l.id === llmId);
      expect(updatedLLM).toMatchObject({
        name: 'Updated Name',
        url: 'https://api.openai.com/v1',
        model: 'gpt-4',
        apiKey: 'original-key',
        enabled: true
      });
    });
  });
});