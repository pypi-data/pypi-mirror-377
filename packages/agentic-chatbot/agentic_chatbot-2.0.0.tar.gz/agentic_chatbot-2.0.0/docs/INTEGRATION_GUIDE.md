# 🚀 AI Agents Integration Guide

**Complete guide to integrating AI agents into your chatbot system**

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Integration](#basic-integration)
3. [Advanced Configuration](#advanced-configuration)
4. [Customization](#customization)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Examples](#examples)

## 🚀 Quick Start

### 1. Install the Package

```bash
pip install ai-agents-chatbot
```

### 2. Basic Setup

```python
from ai_agents import SecurityAgent, ContextAgent, ModelSelectionAgent

# Initialize agents
security_agent = SecurityAgent()
context_agent = ContextAgent(
    chatbot_name="My Bot",
    chatbot_description="A helpful assistant"
)
model_agent = ModelSelectionAgent()

# Use in your chatbot
def handle_query(user_query):
    # Security check
    if security_agent.is_safe(user_query):
        # Context analysis
        context = context_agent.analyze_context(user_query)
        # Model selection
        model = model_agent.select_model(user_query)
        # Generate response
        return generate_response(user_query, model['selected_model'])
    else:
        return "I cannot process that request for security reasons."
```

## 🔧 Basic Integration

### Step-by-Step Integration

#### 1. Import and Initialize

```python
from ai_agents import SecurityAgent, ContextAgent, ModelSelectionAgent
import openai

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key="your_api_key")

# Initialize AI agents
security_agent = SecurityAgent(
    model="gpt-4o",
    threat_threshold=0.7
)

context_agent = ContextAgent(
    chatbot_name="My Assistant",
    chatbot_description="A helpful AI assistant for various tasks",
    keywords=["help", "assist", "support", "information"]
)

model_agent = ModelSelectionAgent(
    cost_sensitivity="medium",
    performance_preference="balanced"
)
```

#### 2. Create Query Processing Pipeline

```python
def process_user_query(user_query, conversation_history=None):
    """
    Process user query through all three AI agents
    """
    # Step 1: Security Analysis
    security_result = security_agent.analyze_security(
        user_query, 
        conversation_history
    )
    
    if security_result['blocked']:
        return {
            'response': "I cannot process that request for security reasons.",
            'blocked': True,
            'security_analysis': security_result
        }
    
    # Step 2: Context Analysis
    context_result = context_agent.analyze_context(
        user_query, 
        conversation_history
    )
    
    # Step 3: Model Selection
    model_result = model_agent.select_model(
        user_query, 
        conversation_history
    )
    
    # Step 4: Generate Response
    response = generate_response_with_model(
        user_query, 
        model_result['selected_model'],
        context_result,
        security_result
    )
    
    return {
        'response': response,
        'blocked': False,
        'security_analysis': security_result,
        'context_analysis': context_result,
        'model_selection': model_result
    }
```

#### 3. Response Generation

```python
def generate_response_with_model(user_query, model_id, context_result, security_result):
    """
    Generate response using the selected model
    """
    # Prepare system message based on analysis
    system_message = f"""You are a helpful AI assistant.

Context: {context_result['reasoning']}
Security Status: {'Safe' if not security_result['blocked'] else 'Blocked'}

Provide helpful and appropriate responses."""
    
    # Generate response
    response = openai_client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_query}
        ],
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content
```

#### 4. Complete Integration Example

```python
class EnhancedChatbot:
    def __init__(self):
        self.security_agent = SecurityAgent()
        self.context_agent = ContextAgent(
            chatbot_name="Enhanced Bot",
            chatbot_description="A smart assistant with AI agents"
        )
        self.model_agent = ModelSelectionAgent()
        self.conversation_history = []
    
    def chat(self, user_message):
        # Process through agents
        result = process_user_query(
            user_message, 
            self.conversation_history
        )
        
        # Update conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        self.conversation_history.append({
            'role': 'assistant',
            'content': result['response']
        })
        
        return result
    
    def get_analytics(self):
        """Get analytics from all agents"""
        return {
            'security': self.security_agent.get_agent_info(),
            'context': self.context_agent.get_agent_info(),
            'model_selection': self.model_agent.get_agent_info(),
            'conversation_length': len(self.conversation_history)
        }

# Usage
chatbot = EnhancedChatbot()
response = chatbot.chat("Hello, how can you help me?")
print(response['response'])
```

## ⚙️ Advanced Configuration

### Security Agent Configuration

```python
# High-security configuration
security_agent = SecurityAgent(
    model="gpt-4o",
    threat_threshold=0.5,  # More strict
    enable_detailed_analysis=True
)

# Add custom threat categories
security_agent.add_threat_category("CUSTOM_THREAT")

# Update configuration dynamically
security_agent.update_config(
    threat_threshold=0.3,
    model="gpt-4"
)
```

### Context Agent Configuration

```python
# Domain-specific configuration
context_agent = ContextAgent(
    chatbot_name="Medical Assistant",
    chatbot_description="A medical AI assistant providing health information",
    keywords=[
        "health", "medical", "symptoms", "treatment", "medicine",
        "doctor", "hospital", "diagnosis", "therapy"
    ],
    chatbot_prompt="You are a medical AI assistant. Always recommend consulting healthcare professionals for serious concerns.",
    relevance_thresholds={
        'high': 0.9,
        'medium': 0.7,
        'low': 0.5,
        'irrelevant': 0.3
    }
)

# Add keywords dynamically
context_agent.add_keywords(["emergency", "urgent", "critical"])

# Update configuration
context_agent.update_config(
    chatbot_description="Updated medical assistant description",
    keywords=["health", "medical", "wellness", "fitness"]
)
```

### Model Selection Agent Configuration

```python
# Custom model configuration
custom_models = {
    'gpt-3.5-turbo': {
        'name': 'GPT-3.5 Turbo',
        'provider': 'OpenAI',
        'description': 'Fast and cost-effective',
        'capabilities': ['general_conversation', 'fast_response'],
        'max_tokens': 4096,
        'cost_per_1k_tokens': 0.0015,
        'speed_rating': 0.9,
        'quality_rating': 0.7
    },
    'gpt-4o': {
        'name': 'GPT-4o',
        'provider': 'OpenAI',
        'description': 'High-quality responses',
        'capabilities': ['complex_analysis', 'high_accuracy'],
        'max_tokens': 128000,
        'cost_per_1k_tokens': 0.005,
        'speed_rating': 0.8,
        'quality_rating': 0.95
    }
}

model_agent = ModelSelectionAgent(
    available_models=custom_models,
    default_model='gpt-3.5-turbo',
    cost_sensitivity='high',  # Prefer cheaper models
    performance_preference='speed'  # Prioritize speed
)

# Add new models
model_agent.add_model('custom-model', {
    'name': 'Custom Model',
    'provider': 'Custom',
    'description': 'Custom trained model',
    'capabilities': ['custom_capability'],
    'max_tokens': 2048,
    'cost_per_1k_tokens': 0.001,
    'speed_rating': 0.8,
    'quality_rating': 0.8
})
```

## 🎨 Customization

### Custom Security Rules

```python
class CustomSecurityAgent(SecurityAgent):
    def __init__(self, custom_rules=None):
        super().__init__()
        self.custom_rules = custom_rules or {}
    
    def analyze_security(self, user_query, conversation_context=None, user_profile=None):
        # Apply custom rules first
        custom_result = self._apply_custom_rules(user_query)
        if custom_result['blocked']:
            return custom_result
        
        # Fall back to standard analysis
        return super().analyze_security(user_query, conversation_context, user_profile)
    
    def _apply_custom_rules(self, user_query):
        # Implement your custom security logic
        for rule_name, rule_func in self.custom_rules.items():
            if rule_func(user_query):
                return {
                    'blocked': True,
                    'threat_level': 'high',
                    'reasoning': f'Blocked by custom rule: {rule_name}'
                }
        
        return {'blocked': False}
```

### Custom Context Analysis

```python
class CustomContextAgent(ContextAgent):
    def __init__(self, domain_specific_rules=None, **kwargs):
        super().__init__(**kwargs)
        self.domain_rules = domain_specific_rules or {}
    
    def analyze_context(self, user_query, conversation_history=None, user_profile=None):
        # Apply domain-specific rules
        domain_score = self._apply_domain_rules(user_query)
        
        # Get base analysis
        base_analysis = super().analyze_context(user_query, conversation_history, user_profile)
        
        # Adjust score based on domain rules
        base_analysis['relevance_score'] = min(
            base_analysis['relevance_score'] + domain_score, 
            1.0
        )
        
        return base_analysis
    
    def _apply_domain_rules(self, user_query):
        score_adjustment = 0.0
        for domain, rules in self.domain_rules.items():
            if any(rule(user_query) for rule in rules):
                score_adjustment += 0.2
        
        return score_adjustment
```

### Custom Model Selection

```python
class CustomModelSelectionAgent(ModelSelectionAgent):
    def __init__(self, custom_scoring=None, **kwargs):
        super().__init__(**kwargs)
        self.custom_scoring = custom_scoring or {}
    
    def _calculate_model_score(self, model, query_analysis):
        # Get base score
        base_score = super()._calculate_model_score(model, query_analysis)
        
        # Apply custom scoring
        for scoring_func in self.custom_scoring.values():
            custom_score = scoring_func(model, query_analysis)
            base_score = (base_score + custom_score) / 2
        
        return base_score
```

## 📊 Best Practices

### 1. Error Handling

```python
def safe_agent_analysis(agent, method, *args, **kwargs):
    """Safely execute agent methods with error handling"""
    try:
        return getattr(agent, method)(*args, **kwargs)
    except Exception as e:
        print(f"Error in {agent.__class__.__name__}.{method}: {e}")
        # Return safe fallback
        return getattr(agent, f"_fallback_{method}")(*args, **kwargs)

# Usage
security_result = safe_agent_analysis(
    security_agent, 
    'analyze_security', 
    user_query
)
```

### 2. Performance Optimization

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_agent_analysis(user_query, conversation_history):
    """Run all agents in parallel for better performance"""
    with ThreadPoolExecutor() as executor:
        # Run all analyses in parallel
        security_future = executor.submit(
            security_agent.analyze_security, 
            user_query
        )
        context_future = executor.submit(
            context_agent.analyze_context, 
            user_query, 
            conversation_history
        )
        model_future = executor.submit(
            model_agent.select_model, 
            user_query, 
            conversation_history
        )
        
        # Wait for all results
        security_result = await asyncio.wrap_future(security_future)
        context_result = await asyncio.wrap_future(context_future)
        model_result = await asyncio.wrap_future(model_future)
        
        return security_result, context_result, model_result
```

### 3. Caching

```python
import functools
from typing import Dict, Any

class CachedAgent:
    def __init__(self, agent, cache_size=100):
        self.agent = agent
        self.cache = {}
        self.cache_size = cache_size
    
    def _get_cache_key(self, method, *args, **kwargs):
        """Generate cache key for method call"""
        import hashlib
        key_data = f"{method}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def __getattr__(self, name):
        """Intercept method calls and add caching"""
        if hasattr(self.agent, name):
            method = getattr(self.agent, name)
            if callable(method):
                return self._cached_method(method)
        return getattr(self.agent, name)
    
    def _cached_method(self, method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            cache_key = self._get_cache_key(method.__name__, *args, **kwargs)
            
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            result = method(*args, **kwargs)
            
            # Add to cache
            if len(self.cache) >= self.cache_size:
                # Remove oldest entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = result
            return result
        
        return wrapper

# Usage
cached_security_agent = CachedAgent(security_agent)
cached_context_agent = CachedAgent(context_agent)
cached_model_agent = CachedAgent(model_agent)
```

### 4. Monitoring and Logging

```python
import logging
import time
from typing import Dict, Any

class MonitoredAgent:
    def __init__(self, agent, logger=None):
        self.agent = agent
        self.logger = logger or logging.getLogger(__name__)
        self.metrics = {
            'total_calls': 0,
            'total_time': 0.0,
            'errors': 0,
            'cache_hits': 0
        }
    
    def __getattr__(self, name):
        """Intercept method calls and add monitoring"""
        if hasattr(self.agent, name):
            method = getattr(self.agent, name)
            if callable(method):
                return self._monitored_method(method, name)
        return getattr(self.agent, name)
    
    def _monitored_method(self, method, method_name):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            self.metrics['total_calls'] += 1
            
            try:
                result = method(*args, **kwargs)
                execution_time = time.time() - start_time
                self.metrics['total_time'] += execution_time
                
                self.logger.info(
                    f"{method_name} executed successfully in {execution_time:.2f}s"
                )
                
                return result
                
            except Exception as e:
                self.metrics['errors'] += 1
                execution_time = time.time() - start_time
                
                self.logger.error(
                    f"Error in {method_name}: {e} (took {execution_time:.2f}s)"
                )
                
                raise
        
        return wrapper
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        avg_time = (
            self.metrics['total_time'] / self.metrics['total_calls']
            if self.metrics['total_calls'] > 0 else 0
        )
        
        return {
            **self.metrics,
            'average_time': avg_time,
            'error_rate': (
                self.metrics['errors'] / self.metrics['total_calls']
                if self.metrics['total_calls'] > 0 else 0
            )
        }

# Usage
monitored_security = MonitoredAgent(security_agent)
monitored_context = MonitoredAgent(context_agent)
monitored_model = MonitoredAgent(model_agent)

# Get metrics
print(monitored_security.get_metrics())
```

## 🔍 Troubleshooting

### Common Issues

#### 1. API Key Errors

```python
# Check if API key is set
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in .env file")

# Test API connection
try:
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=5
    )
    print("✅ API connection successful")
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

#### 2. Model Selection Issues

```python
# Check available models
available_models = model_agent.get_available_models()
print("Available models:", list(available_models.keys()))

# Verify model capabilities
for model_id, model_info in available_models.items():
    print(f"{model_id}: {model_info['capabilities']}")

# Test model selection with simple query
test_result = model_agent.select_model("Hello, how are you?")
print("Test selection:", test_result['selected_model'])
```

#### 3. Context Analysis Issues

```python
# Check agent configuration
config = context_agent.get_config()
print("Context agent config:", config)

# Test with simple query
test_result = context_agent.analyze_context("Hello")
print("Test context analysis:", test_result)

# Verify keywords
keywords = context_agent.get_config()['keywords']
print("Keywords:", keywords)
```

### Debug Mode

```python
# Enable debug mode for detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual agents
security_result = security_agent.analyze_security("test query")
print("Security result:", security_result)

context_result = context_agent.analyze_context("test query")
print("Context result:", context_result)

model_result = model_agent.select_model("test query")
print("Model selection result:", model_result)
```

## 📚 Examples

### Complete Integration Example

See the [examples/](examples/) directory for complete working examples:

- `streamlit_demo.py` - Full Streamlit chatbot with all agents
- `simple_integration.py` - Basic integration example
- `advanced_integration.py` - Advanced features and customization

### Custom Use Cases

#### Healthcare Chatbot

```python
# Initialize healthcare-specific agents
health_security = SecurityAgent(
    model="gpt-4o",
    threat_threshold=0.6  # Stricter for medical content
)

health_context = ContextAgent(
    chatbot_name="Health Assistant",
    chatbot_description="Medical information and health advice",
    keywords=[
        "health", "medical", "symptoms", "treatment", "medicine",
        "doctor", "hospital", "diagnosis", "therapy", "wellness"
    ],
    chatbot_prompt="You are a medical AI assistant. Always recommend consulting healthcare professionals for serious concerns."
)

health_model = ModelSelectionAgent(
    cost_sensitivity="low",  # Quality over cost for medical queries
    performance_preference="quality"
)
```

#### E-commerce Assistant

```python
# Initialize e-commerce specific agents
ecom_security = SecurityAgent(
    model="gpt-4o",
    threat_threshold=0.7
)

ecom_context = ContextAgent(
    chatbot_name="Shopping Assistant",
    chatbot_description="Product recommendations and shopping help",
    keywords=[
        "buy", "purchase", "shop", "product", "price", "discount",
        "shipping", "delivery", "order", "cart", "checkout"
    ]
)

ecom_model = ModelSelectionAgent(
    cost_sensitivity="high",  # Cost-conscious for shopping queries
    performance_preference="speed"
)
```

---

**Need more help?** Check out our [API Reference](API_REFERENCE.md) or [Examples](EXAMPLES.md) for detailed information!
