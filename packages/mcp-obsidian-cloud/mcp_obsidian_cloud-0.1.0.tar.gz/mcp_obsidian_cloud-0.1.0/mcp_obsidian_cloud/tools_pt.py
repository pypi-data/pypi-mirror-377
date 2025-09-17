from .remote_client import ObsidianCloudClient

def build_tools(api: ObsidianCloudClient):
    return [
        {
            "name": "listar_arquivos_raiz",
            "description": "Lista todos os arquivos e pastas na raiz do cofre",
            "input_schema": {},
            "handler": lambda _: api.list_root()
        },
        {
            "name": "listar_arquivos_diretorio", 
            "description": "Lista arquivos/pastas dentro de um diretório",
            "input_schema": {"path": "string"},
            "handler": lambda args: api.list_root()  # Note: use list_root, não list_dir
        },
        {
            "name": "obter_conteudo_arquivo",
            "description": "Retorna o conteúdo de um arquivo",
            "input_schema": {"path": "string"},
            "handler": lambda args: api.get_file(args["path"])
        },
        {
            "name": "buscar",
            "description": "Busca documentos que contenham o texto informado",
            "input_schema": {"query": "string"},
            "handler": lambda args: api.search(args["query"])
        },
        {
            "name": "acrescentar_conteudo",
            "description": "Acrescenta conteúdo a um arquivo (cria se não existir)",
            "input_schema": {"path": "string", "content": "string"},
            "handler": lambda args: api.write_file(
                args["path"],
                (api.get_file(args["path"]) or "") + "\n" + args["content"]
            )
        },
        {
            "name": "inserir_conteudo_heading",
            "description": "Insere conteúdo após um heading específico",
            "input_schema": {"path": "string", "content": "string", "heading": "string"},
            "handler": lambda args: _patch_content(api, args)
        },
        {
            "name": "deletar_arquivo",
            "description": "Remove um arquivo ou pasta",
            "input_schema": {"path": "string"},
            "handler": lambda args: api.delete_file(args["path"])
        },
    ]

def _patch_content(api, args):
    atual = api.get_file(args["path"]) or ""
    heading = args.get("heading")
    novo = (
        atual.replace(heading, f"{heading}\n{args['content']}")
        if heading and heading in atual
        else atual + "\n" + args["content"]
    )
    return api.write_file(args["path"], novo)

