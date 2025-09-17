#!/usr/bin/env python3
import click
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path
import subprocess
import os
import stat
import logging
from contextchain.engine.validator import validate_schema
from contextchain.engine.executor import execute_pipeline, execute_single_task
from contextchain.registry.version_manager import push_schema, list_versions, rollback_version, VersionManager
from contextchain.registry.schema_loader import load_schema
from contextchain.db.mongo_client import get_mongo_client
from contextchain.db.collections import setup_collections
from contextchain.db.vector_db_client import ChromaClient
from contextchain.local_llm_client import OllamaClient
from contextchain.data_processing import chunk_text, summarize_text
from contextchain.dag_builder import build_dag
from contextchain.evaluation import evaluate_results
from contextchain.task_registry import register_task
import networkx as nx
import chromadb
import sentence_transformers
from dotenv import load_dotenv
import time
import shutil
import requests
import jsonschema  # Added for JSON schema validation

# CLI Version
VERSION = "1.1.3"

# Load environment variables from .env file
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load colorama for better color support
try:
    import colorama
    colorama.init()
except ImportError:
    pass

def show_banner():
    """Display the CLI banner with ASCII art and colors."""
    ascii_art = r"""
 ██████╗ ██████╗ ███╗   ██╗████████╗███████╗██╗  ██╗████████╗
██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔════╝╚██╗██╔╝╚══██╔══╝
██║     ██║   ██║██╔██╗ ██║   ██║   █████╗   ╚███╔╝    ██║   
██║     ██║   ██║██║╚██╗██║   ██║   ██╔══╝   ██╔██╗    ██║   
╚██████╗╚██████╔╝██║ ╚████║   ██║   ███████╗██╔╝ ██╗   ██║   
 ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   
                                                              
 ██████╗██╗  ██╗ █████╗ ██╗███╗   ██╗
██╔════╝██║  ██║██╔══██╗██║████╗  ██║
██║     ███████║███████║██║██╔██╗ ██║
██║     ██╔══██║██╔══██║██║██║╚██╗██║
╚██████╗██║  ██║██║  ██║██║██║ ╚████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
    """
    click.secho("=" * 60, fg="bright_blue", bold=True)
    click.secho(ascii_art, fg="bright_blue", bold=True)
    click.secho(f"         ContextChain v{VERSION} CLI", fg="bright_cyan", bold=True)
    click.secho("         Orchestrate AI and Full-Stack Workflows", fg="bright_cyan", bold=True)
    click.secho(f"                        v{VERSION}", fg="bright_white", bold=True)
    click.secho("=" * 60, fg="bright_blue", bold=True)

def update_current_schema(client, db_name, pipeline_id, schema_dir):
    """Update the current_schema.json with the latest schema in the schema file's directory."""
    schema = load_schema(client, db_name, pipeline_id)
    if schema:
        current_schema_path = schema_dir / "current_schema.json"
        meta = {
            "_meta": {
                "pipeline_id": pipeline_id,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "schema": schema
        }
        try:
            with current_schema_path.open("w") as f:
                json.dump(meta, f, indent=2)
            current_schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            click.secho(f"✓ Updated current_schema.json for {pipeline_id}", fg="bright_green", bold=True)
        except PermissionError:
            click.secho(f"✗ Failed to update current_schema.json for {pipeline_id} due to permissions. Run 'chmod u+w {current_schema_path}' manually.", fg="red", bold=True)
    else:
        click.secho(f"✗ No schema found for {pipeline_id}", fg="red", bold=True)

def copy_schema_file(pipeline_id, old_version, new_version, schema_dir):
    """Create a backup copy of the schema file with a timestamp suffix."""
    source_path = schema_dir / f"{pipeline_id}.json"
    if source_path.exists():
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = source_path.with_name(f"{pipeline_id}.{timestamp}.json")
        try:
            shutil.copy2(source_path, backup_path)
            backup_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            click.secho(f"✓ Created backup schema: {backup_path} (version: {new_version})", fg="bright_green", bold=True)
        except Exception as e:
            click.secho(f"✗ Failed to create backup for {source_path}: {e}", fg="red", bold=True)
    else:
        click.secho(f"✗ Source file {source_path} not found for backup.", fg="red", bold=True)

def load_main_schema(main_schema_path):
    """Load main schema and auto-discover sub-schemas if sub-schemas directory exists."""
    try:
        with open(main_schema_path, 'r') as f:
            schema = json.load(f)
        sub_schemas_dir = Path(main_schema_path).parent / "sub-schemas"
        sub_schemas = []
        if sub_schemas_dir.exists():
            for file in sub_schemas_dir.glob("*.json"):
                try:
                    with file.open("r") as f:
                        sub_schema = json.load(f)
                        if sub_schema.get("metadata", {}).get("parent_pipeline_id") == schema["pipeline_id"]:
                            sub_schemas.append(str(file))
                except json.JSONDecodeError:
                    click.secho(f"✗ Invalid JSON in sub-schema file: {file}", fg="red", bold=True)
        schema["metadata"]["sub_schemas"] = sub_schemas
        return schema
    except json.JSONDecodeError:
        raise click.ClickException(f"Invalid JSON in main schema: {main_schema_path}")
    except Exception as e:
        raise click.ClickException(f"Error loading main schema {main_schema_path}: {str(e)}")

class ColoredGroup(click.Group):
    """Custom Click Group that shows banner and colored help."""
    def format_help(self, ctx, formatter):
        show_banner()
        click.secho("\nUsage: contextchain [OPTIONS] COMMAND [ARGS]...", fg="bright_white", bold=True)
        click.secho(f"\nContextChain v{VERSION} CLI", fg="bright_cyan")

        click.secho("\nOptions:", fg="bright_yellow", bold=True)
        click.secho("  -h, --help      Show this help message and exit.", fg="bright_cyan")

        click.secho("\nCommands (grouped by category):", fg="bright_yellow", bold=True)

        click.secho("\n  Initialization:", fg="bright_green", bold=True)
        click.secho("    init          Initialize a new main pipeline with a JSON schema and MongoDB setup.", fg="bright_cyan")
        click.secho("    sub-init      Initialize a sub-schema inheriting from main schema.", fg="bright_cyan")
        click.secho("    new-version   Create a new schema version (local copy only).", fg="bright_cyan")

        click.secho("\n  Schema Management:", fg="bright_green", bold=True)
        click.secho("    schema-compile  Validate a schema file.", fg="bright_cyan")
        click.secho("    schema-push     Push a schema to MongoDB.", fg="bright_cyan")
        click.secho("    schema-pull     Pull a schema from MongoDB.", fg="bright_cyan")
        click.secho("    schema-current  Display the current schema.", fg="bright_cyan")
        click.secho("    version-list    List schema versions for a pipeline.", fg="bright_cyan")
        click.secho("    version-rollback  Rollback to a previous schema version.", fg="bright_cyan")

        click.secho("\n  Execution:", fg="bright_green", bold=True)
        click.secho("    run            Run an entire pipeline.", fg="bright_cyan")
        click.secho("    run-task       Run a single task for development.", fg="bright_cyan")

        click.secho("\n  Collaboration:", fg="bright_green", bold=True)
        click.secho("    ccshare-init    Initialize a .ccshare file for collaborative MongoDB Atlas access.", fg="bright_cyan")
        click.secho("    ccshare-join    Join an existing .ccshare collaboration.", fg="bright_cyan")
        click.secho("    ccshare-status  Check the status of the .ccshare configuration.", fg="bright_cyan")

        click.secho("\n  Utilities:", fg="bright_green", bold=True)
        click.secho("    list-pipelines  List all pipelines in MongoDB.", fg="bright_cyan")
        click.secho("    logs            Display logs for a pipeline.", fg="bright_cyan")
        click.secho("    results         Display results for a specific task.", fg="bright_cyan")

        click.secho("\n  Vector DB Commands:", fg="bright_green", bold=True)
        click.secho("    vector         Vector DB operations (init, search, etc.).", fg="bright_cyan")

        click.secho("\n  LLM Commands:", fg="bright_green", bold=True)
        click.secho("    llm            Local LLM operations (setup, etc.).", fg="bright_cyan")

        click.secho("\n  Metrics and Evaluation:", fg="bright_green", bold=True)
        click.secho("    metrics        Display metrics for a pipeline.", fg="bright_cyan")
        click.secho("    evaluate       Evaluate results for a task.", fg="bright_cyan")

        click.secho("\n  Plugins:", fg="bright_green", bold=True)
        click.secho("    plugin         Manage plugins (register, etc.).", fg="bright_cyan")

        click.secho("\nNotes:", fg="bright_yellow", bold=True)
        click.secho("  - Use 'contextchain COMMAND --help' for detailed options of each command.", fg="bright_cyan")

def configure_task(i, interactive, allowed_task_types, tasks):
    """Configure a single task interactively or with defaults."""
    click.secho(f"\nConfiguring Task {i+1}...", fg="bright_yellow", bold=True)
    if interactive:
        task_type = click.prompt(
            click.style(f"Task {i+1} type", fg="bright_blue"),
            default="LOCAL",
            type=click.Choice(allowed_task_types),
            show_choices=True
        )
    else:
        task_type = "LOCAL"
    
    task = {
        "task_id": i + 1,
        "description": click.prompt(click.style(f"Task {i+1} description", fg="bright_blue"), default=f"Task {i+1}") if interactive else f"Task {i+1}",
        "task_type": task_type,
        "endpoint": click.prompt(click.style(f"Task {i+1} endpoint", fg="bright_blue"), default="contextchain.utils.default_task") if interactive else "contextchain.utils.default_task",
        "inputs": [],
        "input_source": None,
        "wait_for_input": False,
        "output_collection": "task_results",
        "prompt_template": None,
        "parameters": {},
        "cron": None,
        "rerun": None
    }
    
    if task_type in ["LLM", "LLM_GENERATE"] and interactive:
        use_endpoint = click.confirm(click.style(f"Use a custom endpoint for Task {i+1} LLM (otherwise use global config)?", fg="bright_blue"), default=False)
        if use_endpoint:
            task["endpoint"] = click.prompt(click.style(f"Task {i+1} LLM endpoint (e.g., services.custom_llm.generate_summary)", fg="bright_blue"), default=task["endpoint"])
        else:
            task["prompt_template"] = click.prompt(click.style(f"Task {i+1} LLM prompt", fg="bright_blue"), default="")
            output_format = click.prompt(
                click.style(f"Task {i+1} output format", fg="bright_blue"),
                default="text",
                type=click.Choice(["text", "json"]),
                show_choices=True
            )
            task["parameters"]["output_format"] = output_format
            if output_format == "json":
                json_schema = click.prompt(
                    click.style(f"Task {i+1} JSON schema (optional, YAML format)", fg="bright_blue"),
                    default="{}"
                )
                try:
                    task["parameters"]["json_schema"] = yaml.safe_load(json_schema)
                except yaml.YAMLError:
                    click.secho("✗ Invalid JSON schema YAML, using empty schema", fg="red")
                    task["parameters"]["json_schema"] = {}
    
    elif task_type in ["GET", "POST", "PUT"] and interactive:
        if click.confirm(click.style(f"Add input source or inputs for task {i+1}?", fg="bright_blue"), default=False):
            if click.confirm(click.style(f"Use an input source (e.g., URL, DB string)?", fg="bright_blue"), default=False):
                task["input_source"] = click.prompt(click.style(f"Task {i+1} input source", fg="bright_blue"), default="")
            if click.confirm(click.style(f"Add inputs from other tasks?", fg="bright_blue"), default=False):
                input_ids = click.prompt(click.style(f"Task {i+1} input task IDs (comma-separated)", fg="bright_blue"), default="")
                task["inputs"] = [int(x.strip()) for x in input_ids.split(",") if x.strip()]
    
    elif task_type == "LOCAL" and interactive:
        if click.confirm(click.style(f"Use trigger_logs for task {i+1}?", fg="bright_blue"), default=False):
            task["output_collection"] = "trigger_logs"
        if click.confirm(click.style(f"Add granularity for task {i+1}?", fg="bright_blue"), default=False):
            task["parameters"]["granularity"] = click.prompt(click.style(f"Task {i+1} granularity (e.g., monthly, quarterly)", fg="bright_blue"), default="monthly")
    
    elif task_type in ["VECTOR_STORE_ADD", "VECTOR_STORE_SEARCH"] and interactive:
        task["parameters"]["collection_name"] = click.prompt(click.style(f"Task {i+1} vector DB collection name", fg="bright_blue"), default="default_collection")
        if task_type == "VECTOR_STORE_SEARCH":
            task["parameters"]["query"] = click.prompt(click.style(f"Task {i+1} search query", fg="bright_blue"), default="")
    
    elif task_type == "CHUNK_TEXT" and interactive:
        task["parameters"]["max_length"] = click.prompt(click.style(f"Task {i+1} max chunk length", fg="bright_blue"), type=int, default=512)
    
    elif task_type == "EVALUATE" and interactive:
        metrics = click.prompt(click.style(f"Task {i+1} metrics (comma-separated, e.g., mae,rmse)", fg="bright_blue"), default="")
        task["parameters"]["metrics"] = [m.strip() for m in metrics.split(",") if m.strip()]
    
    elif task_type == "CUSTOM_ALERT" and interactive:
        task["parameters"]["recipients"] = click.prompt(click.style(f"Task {i+1} alert recipients (comma-separated emails)", fg="bright_blue"), default="")
    
    if interactive and click.confirm(click.style(f"Add custom parameters for task {i+1}?", fg="bright_blue"), default=False):
        params_str = click.prompt(click.style(f"Task {i+1} parameters (YAML)", fg="bright_blue"), default="{}")
        try:
            params = yaml.safe_load(params_str)
            task["parameters"].update(params or {})
        except yaml.YAMLError:
            click.secho("✗ Invalid YAML, using empty parameters", fg="red")
            task["parameters"] = {}
    
    if interactive and click.confirm(click.style(f"Add cron schedule for task {i+1}?", fg="bright_blue"), default=False):
        task["cron"] = click.prompt(click.style(f"Task {i+1} cron schedule", fg="bright_blue"), default="")
    
    if interactive and click.confirm(click.style(f"Enable rerun for task {i+1} to overwrite existing results?", fg="bright_blue"), default=False):
        task["rerun"] = True
        click.secho("✓ Rerun enabled for task. Existing results will be overwritten with previous data preserved.", fg="bright_green")
    else:
        task["rerun"] = None

    tasks.append(task)
    return tasks

@click.group(cls=ColoredGroup, context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """ContextChain CLI."""
    pass

@cli.command()
@click.option('--file', type=click.Path(), default="schemas/Production.json", help='Output path for main schema (e.g., schemas/Production.json)')
@click.option('--interactive/--no-interactive', default=True, help='Enable interactive prompts')
@click.option('--backend-host', default="http://127.0.0.1:8000", help='Backend host URL')
@click.option('--frontend-host', default="http://127.0.0.1:3636", help='Frontend host URL')
def init(file, interactive, backend_host, frontend_host):
    """Initialize a new main pipeline with a JSON schema, MongoDB, and ChromaDB setup."""
    mongod_process = None
    show_banner()
    click.secho("\nInitializing Main Pipeline...", fg="bright_yellow", bold=True)

    # Validate file path
    schema_path = Path(file)
    if schema_path.is_dir():
        click.secho(f"✗ Schema path is a directory: {schema_path}. Please specify a .json file.", fg="red", bold=True)
        return
    if schema_path.suffix != '.json':
        click.secho(f"✗ Schema path must be a .json file: {schema_path}", fg="red", bold=True)
        return

    # Create schemas directory
    schema_dir = schema_path.parent
    try:
        schema_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(schema_dir, 0o755)
    except Exception as e:
        click.secho(f"✗ Failed to create schema directory {schema_dir}: {e}", fg="red", bold=True)
        return

    # Prompt for sub-schemas directory
    sub_schemas_dir = schema_dir / "sub-schemas"
    create_sub_schemas = interactive and click.confirm(click.style("Create a sub-schemas directory?", fg="bright_blue"), default=False)
    if create_sub_schemas:
        try:
            sub_schemas_dir.mkdir(parents=True, exist_ok=True)
            os.chmod(sub_schemas_dir, 0o755)
            click.secho(f"✓ Sub-schemas directory created: {sub_schemas_dir}", fg="bright_green", bold=True)
        except Exception as e:
            click.secho(f"✗ Failed to create sub-schemas directory {sub_schemas_dir}: {e}", fg="red", bold=True)
            return

    pipeline_id = click.prompt(click.style("Pipeline ID", fg="bright_blue"), default="Production") if interactive else "Production"
    description = click.prompt(click.style("Description", fg="bright_blue"), default="Main orchestrator pipeline") if interactive else "Main orchestrator pipeline"
    created_by = click.prompt(click.style("Creator name", fg="bright_blue"), default="user") if interactive else "user"

    if interactive and click.confirm(click.style("Add optional metadata? (tags, pipeline type)", fg="bright_blue"), default=False):
        tags_input = click.prompt(click.style("Tags (comma-separated)", fg="bright_blue"), default="")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        pipeline_type = click.prompt(click.style("Pipeline type", fg="bright_blue"), default="ai-orchestration")
    else:
        tags = []
        pipeline_type = "ai-orchestration"

    config = {}
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        mode = click.prompt(click.style(f"MongoDB mode (1: Default (local), 2: .ccshare) (attempt {attempt}/{max_attempts})", fg="bright_blue"), 
                           type=click.Choice(["1", "2"]), default="1") if interactive else "1"
        
        config["db_name"] = click.prompt(click.style("MongoDB database name", fg="bright_blue"), default="blacklane-retail") if interactive else "blacklane-retail"
        
        if mode == "2":
            ccshare_path = click.prompt(click.style("Path to .ccshare file", fg="bright_blue"), default="config/team.ccshare")
            try:
                with open(ccshare_path, 'r') as f:
                    ccshare = yaml.safe_load(f)
                if not ccshare or "uri" not in ccshare:
                    click.secho(f"✗ Invalid or missing 'uri' in {ccshare_path}.", fg="red", bold=True)
                    if attempt == max_attempts:
                        return
                    continue
                config["uri"] = ccshare["uri"]
                config["ccshare_path"] = ccshare_path
            except FileNotFoundError:
                click.secho(f"✗ File not found: {ccshare_path}", fg="red", bold=True)
                if attempt == max_attempts:
                    return
                continue
            except yaml.YAMLError as e:
                click.secho(f"✗ Invalid YAML in {ccshare_path}: {e}", fg="red", bold=True)
                if attempt == max_attempts:
                    return
                continue
        else:
            config["uri"] = os.getenv("MONGO_URI", "mongodb://localhost:27017")

        # ChromaDB configuration
        config["chroma_path"] = click.prompt(click.style("ChromaDB storage path", fg="bright_blue"), default="./blacklane-optim") if interactive else "./blacklane-optim"
        try:
            os.makedirs(config["chroma_path"], exist_ok=True)
            os.chmod(config["chroma_path"], 0o755)
            ChromaClient(config["chroma_path"]).heartbeat()
            click.secho(f"✓ Initialized ChromaDB at {config['chroma_path']}", fg="bright_green", bold=True)
        except PermissionError:
            click.secho(f"✗ Permission denied for ChromaDB path: {config['chroma_path']}. Run 'chmod -R u+w {config['chroma_path']}'", fg="red", bold=True)
            if attempt == max_attempts:
                return
            attempt += 1
            continue
        except Exception as e:
            click.secho(f"✗ Failed to initialize ChromaDB: {e}. Ensure chromadb is installed and path is valid.", fg="red", bold=True)
            if attempt == max_attempts:
                return
            attempt += 1
            continue

        config_path = Path("config/default_config.yaml")
        config_path.parent.mkdir(exist_ok=True)
        with config_path.open("w") as f:
            yaml.safe_dump(config, f)
        os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        
        click.secho("Setting up MongoDB connection...", fg="bright_yellow")
        try:
            client = get_mongo_client(config["uri"], db_name=config["db_name"])
            setup_collections(client, config["db_name"])
            click.secho("✓ MongoDB setup completed.", fg="bright_green", bold=True)
            break
        except Exception as e:
            click.secho(f"✗ Failed to connect to MongoDB at {config['uri']}: {str(e)}", fg="red", bold=True)
            if attempt == max_attempts:
                click.secho("✗ Max retry attempts reached. Please ensure MongoDB is installed and running.", fg="red", bold=True)
                return
            attempt += 1
            if "mongodb://localhost" in config["uri"]:
                click.secho("Attempting to start local MongoDB...", fg="bright_yellow")
                try:
                    data_dir = Path("/data/db")
                    data_dir.mkdir(parents=True, exist_ok=True)
                    os.chmod(data_dir, 0o755)
                    mongod_process = subprocess.Popen(["mongod", "--dbpath", str(data_dir)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    time.sleep(3)
                    client = get_mongo_client(config["uri"], db_name=config["db_name"])
                    setup_collections(client, config["db_name"])
                    click.secho("✓ Local MongoDB instance started and setup completed.", fg="bright_green", bold=True)
                    break
                except Exception as local_e:
                    click.secho(f"✗ Failed to start local MongoDB: {str(local_e)}", fg="red", bold=True)
                    if mongod_process and mongod_process.poll() is None:
                        mongod_process.terminate()
                        try:
                            mongod_process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            mongod_process.kill()
                    continue

    if mongod_process and mongod_process.poll() is None and "mongodb://localhost:27017" not in config["uri"]:
        mongod_process.terminate()
        try:
            mongod_process.wait(timeout=5)
            click.secho("✓ Local MongoDB instance terminated.", fg="bright_green", bold=True)
        except subprocess.TimeoutExpired:
            mongod_process.kill()
            click.secho("✓ Local MongoDB instance forcefully terminated.", fg="bright_green", bold=True)

    tasks = []
    allowed_task_types = ["GET", "POST", "PUT", "LLM", "LLM_GENERATE", "LOCAL", "VECTOR_STORE_ADD", "VECTOR_STORE_SEARCH", "CHUNK_TEXT", "EVALUATE", "CUSTOM_ALERT"]
    if interactive:
        config_method = click.prompt(
            click.style("Configure tasks via (1: CLI, 2: Manual JSON Edit)", fg="bright_blue"),
            type=click.Choice(["1", "2"]),
            default="1"
        )
        if config_method == "1":
            while True:
                tasks = configure_task(len(tasks), interactive, allowed_task_types, tasks)
                if not click.confirm(click.style("Add another task?", fg="bright_blue"), default=False):
                    break
        else:
            json_path = click.prompt(click.style("Path to JSON file for schema", fg="bright_blue"), default=str(schema_path))
            json_path = Path(json_path)
            if json_path.is_dir():
                click.secho(f"✗ Provided path is a directory: {json_path}. Please specify a .json file.", fg="red", bold=True)
                return
            json_path.parent.mkdir(parents=True, exist_ok=True)
            if not json_path.exists():
                default_tasks = [{"task_id": 1, "description": "Default Task", "task_type": "LOCAL", "endpoint": "contextchain.utils.default_task", "rerun": None}]
                with json_path.open("w") as f:
                    json.dump({"tasks": default_tasks}, f, indent=2)
                click.secho(f"✓ Created default schema file: {json_path}", fg="bright_green", bold=True)
            try:
                with json_path.open("r") as f:
                    tasks_data = json.load(f)
                tasks = tasks_data.get("tasks", [])
            except json.JSONDecodeError:
                click.secho(f"✗ Invalid JSON format in {json_path}", fg="red", bold=True)
                return
    else:
        tasks = [configure_task(0, interactive, allowed_task_types, [])[0]]

    llm_config = {}
    if any(task["task_type"] in ["LLM", "LLM_GENERATE"] for task in tasks) and interactive:
        if click.confirm(click.style("Configure LLM settings for this pipeline?", fg="bright_blue"), default=True):
            llm_config["provider"] = click.prompt(click.style("LLM provider (e.g., ollama)", fg="bright_blue"), default="ollama")
            llm_config["model"] = click.prompt(click.style("LLM model (e.g., mistral:7b)", fg="bright_blue"), default="mistral:7b")
            llm_config["url"] = click.prompt(click.style("LLM API URL (optional)", fg="bright_blue"), default="http://localhost:11434")
            llm_config["api_key_env"] = click.prompt(click.style("Environment variable for API key", fg="bright_blue"), default="")
            llm_config["api_key"] = click.prompt(click.style("Direct API key (optional)", fg="bright_blue"), default="") if not llm_config["api_key_env"] else ""

    schema = {
        "pipeline_id": pipeline_id,
        "description": description,
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "tasks": tasks,
        "global_config": {
            "default_output_db": config["db_name"],
            "logging_level": "INFO",
            "retry_on_failure": True,
            "max_retries": 2,
            "allowed_task_types": allowed_task_types,
            "allowed_domains": [],
            "backend_host": backend_host,
            "frontend_host": frontend_host,
            "llm_config": llm_config,
            "vector_db_config": {"type": "chroma", "path": config["chroma_path"]}
        },
        "metadata": {
            "tags": tags,
            "pipeline_type": pipeline_type,
            "linked_pipelines": [],
            "status": "draft",
            "parent_version": None,
            "sub_schemas": []
        }
    }

    if interactive and click.confirm(click.style("Configure advanced settings?", fg="bright_blue"), default=False):
        logging_level = click.prompt(click.style("Logging level", fg="bright_blue"), default="INFO", type=click.Choice(["INFO", "DEBUG", "WARNING", "ERROR"]))
        retry_on_failure = click.confirm(click.style("Retry on failure?", fg="bright_blue"), default=True)
        max_retries = click.prompt(click.style("Max retries", fg="bright_blue"), type=int, default=2)
        domains_input = click.prompt(click.style("Allowed domains (comma-separated)", fg="bright_blue"), default="")
        allowed_domains = [d.strip() for d in domains_input.split(",") if d.strip()]
        
        schema["global_config"].update({
            "logging_level": logging_level,
            "retry_on_failure": retry_on_failure,
            "max_retries": max_retries,
            "allowed_domains": allowed_domains
        })

    try:
        client = get_mongo_client(config["uri"], db_name=config["db_name"])
        db_name = config["db_name"]
        validate_schema(schema, is_initial=True)
        push_schema(client, db_name, schema, is_initial=True)
        click.secho(f"✓ Initial schema {pipeline_id} validated and pushed to MongoDB.", fg="bright_green", bold=True)
        update_current_schema(client, db_name, pipeline_id, schema_dir)
    except ValueError as e:
        click.secho(f"✗ Validation error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return
    except Exception as e:
        click.secho(f"✗ Push error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return

    try:
        with schema_path.open("w") as f:
            json.dump(schema, f, indent=2)
        schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        click.secho(f"✓ Main pipeline initialized: {schema_path}", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Failed to write schema file {schema_path}: {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--main-schema', type=click.Path(exists=True), required=True, help='Path to main schema file (e.g., schemas/Production.json)')
@click.option('--interactive/--no-interactive', default=True, help='Enable interactive prompts')
def sub_init(main_schema, interactive):
    """Initialize a sub-schema inheriting from the main schema."""
    show_banner()
    click.secho("\nInitializing Sub-Schema...", fg="bright_yellow", bold=True)

    # Load main schema to inherit global_config
    main_schema_data = load_main_schema(main_schema)
    pipeline_id = click.prompt(click.style("Sub-Schema Pipeline ID", fg="bright_blue"), default="new_sub_pipeline") if interactive else "new_sub_pipeline"
    description = click.prompt(click.style("Description", fg="bright_blue"), default="Sub-schema pipeline") if interactive else "Sub-schema pipeline"
    created_by = click.prompt(click.style("Creator name", fg="bright_blue"), default="user") if interactive else "user"

    if interactive and click.confirm(click.style("Add optional metadata? (tags, pipeline type)", fg="bright_blue"), default=False):
        tags_input = click.prompt(click.style("Tags (comma-separated)", fg="bright_blue"), default="")
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        pipeline_type = click.prompt(click.style("Pipeline type", fg="bright_blue"), default="ai-query")
    else:
        tags = []
        pipeline_type = "ai-query"

    tasks = []
    allowed_task_types = main_schema_data["global_config"]["allowed_task_types"]
    if interactive:
        config_method = click.prompt(
            click.style("Configure tasks via (1: CLI, 2: Manual JSON Edit)", fg="bright_blue"),
            type=click.Choice(["1", "2"]),
            default="1"
        )
        if config_method == "1":
            while True:
                tasks = configure_task(len(tasks), interactive, allowed_task_types, tasks)
                if not click.confirm(click.style("Add another task?", fg="bright_blue"), default=False):
                    break
        else:
            json_path = click.prompt(click.style("Path to JSON file for schema", fg="bright_blue"), default=f"schemas/sub-schemas/{pipeline_id}.json")
            json_path = Path(json_path)
            if json_path.is_dir():
                click.secho(f"✗ Provided path is a directory: {json_path}. Please specify a .json file.", fg="red", bold=True)
                return
            json_path.parent.mkdir(parents=True, exist_ok=True)
            if not json_path.exists():
                default_tasks = [{"task_id": 1, "description": "Default Task", "task_type": "LOCAL", "endpoint": "contextchain.utils.default_task", "rerun": None}]
                with json_path.open("w") as f:
                    json.dump({"tasks": default_tasks}, f, indent=2)
                click.secho(f"✓ Created default schema file: {json_path}", fg="bright_green", bold=True)
            try:
                with json_path.open("r") as f:
                    tasks_data = json.load(f)
                tasks = tasks_data.get("tasks", [])
            except json.JSONDecodeError:
                click.secho(f"✗ Invalid JSON format in {json_path}", fg="red", bold=True)
                return
    else:
        tasks = [configure_task(0, interactive, allowed_task_types, [])[0]]

    schema = {
        "pipeline_id": pipeline_id,
        "description": description,
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "tasks": tasks,
        "global_config": main_schema_data["global_config"],  # Inherit from main schema
        "metadata": {
            "tags": tags,
            "pipeline_type": pipeline_type,
            "linked_pipelines": [],
            "status": "draft",
            "parent_version": None,
            "parent_pipeline_id": main_schema_data["pipeline_id"]
        }
    }

    if interactive and click.confirm(click.style("Configure advanced settings?", fg="bright_blue"), default=False):
        logging_level = click.prompt(click.style("Logging level", fg="bright_blue"), default=main_schema_data["global_config"]["logging_level"], type=click.Choice(["INFO", "DEBUG", "WARNING", "ERROR"]))
        retry_on_failure = click.confirm(click.style("Retry on failure?", fg="bright_blue"), default=main_schema_data["global_config"]["retry_on_failure"])
        max_retries = click.prompt(click.style("Max retries", fg="bright_blue"), type=int, default=main_schema_data["global_config"]["max_retries"])
        domains_input = click.prompt(click.style("Allowed domains (comma-separated)", fg="bright_blue"), default=",".join(main_schema_data["global_config"]["allowed_domains"]))
        allowed_domains = [d.strip() for d in domains_input.split(",") if d.strip()]
        
        schema["global_config"].update({
            "logging_level": logging_level,
            "retry_on_failure": retry_on_failure,
            "max_retries": max_retries,
            "allowed_domains": allowed_domains
        })

    try:
        client = get_mongo_client(main_schema_data["global_config"]["default_output_db"])
        db_name = main_schema_data["global_config"]["default_output_db"]
        validate_schema(schema, is_initial=True)
        push_schema(client, db_name, schema, is_initial=True)
        click.secho(f"✓ Sub-schema {pipeline_id} validated and pushed to MongoDB.", fg="bright_green", bold=True)
        update_current_schema(client, db_name, pipeline_id, Path(main_schema).parent)
    except ValueError as e:
        click.secho(f"✗ Validation error in sub-schema '{pipeline_id}': {e}", fg="red", bold=True)
        return
    except Exception as e:
        click.secho(f"✗ Push error in sub-schema '{pipeline_id}': {e}", fg="red", bold=True)
        return

    schema_path = Path(f"schemas/sub-schemas/{pipeline_id}.json")
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    with schema_path.open("w") as f:
        json.dump(schema, f, indent=2)
    schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    click.secho(f"✓ Sub-schema initialized: {schema_path}", fg="bright_green", bold=True)

@cli.command()
@click.option('--pipeline-id', required=True, help='Pipeline ID')
def new_version(pipeline_id):
    """Create a new schema version (local copy only)."""
    show_banner()
    click.secho(f"\nCreating New Version for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        if not config_path.exists():
            click.secho(f"✗ Config file {config_path} not found. Please run 'init' first.", fg="red", bold=True)
            return
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        versions = list_versions(client, db_name, pipeline_id)
        
        if not versions:
            click.secho(f"✗ No versions found for {pipeline_id}. Starting with new version.", fg="red", bold=True)
            latest_version = "v0.0.0"
        else:
            latest_version = "v0.0.0"  # Default for naming, since schema_version is removed

        click.secho(f"Creating new version for {pipeline_id}", fg="bright_blue")
        new_version = f"v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"  # Use timestamp for versioning
        
        schema = load_schema(client, db_name, pipeline_id)
        if not schema:
            click.secho(f"✗ No schema found for {pipeline_id}.", fg="red", bold=True)
            return
        
        schema["created_at"] = datetime.utcnow().isoformat() + "Z"
        schema["created_by"] = os.getenv("USER", "unknown")
        schema["metadata"]["parent_version"] = latest_version
        schema["metadata"]["status"] = "draft"
        schema["metadata"]["changelog"] = [f"Auto-generated new version {new_version}"]

        schema_dir = Path("schemas")
        schema_dir.mkdir(parents=True, exist_ok=True)
        schema_path = schema_dir / f"{pipeline_id}.{new_version}.json"
        with schema_path.open("w") as f:
            json.dump(schema, f, indent=2)
        schema_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        click.secho(f"✓ New schema version {new_version} created locally: {schema_path}", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--main-schema', type=click.Path(exists=True), required=True, help='Path to main schema file (e.g., schemas/Production.json)')
def schema_compile(main_schema):
    """Validate a main schema and its sub-schemas."""
    click.secho("\nValidating Schema...", fg="bright_yellow", bold=True)
    try:
        schema = load_main_schema(main_schema)
        validate_schema(schema)
        click.secho(f"✓ Main schema {schema['pipeline_id']} validated successfully.", fg="bright_green", bold=True)
        for sub_schema_path in schema["metadata"]["sub_schemas"]:
            try:
                with open(sub_schema_path, 'r') as f:
                    sub_schema = json.load(f)
                validate_schema(sub_schema)
                click.secho(f"✓ Sub-schema {sub_schema['pipeline_id']} validated successfully.", fg="bright_green", bold=True)
            except ValueError as e:
                click.secho(f"✗ Validation error in sub-schema '{sub_schema['pipeline_id']}' ({sub_schema_path}): {e}", fg="red", bold=True)
                sys.exit(1)
            except Exception as e:
                click.secho(f"✗ Error in sub-schema '{sub_schema['pipeline_id']}' ({sub_schema_path}): {e}", fg="red", bold=True)
                sys.exit(1)
    except ValueError as e:
        click.secho(f"✗ Validation error in main schema '{schema['pipeline_id']}': {e}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error in main schema '{schema['pipeline_id']}': {e}", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.option('--main-schema', type=click.Path(exists=True), required=True, help='Path to main schema file (e.g., schemas/Production.json)')
def schema_push(main_schema):
    """Push a main schema and its sub-schemas to MongoDB."""
    click.secho("\nPushing Schema to MongoDB...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_main_schema(main_schema)
        validate_schema(schema)
        push_schema(client, db_name, schema)
        click.secho(f"✓ Main schema {schema['pipeline_id']} pushed to MongoDB.", fg="bright_green", bold=True)
        update_current_schema(client, db_name, schema["pipeline_id"], Path(main_schema).parent)
        copy_schema_file(schema["pipeline_id"], schema["metadata"].get("parent_version", "v0.0.0"), datetime.utcnow().strftime("%Y%m%d_%H%M%S"), Path(main_schema).parent)
        for sub_schema_path in schema["metadata"]["sub_schemas"]:
            try:
                with open(sub_schema_path, 'r') as f:
                    sub_schema = json.load(f)
                validate_schema(sub_schema)
                push_schema(client, db_name, sub_schema)
                click.secho(f"✓ Sub-schema {sub_schema['pipeline_id']} pushed to MongoDB.", fg="bright_green", bold=True)
                update_current_schema(client, db_name, sub_schema["pipeline_id"], Path(main_schema).parent)
                copy_schema_file(sub_schema["pipeline_id"], sub_schema["metadata"].get("parent_version", "v0.0.0"), datetime.utcnow().strftime("%Y%m%d_%H%M%S"), Path(main_schema).parent)
            except ValueError as e:
                click.secho(f"✗ Validation error in sub-schema '{sub_schema['pipeline_id']}' ({sub_schema_path}): {e}", fg="red", bold=True)
                sys.exit(1)
            except Exception as e:
                click.secho(f"✗ Push error in sub-schema '{sub_schema['pipeline_id']}' ({sub_schema_path}): {e}", fg="red", bold=True)
                sys.exit(1)
    except ValueError as e:
        click.secho(f"✗ Validation error in main schema '{schema['pipeline_id']}': {e}", fg="red", bold=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Push error in main schema '{schema['pipeline_id']}': {e}", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--version', help='Schema version (default: latest)')
def run(pipeline_id, version):
    """Run an entire pipeline, including sub-schemas."""
    click.secho(f"\nRunning Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id, version)
        if not schema:
            click.secho(f"✗ Pipeline {pipeline_id} not found.", fg="red", bold=True)
            sys.exit(1)
        execute_pipeline(client, db_name, schema)
        for sub_schema_path in schema["metadata"]["sub_schemas"]:
            try:
                with open(sub_schema_path, 'r') as f:
                    sub_schema = json.load(f)
                execute_pipeline(client, db_name, sub_schema)
                click.secho(f"✓ Sub-schema {sub_schema['pipeline_id']} executed successfully.", fg="bright_green", bold=True)
            except Exception as e:
                click.secho(f"✗ Execution error in sub-schema '{sub_schema['pipeline_id']}' ({sub_schema_path}): {e}", fg="red", bold=True)
                sys.exit(1)
        click.secho(f"✓ Pipeline {pipeline_id} and sub-schemas executed successfully.", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Execution error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--task_id', type=int, required=True, help='Task ID')
@click.option('--version', help='Schema version (default: latest)')
def run_task(pipeline_id, task_id, version):
    """Run a single task for development."""
    click.secho(f"\nRunning Task {task_id} in Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id, version)
        if not schema:
            click.secho(f"✗ Pipeline {pipeline_id} not found.", fg="red", bold=True)
            sys.exit(1)
        task = next((t for t in schema["tasks"] if t["task_id"] == task_id), None)
        if not task:
            click.secho(f"✗ Task {task_id} not found in pipeline '{pipeline_id}'.", fg="red", bold=True)
            sys.exit(1)
        if task["task_type"] == "LLM_GENERATE" and task["parameters"].get("output_format") == "json":
            result = execute_single_task(client, db_name, schema, task)
            try:
                jsonschema.validate(result, task["parameters"].get("json_schema", {}))
            except jsonschema.ValidationError as e:
                click.secho(f"✗ JSON schema validation failed for task '{task_id}' in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
                sys.exit(1)
        else:
            execute_single_task(client, db_name, schema, task)
        click.secho(f"✓ Task {task_id} in pipeline '{pipeline_id}' executed successfully.", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Execution error in task '{task_id}' in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        sys.exit(1)

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def version_list(pipeline_id):
    """List schema versions for a pipeline."""
    click.secho(f"\nListing Versions for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        versions = list_versions(client, db_name, pipeline_id)
        if not versions:
            click.secho(f"No versions found for {pipeline_id}.", fg="bright_yellow")
            return
        click.secho(f"Found {len(versions)} version(s):", fg="bright_green")
        for v in versions:
            is_latest = " (latest)" if v.get("is_latest", False) else ""
            click.secho(f"  • Version {v.get('schema_version', 'unknown')}{is_latest}: Created {v['created_at']}", fg="bright_cyan")
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--version', required=True, help='Version to rollback to')
def version_rollback(pipeline_id, version):
    """Rollback to a previous schema version."""
    click.secho(f"\nRolling Back Pipeline {pipeline_id} to Version {version}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        rollback_version(client, db_name, pipeline_id, version)
        click.secho(f"✓ Rolled back {pipeline_id} to version {version}.", fg="bright_green", bold=True)
        update_current_schema(client, db_name, pipeline_id, Path("schemas"))
    except ValueError as e:
        click.secho(f"✗ Rollback error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return

@cli.command()
def ccshare_init():
    """Initialize a .ccshare file for collaborative MongoDB Atlas access."""
    click.secho("\nInitializing .ccshare File...", fg="bright_yellow", bold=True)
    ccshare = {
        "uri": click.prompt(click.style("MongoDB Atlas URI", fg="bright_blue"), default="mongodb+srv://user:pass@cluster0.mongodb.net"),
        "db_name": click.prompt(click.style("Database name", fg="bright_blue"), default="blacklane-retail"),
        "roles": []
    }
    while click.confirm(click.style("Add a user role?", fg="bright_blue")):
        user = click.prompt(click.style("Username", fg="bright_blue"))
        role = click.prompt(click.style("Role", fg="bright_blue"), default="readOnly", type=click.Choice(["readOnly", "readWrite"]))
        ccshare["roles"].append({"user": user, "role": role})
    output_path = Path("config/team.ccshare")
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w") as f:
        yaml.safe_dump(ccshare, f)
    os.chmod(output_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    click.secho(f"✓ .ccshare file created: {output_path}", fg="bright_green", bold=True)

@cli.command()
@click.option('--uri', required=True, help='MongoDB Atlas URI')
def ccshare_join(uri):
    """Join an existing .ccshare collaboration."""
    click.secho("\nJoining .ccshare Collaboration...", fg="bright_yellow", bold=True)
    ccshare = {
        "uri": uri,
        "db_name": click.prompt(click.style("Database name", fg="bright_blue"), default="blacklane-retail"),
        "roles": [{
            "user": click.prompt(click.style("Username", fg="bright_blue")), 
            "role": click.prompt(click.style("Role", fg="bright_blue"), default="readOnly", type=click.Choice(["readOnly", "readWrite"]))
        }]
    }
    output_path = Path("config/team.ccshare")
    output_path.parent.mkdir(exist_ok=True)
    with output_path.open("w") as f:
        yaml.safe_dump(ccshare, f)
    os.chmod(output_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
    click.secho(f"✓ Joined collaboration: {output_path}", fg="bright_green", bold=True)

@cli.command()
def ccshare_status():
    """Check the status of the .ccshare configuration."""
    click.secho("\nChecking .ccshare Status...", fg="bright_yellow", bold=True)
    ccshare_path = Path("config/team.ccshare")
    if ccshare_path.exists():
        try:
            with ccshare_path.open("r") as f:
                ccshare = yaml.safe_load(f)
            client = get_mongo_client(ccshare["uri"])
            client.server_info()
            click.secho(f"✓ Connected to MongoDB", fg="bright_green", bold=True)
            click.secho(f"  Database: {ccshare['db_name']}", fg="bright_cyan")
            click.secho(f"  Roles: {ccshare['roles']}", fg="bright_cyan")
        except Exception as e:
            click.secho(f"✗ Connection error: {e}", fg="red", bold=True)
            return
    else:
        click.secho("✗ No .ccshare file found.", fg="red", bold=True)
        return

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def logs(pipeline_id):
    """Display logs for a pipeline."""
    click.secho(f"\nDisplaying Logs for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        logs = list(client[db_name]["trigger_logs"].find({"pipeline_id": pipeline_id}))
        if logs:
            click.secho(f"Found {len(logs)} log entries:", fg="bright_green")
            for log in logs:
                click.secho(f"  • {log}", fg="bright_blue")
        else:
            click.secho(f"No logs found for {pipeline_id}.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--task_id', type=int, required=True, help='Task ID')
def results(task_id):
    """Display results for a specific task."""
    click.secho(f"\nDisplaying Results for Task {task_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        results = list(client[db_name]["task_results"].find({"task_id": task_id}))
        if results:
            click.secho(f"Found {len(results)} result(s):", fg="bright_green")
            for result in results:
                click.secho(f"  • {result}", fg="bright_blue")
        else:
            click.secho(f"No results found for task {task_id}.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error in task '{task_id}': {e}", fg="red", bold=True)
        return

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
@click.option('--version', help='Schema version (default: latest)')
def schema_pull(pipeline_id, version):
    """Pull a schema from MongoDB."""
    click.secho(f"\nPulling Schema for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id, version)
        if schema:
            schema_dir = Path("schemas")
            schema_dir.mkdir(parents=True, exist_ok=True)
            schema_path = schema_dir / f"{pipeline_id}.json"
            with schema_path.open("w") as f:
                json.dump(schema, f, indent=2)
            click.secho(f"✓ Schema pulled: {schema_path}", fg="bright_green", bold=True)
        else:
            click.secho(f"✗ Schema {pipeline_id} not found.", fg="red", bold=True)
            return
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)
        return

@cli.command()
def list_pipelines():
    """List all pipelines in MongoDB."""
    click.secho("\nListing All Pipelines...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        pipelines = client[db_name]["schema_registry"].distinct("pipeline_id")
        if pipelines:
            click.secho(f"Found {len(pipelines)} pipeline(s):", fg="bright_green")
            for pipeline in pipelines:
                click.secho(f"  • {pipeline}", fg="bright_cyan")
        else:
            click.secho("No pipelines found.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)
        return

@cli.group()
def vector():
    """Vector DB operations."""
    pass

@vector.command()
@click.option('--collection', required=True, help='Collection name')
def init(collection):
    """Initialize a vector DB collection."""
    click.secho(f"\nInitializing Vector DB Collection {collection}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = ChromaClient(config.get("chroma_path", "./blacklane-optim"))
        client.create_collection(collection)
        click.secho(f"✓ Vector DB collection {collection} initialized.", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)

@vector.command()
@click.option('--collection', required=True, help='Collection name')
@click.option('--query', required=True, help='Search query')
def search(collection, query):
    """Search in a vector DB collection."""
    click.secho(f"\nSearching in Vector DB Collection {collection}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = ChromaClient(config.get("chroma_path", "./blacklane-optim"))
        results = client.search(collection, query)
        click.secho(f"Results: {results}", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)

@cli.group()
def llm():
    """Local LLM operations."""
    pass

@llm.command()
@click.option('--model', required=True, help='LLM model name (e.g., mistral:7b)')
def setup(model):
    """Setup a local LLM model."""
    click.secho(f"\nSetting up LLM Model {model}...", fg="bright_yellow", bold=True)
    try:
        # Check if Ollama server is running
        response = requests.get("http://localhost:11434")
        if response.status_code != 200:
            click.secho("✗ Ollama server not running. Start it with 'ollama run mistral:7b' in a separate terminal.", fg="red", bold=True)
            return
        # Check if model is pulled
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model not in result.stdout:
            click.secho(f"Pulling model {model}...", fg="bright_yellow")
            subprocess.run(["ollama", "pull", model], check=True)
        click.secho(f"✓ LLM model {model} setup completed.", fg="bright_green", bold=True)
    except subprocess.CalledProcessError:
        click.secho(f"✗ Failed to pull model {model}. Ensure Ollama is installed and accessible.", fg="red", bold=True)
    except requests.RequestException:
        click.secho("✗ Ollama server not running. Start it with 'ollama run mistral:7b' in a separate terminal.", fg="red", bold=True)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def metrics(pipeline_id):
    """Display metrics for a pipeline."""
    click.secho(f"\nDisplaying Metrics for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        metrics_data = list(client[db_name]["metrics"].find({"pipeline_id": pipeline_id}))
        if metrics_data:
            click.secho(f"Found {len(metrics_data)} metric entries:", fg="bright_green")
            for metric in metrics_data:
                click.secho(f"  • {metric}", fg="bright_blue")
        else:
            click.secho(f"No metrics found for {pipeline_id}.", fg="bright_yellow")
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)

@cli.command()
@click.option('--task_id', type=int, required=True, help='Task ID')
def evaluate(task_id):
    """Evaluate results for a task."""
    click.secho(f"\nEvaluating Task {task_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        results = list(client[db_name]["task_results"].find({"task_id": task_id}))
        evaluation = evaluate_results(results)
        click.secho(f"Evaluation: {evaluation}", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Error in task '{task_id}': {e}", fg="red", bold=True)

@cli.command()
@click.option('--pipeline_id', required=True, help='Pipeline ID')
def schema_current(pipeline_id):
    """Display the current schema."""
    click.secho(f"\nDisplaying Current Schema for Pipeline {pipeline_id}...", fg="bright_yellow", bold=True)
    try:
        config_path = Path("config/default_config.yaml")
        with config_path.open("r") as f:
            config = yaml.safe_load(f)
        client = get_mongo_client(config["uri"])
        db_name = config["db_name"]
        schema = load_schema(client, db_name, pipeline_id)
        if schema:
            click.secho(f"Created at: {schema['created_at']}", fg="bright_cyan")
            click.secho(f"Description: {schema['description']}", fg="bright_cyan")
        else:
            click.secho(f"✗ Schema {pipeline_id} not found.", fg="red", bold=True)
    except Exception as e:
        click.secho(f"✗ Error in pipeline '{pipeline_id}': {e}", fg="red", bold=True)

@cli.group()
def plugin():
    """Manage plugins."""
    pass

@plugin.command()
@click.option('--type', required=True, help='Task type')
@click.option('--handler', required=True, help='Handler function (module.func)')
def register(type, handler):
    """Register a custom task plugin."""
    click.secho(f"\nRegistering Plugin {type}...", fg="bright_yellow", bold=True)
    try:
        register_task(type, handler)
        click.secho(f"✓ Plugin {type} registered with handler {handler}.", fg="bright_green", bold=True)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", bold=True)

if __name__ == "__main__":
    cli()