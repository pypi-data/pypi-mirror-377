
import asyncio
import logging
from typing import TypedDict, Annotated, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for the KGraphPlanner agent"""
    messages: Annotated[list[BaseMessage], add_messages]
    request_category: Optional[str]
    processing_step: Optional[str]


class KGraphPlannerAgent:
    """Base agent class with async event emission for processing nodes and transitions"""
    
    def __init__(self, 
                 model: LanguageModelLike,
                 event_queue: Optional[asyncio.Queue] = None,
                 checkpointer=None):
        self.model = model
        self.event_queue = event_queue or asyncio.Queue()
        self.checkpointer = checkpointer
        self.workflow = None
        self.compiled_graph = None
        
    async def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit an event to the event queue"""
        event = {
            "type": event_type,
            "timestamp": asyncio.get_event_loop().time(),
            "data": data
        }
        await self.event_queue.put(event)
        logger.info(f"Event emitted: {event_type} - {data}")
    
    async def classify_request(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Classify the user's request into categories using LLM"""
        await self.emit_event("node_start", {"node": "classify_request"})
        
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        if not last_message or not isinstance(last_message, HumanMessage):
            category = "general"
        else:
            # Use LLM for classification
            await self.emit_event("llm_call_start", {"purpose": "classification"})
            
            classification_prompt = f"""Classify the following user request into one of these categories:
- greeting: Simple greetings or social interactions
- help_request: Requests for assistance or support
- question: Questions seeking information or explanations
- creation_request: Requests to create, build, or generate something
- planning_request: Requests for planning, organizing, or task management
- general: Any other type of request

User request: "{last_message.content}"

Respond with only the category name."""

            classification_messages = [HumanMessage(content=classification_prompt)]
            response = await self.model.ainvoke(classification_messages)
            category = response.content.strip().lower()
            
            # Validate category
            valid_categories = ["greeting", "help_request", "question", "creation_request", "planning_request", "general"]
            if category not in valid_categories:
                category = "general"
            
            await self.emit_event("llm_call_end", {"category": category})
        
        await self.emit_event("classification_complete", {
            "category": category,
            "message": last_message.content if last_message else "No message"
        })
        
        state["request_category"] = category
        state["processing_step"] = "classified"
        
        await self.emit_event("node_end", {"node": "classify_request", "category": category})
        return state
    
    def route_to_handler(self, state: AgentState) -> str:
        """Route to the appropriate handler based on classification"""
        category = state.get("request_category", "general")
        return f"handle_{category}"
    
    async def handle_greeting(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Handle greeting requests"""
        await self.emit_event("node_start", {"node": "handle_greeting"})
        
        response_content = "Hello! I'm KGraphPlanner, ready to help you with planning and task management. How can I assist you today?"
        
        ai_message = AIMessage(content=response_content)
        state["messages"] = state["messages"] + [ai_message]
        state["processing_step"] = "completed"
        
        await self.emit_event("response_generated", {
            "category": "greeting",
            "response_length": len(response_content)
        })
        
        await self.emit_event("node_end", {"node": "handle_greeting"})
        return state
    
    async def handle_help_request(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Handle help requests"""
        await self.emit_event("node_start", {"node": "handle_help_request"})
        
        response_content = "I'm here to help! I can assist with planning, organizing tasks, answering questions, and more. What specifically would you like help with?"
        
        ai_message = AIMessage(content=response_content)
        state["messages"] = state["messages"] + [ai_message]
        state["processing_step"] = "completed"
        
        await self.emit_event("response_generated", {
            "category": "help_request",
            "response_length": len(response_content)
        })
        
        await self.emit_event("node_end", {"node": "handle_help_request"})
        return state
    
    async def handle_question(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Handle question requests"""
        await self.emit_event("node_start", {"node": "handle_question"})
        
        messages = state["messages"]
        
        await self.emit_event("llm_call_start", {"category": "question"})
        response = await self.model.ainvoke(messages)
        response_content = response.content
        await self.emit_event("llm_call_end", {"response_length": len(response_content)})
        
        ai_message = AIMessage(content=response_content)
        state["messages"] = state["messages"] + [ai_message]
        state["processing_step"] = "completed"
        
        await self.emit_event("response_generated", {
            "category": "question",
            "response_length": len(response_content)
        })
        
        await self.emit_event("node_end", {"node": "handle_question"})
        return state
    
    async def handle_creation_request(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Handle creation requests"""
        await self.emit_event("node_start", {"node": "handle_creation_request"})
        
        messages = state["messages"]
        
        await self.emit_event("llm_call_start", {"category": "creation_request"})
        response = await self.model.ainvoke(messages)
        response_content = response.content
        await self.emit_event("llm_call_end", {"response_length": len(response_content)})
        
        ai_message = AIMessage(content=response_content)
        state["messages"] = state["messages"] + [ai_message]
        state["processing_step"] = "completed"
        
        await self.emit_event("response_generated", {
            "category": "creation_request",
            "response_length": len(response_content)
        })
        
        await self.emit_event("node_end", {"node": "handle_creation_request"})
        return state
    
    async def handle_planning_request(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Handle planning requests"""
        await self.emit_event("node_start", {"node": "handle_planning_request"})
        
        messages = state["messages"]
        
        await self.emit_event("llm_call_start", {"category": "planning_request"})
        response = await self.model.ainvoke(messages)
        response_content = response.content
        await self.emit_event("llm_call_end", {"response_length": len(response_content)})
        
        ai_message = AIMessage(content=response_content)
        state["messages"] = state["messages"] + [ai_message]
        state["processing_step"] = "completed"
        
        await self.emit_event("response_generated", {
            "category": "planning_request",
            "response_length": len(response_content)
        })
        
        await self.emit_event("node_end", {"node": "handle_planning_request"})
        return state
    
    async def handle_general(self, state: AgentState, config: RunnableConfig) -> AgentState:
        """Handle general requests"""
        await self.emit_event("node_start", {"node": "handle_general"})
        
        messages = state["messages"]
        
        await self.emit_event("llm_call_start", {"category": "general"})
        response = await self.model.ainvoke(messages)
        response_content = response.content
        await self.emit_event("llm_call_end", {"response_length": len(response_content)})
        
        ai_message = AIMessage(content=response_content)
        state["messages"] = state["messages"] + [ai_message]
        state["processing_step"] = "completed"
        
        await self.emit_event("response_generated", {
            "category": "general",
            "response_length": len(response_content)
        })
        
        await self.emit_event("node_end", {"node": "handle_general"})
        return state
    
    def build_workflow(self):
        """Build the agent workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add classification node
        workflow.add_node("classify_request", self.classify_request)
        
        # Add handler nodes for each category
        workflow.add_node("handle_greeting", self.handle_greeting)
        workflow.add_node("handle_help_request", self.handle_help_request)
        workflow.add_node("handle_question", self.handle_question)
        workflow.add_node("handle_creation_request", self.handle_creation_request)
        workflow.add_node("handle_planning_request", self.handle_planning_request)
        workflow.add_node("handle_general", self.handle_general)
        
        # Define flow
        workflow.add_edge(START, "classify_request")
        
        # Add conditional routing from classification to appropriate handler
        workflow.add_conditional_edges(
            "classify_request",
            self.route_to_handler,
            {
                "handle_greeting": "handle_greeting",
                "handle_help_request": "handle_help_request", 
                "handle_question": "handle_question",
                "handle_creation_request": "handle_creation_request",
                "handle_planning_request": "handle_planning_request",
                "handle_general": "handle_general"
            }
        )
        
        # All handlers lead to END
        workflow.add_edge("handle_greeting", END)
        workflow.add_edge("handle_help_request", END)
        workflow.add_edge("handle_question", END)
        workflow.add_edge("handle_creation_request", END)
        workflow.add_edge("handle_planning_request", END)
        workflow.add_edge("handle_general", END)
        
        self.workflow = workflow
        return workflow
    
    def compile(self):
        """Compile the workflow into an executable graph"""
        if not self.workflow:
            self.build_workflow()
            
        self.compiled_graph = self.workflow.compile(checkpointer=self.checkpointer)
        return self.compiled_graph
    
    async def arun(self, messages: list[BaseMessage], config: Optional[RunnableConfig] = None):
        """Run the agent asynchronously"""
        if not self.compiled_graph:
            self.compile()
            
        await self.emit_event("agent_start", {"message_count": len(messages)})
        
        initial_state = AgentState(
            messages=messages,
            request_category=None,
            processing_step="starting"
        )
        
        try:
            result = await self.compiled_graph.ainvoke(initial_state, config=config)
            await self.emit_event("agent_complete", {"final_step": result.get("processing_step")})
            return result
        except Exception as e:
            await self.emit_event("agent_error", {"error": str(e)})
            raise

