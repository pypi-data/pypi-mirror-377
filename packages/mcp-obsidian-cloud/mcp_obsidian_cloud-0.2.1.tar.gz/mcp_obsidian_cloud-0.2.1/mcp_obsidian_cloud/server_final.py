#!/usr/bin/env python3
import asyncio
import json
import logging
import requests
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult
from pydantic import BaseModel
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObsidianCloudServer:
    def __init__(self):
        self.base_url = os.getenv("OBSIDIAN_CLOUD_URL", "https://obsidian-mcp.ggailabs.com").rstrip("/")
        self.api_token = os.getenv("API_TOKEN", "")
        self.headers = {"Authorization": f"Bearer {self.api_token}"}
        
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request to Obsidian Cloud API"""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()

    async def list_files_in_vault(self):
        """Lists all files and directories in the root directory of your Obsidian vault"""
        return self._make_request("GET", "/vault/")

    async def list_files_in_dir(self, dirpath: str):
        """Lists all files and directories in a specific Obsidian directory"""
        # Sua API atual não tem este endpoint, então usa list_files_in_vault
        return self._make_request("GET", "/vault/")

    async def get_file_contents(self, filepath: str):
        """Return the content of a single file in your vault"""
        result = self._make_request("GET", f"/vault/{filepath}")
        return result.get("content", "")

    async def search(self, query: str):
        """Search for documents matching a specified text query across all files in the vault"""
        params = {"query": query}
        return self._make_request("GET", "/search", params=params)

    async def append_content(self, filepath: str, content: str):
        """Append content to a new or existing file in the vault"""
        try:
            # Tenta pegar conteúdo existente
            existing = await self.get_file_contents(filepath)
            new_content = existing + "\n" + content if existing else content
        except:
            new_content = content
            
        data = {"content": new_content}
        return self._make_request("PUT", f"/vault/{filepath}", json=data)

    async def patch_content(self, filepath: str, content: str, operation: str = "append", target_type: str = "", target: str = ""):
        """Insert content into an existing note relative to a heading, block reference, or frontmatter field"""
        # Implementação simples - apenas append por enquanto
        return await self.append_content(filepath, content)

    async def delete_file(self, filepath: str, confirm: bool = False):
        """Delete a file or directory from your vault"""
        if not confirm:
            raise ValueError("Must confirm deletion")
        return self._make_request("DELETE", f"/vault/{filepath}")

# Initialize the MCP server
server = Server("obsidian-cloud-stack")
obsidian = ObsidianCloudServer()

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="obsidian_list_files_in_vault",
            description="Lists all files and directories in the root directory of your Obsidian vault",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="obsidian_list_files_in_dir", 
            description="Lists all files and directories that exist in a specific Obsidian directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "dirpath": {"type": "string", "description": "Path to list files from (relative to your vault root). Note that empty directories will not be returned."}
                },
                "required": ["dirpath"]
            }
        ),
        Tool(
            name="obsidian_get_file_contents",
            description="Return the content of a single file in your vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the relevant file (relative to your vault root)"}
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="obsidian_simple_search",
            description="Simple search for documents matching a specified text query across all files in the vault. Use this tool when you want to do a simple text search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Text to a simple search for in the vault"},
                    "context_length": {"type": "integer", "description": "How much context to return around the matching string (default: 100)"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="obsidian_patch_content",
            description="Insert content into an existing note relative to a heading, block reference, or frontmatter field",
            inputSchema={
                "type": "object", 
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file (relative to vault root)"},
                    "operation": {"type": "string", "description": "Operation to perform (append, prepend, or replace)"},
                    "target_type": {"type": "string", "description": "Type of target to patch"},
                    "target": {"type": "string", "description": "Target identifier (heading path, block reference, or frontmatter field)"},
                    "content": {"type": "string", "description": "Content to insert"}
                },
                "required": ["filepath", "operation", "target_type", "target", "content"]
            }
        ),
        Tool(
            name="obsidian_append_content",
            description="Append content to a new or existing file in the vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file (relative to vault root)"},
                    "content": {"type": "string", "description": "Content to append to the file"}
                },
                "required": ["filepath", "content"]
            }
        ),
        Tool(
            name="obsidian_delete_file",
            description="Delete a file or directory from the vault",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file or directory to delete (relative to vault root)"},
                    "confirm": {"type": "boolean", "description": "Confirmation to delete the file (must be true)"}
                },
                "required": ["filepath", "confirm"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        if name == "obsidian_list_files_in_vault":
            result = await obsidian.list_files_in_vault()
        elif name == "obsidian_list_files_in_dir":
            result = await obsidian.list_files_in_dir(arguments["dirpath"])
        elif name == "obsidian_get_file_contents":
            result = await obsidian.get_file_contents(arguments["filepath"])
        elif name == "obsidian_simple_search":
            result = await obsidian.search(arguments["query"])
        elif name == "obsidian_append_content":
            result = await obsidian.append_content(arguments["filepath"], arguments["content"])
        elif name == "obsidian_patch_content":
            result = await obsidian.patch_content(
                arguments["filepath"], 
                arguments["content"],
                arguments.get("operation", "append"),
                arguments.get("target_type", ""),
                arguments.get("target", "")
            )
        elif name == "obsidian_delete_file":
            result = await obsidian.delete_file(arguments["filepath"], arguments.get("confirm", False))
        else:
            raise ValueError(f"Unknown tool: {name}")
            
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
        )
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def main():
    # Run the server using stdio transport
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

