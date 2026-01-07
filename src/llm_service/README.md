# LLM Service

Unified interface for Large Language Model services with support for multiple providers.

## Supported Providers

- **Gemini** - Google's Gemini models with advanced reasoning capabilities
- **Qwen** - Alibaba's Qwen models via OpenAI-compatible API

## Quick Start

### 1. Install Dependencies

```bash
pip install google-generativeai openai python-dotenv
```

### 2. Configure Environment

Create a `.env` file:

```bash
# For Gemini
GEMINI_API_KEY=your_gemini_api_key_here
LLM_SERVICE=gemini

# For Qwen (optional)
QWEN_API_KEY=your_qwen_api_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 3. Basic Usage

```python
from llm_service import generate, chat, LLMClient

# Simple generation
response = generate("Explain quantum computing in simple terms")
print(response)

# With system prompt
response = generate(
    "What is Python?",
    system_prompt="You are a programming expert",
    temperature=0.0
)

# Chat conversation
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello!"},
]
response = chat(messages)

# Stateful conversation
client = LLMClient(service="gemini", system_prompt="You are helpful")
response1 = client.send("What is AI?")
response2 = client.send("Can you explain more?")
```

## API Reference

### Function: `generate()`

Generate text completion from a prompt.

```python
def generate(
    prompt: str,
    service: Optional[str] = None,  # 'gemini' or 'qwen'
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str
```

**Parameters:**
- `prompt` - User prompt/message
- `service` - LLM service ('gemini' or 'qwen'). Uses `LLM_SERVICE` env var if not provided
- `model` - Model name (optional, uses defaults if not provided)
- `temperature` - 0.0 to 2.0. Higher = more random
- `max_tokens` - Maximum tokens to generate
- `system_prompt` - System instruction/context
- `**kwargs` - Provider-specific parameters

**Returns:** Generated text

---

### Function: `chat()`

Generate response from conversation history.

```python
def chat(
    messages: List[Dict[str, str]],
    service: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    **kwargs
) -> str
```

**Parameters:**
- `messages` - List of message dicts with 'role' and 'content'
  - Roles: 'system', 'user', 'assistant'
- Other parameters same as `generate()`

**Message Format:**
```python
[
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Tell me a joke"}
]
```

**Returns:** Generated response

---

### Class: `LLMClient`

Stateful client for maintaining conversation context.

```python
client = LLMClient(
    service: Optional[str] = None,
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
)
```

**Methods:**

- `send(message: str) -> str` - Send message and get response
- `get_history() -> List[Dict]` - Get conversation history
- `clear_history(keep_system_prompt: bool = True)` - Clear history
- `set_system_prompt(prompt: str)` - Update system prompt

**Example:**
```python
client = LLMClient(
    service="gemini",
    system_prompt="You are a Python expert"
)

# Conversation maintains context
response1 = client.send("What is a list comprehension?")
response2 = client.send("Can you show an example?")  # Remembers context

# View history
history = client.get_history()
print(f"Messages: {len(history)}")

# Start fresh
client.clear_history()
```

---

## Provider Details

### Gemini

**Models:**
- `gemini-3-flash-preview` (default)
- `gemini-2.0-flash-exp`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

**Environment Variables:**
```bash
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-3-flash-preview  # optional
```

**Get API Key:** https://aistudio.google.com/app/apikey

**Example:**
```python
response = generate(
    "Explain transformers",
    service="gemini",
    model="gemini-1.5-pro",
    temperature=0.5
)
```

---

### Qwen (OpenAI-compatible)

**Models:**
- `qwen-turbo` (default, fast)
- `qwen-plus` (balanced)
- `qwen-max` (most capable)
- `qwen-2.5-72b-instruct`
- `qwen-2.5-32b-instruct`

**Environment Variables:**
```bash
QWEN_API_KEY=your_api_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo  # optional
```

**Get API Key:** https://dashscope.console.aliyun.com/

**Supported Endpoints:**
- Alibaba DashScope: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Local vLLM: `http://localhost:8000/v1`
- Local Text Generation Inference: `http://localhost:8080/v1`

**Example:**
```python
response = generate(
    "Explain quantum computing",
    service="qwen",
    model="qwen-plus",
    temperature=0.7,
    max_tokens=500
)
```

---

## Advanced Usage

### Custom Parameters

Each provider supports additional parameters via `**kwargs`:

```python
# Gemini-specific
response = generate(
    "Hello",
    service="gemini",
    top_p=0.95,
    top_k=40
)

# Qwen/OpenAI-compatible
response = generate(
    "Hello",
    service="qwen",
    top_p=0.9,
    frequency_penalty=0.5,
    presence_penalty=0.5
)
```

### Streaming (Qwen only)

```python
from llm_service import QwenLLMService

qwen = QwenLLMService()
messages = [{"role": "user", "content": "Tell me a story"}]

for chunk in qwen.stream_chat(messages):
    print(chunk, end='', flush=True)
```

### Error Handling

```python
from llm_service import generate

try:
    response = generate("Hello", service="qwen")
except ValueError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Generation failed: {e}")
```

### Factory Pattern

```python
from llm_service import LLMServiceFactory

# Create service directly
llm = LLMServiceFactory.create(service="gemini", model="gemini-1.5-pro")

# Use the service
response = llm.generate("Hello")
chat_response = llm.chat([
    {"role": "user", "content": "Hi"}
])
```

---

## Examples

See `examples/llm_usage_examples.py` for complete examples:

```bash
python examples/llm_usage_examples.py
```

---

## Architecture

```
llm_service/
├── __init__.py          # Public exports
├── base.py              # Abstract base class
├── factory.py           # Service factory
├── gemini_service.py    # Gemini implementation
├── qwen_service.py      # Qwen implementation
└── client.py            # High-level client functions
```

**Design Pattern:** Factory + Strategy pattern for swappable LLM providers

---

## Adding New Providers

To add a new LLM provider:

1. Create `your_service.py` implementing `LLMServiceBase`
2. Add to `SERVICES` dict in `factory.py`
3. Update `get_service_info()` in `factory.py`
4. Add environment variables to `.env.example`

Example:
```python
# your_service.py
from .base import LLMServiceBase

class YourLLMService(LLMServiceBase):
    def generate(self, prompt, **kwargs):
        # Your implementation
        pass

    def chat(self, messages, **kwargs):
        # Your implementation
        pass

    # ... other required methods
```

---

## Troubleshooting

### Issue: "API key is not configured"
**Solution:** Set the appropriate environment variable in `.env`
```bash
GEMINI_API_KEY=your_key_here
# or
QWEN_API_KEY=your_key_here
```

### Issue: "Failed to initialize service"
**Solution:** Install required dependencies
```bash
pip install google-generativeai openai
```

### Issue: Qwen connection error
**Solution:** Check `QWEN_BASE_URL` is correct and accessible
```bash
# Test connection
curl https://dashscope.aliyuncs.com/compatible-mode/v1/models \
  -H "Authorization: Bearer $QWEN_API_KEY"
```

---

## License

Part of ExfillFramework project.
