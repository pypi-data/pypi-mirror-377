from __future__ import annotations

from typing import Dict, Any, Tuple, List, Optional, Literal, Type
from dataclasses import dataclass, field
import json
import asyncio

from pydantic import BaseModel, Field, ConfigDict
from langgraph.graph import StateGraph, END
from langgraph.runtime import get_runtime
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import BaseTool

from kgraphplanner.worker.kgraph_worker import KGraphWorker


@dataclass
class KGraphToolWorker(KGraphWorker):
    """
    A tool worker that can decide whether to use tools or generate a final response.
    
    This worker creates a subgraph with:
    - Entry node: decision_node (decides tool vs final)
    - Tool node: tool_node (executes selected tool)
    - Exit node: finalize_node (generates final response)
    
    The decision node loops back to itself after tool execution until
    the worker decides to generate a final response.
    """
    
    tool_manager: Any = None
    available_tool_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize after dataclass creation."""
        super().__post_init__()
        if self.tool_manager is None:
            raise ValueError("tool_manager must be provided to KGraphToolWorker")
        if not self.available_tool_ids:
            raise ValueError("available_tool_ids must be provided and non-empty")
    
    def get_available_tools(self) -> Dict[str, BaseTool]:
        """Get tools that are available to this worker based on tool IDs."""
        tools = {}
        for tool_id in self.available_tool_ids:
            tool = self.tool_manager.get_tool(tool_id)
            if tool:
                tools[tool_id] = tool.get_tool_function()
        return tools
    
    def _make_decision_model(self) -> Type[BaseModel]:
        """Create a Pydantic model for structured decision output."""
        tool_keys = tuple(self.available_tool_ids)
        ToolNameLit = Literal[tool_keys] if tool_keys else Literal["__no_tools__"]
        
        def _require_all_props(schema: dict) -> None:
            """Make all properties required for function calling."""
            props = schema.get("properties")
            if isinstance(props, dict):
                schema["required"] = list(props.keys())
        
        class WorkerDecision(BaseModel):
            model_config = ConfigDict(extra="forbid", json_schema_extra=_require_all_props)
            type: Literal["tool", "final"]
            tool_name: Optional[ToolNameLit] = None
            arguments: Dict[str, Any] = Field(default_factory=dict)
            answer: Optional[str] = None
        
        return WorkerDecision
    
    def build_subgraph(self, graph_builder: StateGraph, occurrence_id: str) -> Tuple[str, str]:
        """
        Build a three-node subgraph for tool-based processing.
        
        Returns:
            Tuple of (entry_node_id, exit_node_id)
        """
        decision_node_id = self._safe_node_id(occurrence_id, "decision")
        tool_node_id = self._safe_node_id(occurrence_id, "tool")
        finalize_node_id = self._safe_node_id(occurrence_id, "finalize")
        
        async def decision_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Make decisions about tool usage based on the current state."""
            runtime = get_runtime()
            writer = runtime.stream_writer
            
            # Get activation data for this worker
            activation = self._get_activation(state, occurrence_id)
            prompt = activation.get("prompt", "")
            args = activation.get("args", {})
            
            print(f"🔧 DEBUG: Tool worker '{occurrence_id}' checking activation: {activation}")
            
            # Check if we have activation data or tool results to work with
            slot = self._get_worker_slot(state, occurrence_id)
            # Check for tool results in both slot messages and global state messages
            slot_messages = slot.get("messages", [])
            state_messages = state.get("messages", [])
            
            # Look for ToolMessages in state that match this worker's tool calls
            has_tool_results = False
            recent_tool_messages = []
            for msg in reversed(state_messages):
                if hasattr(msg, 'tool_call_id') and msg.tool_call_id:
                    has_tool_results = True
                    recent_tool_messages.append(msg)
                    if len(recent_tool_messages) >= 3:  # Limit to recent tool results
                        break
            
            if not prompt and not args and not has_tool_results:
                print(f"🔧 DEBUG: Tool worker '{occurrence_id}' has no activation or tool results, creating final decision")
                # Create a final decision to terminate the worker
                slot["last_decision"] = {
                    "type": "final",
                    "tool_name": None,
                    "arguments": {},
                    "tool_call_id": None,
                    "answer": "No activation data provided"
                }
                return {**state, "work": {**state.get("work", {}), occurrence_id: slot}}
            
            # If no activation but we have tool results, generate final answer from results
            if not prompt and not args and has_tool_results:
                print(f"🔧 DEBUG: Tool worker '{occurrence_id}' has no activation but has tool results, generating final answer")
                print(f"🔧 DEBUG: Found {len(recent_tool_messages)} recent tool messages")
                
                # Build messages for final answer generation
                messages = []
                if self.system_directive:
                    messages.append(SystemMessage(content=self.system_directive))
                
                # Add the original user request from state messages
                for msg in state_messages:
                    if hasattr(msg, 'content') and msg.__class__.__name__ == 'HumanMessage':
                        messages.append(msg)
                        break
                
                # Add recent tool results
                for tool_msg in reversed(recent_tool_messages):
                    messages.append(SystemMessage(content=f"Tool result: {tool_msg.content}"))
                
                messages.append(SystemMessage(content="Based on the tool results above, provide a comprehensive final answer to the user's question."))
                
                print(f"🔧 DEBUG: Generating final answer with {len(messages)} messages")
                
                # Call LLM to generate final answer
                try:
                    response = await self.llm.ainvoke(messages)
                    final_answer = response.content if hasattr(response, 'content') else str(response)
                    
                    print(f"🔧 DEBUG: Generated final answer: {final_answer[:100]}...")
                    
                    slot["last_decision"] = {
                        "type": "final",
                        "tool_name": None,
                        "arguments": {},
                        "tool_call_id": None,
                        "answer": final_answer
                    }
                    
                    # Store the final decision in agent_data.decisions for resolve worker to access
                    agent_data = dict(state.get("agent_data", {}))
                    decisions = dict(agent_data.get("decisions", {}))
                    decisions[occurrence_id] = slot["last_decision"]
                    agent_data["decisions"] = decisions
                    
                    print(f"🔧 DEBUG: Stored final decision in agent_data.decisions[{occurrence_id}]")
                    
                    return {**state, "work": {**state.get("work", {}), occurrence_id: slot}, "agent_data": agent_data}
                except Exception as e:
                    print(f"🔧 DEBUG: Error generating final answer: {e}")
                    slot["last_decision"] = {
                        "type": "final",
                        "tool_name": None,
                        "arguments": {},
                        "tool_call_id": None,
                        "answer": "Error generating final answer from tool results"
                    }
                    
                    # Store the error decision in agent_data.decisions for resolve worker to access
                    agent_data = dict(state.get("agent_data", {}))
                    decisions = dict(agent_data.get("decisions", {}))
                    decisions[occurrence_id] = slot["last_decision"]
                    agent_data["decisions"] = decisions
                    
                    return {**state, "work": {**state.get("work", {}), occurrence_id: slot}, "agent_data": agent_data}
            
            # Get worker slot and check iteration limit
            slot = self._get_worker_slot(state, occurrence_id)
            slot["iters"] += 1
            
            if slot["iters"] > self.max_iters:
                errors = dict(state.get("errors", {}))
                errors[occurrence_id] = f"Max iterations exceeded in {occurrence_id}"
                slot["last_decision"] = {"type": "final", "answer": "I've reached the maximum number of iterations. Based on your request, I'll provide a response with the information I have."}
                return {**state, "errors": errors}
            
            # Build messages for decision
            messages = []
            if self.system_directive:
                messages.append(SystemMessage(content=self.system_directive))
            
            prompt = activation.get("prompt", "")
            args = activation.get("args", {})
            
            if prompt:
                messages.append(SystemMessage(content=f"Task instructions: {prompt}"))
            
            # Add the user's actual request as a human message
            print(f"🔧 DEBUG: Args received: {args}")
            if args and "request" in args:
                from langchain_core.messages import HumanMessage
                messages.append(HumanMessage(content=args["request"]))
                print(f"🔧 DEBUG: Added user request: {args['request']}")
            else:
                print("🔧 DEBUG: No request found in args")
            
            messages.append(SystemMessage(content=f"Available tools: {self.available_tool_ids}"))
            
            # Get LangChain tools for binding to LLM
            langchain_tools = []
            for tool_id in self.available_tool_ids:
                tool_obj = self.tool_manager.get_tool(tool_id)
                if tool_obj:
                    tool_function = tool_obj.get_tool_function()
                    langchain_tools.append(tool_function)
            
            # Add guidance for decision making
            if slot["iters"] == 1:
                messages.append(SystemMessage(content="""You have access to tools to help answer questions. Use the available tools when needed, or provide a direct answer if no tools are required.

If you need to use a tool, call the appropriate function with the required parameters.
If you have enough information to answer directly, provide your response without using tools."""))
            else:
                messages.append(SystemMessage(content=f"This is iteration {slot['iters']}. If tools are failing or you have enough information, provide a final answer instead of retrying tools."))
            
            # Add conversation history from state messages - find AI+Tool pairs
            state_messages = state.get("messages", [])
            print(f"🔧 DEBUG: State messages before extending: {len(state_messages)} messages")
            
            # Find AI+Tool pairs for proper OpenAI conversation structure
            ai_tool_pairs = []
            for i, msg in enumerate(state_messages):
                print(f"  State message {i}: {type(msg).__name__} - \"{str(msg.content)[:100]}{'...' if len(str(msg.content)) > 100 else ''}\"")
                
                # Check if this is an AIMessage with tool_calls
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"    Found AIMessage with tool_calls: {len(msg.tool_calls)}")
                    
                    # For multi-tool support, collect all corresponding ToolMessages
                    tool_messages = []
                    for tool_call in msg.tool_calls:
                        tool_call_id = tool_call['id']
                        corresponding_tool_msg = None
                        
                        # Search for matching ToolMessage after this AIMessage
                        for j in range(i + 1, len(state_messages)):
                            next_msg = state_messages[j]
                            if (hasattr(next_msg, 'tool_call_id') and 
                                hasattr(next_msg, 'name') and 
                                next_msg.tool_call_id == tool_call_id):
                                corresponding_tool_msg = next_msg
                                break
                        
                        if corresponding_tool_msg:
                            tool_messages.append(corresponding_tool_msg)
                            print(f"    Found ToolMessage for tool_call_id: {tool_call_id}")
                    
                    # Only add if we found all corresponding tool messages
                    if len(tool_messages) == len(msg.tool_calls):
                        ai_tool_pairs.append((msg, tool_messages))
                        print(f"    Found complete AI+Tool pair with {len(tool_messages)} tool messages")
            
            # Add only the most recent AI+Tool pair to avoid duplicates
            if ai_tool_pairs:
                ai_msg, tool_messages = ai_tool_pairs[-1]  # Take the most recent pair
                print(f"🔧 DEBUG: Adding most recent AI+Tool pair for proper OpenAI structure")
                
                # Add AIMessage with tool_calls first
                messages.append(ai_msg)
                print(f"    Added AIMessage with {len(ai_msg.tool_calls)} tool_calls")
                
                # Add all matching ToolMessages
                for tool_msg in tool_messages:
                    messages.append(tool_msg)
                    print(f"    Added ToolMessage for tool_call_id: {tool_msg.tool_call_id}")
            
            print(f"🔧 DEBUG: Messages being sent to LLM:")
            for i, msg in enumerate(messages):
                print(f"  Message {i}: {type(msg).__name__}")
                print(f"    Content: {msg.content}")
                print(f"    Content length: {len(str(msg.content))}")
                if hasattr(msg, 'tool_call_id'):
                    print(f"    Tool call ID: {msg.tool_call_id}")
                if hasattr(msg, 'name'):
                    print(f"    Name: {msg.name}")
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    print(f"    Tool calls: {len(msg.tool_calls)} calls")
                    for j, tool_call in enumerate(msg.tool_calls):
                        print(f"      Call {j}: {tool_call.get('name', 'unknown')} - {tool_call.get('args', {})}")
                if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs.get('tool_calls'):
                    print(f"    Additional tool calls: {len(msg.additional_kwargs['tool_calls'])}")
                print()
            
            # Note: writer functionality removed for simplicity
            
            try:
                # Log the exact payload being sent to OpenAI
                print(f"🔧 DEBUG: About to call LLM with {len(messages)} messages")
                print(f"🔧 DEBUG: Message types: {[type(m).__name__ for m in messages]}")
                
                # Use OpenAI function calling with tools bound to LLM
                if langchain_tools:
                    llm_with_tools = self.llm.bind_tools(langchain_tools)
                else:
                    llm_with_tools = self.llm
                
                response = llm_with_tools.invoke(messages)
                
                print(f"🔧 DEBUG: LLM response: {response}")
                
                # Process LLM response and determine action
                decision = self._process_llm_response(response, slot)
                
                # Store decision in both work slot and agent_data
                slot["last_decision"] = decision
                slot["iters"] = slot.get("iters", 0) + 1
                
                # Update work state
                new_state = dict(state)
                if "work" not in new_state:
                    new_state["work"] = {}
                else:
                    new_state["work"] = dict(new_state["work"])
                new_state["work"][occurrence_id] = slot
                
                # Store in agent_data for routing
                if "agent_data" not in new_state:
                    new_state["agent_data"] = {}
                if "decisions" not in new_state["agent_data"]:
                    new_state["agent_data"]["decisions"] = {}
                new_state["agent_data"]["decisions"][occurrence_id] = decision
                
                # Store AIMessage in state messages if it has tool_calls (for proper OpenAI conversation structure)
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    print(f"🔧 DEBUG: Storing AIMessage with tool_calls in state messages")
                    if "messages" not in new_state:
                        new_state["messages"] = []
                    new_state["messages"] = list(new_state["messages"]) + [response]
                
                print(f"🔧 DEBUG: Decision node updated state work: {new_state.get('work', {}).get(occurrence_id, {})}")
                print(f"🔧 DEBUG: Decision stored in agent_data: {new_state.get('agent_data', {}).get('decisions', {}).get(occurrence_id)}")
                
                return new_state
                
            except Exception as e:
                # Note: writer functionality removed for simplicity
                # Force final decision on error
                messages = slot.get("messages", [])
                messages.append(SystemMessage(content=f"[LLM ERROR] {e}"))
                slot["messages"] = messages[-6:]  # Keep last 6 messages
                slot["last_decision"] = {"type": "final", "answer": "I encountered an error while processing your request, but I'll do my best to help with the information available."}
                
                return state
        
        def tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Execute all tool calls from the LLM response."""
            print(f"🔧 DEBUG: === MULTI-TOOL NODE ENTRY ===")
            
            # Get the most recent AIMessage with tool_calls from state messages
            state_messages = state.get("messages", [])
            ai_message_with_tools = None
            
            # Find the most recent AIMessage with tool_calls
            for msg in reversed(state_messages):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    ai_message_with_tools = msg
                    break
            
            if not ai_message_with_tools:
                print(f"🔧 DEBUG: No AIMessage with tool_calls found in state messages")
                return state
            
            print(f"🔧 DEBUG: Found AIMessage with {len(ai_message_with_tools.tool_calls)} tool calls")
            
            # Execute all tool calls and collect ToolMessages
            tool_messages = []
            new_state = dict(state)
            
            for i, tool_call in enumerate(ai_message_with_tools.tool_calls):
                tool_call_id = tool_call['id']
                tool_name = tool_call['name']
                tool_args = tool_call.get('args', {})
                
                print(f"🔧 DEBUG: Processing tool call {i+1}/{len(ai_message_with_tools.tool_calls)}: {tool_name}")
                print(f"🔧 DEBUG: Tool call ID: {tool_call_id}")
                print(f"🔧 DEBUG: Tool args: {tool_args}")
                
                # Validate tool exists
                if tool_name not in self.available_tool_ids:
                    error_msg = f"Tool '{tool_name}' not available. Available tools: {self.available_tool_ids}"
                    tool_message = ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call_id,
                        name=tool_name
                    )
                    tool_messages.append(tool_message)
                    print(f"🔧 DEBUG: Tool {tool_name} not found, added error message")
                    continue
                
                # Get tool object and execute
                tool_obj = self.tool_manager.get_tool(tool_name)
                if not tool_obj:
                    error_msg = f"Tool '{tool_name}' object not found in manager"
                    tool_message = ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call_id,
                        name=tool_name
                    )
                    tool_messages.append(tool_message)
                    print(f"🔧 DEBUG: Tool object {tool_name} not found, added error message")
                    continue
                
                try:
                    # Get tool function and execute
                    tool_func = tool_obj.get_tool_function()
                    activation = self._get_activation(state, occurrence_id)
                    
                    # Coerce tool arguments
                    args = self._coerce_tool_args(tool_func, tool_args, activation.get("args", {}))
                    
                    print(f"🔧 DEBUG: Executing tool {tool_name} with coerced args: {args}")
                    result = tool_func(args)
                    print(f"🔧 DEBUG: Tool {tool_name} executed successfully")
                    print(f"🔧 DEBUG: Raw tool result type: {type(result)}")
                    print(f"🔧 DEBUG: Raw tool result: {result}")
                    
                    # Convert result to JSON string for tool message content
                    import json
                    try:
                        if hasattr(result, 'model_dump'):
                            result_json = json.dumps(result.model_dump(), indent=2)
                        elif hasattr(result, 'dict'):
                            result_json = json.dumps(result.dict(), indent=2)
                        else:
                            result_json = json.dumps(str(result), indent=2)
                        result_text = result_json
                    except Exception as json_error:
                        print(f"🔧 DEBUG: JSON serialization failed: {json_error}")
                        result_text = str(result)
                    
                    # Create ToolMessage
                    tool_message = ToolMessage(
                        content=result_text,
                        tool_call_id=tool_call_id,
                        name=tool_name
                    )
                    tool_messages.append(tool_message)
                    print(f"🔧 DEBUG: Created ToolMessage for {tool_name} with tool_call_id: {tool_call_id}")
                    print(f"🔧 DEBUG: ToolMessage content length: {len(result_text)}")
                    print(f"🔧 DEBUG: ToolMessage content preview: {result_text[:200]}...")
                    
                except Exception as e:
                    error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                    tool_message = ToolMessage(
                        content=error_msg,
                        tool_call_id=tool_call_id,
                        name=tool_name
                    )
                    tool_messages.append(tool_message)
                    print(f"🔧 DEBUG: Tool {tool_name} execution failed: {e}")
            
            # Add all ToolMessages to state messages
            if tool_messages:
                if "messages" not in new_state:
                    new_state["messages"] = []
                new_state["messages"] = list(new_state["messages"]) + tool_messages
                print(f"🔧 DEBUG: Added {len(tool_messages)} ToolMessages to state")
            
            print(f"🔧 DEBUG: === MULTI-TOOL NODE EXIT ===")
            return new_state
        
        def finalize_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """Generate final response and clean up."""
            print(f"🔧 DEBUG: Finalize node called for {occurrence_id}")
            
            # Get decision from agent_data (primary location)
            agent_decisions = state.get("agent_data", {}).get("decisions", {})
            decision = agent_decisions.get(occurrence_id, {})
            
            # Fallback to work slot if not found in agent_data
            if not decision:
                slot = self._get_worker_slot(state, occurrence_id)
                decision = slot.get("last_decision", {})
            
            answer = decision.get("answer", "No activation data provided")
            print(f"🔧 DEBUG: Finalize node - answer: {str(answer)[:100] if answer else 'None'}...")
            
            # Store final result in agent_data.decisions for resolve worker to access
            new_state = dict(state)
            agent_data = dict(new_state.get("agent_data", {}))
            decisions = dict(agent_data.get("decisions", {}))
            decisions[occurrence_id] = decision
            agent_data["decisions"] = decisions
            new_state["agent_data"] = agent_data
            
            # Create final result and add to messages for proper termination
            from langchain_core.messages import AIMessage
            final_message = AIMessage(content=answer or "No activation data provided")
            
            # Update state with final message
            if "messages" not in new_state:
                new_state["messages"] = []
            new_state["messages"] = list(new_state["messages"]) + [final_message]
            
            # Clear work state to signal completion
            if "work" in new_state:
                new_state["work"] = dict(new_state["work"])
                new_state["work"].pop(occurrence_id, None)
            
            print(f"🔧 DEBUG: Finalize node - returning final state with message, should terminate")
            print(f"🔧 DEBUG: Finalize node - final state keys: {list(new_state.keys())}")
            print(f"🔧 DEBUG: Finalize node - work cleared: {'work' not in new_state or occurrence_id not in new_state.get('work', {})}")
            return new_state
        
        # Add nodes to graph
        graph_builder.add_node(decision_node_id, decision_node)
        graph_builder.add_node(tool_node_id, tool_node)
        graph_builder.add_node(finalize_node_id, finalize_node)
        
        # Add conditional routing from decision node
        def route_decision(state: Dict[str, Any]) -> str:
            print(f"🔧 DEBUG: === ROUTE_DECISION CALLED ===")
            
            # Always check work slot first for most recent decision
            work = state.get("work", {})
            slot = work.get(occurrence_id, {})
            decision = slot.get("last_decision", {})
            
            # Fallback to agent_data if not in work slot
            if not decision:
                agent_decisions = state.get("agent_data", {}).get("decisions", {})
                decision = agent_decisions.get(occurrence_id, {})
            
            decision_type = decision.get("type")
            route = "TOOL" if decision_type == "tool" else "FINAL"
            print(f"🔧 DEBUG: Routing decision - type: {decision_type}, route: {route}")
            return route
        
        graph_builder.add_conditional_edges(
            decision_node_id,
            route_decision,
            {"TOOL": tool_node_id, "FINAL": finalize_node_id}
        )
        
        # Finalize node must terminate the graph
        graph_builder.add_edge(finalize_node_id, END)
        
        # Tool node loops back to decision
        graph_builder.add_edge(tool_node_id, decision_node_id)
        
        # Don't set entry point - this causes LangGraph to auto-connect to START
        # The entry point will be connected through conditional routing from worker_setup
        
        return decision_node_id, finalize_node_id
    
    def _push_tool_message(self, slot: Dict[str, Any], tool_name: str, result: Any):
        """Add tool result to conversation history."""
        messages = slot.get("messages", [])
        text = json.dumps(result, ensure_ascii=False)[:2000]
        messages.append(SystemMessage(content=f"[TOOL {tool_name}] {text}"))
        slot["messages"] = messages[-6:]  # Keep last 6 messages
    
    def _coerce_tool_args(self, tool: BaseTool, planned: dict, act_args: dict) -> dict:
        """Fill in required args from activation or defaults."""
        args = dict(planned or {})
        schema = getattr(tool, "args_schema", None)
        
        if schema and hasattr(schema, "model_fields"):
            for name, field in schema.model_fields.items():
                if name in args:
                    continue
                
                # Heuristics for common parameter names
                if name == "query":
                    candidate = (
                        act_args.get("query")
                        or act_args.get("company")
                        or act_args.get("topic")
                        or act_args.get("search_term")
                    )
                    if candidate:
                        args["query"] = str(candidate)
                        continue
                
                # Use field default if present
                if field.default is not None:
                    args[name] = field.default
        
        return args
    
    def _process_llm_response(self, response, slot: Dict[str, Any]) -> Dict[str, Any]:
        """Process LLM response and extract decision information."""
        print(f"🔧 DEBUG: Processing LLM response in _process_llm_response")
        
        # Check if response has tool calls (OpenAI function calling)
        if hasattr(response, 'tool_calls') and response.tool_calls:
            tool_call = response.tool_calls[0]  # Take first tool call
            tool_name = tool_call['name']
            arguments = tool_call['args']
            tool_call_id = tool_call['id']
            
            print(f"🔧 DEBUG: Found tool call - name: {tool_name}, args: {arguments}, id: {tool_call_id}")
            
            decision = {
                "type": "tool",
                "tool_name": tool_name,
                "arguments": arguments,
                "tool_call_id": tool_call_id,
                "answer": None
            }
            
            print(f"🔧 DEBUG: Created tool decision: {decision}")
            return decision
        
        # No tool calls - this is a final answer
        content = response.content if hasattr(response, 'content') else str(response)
        print(f"🔧 DEBUG: No tool calls found, creating final decision with content: {content[:100]}...")
        
        decision = {
            "type": "final",
            "tool_name": None,
            "arguments": {},
            "tool_call_id": None,
            "answer": content
        }
        
        print(f"🔧 DEBUG: Created final decision: {decision}")
        return decision
