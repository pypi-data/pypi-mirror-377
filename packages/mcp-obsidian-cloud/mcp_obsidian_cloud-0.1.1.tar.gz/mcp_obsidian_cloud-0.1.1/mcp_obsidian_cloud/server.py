#!/usr/bin/env python3
import os, sys, json, asyncio
from .tools_pt import build_tools
from .remote_client import ObsidianCloudClient

def _awaitable(fn, args):
    res = fn(args)
    return asyncio.run(res) if asyncio.iscoroutine(res) else res

def main() -> None:
    # Instância do cliente
    BASE  = os.environ["OBSIDIAN_CLOUD_URL"]
    TOKEN = os.environ["API_TOKEN"]
    api   = ObsidianCloudClient(BASE, TOKEN)
    tools = {t["name"]: t for t in build_tools(api)}

    # 1. Envia READY
    ready = {
        "type": "READY",
        "tools": [
            {
                "name": t["name"],
                "description": t["description"],
                "inputSchema": {"type": "object"}
            } for t in tools.values()
        ]
    }
    print(json.dumps(ready), flush=True)

    # 2. Loop MCP (CALL → result) com tratamento de erros
    try:
        for line in sys.stdin:
            line = line.strip()
            
            # Ignora linhas vazias
            if not line:
                continue
                
            try:
                msg = json.loads(line)
                if msg.get("type") != "CALL":
                    continue
                    
                name = msg["name"]
                arguments = msg.get("arguments", {})
                call_id = msg["id"]
                
                result = _awaitable(tools[name]["handler"], arguments)
                print(json.dumps({"id": call_id, "result": result}), flush=True)
                
            except json.JSONDecodeError:
                # Ignora JSON inválido silenciosamente
                continue
            except KeyError as e:
                # Tool não encontrada
                error_msg = {"id": msg.get("id"), "error": f"Tool not found: {e}"}
                print(json.dumps(error_msg), flush=True)
            except Exception as e:
                # Erro genérico
                error_msg = {"id": msg.get("id"), "error": str(e)}
                print(json.dumps(error_msg), flush=True)
                
    except KeyboardInterrupt:
        # Sai graciosamente com Ctrl+C
        sys.exit(0)

if __name__ == "__main__":
    main()

