import os
import sys

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_agents import SecurityAgent


def make_agent():
    return SecurityAgent(model="gpt-4o", threat_threshold=0.7, enable_detailed_analysis=True)


def test_llm_failure_triggers_conservative_block():
    agent = make_agent()
    # Force the LLM call to fail by passing a very large input (simulating API error or similar)
    text = "x" * 100000
    result = agent.analyze_security(text)
    assert result["blocked"] is True
    assert result["threat_level"] in {"high", "critical"}
    assert result["threat_score"] >= 0.8


def test_conservative_metrics_shape_present():
    agent = make_agent()
    text = "x" * 100000
    result = agent.analyze_security(text)
    metrics = result.get("metrics", {})
    # Ensure metrics include expected categories with empty arrays
    for cat in [
        'sexual', 'violence', 'hate_speech', 'profanity', 'weapons', 'crime', 'prompt_injection', 'jailbreak']:
        assert cat in metrics
        for k in ['f1', 'precision', 'recall', 'accuracy']:
            assert isinstance(metrics[cat].get(k, None), list)


