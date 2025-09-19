import os
import httpx
import sys
from typing import Dict, Any, Optional

class LightdashClient:
    def __init__(self):
        self.api_url = os.environ.get('LIGHTDASH_API_URL', 'https://bratrax.com')
        self.api_key = os.environ.get('LIGHTDASH_API_KEY')
        self.project_id = os.environ.get('LIGHTDASH_PROJECT_ID')  # ← Added back
        self._project_set = False  # Track if we've set the project context

        # Print to stderr so it doesn't interfere with MCP protocol
        print(f"Lightdash API URL: {self.api_url}", file=sys.stderr)
        print(f"Lightdash API Key: {self.api_key[:20] if self.api_key else 'None'}...", file=sys.stderr)
        print(f"Lightdash Project ID: {self.project_id}", file=sys.stderr)
        
        if not self.api_key:
            raise ValueError("LIGHTDASH_API_KEY environment variable is required")
        
        if not self.project_id:
            raise ValueError("LIGHTDASH_PROJECT_ID environment variable is required")
    
    async def ensure_project_set(self):
        """Ensure the project context is set before making tool calls"""
        if not self._project_set and self.project_id:
            try:
                print(f"Setting project context to: {self.project_id}", file=sys.stderr)
                await self.call_mcp_tool("set_project", {
                    "type": "set_project",
                    "projectUuid": self.project_id
                })
                self._project_set = True
                print(f"Successfully set active project to: {self.project_id}", file=sys.stderr)
            except Exception as e:
                print(f"Failed to set project context: {e}", file=sys.stderr)
                raise e
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Lightdash MCP server"""
        
        # Auto-set project for data tools (not for project management tools)
        if tool_name in ["find_charts", "find_dashboards", "find_explores", "run_metric_query", "search_field_values"]:
            await self.ensure_project_set()
        
        url = f"{self.api_url}/api/v1/mcp"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        headers = {
            "Authorization": f"ApiKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "lightdash-mcp-client/1.0",
        }
        
        # Debug logging (only for non-project-setting calls to avoid recursion)
        if tool_name != "set_project":
            print(f"Making request to: {url}", file=sys.stderr)
            print(f"Headers: {headers}", file=sys.stderr)
            print(f"Payload: {payload}", file=sys.stderr)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if tool_name != "set_project":
                print(f"Response status: {response.status_code}", file=sys.stderr)
                print(f"Response headers: {response.headers}", file=sys.stderr)
            
            if response.status_code == 406:
                print(f"406 Response body: {response.text}", file=sys.stderr)
                raise Exception(f"Server returned 406 Not Acceptable. The MCP server may not support this request format.")
            
            if response.status_code == 401:
                print(f"Response body: {response.text}", file=sys.stderr)
                raise Exception(f"Authentication failed. Make sure LIGHTDASH_API_KEY is a valid Personal Access Token")
            
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Lightdash MCP Error: {result['error']}")
                
            return result.get("result", {})
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from Lightdash MCP server"""
        url = f"{self.api_url}/api/v1/mcp"
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        headers = {
            "Authorization": f"ApiKey {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "lightdash-mcp-client/1.0",
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return result.get("result", {})