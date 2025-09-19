import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .client import LightdashClient

app = Server("lightdash-mcp-server")
client = LightdashClient()

@app.list_tools()
async def list_tools():
    """List all available Lightdash tools"""
    return [
        Tool(
            name="find_charts",
            description="Search for charts in Lightdash",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for charts"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="find_dashboards", 
            description="Search for dashboards in Lightdash",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for dashboards"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="find_explores",
            description="Find data explores/tables in Lightdash",
            inputSchema={
                "type": "object", 
                "properties": {
                    "tableName": {"type": "string", "description": "Name of table to search for"},
                    "includeFields": {"type": "boolean", "description": "Include field information"}
                }
            }
        ),
        Tool(
            name="run_metric_query",
            description="Run a metric query in Lightdash",
            inputSchema={
                "type": "object",
                "properties": {
                    "exploreName": {"type": "string", "description": "Name of the explore/table"},
                    "metrics": {"type": "array", "items": {"type": "string"}, "description": "Metrics to query"},
                    "dimensions": {"type": "array", "items": {"type": "string"}, "description": "Dimensions to group by"}
                },
                "required": ["exploreName", "metrics"]
            }
        ),
        Tool(
            name="list_projects",
            description="List all accessible projects in Lightdash",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_current_project",
            description="Get the currently active project",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls by forwarding to Lightdash MCP server"""
    try:
        # Map the tool calls to Lightdash MCP format
        if name == "find_charts":
            result = await client.call_mcp_tool("find_charts", {
                "type": "find_charts",
                "chartSearchQueries": [{"label": arguments["query"]}],
                "page": 1
            })
        elif name == "find_dashboards":
            result = await client.call_mcp_tool("find_dashboards", {
                "type": "find_dashboards",
                "dashboardSearchQueries": [{"label": arguments["query"]}],
                "page": 1
            })
        elif name == "find_explores":
            result = await client.call_mcp_tool("find_explores", {
                "type": "find_explores",
                "tableName": arguments.get("tableName"),
                "includeFields": arguments.get("includeFields", True),
                "page": 1,
                "pageSize": 10
            })
        elif name == "run_metric_query":
            result = await client.call_mcp_tool("run_metric_query", {
                "type": "run_metric_query",
                **arguments
            })
        elif name == "list_projects":
            result = await client.call_mcp_tool("list_projects", {
                "type": "list_projects"
            })
        elif name == "get_current_project":
            result = await client.call_mcp_tool("get_current_project", {
                "type": "get_current_project"
            })
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        # Extract the text content from Lightdash response
        content = result.get("content", [])
        if content and len(content) > 0:
            return [TextContent(type="text", text=content[0].get("text", "No results"))]
        else:
            return [TextContent(type="text", text="No results returned")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Error calling {name}: {str(e)}")]

class InitializationOptions:
    """Initialization options class with all required attributes"""
    def __init__(self):
        self.server_name = "lightdash-mcp-server"
        self.server_version = "1.0.0"
        self.instructions = "MCP server bridge for Lightdash analytics platform"
        self.capabilities = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }

async def main_async():
    """Async main function that handles the MCP server"""
    import sys
    print("Starting Lightdash MCP server...", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        # Create initialization options with all required attributes
        init_options = InitializationOptions()
        await app.run(read_stream, write_stream, init_options)

def main():
    """Synchronous entry point that runs the async main function"""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()