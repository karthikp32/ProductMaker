import click
import requests
import json
import sys

API_URL = "http://localhost:8000"

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

if __name__ == "__main__":
    cli()
