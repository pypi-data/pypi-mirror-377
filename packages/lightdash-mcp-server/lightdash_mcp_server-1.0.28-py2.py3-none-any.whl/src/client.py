import os
import httpx
import sys
import time
from typing import Dict, Any, Optional

class LightdashClient:
    def __init__(self):
        self.api_url = os.environ.get('LIGHTDASH_API_URL', 'https://bratrax.com')
        self.client_id = os.environ.get('LIGHTDASH_CLIENT_ID')
        self.client_secret = os.environ.get('LIGHTDASH_CLIENT_SECRET')
        self.project_id = os.environ.get('LIGHTDASH_PROJECT_ID')
        
        # Cache for OAuth token
        self._access_token = None
        self._token_expires_at = None

        # Print to stderr so it doesn't interfere with MCP protocol
        print(f"Lightdash API URL: {self.api_url}", file=sys.stderr)
        print(f"Lightdash Client ID: {self.client_id}", file=sys.stderr)
        print(f"Lightdash Project ID: {self.project_id}", file=sys.stderr)
        
        if not self.client_id or not self.client_secret:
            raise ValueError("LIGHTDASH_CLIENT_ID and LIGHTDASH_CLIENT_SECRET environment variables are required")
    
    async def get_oauth_token(self) -> str:
        """Get OAuth token using client credentials flow"""
        
        # Check if we have a valid cached token
        if self._access_token and self._token_expires_at and time.time() < self._token_expires_at:
            return self._access_token
            
        token_url = f"{self.api_url}/api/v1/oauth/token"
        
        # Use form-encoded data as per OAuth2 spec
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "mcp:read mcp:write"  # Request MCP scopes
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(token_url, data=data, headers=headers)
            
            print(f"Token request status: {response.status_code}", file=sys.stderr)
            
            if response.status_code != 200:
                print(f"Token request failed: {response.text}", file=sys.stderr)
                raise Exception(f"Failed to get OAuth token: {response.status_code} {response.text}")
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            
            # Calculate expiration time (subtract 60 seconds for safety)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = time.time() + expires_in - 60
            
            print(f"Got OAuth token, expires in {expires_in} seconds", file=sys.stderr)
            return self._access_token
    
    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Lightdash MCP server"""
        url = f"{self.api_url}/api/v1/mcp"
        
        # Get OAuth token
        access_token = await self.get_oauth_token()
        
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
            "Authorization": f"Bearer {access_token}",  # ← Bearer token from OAuth!
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            if response.status_code == 401:
                print(f"Auth failed, trying token refresh...", file=sys.stderr)
                # Try to refresh token and retry once
                self._access_token = None
                self._token_expires_at = None
                access_token = await self.get_oauth_token()
                headers["Authorization"] = f"Bearer {access_token}"
                
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 401:
                    raise Exception(f"Authentication failed even after token refresh")
            
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Lightdash MCP Error: {result['error']}")
                
            return result.get("result", {})
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from Lightdash MCP server"""
        url = f"{self.api_url}/api/v1/mcp"
        
        # Get OAuth token
        access_token = await self.get_oauth_token()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            return result.get("result", {})