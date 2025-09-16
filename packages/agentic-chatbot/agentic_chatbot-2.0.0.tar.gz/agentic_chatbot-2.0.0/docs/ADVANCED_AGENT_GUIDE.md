# Advanced Conversation Agent Guide

## Overview

The `AdvancedConversationAgent` is a production-ready, enterprise-grade conversation agent that provides comprehensive features for building sophisticated chatbots and AI assistants.

## 🚀 Key Features

### Multi-Provider LLM Support
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude models
- **Google**: Gemini models
- **Local Models**: Ollama integration
- **Testing**: Fake LLM for development

### Memory Management
- **Buffer Memory**: Store complete conversation history
- **Summary Memory**: Keep only summarized conversations
- **Summary Buffer**: Hybrid approach with token limits
- **Entity Memory**: Track entities across conversations
- **Knowledge Graph**: Relationship-based memory
- **Combined Memory**: Multiple memory types together

### History Backends
- **In-Memory**: Fast, volatile storage
- **File**: Persistent file-based storage
- **Redis**: High-performance caching
- **MongoDB**: Document-based storage
- **PostgreSQL**: Relational database storage

### RAG (Retrieval Augmented Generation)
- Vector store integration (Chroma, FAISS)
- Document embedding and retrieval
- Context-aware responses
- Configurable similarity search

### Tools & Function Calling
- Web search integration
- Wikipedia queries
- Custom tool development
- Agent executor patterns

### Security & Content Filtering
- Integration with SecurityAgent
- Content moderation
- Threat detection
- Configurable thresholds

### Monitoring & Analytics
- Token usage tracking
- Cost estimation
- Response time metrics
- Conversation analytics
- User behavior insights

### Advanced Features
- Async/await support
- Streaming responses
- Multi-user session management
- Conversation export
- System health monitoring
- Error handling & recovery

## 📦 Installation

### Basic Installation
```bash
pip install -r requirements.txt
```

### Optional Dependencies
```bash
# For Redis backend
pip install redis

# For MongoDB backend
pip install pymongo

# For PostgreSQL backend
pip install psycopg2-binary

# For advanced embeddings
pip install sentence-transformers

# For vector stores
pip install chromadb faiss-cpu

# For additional LLM providers
pip install anthropic google-generativeai
```

## 🎯 Quick Start

### Basic Usage
```python
from ai_agents import create_basic_agent

# Create a basic agent
agent = create_basic_agent()

# Have a conversation
user_id = "user_123"
response = agent.invoke(user_id, "Hello! What can you do?")
print(response)

# Continue the conversation
response = agent.invoke(user_id, "Tell me more about your capabilities")
print(response)
```

### OpenAI Integration
```python
from ai_agents import create_openai_agent
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create OpenAI agent
agent = create_openai_agent(
    model="gpt-3.5-turbo",
    enable_rag=True,
    enable_tools=True,
    enable_security=True
)

user_id = "user_456"
response = agent.invoke(user_id, "Explain quantum computing")
print(response)
```

### Custom Configuration
```python
from ai_agents import AdvancedConversationAgent, AgentConfig, MemoryType, HistoryBackend, LLMProvider

config = AgentConfig(
    llm_provider=LLMProvider.OPENAI,
    model_name="gpt-4",
    memory_type=MemoryType.SUMMARY_BUFFER,
    history_backend=HistoryBackend.REDIS,
    redis_url="redis://localhost:6379",
    enable_rag=True,
    enable_tools=True,
    enable_security=True,
    enable_metrics=True,
    max_token_limit=2000,
    temperature=0.7
)

agent = AdvancedConversationAgent(config)
```

## 🔧 Configuration Options

### AgentConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_provider` | LLMProvider | FAKE | LLM provider to use |
| `model_name` | str | "gpt-3.5-turbo" | Model name |
| `temperature` | float | 0.7 | Response randomness |
| `max_tokens` | int | None | Max tokens per response |
| `streaming` | bool | False | Enable streaming |
| `memory_type` | MemoryType | SUMMARY_BUFFER | Memory management type |
| `history_backend` | HistoryBackend | IN_MEMORY | History storage backend |
| `max_token_limit` | int | 2000 | Token limit for memory |
| `enable_rag` | bool | False | Enable RAG capabilities |
| `enable_tools` | bool | False | Enable tool integration |
| `enable_security` | bool | False | Enable security filtering |
| `enable_metrics` | bool | True | Enable metrics tracking |

## 💾 Memory Types Explained

### Buffer Memory
Stores the complete conversation history without summarization.
```python
config = AgentConfig(memory_type=MemoryType.BUFFER)
```

**Pros**: Complete context preservation  
**Cons**: Token usage grows indefinitely  
**Use Case**: Short conversations, debugging

### Summary Memory
Keeps only a running summary of the conversation.
```python
config = AgentConfig(memory_type=MemoryType.SUMMARY)
```

**Pros**: Constant memory usage  
**Cons**: Loss of specific details  
**Use Case**: Long conversations, resource-constrained environments

### Summary Buffer Memory (Recommended)
Hybrid approach that keeps recent messages and summarizes older ones.
```python
config = AgentConfig(
    memory_type=MemoryType.SUMMARY_BUFFER,
    max_token_limit=2000
)
```

**Pros**: Balance between context and efficiency  
**Cons**: Some detail loss in older messages  
**Use Case**: Most production applications

### Entity Memory
Tracks and remembers entities (people, places, things) across conversations.
```python
config = AgentConfig(memory_type=MemoryType.ENTITY)
```

**Pros**: Excellent for relationship tracking  
**Cons**: Higher computational overhead  
**Use Case**: Customer service, personal assistants

## 🗄️ History Backends

### In-Memory (Default)
```python
config = AgentConfig(history_backend=HistoryBackend.IN_MEMORY)
```
- Fastest performance
- No persistence
- Lost on restart

### File-Based
```python
config = AgentConfig(
    history_backend=HistoryBackend.FILE,
    file_storage_path="./chat_histories"
)
```
- Simple persistence
- Good for development
- Limited scalability

### Redis
```python
config = AgentConfig(
    history_backend=HistoryBackend.REDIS,
    redis_url="redis://localhost:6379"
)
```
- High performance
- Distributed caching
- Automatic expiration

### MongoDB
```python
config = AgentConfig(
    history_backend=HistoryBackend.MONGODB,
    mongodb_connection="mongodb://localhost:27017/chatbot"
)
```
- Document-based storage
- Rich querying capabilities
- Horizontal scaling

### PostgreSQL
```python
config = AgentConfig(
    history_backend=HistoryBackend.POSTGRESQL,
    postgres_connection="postgresql://user:pass@localhost/chatbot"
)
```
- ACID compliance
- Complex queries
- Enterprise-grade reliability

## 🔍 RAG Implementation

### Basic RAG Setup
```python
from langchain_core.documents import Document

config = AgentConfig(
    enable_rag=True,
    vector_store_path="./vector_store"
)
agent = AdvancedConversationAgent(config)

# Add documents
documents = [
    Document(page_content="Your company policy document..."),
    Document(page_content="Product documentation..."),
]
agent.add_documents_to_vector_store(documents)
```

### Custom Embeddings
```python
config = AgentConfig(
    enable_rag=True,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    top_k_documents=5
)
```

## 🛠️ Tools Integration

### Enable Built-in Tools
```python
config = AgentConfig(
    enable_tools=True,
    available_tools=["search", "wikipedia"]
)
```

### Custom Tool Development
```python
from langchain.tools import BaseTool

class CustomTool(BaseTool):
    name = "custom_calculator"
    description = "Performs custom calculations"
    
    def _run(self, query: str) -> str:
        # Your tool logic here
        return f"Calculated: {query}"

# Add to agent (requires custom implementation)
```

## 📊 Metrics and Analytics

### Basic Metrics
```python
agent = create_openai_agent(enable_metrics=True)

# After conversation
metrics = agent.get_user_metrics(user_id)
print(f"Messages: {metrics.total_messages}")
print(f"Tokens: {metrics.total_tokens_input + metrics.total_tokens_output}")
print(f"Cost: ${metrics.total_cost:.4f}")
print(f"Avg Response Time: {metrics.avg_response_time:.2f}s")
```

### System-wide Analytics
```python
all_metrics = agent.get_all_metrics()
system_status = agent.get_system_status()

print(f"Active users: {len(all_metrics)}")
print(f"Total sessions: {system_status['active_sessions']}")
```

## 🔒 Security Integration

### Enable Security Filtering
```python
config = AgentConfig(
    enable_security=True,
    content_filter_threshold=0.7
)
```

The agent will automatically filter harmful content using the SecurityAgent.

## ⚡ Async Operations

### Async Conversations
```python
import asyncio

async def async_chat():
    agent = create_basic_agent()
    response = await agent.ainvoke("user_id", "Hello!")
    return response

response = asyncio.run(async_chat())
```

### Streaming Responses
```python
agent = create_openai_agent(streaming=True)

for chunk in agent.stream("user_id", "Tell me a story"):
    print(chunk, end="")
```

## 📤 Data Export

### Export Conversations
```python
# Export as JSON
json_data = agent.export_conversation("user_id", format="json")

# Save to file
with open("conversation_export.json", "w") as f:
    f.write(json_data)
```

## 🚀 Production Deployment

### Enterprise Configuration
```python
from ai_agents import create_enterprise_agent

agent = create_enterprise_agent(
    postgres_connection="postgresql://user:pass@db:5432/prod",
    redis_url="redis://cache:6379",
    enable_rag=True,
    enable_tools=True,
    enable_security=True,
    enable_metrics=True,
    enable_caching=True
)
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "app.py"]
```

### Environment Variables
```bash
# Required for OpenAI
OPENAI_API_KEY=your-openai-key

# Optional for other providers
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key

# Database connections
REDIS_URL=redis://localhost:6379
MONGODB_CONNECTION=mongodb://localhost:27017/chatbot
POSTGRES_CONNECTION=postgresql://user:pass@localhost/chatbot
```

## 🧪 Testing

### Unit Tests
```python
import pytest
from ai_agents import create_basic_agent

def test_basic_conversation():
    agent = create_basic_agent()
    response = agent.invoke("test_user", "Hello")
    assert response is not None
    assert len(response) > 0

def test_memory_persistence():
    agent = create_basic_agent()
    agent.invoke("test_user", "My name is Alice")
    response = agent.invoke("test_user", "What's my name?")
    # Should remember the name (with proper LLM)
```

### Load Testing
```python
import concurrent.futures
import time

def load_test():
    agent = create_basic_agent()
    
    def single_request(user_id):
        return agent.invoke(f"user_{user_id}", "Hello")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(single_request, i) for i in range(100)]
        results = [f.result() for f in futures]
    
    duration = time.time() - start_time
    print(f"100 requests completed in {duration:.2f}s")
```

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install langchain langchain-community langchain-openai
   ```

2. **API Key Issues**
   ```python
   import os
   os.environ["OPENAI_API_KEY"] = "your-key"
   ```

3. **Memory Issues**
   ```python
   config = AgentConfig(max_token_limit=1000)  # Reduce limit
   ```

4. **Performance Issues**
   ```python
   config = AgentConfig(
       history_backend=HistoryBackend.REDIS,  # Faster backend
       enable_caching=True
   )
   ```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

config = AgentConfig(
    enable_logging=True,
    log_level="DEBUG"
)
```

## 📚 Advanced Examples

See `examples/advanced_agent_examples.py` for comprehensive examples covering:
- Multi-user sessions
- Different memory types
- RAG implementation
- Tool integration
- Async operations
- Error handling
- Performance optimization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the examples
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ using LangChain and modern AI technologies**
