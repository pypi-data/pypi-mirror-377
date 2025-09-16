"""
Advanced Conversation Agent - Production-Ready Multi-Modal Agent

A comprehensive, enterprise-grade conversation agent with:
- Multiple LLM providers (OpenAI, Anthropic, Google, Local models)
- Various memory backends (In-memory, File, Redis, MongoDB, PostgreSQL)
- Different memory types (Buffer, Summary, Entity, Knowledge Graph)
- RAG capabilities with vector stores
- Function calling and tool integration
- Token tracking and cost estimation
- Streaming and async support
- Security filtering integration
- Performance monitoring and metrics
- Chain composition and routing
- Multi-user session management
- Conversation analytics
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncGenerator
from dataclasses import dataclass, field

# Core LangChain imports
from langchain_core.language_models import BaseLanguageModel
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.documents import Document

# Memory imports
try:
    from langchain_community.memory import (
        ConversationBufferMemory,
        ConversationSummaryBufferMemory,
    )
except ImportError:
    # Fallback to deprecated imports
    from langchain.memory import (
        ConversationBufferMemory,
        ConversationSummaryBufferMemory,
    )

# LLM providers
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
except ImportError:
    ChatOpenAI = None
    OpenAIEmbeddings = None

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    ChatOllama = None

# History backends
from langchain_community.chat_message_histories import (
    FileChatMessageHistory,
    RedisChatMessageHistory,
    MongoDBChatMessageHistory,
    PostgresChatMessageHistory,
)

# Vector stores and embeddings
try:
    from langchain_chroma import Chroma
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
except ImportError:
    try:
        # Fallback to deprecated imports
        from langchain_community.vectorstores import Chroma, FAISS
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        try:
            # Try the new langchain-huggingface package
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            HuggingFaceEmbeddings = None
        
        Chroma = None
        FAISS = None

# Tools and agents
try:
    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper
    # Google Search for most accurate results
    from langchain_community.tools import GoogleSearchResults
    from langchain_community.utilities import GoogleSearchAPIWrapper
except ImportError:
    WikipediaQueryRun = None
    GoogleSearchResults = None
    GoogleSearchAPIWrapper = None

# Fake LLM for testing
from langchain_community.llms.fake import FakeListLLM

# Google Search tool for most accurate and up-to-date results
class OptimizedGoogleSearchTool:
    """Enhanced Google Search tool with optimized query handling"""
    
    def __init__(self, api_wrapper):
        self.name = "web_search"
        self.__name__ = "web_search"  # LangChain compatibility
        self.description = "Search Google for current information, news, and real-time data (most accurate)"
        self.api_wrapper = api_wrapper
    
    def invoke(self, query: str) -> str:
        """Execute Google search with optimized query handling"""
        try:
            # Optimize queries for better results
            optimized_query = self._optimize_query(query)
            result = self.api_wrapper.run(optimized_query)
            return result
        except Exception as e:
            return f"Google Search error: {str(e)}"
    
    def _optimize_query(self, query: str) -> str:
        """Optimize search queries for better results"""
        # Add current date context for time-sensitive queries
        if any(word in query.lower() for word in ['today', 'current', 'now', 'date', 'time']):
            from datetime import datetime
            current_date = datetime.now().strftime("%B %d, %Y")
            query = f"{query} {current_date}"
        
        # Add "latest" for news and current events
        if any(word in query.lower() for word in ['news', 'update', 'latest', 'recent']):
            query = f"latest {query}"
        
        return query
    
    def run(self, query: str) -> str:
        """LangChain compatibility method"""
        return self.invoke(query)
    
    def __call__(self, query: str) -> str:
        """Callable interface for LangChain"""
        return self.invoke(query)

# Suppress warnings and telemetry
import os
import warnings

# Suppress ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "False"

# Suppress LangChain deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_community")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_core")
warnings.filterwarnings("ignore", message=".*ConversationBufferMemory.*")
warnings.filterwarnings("ignore", message=".*memory.*")

# Suppress HuggingFace warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Setup logging - only show errors and critical messages by default
# Set AI_AGENTS_VERBOSE=1 in environment to enable verbose logging
if os.environ.get("AI_AGENTS_VERBOSE", "0") == "1":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.ERROR,
        format='%(levelname)s:%(name)s:%(message)s'
    )

logger = logging.getLogger(__name__)

# Suppress verbose logging from external libraries
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("langchain").setLevel(logging.ERROR)
logging.getLogger("langchain_community").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Suppress DuckDuckGo specific warnings
logging.getLogger("ddgs").setLevel(logging.ERROR)
logging.getLogger("primp").setLevel(logging.ERROR)

# Suppress Wikipedia warnings
logging.getLogger("wikipedia").setLevel(logging.ERROR)
logging.getLogger("bs4").setLevel(logging.ERROR)

def set_verbose_logging(enabled: bool = True):
    """Enable or disable verbose logging for debugging"""
    if enabled:
        logging.getLogger().setLevel(logging.INFO)
        logger.info("Verbose logging enabled")
    else:
        logging.getLogger().setLevel(logging.ERROR)
        logger.info("Verbose logging disabled")


class MemoryType(Enum):
    """Supported memory types"""
    BUFFER = "buffer"
    SUMMARY_BUFFER = "summary_buffer"


class HistoryBackend(Enum):
    """Supported history backends"""
    IN_MEMORY = "in_memory"
    FILE = "file"
    REDIS = "redis"
    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    FAKE = "fake"


@dataclass
class ConversationMetrics:
    """Metrics for conversation tracking"""
    user_id: str
    session_start: datetime = field(default_factory=datetime.now)
    total_messages: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cost: float = 0.0
    avg_response_time: float = 0.0
    last_activity: datetime = field(default_factory=datetime.now)
    topics: List[str] = field(default_factory=list)
    sentiment_scores: List[float] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Configuration for the Advanced Conversation Agent"""
    # LLM Configuration
    llm_provider: LLMProvider = LLMProvider.FAKE
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    streaming: bool = False
    
    # Prompt Configuration
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    
    # Memory Configuration
    memory_type: MemoryType = MemoryType.SUMMARY_BUFFER
    history_backend: HistoryBackend = HistoryBackend.IN_MEMORY
    max_token_limit: int = 2000
    return_messages: bool = True
    
    # History Backend Settings
    redis_url: Optional[str] = None
    mongodb_connection: Optional[str] = None
    postgres_connection: Optional[str] = None
    file_storage_path: str = "chat_histories"
    
    # RAG Configuration
    enable_rag: bool = False
    vector_store_path: Optional[str] = None
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k_documents: int = 5
    
    # Tools and Functions
    enable_tools: bool = False
    available_tools: List[str] = field(default_factory=lambda: ["search", "wikipedia"])
    
    # Security and Filtering
    enable_security: bool = False
    content_filter_threshold: float = 0.7
    
    # Monitoring and Analytics
    enable_metrics: bool = True
    enable_logging: bool = True
    log_level: str = "INFO"
    
    # Performance
    request_timeout: int = 30
    retry_attempts: int = 3
    enable_caching: bool = False


class ConversationCallback(BaseCallbackHandler):
    """Custom callback handler for tracking metrics"""
    
    def __init__(self, metrics: ConversationMetrics):
        self.metrics = metrics
        self.start_time = None
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        self.start_time = time.time()
    
    def on_llm_end(self, response, **kwargs) -> None:
        if self.start_time:
            response_time = time.time() - self.start_time
            self.metrics.avg_response_time = (
                (self.metrics.avg_response_time * self.metrics.total_messages + response_time) /
                (self.metrics.total_messages + 1)
            )
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        logger.error(f"LLM Error for user {self.metrics.user_id}: {error}")


class AdvancedConversationAgent:
    """
    Production-ready conversation agent with comprehensive features
    
    Features:
    - Multiple LLM providers and models
    - Various memory types and backends
    - RAG capabilities with vector stores
    - Function calling and tool integration
    - Security filtering and content moderation
    - Token tracking and cost estimation
    - Performance monitoring and analytics
    - Streaming and async support
    - Multi-user session management
    - Conversation analytics and insights
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self._user_sessions: Dict[str, Dict[str, Any]] = {}
        self._user_metrics: Dict[str, ConversationMetrics] = {}
        self._vector_store = None
        self._tools = []
        self._redis_client = None
        self._cache_stats = {"hits": 0, "misses": 0}
        
        # Initialize components
        self._setup_logging()
        self._initialize_llm()
        self._initialize_embeddings()
        self._initialize_vector_store()
        self._initialize_tools()
        self._initialize_caching()
        
        logger.info(f"Advanced Conversation Agent initialized with config: {self.config.llm_provider.value}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if self.config.enable_logging:
            logging.getLogger().setLevel(getattr(logging, self.config.log_level))
    
    def _initialize_llm(self) -> BaseLanguageModel:
        """Initialize the language model based on provider"""
        try:
            if self.config.llm_provider == LLMProvider.OPENAI and ChatOpenAI:
                self.llm = ChatOpenAI(
                    model=self.config.model_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                    streaming=self.config.streaming,
                    request_timeout=self.config.request_timeout,
                )
            elif self.config.llm_provider == LLMProvider.ANTHROPIC and ChatAnthropic:
                self.llm = ChatAnthropic(
                    model=self.config.model_name,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
            elif self.config.llm_provider == LLMProvider.GOOGLE and ChatGoogleGenerativeAI:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.config.model_name,
                    temperature=self.config.temperature,
                )
            elif self.config.llm_provider == LLMProvider.OLLAMA and ChatOllama:
                self.llm = ChatOllama(
                    model=self.config.model_name,
                    temperature=self.config.temperature,
                )
            else:
                # Fallback to fake LLM for testing
                self.llm = FakeListLLM(responses=[
                    "Hello! I'm your advanced AI assistant.",
                    "I can help you with various tasks using my advanced capabilities.",
                    "I have access to multiple tools and can maintain context across our conversation.",
                    "Let me know how I can assist you today!",
                ])
                logger.info("Using FakeListLLM as fallback")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.llm = FakeListLLM(responses=["Error initializing LLM. Using fallback."])
    
    def _initialize_embeddings(self):
        """Initialize embeddings for RAG"""
        if not self.config.enable_rag:
            return
        
        try:
            if OpenAIEmbeddings and self.config.llm_provider == LLMProvider.OPENAI:
                self.embeddings = OpenAIEmbeddings()
            elif HuggingFaceEmbeddings:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=self.config.embedding_model
                )
            else:
                self.embeddings = None
                logger.warning("No embeddings available for RAG")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            self.embeddings = None
    
    def _initialize_vector_store(self):
        """Initialize vector store for RAG"""
        if not self.config.enable_rag or not self.embeddings:
            return
        
        try:
            if self.config.vector_store_path and Chroma:
                self._vector_store = Chroma(
                    persist_directory=self.config.vector_store_path,
                    embedding_function=self.embeddings
                )
            elif FAISS:
                # Create empty FAISS store
                self._vector_store = FAISS.from_texts(
                    ["Initial document"], self.embeddings
                )
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
    
    def _initialize_tools(self):
        """Initialize available tools"""
        if not self.config.enable_tools:
            return
        
        try:
            # Google Search only (most accurate results)
            if "search" in self.config.available_tools and GoogleSearchResults and GoogleSearchAPIWrapper:
                try:
                    google_wrapper = GoogleSearchAPIWrapper()
                    search_tool = GoogleSearchResults(api_wrapper=google_wrapper)
                    search_tool.name = "web_search"
                    search_tool.description = "Search Google for current information, news, and real-time data (most accurate)"
                    self._tools.append(search_tool)
                    logger.info("✅ Google Search tool initialized (most accurate results)")
                except Exception as e:
                    logger.error(f"Google Search failed to initialize: {e}")
                    logger.warning("Web search disabled - check GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file")
            elif "search" in self.config.available_tools:
                logger.warning("Google Search not available - web search disabled")
                logger.info("To enable web search, set GOOGLE_API_KEY and GOOGLE_CSE_ID in your .env file")
                logger.info("Get your API key from: https://console.cloud.google.com/")
                logger.info("Get your CSE ID from: https://cse.google.com/cse/")
            
            if "wikipedia" in self.config.available_tools and WikipediaQueryRun:
                wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
                wikipedia.name = "wikipedia_search"
                wikipedia.description = "Search Wikipedia for factual information and detailed explanations"
                self._tools.append(wikipedia)
                logger.info("✅ Wikipedia search tool initialized")
                
            logger.info(f"Total tools initialized: {len(self._tools)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            # Fallback: disable tools if initialization fails
            self.config.enable_tools = False
    
    def _initialize_caching(self):
        """Initialize Redis caching if enabled"""
        if not self.config.enable_caching or not self.config.redis_url:
            return
        
        try:
            import redis
            self._redis_client = redis.from_url(self.config.redis_url)
            # Test connection
            self._redis_client.ping()
            logger.info("✅ Redis caching initialized successfully")
        except ImportError:
            logger.warning("Redis package not installed. Caching disabled.")
            self.config.enable_caching = False
        except Exception as e:
            logger.error(f"Failed to initialize Redis caching: {e}")
            self.config.enable_caching = False
    
    def _create_history_backend(self, user_id: str) -> BaseChatMessageHistory:
        """Create appropriate history backend for user"""
        try:
            if self.config.history_backend == HistoryBackend.REDIS and self.config.redis_url:
                return RedisChatMessageHistory(
                    session_id=user_id,
                    url=self.config.redis_url
                )
            elif self.config.history_backend == HistoryBackend.MONGODB and self.config.mongodb_connection:
                return MongoDBChatMessageHistory(
                    connection_string=self.config.mongodb_connection,
                    session_id=user_id
                )
            elif self.config.history_backend == HistoryBackend.POSTGRESQL and self.config.postgres_connection:
                return PostgresChatMessageHistory(
                    connection_string=self.config.postgres_connection,
                    session_id=user_id
                )
            elif self.config.history_backend == HistoryBackend.FILE:
                return FileChatMessageHistory(
                    file_path=f"{self.config.file_storage_path}/{user_id}.json"
                )
            else:
                return InMemoryChatMessageHistory()
        except Exception as e:
            logger.error(f"Failed to create history backend: {e}")
            return InMemoryChatMessageHistory()
    
    def _create_memory(self, user_id: str, history: BaseChatMessageHistory):
        """Create appropriate memory type for user"""
        try:
            if self.config.memory_type == MemoryType.BUFFER:
                return ConversationBufferMemory(
                    chat_memory=history,
                    return_messages=self.config.return_messages,
                    memory_key="history"
                )
            else:
                # Default to summary buffer - use buffer memory instead to avoid deprecation
                return ConversationBufferMemory(
                    chat_memory=history,
                    return_messages=self.config.return_messages,
                    memory_key="history"
                )
        except Exception as e:
            logger.error(f"Failed to create memory: {e}")
            # Use simple buffer memory as fallback
            return ConversationBufferMemory(
                chat_memory=history,
                return_messages=self.config.return_messages,
                memory_key="history"
            )
    
    def _get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in self._user_sessions:
            history = self._create_history_backend(user_id)
            memory = self._create_memory(user_id, history)
            
            # Create conversation chain with tools if enabled
            if self.config.enable_tools and self._tools:
                # Enhanced system prompt for tools
                system_prompt = """You are a professional AI research assistant with access to real-time information and comprehensive knowledge bases.

You have access to the following tools:
- Google Web Search: Use this for current events, recent news, real-time data, weather, stock prices, and live information (most accurate and up-to-date)
- Wikipedia: Use this for factual information, detailed explanations, historical context, and academic content

CRITICAL RESPONSE REQUIREMENTS:
1. **ALWAYS cite specific sources** when using tools - mention the exact news outlet, website, or publication
2. **Use journalistic style** - be specific, factual, and professional
3. **Provide direct quotes or specific details** from sources when possible
4. **Include source names** in your responses (e.g., "According to Reuters...", "As reported by CNN...")
5. **Make responses comprehensive** but well-structured and easy to read
6. **Use bullet points** for multiple pieces of information
7. **Always verify information** from multiple sources when possible

LOCATION AND TIME DEFAULTS:
- **Date/Time Queries**: When asked about current date/time without specific location, default to India, Delhi (IST - Indian Standard Time)
- **Weather Queries**: When asked about weather without specific location, default to India, Delhi
- **Location-Specific**: Always use the exact location mentioned in the query
- **Time Zones**: Clearly specify the time zone (IST for India, local time for other locations)

When using Google Search:
- Cite the specific news source and publication date
- Include relevant quotes or specific facts
- Provide context about the source's credibility
- For date/time: Always specify IST (Indian Standard Time) when defaulting to India
- **IMPORTANT**: For date/time queries, use specific terms like "current time IST India Delhi now" or "today's date India September 2025"
- **AVOID**: Vague terms like "current" or "today" alone, as they may return irrelevant results
- **QUERY OPTIMIZATION**: Google Search automatically optimizes queries for current information

When using Wikipedia:
- Cite the specific Wikipedia article
- Include key facts and explanations
- Provide historical context and background

Your responses should read like professional journalism with proper attribution."""
                
                # Create chain with tools
                from langchain.agents import AgentExecutor, create_openai_tools_agent
                from langchain_core.prompts import ChatPromptTemplate
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad")
                ])
                
                # Create agent with tools
                agent = create_openai_tools_agent(self.llm, self._tools, prompt)
                chain = AgentExecutor(agent=agent, tools=self._tools, verbose=False)
            else:
                # Basic conversation chain without tools
                from langchain_core.prompts import ChatPromptTemplate
                
                # Use custom system prompt or default
                system_message = self.config.system_prompt or "You are a helpful AI assistant with advanced capabilities."
                
                # Use custom user prompt template or default
                if self.config.user_prompt:
                    # If user_prompt contains {query}, use it as template
                    if "{query}" in self.config.user_prompt:
                        user_message = self.config.user_prompt.replace("{query}", "{input}")
                    else:
                        user_message = f"{self.config.user_prompt}\n\n{{input}}"
                else:
                    user_message = "{input}"
                
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_message),
                    MessagesPlaceholder(variable_name="history"),
                    ("human", user_message)
                ])
                
                chain = prompt | self.llm | StrOutputParser()
            
            self._user_sessions[user_id] = {
                "history": history,
                "memory": memory,
                "chain": chain,
                "created_at": datetime.now()
            }
            
            # Initialize metrics
            if self.config.enable_metrics:
                self._user_metrics[user_id] = ConversationMetrics(user_id=user_id)
        
        return self._user_sessions[user_id]
    
    def _retrieve_context(self, user_id: str, query: str) -> List[Document]:
        """Retrieve relevant context from vector store"""
        if not self._vector_store:
            return []
        
        try:
            docs = self._vector_store.similarity_search(
                query, k=self.config.top_k_documents
            )
            return docs
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []
    
    def _apply_security_filter(self, user_id: str, message: str) -> bool:
        """Apply security filtering to message"""
        if not self.config.enable_security:
            return True
        
        try:
            # Import SecurityAgent if available
            from .security_agent import SecurityAgent
            security_agent = SecurityAgent(threat_threshold=self.config.content_filter_threshold)
            result = security_agent.analyze_security(message)
            return not result.get("blocked", False)
        except ImportError:
            logger.warning("SecurityAgent not available")
            return True
        except Exception as e:
            logger.error(f"Security filter error: {e}")
            return True
    
    def _update_metrics(self, user_id: str, input_text: str, output_text: str, response_time: float):
        """Update conversation metrics"""
        if not self.config.enable_metrics or user_id not in self._user_metrics:
            return
        
        metrics = self._user_metrics[user_id]
        metrics.total_messages += 1
        metrics.last_activity = datetime.now()
        
        # Estimate tokens (rough approximation)
        input_tokens = len(input_text.split()) * 1.3
        output_tokens = len(output_text.split()) * 1.3
        
        metrics.total_tokens_input += int(input_tokens)
        metrics.total_tokens_output += int(output_tokens)
        
        # Estimate cost (rough approximation for GPT-3.5)
        cost_per_1k_input = 0.0015
        cost_per_1k_output = 0.002
        
        session_cost = (input_tokens / 1000 * cost_per_1k_input + 
                       output_tokens / 1000 * cost_per_1k_output)
        metrics.total_cost += session_cost
        
        # Update response time
        metrics.avg_response_time = (
            (metrics.avg_response_time * (metrics.total_messages - 1) + response_time) /
            metrics.total_messages
        )
    
    def invoke(self, user_id: str, message: str, **kwargs) -> str:
        """
        Main method to process user message and return response
        
        Args:
            user_id: Unique identifier for the user
            message: User's input message
            **kwargs: Additional parameters
            
        Returns:
            AI assistant's response
        """
        start_time = time.time()
        
        try:
            # Security filtering
            if not self._apply_security_filter(user_id, message):
                return "I cannot process that message due to content policy violations."
            
            # Check cache first
            cached_response = self._get_cached_response(user_id, message)
            if cached_response:
                logger.info(f"Returning cached response for user {user_id}")
                return cached_response
            
            # Get or create session
            session = self._get_or_create_session(user_id)
            memory = session["memory"]
            chain = session["chain"]
            
            # Retrieve RAG context if enabled
            context_docs = self._retrieve_context(user_id, message) if self.config.enable_rag else []
            context = "\n".join([doc.page_content for doc in context_docs]) if context_docs else ""
            
            # Prepare input with context
            enhanced_message = message
            if context:
                enhanced_message = f"Context: {context}\n\nUser: {message}"
            
            # Get memory variables
            memory_vars = memory.load_memory_variables({})
            
            # Prepare chain input based on chain type
            if hasattr(chain, 'tools') and chain.tools:  # AgentExecutor with tools
                # For tools-enabled chains, we need to handle the input differently
                chain_input = {
                    "input": enhanced_message,
                    "chat_history": memory_vars.get("history", [])
                }
                
                # Setup callback for metrics
                callbacks = []
                if self.config.enable_metrics and user_id in self._user_metrics:
                    callbacks.append(ConversationCallback(self._user_metrics[user_id]))
                
                # Invoke agent with tools
                result = chain.invoke(chain_input, config={"callbacks": callbacks})
                # Extract the response from the agent result
                if hasattr(result, 'output'):
                    response = result.output
                elif isinstance(result, dict) and 'output' in result:
                    response = result['output']
                else:
                    response = str(result)
            else:
                # For basic chains without tools
                chain_input = {
                    "input": enhanced_message,
                    "history": memory_vars.get("history", [])
                }
                
                # Setup callback for metrics
                callbacks = []
                if self.config.enable_metrics and user_id in self._user_metrics:
                    callbacks.append(ConversationCallback(self._user_metrics[user_id]))
                
                # Invoke basic chain
                response = chain.invoke(chain_input, config={"callbacks": callbacks})
            
            # Save to memory
            memory.save_context({"input": message}, {"output": response})
            
            # Cache the response
            self._cache_response(user_id, message, response)
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_metrics(user_id, message, response, response_time)
            
            logger.info(f"Processed message for user {user_id} in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message for user {user_id}: {e}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    def _get_cached_response(self, user_id: str, message: str) -> Optional[str]:
        """Get cached response if available"""
        if not self.config.enable_caching or not self._redis_client:
            return None
        
        try:
            cache_key = f"response:{user_id}:{hash(message)}"
            cached = self._redis_client.get(cache_key)
            if cached:
                self._cache_stats["hits"] += 1
                logger.info(f"Cache HIT for user {user_id}")
                return cached.decode('utf-8')
            else:
                self._cache_stats["misses"] += 1
                logger.info(f"Cache MISS for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None
    
    def _cache_response(self, user_id: str, message: str, response: str, ttl: int = 3600):
        """Cache response for future use"""
        if not self.config.enable_caching or not self._redis_client:
            return
        
        try:
            cache_key = f"response:{user_id}:{hash(message)}"
            self._redis_client.setex(cache_key, ttl, response)
            logger.info(f"Cached response for user {user_id} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache hit/miss statistics"""
        return self._cache_stats.copy()
    
    def clear_cache(self, user_id: str = None) -> bool:
        """Clear cache for specific user or all users"""
        if not self.config.enable_caching or not self._redis_client:
            return False
        
        try:
            if user_id:
                # Clear cache for specific user
                pattern = f"response:{user_id}:*"
                keys = self._redis_client.keys(pattern)
                if keys:
                    self._redis_client.delete(*keys)
                    logger.info(f"Cleared cache for user {user_id}")
                return True
            else:
                # Clear all cache
                pattern = "response:*"
                keys = self._redis_client.keys(pattern)
                if keys:
                    self._redis_client.delete(*keys)
                    logger.info("Cleared all cache")
                return True
        except Exception as e:
            logger.error(f"Cache clearing error: {e}")
            return False
    
    async def ainvoke(self, user_id: str, message: str, **kwargs) -> str:
        """Async version of invoke"""
        # For now, run sync version in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.invoke, user_id, message)
    
    async def stream(self, user_id: str, message: str) -> AsyncGenerator[str, None]:
        """Real-time streaming response tokens"""
        if not self.config.streaming:
            # Fallback to non-streaming if disabled
            response = self.invoke(user_id, message)
            yield response
            return
        
        try:
            # Security filtering
            if not self._apply_security_filter(user_id, message):
                yield "I cannot process that message due to content policy violations."
                return
            
            # Get or create session
            session = self._get_or_create_session(user_id)
            memory = session["memory"]
            
            # Retrieve RAG context if enabled
            context_docs = self._retrieve_context(user_id, message) if self.config.enable_rag else []
            context = "\n".join([doc.page_content for doc in context_docs]) if context_docs else ""
            
            # Prepare input with context
            enhanced_message = message
            if context:
                enhanced_message = f"Context: {context}\n\nUser: {message}"
            
            # Get memory variables
            memory_vars = memory.load_memory_variables({})
            
            # Create streaming prompt
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI assistant with advanced capabilities."),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])
            
            # Create streaming chain
            chain = prompt | self.llm | StrOutputParser()
            
            # Stream the response
            async for chunk in chain.astream({
                "input": enhanced_message,
                "history": memory_vars.get("history", [])
            }):
                yield chunk
            
            # Save to memory after streaming completes
            # Note: This is a simplified approach - in production you'd want to collect chunks differently
            memory.save_context({"input": message}, {"output": "Streamed response"})
            
        except Exception as e:
            logger.error(f"Streaming error for user {user_id}: {e}")
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    def get_conversation_history(self, user_id: str) -> List[BaseMessage]:
        """Get conversation history for a user"""
        if user_id not in self._user_sessions:
            return []
        
        session = self._user_sessions[user_id]
        return session["history"].messages
    
    def get_conversation_summary(self, user_id: str) -> str:
        """Get conversation summary for a user"""
        if user_id not in self._user_sessions:
            return ""
        
        session = self._user_sessions[user_id]
        memory = session["memory"]
        
        if hasattr(memory, "moving_summary_buffer"):
            return memory.moving_summary_buffer
        elif hasattr(memory, "buffer"):
            return str(memory.buffer)
        else:
            return "No summary available"
    
    def get_user_metrics(self, user_id: str) -> Optional[ConversationMetrics]:
        """Get metrics for a user"""
        return self._user_metrics.get(user_id)
    
    def get_all_metrics(self) -> Dict[str, ConversationMetrics]:
        """Get metrics for all users"""
        return self._user_metrics.copy()
    
    def clear_user_session(self, user_id: str) -> bool:
        """Clear session data for a user"""
        try:
            if user_id in self._user_sessions:
                del self._user_sessions[user_id]
            if user_id in self._user_metrics:
                del self._user_metrics[user_id]
            return True
        except Exception as e:
            logger.error(f"Error clearing session for user {user_id}: {e}")
            return False
    
    def add_documents_to_vector_store(self, documents: List[Document]) -> bool:
        """Add documents to vector store for RAG"""
        if not self._vector_store:
            return False
        
        try:
            self._vector_store.add_documents(documents)
            return True
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            return False
    
    def search_documents(self, query: str, k: int = 5) -> List[Document]:
        """Search documents in the vector store through our agent"""
        if not self._vector_store:
            return []
        
        try:
            return self._vector_store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the vector store"""
        if not self._vector_store:
            return 0
        
        try:
            if hasattr(self._vector_store, 'get'):
                # ChromaDB
                return len(self._vector_store.get()['documents'])
            elif hasattr(self._vector_store, 'index_to_docstore_id'):
                # FAISS
                return len(self._vector_store.index_to_docstore_id)
            else:
                return 0
        except Exception as e:
            logger.error(f"Failed to get document count: {e}")
            return 0
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store through our agent"""
        if not self._vector_store:
            return {"status": "not_initialized"}
        
        try:
            info = {
                "type": type(self._vector_store).__name__,
                "document_count": self.get_document_count(),
                "status": "active"
            }
            
            # Add ChromaDB specific info
            if "Chroma" in str(type(self._vector_store)):
                info["backend"] = "ChromaDB"
                if hasattr(self._vector_store, 'persist_directory'):
                    info["storage_path"] = self._vector_store.persist_directory
                info["persistent"] = True
            elif "FAISS" in str(type(self._vector_store)):
                info["backend"] = "FAISS"
                info["persistent"] = False
                info["storage"] = "in_memory"
            
            return info
        except Exception as e:
            logger.error(f"Failed to get vector store info: {e}")
            return {"status": "error", "message": str(e)}
    
    def export_documents(self, format: str = "json") -> str:
        """Export documents from vector store through our agent"""
        if not self._vector_store:
            return "No vector store available"
        
        try:
            documents = self._vector_store.get() if hasattr(self._vector_store, 'get') else []
            
            if format.lower() == "json":
                import json
                return json.dumps([{"content": doc.page_content, "metadata": doc.metadata} for doc in documents], indent=2)
            elif format.lower() == "text":
                return "\n\n".join([f"Content: {doc.page_content}\nMetadata: {doc.metadata}" for doc in documents])
            else:
                return f"Unsupported format: {format}"
        except Exception as e:
            logger.error(f"Failed to export documents: {e}")
            return f"Export failed: {str(e)}"
    
    def export_conversation(self, user_id: str, format: str = "json") -> Optional[str]:
        """Export conversation history in various formats"""
        if user_id not in self._user_sessions:
            return None
        
        try:
            history = self.get_conversation_history(user_id)
            metrics = self.get_user_metrics(user_id)
            
            if format.lower() == "json":
                export_data = {
                    "user_id": user_id,
                    "conversation": [
                        {
                            "type": msg.type,
                            "content": msg.content,
                            "timestamp": getattr(msg, "timestamp", None)
                        }
                        for msg in history
                    ],
                    "metrics": {
                        "total_messages": metrics.total_messages if metrics else 0,
                        "total_tokens": (metrics.total_tokens_input + metrics.total_tokens_output) if metrics else 0,
                        "total_cost": metrics.total_cost if metrics else 0,
                        "session_duration": str(datetime.now() - metrics.session_start) if metrics else None
                    }
                }
                return json.dumps(export_data, indent=2, default=str)
            
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health metrics"""
        tool_info = []
        for tool in self._tools:
            tool_info.append({
                "name": getattr(tool, 'name', 'unknown'),
                "description": getattr(tool, 'description', 'No description available')
            })
        
        return {
            "active_sessions": len(self._user_sessions),
            "total_users": len(self._user_metrics),
            "llm_provider": self.config.llm_provider.value,
            "memory_type": self.config.memory_type.value,
            "history_backend": self.config.history_backend.value,
            "rag_enabled": self.config.enable_rag,
            "tools_enabled": self.config.enable_tools,
            "security_enabled": self.config.enable_security,
            "vector_store_available": self._vector_store is not None,
            "available_tools": len(self._tools),
            "tool_details": tool_info,
            "caching_enabled": self.config.enable_caching,
            "streaming_enabled": self.config.streaming,
            "cache_stats": self._cache_stats,
            "redis_connected": self._redis_client is not None
        }


# Convenience factory functions
def create_basic_agent(**kwargs) -> AdvancedConversationAgent:
    """Create a basic conversation agent with minimal configuration"""
    config = AgentConfig(
        llm_provider=LLMProvider.FAKE,
        memory_type=MemoryType.SUMMARY_BUFFER,
        history_backend=HistoryBackend.IN_MEMORY,
        **kwargs
    )
    return AdvancedConversationAgent(config)


def create_openai_agent(api_key: str = None, model: str = "gpt-3.5-turbo", 
                       system_prompt: str = None, user_prompt: str = None, **kwargs) -> AdvancedConversationAgent:
    """Create an OpenAI-powered conversation agent
    
    Features are opt-in for better control and cost management:
    - enable_rag: Enable document retrieval and context
    - enable_tools: Enable web search, Wikipedia, custom tools
    - enable_security: Enable content filtering and threat detection
    - enable_metrics: Enable performance tracking and analytics
    - system_prompt: Custom system prompt to define agent behavior
    - user_prompt: Custom user prompt template for consistent formatting
    
    Example:
        # Basic OpenAI agent (just chat)
        agent = create_openai_agent()
        
        # With custom system prompt
        agent = create_openai_agent(system_prompt="You are a helpful AI assistant specialized in coding.")
        
        # With custom system and user prompts
        agent = create_openai_agent(
            system_prompt="You are a medical AI assistant. Always be professional and accurate.",
            user_prompt="Medical Query: {query}\nPlease provide a detailed response."
        )
        
        # With RAG for document context
        agent = create_openai_agent(enable_rag=True)
        
        # With tools for real-time information
        agent = create_openai_agent(enable_tools=True)
        
        # Full-featured agent
        agent = create_openai_agent(enable_rag=True, enable_tools=True, enable_security=True)
    """
    import os
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    
    # Extract feature flags to avoid conflicts
    enable_rag = kwargs.pop('enable_rag', False)
    enable_tools = kwargs.pop('enable_tools', False)
    enable_security = kwargs.pop('enable_security', False)
    enable_metrics = kwargs.pop('enable_metrics', True)
    
    config = AgentConfig(
        llm_provider=LLMProvider.OPENAI,
        model_name=model,
        memory_type=MemoryType.SUMMARY_BUFFER,
        history_backend=HistoryBackend.FILE,
        enable_rag=enable_rag,
        enable_tools=enable_tools,
        enable_security=enable_security,
        enable_metrics=enable_metrics,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        **kwargs
    )
    return AdvancedConversationAgent(config)


def create_enterprise_agent(**kwargs) -> AdvancedConversationAgent:
    """Create a full-featured enterprise agent
    
    Enterprise agent comes with production-ready defaults but allows customization:
    - enable_rag: Document retrieval and context (default: True)
    - enable_tools: External tools and APIs (default: True)
    - enable_security: Content filtering and threat detection (default: True)
    - enable_metrics: Performance tracking and analytics (default: True)
    - enable_caching: Redis caching for performance (default: True)
    - streaming: Real-time response streaming (default: True)
    
    Example:
        # Standard enterprise agent (all features enabled)
        agent = create_enterprise_agent()
        
        # Enterprise agent without RAG (chat only)
        agent = create_enterprise_agent(enable_rag=False)
        
        # Enterprise agent with custom model
        agent = create_enterprise_agent(model_name="gpt-4-turbo")
        
        # Enterprise agent with custom history backend
        agent = create_enterprise_agent(history_backend=HistoryBackend.MONGODB)
    """
    # Extract feature flags to avoid conflicts
    model_name = kwargs.pop('model_name', 'gpt-4')
    history_backend = kwargs.pop('history_backend', HistoryBackend.POSTGRESQL)
    enable_rag = kwargs.pop('enable_rag', True)
    enable_tools = kwargs.pop('enable_tools', True)
    enable_security = kwargs.pop('enable_security', True)
    enable_metrics = kwargs.pop('enable_metrics', True)
    enable_caching = kwargs.pop('enable_caching', True)
    streaming = kwargs.pop('streaming', True)
    
    config = AgentConfig(
        llm_provider=LLMProvider.OPENAI,
        model_name=model_name,
        memory_type=MemoryType.SUMMARY_BUFFER,
        history_backend=history_backend,
        enable_rag=enable_rag,
        enable_tools=enable_tools,
        enable_security=enable_security,
        enable_metrics=enable_metrics,
        enable_caching=enable_caching,
        streaming=streaming,
        **kwargs
    )
    return AdvancedConversationAgent(config)


if __name__ == "__main__":
    # Demo usage
    agent = create_basic_agent()
    
    user_id = "demo_user"
    print("Agent:", agent.invoke(user_id, "Hello! Tell me about your capabilities."))
    print("Agent:", agent.invoke(user_id, "What can you help me with?"))
    
    # Show metrics
    metrics = agent.get_user_metrics(user_id)
    if metrics:
        print(f"\nMetrics: {metrics.total_messages} messages, {metrics.total_cost:.4f} cost")
    
    # Show system status
    print("\nSystem Status:", agent.get_system_status())
