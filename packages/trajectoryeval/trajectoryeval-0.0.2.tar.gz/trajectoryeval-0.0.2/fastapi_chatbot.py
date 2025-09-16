from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import os
from dotenv import load_dotenv
from openai import OpenAI
from uuid import uuid4
import json
from datetime import datetime

# Import judgeval tracing
# Import judgeval tracing
from trajectory import Tracer, wrap

load_dotenv()
# Get API credentials
openai_api_key = os.getenv("OPENAI_API_KEY")
trajectory_api_key = os.getenv("TRAJECTORY_API_KEY") or os.getenv("JUDGMENT_API_KEY")
trajectory_org_id = os.getenv("TRAJECTORY_ORGANIZATION_ID") or os.getenv("TRAJECTORY_ORG_ID") or os.getenv("JUDGMENT_ORGANIZATION_ID")

if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY not found in environment variables")
    exit(1)

if not trajectory_api_key or not trajectory_org_id:
    print("⚠️ Warning: TRAJECTORY_API_KEY or TRAJECTORY_ORGANIZATION_ID not found")
    print("Tracing will be disabled. Set these environment variables to enable tracing.")

# Initialize judgeval tracer with trace_across_async_contexts=True for FastAPI
judgment = Tracer(
    api_key=trajectory_api_key,
    organization_id=trajectory_org_id,
    project_name="fastapi_chatbot_project",
    enable_monitoring=True,
    enable_evaluations=False,
    trace_across_async_contexts=False  # CRITICAL: Enable for FastAPI
)

# Initialize OpenAI client and wrap it for tracing
client = OpenAI(api_key=openai_api_key)
traced_client = wrap(client, trace_across_async_contexts=False)  # CRITICAL: Enable for FastAPI

# FastAPI app
app = FastAPI(title="Simple LLM Chatbot with Tracing", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

# Store conversation history (in production, use a database)
conversations = {}

@judgment.observe(span_type="function")
def get_conversation_history(conversation_id: str) -> list:
    """Get conversation history for a given conversation ID"""
    return conversations.get(conversation_id, [])

@judgment.observe(span_type="function")
def add_to_conversation_history(conversation_id: str, role: str, content: str):
    """Add a message to conversation history"""
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    conversations[conversation_id].append({
        "role": role,
        "content": content
    })

# -------------------- Tools (traced) --------------------

@judgment.observe(span_type="tool")
def get_current_time() -> str:
    return datetime.utcnow().isoformat() + "Z"

@judgment.observe(span_type="tool")
def add_numbers(a: float, b: float) -> str:
    return str(a + b)

@judgment.observe(span_type="tool")
def search_docs(query: str) -> str:
    # minimal mock search
    return f"Top result for '{query}': https://example.com/{query.replace(' ', '-')}"


TOOLS_REGISTRY: Dict[str, Any] = {
    "get_current_time": get_current_time,
    "add_numbers": add_numbers,
    "search_docs": search_docs,
}

TOOLS_SPEC = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current UTC time",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "Search internal docs for a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords"}
                },
                "required": ["query"],
            },
        },
    },
]

@judgment.observe(span_type="function")
def _dispatch_tool(name: str, args_json: str) -> str:
    try:
        args = json.loads(args_json) if isinstance(args_json, str) else (args_json or {})
    except Exception:
        args = {}
    fn = TOOLS_REGISTRY.get(name)
    if not fn:
        return f"ERROR: unknown tool '{name}'"
    try:
        return fn(**args) if isinstance(args, dict) else fn()
    except TypeError:
        # wrong signature vs args
        return f"ERROR: bad arguments for tool '{name}': {args}"
    except Exception as e:
        return f"ERROR: tool '{name}' failed: {e}"


# -------------------- LLM with tools --------------------

def run_llm_with_tools(messages: list, max_tokens: int = 500, temperature: float = 0.7):
    resp = traced_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=TOOLS_SPEC,
        tool_choice="auto",
        max_tokens=max_tokens,
        temperature=temperature,
    )

    while True:
        choice = resp.choices[0]
        msg = choice.message
        tool_calls = getattr(msg, "tool_calls", None)

        if not tool_calls:
            return resp

        # 1) Append the assistant message WITH tool_calls
        assistant_msg = {
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        }
        messages.append(assistant_msg)

        # 2) Execute tools and append tool results (each must reference tool_call_id)
        for tc in tool_calls:
            name = tc.function.name
            args = tc.function.arguments
            result = _dispatch_tool(name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result if isinstance(result, str) else json.dumps(result),
            })

        # 3) Ask the model again with the assistant+tool messages included
        resp = traced_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=TOOLS_SPEC,
            tool_choice="auto",
            max_tokens=max_tokens,
            temperature=temperature,
        )

def call_openai(messages: list, max_tokens: int = 500, temperature: float = 0.7):
    """Call OpenAI API with tracing"""
    response = traced_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response

@judgment.observe(span_type="tool")
def prepare_messages(history: list, user_message: str) -> list:
    """Prepare messages for OpenAI API"""
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Keep your responses concise and friendly."}
    ]
    
    # Add conversation history
    messages.extend(history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    return messages

@judgment.observe(span_type="function")
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        conversation_id = request.conversation_id or str(uuid4())
        with judgment.conversation(conversation_id, user_id=str(uuid4())):
            with judgment.trace("chat_request") as trace:
                history = get_conversation_history(conversation_id)
                messages = prepare_messages(history, request.message)

                # USE TOOLS
                response = run_llm_with_tools(messages)

                assistant_response = response.choices[0].message.content
                add_to_conversation_history(conversation_id, "user", request.message)
                add_to_conversation_history(conversation_id, "assistant", assistant_response)
                trace.save(final_save=True)
                return ChatResponse(response=assistant_response, conversation_id=conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/new-conversation", response_model=ChatResponse)
async def new_conversation(request: ChatRequest):
    try:
        conversation_id = str(uuid4())
        with judgment.conversation(conversation_id, user_id=str(uuid4())):
            with judgment.trace("new_conversation") as trace:
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant. Keep your responses concise and friendly."},
                    {"role": "user", "content": request.message}
                ]

                # USE TOOLS
                response = run_llm_with_tools(messages)

                assistant_response = response.choices[0].message.content
                add_to_conversation_history(conversation_id, "user", request.message)
                add_to_conversation_history(conversation_id, "assistant", assistant_response)

                # Log user metrics (no spans; stored on trace.metadata.user_metrics)
                judgment.log_metric(
                    "chat_user_message",
                    value=len(request.message or ""),
                    unit="chars",
                    tags=["chat"],
                    properties={"conversation_id": conversation_id},
                    persist=True,
                )
                judgment.log_metric(
                    "chat_assistant_message",
                    value=len(assistant_response or ""),
                    unit="chars",
                    tags=["chat"],
                    properties={"conversation_id": conversation_id},
                    persist=True,
                )

                trace.save(final_save=True)
                return ChatResponse(response=assistant_response, conversation_id=conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@judgment.observe(span_type="function")
def get_conversation_data(conversation_id: str):
    """Get conversation data with tracing"""
    history = get_conversation_history(conversation_id)
    return {
        "conversation_id": conversation_id,
        "messages": history,
        "message_count": len(history)
    }

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history with tracing"""
    with judgment.trace("get_conversation") as trace:
        trace.update_metadata({
            "conversation_id": conversation_id
        })
        
        data = get_conversation_data(conversation_id)
        trace.update_metadata({
            "message_count": data["message_count"]
        })
        
        return data

@judgment.observe(span_type="function")
def list_all_conversations():
    """List all conversations with tracing"""
    return {
        "conversations": [
            {
                "conversation_id": conv_id,
                "message_count": len(messages)
            }
            for conv_id, messages in conversations.items()
        ]
    }

@app.get("/conversations")
async def list_conversations():
    """List all conversations with tracing"""
    with judgment.trace("list_conversations") as trace:
        data = list_all_conversations()
        trace.update_metadata({
            "conversation_count": len(data["conversations"])
        })
        return data

@judgment.observe(span_type="function")
def delete_conversation_data(conversation_id: str):
    """Delete conversation data with tracing"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation with tracing"""
    with judgment.trace("delete_conversation") as trace:
        trace.update_metadata({
            "conversation_id": conversation_id
        })
        
        result = delete_conversation_data(conversation_id)
        return result

@app.get("/")
async def root():
    """Root endpoint with usage instructions"""
    return {
        "message": "Simple LLM Chatbot API with Tracing",
        "tracing_enabled": trajectory_api_key is not None and trajectory_org_id is not None,
        "endpoints": {
            "POST /chat": "Send a message (continues conversation)",
            "POST /new-conversation": "Start a new conversation",
            "GET /conversations/{id}": "Get conversation history",
            "GET /conversations": "List all conversations",
            "DELETE /conversations/{id}": "Delete a conversation"
        },
        "usage": {
            "chat": {
                "url": "/chat",
                "method": "POST",
                "body": {"message": "Hello!", "conversation_id": "optional"}
            },
            "new_conversation": {
                "url": "/new-conversation", 
                "method": "POST",
                "body": {"message": "Hello!"}
            }
        }
    }

if __name__ == "__main__":
    print(" Starting Simple LLM Chatbot with Tracing...")
    print("📝 Available endpoints:")
    print("   POST /chat - Send a message (continues conversation)")
    print("   POST /new-conversation - Start new conversation")
    print("   GET /conversations/{id} - Get conversation history")
    print("   GET /conversations - List all conversations")
    print("   DELETE /conversations/{id} - Delete a conversation")
    print(f"\n Tracing enabled: { trajectory_api_key is not None and trajectory_org_id is not None}")
    print("🌐 Server will be available at: http://localhost:8001")
    print("📖 API docs at: http://localhost:8001/docs")
    print("📊 Traces will be sent to your JudgEval dashboard")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
