# MultiBrain

MultiBrain is a powerful web application that queries multiple AI models simultaneously, providing real-time streaming responses and intelligent summaries. Built with **Svelte 5** and FastAPI, it offers a modern, responsive interface for comparing AI responses side-by-side.

![MultiBrain](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)
![Svelte](https://img.shields.io/badge/Svelte-5.0-orange.svg)

## 🚀 Features

- **Multi-Model Querying**: Query multiple AI providers simultaneously (OpenAI, Anthropic, Groq, Ollama, etc.)
- **Real-Time Streaming**: Watch responses stream in real-time from all configured models
- **Intelligent Summaries**: Automatic synthesis of all responses into a unified, fact-checked summary
- **Bring Your Own Keys**: Secure, client-side API key management with local encryption
- **Modern UI**: Beautiful, responsive interface built with Svelte and Tailwind CSS
- **Keyboard Shortcuts**: Efficient navigation with customizable keyboard shortcuts
- **No Limits**: Configure unlimited AI models with no artificial restrictions

## 📋 Requirements

- Python 3.8+
- Node.js 16+
- npm or yarn
- Svelte 5.0+ (included in dependencies)

## 🛠️ Installation

### Backend Setup

1. Clone the repository:
```bash
git clone https://spacecruft.org/deepcrayon/multibrain
cd multibrain
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -U pip setuptools wheel
pip install -e .
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## 🚦 Running the Application

### Development Mode

1. Start the backend API server:
```bash
multibrain-api
```
The API server will run on `http://localhost:8000`

2. In a new terminal, start the frontend development server:
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:5173`

### Production Mode

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. Start the backend with static file serving:
```bash
multibrain-api --serve-static
```

Visit `http://localhost:8000` to use the application.

## 🔧 Configuration

### Adding LLM Providers

1. Click the "Configure LLMs" button in the header
2. Select a provider preset or choose "Custom"
3. Enter your API credentials:
   - **Display Name**: A friendly name for the LLM
   - **API URL**: The OpenAI-compatible endpoint
   - **Model**: The specific model to use
   - **API Key**: Your provider's API key

### Supported Providers

- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 Opus, Sonnet, Haiku
- **Groq**: Mixtral, Llama 2
- **Ollama**: Local models (Llama 2, Mistral, CodeLlama)
- **Custom**: Any OpenAI-compatible endpoint

### Setting a Summary LLM

The summary LLM analyzes all responses and provides a unified answer:

1. Configure at least one LLM
2. In the configuration modal, select your preferred model from the "Summary LLM" dropdown
3. The summary will automatically generate after all responses complete

## ⌨️ Keyboard Shortcuts

- `Ctrl+K`: Open LLM configuration
- `Ctrl+/`: Focus query input
- `Ctrl+Enter`: Submit query
- `Shift+?`: Show keyboard shortcuts
- `Escape`: Close modals

## 🏗️ Architecture

### Frontend (Svelte 5 + Vite)

The frontend has been fully migrated to Svelte 5, leveraging the latest features:

- **Runes API**: Using `$state`, `$derived`, `$effect` for reactive state management
- **Props with `$props()`**: Modern component prop handling
- **Bindable Props**: Two-way binding with `$bindable`
- **Snippets**: Reusable template fragments for better composition

```
frontend/
├── src/
│   ├── components/      # Svelte 5 components with runes
│   ├── stores/          # State management (.svelte.js files)
│   ├── lib/             # Utilities and helpers
│   └── App.svelte       # Main application
```

#### Key Svelte 5 Features Used:

1. **State Management**: All stores use `.svelte.js` extension with runes
2. **Component Props**: Migrated from `export let` to `$props()`
3. **Reactive Effects**: Using `$effect` for side effects instead of `$:`
4. **Performance**: Leveraging Svelte 5's improved reactivity system

### Backend (FastAPI)
```
src/multibrain/
├── api/
│   ├── routes/          # API endpoints
│   │   ├── streaming.py # SSE streaming logic
│   │   └── router.py    # Route definitions
│   └── main.py          # FastAPI application
```

## 🔒 Security

- **Local Storage**: API keys are encrypted using Web Crypto API
- **No Backend Storage**: Keys are never sent to or stored on the backend
- **Secure Proxy**: Backend proxies requests to avoid CORS issues
- **HTTPS Ready**: Full support for secure deployments

## 🧪 Development

### Svelte 5 Migration

This project has been fully migrated to Svelte 5. Key changes include:

- All components use the new runes API (`$state`, `$derived`, `$effect`)
- Stores are now `.svelte.js` files with reactive primitives
- Props use the `$props()` rune for better type safety
- Two-way binding with `$bindable` for form inputs
- Improved performance with Svelte 5's optimized compiler

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

### Component Development

When creating new components, follow the Svelte 5 patterns:

```javascript
// Use $props() for component props
let { value = $bindable(''), onsubmit } = $props();

// Use $state for reactive state
let count = $state(0);

// Use $derived for computed values
let doubled = $derived(count * 2);

// Use $effect for side effects
$effect(() => {
  console.log('Count changed:', count);
});
```

### Building for Production

```bash
# Build Python package
python -m build

# Build frontend
cd frontend
npm run build
```

## 📝 API Documentation

Once the backend is running, visit:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /api/query/stream`: Stream responses from multiple LLMs
- `POST /api/llm/validate`: Test LLM configuration
- `POST /api/llm/models`: List available models

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE-apache.txt) file for details.

Alternative licensing under Creative Commons CC BY-SA 4.0 International is also available.

## 🙏 Acknowledgments

- Built with [Svelte 5](https://svelte.dev/) and [FastAPI](https://fastapi.tiangolo.com/)
- UI components styled with [Tailwind CSS](https://tailwindcss.com/)
- Markdown rendering by [Marked](https://marked.js.org/)
- Migrated to Svelte 5 runes API for improved performance and developer experience

## 📞 Support

- Documentation: [https://spacecruft.org/deepcrayon/multibrain](https://spacecruft.org/deepcrayon/multibrain)
- Issues: [https://spacecruft.org/deepcrayon/multibrain/issues](https://spacecruft.org/deepcrayon/multibrain/issues)

---

*Copyright © 2025 Jeff Moe*