"""
Setup script to create Gateway with Lambda target and save configuration
Run this first: python setup_gateway.py
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json
import logging
import time
import random
import os

def setup_gateway():
    # Configuration
    start_time = time.perf_counter()  # <-- start timing
    region = "eu-west-1"  # IF in EU - CHANGE THIS !!!
# Europe (Paris) eu-west-3
# Europe (Ireland) eu-west-1
# Europe (Frankfurt) eu-central-1
# Europe (Stockholm) eu-north-1

    # Generate a unique 4-digit suffix for this run to avoid overriding resources
    suffix = f"{random.randint(0, 9999):04d}"
    authorizer_name = f"TestGateway-{suffix}"
    gateway_name = f"AgentCoreGateway-{suffix}"
    target_name = f"AgentCoreLambdaTarget-{suffix}"
    config_filename = f"gateway_config_{suffix}.json"

    print("🚀 Setting up AgentCore Gateway...")
    print(f"Region: {region}")
    print(f"Run suffix: {suffix}\n")

    # Initialize client
    client = GatewayClient(region_name=region)
    client.logger.setLevel(logging.INFO)

    # Step 2.1: Create OAuth authorizer
    print("Step 2.1: Creating OAuth authorization server...")
    # pass a unique authorizer name so we don't override existing ones
    cognito_response = client.create_oauth_authorizer_with_cognito(authorizer_name)
    print(f"✓ Authorization server created: {authorizer_name}\n")

    # Step 2.2: Create Gateway
    print("Step 2.2: Creating Gateway...")
    gateway = client.create_mcp_gateway(
        # the name of the Gateway - provide a unique name to avoid overrides.
        name=gateway_name,
        # the role arn that the Gateway will use - if you don't set one, one will be created.
        # NOTE: if you are using your own role make sure it has a trust policy that trusts bedrock-agentcore.amazonaws.com
        role_arn=None,
        # the OAuth authorization server details. If you are providing your own authorization server,
        # then pass an input of the following form: {"customJWTAuthorizer": {"allowedClients": ["<INSERT CLIENT ID>"], "discoveryUrl": "<INSERT DISCOVERY URL">}}
        authorizer_config=cognito_response["authorizer_config"],
        # enable semantic search
        enable_semantic_search=True,
    )
    print(f"✓ Gateway created: {gateway['gatewayUrl']} (name: {gateway_name})\n")

    # If role_arn was not provided, fix IAM permissions
    # NOTE: This is handled internally by the toolkit when no role is provided
    client.fix_iam_permissions(gateway)
    print("⏳ Waiting 30s for IAM propagation...")
    time.sleep(30)
    print("✓ IAM permissions configured\n")

    # Step 2.3: Add Lambda target
    print("Step 2.3: Adding Lambda target...")
    lambda_target = client.create_mcp_gateway_target(
        # the gateway created in the previous step
        gateway=gateway,
        # the name of the Target - provide a unique name to avoid overrides.
        name=target_name,
        # the type of the Target
        target_type="lambda",
        # the target details - set this to define your own lambda if you pre-created one.
        # Otherwise leave this None and one will be created for you.
        target_payload=None,
        # you will see later in the tutorial how to use this to connect to APIs using API keys and OAuth credentials.
        credentials=None,
    )
    print(f"✓ Lambda target added: {target_name}\n")

    # Step 2.4: Save configuration for agent
    config = {
        "gateway_url": gateway["gatewayUrl"],
        "gateway_id": gateway["gatewayId"],
        "region": region,
        "client_info": cognito_response["client_info"],
        "names": {
            "authorizer": authorizer_name,
            "gateway": gateway_name,
            "target": target_name
        },
        "suffix": suffix
    }

    # Avoid overwriting an existing config file; write a suffix-specific file instead
    with open(config_filename, "w") as f:
        json.dump(config, f, indent=2)

    # Print timing before returning
    elapsed = time.perf_counter() - start_time
    print("=" * 30)
    print("✅ Gateway setup complete!")
    print(f"Gateway URL: {gateway['gatewayUrl']}")
    print(f"Gateway ID: {gateway['gatewayId']}")
    print(f"\nConfiguration saved to: {config_filename}")
    print("\nNext step: Run 'python run_agent.py' to test your Gateway")
    print("=" * 30)
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    print(f"\n⏱️ Total execution time: {minutes:02d}m:{seconds:02d}s")

    return config

if __name__ == "__main__":
    setup_gateway()