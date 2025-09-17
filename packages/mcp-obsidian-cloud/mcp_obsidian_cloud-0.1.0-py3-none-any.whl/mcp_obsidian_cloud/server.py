#!/usr/bin/env python3
import os, sys, json, asyncio
from .tools_pt import build_tools
from .remote_client import ObsidianCloudClient

# --- Instância do cliente -----------------
BASE  = os.environ["OBSIDIAN_CLOUD_URL"]
TOKEN = os.environ["API_TOKEN"]
api   = ObsidianCloudClient(BASE, TOKEN)

# Tools em dicionário  {nome: spec}
tools = {t["name"]: t for t in build_tools(api)}

def _awaitable(fn, args):
    res = fn(args)
    return asyncio.run(res) if asyncio.iscoroutine(res) else res

# --- Ponto de entrada CLI -----------------
def main() -> None:
    # 1. Envia READY
    ready = {
        "type": "READY",
        "tools": [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": {"type": "object"}   # simplificado
            } for t in tools.values()
        ]
    }
    print(json.dumps(ready), flush=True)

    # 2. Loop MCP (CALL → result)
    for line in sys.stdin:
        msg = json.loads(line)
        if msg.get("type") != "CALL":
            continue
        name       = msg["name"]
        arguments  = msg.get("arguments", {})
        call_id    = msg["id"]

        result = _awaitable(tools[name]["handler"], arguments)
        print(json.dumps({"id": call_id, "result": result}), flush=True)

# --- Execução direta -----------------------
if __name__ == "__main__":
    main()

