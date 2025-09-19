from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Protocol, TypedDict

class StandardizedExample(TypedDict):
    prompt: str
    ground_truth: Any
    init_rollout_args: Optional[Dict[str, Any]]

@dataclass
class ToolDefinition:
    """Definition of a tool's interface"""
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None

class RewardFunction(Protocol):
    """Function that evaluates model interactions"""
    def __call__(
        self,
        completion: str,     # Model's generated completion/response
        ground_truth: Any,   # Expected/correct output to compare against
        workspace: str,      # Current workspace of the rollout
        **kwargs: Any        # Additional context for reward computation
    ) -> float:             # Reward score (typically in range [0, 1])
        ...
