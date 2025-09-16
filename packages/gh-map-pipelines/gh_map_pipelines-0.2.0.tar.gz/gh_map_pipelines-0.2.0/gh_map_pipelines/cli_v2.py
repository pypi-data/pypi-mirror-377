import typer
from rich.console import Console
from gh_map_pipelines.github_api_v2 import GitHub
from typing import Optional
from enum import Enum

app = typer.Typer(help="GitHub Actions Pipeline Mapper")
console = Console()

class ProcessMode(str, Enum):
    full = "full"
    resume = "resume"
    uses_only = "uses-only"
    status = "status"

@app.command()
def process(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization to process"),
    mode: ProcessMode = typer.Option(ProcessMode.full, "--mode", "-m", help="Processing mode"),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Batch size for saving data"),
    rate_limit_wait: int = typer.Option(60, "--wait", "-w", help="Seconds to wait after rate limit")
):
    """
    Process GitHub organization workflows and extract uses.
    
    Modes:
    - full: Complete processing from scratch
    - resume: Resume from last checkpoint
    - uses-only: Only process uses (assumes repos and workflows are already fetched)
    - status: Show current processing status
    """
    
    gh = GitHub(org=org)
    gh.rate_limit_wait_time = rate_limit_wait
    
    if mode == ProcessMode.status:
        gh.get_status_report()
        return
    
    if mode == ProcessMode.uses_only:
        console.print("[blue bold][*] [white]Processing only uses from existing workflows...")
        gh.populate_uses_actions(resume=True, batch_size=batch_size)
        gh.get_status_report()
        return
    
    resume = mode == ProcessMode.resume
    
    # Process repositories
    console.print(f"[blue bold][*] [white]Starting repository collection for org: {org}")
    all_repos = gh.list_all_repos_org(write_db=True, resume=resume)
    
    if not all_repos:
        console.print("[red bold][-] [white]No repositories found or error occurred")
        return
    
    console.print(f"[green bold][+] [white]Found {len(all_repos)} repositories")
    
    # Process workflows for each repository
    console.print("[blue bold][*] [white]Collecting workflows from repositories...")
    for repo in all_repos:
        gh.list_actions_runs(
            repo=repo.get('name'), 
            id_repo=repo.get('id'), 
            write_db=True
        )
    
    # Process uses from workflows
    console.print("[blue bold][*] [white]Extracting uses from workflow files...")
    gh.populate_uses_actions(resume=True, batch_size=batch_size)
    
    # Show final status
    gh.get_status_report()

@app.command()
def resume(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization to process"),
    batch_size: int = typer.Option(10, "--batch-size", "-b", help="Batch size for saving data")
):
    """
    Resume processing from last checkpoint.
    Shortcut for: process --mode resume
    """
    process(org=org, mode=ProcessMode.resume, batch_size=batch_size)

@app.command()
def status(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization")
):
    """
    Show current processing status.
    """
    gh = GitHub(org=org)
    gh.get_status_report()

@app.command()
def reset(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization"),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm reset action")
):
    """
    Reset processing status (keeps data but allows reprocessing).
    """
    if not confirm:
        console.print("[yellow bold][!] [white]This will reset processing status. Use --confirm to proceed.")
        return
    
    gh = GitHub(org=org)
    cursor = gh.conn.cursor()
    
    # Reset workflow status
    cursor.execute("DELETE FROM workflow_status")
    cursor.execute("DELETE FROM processing_status")
    cursor.execute("DELETE FROM rate_limit_log")
    gh.conn.commit()
    
    console.print("[green bold][✓] [white]Processing status reset. Data preserved.")

@app.command()
def clean(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization"),
    confirm: bool = typer.Option(False, "--confirm", help="Confirm clean action"),
    keep_repos: bool = typer.Option(False, "--keep-repos", help="Keep repository data")
):
    """
    Clean all data and start fresh.
    WARNING: This will delete all collected data!
    """
    if not confirm:
        console.print("[red bold][!] [white]This will DELETE all data! Use --confirm to proceed.")
        return
    
    gh = GitHub(org=org)
    cursor = gh.conn.cursor()
    
    # Clean tables
    if not keep_repos:
        cursor.execute("DELETE FROM repositorios")
        console.print("[yellow bold][*] [white]Repositories cleaned")
    
    cursor.execute("DELETE FROM workflow_runs")
    cursor.execute("DELETE FROM uses_workflows")
    cursor.execute("DELETE FROM workflow_status")
    cursor.execute("DELETE FROM processing_status")
    cursor.execute("DELETE FROM rate_limit_log")
    gh.conn.commit()
    
    # Clean parquet files
    import os
    files_to_clean = ["workflow_runs.parquet", "uses_workflows.parquet"]
    if not keep_repos:
        files_to_clean.append("repos.parquet")
    
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            console.print(f"[yellow bold][*] [white]Removed {file}")
    
    console.print("[green bold][✓] [white]All data cleaned successfully")

@app.command()
def verify_token(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization to verify access")
):
    """
    Verify GitHub token and permissions for the organization.
    """
    console.print("[bold cyan]🔐 GitHub Token Verification[/bold cyan]\n")
    
    # This will automatically validate the token during initialization
    try:
        gh = GitHub(org=org)
        console.print("\n[green bold]✅ Token is valid and has access to the organization![/green bold]")
        console.print("\nYou can proceed with:")
        console.print(f"  gh_map process --org {org}")
    except SystemExit:
        # Token validation failed, error already displayed
        pass
    except Exception as e:
        console.print(f"[red bold][-] [white]Unexpected error: {e}")
        raise typer.Exit(1)

@app.command()
def export(
    org: str = typer.Option(..., "--org", "-o", help="GitHub organization"),
    format: str = typer.Option("json", "--format", "-f", help="Export format: json, csv"),
    output: Optional[str] = typer.Option(None, "--output", "-O", help="Output file path")
):
    """
    Export collected data to different formats.
    """
    import pandas as pd
    import json
    
    gh = GitHub(org=org)
    
    # Get all data
    repos_df = pd.read_sql("SELECT * FROM repositorios", con=gh.conn)
    workflows_df = pd.read_sql("SELECT * FROM workflow_runs", con=gh.conn)
    uses_df = pd.read_sql("SELECT * FROM uses_workflows", con=gh.conn)
    
    if format == "json":
        data = {
            "organization": org,
            "repositories": repos_df.to_dict(orient="records"),
            "workflows": workflows_df.to_dict(orient="records"),
            "uses": uses_df.to_dict(orient="records")
        }
        
        if output:
            with open(output, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            console.print(f"[green bold][✓] [white]Data exported to {output}")
        else:
            console.print(json.dumps(data, indent=2, default=str))
    
    elif format == "csv":
        base_name = output.replace('.csv', '') if output else f"{org}_export"
        
        repos_df.to_csv(f"{base_name}_repos.csv", index=False)
        workflows_df.to_csv(f"{base_name}_workflows.csv", index=False)
        uses_df.to_csv(f"{base_name}_uses.csv", index=False)
        
        console.print(f"[green bold][✓] [white]Data exported to {base_name}_*.csv files")
    
    else:
        console.print(f"[red bold][-] [white]Unsupported format: {format}")

if __name__ == "__main__":
    app()
