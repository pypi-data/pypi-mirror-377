"""
AI Agents Demo Streamlit Chatbot
Demonstrates the three AI agents working together:
1. Security Agent - Malicious content detection
2. Context Agent - Query relevance analysis
3. Model Selection Agent - Optimal LLM selection
"""

import streamlit as st
import os
import sys
import time
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agents import SecurityAgent, ContextAgent, ModelSelectionAgent
import openai

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Agents Demo Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #1f77b4;
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.agent-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #1f77b4;
}

.security-warning {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}

.context-info {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}

.model-info {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 0.75rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}

.metric-card {
    background-color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #e9ecef;
    text-align: center;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #1f77b4;
}

.metric-label {
    font-size: 0.9rem;
    color: #6c757d;
}
</style>
""", unsafe_allow_html=True)

def initialize_agents():
    """Initialize the three AI agents"""
    if 'agents_initialized' not in st.session_state:
        # Initialize Security Agent
        security_agent = SecurityAgent(
            model="gpt-4o",
            threat_threshold=0.7,
            enable_detailed_analysis=True
        )
        
        # Initialize Context Agent
        context_agent = ContextAgent(
            chatbot_name="AI Agents Demo Bot",
            chatbot_description="A demonstration chatbot showcasing three AI agents working together: Security, Context, and Model Selection",
            keywords=[
                "demo", "showcase", "ai", "agents", "security", "context", "model", "selection",
                "chatbot", "intelligence", "analysis", "detection", "optimization"
            ],
            chatbot_prompt="You are a helpful AI assistant demonstrating the capabilities of three specialized AI agents working together.",
            model="gpt-3.5-turbo"
        )
        
        # Initialize Model Selection Agent
        model_selection_agent = ModelSelectionAgent(
            cost_sensitivity="medium",
            performance_preference="balanced"
        )
        
        st.session_state.security_agent = security_agent
        st.session_state.context_agent = context_agent
        st.session_state.model_selection_agent = model_selection_agent
        st.session_state.agents_initialized = True
        
        # Initialize OpenAI client
        st.session_state.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize conversation history
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        # Initialize metrics
        if 'metrics' not in st.session_state:
            st.session_state.metrics = {
                'total_queries': 0,
                'security_blocks': 0,
                'context_analyses': 0,
                'model_selections': 0,
                'total_cost': 0.0,
                'total_tokens': 0
            }

def render_sidebar():
    """Render the sidebar with agent information and controls"""
    st.sidebar.title("🤖 AI Agents Demo")
    
    # Agent Status
    st.sidebar.subheader("Agent Status")
    
    if st.session_state.agents_initialized:
        # Security Agent
        security_info = st.session_state.security_agent.get_agent_info()
        with st.sidebar.expander("🛡️ Security Agent", expanded=True):
            st.write(f"**Status:** ✅ Active")
            st.write(f"**Model:** {security_info['model']}")
            st.write(f"**Threat Threshold:** {security_info['threat_threshold']}")
            st.write(f"**Capabilities:** {', '.join(security_info['capabilities'][:2])}...")
        
        # Context Agent
        context_info = st.session_state.context_agent.get_agent_info()
        with st.sidebar.expander("🧠 Context Agent", expanded=True):
            st.write(f"**Status:** ✅ Active")
            st.write(f"**Model:** {context_info['model']}")
            st.write(f"**Keywords:** {context_info['keywords_count']}")
            st.write(f"**Capabilities:** {', '.join(context_info['capabilities'][:2])}...")
        
        # Model Selection Agent
        model_info = st.session_state.model_selection_agent.get_agent_info()
        with st.sidebar.expander("🎯 Model Selection Agent", expanded=True):
            st.write(f"**Status:** ✅ Active")
            st.write(f"**Available Models:** {model_info['available_models_count']}")
            st.write(f"**Cost Sensitivity:** {model_info['cost_sensitivity']}")
            st.write(f"**Capabilities:** {', '.join(model_info['capabilities'][:2])}...")
    
    # Configuration
    st.sidebar.subheader("⚙️ Configuration")
    
    if st.sidebar.button("🔄 Reinitialize Agents"):
        st.session_state.agents_initialized = False
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.metrics['total_queries'] = 0
        st.rerun()
    
    # Metrics
    st.sidebar.subheader("📊 Metrics")
    if 'metrics' in st.session_state:
        metrics = st.session_state.metrics
        st.sidebar.metric("Total Queries", metrics['total_queries'])
        st.sidebar.metric("Security Blocks", metrics['security_blocks'])
        st.sidebar.metric("Total Cost", f"${metrics['total_cost']:.4f}")

def render_chat_interface():
    """Render the main chat interface"""
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Agents Demo Chatbot</h1>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.2rem; color: #666;">
            Experience three AI agents working together: Security, Context Analysis, and Intelligent Model Selection
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
                # Display agent analysis if available
                if "agent_analysis" in message:
                    render_agent_analysis(message["agent_analysis"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything to see the AI agents in action..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Process with AI agents
        with st.spinner("🤖 AI agents are analyzing your query..."):
            response, agent_analysis = process_with_agents(prompt)
        
        # Add assistant response
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response,
            "agent_analysis": agent_analysis
        })
        
        # Update metrics
        st.session_state.metrics['total_queries'] += 1
        if agent_analysis['security']['blocked']:
            st.session_state.metrics['security_blocks'] += 1
        
        st.rerun()

def process_with_agents(user_query: str):
    """Process user query through all three AI agents"""
    start_time = time.time()
    
    # Step 1: Security Analysis
    security_result = st.session_state.security_agent.analyze_security(user_query)
    
    # Short-circuit on blocked inputs to avoid extra cost/latency
    if security_result['blocked']:
        response = f"🚫 **Security Alert:** {security_result['llm_analysis']['reasoning']}\n\nI cannot process this request as it appears to contain potentially harmful content. Please rephrase your question in a safe and appropriate manner."
        context_result = {
            'relevance_level': 'irrelevant',
            'relevance_score': 0.0,
            'context_shift': True,
            'domain_alignment': 0.0,
            'reasoning': 'Skipped due to security block',
            'chatbot_context': {
                'name': 'AI Agents Demo Bot',
                'description': 'Blocked due to security',
                'keywords_used': [],
                'prompt_available': False,
                'total_keywords': 0
            },
            'estimated_tokens': 0,
            'estimated_cost': 0.0
        }
        model_result = {
            'selected_model': 'N/A',
            'model_info': {'name': 'N/A', 'description': 'Blocked by security'},
            'confidence_score': 0.0,
            'estimated_cost': 0.0,
            'estimated_tokens': 0,
            'processing_time': 0.0
        }
        # Update totals even when blocked (security/context calls still cost)
        st.session_state.metrics['total_cost'] += (
            security_result.get('estimated_cost', 0.0) + context_result.get('estimated_cost', 0.0)
        )
        st.session_state.metrics['total_tokens'] += (
            security_result.get('estimated_tokens', 0) + context_result.get('estimated_tokens', 0)
        )
    else:
        # Step 2: Context Analysis
        conversation_history = [{"role": msg["role"], "content": msg["content"]} 
                               for msg in st.session_state.messages[-10:]]  # Last 10 messages
        context_result = st.session_state.context_agent.analyze_context(user_query, conversation_history)
        
        # Step 3: Model Selection
        model_result = st.session_state.model_selection_agent.select_model(
            user_query, 
            str(conversation_history[-3:]) if conversation_history else None
        )
        
        # Step 4: Generate response using selected model
        response = generate_response(user_query, model_result, context_result, security_result)
        
        # Update metrics (sum model + security + context costs)
        st.session_state.metrics['total_cost'] += (
            model_result.get('estimated_cost', 0.0)
            + security_result.get('estimated_cost', 0.0)
            + context_result.get('estimated_cost', 0.0)
        )
        st.session_state.metrics['total_tokens'] += (
            model_result.get('estimated_tokens', 0)
            + security_result.get('estimated_tokens', 0)
            + context_result.get('estimated_tokens', 0)
        )
    
    processing_time = time.time() - start_time
    
    # Compile agent analysis
    agent_analysis = {
        'security': security_result,
        'context': context_result,
        'model_selection': model_result,
        'processing_time': processing_time,
        'timestamp': datetime.now().isoformat()
    }
    
    return response, agent_analysis

def generate_response(user_query: str, model_result: Dict, context_result: Dict, security_result: Dict):
    """Generate response using the selected model"""
    try:
        # Prepare system message based on context and security
        system_message = f"""You are a helpful AI assistant demonstrating the capabilities of three specialized AI agents working together.

Context Analysis: {context_result['reasoning']}
Security Status: {'Safe' if not security_result['blocked'] else 'Blocked'}
Selected Model: {model_result['model_info']['name']} - {model_result['model_info']['description']}

Provide a helpful, informative response that demonstrates the AI agents' capabilities."""
        
        # Generate response
        response = st.session_state.openai_client.chat.completions.create(
            model=model_result['selected_model'],
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_query}
            ],
            temperature=0.7,
            max_tokens=model_result['estimated_tokens']
        )
        
        response_text = response.choices[0].message.content
        
        # Add agent information to response
        agent_info = f"""

---
🤖 **AI Agents Analysis:**
🛡️ **Security:** {security_result['threat_level'].title()} (Score: {security_result['threat_score']:.2f})
🧠 **Context:** {context_result['relevance_level'].title()} (Score: {context_result['relevance_score']:.2f})
🎯 **Model:** {model_result['model_info']['name']} (Confidence: {model_result['confidence_score']:.2f})
⏱️ **Processing Time:** {model_result['processing_time']:.2f}s
💰 **Estimated Cost:** ${model_result['estimated_cost']:.4f}
"""
        
        return response_text + agent_info
        
    except Exception as e:
        return f"I apologize, but I encountered an error while generating a response: {str(e)}"

def render_agent_analysis(agent_analysis: Dict):
    """Render the agent analysis panel"""
    with st.expander("🔍 AI Agents Analysis", expanded=False):
        # Create columns for different agents
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🛡️ Security Agent")
            security = agent_analysis['security']
            st.write(f"**Threat Level:** {security['threat_level'].title()}")
            st.write(f"**Threat Score:** {security['threat_score']:.2f}")
            st.write(f"**Confidence:** {security['confidence_score']:.2f}")
            st.write(f"**Blocked:** {'Yes' if security['blocked'] else 'No'}")
            if 'estimated_cost' in security:
                st.write(f"**Estimated Cost:** ${security['estimated_cost']:.4f}")
            if 'estimated_tokens' in security:
                st.write(f"**Tokens:** {security['estimated_tokens']}")
            # Show per-category metrics (empty arrays now; populated by downstream tracking)
            if 'metrics' in security:
                with st.expander("Per-category Metrics"):
                    st.json(security['metrics'])
            
            if security['warnings']:
                for warning in security['warnings']:
                    st.warning(warning)
        
        with col2:
            st.markdown("### 🧠 Context Agent")
            context = agent_analysis['context']
            st.write(f"**Relevance:** {context['relevance_level'].title()}")
            st.write(f"**Relevance Score:** {context['relevance_score']:.2f}")
            st.write(f"**Context Shift:** {'Yes' if context['context_shift'] else 'No'}")
            st.write(f"**Domain Alignment:** {context['domain_alignment']:.2f}")
            if 'estimated_cost' in context:
                st.write(f"**Estimated Cost:** ${context['estimated_cost']:.4f}")
            if 'estimated_tokens' in context:
                st.write(f"**Tokens:** {context['estimated_tokens']}")
            
            chatbot_ctx = context.get('chatbot_context', {})
            if chatbot_ctx.get('keywords_used'):
                st.info(f"**Keywords Used:** {', '.join(chatbot_ctx['keywords_used'])}")
        
        with col3:
            st.markdown("### 🎯 Model Selection Agent")
            model_sel = agent_analysis['model_selection']
            st.write(f"**Selected Model:** {model_sel['model_info']['name']}")
            st.write(f"**Confidence:** {model_sel['confidence_score']:.2f}")
            st.write(f"**Estimated Cost:** ${model_sel['estimated_cost']:.4f}")
            st.write(f"**Estimated Tokens:** {model_sel['estimated_tokens']}")
        
        # Performance metrics
        st.markdown("### 📊 Performance Metrics")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.metric("Processing Time", f"{agent_analysis['processing_time']:.2f}s")
        
        with col5:
            sec_cost = agent_analysis['security'].get('estimated_cost', 0.0)
            ctx_cost = agent_analysis['context'].get('estimated_cost', 0.0)
            mdl_cost = agent_analysis['model_selection'].get('estimated_cost', 0.0)
            total_cost = sec_cost + ctx_cost + mdl_cost
            st.metric("Total Cost", f"${total_cost:.4f}")
        
        with col6:
            st.metric("Security Status", "🛡️ Safe" if not agent_analysis['security']['blocked'] else "🚫 Blocked")
        
        # Raw data
        with st.expander("🔧 Raw Agent Data"):
            st.json(agent_analysis)

def main():
    """Main application function"""
    # Initialize agents
    initialize_agents()
    
    # Render sidebar
    render_sidebar()
    
    # Render main interface
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem;">
        <p>🤖 Powered by Three AI Agents: Security • Context • Model Selection</p>
        <p>Open Source AI Agents for Enhanced Chatbot Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
