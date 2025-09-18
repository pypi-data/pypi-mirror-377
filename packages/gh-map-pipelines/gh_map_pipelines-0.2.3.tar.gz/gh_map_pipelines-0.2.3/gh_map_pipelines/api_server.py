"""
FastAPI application for gh_map_pipelines analytics
Provides endpoints for analyzing GitHub Actions usage across repositories
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd
from pathlib import Path
from pydantic import BaseModel
from contextlib import contextmanager
from gh_map_pipelines.dashboard import DASHBOARD_HTML
import json
import os

# Pydantic models for responses
class RepositoryStats(BaseModel):
    total_repos: int
    public_repos: int
    private_repos: int
    archived_repos: int
    disabled_repos: int
    template_repos: int
    forked_repos: int
    
class LanguageDistribution(BaseModel):
    language: str
    count: int
    percentage: float
    
class RepositoryMetrics(BaseModel):
    name: str
    stars: int
    forks: int
    watchers: int
    size: int
    url: str
    
class ActionUsage(BaseModel):
    action: str
    repository: str
    repository_id: int
    workflow_count: int
    
class RepoWithLink(BaseModel):
    name: str
    url: str
    
class ActionSummary(BaseModel):
    action: str
    total_uses: int
    unique_repos: int
    repos_using: List[RepoWithLink]
    repos_not_using: List[RepoWithLink]

class WorkflowStats(BaseModel):
    total_workflows: int
    active_workflows: int
    inactive_workflows: int
    workflows_per_repo: Dict[str, int]
    
class DashboardData(BaseModel):
    repository_stats: RepositoryStats
    language_distribution: List[LanguageDistribution]
    top_starred: List[RepositoryMetrics]
    top_forked: List[RepositoryMetrics]
    recent_updates: List[Dict[str, Any]]
    workflow_stats: WorkflowStats
    
# FastAPI app
app = FastAPI(
    title="GitHub Map Pipelines API",
    description="API for analyzing GitHub Actions usage across organizations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_PATH = "database.db"

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Helper functions
def dict_from_row(row):
    """Convert sqlite3.Row to dict"""
    return dict(zip(row.keys(), row))

# API Endpoints

@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "GitHub Map Pipelines API"}

@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def get_dashboard():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api/stats/overview", response_model=RepositoryStats, tags=["Statistics"])
async def get_repository_overview():
    """Get overview statistics of all repositories"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total repos
        total = cursor.execute("SELECT COUNT(*) FROM repositorios").fetchone()[0]
        
        # Public vs Private
        public = cursor.execute("SELECT COUNT(*) FROM repositorios WHERE private = 0").fetchone()[0]
        private = cursor.execute("SELECT COUNT(*) FROM repositorios WHERE private = 1").fetchone()[0]
        
        # Archived
        archived = cursor.execute("SELECT COUNT(*) FROM repositorios WHERE archived = 1").fetchone()[0]
        
        # Disabled
        disabled = cursor.execute("SELECT COUNT(*) FROM repositorios WHERE disabled = 1").fetchone()[0]
        
        # Templates
        templates = cursor.execute("SELECT COUNT(*) FROM repositorios WHERE is_template = 1").fetchone()[0]
        
        # Forks
        forks = cursor.execute("SELECT COUNT(*) FROM repositorios WHERE fork = 1").fetchone()[0]
        
        return RepositoryStats(
            total_repos=total,
            public_repos=public,
            private_repos=private,
            archived_repos=archived,
            disabled_repos=disabled,
            template_repos=templates,
            forked_repos=forks
        )

@app.get("/api/stats/languages", response_model=List[LanguageDistribution], tags=["Statistics"])
async def get_language_distribution():
    """Get distribution of programming languages across repositories"""
    with get_db() as conn:
        query = """
        SELECT 
            COALESCE(language, 'Not specified') as language,
            COUNT(*) as count
        FROM repositorios
        GROUP BY language
        ORDER BY count DESC
        """
        
        df = pd.read_sql_query(query, conn)
        total = df['count'].sum()
        
        result = []
        for _, row in df.iterrows():
            result.append(LanguageDistribution(
                language=row['language'],
                count=row['count'],
                percentage=round((row['count'] / total) * 100, 2)
            ))
        
        return result

@app.get("/api/stats/top-starred", response_model=List[RepositoryMetrics], tags=["Statistics"])
async def get_top_starred_repos(limit: int = Query(10, ge=1, le=50)):
    """Get top repositories by star count"""
    with get_db() as conn:
        query = """
        SELECT name, stargazers_count as stars, forks_count as forks, 
               watchers_count as watchers, size, html_url
        FROM repositorios
        WHERE archived = 0 AND disabled = 0
        ORDER BY stargazers_count DESC
        LIMIT ?
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (limit,)).fetchall()
        
        return [
            RepositoryMetrics(
                name=row['name'],
                stars=row['stars'],
                forks=row['forks'],
                watchers=row['watchers'],
                size=row['size'],
                url=row['html_url']
            ) for row in results
        ]

@app.get("/api/stats/top-forked", response_model=List[RepositoryMetrics], tags=["Statistics"])
async def get_top_forked_repos(limit: int = Query(10, ge=1, le=50)):
    """Get top repositories by fork count"""
    with get_db() as conn:
        query = """
        SELECT name, stargazers_count as stars, forks_count as forks, 
               watchers_count as watchers, size, html_url
        FROM repositorios
        WHERE archived = 0 AND disabled = 0
        ORDER BY forks_count DESC
        LIMIT ?
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (limit,)).fetchall()
        
        return [
            RepositoryMetrics(
                name=row['name'],
                stars=row['stars'],
                forks=row['forks'],
                watchers=row['watchers'],
                size=row['size'],
                url=row['html_url']
            ) for row in results
        ]

@app.get("/api/actions/usage", response_model=ActionSummary, tags=["Actions"])
async def get_action_usage(action: str = Query(..., description="Action name (e.g., actions/checkout)")):
    """
    Get detailed usage information for a specific GitHub Action
    Shows which repositories use it and which don't, with links to the actual usage
    
    Example: /api/actions/usage?action=actions/checkout
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get repos using this action with the workflow file URL
        query_using = """
        SELECT DISTINCT 
            r.name, 
            r.id,
            r.html_url as repo_url,
            uw.raw_url
        FROM repositorios r
        JOIN workflow_runs wr ON r.id = wr.id_repo
        JOIN uses_workflows uw ON wr.node_id = uw.node_id_workflow
        WHERE uw.use LIKE ?
        GROUP BY r.name, r.id, r.html_url
        """
        
        repos_using = cursor.execute(query_using, (f"%{action}%",)).fetchall()
        
        # Build repos_using with links to workflow files
        repos_using_list = []
        for row in repos_using:
            # Convert raw_url to GitHub blob URL if needed
            raw_url = row['raw_url']
            if raw_url and 'raw.githubusercontent.com' in raw_url:
                # Convert raw URL to GitHub web URL
                # From: https://raw.githubusercontent.com/org/repo/refs/heads/main/.github/workflows/file.yml
                # To: https://github.com/org/repo/blob/main/.github/workflows/file.yml
                github_url = raw_url.replace('raw.githubusercontent.com', 'github.com')
                github_url = github_url.replace('/refs/heads/', '/blob/')
            else:
                # Fallback to repository URL if raw_url is not available
                github_url = row['repo_url']
            
            repos_using_list.append(RepoWithLink(
                name=row['name'],
                url=github_url
            ))
        
        repos_using_ids = list(set([row['id'] for row in repos_using]))
        
        # Get repos NOT using this action with their regular repo URLs
        if repos_using_ids:
            placeholders = ','.join('?' * len(repos_using_ids))
            query_not_using = f"""
            SELECT name, html_url 
            FROM repositorios
            WHERE id NOT IN ({placeholders})
            AND archived = 0 AND disabled = 0
            """
            repos_not_using = cursor.execute(query_not_using, repos_using_ids).fetchall()
        else:
            repos_not_using = cursor.execute(
                "SELECT name, html_url FROM repositorios WHERE archived = 0 AND disabled = 0"
            ).fetchall()
        
        repos_not_using_list = [
            RepoWithLink(name=row['name'], url=row['html_url']) 
            for row in repos_not_using
        ]
        
        # Get total usage count
        total_uses = cursor.execute(
            "SELECT COUNT(*) FROM uses_workflows WHERE use LIKE ?",
            (f"%{action}%",)
        ).fetchone()[0]
        
        return ActionSummary(
            action=action,
            total_uses=total_uses,
            unique_repos=len(repos_using_list),
            repos_using=repos_using_list,
            repos_not_using=repos_not_using_list
        )

# Manter o endpoint antigo para compatibilidade, mas com path:path para aceitar /
@app.get("/api/actions/usage/{action_name:path}", response_model=ActionSummary, tags=["Actions"], deprecated=True)
async def get_action_usage_legacy(action_name: str):
    """
    [DEPRECATED] Use /api/actions/usage?action=name instead
    Legacy endpoint for backward compatibility
    """
    return await get_action_usage(action=action_name)

@app.get("/api/actions/all", tags=["Actions"])
async def get_all_actions(limit: int = Query(50, ge=1, le=500)):
    """Get all unique actions used across the organization"""
    with get_db() as conn:
        query = """
        SELECT 
            use as action,
            COUNT(*) as usage_count,
            COUNT(DISTINCT node_id_workflow) as workflow_count
        FROM uses_workflows
        GROUP BY use
        ORDER BY usage_count DESC
        LIMIT ?
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (limit,)).fetchall()
        
        return [dict_from_row(row) for row in results]

@app.get("/api/actions/usage-details", tags=["Actions"])
async def get_action_usage_details(action: str = Query(..., description="Action name (e.g., actions/checkout)")):
    """
    Get detailed usage information for a specific GitHub Action
    Including all workflow files where it's used
    
    Example: /api/actions/usage-details?action=actions/checkout
    """
    with get_db() as conn:
        query = """
        SELECT 
            r.name as repo_name,
            r.html_url as repo_url,
            wr.name as workflow_name,
            wr.path as workflow_path,
            uw.raw_url,
            COUNT(*) as usage_count
        FROM uses_workflows uw
        JOIN workflow_runs wr ON uw.node_id_workflow = wr.node_id
        JOIN repositorios r ON wr.id_repo = r.id
        WHERE uw.use LIKE ?
        GROUP BY r.name, r.html_url, wr.name, wr.path, uw.raw_url
        ORDER BY r.name, wr.name
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (f"%{action}%",)).fetchall()
        
        # Group by repository
        repos_detail = {}
        for row in results:
            repo_name = row['repo_name']
            if repo_name not in repos_detail:
                repos_detail[repo_name] = {
                    'repo_name': repo_name,
                    'repo_url': row['repo_url'],
                    'workflows': []
                }
            
            # Convert raw URL to GitHub web URL
            github_url = row['raw_url']
            if github_url and 'raw.githubusercontent.com' in github_url:
                github_url = github_url.replace('raw.githubusercontent.com', 'github.com')
                github_url = github_url.replace('/refs/heads/', '/blob/')
            
            repos_detail[repo_name]['workflows'].append({
                'workflow_name': row['workflow_name'],
                'workflow_path': row['workflow_path'],
                'workflow_url': github_url,
                'usage_count': row['usage_count']
            })
        
        return {
            'action': action,
            'total_repos': len(repos_detail),
            'details': list(repos_detail.values())
        }

# Manter o endpoint antigo para compatibilidade
@app.get("/api/actions/usage-details/{action_name:path}", tags=["Actions"], deprecated=True)
async def get_action_usage_details_legacy(action_name: str):
    """
    [DEPRECATED] Use /api/actions/usage-details?action=name instead
    Legacy endpoint for backward compatibility
    """
    return await get_action_usage_details(action=action_name)

@app.get("/api/actions/by-repo/{repo_name}", tags=["Actions"])
async def get_actions_by_repo(repo_name: str):
    """Get all actions used by a specific repository"""
    with get_db() as conn:
        query = """
        SELECT DISTINCT uw.use as action, COUNT(*) as usage_count
        FROM uses_workflows uw
        JOIN workflow_runs wr ON uw.node_id_workflow = wr.node_id
        JOIN repositorios r ON wr.id_repo = r.id
        WHERE r.name = ?
        GROUP BY uw.use
        ORDER BY usage_count DESC
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (repo_name,)).fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Repository '{repo_name}' not found or has no workflows")
        
        return [dict_from_row(row) for row in results]

@app.get("/api/workflows/stats", response_model=WorkflowStats, tags=["Workflows"])
async def get_workflow_stats():
    """Get workflow statistics across all repositories"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total workflows
        total = cursor.execute("SELECT COUNT(DISTINCT id) FROM workflow_runs").fetchone()[0]
        
        # Active vs Inactive
        active = cursor.execute("SELECT COUNT(DISTINCT id) FROM workflow_runs WHERE state = 'active'").fetchone()[0]
        inactive = total - active
        
        # Workflows per repo
        query_per_repo = """
        SELECT r.name, COUNT(DISTINCT wr.id) as workflow_count
        FROM repositorios r
        LEFT JOIN workflow_runs wr ON r.id = wr.id_repo
        GROUP BY r.name
        ORDER BY workflow_count DESC
        """
        
        per_repo_results = cursor.execute(query_per_repo).fetchall()
        workflows_per_repo = {row['name']: row['workflow_count'] for row in per_repo_results}
        
        return WorkflowStats(
            total_workflows=total,
            active_workflows=active,
            inactive_workflows=inactive,
            workflows_per_repo=workflows_per_repo
        )

@app.get("/api/dashboard", response_model=DashboardData, tags=["Dashboard"])
async def get_dashboard_data():
    """Get all dashboard data in a single endpoint"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Repository stats
        repo_stats = await get_repository_overview()
        
        # Language distribution (top 10)
        languages = await get_language_distribution()
        
        # Top starred (top 5)
        top_starred = await get_top_starred_repos(limit=5)
        
        # Top forked (top 5)
        top_forked = await get_top_forked_repos(limit=5)
        
        # Recent updates
        recent_query = """
        SELECT name, updated_at, stargazers_count, language
        FROM repositorios
        WHERE archived = 0 AND disabled = 0
        ORDER BY updated_at DESC
        LIMIT 10
        """
        recent_results = cursor.execute(recent_query).fetchall()
        recent_updates = [dict_from_row(row) for row in recent_results]
        
        # Workflow stats
        workflow_stats = await get_workflow_stats()
        
        return DashboardData(
            repository_stats=repo_stats,
            language_distribution=languages[:10],
            top_starred=top_starred,
            top_forked=top_forked,
            recent_updates=recent_updates,
            workflow_stats=workflow_stats
        )

@app.get("/api/repos/search", tags=["Repositories"])
async def search_repositories(
    q: Optional[str] = Query(None, description="Search query"),
    language: Optional[str] = Query(None, description="Filter by language"),
    visibility: Optional[str] = Query(None, description="Filter by visibility (public/private)"),
    archived: Optional[bool] = Query(None, description="Filter by archived status"),
    limit: int = Query(20, ge=1, le=100)
):
    """Search and filter repositories"""
    with get_db() as conn:
        query = "SELECT * FROM repositorios WHERE 1=1"
        params = []
        
        if q:
            query += " AND (name LIKE ? OR full_name LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%"])
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if visibility:
            if visibility == "public":
                query += " AND private = 0"
            elif visibility == "private":
                query += " AND private = 1"
        
        if archived is not None:
            query += " AND archived = ?"
            params.append(1 if archived else 0)
        
        query += f" LIMIT {limit}"
        
        cursor = conn.cursor()
        results = cursor.execute(query, params).fetchall()
        
        return [dict_from_row(row) for row in results]

@app.get("/api/runners/usage", tags=["Runners"])
async def get_runner_usage():
    """
    Get usage statistics for all runners (runs-on values)
    Shows which runners are most used across workflows
    """
    with get_db() as conn:
        query = """
        SELECT 
            runs_on,
            COUNT(*) as usage_count,
            COUNT(DISTINCT node_id_workflow) as workflow_count,
            COUNT(DISTINCT job_name) as job_count
        FROM runs_on_workflows
        GROUP BY runs_on
        ORDER BY usage_count DESC
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query).fetchall()
        
        return [
            {
                "runner": row['runs_on'],
                "usage_count": row['usage_count'],
                "workflow_count": row['workflow_count'],
                "job_count": row['job_count']
            }
            for row in results
        ]

@app.get("/api/runners/by-repo/{repo_name}", tags=["Runners"])
async def get_runners_by_repo(repo_name: str):
    """
    Get all runners used by a specific repository
    """
    with get_db() as conn:
        query = """
        SELECT DISTINCT 
            ro.runs_on,
            ro.job_name,
            COUNT(*) as usage_count
        FROM runs_on_workflows ro
        JOIN workflow_runs wr ON ro.node_id_workflow = wr.node_id
        JOIN repositorios r ON wr.id_repo = r.id
        WHERE r.name = ?
        GROUP BY ro.runs_on, ro.job_name
        ORDER BY usage_count DESC
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (repo_name,)).fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail=f"Repository '{repo_name}' not found or has no runners")
        
        return [dict_from_row(row) for row in results]

@app.get("/api/runners/distribution", tags=["Runners"])
async def get_runner_distribution():
    """
    Get distribution of runner types (ubuntu, windows, macos, self-hosted, etc.)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Categorizar runners
        results = cursor.execute("""
            SELECT runs_on, COUNT(*) as count
            FROM runs_on_workflows
            GROUP BY runs_on
        """).fetchall()
        
        distribution = {
            'ubuntu': 0,
            'windows': 0,
            'macos': 0,
            'self_hosted': 0,
            'other': 0
        }
        
        for row in results:
            runner = row['runs_on'].lower()
            count = row['count']
            
            if 'ubuntu' in runner:
                distribution['ubuntu'] += count
            elif 'windows' in runner:
                distribution['windows'] += count
            elif 'macos' in runner or 'mac' in runner:
                distribution['macos'] += count
            elif 'self-hosted' in runner:
                distribution['self_hosted'] += count
            else:
                distribution['other'] += count
        
        total = sum(distribution.values())
        
        return {
            'distribution': distribution,
            'percentages': {
                k: round((v / total * 100), 2) if total > 0 else 0
                for k, v in distribution.items()
            },
            'total': total
        }

@app.get("/api/runners/repos-using", tags=["Runners"])
async def get_repos_using_runner(runner: str = Query(..., description="Runner name (e.g., ubuntu-latest)")):
    """
    Get all repositories using a specific runner
    """
    with get_db() as conn:
        query = """
        SELECT DISTINCT
            r.name as repo_name,
            r.html_url,
            COUNT(DISTINCT ro.job_name) as job_count
        FROM runs_on_workflows ro
        JOIN workflow_runs wr ON ro.node_id_workflow = wr.node_id
        JOIN repositorios r ON wr.id_repo = r.id
        WHERE ro.runs_on LIKE ?
        GROUP BY r.name, r.html_url
        ORDER BY job_count DESC
        """
        
        cursor = conn.cursor()
        results = cursor.execute(query, (f"%{runner}%",)).fetchall()
        
        return [
            {
                "repo_name": row['repo_name'],
                "repo_url": row['html_url'],
                "job_count": row['job_count']
            }
            for row in results
        ]

@app.get("/api/matrix/runner-repo", tags=["Matrix"])
async def get_action_repo_matrix():
    """
    Get a matrix view of actions vs repositories
    Useful for creating heatmaps and coverage reports
    """
    with get_db() as conn:
        query = """
        SELECT 
            r.name as repo_name,
            uw.use as action,
            COUNT(*) as usage_count
        FROM repositorios r
        JOIN workflow_runs wr ON r.id = wr.id_repo
        JOIN uses_workflows uw ON wr.node_id = uw.node_id_workflow
        WHERE r.archived = 0 AND r.disabled = 0
        GROUP BY r.name, uw.use
        ORDER BY r.name, usage_count DESC
        """
        
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return {"matrix": {}, "repos": [], "actions": []}
        
        # Pivot to create matrix
        matrix = df.pivot_table(
            index='repo_name',
            columns='action',
            values='usage_count',
            fill_value=0
        )
        
        return {
            "matrix": matrix.to_dict(),
            "repos": matrix.index.tolist(),
            "actions": matrix.columns.tolist()
        }

@app.get("/api/coverage/action", tags=["Coverage"])
async def get_action_coverage(action: str = Query(..., description="Action name (e.g., actions/checkout)")):
    """
    Get coverage statistics for a specific action
    Shows adoption rate across the organization
    
    Example: /api/coverage/action?action=actions/checkout
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total active repos
        total_repos = cursor.execute(
            "SELECT COUNT(*) FROM repositorios WHERE archived = 0 AND disabled = 0"
        ).fetchone()[0]
        
        # Repos using this action
        using_query = """
        SELECT COUNT(DISTINCT r.id) as count
        FROM repositorios r
        JOIN workflow_runs wr ON r.id = wr.id_repo
        JOIN uses_workflows uw ON wr.node_id = uw.node_id_workflow
        WHERE uw.use LIKE ? AND r.archived = 0 AND r.disabled = 0
        """
        
        repos_using = cursor.execute(using_query, (f"%{action}%",)).fetchone()[0]
        
        coverage_percentage = (repos_using / total_repos * 100) if total_repos > 0 else 0
        
        return {
            "action": action,
            "total_repos": total_repos,
            "repos_using": repos_using,
            "repos_not_using": total_repos - repos_using,
            "coverage_percentage": round(coverage_percentage, 2),
            "adoption_level": "High" if coverage_percentage > 75 else "Medium" if coverage_percentage > 25 else "Low"
        }

# Manter o endpoint antigo para compatibilidade
@app.get("/api/coverage/action/{action_name:path}", tags=["Coverage"], deprecated=True)
async def get_action_coverage_legacy(action_name: str):
    """
    [DEPRECATED] Use /api/coverage/action?action=name instead
    Legacy endpoint for backward compatibility
    """
    return await get_action_coverage(action=action_name)

@app.get("/api/trends/adoption", tags=["Trends"])
async def get_adoption_trends():
    """
    Get adoption trends for top actions
    Useful for tracking standardization efforts
    """
    with get_db() as conn:
        # Get top 10 most used actions
        top_actions_query = """
        SELECT use as action, COUNT(*) as total_usage
        FROM uses_workflows
        GROUP BY use
        ORDER BY total_usage DESC
        LIMIT 10
        """
        
        cursor = conn.cursor()
        top_actions = cursor.execute(top_actions_query).fetchall()
        
        trends = []
        for action_row in top_actions:
            action = action_row['action']
            
            # Get coverage for each action
            coverage_data = await get_action_coverage(action)
            
            trends.append({
                "action": action,
                "total_usage": action_row['total_usage'],
                **coverage_data
            })
        
        return trends
def run():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
   run()