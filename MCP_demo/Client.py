import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client

# .env is one level above the MCP_demo folder
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError(f"OPENAI_API_KEY not found. Looked for .env at: {dotenv_path}")

openai_client = OpenAI(api_key=api_key)


def clean_schema(schema: dict) -> dict:
    """Recursively remove keys that OpenAI's API does not accept."""
    BLOCKED_KEYS = {"$schema", "default"}
    return {
        k: clean_schema(v) if isinstance(v, dict) else v
        for k, v in schema.items()
        if k not in BLOCKED_KEYS
    }


async def main():
    async with Client("server.py") as mcp_client:

        # --- Fetch tools from MCP server and convert to OpenAI format ---
        mcp_tools = await mcp_client.list_tools()

        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": clean_schema(t.inputSchema),
                },
            }
            for t in mcp_tools
        ]

        # --- Chat loop ---
        print("MCP + OpenAI demo. Type 'quit' to exit.\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit"):
                break

            messages = [{"role": "user", "content": user_input}]

            # --- Agentic loop: handle tool calls until OpenAI returns text ---
            while True:
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                )

                message = response.choices[0].message
                messages.append(message)

                if not message.tool_calls:
                    # No more tool calls — print final answer
                    print(f"OpenAI: {message.content}\n")
                    break

                # Execute each tool call via MCP and collect results
                for call in message.tool_calls:
                    args = json.loads(call.function.arguments)
                    print(f"  [calling tool: {call.function.name}({args})]")
                    mcp_result = await mcp_client.call_tool(call.function.name, args)
                    # FastMCP 3.x returns a CallToolResult object; extract text content
                    result_text = mcp_result.content[0].text
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result_text,
                    })


if __name__ == "__main__":
    asyncio.run(main())