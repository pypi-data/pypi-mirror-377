"""CLI entry point for reprompt package."""

from __future__ import annotations

import csv
import io
import json
import logging
import os
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.json import JSON

from .client import RepromptClient
from .exceptions import RepromptAPIError

# Suppress INFO logs from httpx and other libraries to keep CLI output clean
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
# Set root logger to ERROR to suppress all INFO logs unless explicitly needed
logging.basicConfig(level=logging.ERROR)

# Removed CSV upload functionality - read-only client

# Create the main app and console
app = typer.Typer(
    help="Reprompt CLI - Place enrichment API client with autopagination",
    rich_markup_mode="rich",
    epilog="Visit https://docs.repromptai.com for more information.\\n\\n"
    "[bold]Autopagination:[/bold] List commands fetch ALL results by default. Use --limit to restrict output.",
)
console = Console()

# Create subcommands
jobs_app = typer.Typer(help="Manage individual place enrichment jobs", rich_markup_mode="rich")
batches_app = typer.Typer(help="Manage batches of place enrichment jobs", rich_markup_mode="rich")

app.add_typer(jobs_app, name="jobs")
app.add_typer(batches_app, name="batches")


def get_client(
    api_key: Optional[str] = None,
    org_slug: Optional[str] = None,
    base_url: str = "https://api.repromptai.com/v1",
    timeout: float = 30.0,
) -> RepromptClient:
    """Get configured RepromptClient with auth resolution."""
    # Resolve API key
    resolved_api_key = api_key or os.getenv("REPROMPT_API_KEY")
    if not resolved_api_key:
        console.print(
            "[red]Error: API key is required. Use --api-key or set REPROMPT_API_KEY environment variable.[/red]"
        )
        sys.exit(3)

    # Resolve org slug
    resolved_org_slug = org_slug or os.getenv("REPROMPT_ORG_SLUG")
    if not resolved_org_slug:
        console.print(
            "[red]Error: Organization slug is required. "
            "Use --org-slug or set REPROMPT_ORG_SLUG environment variable.[/red]"
        )
        sys.exit(3)

    try:
        return RepromptClient(
            api_key=resolved_api_key,
            org_slug=resolved_org_slug,
            base_url=base_url,
            timeout=timeout,
        )
    except RepromptAPIError as e:
        console.print(f"[red]API Error creating client: {e}[/red]")
        sys.exit(1)
    except (ValueError, KeyError) as e:
        console.print(f"[red]Configuration error: {e}[/red]")
        sys.exit(1)


def serialize_for_json(obj):
    """Custom serializer for JSON output that handles Pydantic models."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def flatten_dict(d, parent_key="", sep="."):
    """Flatten nested dictionary for CSV output."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # For lists of dicts, just convert to JSON string
            items.append((new_key, json.dumps(v)))
        elif isinstance(v, list):
            # For simple lists, join with semicolons
            items.append((new_key, ";".join(str(item) for item in v)))
        else:
            items.append((new_key, v))
    return dict(items)


def to_csv_string(data):
    """Convert data to CSV format."""
    if not data:
        return ""

    # Convert to list if single item
    if not isinstance(data, list):
        data = [data]

    # Convert each item to dict and flatten
    flattened_items = []
    for item in data:
        if hasattr(item, "model_dump"):
            item_dict = item.model_dump()
        elif isinstance(item, dict):
            item_dict = item
        else:
            item_dict = {"value": str(item)}

        flattened_items.append(flatten_dict(item_dict))

    if not flattened_items:
        return ""

    # Get all unique keys
    all_keys = set()
    for item in flattened_items:
        all_keys.update(item.keys())

    # Sort keys for consistent column order
    all_keys = sorted(all_keys)

    # Create CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=all_keys)
    writer.writeheader()
    for item in flattened_items:
        writer.writerow(item)

    return output.getvalue()


# Removed JSONL output format


def _output_json_lines(result):
    """Output result as JSON Lines format."""
    for item in result:
        if hasattr(item, "model_dump"):
            print(json.dumps(item.model_dump(), default=serialize_for_json))
        else:
            print(json.dumps(item, default=serialize_for_json))


def _output_json_array(result):
    """Output result as JSON array."""
    items = []
    for item in result:
        if hasattr(item, "model_dump"):
            items.append(item.model_dump())
        else:
            items.append(item)
    print(json.dumps(items, default=serialize_for_json))


def _output_json(result):
    """Output single result as JSON."""
    if hasattr(result, "model_dump"):
        print(json.dumps(result.model_dump(), default=serialize_for_json))
    else:
        print(json.dumps(result, default=serialize_for_json))


def _output_pretty(result, quiet):
    """Output result in pretty format."""
    if quiet:
        return
    if isinstance(result, dict):
        console.print(JSON(json.dumps(result, default=serialize_for_json, ensure_ascii=False)))
    elif hasattr(result, "model_dump"):
        console.print(JSON(result.model_dump_json()))
    else:
        console.print(result)


def output_result(result, output_format: str = "pretty", quiet: bool = False) -> None:
    """Output result in specified format (pretty, json, jsonl, or csv)."""
    if output_format == "csv":
        print(to_csv_string(result))
    elif output_format == "jsonl" and isinstance(result, list):
        _output_json_lines(result)
    elif output_format == "json":
        if isinstance(result, list):
            _output_json_array(result)
        else:
            _output_json(result)
    elif output_format == "jsonl":  # jsonl but not a list
        _output_json(result)
    else:  # pretty format
        _output_pretty(result, quiet)


def handle_api_error(e: RepromptAPIError) -> None:
    """Handle API errors with user-friendly messages."""
    if e.status_code == 401:
        console.print("[red]Error: Invalid API key or unauthorized access.[/red]")
        console.print("Check your API key and organization slug.")
    elif e.status_code == 403:
        console.print("[red]Error: Access forbidden.[/red]")
        console.print("You may not have permission to access this resource.")
    elif e.status_code == 404:
        console.print("[red]Error: Resource not found.[/red]")
    elif e.status_code == 429:
        console.print("[red]Error: Rate limit exceeded.[/red]")
        console.print("Please wait before making more requests.")
    else:
        console.print(f"[red]API Error ({e.status_code}): {str(e)}[/red]")

    sys.exit(2)


def execute_command_with_error_handling(func, *args, **kwargs):
    """Execute a command function with consistent error handling."""
    try:
        return func(*args, **kwargs)
    except RepromptAPIError as e:
        handle_api_error(e)
        return None  # handle_api_error calls sys.exit, but adding return for consistency
    except TypeError as e:
        if "unexpected keyword argument" in str(e):
            console.print("[red]CLI Error: Parameter mismatch with API method[/red]")
            console.print(f"[yellow]Details: {e}[/yellow]")
            console.print("[blue]This appears to be a CLI bug. Please report it.[/blue]")
        else:
            console.print(f"[red]Type Error: {e}[/red]")
        sys.exit(1)


# Removed deprecated JSON flag handling


# BATCH COMMANDS


@batches_app.command("list")
def list_batches(
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit number of results"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Query to filter batch names"),
    output: str = typer.Option("pretty", "--output", "-o", help="Output format: pretty, csv"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="REPROMPT_API_KEY", help="API key"),
    org_slug: Optional[str] = typer.Option(None, "--org-slug", envvar="REPROMPT_ORG_SLUG", help="Organization slug"),
):
    """List all batches with optional search and pagination."""

    def _list_batches_impl():
        output_format = output
        client = get_client(api_key=api_key, org_slug=org_slug)

        # Use the iterator directly with slicing
        iterator = client.batches.list_batches(query=query)
        batches = list(iterator) if limit is None else iterator[:limit]

        if not quiet:
            if query:
                console.print(f"Found {len(batches)} batches matching '{query}'")
            else:
                console.print(f"Found {len(batches)} batches")

        output_result(batches, output_format, quiet)

    execute_command_with_error_handling(_list_batches_impl)


@batches_app.command("get")
def get_batch(
    batch_id: str = typer.Argument(..., help="Batch ID to retrieve"),
    output: str = typer.Option("pretty", "--output", "-o", help="Output format: pretty, csv"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="REPROMPT_API_KEY", help="API key"),
    org_slug: Optional[str] = typer.Option(None, "--org-slug", envvar="REPROMPT_ORG_SLUG", help="Organization slug"),
):
    """Get details for a specific batch."""

    def _get_batch_impl():
        output_format = output
        client = get_client(api_key=api_key, org_slug=org_slug)
        batch = client.batches.get_batch(batch_id)

        if not quiet:
            batch_id_str = batch.get("batch_id") or batch.get("id") or batch_id
            console.print(f"Retrieved batch: {batch_id_str}")

        output_result(batch, output_format, quiet)

    execute_command_with_error_handling(_get_batch_impl)


# Removed delete_batch command - read-only client


# Removed upload_csv command - read-only client


# JOB COMMANDS


@jobs_app.command("list")
def list_jobs(
    batch_id: Optional[str] = typer.Option(None, "--batch-id", "-b", help="Filter by batch ID"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Limit number of results"),
    output: str = typer.Option("pretty", "--output", "-o", help="Output format: pretty, csv"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="REPROMPT_API_KEY", help="API key"),
    org_slug: Optional[str] = typer.Option(None, "--org-slug", envvar="REPROMPT_ORG_SLUG", help="Organization slug"),
):
    """List jobs with optional batch filtering and pagination."""

    def _list_jobs_impl():
        output_format = output
        client = get_client(api_key=api_key, org_slug=org_slug)

        if not batch_id:
            console.print("[red]Error: batch_id is required for listing jobs[/red]")
            raise typer.Exit(1)
        # Use the iterator directly with slicing
        iterator = client.jobs.get_jobs_by_batch_id(batch_id=batch_id)
        jobs = list(iterator) if limit is None else iterator[:limit]

        if not quiet:
            if batch_id:
                console.print(f"Found {len(jobs)} jobs in batch {batch_id}")
            else:
                console.print(f"Found {len(jobs)} jobs")

        output_result(jobs, output_format, quiet)

    execute_command_with_error_handling(_list_jobs_impl)


@jobs_app.command("get")
def get_job(
    place_id: str = typer.Argument(..., help="Place ID to retrieve"),
    output: str = typer.Option("pretty", "--output", "-o", help="Output format: pretty, csv"),
    quiet: bool = typer.Option(False, "--quiet", help="Minimal output"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="REPROMPT_API_KEY", help="API key"),
    org_slug: Optional[str] = typer.Option(None, "--org-slug", envvar="REPROMPT_ORG_SLUG", help="Organization slug"),
):
    """Get details for a specific job by place ID."""

    def _get_job_impl():
        output_format = output
        client = get_client(api_key=api_key, org_slug=org_slug)
        job = client.jobs.get_job(place_id)

        if not quiet:
            console.print(f"Retrieved job for place: {place_id}")

        output_result(job, output_format, quiet)

    execute_command_with_error_handling(_get_job_impl)


# Removed delete_job command - read-only client


if __name__ == "__main__":
    app()
