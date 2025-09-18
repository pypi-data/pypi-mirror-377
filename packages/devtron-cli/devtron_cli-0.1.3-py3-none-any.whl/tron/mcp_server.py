import os
import yaml
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent
from tron.devtron_api import DevtronApplication


# Create the server instance
server = Server("tron-mcp")

@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        {
            "name": "create_application",
            "description": "Create a new Devtron application from YAML configuration",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path to the YAML configuration file"
                    },
                    "devtron_url": {
                        "type": "string",
                        "description": "Devtron URL (optional, can use DEVTRON_URL env var)"
                    },
                    "api_token": {
                        "type": "string", 
                        "description": "API token (optional, can use DEVTRON_API_TOKEN env var)"
                    }
                },
                "required": ["config_path"]
            }
        },
        {
            "name": "get_application",
            "description": "Get application configuration from Devtron",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "devtron_url": {
                        "type": "string",
                        "description": "Devtron URL"
                    },
                    "api_token": {
                        "type": "string",
                        "description": "API token"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Application name"
                    }
                },
                "required": ["devtron_url", "api_token", "app_name"]
            }
        },
        {
            "name": "update_application",
            "description": "Update an existing Devtron application",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "description": "Path to the YAML configuration file"
                    },
                    "devtron_url": {
                        "type": "string",
                        "description": "Devtron URL (optional, can use DEVTRON_URL env var)"
                    },
                    "api_token": {
                        "type": "string",
                        "description": "API token (optional, can use DEVTRON_API_TOKEN env var)"
                    }
                },
                "required": ["config_path"]
            }
        },
        {
            "name": "delete_application",
            "description": "Delete a Devtron application",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "devtron_url": {
                        "type": "string",
                        "description": "Devtron URL"
                    },
                    "api_token": {
                        "type": "string",
                        "description": "API token"
                    },
                    "app_name": {
                        "type": "string",
                        "description": "Application name"
                    },
                    "approve": {
                        "type": "boolean",
                        "description": "Confirm deletion"
                    }
                },
                "required": ["devtron_url", "api_token", "app_name"]
            }
        }
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "create_application":
        return await create_application_tool(arguments)
    elif name == "get_application":
        return await get_application_tool(arguments)
    elif name == "update_application":
        return await update_application_tool(arguments)
    elif name == "delete_application":
        return await delete_application_tool(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def create_application_tool(arguments: dict) -> TextContent:
    """Create a new application in Devtron using YAML configuration."""
    try:
        config_path = arguments["config_path"]
        devtron_url = arguments.get("devtron_url") or os.environ.get('DEVTRON_URL')
        api_token = arguments.get("api_token") or os.environ.get('DEVTRON_API_TOKEN')
        
        if not devtron_url:
            return TextContent(
                type="text",
                text="Error: Devtron URL is required. Please provide it via devtron_url parameter or DEVTRON_URL environment variable."
            )
        
        if not api_token:
            return TextContent(
                type="text",
                text="Error: API token is required. Please provide it via api_token parameter or DEVTRON_API_TOKEN environment variable."
            )
        
        if not os.path.exists(config_path):
            return TextContent(
                type="text",
                text=f"Error: Config file '{config_path}' not found."
            )
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            return TextContent(
                type="text",
                text=f"Error loading config file: {e}"
            )
        
        devtron_api = DevtronApplication(
            base_url=devtron_url,
            api_token=api_token
        )
        
        result = devtron_api.create_application(config_data)
        
        if result['success']:
            return TextContent(
                type="text",
                text=f"Application created successfully!\nApplication ID: {result['app_id']}"
            )
        else:
            return TextContent(
                type="text",
                text=f"Error creating application: {result['error']}"
            )
            
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Exception occurred: {str(e)}"
        )

async def get_application_tool(arguments: dict) -> TextContent:
    """Get application configuration from Devtron."""
    try:
        devtron_url = arguments["devtron_url"]
        api_token = arguments["api_token"]
        app_name = arguments["app_name"]
        
        devtron_api = DevtronApplication(base_url=devtron_url, api_token=api_token)
        result = devtron_api.get_application(app_name)
        
        if result['success']:
            return TextContent(
                type="text",
                text=json.dumps(result['config_data'], indent=2)
            )
        else:
            return TextContent(
                type="text",
                text=f"Error getting application: {result['error']}"
            )
            
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Exception occurred: {str(e)}"
        )

async def update_application_tool(arguments: dict) -> TextContent:
    """Update an existing Devtron application."""
    try:
        config_path = arguments["config_path"]
        devtron_url = arguments.get("devtron_url") or os.environ.get('DEVTRON_URL')
        api_token = arguments.get("api_token") or os.environ.get('DEVTRON_API_TOKEN')
        
        if not devtron_url:
            return TextContent(
                type="text",
                text="Error: Devtron URL is required. Please provide it via devtron_url parameter or DEVTRON_URL environment variable."
            )
        
        if not api_token:
            return TextContent(
                type="text",
                text="Error: API token is required. Please provide it via api_token parameter or DEVTRON_API_TOKEN environment variable."
            )
        
        if not os.path.exists(config_path):
            return TextContent(
                type="text",
                text=f"Error: Config file '{config_path}' not found."
            )
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            return TextContent(
                type="text",
                text=f"Error loading config file: {e}"
            )
        
        devtron_api = DevtronApplication(
            base_url=devtron_url,
            api_token=api_token
        )
        
        result = devtron_api.update_application(config_data)
        
        if result['success']:
            return TextContent(
                type="text",
                text="Application updated successfully!"
            )
        else:
            return TextContent(
                type="text",
                text=f"Error updating application: {result['error']}"
            )
            
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Exception occurred: {str(e)}"
        )

async def delete_application_tool(arguments: dict) -> TextContent:
    """Delete a Devtron application."""
    try:
        devtron_url = arguments["devtron_url"]
        api_token = arguments["api_token"]
        app_name = arguments["app_name"]
        approve = arguments.get("approve", False)
        
        devtron_api = DevtronApplication(base_url=devtron_url, api_token=api_token)
        result = devtron_api.delete_application(app_name, approve)
        
        if result['success']:
            return TextContent(
                type="text",
                text=result['message']
            )
        else:
            return TextContent(
                type="text",
                text=f"Error deleting application: {result['error']}"
            )
            
    except Exception as e:
        return TextContent(
            type="text",
            text=f"Exception occurred: {str(e)}"
        )

async def main():
    """Main function to run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, {})


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
