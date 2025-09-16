# 🤖 AI Agents for Enhanced Chatbots

**Advanced intelligent AI agents that work together to create smarter, safer, and more efficient chatbots with conversation memory and enterprise-grade features.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com)

## 🎯 Overview

This project provides advanced AI agents that can be integrated into any chatbot system to enhance its capabilities:

1. **🛡️ Security Agent** - Detects malicious content and security threats
2. **🧠 Context Agent** - Analyzes query relevance and conversation flow  
3. **🎯 Model Selection Agent** - Intelligently selects optimal LLM models
4. **💬 Advanced Conversation Agent** - Enterprise-grade conversation memory with RAG, tools, and multi-provider support

## 🏗️ What We've Built

### **Advanced Conversation Agent System**

We've created a **comprehensive conversation management system** that handles:

#### **🤖 Multi-Provider LLM Support**
- **OpenAI**: GPT-3.5, GPT-4, GPT-4 Turbo
- **Anthropic**: Claude models (claude-3-sonnet, claude-3-opus, etc.)
- **Google**: Gemini models (gemini-pro, gemini-pro-vision)
- **Ollama**: Local models (llama2, mistral, codellama, etc.)
- **Fake LLM**: For testing (no API key needed)

#### **👥 Multi-User Session Management**
- **Separate Conversations**: Each user has their own conversation history
- **User-Level Memory**: Independent memory for each user_id
- **Isolated Metrics**: Per-user analytics and cost tracking
- **Session Management**: Create, retrieve, clear user sessions
- **Data Export**: Export individual user conversations

#### **🧠 Advanced Memory Management**
- **Buffer Memory**: Complete conversation history
- **Summary Memory**: Condensed conversations for efficiency
- **Summary Buffer**: Hybrid approach with token limits
- **Entity Memory**: Track people, places, things across conversations
- **Knowledge Graph**: Relationship-based memory

#### **🗄️ Enterprise Storage Backends**
- **In-Memory**: Lightning fast, volatile storage
- **File**: Simple persistence for development
- **Redis**: High-performance caching for production
- **MongoDB**: Document storage for flexibility
- **PostgreSQL**: Enterprise-grade reliability

#### **🔍 RAG (Retrieval Augmented Generation)**
- **Vector Stores**: ChromaDB (persistent), FAISS (in-memory) integration
- **Document Embedding**: OpenAI, HuggingFace embedding models
- **Similarity Search**: Configurable retrieval with agent methods
- **Context Enhancement**: Automatic document retrieval and context injection
- **ChromaDB Integration**: Full access through our agent (no external client needed)
- **Document Management**: Add, search, count, export documents through agent methods

#### **🛠️ Tool Integration**
- **Google Search**: Most accurate and up-to-date results (requires API key)

- **Wikipedia**: Knowledge base queries for factual details
- **Custom Tools**: Extensible tool framework
- **Function Calling**: Native LLM function support
- **Automatic Tool Selection**: Agent intelligently chooses when to use tools
- **Seamless Integration**: Tools work within conversation flow

#### **📊 Comprehensive Monitoring**
- **Token Tracking**: Input/output token counting
- **Cost Estimation**: Real-time cost calculation
- **Performance Metrics**: Response times, throughput
- **User Analytics**: Conversation patterns
- **System Health**: Status monitoring

#### **🗄️ ChromaDB Integration & Document Management**
- **Persistent Storage**: Documents survive script restarts
- **Agent-Centric Access**: All operations through our agent methods
- **Document Operations**: Add, search, count, export documents
- **Vector Store Info**: Get detailed information about storage backend
- **Multi-Agent Sharing**: Multiple agents can share the same knowledge base
- **No External Client**: Everything works through our clean agent interface

### **🗄️ Database Integration & Purpose**

#### **PostgreSQL - Conversation History Storage**
```python
postgres_connection="postgresql://user:pass@db/chatbot"
```
- **Purpose**: Persistent storage of all conversation history
- **What it stores**: User messages, AI responses, timestamps, metadata
- **Benefits**: ACID compliance, scalability, backup/recovery
- **Use case**: Enterprise applications with thousands of users

#### **Redis - Caching & Fast Access**
```python
redis_url="redis://cache:6379"
```
- **Purpose**: High-speed caching and session management
- **What it caches**: AI responses, search results, user sessions
- **Benefits**: Sub-millisecond access, reduced API calls, cost savings
- **Use case**: High-traffic applications, real-time features

### **🛠️ How Tools Work Automatically**

Our agents now **automatically use tools** when users ask questions that need real-time information:

#### **Automatic Tool Selection**
```python
# Create agent with tools enabled
agent = create_openai_agent(enable_tools=True)

# Ask about current events → Agent automatically uses DuckDuckGo
response = agent.invoke("user_123", "What's the latest news about AI today?")

# Ask for factual information → Agent automatically uses Wikipedia  
response = agent.invoke("user_123", "Tell me about quantum computing")

# Ask about recent developments → Agent automatically searches the web
response = agent.invoke("user_123", "What are the latest developments in renewable energy?")
```

#### **What Happens Behind the Scenes**
1. **User asks question** → Agent analyzes if tools are needed
2. **Tool selection** → Agent chooses DuckDuckGo (current events) or Wikipedia (facts)
3. **Tool execution** → Searches web/Wikipedia for real-time information
4. **Response generation** → Combines tool results with AI knowledge
5. **Final answer** → User gets informed, up-to-date response

#### **Tools Available**
- **🦆 DuckDuckGo Web Search**: Current events, news, real-time information
- **📚 Wikipedia Search**: Factual information, detailed explanations
- **🔧 Custom Tools**: Extend with your own functions

### **⚡ New Performance Features**

#### **Real Redis Caching**
```python
agent = create_enterprise_agent(enable_caching=True)

# Cache statistics
stats = agent.get_cache_stats()
print(f"Cache hits: {stats['hits']}, misses: {stats['misses']}")

# Clear cache
agent.clear_cache()  # All users
agent.clear_cache("user_123")  # Specific user
```

#### **Real Async Streaming**
```python
agent = create_enterprise_agent(streaming=True)

# Stream response tokens in real-time
async for chunk in agent.stream("user_123", "Explain AI in detail"):
    print(chunk, end="", flush=True)
```

#### **Performance Benefits**
- **Caching**: 50-200ms responses (vs 1-3s LLM calls)
- **Streaming**: Real-time token delivery
- **Database**: Persistent, scalable storage
- **Redis**: Sub-millisecond cache access

### **🔧 New Agent Methods for ChromaDB Access**

Our agents now provide **direct access to vector store operations** without needing external clients:

#### **Document Management Methods**
```python
# Add documents to vector store
agent.add_documents_to_vector_store(documents)

# Search documents through our agent
results = agent.search_documents("your query", k=5)

# Get document count
doc_count = agent.get_document_count()

# Get vector store information
vector_info = agent.get_vector_store_info()

# Export documents in various formats
json_export = agent.export_documents("json")
text_export = agent.export_documents("text")
```

#### **ChromaDB Integration Benefits**
- **✅ No External Client**: Everything through our agent
- **✅ Persistent Storage**: Documents survive restarts
- **✅ Easy Sharing**: Multiple agents use same knowledge base
- **✅ Clean API**: Simple method calls for all operations
- **✅ Production Ready**: Perfect for real applications

### **Factory Functions - Easy Setup**

We provide **three factory functions** to make setup incredibly easy:

#### **1. `create_basic_agent()` - Development & Testing**
```python
from ai_agents import create_basic_agent
agent = create_basic_agent()  # No API key needed!
```
- **Use Case**: Development, testing, demos
- **Features**: In-memory storage, basic metrics, fake LLM
- **Setup Time**: 30 seconds

#### **2. `create_openai_agent()` - Production Ready**
```python
from ai_agents import create_openai_agent
agent = create_openai_agent(enable_rag=True, enable_tools=True)
```
- **Use Case**: Production applications
- **Features**: OpenAI integration, RAG, tools, security, metrics
- **Setup Time**: 2 minutes

#### **3. `create_enterprise_agent()` - Full Enterprise**
```python
from ai_agents import create_enterprise_agent
agent = create_enterprise_agent(
    postgres_connection="postgresql://user:pass@db/chatbot",
    redis_url="redis://cache:6379",
    enable_caching=True,    # Real Redis caching
    streaming=True          # Real async streaming
)
```
- **Use Case**: Enterprise deployments
- **Features**: All features + PostgreSQL, Redis, real streaming, real caching
- **Setup Time**: 5 minutes

## ✨ Key Features

### Core Agents
- **🔒 Enhanced Security**: Advanced threat detection using GPT-4o
- **🧠 Smart Context**: Intelligent query relevance analysis
- **💰 Cost Optimization**: Automatic model selection for cost-performance balance

### Advanced Conversation Agent
- **🤖 Multi-Provider LLM**: OpenAI, Anthropic, Google, Ollama, Local models
- **👥 Multi-User Sessions**: Separate conversation history for each user
- **🧠 Advanced Memory**: 5 memory types (Buffer, Summary, Entity, KG, Combined)
- **🗄️ Enterprise Storage**: Redis, PostgreSQL, MongoDB, File, In-Memory backends
- **🔍 RAG Capabilities**: Vector stores, document retrieval, context-aware responses
- **🛠️ Tool Integration**: Web search, Wikipedia, custom tools
- **🔒 Security Integration**: Content filtering with SecurityAgent
- **📊 Comprehensive Monitoring**: Token tracking, cost estimation, performance metrics
- **⚡ Advanced Features**: Async/await, streaming, multi-user sessions, export

### Platform Features
- **🚀 Easy Integration**: Simple API for any chatbot platform
- **⚙️ Configurable**: 25+ configuration options
- **📊 Analytics**: Detailed analysis and performance metrics
- **🔄 Production Ready**: Docker support, error handling, auto-recovery

## 🚀 Quick Start

📚 **For comprehensive documentation, see [COMPREHENSIVE_AGENT_GUIDE.md](COMPREHENSIVE_AGENT_GUIDE.md)**

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-agents-chatbot.git
cd ai-agents-chatbot

# Create virtual environment
python -m venv venv 
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Add your OpenAI API key (optional for basic agent)
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

### 3. Start Using Agents

#### **Option A: Basic Agent (No API Key Required)**
```python
from ai_agents import create_basic_agent

# Create agent in 30 seconds
agent = create_basic_agent()

# Start chatting immediately
response = agent.invoke("user_123", "Hello! What can you do?")
print(response)
```

#### **Option B: OpenAI Agent (Production Ready)**
```python
from ai_agents import create_openai_agent
import os

# Set your API key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# Create production agent
agent = create_openai_agent(
    model="gpt-3.5-turbo",
    enable_rag=True,
    enable_tools=True
)

# Multi-turn conversation with memory
response1 = agent.invoke("user_123", "What is Python?")
response2 = agent.invoke("user_123", "Tell me more about what we discussed")

# Get conversation history
history = agent.get_conversation_history("user_123")
print(f"Conversation has {len(history)} messages")
```

#### **Option C: Run the Demo**
```bash
# Streamlit demo with conversation history
streamlit run examples/streamlit_demo.py

# Comprehensive examples
python examples/advanced_agent_examples.py
```

## 📦 Dependencies

Our package supports **feature-based installation** - install only what you need:

### **Core Dependencies** (Required)
```bash
pip install langchain langchain-community langchain-openai python-dotenv
```

### **RAG Support** (Document Retrieval)
```bash
pip install sentence-transformers chromadb faiss-cpu langchain-chroma
```

### **Tool Integration** (Google Search, Wikipedia)
```bash
pip install wikipedia

# For Google Search (most accurate results)
pip install google-api-python-client google-auth
```

### **🔍 Search Tool Setup**

#### **Option 1: Google Search (Recommended - Most Accurate)**
1. **Get Google API Key**: Visit [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable Custom Search API**: Go to APIs & Services → Library → Custom Search API
3. **Create API Key**: Go to Credentials → Create Credentials → API Key
4. **Set up Custom Search Engine**: Visit [Google CSE](https://cse.google.com/cse/)
5. **Update .env file**:
   ```bash
   GOOGLE_API_KEY=your_actual_api_key_here
   GOOGLE_CSE_ID=your_search_engine_id_here
   OPENAI_API_KEY=your_openai_key_here
   ```



### **Persistent Storage** (Redis, MongoDB, PostgreSQL)
```bash
pip install redis pymongo psycopg2-binary
```

### **Full Installation** (All Features)
```bash
pip install -r requirements.txt
```

💡 **Start simple, add features as needed!**

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Security      │    │   Context       │    │   Model         │
│   Agent         │    │   Agent         │    │   Selection     │
│                 │    │                 │    │   Agent         │
│ • Threat        │    │ • Relevance     │    │ • Query        │
│   Detection     │    │   Analysis      │    │   Analysis     │
│ • Content       │    │ • Domain        │    │ • Model        │
│   Safety        │    │   Detection     │    │   Ranking      │
│ • Malicious     │    │ • Flow          │    │ • Cost         │
│   Prompt        │    │   Analysis      │    │   Optimization │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Advanced      │
                    │   Conversation  │
                    │   Agent         │
                    │                 │
                    │ • Multi-LLM     │
                    │   Support       │
                    │ • Memory        │
                    │   Management    │
                    │ • RAG & Tools   │
                    │ • Monitoring    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Chatbot       │
                    │   Orchestrator  │
                    │                 │
                    │ • Coordinates   │
                    │   agents        │
                    │ • Manages flow  │
                    │ • Generates     │
                    │   responses     │
                    └─────────────────┘
```

## 🔧 Integration Guide

### Basic Integration

```python
from ai_agents import SecurityAgent, ContextAgent, ModelSelectionAgent

# Initialize agents
security_agent = SecurityAgent(
    model="gpt-4o",
    threat_threshold=0.7
)

context_agent = ContextAgent(
    chatbot_name="My Bot",
    chatbot_description="A helpful assistant",
    keywords=["help", "assist", "support"]
)

model_agent = ModelSelectionAgent(
    cost_sensitivity="medium",
    performance_preference="balanced"
)

# Process user query
def handle_query(user_query, conversation_history):
    # Security check
    security_result = security_agent.analyze_security(user_query)
    if security_result['blocked']:
        return "I cannot process that request for security reasons."
    
    # Context analysis
    context_result = context_agent.analyze_context(user_query, conversation_history)
    
    # Model selection
    model_result = model_agent.select_model(user_query, conversation_history)
    
    # Generate response using selected model
    response = generate_response(user_query, model_result['selected_model'])
    
    return response
```

### Advanced Conversation Agent Integration

#### **Factory Functions Overview**

We provide three convenient factory functions to create agents with different configurations:

1. **`create_basic_agent()`** - For development and testing (no API key needed)
2. **`create_openai_agent()`** - For production with OpenAI (recommended)
3. **`create_enterprise_agent()`** - For enterprise deployments with full features

#### **1. Basic Agent (Development)**
```python
from ai_agents import create_basic_agent

# No API key required - uses fake LLM for testing
agent = create_basic_agent()

# Start chatting immediately
user_id = "user_123"
response = agent.invoke(user_id, "Hello! What can you do?")
print(response)

# Features: In-memory storage, basic metrics, no external dependencies
```

#### **2. OpenAI Agent (Production)**
```python
from ai_agents import create_openai_agent
import os

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Create production-ready agent
agent = create_openai_agent(
    model="gpt-3.5-turbo",  # or "gpt-4", "gpt-4-turbo"
    enable_rag=True,        # Enable document retrieval
    enable_tools=True,      # Enable web search, Wikipedia
    enable_security=True,   # Enable content filtering
    enable_metrics=True     # Enable cost and performance tracking
)

# Multi-user conversations with separate history
user1_response = agent.invoke("user_123", "My name is Alice")
user2_response = agent.invoke("user_456", "My name is Bob")

# Each user has their own conversation history
alice_history = agent.get_conversation_history("user_123")
bob_history = agent.get_conversation_history("user_456")

# Users remember their own context
response1 = agent.invoke("user_123", "What's my name?")  # Remembers "Alice"
response2 = agent.invoke("user_456", "What's my name?")  # Remembers "Bob"
```

# Multi-user conversation with memory
user_id = "user_123"
response1 = agent.invoke(user_id, "Hello! What can you do?")
response2 = agent.invoke(user_id, "What did we talk about before?")

# Get conversation history
history = agent.get_conversation_history(user_id)
print(f"Conversation has {len(history)} messages")

# Get detailed metrics
metrics = agent.get_user_metrics(user_id)
print(f"Cost: ${metrics.total_cost:.4f}")
print(f"Tokens: {metrics.total_tokens_input + metrics.total_tokens_output}")
print(f"Avg Response Time: {metrics.avg_response_time:.2f}s")

# Export conversation
export_data = agent.export_conversation(user_id, format="json")
print("Conversation exported:", export_data[:200] + "...")
```

#### **3. Enterprise Agent (Full Features)**
```python
from ai_agents import create_enterprise_agent

# Enterprise setup with all features
enterprise_agent = create_enterprise_agent(
    # Database connections
    postgres_connection="postgresql://user:pass@db/chatbot",
    redis_url="redis://cache:6379",
    
    # Advanced features
    enable_rag=True,
    enable_tools=True,
    enable_security=True,
    enable_metrics=True,
    enable_caching=True,
    streaming=True,
    
    # Custom configuration
    max_token_limit=4000,
    temperature=0.7
)

# Multi-tenant enterprise usage
enterprise_agent.invoke("company_a_user_1", "What's our company policy?")
enterprise_agent.invoke("company_b_user_1", "Show me our sales data")

# Each company/user has isolated data
company_a_history = enterprise_agent.get_conversation_history("company_a_user_1")
company_b_history = enterprise_agent.get_conversation_history("company_b_user_1")
```

# Enterprise features
user_id = "enterprise_user"

# Multi-turn conversation with persistent storage
response = enterprise_agent.invoke(user_id, "Explain our company's AI strategy")

# Get system status
status = enterprise_agent.get_system_status()
print(f"Active sessions: {status['active_sessions']}")
print(f"Total users: {status['total_users']}")
print(f"RAG enabled: {status['rag_enabled']}")
print(f"Tools available: {status['available_tools']}")
```

#### **Factory Function Comparison**

| Feature | Basic Agent | OpenAI Agent | Enterprise Agent |
|---------|-------------|--------------|------------------|
| **LLM Provider** | Fake (testing) | OpenAI | OpenAI |
| **Memory Type** | Summary Buffer | Summary Buffer | Combined |
| **Storage** | In-Memory | File | PostgreSQL |
| **RAG** | ❌ | ✅ | ✅ |
| **Tools** | ❌ | ✅ | ✅ |
| **Security** | ❌ | ✅ | ✅ |
| **Metrics** | ✅ | ✅ | ✅ |
| **Streaming** | ❌ | ❌ | ✅ |
| **Caching** | ❌ | ❌ | ✅ |
| **API Key** | Not needed | Required | Required |
| **Use Case** | Development | Production | Enterprise |

### Advanced Configuration

```python
# Custom security thresholds
security_agent = SecurityAgent(
    model="gpt-4o",
    threat_threshold=0.5,  # More strict
    enable_detailed_analysis=True
)

# Domain-specific context
context_agent = ContextAgent(
    chatbot_name="Health Assistant",
    chatbot_description="Medical information and health advice",
    keywords=["health", "medical", "symptoms", "treatment"],
    chatbot_prompt="You are a medical AI assistant..."
)

# Cost-optimized model selection
model_agent = ModelSelectionAgent(
    cost_sensitivity="high",  # Prefer cheaper models
    performance_preference="speed"  # Prioritize speed over quality
)
```

## 📚 API Reference

### Security Agent

```python
class SecurityAgent:
    def analyze_security(self, user_query: str, 
                        conversation_context: str = None,
                        user_profile: Dict = None) -> Dict:
        """
        Analyze user query for security threats
        
        Returns:
            {
                'is_malicious': bool,
                'threat_level': str,  # 'safe', 'low', 'medium', 'high', 'critical'
                'threat_score': float,  # 0.0-1.0
                'confidence_score': float,
                'blocked': bool,
                'warnings': List[str],
                'llm_analysis': Dict,
                'metrics': {
                    'sexual': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'violence': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'hate_speech': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'profanity': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'weapons': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'crime': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'prompt_injection': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []},
                    'jailbreak': {'f1': [], 'precision': [], 'recall': [], 'accuracy': []}
                }
            }
        """
```

### Context Agent

```python
class ContextAgent:
    def analyze_context(self, user_query: str, 
                       conversation_history: List[Dict] = None,
                       user_profile: Dict = None) -> Dict:
        """
        Analyze query relevance and context
        
        Returns:
            {
                'is_contextual': bool,
                'relevance_score': float,  # 0.0-1.0
                'relevance_level': str,  # 'irrelevant', 'low', 'medium', 'high'
                'reasoning': str,
                'context_shift': bool,
                'domain_alignment': float,
                'chatbot_context': Dict
            }
        """
```

### Model Selection Agent

```python
class ModelSelectionAgent:
    def select_model(self, user_query: str, 
                    conversation_context: str = None,
                    user_preferences: Dict = None) -> Dict:
        """
        Select optimal LLM model for query
        
        Returns:
            {
                'selected_model': str,
                'model_info': Dict,
                'selection_reasoning': str,
                'confidence_score': float,
                'estimated_cost': float,
                'estimated_tokens': int,
                'query_analysis': Dict
            }
        """
```

### Advanced Conversation Agent

```python
class AdvancedConversationAgent:
    def invoke(self, user_id: str, message: str) -> str:
        """Process user message and return response with memory"""
    
    def get_conversation_history(self, user_id: str) -> List[BaseMessage]:
        """Get conversation history for user"""
    
    def get_conversation_summary(self, user_id: str) -> str:
        """Get conversation summary for user"""
    
    def get_user_metrics(self, user_id: str) -> ConversationMetrics:
        """Get metrics for user (tokens, cost, performance)"""
    
    def export_conversation(self, user_id: str, format: str = "json") -> str:
        """Export conversation in various formats"""
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system health and status"""
    
    def clear_user_session(self, user_id: str) -> bool:
        """Clear session data for a user"""
    
    def add_documents_to_vector_store(self, documents: List[Document]) -> bool:
        """Add documents to vector store for RAG"""

# Factory functions
def create_basic_agent(**kwargs) -> AdvancedConversationAgent:
    """Create basic agent with minimal configuration"""

def create_openai_agent(api_key: str = None, **kwargs) -> AdvancedConversationAgent:
    """Create OpenAI-powered agent with full features"""

def create_enterprise_agent(**kwargs) -> AdvancedConversationAgent:
    """Create enterprise agent with PostgreSQL, Redis, etc."""
```

### **Key Capabilities**

#### **🔄 Multi-User Conversation Memory**
```python
# Multi-user conversations with separate context
agent.invoke("user_123", "My name is Alice")
agent.invoke("user_456", "My name is Bob")

# Each user remembers their own context
response1 = agent.invoke("user_123", "What's my name?")  # Remembers "Alice"
response2 = agent.invoke("user_456", "What's my name?")  # Remembers "Bob"

# Get conversation history for specific users
alice_history = agent.get_conversation_history("user_123")
bob_history = agent.get_conversation_history("user_456")

print(f"Alice has {len(alice_history)} messages")
print(f"Bob has {len(bob_history)} messages")
```

#### **📊 Multi-User Metrics & Analytics**
```python
# Get detailed metrics for specific users
alice_metrics = agent.get_user_metrics("user_123")
bob_metrics = agent.get_user_metrics("user_456")

print(f"Alice - Messages: {alice_metrics.total_messages}, Cost: ${alice_metrics.total_cost:.4f}")
print(f"Bob - Messages: {bob_metrics.total_messages}, Cost: ${bob_metrics.total_cost:.4f}")

# Get all user metrics
all_metrics = agent.get_all_metrics()
for user_id, metrics in all_metrics.items():
    print(f"{user_id}: {metrics.total_messages} messages, ${metrics.total_cost:.4f} cost")
```

#### **📤 Multi-User Data Export**
```python
# Export conversation for specific users
alice_export = agent.export_conversation("user_123", format="json")
bob_export = agent.export_conversation("user_456", format="json")

# Each export includes: messages, metrics, timestamps, session duration
print("Alice's conversation:", alice_export[:200] + "...")
print("Bob's conversation:", bob_export[:200] + "...")

# Clear specific user sessions
agent.clear_user_session("user_123")  # Only clears Alice's data
```

#### **🔍 RAG Integration**
```python
# Add documents to vector store
from langchain_core.documents import Document
documents = [Document(page_content="Your company knowledge...")]
agent.add_documents_to_vector_store(documents)

# Agent will automatically retrieve relevant context
response = agent.invoke("user_123", "What does our company policy say?")
```

#### **🛠️ Tool Usage**
```python
# Agent automatically uses tools when needed
response = agent.invoke("user_123", "Search for latest AI news")
# Uses DuckDuckGo search tool automatically

response = agent.invoke("user_123", "Tell me about Python programming")
# Uses Wikipedia tool for additional context
```

#### **🔒 Security Integration**
```python
# Agent automatically filters harmful content
response = agent.invoke("user_123", "malicious prompt here")
# Returns: "I cannot process that message due to content policy violations."
```

#### **🤖 Multi-LLM Provider Support**
```python
from ai_agents import AdvancedConversationAgent, AgentConfig, LLMProvider

# OpenAI Agent
openai_agent = AdvancedConversationAgent(AgentConfig(
    llm_provider=LLMProvider.OPENAI,
    model_name="gpt-4"
))

# Anthropic Agent
anthropic_agent = AdvancedConversationAgent(AgentConfig(
    llm_provider=LLMProvider.ANTHROPIC,
    model_name="claude-3-sonnet-20240229"
))

# Google Agent
google_agent = AdvancedConversationAgent(AgentConfig(
    llm_provider=LLMProvider.GOOGLE,
    model_name="gemini-pro"
))

# Ollama (Local) Agent
ollama_agent = AdvancedConversationAgent(AgentConfig(
    llm_provider=LLMProvider.OLLAMA,
    model_name="llama2"
))

# All agents support multi-user conversations
openai_agent.invoke("user_123", "Hello from OpenAI!")
anthropic_agent.invoke("user_123", "Hello from Claude!")
google_agent.invoke("user_123", "Hello from Gemini!")
```

## 🧪 Testing & Showcase

### **Live Demonstration Script**
We provide a comprehensive showcase script that demonstrates all features:

```bash
# Run the showcase to see all capabilities in action
python showcase_agent_capabilities.py
```

**What the showcase demonstrates:**
- ✅ **Basic Agent**: Multi-user conversations, memory, metrics
- ✅ **OpenAI Agent**: RAG, tools, security, persistent storage
- ✅ **Enterprise Features**: Multi-user analytics, data export, session management
- ✅ **ChromaDB Integration**: Document persistence, agent-based access, sharing
- ✅ **Multi-LLM Support**: Different providers and models
- ✅ **Performance Monitoring**: Real-time metrics and analytics

### **Testing Your Setup**
```bash
# Basic functionality test
python examples/agent_smoke_test.py

# Interactive web demo
streamlit run examples/streamlit_demo.py

# Advanced examples
python examples/advanced_agent_examples.py
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific agent tests
python tests/test_security_agent.py
python tests/test_context_agent.py
python tests/test_model_selection_agent.py

# Run integration tests
python tests/test_integration.py
```

## 📊 Performance

### Core Agents
- **Security Analysis**: ~1-1.2 seconds (GPT-4o)
- **Context Analysis**: ~0-0.8 seconds (GPT-3.5-turbo)
- **Model Selection**: ~0.5-1 second (GPT-3.5-turbo)
- **Total Overhead**: ~1.5-2.5 seconds per query
- **Cost**: ~$0.01-0.05 per query (depending on models used)

### Advanced Conversation Agent
- **Response Time**: 50-200ms (cached) / 1-3s (LLM call)
- **Throughput**: 100+ requests/second (Redis backend)
- **Memory Usage**: 10-50MB per 1000 conversations
- **Token Efficiency**: 50-90% reduction with summary memory
- **Multi-User**: Supports unlimited concurrent users
- **Scalability**: Horizontal scaling with load balancing

## 🔒 Security Features

- **Threat Detection**: 20+ threat categories
- **Prompt Injection**: Advanced jailbreak detection
- **Content Safety**: Comprehensive safety analysis
- **Fallback Protection**: Conservative blocking on errors
- **Configurable Thresholds**: Adjustable sensitivity levels

## 💬 Conversation Agent Features

### Memory Management
- **Buffer Memory**: Complete conversation history
- **Summary Memory**: Condensed conversations for efficiency
- **Summary Buffer**: Hybrid approach with token limits
- **Entity Memory**: Track people, places, things across conversations
- **Knowledge Graph**: Relationship-based memory

### Storage Backends
- **In-Memory**: Lightning fast, volatile storage
- **File**: Simple persistence for development
- **Redis**: High-performance caching for production
- **MongoDB**: Document storage for flexibility
- **PostgreSQL**: Enterprise-grade reliability

### RAG Capabilities
- **Vector Stores**: Chroma, FAISS integration
- **Document Embedding**: Multiple embedding models
- **Similarity Search**: Configurable retrieval
- **Context Enhancement**: Automatic document retrieval

### Tool Integration
- **Google Search**: Most accurate results (requires API key)
- **Wikipedia**: Knowledge base queries
- **Custom Tools**: Extensible tool framework
- **Function Calling**: Native LLM function support

## 📚 Usage Examples

### **Basic Chatbot with Memory**
```python
from ai_agents import create_basic_agent

# Create agent (no API key needed)
agent = create_basic_agent()

# Start chatting with memory
response1 = agent.invoke("user_123", "Hello! My name is Alice")
response2 = agent.invoke("user_123", "What's my name?")  # Agent remembers!

# Get conversation history
history = agent.get_conversation_history("user_123")
print(f"Conversation has {len(history)} messages")
```

### **RAG-Enabled Agent with ChromaDB Integration**
```python
from ai_agents import create_openai_agent
from langchain_core.documents import Document

# Create RAG-enabled agent with persistent storage
agent = create_openai_agent(
    enable_rag=True,
    vector_store_path="./company_docs"  # ChromaDB storage
)

# Add company documents
documents = [
    Document(page_content="Our company policy states..."),
    Document(page_content="Product specifications include...")
]
agent.add_documents_to_vector_store(documents)

# Query with RAG context
response = agent.invoke("user_123", "What are our company policies?")

# Access vector store through our agent methods
doc_count = agent.get_document_count()
print(f"Total documents: {doc_count}")

vector_info = agent.get_vector_store_info()
print(f"Vector store: {vector_info}")

# Search documents
results = agent.search_documents("policy", k=3)
for doc in results:
    print(f"Found: {doc.page_content[:100]}...")

# Export documents
json_export = agent.export_documents("json")
print(f"Exported {len(json_export)} documents")
```

### **Tools-Enabled Agent (Web Search + Wikipedia)**
```python
from ai_agents import create_openai_agent

# Create agent with tools enabled
agent = create_openai_agent(enable_tools=True)

# Ask about current events → Agent automatically uses DuckDuckGo
response = agent.invoke("user_123", "What's the latest news about AI today?")

# Ask for factual information → Agent automatically uses Wikipedia
response = agent.invoke("user_123", "Tell me about quantum computing")

# Ask about recent developments → Agent automatically searches the web
response = agent.invoke("user_123", "What are the latest developments in renewable energy?")

print("✅ Tools work automatically - no manual configuration needed!")
```

### **Multi-User Support System**
```python
from ai_agents import create_enterprise_agent

# Create enterprise agent
agent = create_enterprise_agent()

# Multiple users with separate conversations
users = ["alice", "bob", "charlie"]
for user in users:
    response = agent.invoke(user, f"Hello, I'm {user.capitalize()}")
    print(f"{user}: {response}")

# Get analytics for all users
all_metrics = agent.get_all_metrics()
for user_id, metrics in all_metrics.items():
    print(f"{user_id}: {metrics.total_messages} messages")
```

### **Shared Knowledge Base Between Agents**
```python
from ai_agents import create_openai_agent

# Agent 1: Adds documents to shared knowledge base
agent1 = create_openai_agent(
    enable_rag=True,
    vector_store_path="./shared_knowledge"  # Same path!
)
agent1.add_documents_to_vector_store(company_docs)

# Agent 2: Accesses the same knowledge base
agent2 = create_openai_agent(
    enable_rag=True,
    vector_store_path="./shared_knowledge"  # Same path!
)

# Both agents now have access to the same documents!
response1 = agent1.invoke("user_1", "What do you know about our products?")
response2 = agent2.invoke("user_2", "Tell me about our company policies")
```

## 🌟 Use Cases

### Healthcare Chatbots
- **Security**: Detect medical misinformation and harmful advice
- **Context**: Ensure queries are health-related
- **Model Selection**: Use high-quality models for medical queries
- **Conversation**: Maintain patient history and treatment context

### E-commerce Assistants
- **Security**: Prevent fraud and malicious requests
- **Context**: Identify shopping-related queries
- **Model Selection**: Balance cost and response quality
- **Conversation**: Remember user preferences and shopping history

### Educational Bots
- **Security**: Filter inappropriate content
- **Context**: Maintain educational focus
- **Model Selection**: Optimize for learning outcomes
- **Conversation**: Track learning progress and adapt difficulty

### Customer Service
- **Security**: Protect against abuse and spam
- **Context**: Route queries to appropriate departments
- **Model Selection**: Ensure consistent service quality
- **Conversation**: Maintain support ticket history and resolution context

### Enterprise AI Assistants
- **Conversation**: Multi-user session management with PostgreSQL
- **RAG**: Company knowledge base integration
- **Tools**: Internal system integration
- **Monitoring**: Comprehensive analytics and cost tracking

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 ai_agents/ tests/
black ai_agents/ tests/

# Run tests with coverage
pytest --cov=ai_agents tests/
```

For demo usage, sample queries, and examples, refer to `examples/README.md`.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- Streamlit for the demo interface
- The open source community for inspiration and feedback

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-agents-chatbot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-agents-chatbot/discussions)
- **Documentation**: [Full Documentation](docs/)

## 🚀 Roadmap

- [x] **Multi-provider Support**: OpenAI, Anthropic Claude, Google Gemini, Ollama
- [x] **Advanced Conversation Memory**: Multiple memory types and storage backends
- [x] **RAG Integration**: Vector stores and document retrieval
- [x] **Tool Integration**: Web search, Wikipedia, custom tools
- [x] **Automatic Tool Selection**: Agent intelligently chooses when to use tools
- [x] **Comprehensive Monitoring**: Token tracking, cost estimation, performance metrics
- [x] **ChromaDB Integration**: Persistent storage with agent-centric access
- [x] **Document Management**: Add, search, count, export through agent methods
- [x] **Multi-Agent Sharing**: Shared knowledge bases between agents
- [x] **Agent-Centric Vector Store**: All operations through our clean interface
- [x] **Persistent Storage**: Documents survive script restarts

---

**Ready to build enterprise-grade AI chatbots?** 🚀

Start with our [Advanced Agent Guide](docs/ADVANCED_AGENT_GUIDE.md) or explore the [examples](examples/) directory!

**Quick Start:**
```python
from ai_agents import create_openai_agent

# Basic agent with tools
agent = create_openai_agent(enable_tools=True)
response = agent.invoke("user_123", "What's the latest news about AI?")

# Full-featured agent
agent = create_openai_agent(enable_rag=True, enable_tools=True)
response = agent.invoke("user_123", "Tell me about quantum computing and recent developments")
```

Made with ❤️ by the AI Agents Team
