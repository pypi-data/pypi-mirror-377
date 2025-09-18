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
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls by forwarding to Lightdash MCP server"""
    try:
        # Map the tool calls to Lightdash MCP format
        if name == "find_charts":
            result = await client.call_mcp_tool("find_charts", {
                "chartSearchQueries": [{"label": arguments["query"]}]
            })
        elif name == "find_dashboards":
            result = await client.call_mcp_tool("find_dashboards", {
                "dashboardSearchQueries": [{"label": arguments["query"]}]
            })
        elif name == "find_explores":
            result = await client.call_mcp_tool("find_explores", {
                "tableName": arguments.get("tableName"),
                "includeFields": arguments.get("includeFields", True),
                "page": 1,
                "pageSize": 10
            })
        elif name == "run_metric_query":
            result = await client.call_mcp_tool("run_metric_query", arguments)
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

def main():
    """Main entry point - synchronous function that runs the server"""
    import sys
    # Ensure we don't pollute stdout (which interferes with MCP protocol)
    print("Starting Lightdash MCP server...", file=sys.stderr)
    
    # This is the correct pattern for MCP servers
    asyncio.run(stdio_server(app))

if __name__ == "__main__":
    main()