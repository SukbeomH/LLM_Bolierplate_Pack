"""Agent Observability & Logging Module.

Provides free observability using Python's built-in logging.
Tracks:
- Agent execution duration
- State transitions
- Estimated LLM costs
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging configuration
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'agent_execution.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AgentLogger")

class AgentLogger:
    """Free observability tool using standard logging."""

    # Cost per 1M tokens (approximate as of 2024/2026)
    MODEL_COSTS = {
        "gpt-4o": {"input": 5.00, "output": 15.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "gemini-2.0-flash-exp": {"input": 0.00, "output": 0.00},  # Free tier assumption
    }

    @staticmethod
    def log_agent_start(agent_name: str, state: Dict[str, Any]):
        """Log start of agent execution."""
        log_entry = {
            "event": "agent_start",
            "agent": agent_name,
            "timestamp": datetime.now().isoformat(),
            "state_summary": {k: str(v)[:100] for k, v in state.items() if k != "messages"}
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_agent_end(agent_name: str, duration: float, result_keys: list):
        """Log end of agent execution."""
        log_entry = {
            "event": "agent_end",
            "agent": agent_name,
            "duration_seconds": round(duration, 4),
            "timestamp": datetime.now().isoformat(),
            "updated_keys": result_keys
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def log_llm_call(
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration: float
    ):
        """Log LLM call details and estimated cost."""
        cost = AgentLogger._calculate_cost(model, input_tokens, output_tokens)

        log_entry = {
            "event": "llm_call",
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_seconds": round(duration, 4),
            "estimated_cost_usd": round(cost, 6),
            "timestamp": datetime.now().isoformat()
        }
        logger.info(json.dumps(log_entry))

    @staticmethod
    def _calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost based on model pricing."""
        # Find matching model key (partial match)
        pricing = None
        for key, price in AgentLogger.MODEL_COSTS.items():
            if key in model:
                pricing = price
                break

        if not pricing:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost

# Usage helper
def track_execution(agent_name: str):
    """Decorator to track agent execution time."""
    def decorator(func):
        def wrapper(state, *args, **kwargs):
            AgentLogger.log_agent_start(agent_name, state)
            start_time = time.time()
            try:
                result = func(state, *args, **kwargs)
                duration = time.time() - start_time

                # Determine what changed (heuristic)
                updated_keys = []
                if hasattr(result, "update"):
                    updated_keys = list(result.update.keys())

                AgentLogger.log_agent_end(agent_name, duration, updated_keys)
                return result
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                raise e
        return wrapper
    return decorator
