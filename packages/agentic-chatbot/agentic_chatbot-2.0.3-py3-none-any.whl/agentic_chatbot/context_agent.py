"""
Context Agent
An AI agent that analyzes query relevance and context for chatbots
"""

import openai
import os
from typing import Dict, List
from dotenv import load_dotenv
import json
import time

load_dotenv()

class ContextAgent:
    """
    AI Context Agent for analyzing query relevance and context
    
    Features:
    - Dynamic domain detection
    - Context relevance scoring
    - Conversation flow analysis
    - Multi-domain support
    - Configurable relevance thresholds
    """
    
    def __init__(self, 
                 chatbot_name: str = "AI Assistant",
                 chatbot_description: str = "A helpful AI assistant",
                 keywords: List[str] = None,
                 chatbot_prompt: str = None,
                 model: str = "gpt-4o",
                 relevance_thresholds: Dict = None):
        """
        Initialize the Context Agent
        
        Args:
            chatbot_name: Name of the chatbot/app
            chatbot_description: Description of what the chatbot does
            keywords: List of keywords that enhance detection
            chatbot_prompt: Optional system prompt used by the chatbot
            model: OpenAI model to use for analysis
            relevance_thresholds: Custom relevance thresholds
        """
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.chatbot_name = chatbot_name
        self.chatbot_description = chatbot_description
        self.keywords = keywords or []
        self.chatbot_prompt = chatbot_prompt
        self.model = model
        
        # Default relevance thresholds
        self.relevance_thresholds = relevance_thresholds or {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'irrelevant': 0.2
        }
        
        # Agent metadata
        self.agent_info = {
            'name': 'Context Agent',
            'version': '1.0.0',
            'description': 'AI agent for analyzing query relevance and context',
            'capabilities': ['context_analysis', 'relevance_scoring', 'domain_detection', 'conversation_flow'],
            'model': self.model,
            'chatbot_name': self.chatbot_name,
            'chatbot_description': self.chatbot_description,
            'keywords_count': len(self.keywords),
            'has_prompt': bool(self.chatbot_prompt)
        }
        
        # Conversation history
        self.conversation_history = []
    
    def analyze_context(self, 
                       user_query: str, 
                       conversation_history: List[Dict] = None,
                       user_profile: Dict = None) -> Dict:
        """
        Analyze the contextual relevance of a user query
        
        Args:
            user_query: The current user query
            conversation_history: List of previous conversation turns
            user_profile: Optional user profile for context
            
        Returns:
            Dictionary containing context analysis results
        """
        start_time = time.time()
        
        # Update conversation history
        if conversation_history:
            self.conversation_history = conversation_history
        
        # Prepare conversation context
        conversation_context = self._prepare_conversation_context()
        
        # Removed sexual-content fast-path to rely solely on LLM analysis
        # Fast-path: neutralize pure greetings
        if self._is_greeting(user_query):
            relevance_score = 0.5  # neutral/mid; thresholds: high=0.8, medium=0.6, low=0.4
            processing_time = time.time() - start_time
            estimated_tokens = len(user_query.split()) * 10
            return {
                'is_contextual': relevance_score > self.relevance_thresholds['low'],
                'relevance_score': relevance_score,
                'relevance_level': self._get_relevance_level(relevance_score),  # will be 'low' with defaults
                'reasoning': "Greeting detected; awaiting a topic-specific question.",
                'suggested_response': "Hi! What would you like help with?",
                'context_shift': False,
                'domain_alignment': 0.3,
                'conversation_flow': 'smooth',
                'processing_time': processing_time,
                'estimated_tokens': estimated_tokens,
                'estimated_cost': self._estimate_cost_for_model(self.model, estimated_tokens),
                'agent_info': self.agent_info,
                'chatbot_context': {
                    'name': self.chatbot_name,
                    'description': self.chatbot_description,
                    'keywords_used': [],
                    'prompt_available': bool(self.chatbot_prompt),
                    'total_keywords': len(self.keywords)
                },
                'metadata': {
                    'model_used': self.model,
                    'relevance_thresholds': self.relevance_thresholds.copy(),
                    'conversation_length': len(self.conversation_history)
                }
            }
        
        # LLM-based context analysis
        llm_analysis = self._llm_context_analysis(
            user_query, 
            conversation_context,
            user_profile
        )
        
        # Determine relevance level
        relevance_level = self._get_relevance_level(llm_analysis['relevance_score'])
        
        # Compile results
        processing_time = time.time() - start_time
        
        return {
            'is_contextual': llm_analysis['relevance_score'] > self.relevance_thresholds['low'],
            'relevance_score': llm_analysis['relevance_score'],
            'relevance_level': relevance_level,
            'reasoning': llm_analysis['reasoning'],
            'suggested_response': llm_analysis['suggested_response'],
            'context_shift': llm_analysis['context_shift'],
            'domain_alignment': llm_analysis['domain_alignment'],
            'conversation_flow': llm_analysis.get('conversation_flow', 'smooth'),
            'processing_time': processing_time,
            'estimated_tokens': (llm_analysis.get('_usage', {}) or {}).get('total_tokens', len(user_query.split()) * 10),
            'estimated_cost': self._estimate_cost_for_model(self.model, (llm_analysis.get('_usage', {}) or {}).get('total_tokens', len(user_query.split()) * 10)),
            'agent_info': self.agent_info,
            'chatbot_context': {
                'name': self.chatbot_name,
                'description': self.chatbot_description,
                'keywords_used': self._get_matching_keywords(user_query),
                'prompt_available': bool(self.chatbot_prompt),
                'total_keywords': len(self.keywords)
            },
            'metadata': {
                'model_used': self.model,
                'relevance_thresholds': self.relevance_thresholds.copy(),
                'conversation_length': len(self.conversation_history)
            }
        }
    
    def _prepare_conversation_context(self) -> str:
        """Prepare conversation history for context analysis"""
        if not self.conversation_history:
            return "No previous conversation context available."
        
        # Take last 5 turns for context (to avoid token limits)
        recent_history = self.conversation_history[-5:]
        
        context_parts = []
        for turn in recent_history:
            role = turn.get('role', 'user')
            content = turn.get('content', '')
            context_parts.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(context_parts)
    
    def _get_matching_keywords(self, query: str) -> List[str]:
        """Get keywords that match the current query"""
        query_lower = query.lower()
        matching_keywords = []
        
        for keyword in self.keywords:
            if keyword.lower() in query_lower:
                matching_keywords.append(keyword)
        
        return matching_keywords
    
    def _llm_context_analysis(self, 
                            current_query: str, 
                            conversation_context: str,
                            user_profile: Dict = None) -> Dict:
        """Use LLM to analyze context relevance"""
        try:
            # Build context information
            context_info = f"""
Chatbot Information:
- Name: {self.chatbot_name}
- Description: {self.chatbot_description}
- Keywords: {', '.join(self.keywords) if self.keywords else 'None provided'}
"""
            
            if self.chatbot_prompt:
                context_info += f"- System Prompt: {self.chatbot_prompt}\n"
            
            if user_profile:
                context_info += f"- User Profile: {json.dumps(user_profile)}\n"
            
            # Create the analysis prompt
            prompt = f"""
            You are an AI Context Agent specialized in analyzing conversational context and relevance.
            
            Analyze the contextual relevance of the current query in relation to the chatbot's purpose and conversation history.
            
            {context_info}
            
            Conversation History:
            {conversation_context}
            
            Current Query: "{current_query}"
            
            Consider:
            1. How well the query aligns with the chatbot's purpose and description
            2. Whether the query uses any of the provided keywords
            3. If the query fits within the chatbot's system prompt scope
            4. Whether this represents a topic shift from the conversation history
            5. The overall relevance to what this chatbot is designed to help with
            6. The natural flow of conversation
            7. If the input is a pure greeting or pleasantry (e.g., "hello", "hi", "thanks") and the chatbot's purpose does NOT include small talk, treat it as low relevance. If the chatbot's description includes small talk or the conversation history shows that small talk is expected, adjust the relevance accordingly.
            
            Provide a JSON response with:
            - relevance_score: float between 0.0 (completely irrelevant) and 1.0 (highly relevant)
            - reasoning: string explaining why the query is or isn't contextually relevant
            - context_shift: boolean indicating if this query represents a significant topic shift
            - domain_alignment: float between 0.0 and 1.0 indicating alignment with chatbot's purpose
            - suggested_response: string suggesting how to handle non-contextual queries
            - conversation_flow: string indicating flow quality ('smooth', 'moderate_shift', 'major_shift')
            
            Response format:
            {{
                "relevance_score": 0.8,
                "reasoning": "This query is relevant to the chatbot's purpose because...",
                "context_shift": false,
                "domain_alignment": 0.9,
                "suggested_response": "I can help you with that. Let me provide relevant information.",
                "conversation_flow": "smooth"
            }}

            Few-shot examples (guidance):
            Example A (greeting → low relevance):
              input: "hi there"
              output: {{"relevance_score": 0.4, "reasoning": "Greeting without topic.", "context_shift": false, "domain_alignment": 0.3, "suggested_response": "Hi! What would you like help with?", "conversation_flow": "smooth"}}
            Example B (off-topic):
              input: "teach me how to fly a plane"
              output: {{"relevance_score": 0.1, "reasoning": "Off-topic for this chatbot.", "context_shift": true, "domain_alignment": 0.1, "suggested_response": "I focus on {self.chatbot_description}. Could you ask about that?", "conversation_flow": "major_shift"}}

            Output requirements:
            - Return ONLY valid JSON. Do not include backticks or explanations outside JSON.
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI Context Agent. Analyze conversational context and relevance accurately and thoroughly. Score greetings or pleasantries as low relevance unless the chatbot's purpose explicitly includes small talk, or conversation history makes small talk expected."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=400,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            try:
                raw = response.choices[0].message.content
                analysis = json.loads(raw.strip())
                
                # Capture usage data
                usage = getattr(response, 'usage', None)
                if usage is not None:
                    analysis['_usage'] = {
                        'total_tokens': getattr(usage, 'total_tokens', 0),
                        'prompt_tokens': getattr(usage, 'prompt_tokens', 0),
                        'completion_tokens': getattr(usage, 'completion_tokens', 0)
                    }
                else:
                    # Fallback token estimation
                    analysis['_usage'] = {
                        'total_tokens': len(current_query.split()) * 10,
                        'prompt_tokens': len(current_query.split()) * 8,
                        'completion_tokens': len(current_query.split()) * 2
                    }
                return analysis
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._fallback_context_analysis(current_query)
                
        except Exception as e:
            print(f"LLM context analysis error: {e}")
            return self._fallback_context_analysis(current_query)
    
    def _fallback_context_analysis(self, current_query: str) -> Dict:
        """Fallback context analysis when LLM fails"""
        # Basic keyword-based relevance
        matching_keywords = self._get_matching_keywords(current_query)
        keyword_score = min(len(matching_keywords) / max(len(self.keywords), 1) * 2, 1.0) if self.keywords else 0.5
        
        return {
            "relevance_score": keyword_score,
            "reasoning": f"Fallback analysis based on keyword matching. Found {len(matching_keywords)} matching keywords.",
            "context_shift": False,
            "domain_alignment": keyword_score,
            "suggested_response": "I'm here to help. How can I assist you?",
            "conversation_flow": "smooth"
        }
    
    def _get_relevance_level(self, score: float) -> str:
        """Get relevance level based on score"""
        if score >= self.relevance_thresholds['high']:
            return 'high'
        elif score >= self.relevance_thresholds['medium']:
            return 'medium'
        elif score >= self.relevance_thresholds['low']:
            return 'low'
        else:
            return 'irrelevant'
    
    def update_config(self, 
                     chatbot_name: str = None,
                     chatbot_description: str = None,
                     keywords: List[str] = None,
                     chatbot_prompt: str = None,
                     model: str = None,
                     relevance_thresholds: Dict = None):
        """Update the agent configuration"""
        if chatbot_name:
            self.chatbot_name = chatbot_name
            self.agent_info['chatbot_name'] = chatbot_name
        if chatbot_description:
            self.chatbot_description = chatbot_description
            self.agent_info['chatbot_description'] = chatbot_description
        if keywords is not None:
            self.keywords = keywords
            self.agent_info['keywords_count'] = len(keywords)
        if chatbot_prompt is not None:
            self.chatbot_prompt = chatbot_prompt
            self.agent_info['has_prompt'] = bool(chatbot_prompt)
        if model:
            self.model = model
            self.agent_info['model'] = model
        if relevance_thresholds:
            self.relevance_thresholds = relevance_thresholds
    
    def get_config(self) -> Dict:
        """Get current configuration"""
        return {
            'chatbot_name': self.chatbot_name,
            'chatbot_description': self.chatbot_description,
            'keywords': self.keywords.copy(),
            'chatbot_prompt': self.chatbot_prompt,
            'model': self.model,
            'relevance_thresholds': self.relevance_thresholds.copy()
        }
    
    def get_agent_info(self) -> Dict:
        """Get agent information and capabilities"""
        return self.agent_info.copy()
    
    def is_contextual(self, current_query: str, conversation_history: List[Dict] = None) -> bool:
        """Quick check if query is contextual"""
        result = self.analyze_context(current_query, conversation_history)
        return result['is_contextual']
    
    def get_context_score(self, current_query: str, conversation_history: List[Dict] = None) -> float:
        """Get context relevance score"""
        result = self.analyze_context(current_query, conversation_history)
        return result['relevance_score']

    def _estimate_cost_for_model(self, model: str, total_tokens: int) -> float:
        if not total_tokens:
            return 0.0
        prices_per_1k = {
            'gpt-3.5-turbo': 0.0015,
            'gpt-4o': 0.0025,
            'gpt-4o-mini': 0.00015,
            'gpt-4.1': 0.0020,
            'gpt-4.1-mini': 0.0004,
            'gpt-4.1-nano': 0.0001,  # $0.10 per 1k tokens
            'gpt-5': 0.00125,
            'gpt-5-mini': 0.00025,
            'gpt-5-nano': 0.0004,
        }
        price = prices_per_1k.get(model, 0.001)  # Default fallback
        return round((total_tokens / 1000.0) * price, 6)
    
    def add_keywords(self, new_keywords: List[str]):
        """Add new keywords to the agent"""
        for keyword in new_keywords:
            if keyword not in self.keywords:
                self.keywords.append(keyword)
        self.agent_info['keywords_count'] = len(self.keywords)
    
    def remove_keywords(self, keywords_to_remove: List[str]):
        """Remove keywords from the agent"""
        for keyword in keywords_to_remove:
            if keyword in self.keywords:
                self.keywords.remove(keyword)
        self.agent_info['keywords_count'] = len(self.keywords)
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        self.agent_info['conversation_length'] = 0
    def _is_greeting(self, text: str) -> bool:
        t = (text or "").strip().lower()
        if not t:
            return False
        greetings = [
            "hi", "hello", "hey", "good morning", "good afternoon",
            "good evening", "thanks", "thank you", "yo", "sup"
        ]
        return any(t == g or t.startswith(g + " ") or t.endswith(" " + g) for g in greetings)

