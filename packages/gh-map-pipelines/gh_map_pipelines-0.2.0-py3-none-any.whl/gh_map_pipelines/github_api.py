import json, time
import yaml
from typing import List, Any
import os
import httpx
from functools import cache
import time
import pandas as pd
from rich.console import Console
from rich.progress import Progress
from gh_map_pipelines.database_admin import DBAdmin
from datetime import datetime

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
        self._create_status_table()

    def _create_status_table(self):
        """Cria tabela de controle de status se não existir"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS workflow_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id TEXT UNIQUE,
            raw_url TEXT,
            status TEXT,
            last_attempt TIMESTAMP,
            uses_found TEXT,
            error_message TEXT
        )
        """
        cursor = self.conn.cursor()
        cursor.execute(create_table_sql)
        self.conn.commit()

    def _save_workflow_status(self, node_id: str, raw_url: str, status: str, uses_found: List[str] = None, error_message: str = None):
        """Salva o status do processamento de um workflow"""
        cursor = self.conn.cursor()
        uses_json = json.dumps(uses_found) if uses_found else None
        
        cursor.execute("""
            INSERT OR REPLACE INTO workflow_status (node_id, raw_url, status, last_attempt, uses_found, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (node_id, raw_url, status, datetime.now(), uses_json, error_message))
        
        self.conn.commit()

    def _get_pending_workflows(self):
        """Retorna workflows que ainda não foram processados ou tiveram erro"""
        df_all = pd.read_sql(con=self.conn, sql="SELECT node_id, html_url FROM workflow_runs GROUP BY node_id")
        
        # Adiciona raw_urls
        raw_urls = []
        for index in range(0, len(df_all['html_url'])):
            raw_url, branch, type_url = self.__get_raw_url(url=df_all['html_url'][index])
            raw_urls.append(raw_url)
        df_all["raw_url"] = raw_urls
        
        # Verifica quais já foram processados com sucesso
        df_processed = pd.read_sql(con=self.conn, sql="SELECT node_id FROM workflow_status WHERE status = 'completed'")
        processed_node_ids = set(df_processed['node_id'].tolist()) if not df_processed.empty else set()
        
        # Filtra apenas os pendentes
        df_pending = df_all[~df_all['node_id'].isin(processed_node_ids)]
        
        return df_pending

    def _check_last_rate_limit_error(self):
        """Verifica se houve erro de rate limit recente"""
        cursor = self.conn.cursor()
        result = cursor.execute("""
            SELECT COUNT(*) as count, MAX(last_attempt) as last_error
            FROM workflow_status 
            WHERE status = 'rate_limited'
            AND last_attempt > datetime('now', '-1 hour')
        """).fetchone()
        
        if result['count'] > 0:
            console.print(f"[red bold][-] [white]Erro de rate limit detectado em {result['last_error']}. Aguarde antes de tentar novamente.")
            return True
        return False

    @cache
    def __list_repos_org(self, page):
        endpoint = f"https://api.github.com/orgs/{self.org}/repos"
        repos = []
        params = {
            "per_page": 100,
            "page": page,
            "sort": "updated"
        }

        r = httpx.get(url=endpoint, params=params, headers=self.headers)
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
    
    @cache
    def list_all_repos_org(self, write_db: bool = False):
        num = 1
        repos = []
        while True:
            status, repo = self.__list_repos_org(page=num)
            num += 1
            time.sleep(5)
            
            if repo:
                for r in repo:
                    console.print(f"[green bold][+] [white]Found {r.get('name')}")
                    repos.append(r)
                    if write_db:
                        df = pd.DataFrame(repos)
                        df.to_sql(name="repositorios", con=self.conn, if_exists="replace", index=False)
                        df.to_parquet(path="repos.parquet", index=False)
            else:
                break
            console.print("Waiting 5 seconds...")
        
        return repos
    
    @cache
    def list_actions_runs(self, repo, id_repo, write_db: bool = False):
        count = 100
        page = 1
        endpoint = f"https://api.github.com/repos/{self.org}/{repo}/actions/workflows"
        params = {
            "per_page": 100,
            "page": 1
        }
        r = httpx.get(url=endpoint, params=params, headers=self.headers)
        r_json = r.json()
        if r.status_code == 200 and len(r_json.get("workflows")) != 0:
            self.workflows = r_json.get("workflows")
        
        while r_json.get('total_count') > count:
            count += 100
            page += 1
            params['page'] = page
            r = httpx.get(url=endpoint, params=params, headers=self.headers)
            r_json = r.json()
            for w in r_json.get("workflows"):
                self.workflows.append(w)

        self.__sanitize_actions_runs(id_repo=id_repo)

        if write_db:
            df = pd.DataFrame(self.workflows)
            df.to_sql(name="workflow_runs", con=self.conn, if_exists="append", index=False)
            df.to_parquet(path="workflow_runs.parquet", index=False)

        return self.workflows

    def __sanitize_actions_runs(self, id_repo) -> None:
        workflow_temp = self.workflows
        self.workflows = []
        for workflow in workflow_temp:
            model = {
                "id": workflow.get('id'),
                "id_repo": id_repo,
                "name": workflow.get('name'),
                "node_id": workflow.get('node_id'),
                "state": workflow.get('state'),
                "path": workflow.get('path'),
                "status": workflow.get('status'),
                "created_at": workflow.get('created_at'),
                "updated_at": workflow.get('updated_at'),
                "html_url": workflow.get('html_url'),
                "raw_url": self.__get_raw_url(url=workflow.get('html_url'))[0],
                "branch": self.__get_raw_url(url=workflow.get('html_url'))[1],
                "type": self.__get_raw_url(url=workflow.get('html_url'))[2]
            }
            self.workflows.append(model)
            console.print(f"[green bold][+] [white]Workflow: {workflow.get('name')} - State: {workflow.get('state')}")
        del(workflow_temp)

    @cache
    def __get_raw_url(self, url: str = "") -> tuple:
        branch = None
        type_url = url.split("/")[5]
        if type_url == "blob":
            branch = url.split("/")[6]
            url = url.replace("github.com", "raw.githubusercontent.com").replace("blob", "refs/heads")
        elif type_url == "actions":
            url = None
        return url, branch, type_url
    
    def __find_uses_recursive(self, data: Any, found_uses: List[str]) -> None:
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

    @cache
    def get_uses_from_github_yaml(self, raw_url: str) -> List[str]:
        try:
            response = httpx.get(raw_url, headers=self.headers)
            
            # Verifica rate limit
            if response.status_code == 429:
                console.print(f"[red bold][-] [white]Rate limit atingido! Status: {response.status_code}")
                return None  # Indica rate limit
            
            response.raise_for_status()
            yaml_content = yaml.safe_load(response.text)
            uses_list = []
            if yaml_content:
                self.__find_uses_recursive(yaml_content, uses_list)
            
            if response.status_code != 200:
                print(f"Erro ao acessar a URL: {response.status_code}")
                return []
            
            return uses_list

        except yaml.YAMLError as e:
            print(f"Erro ao processar o arquivo YAML: {e}")
            return []
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
            return []
    
    def populate_uses_actions(self):
        # Verifica se houve erro de rate limit recente
        if self._check_last_rate_limit_error():
            console.print("[yellow bold][!] [white]Rate limit detectado recentemente. Tente novamente mais tarde.")
            exit(1)
        
        # Obtém workflows pendentes
        df = self._get_pending_workflows()
        
        if df.empty:
            console.print("[green bold][✓] [white]Todos os workflows já foram processados!")
            return
        
        size_urls = len(df)
        console.print(f"[blue bold][*] [white]Processando {size_urls} workflows pendentes...")
        
        with Progress() as progress:
            task1 = progress.add_task("[bold yellow][*] [white] Getting data", total=size_urls)
            uses_in_workflows = []
            
            for index, row in df.iterrows():
                node_id = row['node_id']
                raw_url = row['raw_url']
                
                if raw_url:
                    uses = self.get_uses_from_github_yaml(raw_url=raw_url)
                    
                    # Verifica se houve rate limit
                    if uses is None:
                        self._save_workflow_status(node_id, raw_url, 'rate_limited', error_message='HTTP 429 - Rate limit exceeded')
                        console.print(f"[red bold][-] [white]Rate limit atingido ao processar {raw_url}")
                        console.print("[yellow bold][!] [white]Estado salvo. Execute o script novamente mais tarde para continuar.")
                        
                        # Salva uses coletados até agora
                        if uses_in_workflows:
                            df_partial = pd.DataFrame(uses_in_workflows)
                            df_partial.to_sql(name="uses_workflows", con=self.conn, if_exists="append", index=False)
                            console.print(f"[green bold][✓] [white]{len(uses_in_workflows)} uses salvos antes do rate limit.")
                        
                        exit(1)
                    
                    # Processa uses encontrados
                    if len(uses) > 0:
                        for use in uses:
                            model = {
                                "use": use,
                                "node_id_workflow": node_id,
                                "raw_url": raw_url
                            }
                            uses_in_workflows.append(model)
                        self._save_workflow_status(node_id, raw_url, 'completed', uses_found=uses)
                    else:
                        self._save_workflow_status(node_id, raw_url, 'completed', uses_found=[])
                    
                    console.print("Waiting 5 seconds...")
                    time.sleep(5)
                else:
                    # URL raw é None (provavelmente type_url == "actions")
                    self._save_workflow_status(node_id, None, 'skipped', error_message='No raw URL available')
                
                progress.update(task1, advance=1, description=f"[bold yellow][*] [white] Getting data: {raw_url}")
            
            # Salva todos os uses encontrados
            if uses_in_workflows:
                df2 = pd.DataFrame(uses_in_workflows)
                df2.to_sql(name="uses_workflows", con=self.conn, if_exists="replace", index=False)
                df2.to_parquet(path="uses_workflows.parquet", index=False)
                console.print(f"[green bold][✓] [white]Processamento concluído! {len(uses_in_workflows)} uses encontrados.")
                
if __name__ == "__main__":
    g = GitHub(org="enterprisesecure")
    
    # Verifica se já existem repositórios no banco
    cursor = g.conn.cursor()
    repo_count = cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='repositorios'").fetchone()[0]
    
    if repo_count == 0:
        # Primeira execução - busca todos os repositórios
        all_repos = g.list_all_repos_org(write_db=True)
        for repo in all_repos:
            g.list_actions_runs(repo=repo.get('name'), id_repo=repo.get('id'), write_db=True)
            console.print("Waiting 5 seconds...")
            time.sleep(5)
    
    # Processa uses dos workflows (com controle de estado)
    g.populate_uses_actions()