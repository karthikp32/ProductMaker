import click
import requests
import json
import sys

API_URL = "http://localhost:8083"

@click.group()
def cli():
    """ProductMaker CLI"""
    pass

@cli.command()
@click.argument("agent_name")
@click.argument("instruction")
@click.option("--context", default="{}", help="JSON context string")
def instruct(agent_name, instruction, context):
    """Instruct an agent to do something."""
    try:
        context_dict = json.loads(context)
    except json.JSONDecodeError:
        click.echo("Error: Context must be valid JSON.")
        sys.exit(1)

    url = f"{API_URL}/instruct/{agent_name}"
    try:
        response = requests.post(url, json={"instruction": instruction, "context": context_dict})
        response.raise_for_status()
        click.echo(f"Success: {response.json()}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: {e}")
        sys.exit(1)

@cli.command()
def list_agents():
    """List available agents."""
    url = f"{API_URL}/agents"
    try:
        response = requests.get(url)
        response.raise_for_status()
        click.echo(f"Agents: {', '.join(response.json()['agents'])}")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: {e}")
        sys.exit(1)

@cli.command()
def analyze_segment():
    """Prompt for segment analysis details and trigger the process."""
    segment_name = click.prompt("Enter the Customer Segment Name (e.g., Indie Game Developers)")
    industry = click.prompt("Enter the Industry (e.g., Gaming)", default="General")
    target_repo_path = click.prompt("Enter the Target Repo Path (e.g., ~/repos/crispr-tools)", default="")

    payload = {
        "segment_name": segment_name,
        "industry": industry,
        "target_repo_path": target_repo_path if target_repo_path else None
    }

    url = f"{API_URL}/analyze-segment"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        click.echo(f"Success: {response.json()}")
        click.echo("PM Agent is now working in the background. Check logs or output/ folder.")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: {e}")
        sys.exit(1)

@cli.command()
def analyze_industry():
    """Prompt for industry landscape analysis."""
    industry = click.prompt("Enter the Industry name (e.g., Sustainable Fashion, BioTech)")
    target_repo_path = click.prompt("Enter the Target Repo Path (e.g., ~/repos/crispr-tools)", default="")

    payload = {
        "industry": industry,
        "target_repo_path": target_repo_path if target_repo_path else None
    }

    url = f"{API_URL}/analyze-industry"
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        click.echo(f"Success: {response.json()}")
        click.echo("PM Agent is doing high-level research and prioritization. Check logs.")
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: {e}")
        sys.exit(1)

@cli.command()
@click.option('--prd_path', default="output/athletes/the_\"nil\"_era_athlete/prds/prd_athletecorp_os.md", help="Path to the PRD file.")
def architect_design(prd_path):
    """Test Architect Agent with a PRD."""
    try:
        with open(prd_path, "r") as f:
            prd_content = f.read()
            
        payload = {
            "instruction": "Design the system architecture based on the attached PRD.",
            "context": {
                "prd_content": prd_content,
                "project_name": "AthleteCorp_OS",
                "industry": "Athletes",
                "segment": "The \"NIL\" Era Athlete"
            }
        }
        
        url = f"{API_URL}/instruct/architect"
        response = requests.post(url, json=payload)
        response.raise_for_status()
        click.echo(f"Success: {response.json()}")
        click.echo("Architect Agent commissioned. Check: output/athletes/the_\"nil\"_era_athlete/design_docs/athletecorp_os/system_architecture.md")
        
    except FileNotFoundError:
        click.echo(f"Error: PRD file not found at {prd_path}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: API Request failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
