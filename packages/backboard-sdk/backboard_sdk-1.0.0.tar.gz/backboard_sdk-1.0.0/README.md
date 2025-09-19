# Backboard Python SDK

The official Python SDK for the Backboard API - Build conversational AI applications with persistent memory and intelligent document processing.

## Installation

```bash
pip install backboard-sdk
```

## Quick Start

```python
import backboard
from backboard.api import assistants_api, threads_api, documents_api
from backboard.model.assistant_create import AssistantCreate

# Configure API key authentication
configuration = backboard.Configuration(
    api_key={'APIKeyHeader': 'your_api_key_here'}
)

# Create API client
with backboard.ApiClient(configuration) as api_client:
    # Create APIs
    assistants = assistants_api.AssistantsApi(api_client)
    threads = threads_api.ThreadsApi(api_client)
    documents = documents_api.DocumentsApi(api_client)

    # 1. Create an assistant
    assistant_data = AssistantCreate(
        name="Support Bot",
        instructions="You are a helpful customer support assistant."
    )
    assistant = assistants.create_assistant(assistant_data)
    print(f"Created assistant: {assistant.id}")

    # 2. Create a thread
    thread = threads.create_thread()
    print(f"Created thread: {thread.id}")

    # 3. Send a message
    message = threads.send_message(
        thread_id=thread.id,
        message="Hello! I need help with my account."
    )
    print(f"Message sent: {message.id}")
```

## API Reference

### Assistants API
- `create_assistant(assistant_data)` - Create a new assistant
- `get_assistant(assistant_id)` - Retrieve an assistant
- `list_assistants()` - List all assistants
- `update_assistant(assistant_id, update_data)` - Update an assistant
- `delete_assistant(assistant_id)` - Delete an assistant

### Threads API
- `create_thread()` - Create a new conversation thread
- `get_thread(thread_id)` - Retrieve a thread
- `list_threads()` - List all threads
- `delete_thread(thread_id)` - Delete a thread
- `send_message(thread_id, message)` - Send a message to a thread
- `get_messages(thread_id)` - Get messages from a thread

### Documents API
- `upload_document(file_data)` - Upload a document
- `get_document(document_id)` - Retrieve a document
- `list_documents()` - List all documents
- `delete_document(document_id)` - Delete a document

## Authentication

The SDK supports API key authentication. You can get your API key from the [Backboard Dashboard](https://backboard.io/dashboard).

```python
configuration = backboard.Configuration(
    api_key={'APIKeyHeader': 'your_api_key_here'}
)
```

## Error Handling

```python
from backboard.exceptions import ApiException

try:
    assistant = assistants.create_assistant(assistant_data)
except ApiException as e:
    print(f"API Error: {e.status} - {e.reason}")
    print(f"Response body: {e.body}")
```

## Advanced Usage

### Custom Configuration

```python
configuration = backboard.Configuration(
    host="https://your-custom-api-endpoint.com",
    api_key={'APIKeyHeader': 'your_api_key_here'}
)
```

### Async Support

The SDK supports async operations:

```python
import asyncio
import backboard

async def main():
    configuration = backboard.Configuration(
        api_key={'APIKeyHeader': 'your_api_key_here'}
    )
    
    async with backboard.ApiClient(configuration) as api_client:
        assistants = assistants_api.AssistantsApi(api_client)
        assistant = await assistants.create_assistant(assistant_data)
        print(f"Created assistant: {assistant.id}")

asyncio.run(main())
```

## Examples

Check out the `example.py` file in this repository for a complete working example.

## Support

- **Documentation**: [https://docs.backboard.io](https://docs.backboard.io)
- **API Reference**: [https://backboard.io/api/docs](https://backboard.io/api/docs)
- **Support**: [support@backboard.io](mailto:support@backboard.io)

## License

This project is licensed under the MIT License.