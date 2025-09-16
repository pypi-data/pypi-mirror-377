"""
Agent Evaluation CLI

Run large-scale evaluations for the Security, Context, and Model Selection agents
using a JSONL dataset. Supports thousands of queries with retry, simple
concurrency, and a summary report. Requires OPENAI_API_KEY.

Usage examples:
  python examples/eval_agents.py --data examples/data/sample_eval.jsonl --agent all --max 1000 --concurrency 4 --report report.json
  python examples/eval_agents.py --data examples/data/sample_eval.jsonl --agent security --dry-run

Dataset JSONL schema (one JSON object per line):
  {
    "agent": "security" | "context" | "model_selection",  # required if --agent all, else optional
    "input": "user query text",
    "expected": { ... },    # expected outcome per agent type (see below)
    "meta": { ... }         # optional metadata
  }

Expected field examples:
- security:
    {"blocked": true, "category": "sexual"}           # category optional
- context:
    {"is_contextual": false}                            # can also include min_relevance: 0.6
- model_selection:
    {"selected": "gpt-3.5-turbo"} or {"selected_in": ["gpt-3.5-turbo","gpt-4o-mini"]}

Report JSON structure (written to --report if provided):
  {
    "summary": { totals... },
    "by_agent": { "security": {...}, "context": {...}, "model_selection": {...} },
    "failures_sample": [ up to 50 examples ]
  }
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from ai_agents import SecurityAgent, ContextAgent, ModelSelectionAgent  # noqa: E402


def read_jsonl(path: str, agent_filter: Optional[str]) -> List[Dict[str, Any]]:
    data: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if agent_filter and obj.get("agent") and obj.get("agent") != agent_filter:
                    continue
                data.append(obj)
            except json.JSONDecodeError:
                continue
    return data


def build_agents() -> Dict[str, Any]:
    # Defaults align with examples/agent_smoke_test.py
    security = SecurityAgent(model="gpt-4o", threat_threshold=0.7, enable_detailed_analysis=True)
    context = ContextAgent(
        chatbot_name="AI Agents Demo Bot",
        chatbot_description=(
            "A demonstration chatbot showcasing three AI agents working together: "
            "Security, Context, and Model Selection"
        ),
        keywords=["demo", "agents", "security", "context", "model", "selection"],
        model="gpt-3.5-turbo",
    )
    model_sel = ModelSelectionAgent(cost_sensitivity="medium", performance_preference="balanced")
    return {
        "security": security,
        "context": context,
        "model_selection": model_sel,
    }


def evaluate_security(agent: SecurityAgent, item: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    expected = item.get("expected", {}) or {}
    res = agent.analyze_security(item["input"])
    ok = True
    if "blocked" in expected:
        ok = ok and (bool(res.get("blocked")) == bool(expected["blocked"]))
    exp_cat = expected.get("category")
    if exp_cat:
        llm = (res.get("llm_analysis") or {})
        primary = (llm.get("threat_type") or "").lower()
        ok = ok and (primary == exp_cat.lower())
    return ok, {"result": res}


def evaluate_context(agent: ContextAgent, item: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    expected = item.get("expected", {}) or {}
    res = agent.analyze_context(item["input"], conversation_history=item.get("history") or [])
    ok = True
    if "is_contextual" in expected:
        ok = ok and (bool(res.get("is_contextual")) == bool(expected["is_contextual"]))
    min_rel = expected.get("min_relevance")
    if isinstance(min_rel, (int, float)):
        ok = ok and (float(res.get("relevance_score", 0.0)) >= float(min_rel))
    return ok, {"result": res}


def evaluate_model_selection(agent: ModelSelectionAgent, item: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    expected = item.get("expected", {}) or {}
    res = agent.select_model(item["input"], conversation_context=item.get("context"))
    selected = res.get("selected_model")
    ok = True
    if "selected" in expected:
        ok = ok and (selected == expected["selected"]) 
    if "selected_in" in expected:
        ok = ok and (selected in list(expected["selected_in"]))
    return ok, {"result": res}


def worker(item: Dict[str, Any], agents: Dict[str, Any], dry_run: bool, retries: int, retry_sleep: float) -> Dict[str, Any]:
    agent_name = item.get("agent")
    if agent_name not in agents:
        return {"ok": False, "error": f"unknown agent: {agent_name}", "item": item}

    if dry_run:
        return {"ok": True, "skipped": True, "item": item}

    attempt = 0
    while True:
        try:
            if agent_name == "security":
                ok, details = evaluate_security(agents[agent_name], item)
            elif agent_name == "context":
                ok, details = evaluate_context(agents[agent_name], item)
            else:
                ok, details = evaluate_model_selection(agents[agent_name], item)
            return {"ok": ok, "details": details, "item": item}
        except Exception as e:
            attempt += 1
            if attempt > retries:
                return {"ok": False, "error": str(e), "item": item}
            time.sleep(retry_sleep)


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r.get("ok"))
    failed = total - passed
    by_agent: Dict[str, Dict[str, int]] = {}
    for r in results:
        name = r.get("item", {}).get("agent", "unknown")
        s = by_agent.setdefault(name, {"total": 0, "passed": 0, "failed": 0})
        s["total"] += 1
        if r.get("ok"):
            s["passed"] += 1
        else:
            s["failed"] += 1
    failure_rate = (failed / total) if total else 0.0
    return {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "failure_rate": round(failure_rate, 4),
            "upgrade_prompt_recommended": failure_rate >= 0.10,
        },
        "by_agent": by_agent,
    }


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Evaluate agents on a JSONL dataset")
    parser.add_argument("--data", required=True, help="Path to JSONL dataset")
    parser.add_argument("--agent", choices=["all", "security", "context", "model_selection"], default="all")
    parser.add_argument("--max", type=int, default=0, help="Limit number of samples (0 = all)")
    parser.add_argument("--concurrency", type=int, default=2, help="Thread concurrency")
    parser.add_argument("--retries", type=int, default=2, help="Retries per item on error")
    parser.add_argument("--retry-sleep", type=float, default=1.5, help="Sleep between retries (seconds)")
    parser.add_argument("--report", type=str, default="", help="Write JSON report to this path")
    parser.add_argument("--dry-run", action="store_true", help="Validate dataset only; do not call APIs")
    args = parser.parse_args()

    if not args.dry_run and not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set. Use --dry-run to validate without calling APIs.")
        sys.exit(1)

    agent_filter = None if args.agent == "all" else args.agent
    items = read_jsonl(args.data, agent_filter)
    if args.max and args.max > 0:
        items = items[: args.max]
    if not items:
        print("No items to evaluate.")
        sys.exit(1)

    if args.dry_run:
        print(f"Dry-run OK. Loaded {len(items)} items.")
        sys.exit(0)

    agents = build_agents()

    started = time.time()
    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futs = [pool.submit(worker, item, agents, False, args.retries, args.retry_sleep) for item in items]
        for fut in as_completed(futs):
            results.append(fut.result())

    report = summarize(results)

    # Include up to 50 failure samples
    failures = [r for r in results if not r.get("ok")]
    report["failures_sample"] = failures[:50]

    elapsed = time.time() - started
    s = report["summary"]
    print(
        f"\nDone in {elapsed:.2f}s | Total: {s['total']} | Passed: {s['passed']} | "
        f"Failed: {s['failed']} | Failure rate: {s['failure_rate']*100:.2f}%"
    )
    if s.get("upgrade_prompt_recommended"):
        print("Recommendation: Failure rate >= 10%. Consider upgrading prompts/config.")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()





