from __future__ import annotations

from typing import Dict, Any, Tuple
from dataclasses import dataclass

from langgraph.graph import StateGraph
from langgraph.runtime import get_runtime
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from kgraphplanner.worker.kgraph_worker import KGraphWorker


@dataclass
class KGraphChatWorker(KGraphWorker):
    """
    A simple chat worker that performs a single LLM call to respond to a message.
    
    This worker creates a subgraph with:
    - Entry node: chat_node (performs LLM call)
    - Exit node: chat_node (same node, single step)
    
    The worker takes the activation prompt and args, makes an LLM call,
    and stores the response in the state.
    """
    
    def build_subgraph(self, graph_builder: StateGraph, occurrence_id: str) -> Tuple[str, str]:
        """
        Build a simple single-node subgraph for chat processing.
        
        Returns:
            Tuple of (entry_node_id, exit_node_id) - both are the same for this simple worker
        """
        chat_node_id = self._safe_node_id(occurrence_id, "chat")
        
        async def chat_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Perform a single LLM call and return the response."""
            runtime = get_runtime()
            writer = runtime.stream_writer
            
            # Get activation data
            activation = self._get_activation(state, occurrence_id)
            prompt = activation.get("prompt", "")
            args = activation.get("args", {})
            
            print(f"🔧 DEBUG: Chat worker '{occurrence_id}' checking activation: {activation}")
            
            # Only proceed if we have actual activation data
            if not prompt and not args:
                print(f"🔧 DEBUG: Chat worker '{occurrence_id}' has no activation, skipping")
                return state
            
            print(f"🔧 DEBUG: Chat worker '{occurrence_id}' processing with prompt: {prompt[:100]}...")
            print(f"🔧 DEBUG: Chat worker '{occurrence_id}' args keys: {list(args.keys()) if args else 'None'}")
            
            # Build messages for LLM
            messages = []
            if self.system_directive:
                messages.append(SystemMessage(content=self.system_directive))
            
            if prompt:
                messages.append(SystemMessage(content=f"Task instructions: {prompt}"))
            
            if args:
                messages.append(SystemMessage(content=f"Task args: {args}"))
            
            # Add a human message to trigger response
            user_query = args.get("query", args.get("message", args.get("worker_output", "Please respond based on the task instructions.")))
            messages.append(HumanMessage(content=str(user_query)))
            
            print(f"🔧 DEBUG: Chat worker '{occurrence_id}' sending {len(messages)} messages to LLM")
            print(f"🔧 DEBUG: Chat worker '{occurrence_id}' user query length: {len(str(user_query))}")
            
            writer({
                "phase": "chat_start",
                "node": occurrence_id,
                "worker": self.name,
                "activation": activation
            })
            
            try:
                # Make LLM call
                response = await self.llm.ainvoke(messages)
                result_text = response.content if hasattr(response, 'content') else str(response)
                
                writer({
                    "phase": "chat_complete",
                    "node": occurrence_id,
                    "worker": self.name,
                    "result": result_text[:200] + "..." if len(result_text) > 200 else result_text
                })
                
                # Store result in agent_data.decisions for resolve worker to access
                agent_data = dict(state.get("agent_data", {}))
                decisions = dict(agent_data.get("decisions", {}))
                decisions[occurrence_id] = {
                    "type": "final",
                    "tool_name": None,
                    "arguments": {},
                    "tool_call_id": None,
                    "answer": result_text
                }
                agent_data["decisions"] = decisions
                
                print(f"🔧 DEBUG: Chat worker '{occurrence_id}' stored final decision in agent_data.decisions")
                
                # Also finalize using base method for cleanup
                final_state = self._finalize_result(state, occurrence_id, result_text)
                final_state["agent_data"] = {**final_state.get("agent_data", {}), **agent_data}
                return final_state
                
            except Exception as e:
                writer({
                    "phase": "chat_error",
                    "node": occurrence_id,
                    "worker": self.name,
                    "error": str(e)
                })
                
                # Store error result in agent_data.decisions for resolve worker to access
                error_result = f"Chat error: {str(e)}"
                agent_data = dict(state.get("agent_data", {}))
                decisions = dict(agent_data.get("decisions", {}))
                decisions[occurrence_id] = {
                    "type": "final",
                    "tool_name": None,
                    "arguments": {},
                    "tool_call_id": None,
                    "answer": error_result
                }
                agent_data["decisions"] = decisions
                
                # Also finalize using base method for cleanup
                final_state = self._finalize_result(state, occurrence_id, error_result)
                final_state["agent_data"] = {**final_state.get("agent_data", {}), **agent_data}
                return final_state
        
        # Add the single node to the graph
        graph_builder.add_node(chat_node_id, chat_node)
        
        # Return the same node as both entry and exit
        return chat_node_id, chat_node_id
