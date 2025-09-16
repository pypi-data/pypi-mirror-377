import sqlite3
import os
from rich.console import Console

console = Console()

class DBAdmin:
    def __init__(self):
        self.conn = sqlite3.connect(database="database.db")
        self.__create_table_repos()

    def __create_table_repos(self):
        query = """CREATE TABLE IF NOT EXISTS repositorios (
                id INTEGER PRIMARY KEY,
                node_id TEXT,
                name TEXT,
                full_name TEXT,
                owner TEXT,
                private BOOLEAN,
                html_url TEXT,
                fork BOOLEAN,
                language TEXT,
                forks_count INTEGER,
                stargazers_count INTEGER,
                watchers_count INTEGER,
                size INTEGER,
                default_branch TEXT,
                is_template BOOLEAN,
                archived BOOLEAN,
                disabled BOOLEAN,
                visibility TEXT,
                created_at TEXT,
                updated_at TEXT
            );
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()
    
    def __create_table_workflows_runs(self):
        query = """CREATE TABLE IF NOT EXISTS workflow_runs (
                id BIGINT PRIMARY KEY,
                name VARCHAR(255),
                node_id VARCHAR(255),
                head_branch VARCHAR(255),
                path VARCHAR(255),
                status VARCHAR(50),
                conclusion VARCHAR(50),
                html_url VARCHAR(255),
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                run_started_at TIMESTAMP,
                actor_name VARCHAR(255),
                actor_url VARCHAR(255),
                actor_type VARCHAR(50),
                repository_id BIGINT,
                repository_name VARCHAR(255)
            );
        """
        cursor = self.conn.cursor()
        cursor.execute(query)
        self.conn.commit()

    def return_connection(self):
        return self.conn

if __name__ == "__main__":
    DBAdmin()