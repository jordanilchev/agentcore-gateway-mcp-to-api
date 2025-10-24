import json
import datetime
from zoneinfo import ZoneInfo


def get_weather(location):
    # Mock weather implementation
   
    return  json.dumps({
                'location': location,
                'temperature': '18°C',
                'conditions': 'Partially Sunny'
            }
        )

def get_time(timezone):
    try:
        tz = ZoneInfo(timezone)
        now = datetime.datetime.now(tz)
        return (json.dumps({
            'timezone': tz.tzname(now),  # Fixed: call the method with 'now' to get the string
            'UTC_offset': tz.utcoffset(now).total_seconds() / 3600,
            'current_time': now.strftime('%Y-%m-%d %H:%M:%S')
        }))
    except Exception as e:
        return "Failed to get time for timezone " + timezone + ": " + str(e)


def lambda_handler(event, context):
    # Log the request parameters to console
    print(f"Event: {json.dumps(event)}")
    print(f"Context: {context}")

    # Try to get tool name from context (Bedrock Agent), fallback to event for console testing
    tool_name = None
    if context and getattr(context, "client_context", None):
        tool_name = context.client_context.custom.get(
            "bedrockAgentCoreToolName", "unknown"
        )
    else:
        tool_name = event.get("bedrockAgentCoreToolName", "unknown")

    # Extract the actual tool name by stripping any prefix before the last '___'
    if "___" in tool_name:
        tool_name = tool_name.split("___")[-1]

    # Get arguments: prefer nested "arguments" dict, fallback to top-level event keys
    args = event.get("arguments", event)
    print(f"Tool Name: {tool_name}, Arguments: {args}")

    # call the appropriate tool based on tool_name
    if tool_name == "get_weather":
        if "location" not in args:
            result = "Error: Missing 'location' argument"
        else:
            result = get_weather(args["location"])
    elif tool_name == "get_time":
        if "timezone" not in args:
            result = "Error: Missing 'timezone' argument"
        else:
            result = get_time(args["timezone"])
    else:
        result = "Unknown tool"

    print(f"Tool: {tool_name}, Result: {result}")
    return {
        "statusCode": 200,
        "body": json.dumps({"result": result})
    }

