"""
AI Agents Package
Advanced intelligent AI agents for enterprise chatbot enhancement:
1. Security Agent - Malicious content detection & filtering
2. Context Agent - Query relevance analysis & routing
3. Model Selection Agent - Optimal LLM selection & cost optimization
4. Advanced Conversation Agent - Enterprise-grade multi-modal agent with RAG, tools, metrics
"""

from .security_agent import SecurityAgent
from .context_agent import ContextAgent
from .model_selection_agent import ModelSelectionAgent
from .advanced_conversation_agent import (
    AdvancedConversationAgent,
    AgentConfig,
    ConversationMetrics,
    MemoryType,
    HistoryBackend,
    LLMProvider,
    create_basic_agent,
    create_openai_agent,
    create_enterprise_agent,
)

__version__ = "2.0.0"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "SecurityAgent",
    "ContextAgent", 
    "ModelSelectionAgent",
    "AdvancedConversationAgent",
    "AgentConfig",
    "ConversationMetrics",
    "MemoryType",
    "HistoryBackend",
    "LLMProvider",
    "create_basic_agent",
    "create_openai_agent",
    "create_enterprise_agent",
]
