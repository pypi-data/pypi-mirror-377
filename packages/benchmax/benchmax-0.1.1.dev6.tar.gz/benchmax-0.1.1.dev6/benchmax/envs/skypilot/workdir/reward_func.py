from typing import Any
from fastmcp import Client

def reward_function(
    completion: str,
    ground_truth: Any,
    workspace: str,
    mcp_client: Client,
    **kwargs: Any
) -> float:
    """Compute the reward for a given model completion."""
    print(f"Workspace for reward function: {workspace}")
    return 1.0 if completion.strip() == ground_truth.strip() else 0.0


reward_functions = [reward_function]