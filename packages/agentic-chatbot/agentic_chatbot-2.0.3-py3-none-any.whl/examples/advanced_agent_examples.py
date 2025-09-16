#!/usr/bin/env python3
"""
Advanced Conversation Agent Examples

This file demonstrates the comprehensive capabilities of the AdvancedConversationAgent
including various configurations, use cases, and integrations.

Usage:
    python examples/advanced_agent_examples.py

Requirements:
    - Set OPENAI_API_KEY environment variable for OpenAI examples
    - Install optional dependencies for specific backends:
      pip install redis pymongo psycopg2-binary sentence-transformers
"""

import os
import sys
import asyncio
import time
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ai_agents import (
    AdvancedConversationAgent,
    AgentConfig,
    MemoryType,
    HistoryBackend,
    LLMProvider,
    create_basic_agent,
    create_openai_agent,
    create_enterprise_agent,
)


def example_1_basic_usage():
    """Example 1: Basic usage with default settings"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Usage")
    print("=" * 60)
    
    # Create a basic agent
    agent = create_basic_agent()
    user_id = "user_001"
    
    # Have a conversation
    print("User: Hello! What can you do?")
    response1 = agent.invoke(user_id, "Hello! What can you do?")
    print(f"Agent: {response1}")
    
    print("\nUser: Tell me more about your capabilities")
    response2 = agent.invoke(user_id, "Tell me more about your capabilities")
    print(f"Agent: {response2}")
    
    # Show conversation history
    print("\n--- Conversation History ---")
    history = agent.get_conversation_history(user_id)
    for msg in history:
        print(f"{msg.type}: {msg.content}")
    
    # Show metrics
    metrics = agent.get_user_metrics(user_id)
    if metrics:
        print(f"\n--- Metrics ---")
        print(f"Messages: {metrics.total_messages}")
        print(f"Avg Response Time: {metrics.avg_response_time:.2f}s")
        print(f"Estimated Cost: ${metrics.total_cost:.4f}")


def example_2_memory_types():
    """Example 2: Different memory types"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Different Memory Types")
    print("=" * 60)
    
    memory_types = [
        (MemoryType.BUFFER, "Buffer Memory - Stores all messages"),
        (MemoryType.SUMMARY_BUFFER, "Summary Buffer - Summarizes old messages"),
        (MemoryType.SUMMARY, "Summary Memory - Only keeps summary"),
    ]
    
    for memory_type, description in memory_types:
        print(f"\n--- {description} ---")
        
        config = AgentConfig(
            memory_type=memory_type,
            max_token_limit=100,  # Small limit to trigger summarization
        )
        agent = AdvancedConversationAgent(config)
        user_id = f"user_{memory_type.value}"
        
        # Add several messages
        messages = [
            "Hi, I'm interested in learning about AI",
            "Can you tell me about machine learning?",
            "What about deep learning specifically?",
            "How does neural network training work?",
            "What are the latest developments in AI?"
        ]
        
        for msg in messages:
            agent.invoke(user_id, msg)
        
        # Show summary
        summary = agent.get_conversation_summary(user_id)
        print(f"Summary: {summary}")
        
        # Show history length
        history = agent.get_conversation_history(user_id)
        print(f"History messages: {len(history)}")


def example_3_history_backends():
    """Example 3: Different history backends"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: History Backends")
    print("=" * 60)
    
    # File backend
    print("--- File Backend ---")
    config = AgentConfig(
        history_backend=HistoryBackend.FILE,
        file_storage_path="./chat_histories_demo"
    )
    agent = AdvancedConversationAgent(config)
    user_id = "file_user"
    
    agent.invoke(user_id, "This conversation will be saved to file")
    agent.invoke(user_id, "Even if I restart the application")
    
    print("Conversation saved to file backend")
    
    # In-memory backend
    print("\n--- In-Memory Backend ---")
    config = AgentConfig(history_backend=HistoryBackend.IN_MEMORY)
    agent2 = AdvancedConversationAgent(config)
    
    agent2.invoke(user_id, "This conversation is only in memory")
    print("Conversation stored in memory only")


def example_4_openai_integration():
    """Example 4: OpenAI integration (requires API key)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: OpenAI Integration")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Skipping OpenAI example - OPENAI_API_KEY not set")
        return
    
    try:
        # Create OpenAI agent
        agent = create_openai_agent(
            model="gpt-3.5-turbo",
            enable_metrics=True
        )
        
        user_id = "openai_user"
        
        print("User: Explain quantum computing in simple terms")
        response = agent.invoke(user_id, "Explain quantum computing in simple terms")
        print(f"Agent: {response}")
        
        # Show detailed metrics
        metrics = agent.get_user_metrics(user_id)
        if metrics:
            print(f"\n--- OpenAI Metrics ---")
            print(f"Input Tokens: {metrics.total_tokens_input}")
            print(f"Output Tokens: {metrics.total_tokens_output}")
            print(f"Estimated Cost: ${metrics.total_cost:.4f}")
        
    except Exception as e:
        print(f"OpenAI example failed: {e}")


def example_5_rag_capabilities():
    """Example 5: RAG (Retrieval Augmented Generation)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: RAG Capabilities")
    print("=" * 60)
    
    try:
        config = AgentConfig(
            enable_rag=True,
            vector_store_path="./vector_store_demo"
        )
        agent = AdvancedConversationAgent(config)
        
        # Add some documents to the vector store
        from langchain_core.documents import Document
        
        documents = [
            Document(page_content="Python is a high-level programming language known for its simplicity and readability."),
            Document(page_content="Machine learning is a subset of AI that enables computers to learn from data."),
            Document(page_content="LangChain is a framework for building applications with large language models."),
        ]
        
        success = agent.add_documents_to_vector_store(documents)
        if success:
            print("Documents added to vector store")
            
            user_id = "rag_user"
            response = agent.invoke(user_id, "What is Python?")
            print(f"Agent (with RAG): {response}")
        else:
            print("Failed to add documents to vector store")
            
    except Exception as e:
        print(f"RAG example failed: {e}")


def example_6_multi_user_sessions():
    """Example 6: Multi-user session management"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Multi-User Sessions")
    print("=" * 60)
    
    agent = create_basic_agent()
    
    # Simulate multiple users
    users = ["alice", "bob", "charlie"]
    
    for user in users:
        print(f"\n--- User: {user} ---")
        agent.invoke(user, f"Hi, I'm {user}")
        agent.invoke(user, "What's my name?")
        
        # Show this user's history
        history = agent.get_conversation_history(user)
        print(f"History for {user}: {len(history)} messages")
    
    # Show system status
    status = agent.get_system_status()
    print(f"\n--- System Status ---")
    print(f"Active Sessions: {status['active_sessions']}")
    print(f"Total Users: {status['total_users']}")


def example_7_async_operations():
    """Example 7: Async operations"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Async Operations")
    print("=" * 60)
    
    async def async_conversation():
        agent = create_basic_agent()
        user_id = "async_user"
        
        print("Starting async conversation...")
        
        # Run multiple async invocations
        tasks = [
            agent.ainvoke(user_id, "Hello!"),
            agent.ainvoke(user_id, "How are you?"),
            agent.ainvoke(user_id, "What can you do?"),
        ]
        
        responses = await asyncio.gather(*tasks)
        
        for i, response in enumerate(responses, 1):
            print(f"Response {i}: {response}")
    
    # Run async example
    asyncio.run(async_conversation())


def example_8_conversation_export():
    """Example 8: Conversation export and analytics"""
    print("\n" + "=" * 60)
    print("EXAMPLE 8: Conversation Export")
    print("=" * 60)
    
    agent = create_basic_agent()
    user_id = "export_user"
    
    # Have a conversation
    messages = [
        "Hello, I need help with Python",
        "Can you explain list comprehensions?",
        "What about error handling?",
        "Thanks for the help!"
    ]
    
    for msg in messages:
        agent.invoke(user_id, msg)
    
    # Export conversation
    export_data = agent.export_conversation(user_id, format="json")
    if export_data:
        print("Conversation exported successfully:")
        print(export_data[:500] + "..." if len(export_data) > 500 else export_data)
    
    # Show all metrics
    all_metrics = agent.get_all_metrics()
    print(f"\nTotal users tracked: {len(all_metrics)}")


def example_9_custom_configuration():
    """Example 9: Custom configuration"""
    print("\n" + "=" * 60)
    print("EXAMPLE 9: Custom Configuration")
    print("=" * 60)
    
    # Create highly customized agent
    config = AgentConfig(
        llm_provider=LLMProvider.FAKE,
        memory_type=MemoryType.SUMMARY_BUFFER,
        history_backend=HistoryBackend.FILE,
        max_token_limit=500,
        enable_rag=False,
        enable_tools=False,
        enable_security=True,
        enable_metrics=True,
        temperature=0.9,
        file_storage_path="./custom_chat_histories"
    )
    
    agent = AdvancedConversationAgent(config)
    user_id = "custom_user"
    
    print("Custom agent created with:")
    print(f"- LLM Provider: {config.llm_provider.value}")
    print(f"- Memory Type: {config.memory_type.value}")
    print(f"- History Backend: {config.history_backend.value}")
    print(f"- Security Enabled: {config.enable_security}")
    
    response = agent.invoke(user_id, "Test the custom configuration")
    print(f"Agent: {response}")
    
    # Show system status
    status = agent.get_system_status()
    print(f"\nSystem Status: {status}")


def example_10_error_handling():
    """Example 10: Error handling and robustness"""
    print("\n" + "=" * 60)
    print("EXAMPLE 10: Error Handling")
    print("=" * 60)
    
    # Test with invalid configuration
    try:
        config = AgentConfig(
            llm_provider=LLMProvider.OPENAI,  # Will fail without API key
            model_name="nonexistent-model"
        )
        agent = AdvancedConversationAgent(config)
        
        # Should still work due to fallback mechanisms
        response = agent.invoke("error_user", "This should still work")
        print(f"Fallback response: {response}")
        
    except Exception as e:
        print(f"Handled error gracefully: {e}")
    
    # Test session clearing
    agent = create_basic_agent()
    user_id = "clear_user"
    
    agent.invoke(user_id, "Hello")
    print(f"Sessions before clear: {agent.get_system_status()['active_sessions']}")
    
    agent.clear_user_session(user_id)
    print(f"Sessions after clear: {agent.get_system_status()['active_sessions']}")


def main():
    """Run all examples"""
    load_dotenv()  # Load environment variables
    
    print("🚀 Advanced Conversation Agent Examples")
    print("=" * 60)
    
    examples = [
        example_1_basic_usage,
        example_2_memory_types,
        example_3_history_backends,
        example_4_openai_integration,
        example_5_rag_capabilities,
        example_6_multi_user_sessions,
        example_7_async_operations,
        example_8_conversation_export,
        example_9_custom_configuration,
        example_10_error_handling,
    ]
    
    for example in examples:
        try:
            example()
            time.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"Example failed: {e}")
            continue
    
    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
