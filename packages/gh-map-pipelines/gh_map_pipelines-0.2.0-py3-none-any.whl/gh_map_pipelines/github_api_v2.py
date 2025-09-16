import json, time
import yaml
from typing import List, Any, Optional
import os
import httpx
from functools import cache
import pandas as pd
from rich.console import Console
from rich.progress import Progress
from gh_map_pipelines.database_admin import DBAdmin
from datetime import datetime, timedelta
import sqlite3

console = Console()

class GitHub:
    def __init__(self, org: str):
        self.org = org
        self.workflows = []
        if os.environ.get("GH_TOKEN") == None:
            console.print("[red bold][-] [white italic]Define GitHub Token with environment variable [red bold]GH_TOKEN")
            exit(1)

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ.get("GH_TOKEN")}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.conn = DBAdmin().return_connection()
        self.conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        self._create_tables()
        self.rate_limit_wait_time = 60  # Tempo de espera em segundos após rate limit
        self._validate_token()  # Validar token na inicialização

    def _validate_token(self):
        """Valida o token do GitHub fazendo uma requisição de teste"""
        console.print("[blue bold][*] [white]Validating GitHub token...")
        
        try:
            # Fazer uma requisição simples para validar o token
            test_endpoint = "https://api.github.com/user"
            response = httpx.get(url=test_endpoint, headers=self.headers, timeout=10)
            
            if response.status_code == 401:
                console.print("[red bold][-] [white]Authentication failed! Invalid or expired GitHub token.")
                console.print("[yellow bold][!] [white]Please check your GH_TOKEN environment variable.")
                console.print("\n[dim]To generate a new token:")
                console.print("1. Go to https://github.com/settings/tokens")
                console.print("2. Click 'Generate new token (classic)'")
                console.print("3. Select scopes: repo, workflow, read:org")
                console.print("4. Export the token: export GH_TOKEN=your_token_here[/dim]")
                exit(1)
            elif response.status_code == 403:
                console.print("[red bold][-] [white]Access forbidden! Token doesn't have required permissions.")
                console.print("[yellow bold][!] [white]Required scopes: repo, workflow, read:org")
                exit(1)
            elif response.status_code == 200:
                user_data = response.json()
                console.print(f"[green bold][✓] [white]Authenticated as: {user_data.get('login', 'Unknown')}")
                
                # Verificar se a organização existe e temos acesso
                org_endpoint = f"https://api.github.com/orgs/{self.org}"
                org_response = httpx.get(url=org_endpoint, headers=self.headers, timeout=10)
                
                if org_response.status_code == 404:
                    console.print(f"[red bold][-] [white]Organization '{self.org}' not found or no access permission!")
                    console.print("[yellow bold][!] [white]Please check:")
                    console.print("  • Organization name is correct")
                    console.print("  • Your token has access to this organization")
                    console.print("  • You are a member of the organization")
                    exit(1)
                elif org_response.status_code == 401:
                    console.print(f"[red bold][-] [white]Not authorized to access organization '{self.org}'!")
                    exit(1)
                elif org_response.status_code == 200:
                    org_data = org_response.json()
                    console.print(f"[green bold][✓] [white]Organization found: {org_data.get('name', self.org)}")
                    console.print(f"[dim]  • Public repos: {org_data.get('public_repos', 0)}")
                    console.print(f"  • Private repos: {org_data.get('total_private_repos', 'N/A')}[/dim]")
                else:
                    console.print(f"[yellow bold][!] [white]Unexpected response when checking organization: {org_response.status_code}")
            else:
                console.print(f"[yellow bold][!] [white]Unexpected response during authentication: {response.status_code}")
                
        except httpx.TimeoutException:
            console.print("[red bold][-] [white]Timeout while validating token. Check your internet connection.")
            exit(1)
        except httpx.RequestError as e:
            console.print(f"[red bold][-] [white]Network error while validating token: {e}")
            exit(1)
        except Exception as e:
            console.print(f"[red bold][-] [white]Unexpected error during token validation: {e}")
            exit(1)
    
    def _create_tables(self):
        """Cria todas as tabelas necessárias se não existirem"""
        cursor = self.conn.cursor()
        
        # Tabela de controle de status de workflows
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT UNIQUE,
            raw_url TEXT,
            status TEXT,
            last_attempt TIMESTAMP,
            uses_found TEXT,
            error_message TEXT,
            retry_count INTEGER DEFAULT 0
        )
        """)
        
        # Tabela de controle de processamento geral
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS processing_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            process_type TEXT UNIQUE,
            status TEXT,
            last_update TIMESTAMP,
            metadata TEXT
        )
        """)
        
        # Tabela de controle de rate limit
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rate_limit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            endpoint TEXT,
            timestamp TIMESTAMP,
            retry_after INTEGER
        )
        """)
        
        self.conn.commit()

    def _log_rate_limit(self, endpoint: str, retry_after: int = None):
        """Registra ocorrência de rate limit"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO rate_limit_log (endpoint, timestamp, retry_after)
            VALUES (?, ?, ?)
        """, (endpoint, datetime.now(), retry_after or self.rate_limit_wait_time))
        self.conn.commit()

    def _can_make_request(self) -> bool:
        """Verifica se pode fazer requisição baseado no histórico de rate limit"""
        cursor = self.conn.cursor()
        result = cursor.execute("""
            SELECT MAX(timestamp) as last_limit, retry_after
            FROM rate_limit_log
            WHERE timestamp > datetime('now', '-5 minutes')
            ORDER BY timestamp DESC
            LIMIT 1
        """).fetchone()
        
        if result and result['last_limit']:
            last_limit = datetime.fromisoformat(result['last_limit'])
            retry_after = result['retry_after'] or self.rate_limit_wait_time
            wait_until = last_limit + timedelta(seconds=retry_after)
            
            if datetime.now() < wait_until:
                remaining = (wait_until - datetime.now()).seconds
                console.print(f"[yellow bold][!] [white]Rate limit ativo. Aguardando {remaining} segundos...")
                return False
        
        return True

    def _save_processing_status(self, process_type: str, status: str, metadata: dict = None):
        """Salva o status do processamento"""
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO processing_status (process_type, status, last_update, metadata)
            VALUES (?, ?, ?, ?)
        """, (process_type, status, datetime.now(), metadata_json))
        
        self.conn.commit()

    def _get_processing_status(self, process_type: str) -> Optional[dict]:
        """Obtém o status do processamento"""
        cursor = self.conn.cursor()
        result = cursor.execute("""
            SELECT status, last_update, metadata
            FROM processing_status
            WHERE process_type = ?
        """, (process_type,)).fetchone()
        
        if result:
            return {
                'status': result['status'],
                'last_update': result['last_update'],
                'metadata': json.loads(result['metadata']) if result['metadata'] else {}
            }
        return None

    def _append_to_parquet(self, df: pd.DataFrame, filename: str):
        """Adiciona dados ao arquivo parquet de forma incremental"""
        if os.path.exists(filename):
            existing_df = pd.read_parquet(filename)
            # Remove duplicatas baseado em colunas chave
            if 'node_id' in df.columns:
                combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['node_id'], keep='last')
            elif 'id' in df.columns:
                combined_df = pd.concat([existing_df, df]).drop_duplicates(subset=['id'], keep='last')
            else:
                combined_df = pd.concat([existing_df, df]).drop_duplicates()
            combined_df.to_parquet(filename, index=False)
        else:
            df.to_parquet(filename, index=False)

    @cache
    def __list_repos_org(self, page):
        """Lista repositórios de uma página específica"""
        if not self._can_make_request():
            time.sleep(self.rate_limit_wait_time)
            return self.__list_repos_org(page)  # Retry após esperar
        
        endpoint = f"https://api.github.com/orgs/{self.org}/repos"
        repos = []
        params = {
            "per_page": 100,
            "page": page,
            "sort": "updated"
        }

        try:
            r = httpx.get(url=endpoint, params=params, headers=self.headers, timeout=30)
            
            if r.status_code == 401:
                self.handle_auth_error("listing repositories")
            elif r.status_code == 403:
                console.print(f"[red bold][-] [white]Access forbidden! Insufficient permissions.")
                console.print("[yellow bold][!] [white]Ensure your token has: repo, workflow, read:org scopes.")
                exit(1)
            elif r.status_code == 429:
                self._log_rate_limit(endpoint)
                console.print(f"[red bold][-] [white]Rate limit atingido! Aguardando {self.rate_limit_wait_time} segundos...")
                time.sleep(self.rate_limit_wait_time)
                return self.__list_repos_org(page)  # Retry
            
            r_json = r.json()
            if r.status_code == 200 and len(r_json) != 0:
                for repo in r_json:
                    model = {
                        "id": repo.get('id'),
                        "node_id": repo.get('node_id'),
                        "name": repo.get('name'),
                        "full_name": repo.get('full_name'),
                        "owner": repo.get('owner').get('login'),
                        "private": repo.get('private'),
                        "html_url": repo.get('html_url'),
                        "fork": repo.get('fork'),
                        "language": repo.get('language'),
                        "forks_count": repo.get('forks_count'),
                        "stargazers_count": repo.get('stargazers_count'),
                        "watchers_count": repo.get('watchers_count'),
                        "size": repo.get('size'),
                        "default_branch": repo.get('default_branch'),
                        "is_template": repo.get('is_template'),
                        "archived": repo.get('archived'),
                        "disabled": repo.get('disabled'),
                        "visibility": repo.get('visibility'),
                        "created_at": repo.get('created_at'),
                        "updated_at": repo.get('updated_at')
                    }
                    repos.append(model)
                return r.status_code, repos
            elif len(r_json) == 0:
                return r.status_code, None
                
        except httpx.TimeoutException:
            console.print(f"[yellow bold][!] [white]Timeout ao buscar página {page}. Tentando novamente...")
            time.sleep(5)
            return self.__list_repos_org(page)
    
    def list_all_repos_org(self, write_db: bool = True, resume: bool = False):
        """Lista todos os repositórios com suporte a retomada"""
        status = self._get_processing_status('list_repos')
        start_page = 1
        
        if resume and status and status['status'] == 'in_progress':
            start_page = status['metadata'].get('last_page', 1) + 1
            console.print(f"[blue bold][*] [white]Retomando listagem de repositórios da página {start_page}")
        
        num = start_page
        repos_batch = []
        batch_size = 10  # Salva a cada 10 repositórios
        
        while True:
            self._save_processing_status('list_repos', 'in_progress', {'last_page': num - 1})
            
            status, repos = self.__list_repos_org(page=num)
            num += 1
            
            if repos:
                for r in repos:
                    console.print(f"[green bold][+] [white]Found {r.get('name')}")
                    repos_batch.append(r)
                    
                    # Salva em lote
                    if len(repos_batch) >= batch_size and write_db:
                        df = pd.DataFrame(repos_batch)
                        df.to_sql(name="repositorios", con=self.conn, if_exists="append", index=False)
                        self._append_to_parquet(df, "repos.parquet")
                        repos_batch = []  # Limpa o batch
                        console.print(f"[blue bold][*] [white]Batch de {batch_size} repositórios salvo")
                
                console.print("Waiting 5 seconds...")
                time.sleep(5)
            else:
                # Salva qualquer repositório restante
                if repos_batch and write_db:
                    df = pd.DataFrame(repos_batch)
                    df.to_sql(name="repositorios", con=self.conn, if_exists="append", index=False)
                    self._append_to_parquet(df, "repos.parquet")
                    console.print(f"[blue bold][*] [white]Últimos {len(repos_batch)} repositórios salvos")
                
                self._save_processing_status('list_repos', 'completed', {'total_pages': num - 1})
                break
        
        # Retorna todos os repos do banco
        df_all = pd.read_sql("SELECT * FROM repositorios", con=self.conn)
        return df_all.to_dict('records')
    
    def list_actions_runs(self, repo: str, id_repo: int, write_db: bool = True):
        """Lista workflows de um repositório com gravação incremental"""
        if not self._can_make_request():
            time.sleep(self.rate_limit_wait_time)
            return self.list_actions_runs(repo, id_repo, write_db)
        
        # Verifica se já foi processado
        cursor = self.conn.cursor()
        existing = cursor.execute("""
            SELECT COUNT(*) as count FROM workflow_runs WHERE id_repo = ?
        """, (id_repo,)).fetchone()
        
        if existing and existing['count'] > 0:
            console.print(f"[yellow bold][*] [white]Repositório {repo} já processado. Pulando...")
            return []
        
        count = 100
        page = 1
        endpoint = f"https://api.github.com/repos/{self.org}/{repo}/actions/workflows"
        workflows_batch = []
        
        while True:
            params = {
                "per_page": 100,
                "page": page
            }
            
            try:
                r = httpx.get(url=endpoint, params=params, headers=self.headers, timeout=30)
                
                if r.status_code == 401:
                    self.handle_auth_error(f"accessing repository '{repo}'")
                elif r.status_code == 403:
                    console.print(f"[red bold][-] [white]Access forbidden for {repo}! Check token permissions.")
                    console.print("[yellow bold][!] [white]Required scopes: repo, workflow, read:org")
                    exit(1)
                elif r.status_code == 429:
                    self._log_rate_limit(endpoint)
                    console.print(f"[red bold][-] [white]Rate limit! Aguardando {self.rate_limit_wait_time}s...")
                    time.sleep(self.rate_limit_wait_time)
                    continue  # Retry mesma página
                
                if r.status_code == 404:
                    console.print(f"[yellow bold][!] [white]Repositório {repo} não encontrado ou sem permissão")
                    break
                
                r_json = r.json()
                
                if r.status_code == 200:
                    workflows = r_json.get("workflows", [])
                    
                    if not workflows:
                        break
                    
                    # Processa workflows da página atual
                    for workflow in workflows:
                        model = self.__sanitize_workflow(workflow, id_repo)
                        workflows_batch.append(model)
                        console.print(f"[green bold][+] [white]Workflow: {workflow.get('name')} - State: {workflow.get('state')}")
                    
                    # Salva batch incrementalmente
                    if workflows_batch and write_db:
                        df = pd.DataFrame(workflows_batch)
                        df.to_sql(name="workflow_runs", con=self.conn, if_exists="append", index=False)
                        self._append_to_parquet(df, "workflow_runs.parquet")
                        workflows_batch = []
                    
                    # Verifica se há mais páginas
                    if r_json.get('total_count', 0) <= page * 100:
                        break
                    
                    page += 1
                    time.sleep(2)  # Espera entre páginas
                else:
                    console.print(f"[red bold][-] [white]Erro {r.status_code} ao buscar workflows de {repo}")
                    break
                    
            except httpx.TimeoutException:
                console.print(f"[yellow bold][!] [white]Timeout ao buscar workflows de {repo}. Tentando novamente...")
                time.sleep(5)
                continue
        
        return workflows_batch

    def __sanitize_workflow(self, workflow: dict, id_repo: int) -> dict:
        """Sanitiza dados de um workflow"""
        raw_url, branch, type_url = self.__get_raw_url(url=workflow.get('html_url'))
        
        return {
            "id": workflow.get('id'),
            "id_repo": id_repo,
            "name": workflow.get('name'),
            "node_id": workflow.get('node_id'),
            "state": workflow.get('state'),
            "path": workflow.get('path'),
            "created_at": workflow.get('created_at'),
            "updated_at": workflow.get('updated_at'),
            "html_url": workflow.get('html_url'),
            "raw_url": raw_url,
            "branch": branch,
            "type": type_url
        }

    @cache
    def __get_raw_url(self, url: str = "") -> tuple:
        """Converte URL do GitHub para URL raw"""
        branch = None
        type_url = url.split("/")[5]
        if type_url == "blob":
            branch = url.split("/")[6]
            url = url.replace("github.com", "raw.githubusercontent.com").replace("blob", "refs/heads")
        elif type_url == "actions":
            url = None
        return url, branch, type_url
    
    def __find_uses_recursive(self, data: Any, found_uses: List[str]) -> None:
        """Busca recursivamente por 'uses' em estrutura YAML"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'uses':
                    if isinstance(value, str):
                        found_uses.append(value)
                else:
                    self.__find_uses_recursive(value, found_uses)
        elif isinstance(data, list):
            for item in data:
                self.__find_uses_recursive(item, found_uses)

    def get_uses_from_github_yaml(self, raw_url: str, node_id: str) -> List[str]:
        """Obtém uses de um arquivo YAML com retry automático"""
        if not self._can_make_request():
            time.sleep(self.rate_limit_wait_time)
            return self.get_uses_from_github_yaml(raw_url, node_id)
        
        try:
            response = httpx.get(raw_url, headers=self.headers, timeout=30)
            
            if response.status_code == 401:
                self._update_workflow_status(node_id, 'auth_failed', error_message='Token expired or invalid')
                self.handle_auth_error(f"fetching workflow file from {raw_url}")
            elif response.status_code == 403:
                self._update_workflow_status(node_id, 'forbidden', error_message='Insufficient permissions')
                console.print(f"[red bold][-] [white]Access forbidden! Check token permissions.")
                exit(1)
            elif response.status_code == 429:
                self._log_rate_limit(raw_url)
                self._update_workflow_status(node_id, 'rate_limited', retry_count_increment=1)
                console.print(f"[red bold][-] [white]Rate limit! Aguardando {self.rate_limit_wait_time}s...")
                time.sleep(self.rate_limit_wait_time)
                return self.get_uses_from_github_yaml(raw_url, node_id)  # Retry
            
            if response.status_code == 404:
                self._update_workflow_status(node_id, 'not_found')
                return []
            
            response.raise_for_status()
            yaml_content = yaml.safe_load(response.text)
            uses_list = []
            if yaml_content:
                self.__find_uses_recursive(yaml_content, uses_list)
            
            return uses_list

        except yaml.YAMLError as e:
            self._update_workflow_status(node_id, 'yaml_error', error_message=str(e))
            console.print(f"[yellow bold][!] [white]Erro ao processar YAML: {e}")
            return []
        except Exception as e:
            self._update_workflow_status(node_id, 'error', error_message=str(e))
            console.print(f"[red bold][-] [white]Erro: {e}")
            return []
    
    def _update_workflow_status(self, node_id: str, status: str, error_message: str = None, retry_count_increment: int = 0):
        """Atualiza status de um workflow"""
        cursor = self.conn.cursor()
        
        if retry_count_increment > 0:
            cursor.execute("""
                UPDATE workflow_status 
                SET status = ?, last_attempt = ?, error_message = ?, retry_count = retry_count + ?
                WHERE node_id = ?
            """, (status, datetime.now(), error_message, retry_count_increment, node_id))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO workflow_status (node_id, status, last_attempt, error_message, retry_count)
                VALUES (?, ?, ?, ?, COALESCE((SELECT retry_count FROM workflow_status WHERE node_id = ?), 0))
            """, (node_id, status, datetime.now(), error_message, node_id))
        
        self.conn.commit()
    
    def _get_pending_workflows(self, max_retries: int = 3):
        """Retorna workflows pendentes ou com erro (com limite de tentativas)"""
        query = """
            SELECT DISTINCT wr.node_id, wr.html_url, wr.raw_url
            FROM workflow_runs wr
            LEFT JOIN workflow_status ws ON wr.node_id = ws.node_id
            WHERE (
                ws.status IS NULL 
                OR ws.status IN ('rate_limited', 'error', 'timeout')
                OR (ws.status = 'rate_limited' AND ws.retry_count < ?)
            )
            AND wr.raw_url IS NOT NULL
            AND (ws.retry_count IS NULL OR ws.retry_count < ?)
            ORDER BY COALESCE(ws.retry_count, 0) ASC, ws.last_attempt ASC
        """
        
        df = pd.read_sql(query, con=self.conn, params=(max_retries, max_retries))
        return df
    
    def populate_uses_actions(self, resume: bool = True, batch_size: int = 10):
        """Popula uses com controle de estado e retry"""
        # Verifica status do processamento
        if resume:
            status = self._get_processing_status('populate_uses')
            if status and status['status'] == 'completed':
                console.print("[green bold][✓] [white]Processamento de uses já foi concluído!")
                return
        
        # Obtém workflows pendentes
        df = self._get_pending_workflows()
        
        if df.empty:
            console.print("[green bold][✓] [white]Todos os workflows já foram processados!")
            self._save_processing_status('populate_uses', 'completed')
            return
        
        size_urls = len(df)
        console.print(f"[blue bold][*] [white]Processando {size_urls} workflows pendentes...")
        
        self._save_processing_status('populate_uses', 'in_progress', {'total': size_urls})
        
        with Progress() as progress:
            task1 = progress.add_task("[bold yellow][*] [white] Getting data", total=size_urls)
            uses_batch = []
            processed_count = 0
            
            for index, row in df.iterrows():
                node_id = row['node_id']
                raw_url = row['raw_url']
                
                # Verifica rate limit antes de processar
                if not self._can_make_request():
                    console.print(f"[yellow bold][!] [white]Aguardando rate limit expirar...")
                    time.sleep(self.rate_limit_wait_time)
                
                if raw_url:
                    uses = self.get_uses_from_github_yaml(raw_url=raw_url, node_id=node_id)
                    
                    if uses:
                        for use in uses:
                            model = {
                                "use": use,
                                "node_id_workflow": node_id,
                                "raw_url": raw_url
                            }
                            uses_batch.append(model)
                        
                        self._update_workflow_status(node_id, 'completed')
                    else:
                        self._update_workflow_status(node_id, 'completed')
                    
                    processed_count += 1
                    
                    # Salva batch incrementalmente
                    if len(uses_batch) >= batch_size:
                        df_batch = pd.DataFrame(uses_batch)
                        df_batch.to_sql(name="uses_workflows", con=self.conn, if_exists="append", index=False)
                        self._append_to_parquet(df_batch, "uses_workflows.parquet")
                        console.print(f"[blue bold][*] [white]Batch de {len(uses_batch)} uses salvo")
                        uses_batch = []
                    
                    # Atualiza progresso
                    self._save_processing_status('populate_uses', 'in_progress', {
                        'total': size_urls,
                        'processed': processed_count
                    })
                    
                    progress.update(task1, advance=1, description=f"[bold yellow][*] [white] Processing: {raw_url}")
                    time.sleep(2)  # Espera entre requisições
                else:
                    self._update_workflow_status(node_id, 'skipped')
                    progress.update(task1, advance=1)
            
            # Salva uses restantes
            if uses_batch:
                df_batch = pd.DataFrame(uses_batch)
                df_batch.to_sql(name="uses_workflows", con=self.conn, if_exists="append", index=False)
                self._append_to_parquet(df_batch, "uses_workflows.parquet")
                console.print(f"[blue bold][*] [white]Últimos {len(uses_batch)} uses salvos")
        
        self._save_processing_status('populate_uses', 'completed', {'total_processed': processed_count})
        console.print(f"[green bold][✓] [white]Processamento concluído! {processed_count} workflows processados.")
    
    def check_token_validity(self) -> bool:
        """Verifica se o token ainda é válido"""
        try:
            test_endpoint = "https://api.github.com/user"
            response = httpx.get(url=test_endpoint, headers=self.headers, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def handle_auth_error(self, context: str = ""):
        """Tratamento centralizado de erros de autenticação"""
        console.print(f"\n[red bold]⚠️  AUTHENTICATION ERROR ⚠️[/red bold]")
        console.print(f"[red bold][-] [white]Token authentication failed{' while ' + context if context else ''}!")
        console.print("\n[yellow bold]Possible causes:[/yellow bold]")
        console.print("  • Token expired")
        console.print("  • Token revoked")
        console.print("  • Token deleted")
        console.print("  • Invalid token format")
        console.print("\n[cyan bold]How to fix:[/cyan bold]")
        console.print("  1. Generate a new token at: https://github.com/settings/tokens")
        console.print("  2. Ensure these scopes are selected:")
        console.print("     ✓ repo (Full control of private repositories)")
        console.print("     ✓ workflow (Update GitHub Action workflows)")
        console.print("     ✓ read:org (Read org and team membership)")
        console.print("  3. Update your environment variable:")
        console.print("     [dim]Linux/Mac:[/dim] export GH_TOKEN='your_new_token_here'")
        console.print("     [dim]Windows:[/dim] set GH_TOKEN=your_new_token_here")
        console.print("  4. Run the command again")
        console.print("\n[dim]For more info: https://docs.github.com/en/authentication[/dim]")
        
        # Salvar estado antes de sair
        self._save_processing_status('last_error', 'auth_failed', {
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        exit(1)
    
    def get_status_report(self):
        """Gera relatório de status do processamento"""
        cursor = self.conn.cursor()
        
        # Status geral
        repos_count = cursor.execute("SELECT COUNT(*) FROM repositorios").fetchone()[0]
        workflows_count = cursor.execute("SELECT COUNT(*) FROM workflow_runs").fetchone()[0]
        uses_count = cursor.execute("SELECT COUNT(*) FROM uses_workflows").fetchone()[0]
        
        # Status de processamento
        completed = cursor.execute("SELECT COUNT(*) FROM workflow_status WHERE status = 'completed'").fetchone()[0]
        errors = cursor.execute("SELECT COUNT(*) FROM workflow_status WHERE status IN ('error', 'yaml_error', 'not_found')").fetchone()[0]
        rate_limited = cursor.execute("SELECT COUNT(*) FROM workflow_status WHERE status = 'rate_limited'").fetchone()[0]
        
        console.print("\n[bold cyan]📊 Status Report[/bold cyan]")
        console.print(f"├── Repositórios: {repos_count}")
        console.print(f"├── Workflows: {workflows_count}")
        console.print(f"├── Uses encontrados: {uses_count}")
        console.print(f"├── Workflows processados: {completed}")
        console.print(f"├── Erros: {errors}")
        console.print(f"└── Rate limited (pendentes): {rate_limited}")
        
        return {
            'repos': repos_count,
            'workflows': workflows_count,
            'uses': uses_count,
            'completed': completed,
            'errors': errors,
            'rate_limited': rate_limited
        }
