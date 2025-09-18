import os
import httpx
import sys
from typing import Dict, Any, Optional

class LightdashClient:
    def __init__(self):
        self.api_url = os.environ.get('LIGHTDASH_API_URL', 'https://bratrax.com')
        self.api_key = os.environ.get('LIGHTDASH_API_KEY')  # ← Changed back to API key

        # Print to stderr so it doesn't interfere with MCP protocol
        print(f"Lightdash API URL: {self.api_url}", file=sys.stderr)
        print(f"Lightdash API Key: {self.api_key[:20] if self.api_key else 'None'}...", file=sys.stderr)
        
        if not self.api_key:
            raise ValueError("LIGHTDASH_API_KEY environment variable is required")
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Lightdash MCP server"""
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
            "Authorization": f"ApiKey {self.api_key}",  # ← Back to ApiKey format
            "Content-Type": "application/json"
        }
        
        # Debug logging
        print(f"Making request to: {url}", file=sys.stderr)
        print(f"Headers: {headers}", file=sys.stderr)
        print(f"Payload: {payload}", file=sys.stderr)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"Response status: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {response.headers}", file=sys.stderr)
            
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
            "Authorization": f"ApiKey {self.api_key}",  # ← ApiKey format
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return result.get("result", {})