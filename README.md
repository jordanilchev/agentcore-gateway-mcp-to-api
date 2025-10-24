# AgentCore Gateway QuickStart 🚀

Amazon Bedrock AgentCore Gateway makes it easy to convert APIs, Lambda functions, and services into MCP-compatible tools and expose them to AI agents. This repo is a minimal quickstart to create a Gateway, register a Lambda target, and run a test agent that invokes the tools.

See the upstream guide for more detail: https://aws.github.io/bedrock-agentcore-starter-toolkit/user-guide/gateway/quickstart.html

## Files in this repo

- [1-setup_gateway.py](1-setup_gateway.py) — script to create a Gateway and add a Lambda target. See function [`setup_gateway`](1-setup_gateway.py).
- [2-run_agent.py](2-run_agent.py) — interactive agent tester. See function [`run_agent`](2-run_agent.py).
- [lambda_function.py](lambda_function.py) — Lambda implementation exposing tools: [`lambda_handler`](lambda_function.py), [`get_weather`](lambda_function.py), [`get_time`](lambda_function.py).
- [mcp-definition.json](mcp-definition.json) — MCP tool definitions (names: `get_weather`, `get_time`).
- [gateway_config.json](gateway_config.json) — saved gateway configuration produced by the setup script.
- [discovery-endpoint.json](discovery-endpoint.json) — OAuth discovery endpoint used by the Gateway.

## Quick start

1. Install dependencies (example):

Create and activate a virtual environment (recommended):

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # on macOS / Linux
    ```
    Then install the required Python packages:

    ```sh
    pip install boto3
    pip install bedrock-agentcore-starter-toolkit
    pip install strands-agents
    ```

2. Create the Gateway and Lambda target:

    **Note**: If you're using a multi-profile AWS configuration, make sure to activate the appropriate profile before running the scripts and setting it up the environment ($AWS_PROFILE):

    ```bash
    export AWS_PROFILE=[a profile from ~/.aws/credentials]
    ```

    ```sh
    python 1-setup_gateway.py
    ```

- This runs [`setup_gateway`](1-setup_gateway.py).
- On success it writes [gateway_config.json](gateway_config.json).

3. Run the interactive agent:

    ```sh
    python 2-run_agent.py
    ```

   - This runs [`run_agent`](2-run_agent.py).
   - The agent uses the Bedrock model (change `model_id` inside the script as needed) and lists available tools from the Gateway.

4. Test tools
   - Ask the agent about weather or time (the Lambda tools are defined in [lambda_function.py](lambda_function.py) and declared in [mcp-definition.json](mcp-definition.json)).
   - Lambda tools:
     - [`get_weather`](lambda_function.py): accepts `location`
     - [`get_time`](lambda_function.py): accepts `timezone`

## Notes & customization

- Change region in [1-setup_gateway.py](1-setup_gateway.py) before running if you are not in `eu-west-1`.
- Update model in [2-run_agent.py](2-run_agent.py) by editing `model_id`.
- Replace or extend the Lambda implementation in [lambda_function.py](lambda_function.py) to connect real services.
- The setup uses Cognito and generates client details to a file [gateway_config.json](gateway_config.json).
- OAuth discovery details are generated and stored in [discovery-endpoint.json](discovery-endpoint.json).

## MCP definition for reference

    ```json
    [
    {
        "description": "Get weather for a location",
        "inputSchema": {
        "properties": {
            "location": {
            "type": "string"
            }
        },
        "required": [
            "location"
        ],
        "type": "object"
        },
        "name": "get_weather"
    },
    {
        "description": "Get time for a timezone",
        "inputSchema": {
        "properties": {
            "timezone": {
            "type": "string"
            }
        },
        "required": [
            "timezone"
        ],
        "type": "object"
        },
        "name": "get_time"
    }
    ]
    ```

## Troubleshooting

- If [gateway_config.json](gateway_config.json) is missing, run [`setup_gateway`](1-setup_gateway.py) again.
- If the agent cannot fetch tools, check access token retrieval in [`run_agent`](2-run_agent.py) and the values in [gateway_config.json](gateway_config.json).

## License & references

- This quickstart is a minimal example. For full operations and advanced configuration, see the AgentCore Starter Toolkit documentation:
  https://aws.github.io/bedrock-agentcore-starter-toolkit/
