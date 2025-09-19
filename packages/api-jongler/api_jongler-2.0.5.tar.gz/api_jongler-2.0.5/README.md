# API Jongler v2.0.0

A sophisticated middleware utility for calling Google AI APIs (Gemini and Gemma) with intelligent rate limiting, automatic retry logic, and advanced key management to maximize free tier usage.

## Description

APIJongler is a production-ready Python utility that intelligently manages multiple API keys for Google AI services (Gemini) and Hugging Face Gemma models. Version 2.0.0 introduces advanced features including automatic rate limit detection, sophisticated retry logic, and intelligent key state management to ensure maximum uptime and efficiency.

## 🚀 What's New in v2.0.0

- **🧠 Intelligent Rate Limit Detection**: Automatically detects and handles rate limiting (429, 403, 503, 509 errors)
- **🔄 Advanced Retry Logic**: Connection-scoped key tracking with smart retry mechanisms
- **🔒 LOCKDOWN State Management**: Temporarily quarantines rate-limited keys with automatic recovery
- **📊 Real-time Key Monitoring**: New APIs to monitor key states (`getKeyStates()`, `getLockdownKeys()`, `getVacantKeys()`)
- **💾 Persistent State Management**: File-based state persistence survives application restarts
- **🛡️ Production-Ready Error Handling**: Meaningful error messages with configuration examples
- **📈 Enhanced Logging**: Comprehensive state transition logging for debugging and monitoring
- **🔙 100% Backward Compatible**: Drop-in replacement for v1.x installations

## Features

- **Google AI Integration**: Seamless access to both Gemini API and Gemma models via Hugging Face
- **Intelligent Key Management**: Advanced state machine with VACANT → LOCKED → LOCKDOWN states
- **Automatic Rate Limiting**: Detects rate limits and automatically switches to alternative keys
- **Smart Retry Logic**: Connection-scoped tracking prevents infinite loops while maximizing success
- **Lock Management**: Prevents concurrent use of the same API key across multiple processes
- **Persistent State**: File-based state management survives crashes and restarts
- **Error Recovery**: Automatic recovery of rate-limited keys on successful requests
- **Tor Support**: Optional routing through Tor network for enhanced privacy
- **Extensible**: Easy to add new API connectors via JSON configuration
- **Production Logging**: Comprehensive logging with colored console output and state tracking

## Installation

```bash
pip install api-jongler
```

## Configuration

1. Set the configuration file path:
```bash
export APIJONGLER_CONFIG=/path/to/your/APIJongler.ini
```

2. Create your configuration file (APIJongler.ini):
```ini
[generativelanguage.googleapis.com]
key1 = your-gemini-api-key-1
key2 = your-gemini-api-key-2
key3 = your-gemini-api-key-3

[api-inference.huggingface.co]
key1 = hf_your-huggingface-token-1
key2 = hf_your-huggingface-token-2
key3 = hf_your-huggingface-token-3
```

**Note**: 
- For Google Gemini API keys, get them free at [Google AI Studio](https://aistudio.google.com/app/apikey).
- For Gemma models via Hugging Face, get API tokens at [Hugging Face Settings](https://huggingface.co/settings/tokens).

## 🔄 Migration from v1.x to v2.0.0

APIJongler v2.0.0 is **100% backward compatible**. Existing code will work unchanged with additional benefits:

### What You Get Automatically
- ✅ **Automatic rate limit handling** - No code changes needed
- ✅ **Intelligent retry logic** - Requests automatically retry with different keys
- ✅ **Better error messages** - More helpful error information
- ✅ **Persistent state** - Key states survive application restarts
- ✅ **Enhanced logging** - Better visibility into what's happening

### Optional New Features
```python
# Your existing v1.x code works unchanged:
jongler = APIJongler("generativelanguage.googleapis.com")
response = jongler.requestJSON("/endpoint", {"data": "test"})

# But you can now optionally monitor key states:
states = jongler.getKeyStates()  # New in v2.0.0
lockdown_keys = jongler.getLockdownKeys()  # New in v2.0.0
vacant_keys = jongler.getVacantKeys()  # New in v2.0.0

# Rate limiting and retry happen automatically - no code changes needed!
```

### Configuration Changes
- ✅ **No changes required** - Same `APIJongler.ini` format
- ✅ **Same environment variable** - `APIJONGLER_CONFIG` 
- ✅ **Same CLI commands** - All existing commands work
- ✅ **Additional cleanup options** - New `--cleanup` and `--cleanup-all` flags

## Usage

### Basic Example with Google Gemini (Free Tier)

```python
from api_jongler import APIJongler

# Initialize with Gemini connector - automatically selects best available key
jongler = APIJongler("generativelanguage.googleapis.com", is_tor_enabled=False)

# Use Gemini 1.5 Flash (free tier) for text generation
# v2.0.0 automatically handles rate limits and retries with different keys
response, status_code = jongler.request(
    method="POST",
    endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
    request='{"contents":[{"parts":[{"text":"Hello, how are you?"}]}]}'
)

print(f"Response: {response}")
print(f"Status Code: {status_code}")

# Monitor key states (new in v2.0.0)
states = jongler.getKeyStates()
print(f"Available keys: {len(states['vacant'])}")
print(f"Rate-limited keys: {len(states['lockdown'])}")

# Clean up when done (automatically called on destruction)
del jongler

# Or manually clean up all locks and errors
APIJongler.cleanUp()
```

### Advanced Key Management (New in v2.0.0)

```python
from api_jongler import APIJongler

# Initialize connector
jongler = APIJongler("generativelanguage.googleapis.com")

# Monitor key states in real-time
states = jongler.getKeyStates()
print(f"Vacant keys: {states['vacant']}")        # Available for use
print(f"Locked keys: {states['locked']}")        # Currently in use
print(f"Lockdown keys: {states['lockdown']}")    # Rate-limited, recovering
print(f"Error keys: {states['error']}")          # Permanently failed

# Get specific key sets
vacant_keys = jongler.getVacantKeys()        # Ready to use
lockdown_keys = jongler.getLockdownKeys()    # Temporarily unavailable
available_keys = jongler.getAvailableKeys()  # All configured keys

# Make requests with automatic retry and rate limit handling
try:
    response_data = jongler.requestJSON(
        endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
        data={"contents": [{"parts": [{"text": "Explain quantum computing"}]}]}
    )
    print("Request successful!")
except RuntimeError as e:
    print(f"All keys exhausted: {e}")
    # Error includes helpful configuration examples

jongler.disconnect()
```

### Working with JSON Data (Recommended)

```python
from api_jongler import APIJongler

# Initialize with Gemini connector
jongler = APIJongler("generativelanguage.googleapis.com")

# Use requestJSON() for automatic JSON handling (recommended)
# v2.0.0 automatically retries with different keys on rate limits
response_data = jongler.requestJSON(
    endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
    data={
        "contents": [{"parts": [{"text": "Explain machine learning"}]}]
    }
)

# Response is automatically parsed as dictionary
print(response_data["candidates"][0]["content"]["parts"][0]["text"])

# Check if any keys were moved to lockdown during the request
lockdown_keys = jongler.getLockdownKeys()
if lockdown_keys:
    print(f"Rate-limited keys: {lockdown_keys}")
    print("These keys will be automatically retried later")
```

### Method Comparison

APIJongler provides two methods for making requests:

| Method | Input | Output | Rate Limit Handling | Use Case |
|--------|--------|---------|---------------------|----------|
| `request()` | Raw string | `(response_text, status_code)` | ✅ Automatic retry | Low-level control, non-JSON APIs |
| `requestJSON()` | Python dict | Parsed dictionary | ✅ Automatic retry | JSON APIs (recommended) |

**Example with both methods:**

```python
# Low-level with request() - includes automatic rate limit handling
response_text, status_code = jongler.request(
    method="POST",
    endpoint="/v1beta/models/gemini-1.5-flash:generateContent", 
    request='{"contents":[{"parts":[{"text":"Hello"}]}]}'  # Raw JSON string
)
import json
data = json.loads(response_text)  # Manual parsing

# High-level with requestJSON() - includes automatic rate limit handling
data = jongler.requestJSON(
    endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
    data={"contents": [{"parts": [{"text": "Hello"}]}]}  # Python dict
)
# No manual parsing needed
```

### Rate Limiting and Recovery (New in v2.0.0)

APIJongler v2.0.0 intelligently handles rate limiting:

```python
from api_jongler import APIJongler
import time

jongler = APIJongler("generativelanguage.googleapis.com")

# Make multiple requests - rate limiting handled automatically
for i in range(10):
    try:
        response = jongler.requestJSON(
            endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
            data={"contents": [{"parts": [{"text": f"Request {i}"}]}]}
        )
        print(f"Request {i}: Success")
        
        # Check key states after each request
        states = jongler.getKeyStates()
        if states['lockdown']:
            print(f"Keys in lockdown: {states['lockdown']}")
            
    except RuntimeError as e:
        print(f"Request {i}: All keys exhausted - {e}")
        # Wait for lockdown keys to potentially recover
        time.sleep(60)
        continue

# Keys in lockdown will automatically recover on successful requests
print("Final key states:")
final_states = jongler.getKeyStates()
for state, keys in final_states.items():
    if keys:
        print(f"{state.title()}: {keys}")

jongler.disconnect()
```

### Available Gemini Models

The Gemini connector provides access to these models:

| Model | Description | Free Tier | Best For |
|-------|-------------|-----------|----------|
| `gemini-1.5-flash` | Fast and versatile | ✅ Yes | General tasks, quick responses |
| `gemini-2.0-flash` | Latest generation | ✅ Yes | Modern features, enhanced speed |
| `gemini-2.5-flash` | Best price/performance | Paid | Cost-effective quality responses |
| `gemini-2.5-pro` | Most powerful | Paid | Complex reasoning, advanced tasks |
| `gemini-1.5-pro` | Complex reasoning | Paid | Advanced analysis, coding |

### CLI Usage Examples

```bash
# Quick text generation (free tier) with automatic rate limit handling
apijongler generativelanguage.googleapis.com POST /v1beta/models/gemini-1.5-flash:generateContent '{"contents":[{"parts":[{"text":"Hello"}]}]}' --pretty

# Code generation (free tier) - will automatically retry with different keys if rate limited
apijongler generativelanguage.googleapis.com POST /v1beta/models/gemini-2.0-flash:generateContent '{"contents":[{"parts":[{"text":"Write a Python function"}]}]}' --pretty

# Advanced reasoning (requires paid tier)
apijongler generativelanguage.googleapis.com POST /v1beta/models/gemini-2.5-pro:generateContent '{"contents":[{"parts":[{"text":"Analyze this problem"}]}]}' --pretty

# Clean up lockdown/error states for specific connector
apijongler --cleanup generativelanguage.googleapis.com

# Clean up all lockdown and error states 
apijongler --cleanup-all

# Use with custom config file
apijongler --config /path/to/config.ini generativelanguage.googleapis.com POST /endpoint '{"data":"test"}'
```

## 🔧 Key State Management

APIJongler v2.0.0 uses a sophisticated state machine for key management:

### Key States

| State | Description | File Marker | Recovery |
|-------|-------------|-------------|----------|
| **VACANT** | Available for use | No file | Ready |
| **LOCKED** | Currently in use | `.lock` | Auto on disconnect |
| **LOCKDOWN** | Rate-limited | `.lockdown` | Auto on successful request |
| **ERROR** | Permanent failure | `.error` | Manual cleanup only |

### State Transitions

```
VACANT → LOCKED (when selected for request)
  ↓
LOCKED → VACANT (on successful request or non-rate-limit error)
  ↓
LOCKED → LOCKDOWN (on rate limit error: 429, 403, 503, 509)
  ↓
LOCKDOWN → VACANT (on successful request with lockdown key)
```

### Monitoring Key States

```python
from api_jongler import APIJongler

jongler = APIJongler("generativelanguage.googleapis.com")

# Get complete state breakdown
states = jongler.getKeyStates()
print(f"📊 Key State Summary:")
print(f"  💚 Vacant (ready): {len(states['vacant'])}")
print(f"  🟡 Locked (in use): {len(states['locked'])}")  
print(f"  🔴 Lockdown (rate limited): {len(states['lockdown'])}")
print(f"  ❌ Error (failed): {len(states['error'])}")

# Get specific key sets
vacant = jongler.getVacantKeys()        # Set of available keys
lockdown = jongler.getLockdownKeys()    # Set of rate-limited keys
available = jongler.getAvailableKeys()  # Dict of all configured keys

# Monitor during high-volume usage
for i in range(100):
    try:
        response = jongler.requestJSON("/endpoint", {"data": f"request {i}"})
        if i % 10 == 0:  # Check every 10 requests
            current_lockdown = jongler.getLockdownKeys()
            if current_lockdown:
                print(f"Request {i}: {len(current_lockdown)} keys in lockdown")
    except RuntimeError:
        print(f"Request {i}: All keys exhausted")
        break

jongler.disconnect()
```

## API Connectors

API connectors are defined in JSON files in the `connectors/` directory. Example:

```json
{
    "name": "generativelanguage.googleapis.com",
    "host": "generativelanguage.googleapis.com",
    "port": 443,
    "protocol": "https",
    "format": "json",
    "requires_api_key": true
}
```

### Pre-configured Connectors

- **generativelanguage.googleapis.com**: Access to Google's Gemini API models (gemini-1.5-flash, gemini-2.0-flash, gemini-2.5-flash, etc.)
- **api-inference.huggingface.co**: Open-source Gemma models via Hugging Face Inference API (gemma-2-9b-it, gemma-2-27b-it, etc.)
- **httpbin.org**: For testing and development purposes only

### Gemma vs Gemini Models

**Important**: Gemma and Gemini are different model families:

| Model Family | Access Method | API Keys Source | Example Model |
|--------------|---------------|-----------------|---------------|
| **Gemini** | Google's Cloud API | [Google AI Studio](https://aistudio.google.com/app/apikey) | gemini-1.5-flash |
| **Gemma** | Hugging Face Inference API | [HuggingFace Tokens](https://huggingface.co/settings/tokens) | google/gemma-2-9b-it |

#### Gemma Usage Examples

```python
from api_jongler import APIJongler

# Use Gemma 2 9B model
jongler = APIJongler("api-inference.huggingface.co")
response = jongler.requestJSON(
    endpoint="/models/google/gemma-2-9b-it",
    data={
        "inputs": "What is machine learning?",
        "parameters": {"max_new_tokens": 100, "temperature": 0.7}
    }
)
print(response)
```

```bash
# CLI usage for Gemma
apijongler api-inference.huggingface.co POST /models/google/gemma-2-27b-it '{"inputs":"Explain Python","parameters":{"max_new_tokens":150}}' --pretty
```

**Note**: The Gemini connector provides access to Google's **Gemini API** models, not Gemma models. Available models include:
- `gemini-1.5-flash` - Fast and versatile (free tier)
- `gemini-2.0-flash` - Latest generation (free tier)  
- `gemini-2.5-flash` - Best price/performance
- `gemini-2.5-pro` - Most powerful model
- `gemini-1.5-pro` - Complex reasoning tasks

## 🚀 Production Tips

### Maximizing Free Tier Usage

```python
# Configure multiple keys for maximum throughput
# APIJongler automatically distributes load and handles rate limits

# Monitor key health in production
import logging
logging.basicConfig(level=logging.INFO)

jongler = APIJongler("generativelanguage.googleapis.com")

# Check available capacity before high-volume operations
states = jongler.getKeyStates()
available_capacity = len(states['vacant']) + len(states['lockdown'])

if available_capacity < 2:
    print("⚠️  Low key availability - consider adding more keys")

# Use in production with proper error handling
def make_ai_request(prompt):
    try:
        return jongler.requestJSON(
            endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
            data={"contents": [{"parts": [{"text": prompt}]}]}
        )
    except RuntimeError as e:
        # All keys exhausted - implement backoff strategy
        print(f"API temporarily unavailable: {e}")
        return None

# Clean up lockdown states periodically (optional)
# Keys recover automatically, but manual cleanup can help in some cases
APIJongler.cleanUp()
```

### Error Handling and Recovery

```python
from api_jongler import APIJongler
import time

def robust_api_call(prompt, max_retries=3):
    jongler = APIJongler("generativelanguage.googleapis.com")
    
    for attempt in range(max_retries):
        try:
            return jongler.requestJSON(
                endpoint="/v1beta/models/gemini-1.5-flash:generateContent",
                data={"contents": [{"parts": [{"text": prompt}]}]}
            )
        except RuntimeError as e:
            if "No API keys available" in str(e):
                print(f"Attempt {attempt + 1}: All keys exhausted")
                if attempt < max_retries - 1:
                    # Wait for potential key recovery
                    time.sleep(30)  
                    continue
                else:
                    raise
        finally:
            jongler.disconnect()
    
    return None

# Use with automatic recovery
result = robust_api_call("Explain quantum computing")
if result:
    print("Success!")
else:
    print("Failed after all retries")
```

## License

MIT License
