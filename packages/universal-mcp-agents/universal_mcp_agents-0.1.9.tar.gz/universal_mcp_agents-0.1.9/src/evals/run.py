import argparse
import asyncio
from datetime import datetime
from typing import Any

from langsmith import Client, aevaluate
from langsmith.evaluation import RunEvaluator
from universal_mcp.agentr.client import AgentrClient
from universal_mcp.agentr.registry import AgentrRegistry

from evals.dataset import load_dataset
from evals.evaluators import (
    correctness_evaluator,
    exact_match_evaluator,
    trajectory_evaluator,
    tool_node_evaluator,
)
from universal_mcp.agents import get_agent
from universal_mcp.agents.base import BaseAgent
from universal_mcp.agents.utils import messages_to_list


# 1. Agent Factory
def build_agent(agent_name: str):
    """
    Factory function to get an agent instance by name.
    """
    client = AgentrClient()
    common_params = {
        "instructions": "You are a helpful assistant. Respond to the final answer in one or two words. Eg, if the answer is 4, you should respond with '4'. Do not provide with any explanation",
        "model": "anthropic/claude-4-sonnet-20250514",
        "registry": AgentrRegistry(client=client) if agent_name != "simple" else None,
    }
    agent = get_agent(agent_name)(name=agent_name, **common_params)
    return agent



# 2. Evaluator Registry
EVALUATORS: dict[str, Any] = {
    "llm_as_judge": correctness_evaluator,
    "exact_match": exact_match_evaluator,
    "trajectory": trajectory_evaluator,
    "tool_node": tool_node_evaluator,
}


def get_evaluator(evaluator_name: str) -> RunEvaluator:
    """
    Retrieves an evaluator from the registry.
    """
    evaluator = EVALUATORS.get(evaluator_name)
    if evaluator is None:
        raise ValueError(
            f"Unknown evaluator: {evaluator_name}. Available evaluators: {', '.join(EVALUATORS.keys())}"
        )
    return evaluator



async def agent_runner(agent: BaseAgent, inputs: dict) -> dict:
    """
    Runs the agent and returns a dictionary with the final output.
    """
    result = await agent.invoke(user_input=inputs["user_input"])
    messages = messages_to_list(result["messages"])
    return_result = {"output": messages}
    if "tool_config" in result:
        return_result["tool_config"] = result["tool_config"]
    return return_result

async def main(agent_name: str, dataset_path: str, evaluator_name: str):
    """
    The main function for the evaluation CLI.
    """

    # 1. Get the agent and evaluator
    agent = build_agent(agent_name)
    evaluator = get_evaluator(evaluator_name)

    # Create a callable for aevaluate
    async def target_func(inputs: dict):
        return await agent_runner(agent, inputs)

    # 2. Load the dataset from file
    dataset_examples = load_dataset(dataset_path)

    # 3. Upload dataset to LangSmith for the evaluation run
    client = Client()
    dataset_name = f"{dataset_path.split('/')[-1].split('.')[0]}"
    # dataset_name = f"{agent_name}-{evaluator_name}-eval-dataset"
    try:
        # If dataset with same name and examples exists, read it.
        # Otherwise, a new one is created.
        dataset = client.create_dataset(
            dataset_name,
            description=f"Dataset for {agent_name} evaluation with {evaluator_name}.",
        )
        for example in dataset_examples:
            client.create_example(
                inputs={"user_input": example["user_input"]},
                outputs={
                    "expected_output": example.get("expected_output", ""), 
                    "required_tools": example.get("required_tools", {})
                },
                dataset_id=dataset.id,
            )
    except Exception:
        pass

    # 4. Run the evaluation
    await aevaluate(
        target_func,
        data=dataset_name,  # Pass the dataset name
        evaluators=[evaluator],
        experiment_prefix=f"{agent_name}-{evaluator_name}-eval",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluations on different agents.")
    parser.add_argument(
        "agent",
        type=str,
        help="The name of the agent to evaluate.",
    )
    parser.add_argument(
        "dataset",
        type=str,
        help="Path to the dataset file (e.g., src/evals/example_dataset.jsonl).",
    )
    parser.add_argument(
        "evaluator",
        type=str,
        choices=list(EVALUATORS.keys()),
        help="The name of the evaluator to use.",
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            agent_name=args.agent,
            dataset_path=args.dataset,
            evaluator_name=args.evaluator,
        )
    )
