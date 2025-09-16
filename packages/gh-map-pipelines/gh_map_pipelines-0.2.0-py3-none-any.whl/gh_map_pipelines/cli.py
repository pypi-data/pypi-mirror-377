import typer, time
from rich.console import Console
from gh_map_pipelines.github_api import GitHub


app = typer.Typer(help="GitHub")
console = Console()

@app.command()
def process(org: str = typer.Option(help="Org GitHub to process data.")):
    gh = GitHub(org=org)
    all_repos = gh.list_all_repos_org(write_db=True)
    for repo in all_repos:
        gh.list_actions_runs(repo=repo.get('name'), id_repo=repo.get('id'), write_db=True)
        console.print("Waiting 5 seconds...")
        time.sleep(5)
    gh.populate_uses_actions()


if __name__ == "__main__":
    app()