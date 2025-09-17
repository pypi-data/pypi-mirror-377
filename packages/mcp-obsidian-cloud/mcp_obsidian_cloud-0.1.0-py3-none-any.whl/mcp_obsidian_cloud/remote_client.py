"""
remote_client.py - Cliente REST para a Obsidian Cloud Stack
"""

import os, sys, requests
from typing import Dict, List, Optional

class ObsidianCloudClient:
    def __init__(self, base_url: str, api_token: str, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.headers  = {"Authorization": f"Bearer {api_token}"}
        self.timeout  = timeout

    # -------- REST ----------
    def _url(self, route: str) -> str:
        return f"{self.base_url}{route}"

    def list_root(self) -> List[Dict]:
        r = requests.get(self._url("/vault/"), headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def get_file(self, path: str) -> Optional[str]:
        r = requests.get(self._url(f"/vault/{path}"), headers=self.headers, timeout=self.timeout)
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get("content")

    def write_file(self, path: str, markdown: str) -> Dict:
        r = requests.put(self._url(f"/vault/{path}"),
                         json={"content": markdown},
                         headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def delete_file(self, path: str) -> Dict:
        r = requests.delete(self._url(f"/vault/{path}"), headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def search(self, query: str) -> List[Dict]:
        r = requests.get(self._url("/search"),
                         params={"query": query},
                         headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json().get("results", [])

    # ---------- Conveniências ----------
    def create_insight(self, filename: str, markdown: str) -> Dict:
        return self.write_file(f"5 - INSIGHTS-IA/{filename}", markdown)

    # ---------- MCP ----------
    def mcp_tools(self) -> List[Dict]:
        r = requests.post(self._url("/mcp/tools/list"), headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()["tools"]

    def mcp_call(self, name: str, arguments: Dict) -> Dict:
        r = requests.post(self._url("/mcp/tools/call"),
                          json={"name": name, "arguments": arguments},
                          headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        body = r.json()
        return body["content"][0] if "content" in body and body["content"] else body

    # ---------- Sync ----------
    def sync_status(self) -> Dict:
        r = requests.get(self._url("/sync/auto/status"), headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def force_sync(self, sync_type: str = "both") -> Dict:
        assert sync_type in ("both", "pull", "push")
        r = requests.post(self._url("/sync/auto/force"),
                          json={"type": sync_type},
                          headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()

    def health(self) -> Dict:
        r = requests.get(self._url("/health"), headers=self.headers, timeout=self.timeout)
        r.raise_for_status()
        return r.json()


# -------- Execução direta (teste básico) --------
def _env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        print(f"❌ Variável de ambiente {name} não definida.", file=sys.stderr)
        sys.exit(1)
    return val

if __name__ == "__main__":
    base  = _env("OBSIDIAN_CLOUD_URL")
    token = _env("API_TOKEN")
    cli   = ObsidianCloudClient(base, token)

    # Apenas testa conexão básica
    print("✅ Conexão OK - listando arquivos raiz:")
    print(f"   {len(cli.list_root())} itens encontrados")
    print("✅ Status do sincronizador:")
    print(f"   Auto-sync: {cli.sync_status().get('auto_sync_enabled', 'N/A')}")

