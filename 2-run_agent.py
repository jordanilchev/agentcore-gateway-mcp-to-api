"""
Agent script to test the Gateway
Run this after setup: python run_agent.py
"""

from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json
import sys
import os
import glob

def create_streamable_http_transport(mcp_url: str, access_token: str):
    return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})

def get_full_tools_list(client):
    """Get all tools with pagination support"""
    more_tools = True
    tools = []
    pagination_token = None
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if tmp_tools.pagination_token is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    return tools

def choose_config_file(cli_arg=None):
    # Accept either a suffix or a filename from CLI, otherwise list available gateway_config_*.json files
    candidates = sorted(glob.glob("gateway_config_*.json"))
    # backward compatibility: also accept gateway_config.json
    if os.path.exists("gateway_config.json"):
        candidates.insert(0, "gateway_config.json")

    if cli_arg:
        # If arg matches an existing filename, use it
        if os.path.exists(cli_arg):
            return cli_arg
        # If arg looks like a 4-digit suffix or plain suffix, try gateway_config_{arg}.json
        candidate_by_suffix = f"gateway_config_{cli_arg}.json"
        if os.path.exists(candidate_by_suffix):
            return candidate_by_suffix
        print(f"❌ Specified config '{cli_arg}' not found.")
        return None

    if not candidates:
        return None

    if len(candidates) == 1:
        return candidates[0]

    # Multiple candidates - prompt user to pick
    print("Multiple gateway config files found. Choose one:")
    for i, fn in enumerate(candidates, start=1):
        print(f"  {i}) {fn}")
    while True:
        choice = input(f"Select [1-{len(candidates)}] (default 1): ").strip()
        if choice == "":
            return candidates[0]
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(candidates):
                return candidates[idx-1]
        # allow entering filename directly
        if os.path.exists(choice):
            return choice
        print("Invalid selection, try again.")

def run_agent():
    # Load configuration
    config_file = None
    # allow passing filename or suffix as CLI arg
    cli_arg = sys.argv[1] if len(sys.argv) > 1 else None
    config_file = choose_config_file(cli_arg)

    if not config_file:
        print("❌ Error: No gateway_config_*.json found!")
        print("Please run 'python 1-setup_gateway.py' to create the Gateway.")
        sys.exit(1)

    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config '{config_file}': {e}")
        sys.exit(1)

    gateway_url = config["gateway_url"]
    client_info = config["client_info"]

    # Get access token for the agent
    print(f"Using config: {config_file}")
    print("Getting access token...")
    client = GatewayClient(region_name=config["region"])
    access_token = client.get_access_token_for_cognito(client_info)
    print("✓ Access token obtained\n")

    # Model configuration - CHANGE THIS!!!
    model_id = "eu.amazon.nova-lite-v1:0"

    print("🤖 Starting AgentCore Gateway Test Agent")
    print(f"Gateway URL: {gateway_url}")
    print(f"Model: {model_id}")
    print("-" * 60)

    # Setup Bedrock model
    bedrockmodel = BedrockModel(
        model_id=model_id,
        streaming=True,
    )

    # Setup MCP client
    mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url, access_token))

    with mcp_client:
        # List available tools
        tools = get_full_tools_list(mcp_client)
        print(f"\n📋 Available tools: {[tool.tool_name for tool in tools]}")
        print("-" * 60)

        # Create agent
        agent = Agent(model=bedrockmodel, tools=tools)

        # Interactive loop
        print("\n💬 Interactive Agent Ready!")
        print("Try asking: 'What's the weather or time in a <city>?'")
        print("Type 'exit', 'quit', or 'bye' to end.\n")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("👋 Goodbye!")
                break

            print("\n🤔 Thinking...\n")
            response = agent(user_input)
  
            print("\n\n")

if __name__ == "__main__":
    run_agent()
