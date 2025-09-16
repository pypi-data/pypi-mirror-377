from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage


@dataclass
class KGraphWorker(ABC):
    """
    Base class for KGraph workers that can generate subgraphs for LangGraph.
    
    Each worker represents a specific type of processing capability that can be
    dynamically added to a LangGraph execution graph. Workers are responsible for:
    1. Defining their processing logic
    2. Generating their own subgraph structure
    3. Managing their internal state and execution flow
    """
    
    name: str
    llm: ChatOpenAI
    system_directive: str = ""
    required_inputs: Optional[List[str]] = None
    max_iters: int = 6
    
    def __post_init__(self):
        if self.required_inputs is None:
            self.required_inputs = []
    
    @abstractmethod
    def build_subgraph(self, graph_builder: StateGraph, occurrence_id: str) -> Tuple[str, str]:
        """
        Build and add this worker's subgraph to the provided StateGraph.
        
        Args:
            graph_builder: The StateGraph to add nodes and edges to
            occurrence_id: Unique identifier for this worker occurrence in the graph
            
        Returns:
            Tuple of (entry_node_id, exit_node_id) for connecting to other parts of the graph
        """
        pass
    
    def _safe_node_id(self, occurrence_id: str, *parts: str) -> str:
        """
        Generate a safe node ID by combining occurrence_id with additional parts.
        """
        import re
        combined = "__".join([occurrence_id] + list(parts))
        return re.sub(r"[^A-Za-z0-9_.-]", "_", combined)
    
    def _get_worker_slot(self, state: Dict[str, Any], occurrence_id: str) -> Dict[str, Any]:
        """
        Get or create the worker's slot in the execution state.
        """
        # Ensure work exists in state
        if "work" not in state:
            state["work"] = {}
        
        # Get existing slot or create new one
        if occurrence_id not in state["work"]:
            state["work"][occurrence_id] = {
                "iters": 0,
                "messages": []
            }
        
        # Return reference to the slot in state (not a copy)
        return state["work"][occurrence_id]
    
    def _get_activation(self, state: Dict[str, Any], occurrence_id: str) -> Dict[str, Any]:
        """
        Get the activation data for this worker occurrence.
        """
        # Standard location: state["agent_data"]["activation"]
        agent_data = state.get("agent_data", {})
        activation_map = agent_data.get("activation", {})
        return activation_map.get(occurrence_id, {"prompt": "", "args": {}})
    
    def _finalize_result(self, state: Dict[str, Any], occurrence_id: str, result_text: str) -> Dict[str, Any]:
        """
        Finalize the worker's result and clean up its working state.
        """
        # Standard location: state["agent_data"]
        agent_data = state.get("agent_data", {})
        results = dict(agent_data.get("results", {}))
        errors = dict(agent_data.get("errors", {}))
        activation_map = dict(agent_data.get("activation", {}))
        work = dict(agent_data.get("work", {}))
        
        # Store the result
        activation = activation_map.get(occurrence_id, {})
        payload = {
            "result_text": result_text,
            "args_used": activation.get("args", {})
        }
        results[occurrence_id] = payload
        
        # Clean up working state
        work.pop(occurrence_id, None)
        activation_map.pop(occurrence_id, None)
        
        # Return updated agent_data structure
        return {
            **state,
            "agent_data": {
                **agent_data,
                "results": results,
                "errors": errors,
                "activation": activation_map,
                "work": work
            }
        }
