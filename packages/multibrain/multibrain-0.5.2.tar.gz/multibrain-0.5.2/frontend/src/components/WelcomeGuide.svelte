<!-- Svelte 5 Migration: WelcomeGuide.svelte - 2025-09-15 -->
<script>
  import { fade, fly } from 'svelte/transition';
  
  let { oncomplete } = $props();
  
  let currentStep = $state(0);
  
  const steps = [
    {
      title: 'Welcome to MultiBrain!',
      content: 'Query multiple AI models simultaneously and get a unified summary.',
      icon: `<svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"></path>
      </svg>`
    },
    {
      title: 'Configure Your LLMs',
      content: 'Add your API keys for OpenAI, Anthropic, or other providers.',
      icon: `<svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
      </svg>`
    },
    {
      title: 'Ask Your Question',
      content: 'Type your query and watch as multiple AIs respond in real-time.',
      icon: `<svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
      </svg>`
    },
    {
      title: 'Get Unified Insights',
      content: 'A summary AI analyzes all responses and provides a comprehensive answer.',
      icon: `<svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
      </svg>`
    }
  ];
  
  function nextStep() {
    if (currentStep < steps.length - 1) {
      currentStep++;
    } else {
      oncomplete?.();
    }
  }
  
  function prevStep() {
    if (currentStep > 0) {
      currentStep--;
    }
  }
  
  function skip() {
    oncomplete?.();
  }
</script>

<div class="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" transition:fade={{ duration: 300 }}>
  <div
    class="bg-gray-800 rounded-lg shadow-2xl max-w-md w-full overflow-hidden"
    transition:fly={{ y: 50, duration: 300 }}
  >
    <!-- Progress Bar -->
    <div class="h-1 bg-gray-700">
      <div 
        class="h-full bg-blue-500 transition-all duration-300"
        style="width: {((currentStep + 1) / steps.length) * 100}%"
      ></div>
    </div>
    
    <!-- Content -->
    <div class="p-8">
      {#key currentStep}
        <div in:fade={{ duration: 200, delay: 100 }}>
          <!-- Icon -->
          <div class="text-blue-400 mb-6 flex justify-center">
            {@html steps[currentStep].icon}
          </div>
          
          <!-- Title -->
          <h2 class="text-2xl font-bold text-center mb-4">
            {steps[currentStep].title}
          </h2>
          
          <!-- Content -->
          <p class="text-gray-300 text-center mb-8">
            {steps[currentStep].content}
          </p>
        </div>
      {/key}
      
      <!-- Navigation -->
      <div class="flex items-center justify-between">
        <button
          onclick={skip}
          class="text-gray-400 hover:text-gray-300 transition-colors"
        >
          Skip
        </button>
        
        <div class="flex items-center gap-2">
          {#each steps as _, i}
            <div 
              class="w-2 h-2 rounded-full transition-all duration-300 {i === currentStep ? 'bg-blue-500 w-8' : 'bg-gray-600'}"
            ></div>
          {/each}
        </div>
        
        <div class="flex items-center gap-2">
          {#if currentStep > 0}
            <button
              onclick={prevStep}
              class="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              aria-label="Previous step"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
              </svg>
            </button>
          {/if}
          
          <button
            onclick={nextStep}
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-2"
          >
            {#if currentStep === steps.length - 1}
              Get Started
            {:else}
              Next
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
              </svg>
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
</div>