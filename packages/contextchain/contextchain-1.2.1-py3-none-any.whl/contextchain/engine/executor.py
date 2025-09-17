#!/usr/bin/env python3
import logging
import requests
import json
import os
from typing import Dict, List, Any
from contextchain.db.mongo_client import get_mongo_client
from contextchain.db.vector_db_client import get_vector_db_client
from contextchain.engine.validator import validate_schema
from contextchain.local_llm_client import OllamaClient
from contextchain.data_processing import chunk_text, summarize_text
from contextchain.dag_builder import build_dag
from contextchain.evaluation import evaluate_results
from contextchain.task_registry import get_task_handler
from datetime import datetime
import time
import importlib
from urllib.parse import urlparse, urljoin
from pymongo import UpdateOne
import concurrent.futures
import networkx as nx
from pathlib import Path
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_inputs(task: Dict[str, Any], db: Any, schema: Dict[str, Any], sub_schemas: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Fetch inputs from previous tasks, input_source, or sub-schemas based on task dependencies."""
    inputs = {}
    sub_schemas = sub_schemas or []

    # Handle inputs from main schema
    if task.get("inputs"):
        for input_ref in task["inputs"]:
            if isinstance(input_ref, int):  # Task ID dependency
                source_task = next((t for t in schema["tasks"] if t["task_id"] == input_ref), None)
                if source_task:
                    source_coll = source_task.get("output_collection", "task_results")
                    data = db[source_coll].find_one({"task_id": input_ref}, sort=[("timestamp", -1)])
                    inputs[f"task_{input_ref}"] = data.get("output", {}) if data else {}
                else:
                    # Check sub-schemas for input task
                    for sub_schema in sub_schemas:
                        source_task = next((t for t in sub_schema["tasks"] if t["task_id"] == input_ref), None)
                        if source_task:
                            source_coll = source_task.get("output_collection", "task_results")
                            data = db[source_coll].find_one({"task_id": input_ref}, sort=[("timestamp", -1)])
                            inputs[f"task_{input_ref}"] = data.get("output", {}) if data else {}
                            break
            elif isinstance(input_ref, str):  # Named input
                source_coll = task.get("input_source")
                if source_coll and isinstance(source_coll, (str, list)):
                    if isinstance(source_coll, list):
                        source_coll = source_coll[0]  # Use first source
                    data = db[source_coll].find_one(sort=[("timestamp", -1)])
                    inputs[input_ref] = data.get(input_ref) if data else None
    return inputs

def resolve_dependencies(tasks: List[Dict[str, Any]], task_id: int, context: Dict[int, Any]) -> Dict[str, Any]:
    """Resolve dependencies and build input mapping."""
    task = next(t for t in tasks if t["task_id"] == task_id)
    inputs = task.get("inputs", [])
    input_mapping = task.get("input_mapping", [])
    resolved_context = context.copy()

    for input_id in inputs:
        if isinstance(input_id, int) and input_id not in context:
            raise ValueError(f"Dependency {input_id} not executed before task {task_id}")
        resolved_context[input_id] = context.get(input_id, {})

    payload = {}
    for mapping in input_mapping:
        source = mapping.get("source", "task_results")
        key = mapping.get("key")
        task_id_ref = mapping.get("task_id")
        if task_id_ref and task_id_ref in context:
            data = context[task_id_ref]
            if isinstance(data, dict) and key in data.get("output", {}):
                payload[key] = data["output"][key]
    return payload

def execute_http_request(url: str, method: str, payload: Dict[str, Any], headers: Dict[str, str] = None, timeout: int = 30, retries: int = 0) -> Dict[str, Any]:
    """Execute an HTTP request with retry logic."""
    headers = headers or {"Content-Type": "application/json"}
    for attempt in range(retries + 1):
        try:
            response = requests.request(method.lower(), url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return {"output": response.json(), "status": "success"}
        except requests.RequestException as e:
            logger.error(f"HTTP request failed (attempt {attempt + 1}/{retries + 1}): {str(e)}")
            if attempt == retries:
                return {"status": "failed", "error": str(e)}
            time.sleep(2 ** attempt)
    return {"status": "failed"}

def execute_llm_request(llm_config: Dict[str, Any], prompt: str, task_model: str = None, timeout: int = 30) -> Dict[str, Any]:
    """Execute an LLM request using global config."""
    provider = llm_config.get("provider", "ollama")
    if provider == "ollama":
        model = task_model or llm_config.get("model", "mistral:7b")
        llm_client = OllamaClient(model=model)
        try:
            response = llm_client.generate(prompt, max_tokens=llm_config.get("max_tokens", 512))
            return {"output": response, "status": "success"}
        except Exception as e:
            logger.error(f"LLM request failed: {str(e)}")
            return {"status": "failed", "error": str(e)}
    else:
        api_key = llm_config.get("api_key") or os.getenv(llm_config.get("api_key_env", "OPENROUTER_API_KEY"))
        if not api_key:
            return {"status": "failed", "error": "LLM API key not found"}
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": llm_config.get("referer", "http://localhost:3000"),
            "X-Title": llm_config.get("title", "Retail Intelligence"),
            "Content-Type": "application/json"
        }
        model = task_model or llm_config["model"]
        url = llm_config.get("url", "")
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                timeout=timeout
            )
            response.raise_for_status()
            return {"output": response.json()["choices"][0]["message"]["content"], "status": "success"}
        except requests.RequestException as e:
            logger.error(f"LLM request failed: {str(e)}")
            return {"status": "failed", "error": str(e)}

def execute_task(task: Dict[str, Any], schema: Dict[str, Any], db: Any, sub_schemas: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Execute a single task based on its type."""
    output_collection = task.get("output_collection", "task_results")
    result = {}
    parameters = task.get("parameters", {})
    vdb_client = get_vector_db_client(schema["global_config"].get("vector_db_config", {}).get("path", None))

    try:
        if task["task_type"] == "LLM":
            prompt = task.get("prompt_template", "").format(**parameters)
            result = execute_llm_request(schema["global_config"]["llm_config"], prompt, task.get("model"))
        elif task["task_type"] == "LOCAL":
            module, func = task["endpoint"].rsplit(".", 1)
            mod = importlib.import_module(module)
            func = getattr(mod, func)
            inputs = fetch_inputs(task, db, schema, sub_schemas)
            merged_inputs = {k: v for d in inputs.values() for k, v in d.items()}
            result = func(**merged_inputs, db=db) if merged_inputs else func(db=db)
        elif task["task_type"] in ["GET", "POST", "PUT", "HTTP"]:
            full_url = task.get("full_url", task["endpoint"])
            if not urlparse(full_url).scheme:
                backend_host = schema["global_config"].get("backend_host", "http://127.0.0.1:8000")
                full_url = urljoin(backend_host, full_url.lstrip("/"))
            result = execute_http_request(full_url, task["task_type"], fetch_inputs(task, db, schema, sub_schemas), retries=schema["global_config"]["max_retries"])
        elif task["task_type"] == "VECTOR_STORE_ADD":
            documents = parameters.get("documents", [])
            metadata = parameters.get("metadata", None)
            collection_name = parameters.get("collection_name", "default_collection")
            if not vdb_client.heartbeat():
                raise ValueError("ChromaDB client is not operational")
            vdb_client.create_collection(collection_name)  # Ensure collection exists
            metrics = vdb_client.add_documents(collection_name, documents, metadata)
            result = {"output": metrics, "status": "success"}
            db["metrics"].insert_one({
                "pipeline_id": schema["pipeline_id"],
                "task_id": task["task_id"],
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        elif task["task_type"] == "VECTOR_STORE_SEARCH":
            query = parameters.get("query", "")
            k = parameters.get("k", 5)
            collection_name = parameters.get("collection_name", "default_collection")
            if not vdb_client.heartbeat():
                raise ValueError("ChromaDB client is not operational")
            vdb_client.create_collection(collection_name)  # Ensure collection exists
            metrics = vdb_client.search(collection_name, query, k)
            result = {"output": metrics["results"], "status": "success"}
            db["metrics"].insert_one({
                "pipeline_id": schema["pipeline_id"],
                "task_id": task["task_id"],
                "metrics": {"time_taken": metrics["time_taken"]},
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        elif task["task_type"] == "CHUNK_TEXT":
            text = parameters.get("text", "")
            max_length = parameters.get("max_length", 512)
            chunks = chunk_text(text, max_length)
            result = {"output": {"chunks": chunks}, "status": "success"}
        elif task["task_type"] == "SUMMARIZE":
            text = parameters.get("text", "")
            model = schema["global_config"].get("llm_config", {}).get("model", "mistral:7b")
            summary = summarize_text(text, model)
            result = {"output": {"summary": summary}, "status": "success"}
        elif task["task_type"] == "EVALUATE":
            results = list(db["task_results"].find({"task_id": task["task_id"]}))
            evaluation = evaluate_results(results)
            result = {"output": {"evaluation": evaluation}, "status": "success"}
        elif task["task_type"] == "LLM_GENERATE":
            llm_client = OllamaClient(model=schema["global_config"].get("llm_config", {}).get("model", "mistral:7b"))
            prompt = parameters.get("prompt", "")
            max_tokens = parameters.get("max_tokens", 512)
            response = llm_client.generate(prompt, max_tokens)
            result = {"output": {"response": response}, "status": "success"}
        else:
            handler = get_task_handler(task["task_type"])
            if handler:
                inputs = fetch_inputs(task, db, schema, sub_schemas)
                result = handler(task, schema, inputs)
            else:
                raise ValueError(f"Unknown task type: {task['task_type']}")

        # Handle rerun logic
        if task.get("rerun", False):
            existing_result = db[output_collection].find_one({
                "pipeline_id": schema["pipeline_id"],
                "schema_version": schema["schema_version"],
                "task_id": task["task_id"]
            })
            previous_data = existing_result.get("output", {}) if existing_result else {}

            if isinstance(result, dict):
                updated_result = result.copy()
                updated_result.update({
                    "pipeline_id": schema["pipeline_id"],
                    "schema_version": schema["schema_version"],
                    "task_id": task["task_id"],
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "previous_data": previous_data
                })
                db[output_collection].delete_many({
                    "pipeline_id": schema["pipeline_id"],
                    "schema_version": schema["schema_version"],
                    "task_id": task["task_id"]
                })
                db[output_collection].insert_one(updated_result)
                return updated_result
            elif isinstance(result, list):
                updated_results = []
                for item in result:
                    if isinstance(item, dict):
                        updated_item = item.copy()
                        updated_item.update({
                            "pipeline_id": schema["pipeline_id"],
                            "schema_version": schema["schema_version"],
                            "task_id": task["task_id"],
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "previous_data": previous_data if not updated_results else {}
                        })
                        db[output_collection].delete_many({
                            "pipeline_id": schema["pipeline_id"],
                            "schema_version": schema["schema_version"],
                            "task_id": task["task_id"],
                            "granularity": updated_item.get("granularity")
                        })
                        db[output_collection].insert_one(updated_item)
                        updated_results.append(updated_item)
                    else:
                        logger.warning(f"Skipping non-dictionary item in list for task {task['task_id']}")
                return updated_results
        else:
            if isinstance(result, dict):
                updated_result = result.copy()
                updated_result.update({
                    "pipeline_id": schema["pipeline_id"],
                    "schema_version": schema["schema_version"],
                    "task_id": task["task_id"],
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                db[output_collection].insert_one(updated_result)
                return updated_result
            elif isinstance(result, list):
                updated_results = []
                for item in result:
                    if isinstance(item, dict):
                        updated_item = item.copy()
                        updated_item.update({
                            "pipeline_id": schema["pipeline_id"],
                            "schema_version": schema["schema_version"],
                            "task_id": task["task_id"],
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        })
                        db[output_collection].insert_one(updated_item)
                        updated_results.append(updated_item)
                    else:
                        logger.warning(f"Skipping non-dictionary item in list for task {task['task_id']}")
                return updated_results

        raise ValueError(f"Unsupported result type {type(result)} for task {task['task_id']}")
    except Exception as e:
        logger.error(f"Task {task['task_id']} execution failed: {str(e)}")
        return {"status": "failed", "error": str(e), "task_id": task["task_id"]}

def execute_pipeline(client: Any, db_name: str, schema: Dict[str, Any]) -> None:
    """Execute the entire pipeline with parallel task execution, including sub-schemas."""
    logger.info(f"Starting pipeline execution for {schema['pipeline_id']}")
    db = client[db_name]

    # Validate schema
    try:
        validate_schema(schema)
    except ValueError as e:
        logger.error(f"Schema validation failed: {str(e)}")
        raise

    # Load sub-schemas
    sub_schemas = []
    for sub_schema_path in schema.get("metadata", {}).get("sub_schemas", []):
        try:
            sub_schema_path = Path(sub_schema_path)
            if not sub_schema_path.is_file():
                logger.error(f"Sub-schema file not found: {sub_schema_path}")
                continue
            with sub_schema_path.open("r") as f:
                sub_schema = json.load(f)
            validate_schema(sub_schema)
            sub_schemas.append(sub_schema)
            logger.info(f"Loaded sub-schema: {sub_schema['pipeline_id']}")
        except Exception as e:
            logger.error(f"Failed to load sub-schema {sub_schema_path}: {str(e)}")
            continue

    # Build DAG for main schema
    dag = build_dag(schema["tasks"])
    tasks = schema["tasks"]
    context = {}  # Store task results by task_id

    # Resolve URLs for HTTP tasks
    resolved_schema = schema.copy()
    for task in tasks:
        task_copy = task.copy()
        if task["task_type"] in ["HTTP", "POST", "GET", "PUT"]:
            endpoint = task["endpoint"]
            if not urlparse(endpoint).scheme:
                backend_host = schema["global_config"].get("backend_host", "http://127.0.0.1:8000")
                task_copy["full_url"] = urljoin(backend_host, endpoint.lstrip("/"))
            else:
                task_copy["full_url"] = endpoint
        resolved_schema["tasks"] = [t for t in resolved_schema["tasks"] if t["task_id"] != task["task_id"]]
        resolved_schema["tasks"].append(task_copy)

    # Save resolved schema
    schema_path = Path(f"schemas/{schema['pipeline_id']}.json")
    output_dir = schema_path.parent / "resolved" / f"{schema['pipeline_id']}_{schema['schema_version']}.json"
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with output_dir.open("w") as f:
        json.dump(resolved_schema, f, indent=2)
    logger.info(f"Saved resolved schema to {output_dir}")

    # Execute tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_task = {}
        for task in tasks:
            if not list(dag.predecessors(task["task_id"])):  # No dependencies
                future = executor.submit(execute_task, task, schema, db, sub_schemas)
                future_to_task[future] = task

        for future in concurrent.futures.as_completed(future_to_task):
            task = future_to_task[future]
            try:
                context[task["task_id"]] = future.result()
                logger.info(f"Task {task['task_id']} executed successfully")
                for successor in dag.successors(task["task_id"]):
                    successor_task = next(t for t in tasks if t["task_id"] == successor)
                    if all(pred in context for pred in dag.predecessors(successor)):
                        future = executor.submit(execute_task, successor_task, schema, db, sub_schemas)
                        future_to_task[future] = successor_task
            except Exception as e:
                logger.error(f"Task {task['task_id']} failed: {str(e)}")
                if not schema["global_config"]["retry_on_failure"]:
                    raise
                for attempt in range(schema["global_config"]["max_retries"]):
                    try:
                        context[task["task_id"]] = execute_task(task, schema, db, sub_schemas)
                        logger.info(f"Task {task['task_id']} retry succeeded")
                        break
                    except Exception as retry_e:
                        logger.error(f"Retry {attempt + 1} failed for task {task['task_id']}: {str(retry_e)}")
                        time.sleep(2)
                else:
                    raise Exception(f"Task {task['task_id']} failed after {schema['global_config']['max_retries']} retries")

    # Execute sub-schemas in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        sub_schema_futures = {}
        for sub_schema in sub_schemas:
            if sub_schema["pipeline_id"] != schema["pipeline_id"]:  # Avoid recursive loops
                future = executor.submit(execute_pipeline, client, db_name, sub_schema)
                sub_schema_futures[future] = sub_schema

        for future in concurrent.futures.as_completed(sub_schema_futures):
            sub_schema = sub_schema_futures[future]
            try:
                future.result()
                logger.info(f"Sub-schema {sub_schema['pipeline_id']} executed successfully")
            except Exception as e:
                logger.error(f"Sub-schema {sub_schema['pipeline_id']} failed: {str(e)}")
                # Continue with other sub-schemas instead of failing the entire pipeline

    logger.info(f"Pipeline {schema['pipeline_id']} execution completed")

def execute_single_task(client: Any, db_name: str, schema: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single task via API request."""
    db = client[db_name]
    # Load sub-schemas for input resolution
    sub_schemas = []
    for sub_schema_path in schema.get("metadata", {}).get("sub_schemas", []):
        try:
            with Path(sub_schema_path).open("r") as f:
                sub_schema = json.load(f)
            sub_schemas.append(sub_schema)
        except Exception as e:
            logger.error(f"Failed to load sub-schema {sub_schema_path}: {str(e)}")
    return execute_task(task, schema, db, sub_schemas)

if __name__ == "__main__":
    # Generalized example - users can replace with their schema
    client = get_mongo_client()
    db_name = "RetailDB"  # Default; can be overridden
    schema_path = Path("schemas/example.json")  # Default example schema; replace with your schema
    if schema_path.exists():
        with schema_path.open("r") as f:
            schema = json.load(f)
        execute_pipeline(client, db_name, schema)
    else:
        print("Example schema not found. Please provide a schema file (e.g., schemas/production.json) and run the executor accordingly.")