"""
Model Selection Agent
An AI agent that intelligently selects the optimal LLM model for queries
"""

import openai
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import json
import time

load_dotenv()

class ModelSelectionAgent:
    """
    AI Model Selection Agent for choosing optimal LLM models
    
    Features:
    - Intelligent model selection based on query characteristics
    - Cost optimization and performance balancing
    - Dynamic model configuration
    - Query complexity analysis
    - Multi-provider support
    """
    
    def __init__(self, 
                 available_models: Dict = None,
                 default_model: str = "gpt-4.1-nano",
                 cost_sensitivity: str = "medium",
                 performance_preference: str = "balanced"):
        """
        Initialize the Model Selection Agent
        
        Args:
            available_models: Dictionary of available models with their capabilities
            default_model: Default model to use as fallback
            cost_sensitivity: Cost sensitivity level ('low', 'medium', 'high')
            performance_preference: Performance preference ('speed', 'balanced', 'quality')
        """
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.default_model = default_model
        self.cost_sensitivity = cost_sensitivity
        self.performance_preference = performance_preference
        
        # Default available models if none provided
        self.available_models = available_models or self._get_default_models()
        
        # Agent metadata
        self.agent_info = {
            'name': 'Model Selection Agent',
            'version': '1.0.0',
            'description': 'AI agent for intelligent LLM model selection',
            'capabilities': ['model_selection', 'query_analysis', 'cost_optimization', 'performance_balancing'],
            'default_model': self.default_model,
            'cost_sensitivity': self.cost_sensitivity,
            'performance_preference': self.performance_preference,
            'available_models_count': len(self.available_models)
        }
        
        # Selection history for learning
        self.selection_history = []
    
    def _get_default_models(self) -> Dict:
        """Get default available models configuration"""
        return {
            # 'gpt-5-nano': {  # Removed due to empty response issue
            #     'name': 'GPT-5 Nano',
            #     'provider': 'OpenAI',
            #     'description': 'Ultra-fast and cost-effective model for simple tasks',
            #     'capabilities': ['general_conversation', 'basic_analysis', 'ultra_fast_response', 'summarization', 'simple_tasks', 'text_summarization'],
            #     'max_tokens': 16384,
            #     'cost_per_1k_tokens': 0.0004,
            #     'speed_rating': 0.95,
            #     'quality_rating': 0.6,
            #     'best_for': ['simple_queries', 'general_conversation', 'ultra_cost_sensitive_tasks']
            # },
            'gpt-5-mini': {
                'name': 'GPT-5 Mini',
                'provider': 'OpenAI',
                'description': 'Fast and efficient model for moderate tasks',
                'capabilities': ['moderate_analysis', 'good_accuracy', 'fast_response'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.00025,
                'speed_rating': 0.9,
                'quality_rating': 0.75,
                'best_for': ['moderate_queries', 'balanced_tasks', 'cost_sensitive_tasks']
            },
            'gpt-5': {
                'name': 'GPT-5',
                'provider': 'OpenAI',
                'description': 'Latest high-performance model for complex tasks',
                'capabilities': ['complex_analysis', 'detailed_explanations', 'high_accuracy', 'advanced_reasoning', 'statistical_analysis', 'code_generation', 'comparative_analysis', 'research_capabilities', 'statistical_methods', 'programming'],
                'max_tokens': 128000,
                'cost_per_1k_tokens': 0.00125,
                'speed_rating': 0.85,
                'quality_rating': 0.98,
                'best_for': ['complex_queries', 'detailed_analysis', 'high_quality_responses', 'advanced_tasks']
            },
            'gpt-4o': {
                'name': 'GPT-4o',
                'provider': 'OpenAI',
                'description': 'High-performance model for complex tasks',
                'capabilities': ['complex_analysis', 'detailed_explanations', 'high_accuracy', 'statistical_analysis', 'code_generation', 'comparative_analysis', 'statistical_methods', 'programming'],
                'max_tokens': 128000,
                'cost_per_1k_tokens': 2.5,
                'speed_rating': 0.8,
                'quality_rating': 0.95,
                'best_for': ['complex_queries', 'detailed_analysis', 'high_quality_responses']
            },
            'gpt-4o-mini': {
                'name': 'GPT-4o Mini',
                'provider': 'OpenAI',
                'description': 'Balanced model with good performance and reasonable cost',
                'capabilities': ['moderate_analysis', 'good_accuracy', 'balanced_performance'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.00015,
                'speed_rating': 0.85,
                'quality_rating': 0.8,
                'best_for': ['moderate_complexity', 'balanced_tasks', 'cost_conscious_quality']
            },
            'gpt-4.1': {
                'name': 'GPT-4.1',
                'provider': 'OpenAI',
                'description': 'Advanced model with enhanced capabilities',
                'capabilities': ['advanced_analysis', 'detailed_explanations', 'high_accuracy', 'research_capabilities'],
                'max_tokens': 128000,
                'cost_per_1k_tokens': 2.0,
                'speed_rating': 0.75,
                'quality_rating': 0.97,
                'best_for': ['advanced_queries', 'research_tasks', 'high_quality_responses']
            },
            'gpt-4.1-mini': {
                'name': 'GPT-4.1 Mini',
                'provider': 'OpenAI',
                'description': 'Efficient advanced model for moderate complexity',
                'capabilities': ['moderate_analysis', 'good_accuracy', 'balanced_performance'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.4,
                'speed_rating': 0.8,
                'quality_rating': 0.85,
                'best_for': ['moderate_complexity', 'balanced_tasks', 'cost_conscious_quality']
            },
            'gpt-4.1-nano': {
                'name': 'GPT-4.1 Nano',
                'provider': 'OpenAI',
                'description': 'Ultra-fast and cost-effective model for simple tasks (cheapest available)',
                'capabilities': ['general_conversation', 'basic_analysis', 'ultra_fast_response', 'summarization', 'simple_tasks', 'text_summarization'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.0001,  # Updated to correct pricing: $0.10 per 1k tokens
                'speed_rating': 0.95,
                'quality_rating': 0.7,
                'best_for': ['simple_queries', 'general_conversation', 'ultra_cost_sensitive_tasks']
            },
            'o1': {
                'name': 'O1',
                'provider': 'OpenAI',
                'description': 'Ultra-advanced model for complex reasoning and research',
                'capabilities': ['advanced_reasoning', 'research_capabilities', 'complex_analysis', 'highest_accuracy'],
                'max_tokens': 128000,
                'cost_per_1k_tokens': 0.015,
                'speed_rating': 0.6,
                'quality_rating': 0.99,
                'best_for': ['research_tasks', 'complex_reasoning', 'highest_quality_responses']
            },
            'o1-mini': {
                'name': 'O1 Mini',
                'provider': 'OpenAI',
                'description': 'Efficient advanced reasoning model',
                'capabilities': ['advanced_reasoning', 'moderate_analysis', 'good_accuracy'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.0011,
                'speed_rating': 0.7,
                'quality_rating': 0.9,
                'best_for': ['moderate_reasoning', 'balanced_tasks', 'quality_responses']
            },
            'o3': {
                'name': 'O3',
                'provider': 'OpenAI',
                'description': 'Advanced reasoning model for complex tasks',
                'capabilities': ['advanced_reasoning', 'complex_analysis', 'high_accuracy'],
                'max_tokens': 128000,
                'cost_per_1k_tokens': 0.002,
                'speed_rating': 0.7,
                'quality_rating': 0.95,
                'best_for': ['complex_reasoning', 'advanced_tasks', 'high_quality_responses']
            },
            'o3-mini': {
                'name': 'O3 Mini',
                'provider': 'OpenAI',
                'description': 'Efficient reasoning model for moderate tasks',
                'capabilities': ['moderate_reasoning', 'good_accuracy', 'balanced_performance'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.0011,
                'speed_rating': 0.75,
                'quality_rating': 0.85,
                'best_for': ['moderate_reasoning', 'balanced_tasks', 'quality_responses']
            },
            'o4-mini': {
                'name': 'O4 Mini',
                'provider': 'OpenAI',
                'description': 'Latest efficient model for balanced tasks',
                'capabilities': ['moderate_analysis', 'good_accuracy', 'balanced_performance'],
                'max_tokens': 16384,
                'cost_per_1k_tokens': 0.0011,
                'speed_rating': 0.8,
                'quality_rating': 0.88,
                'best_for': ['moderate_complexity', 'balanced_tasks', 'modern_quality_responses']
            }
        }
    
    def select_model(self, 
                    user_query: str, 
                    conversation_context: str = None,
                    user_preferences: Dict = None,
                    query_metadata: Dict = None,
                    context_relevance: float = None) -> Dict:
        """
        Select the optimal model for a user query
        
        Args:
            user_query: The user's input query
            conversation_context: Optional conversation context
            user_preferences: Optional user preferences
            query_metadata: Optional query metadata
            
        Returns:
            Dictionary containing model selection results
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze query requirements
            query_analysis = self._analyze_query_requirements(
                user_query, 
                conversation_context, 
                user_preferences
            )
            
            # Step 2: Get candidate models
            candidate_models = self._get_candidate_models(query_analysis)
            
            # Step 3: Score and rank models (considering context relevance)
            ranked_models = self._rank_models_with_context(candidate_models, query_analysis, context_relevance)
            
            # Step 4: Select best model
            selected_model = ranked_models[0] if ranked_models else self.available_models[self.default_model]
            # Ensure selected_model has an 'id' field
            if 'id' not in selected_model:
                selected_model['id'] = self.default_model
            
            # Step 5: Compile results
            processing_time = time.time() - start_time
            
            # Update selection history
            self._update_selection_history(selected_model, query_analysis, processing_time)
            
            return {
                'selected_model': selected_model['id'],
                'model_info': selected_model,
                'selection_reasoning': self._generate_selection_reasoning(selected_model, query_analysis, context_relevance),
                'confidence_score': self._calculate_selection_confidence(selected_model, query_analysis),
                'estimated_cost': self._estimate_cost(selected_model, query_analysis),
                'estimated_tokens': query_analysis['estimated_tokens'],
                'query_analysis': query_analysis,
                'candidate_models': candidate_models,
                'processing_time': processing_time,
                'agent_info': self.agent_info,
                'metadata': {
                    'cost_sensitivity': self.cost_sensitivity,
                    'performance_preference': self.performance_preference,
                    'models_considered': len(candidate_models),
                    'selection_criteria': list(query_analysis.keys()),
                    'context_relevance': context_relevance
                }
            }
            
        except Exception as e:
            print(f"Model selection error: {e}")
            return self._fallback_model_selection(user_query, str(e))
    
    def _analyze_query_requirements(self, 
                                  user_query: str, 
                                  conversation_context: str = None,
                                  user_preferences: Dict = None) -> Dict:
        """Analyze query to determine requirements"""
        try:
            # LLM-based query analysis
            llm_analysis = self._llm_query_analysis(
                user_query, 
                conversation_context, 
                user_preferences
            )
            
            return llm_analysis
            
        except Exception as e:
            print(f"LLM query analysis error: {e}")
            return self._fallback_query_analysis(user_query)
    
    def _llm_query_analysis(self, 
                           user_query: str, 
                           conversation_context: str = None,
                           user_preferences: Dict = None) -> Dict:
        """Use LLM to analyze query requirements"""
        try:
            # Build context information
            context_info = ""
            if conversation_context:
                context_info += f"\nConversation Context: {conversation_context}"
            if user_preferences:
                context_info += f"\nUser Preferences: {json.dumps(user_preferences)}"
            
            # Create analysis prompt
            prompt = f"""
            You are an AI Model Selection Agent specialized in analyzing queries to determine optimal LLM model requirements.
            
            Analyze the following user query to determine:
            1. Query complexity level
            2. Required capabilities
            3. Estimated token usage
            4. Performance requirements
            5. Cost considerations
            
            User Query: "{user_query}"{context_info}
            
            Provide a JSON response with:
            - complexity_score: float between 0.0 (simple) and 1.0 (very complex)
            - domain: string indicating the query domain (e.g., "health", "technology", "general")
            - required_capabilities: list of required capabilities
            - estimated_tokens: integer estimate of token usage
            - performance_priority: string indicating priority ("speed", "quality", "balanced")
            - cost_sensitivity: string indicating cost sensitivity ("low", "medium", "high")
            
            Response format:
            {{
                "complexity_score": 0.7,
                "domain": "health",
                "required_capabilities": ["detailed_analysis", "medical_knowledge"],
                "estimated_tokens": 500,
                "performance_priority": "quality",
                "cost_sensitivity": "medium"
            }}

            Few-shot examples (guidance):
            Example 1 (simple/fast):
              input: "Summarize this short paragraph"
              output: {{"complexity_score": 0.2, "domain": "general", "required_capabilities": ["general_conversation"], "estimated_tokens": 150, "performance_priority": "speed", "cost_sensitivity": "high"}}
            Example 2 (complex/quality):
              input: "Compare Bayesian and frequentist methods for hierarchical models with code"
              output: {{"complexity_score": 0.85, "domain": "technology", "required_capabilities": ["complex_analysis"], "estimated_tokens": 900, "performance_priority": "quality", "cost_sensitivity": "low"}}

            Output requirements:
            - Return ONLY valid JSON. Do not include backticks or explanations outside JSON.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert AI Model Selection Agent. Analyze queries accurately to determine optimal model requirements."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=300,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            try:
                analysis = json.loads(response.choices[0].message.content.strip())
                
                # Ensure minimum token estimation
                if analysis.get('estimated_tokens', 0) < 50:
                    analysis['estimated_tokens'] = max(len(user_query.split()) * 15, 200)
                
                return analysis
            except json.JSONDecodeError:
                print(f"JSON decode error for query: {user_query}")
                return self._fallback_query_analysis(user_query)
                
        except Exception as e:
            print(f"LLM query analysis error: {e}")
            return self._fallback_query_analysis(user_query)
    
    def _fallback_query_analysis(self, user_query: str) -> Dict:
        """Fallback query analysis when LLM fails"""
        # Basic keyword-based analysis
        query_lower = user_query.lower()
        
        # Simple complexity estimation
        complexity_indicators = [
            'explain', 'analyze', 'compare', 'discuss', 'evaluate', 'research',
            'detailed', 'comprehensive', 'thorough', 'in-depth', 'complex'
        ]
        
        complexity_score = 0.3  # Default to simple
        for indicator in complexity_indicators:
            if indicator in query_lower:
                complexity_score += 0.2
        
        complexity_score = min(complexity_score, 1.0)
        
        # Estimate tokens based on query length and complexity
        base_tokens = len(user_query.split()) * 15  # More realistic estimate (words to tokens)
        estimated_tokens = max(base_tokens, 200)  # Minimum 200 tokens for a proper response
        
        return {
            "complexity_score": complexity_score,
            "domain": "general",
            "required_capabilities": ["general_conversation", "basic_analysis"],
            "estimated_tokens": estimated_tokens,
            "performance_priority": "balanced",
            "cost_sensitivity": "medium"
        }
    
    def _get_candidate_models(self, query_analysis: Dict) -> List[Dict]:
        """Get candidate models based on query requirements"""
        candidates = []
        
        for model_id, model_info in self.available_models.items():
            # Check if model has required capabilities
            if self._model_matches_requirements(model_info, query_analysis):
                candidate = model_info.copy()
                candidate['id'] = model_id
                candidates.append(candidate)
        
        return candidates
    
    def _model_matches_requirements(self, model_info: Dict, query_analysis: Dict) -> bool:
        """Check if model matches query requirements"""
        required_capabilities = query_analysis.get('required_capabilities', [])
        
        # If no capabilities required, all models match
        if not required_capabilities:
            return True
        
        # Check if at least one required capability matches
        model_capabilities = model_info.get('capabilities', [])
        for capability in required_capabilities:
            if capability in model_capabilities:
                return True
        
        return False
    
    def _rank_models(self, candidate_models: List[Dict], query_analysis: Dict) -> List[Dict]:
        """Rank candidate models by suitability"""
        if not candidate_models:
            return []
        
        # Score each candidate
        scored_models = []
        for model in candidate_models:
            score = self._calculate_model_score(model, query_analysis)
            scored_models.append((model, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # Return models in ranked order
        return [model for model, score in scored_models]
    
    def _rank_models_with_context(self, candidate_models: List[Dict], query_analysis: Dict, context_relevance: float = None) -> List[Dict]:
        """Rank candidate models by suitability, considering context relevance"""
        if not candidate_models:
            return []
        
        # Score each candidate
        scored_models = []
        for model in candidate_models:
            score = self._calculate_model_score_with_context(model, query_analysis, context_relevance)
            scored_models.append((model, score))
        
        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # Return models in ranked order
        return [model for model, score in scored_models]
    
    def _calculate_model_score(self, model: Dict, query_analysis: Dict) -> float:
        """Calculate suitability score for a model"""
        complexity_score = query_analysis.get('complexity_score', 0.5)
        performance_priority = query_analysis.get('performance_priority', 'balanced')
        cost_sensitivity = query_analysis.get('cost_sensitivity', 'medium')
        
        # Base score from model ratings
        base_score = (model.get('quality_rating', 0.5) + model.get('speed_rating', 0.5)) / 2
        
        # Complexity adjustment
        if complexity_score > 0.7:
            # Complex queries prefer quality
            quality_weight = 0.8
            speed_weight = 0.2
        elif complexity_score < 0.3:
            # Simple queries prefer speed
            quality_weight = 0.2
            speed_weight = 0.8
        else:
            # Balanced queries
            quality_weight = 0.5
            speed_weight = 0.5
        
        # Performance preference adjustment
        if performance_priority == 'quality':
            quality_weight *= 1.5
        elif performance_priority == 'speed':
            speed_weight *= 1.5
        
        # Cost sensitivity adjustment
        cost_multiplier = 1.0
        if cost_sensitivity == 'high':
            cost_multiplier = 0.3  # Strongly prefer cheaper models
        elif cost_sensitivity == 'low':
            cost_multiplier = 1.3  # Prefer better models
        
        # Direct cost adjustment - favor cheaper models for simple queries, quality for complex
        cost_per_1k = model.get('cost_per_1k_tokens', 0.001)
        
        if complexity_score < 0.3:
            # Simple queries - heavily favor cost
            cost_penalty = cost_per_1k * 1000
            quality_bonus = 0
        elif complexity_score > 0.7:
            # Complex queries - favor quality over cost
            cost_penalty = cost_per_1k * 100
            quality_bonus = model.get('quality_rating', 0.5) * 0.5
        else:
            # Moderate queries - balanced approach
            cost_penalty = cost_per_1k * 500
            quality_bonus = model.get('quality_rating', 0.5) * 0.2
        
        # Calculate final score
        final_score = (
            base_score * 0.3 +
            model.get('quality_rating', 0.5) * quality_weight * 0.2 +
            model.get('speed_rating', 0.5) * speed_weight * 0.2 +
            quality_bonus -
            cost_penalty * 0.3  # Subtract cost penalty
        ) * cost_multiplier
        
        return min(max(final_score, 0.0), 1.0)
    
    def _calculate_model_score_with_context(self, model: Dict, query_analysis: Dict, context_relevance: float = None) -> float:
        """Calculate suitability score for a model, considering context relevance"""
        # Get base score
        base_score = self._calculate_model_score(model, query_analysis)
        
        # If no context relevance provided, return base score
        if context_relevance is None:
            return base_score
        
        # Context relevance adjustment
        # For low relevance queries, heavily favor cheaper models
        # For high relevance queries, allow more expensive models
        context_multiplier = 1.0
        
        if context_relevance < 0.3:
            # Very low relevance - strongly prefer cheapest models
            context_multiplier = 0.3
        elif context_relevance < 0.5:
            # Low relevance - prefer cheaper models
            context_multiplier = 0.6
        elif context_relevance < 0.7:
            # Medium relevance - balanced approach
            context_multiplier = 0.8
        else:
            # High relevance - allow expensive models
            context_multiplier = 1.0
        
        # Apply context multiplier to base score
        final_score = base_score * context_multiplier
        
        return min(max(final_score, 0.0), 1.0)
    
    def _generate_selection_reasoning(self, selected_model: Dict, query_analysis: Dict, context_relevance: float = None) -> str:
        """Generate human-readable reasoning for model selection"""
        complexity = query_analysis.get('complexity_score', 0.5)
        domain = query_analysis.get('domain', 'general')
        capabilities = query_analysis.get('required_capabilities', [])
        
        reasoning_parts = []
        
        if complexity > 0.7:
            reasoning_parts.append("Complex query requiring detailed analysis")
        elif complexity < 0.3:
            reasoning_parts.append("Simple query suitable for fast response")
        else:
            reasoning_parts.append("Moderate complexity query")
        
        if context_relevance is not None:
            if context_relevance < 0.3:
                reasoning_parts.append("Low context relevance - prioritizing cost efficiency")
            elif context_relevance < 0.5:
                reasoning_parts.append("Moderate context relevance - balanced cost/quality")
            else:
                reasoning_parts.append("High context relevance - prioritizing quality")
        
        if domain != 'general':
            reasoning_parts.append(f"Domain-specific requirements for {domain}")
        
        if capabilities:
            reasoning_parts.append(f"Required capabilities: {', '.join(capabilities)}")
        
        reasoning_parts.append(f"Selected {selected_model['name']} for optimal performance")
        
        return ". ".join(reasoning_parts) + "."
    
    def _calculate_selection_confidence(self, selected_model: Dict, query_analysis: Dict) -> float:
        """Calculate confidence in the model selection"""
        # Base confidence from model capabilities match
        required_capabilities = query_analysis.get('required_capabilities', [])
        available_capabilities = selected_model.get('capabilities', [])
        
        capability_match = sum(1 for cap in required_capabilities if cap in available_capabilities)
        capability_score = capability_match / max(len(required_capabilities), 1)
        
        # Complexity alignment
        complexity_score = query_analysis.get('complexity_score', 0.5)
        model_quality = selected_model.get('quality_rating', 0.5)
        
        complexity_alignment = 1.0 - abs(complexity_score - model_quality)
        
        # Overall confidence
        confidence = (capability_score * 0.6 + complexity_alignment * 0.4)
        
        return min(max(confidence, 0.0), 1.0)
    
    def _estimate_cost(self, selected_model: Dict, query_analysis: Dict) -> float:
        """Estimate cost for the selected model"""
        estimated_tokens = query_analysis.get('estimated_tokens', 300)
        cost_per_1k = selected_model.get('cost_per_1k_tokens', 0.001)
        
        # Ensure we have a reasonable token estimate
        if estimated_tokens < 50:
            estimated_tokens = 150  # Minimum reasonable tokens for a response
        
        return (estimated_tokens / 1000) * cost_per_1k
    
    def _update_selection_history(self, selected_model: Dict, query_analysis: Dict, processing_time: float):
        """Update selection history for learning"""
        history_entry = {
            'timestamp': time.time(),
            'selected_model': selected_model['id'],
            'query_analysis': query_analysis,
            'processing_time': processing_time
        }
        
        self.selection_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.selection_history) > 100:
            self.selection_history = self.selection_history[-100:]
    
    def _fallback_model_selection(self, user_query: str, error: str) -> Dict:
        """Fallback model selection when analysis fails"""
        default_model_info = self.available_models[self.default_model].copy()
        default_model_info['id'] = self.default_model
        
        return {
            'selected_model': self.default_model,
            'model_info': default_model_info,
            'selection_reasoning': f"Fallback to default model due to error: {error}",
            'confidence_score': 0.3,
            'estimated_cost': 0.001,
            'estimated_tokens': 300,
            'query_analysis': {'complexity_score': 0.5, 'domain': 'general'},
            'candidate_models': [default_model_info],
            'processing_time': 0.0,
            'agent_info': self.agent_info,
            'metadata': {
                'cost_sensitivity': self.cost_sensitivity,
                'performance_preference': self.performance_preference,
                'models_considered': 1,
                'selection_criteria': ['fallback'],
                'error': error
            }
        }
    
    def update_config(self, 
                     available_models: Dict = None,
                     default_model: str = None,
                     cost_sensitivity: str = None,
                     performance_preference: str = None):
        """Update agent configuration"""
        if available_models:
            self.available_models = available_models
            self.agent_info['available_models_count'] = len(available_models)
        if default_model:
            self.default_model = default_model
            self.agent_info['default_model'] = default_model
        if cost_sensitivity:
            self.cost_sensitivity = cost_sensitivity
            self.agent_info['cost_sensitivity'] = cost_sensitivity
        if performance_preference:
            self.performance_preference = performance_preference
            self.agent_info['performance_preference'] = performance_preference
    
    def get_agent_info(self) -> Dict:
        """Get agent information and capabilities"""
        return self.agent_info.copy()
    
    def get_available_models(self) -> Dict:
        """Get available models configuration"""
        return self.available_models.copy()
    
    def add_model(self, model_id: str, model_info: Dict):
        """Add a new model to available models"""
        self.available_models[model_id] = model_info
        self.agent_info['available_models_count'] = len(self.available_models)
    
    def remove_model(self, model_id: str):
        """Remove a model from available models"""
        if model_id in self.available_models and model_id != self.default_model:
            del self.available_models[model_id]
            self.agent_info['available_models_count'] = len(self.available_models)
    
    def get_selection_history(self) -> List[Dict]:
        """Get model selection history"""
        return self.selection_history.copy()
    
    def clear_selection_history(self):
        """Clear selection history"""
        self.selection_history = []
