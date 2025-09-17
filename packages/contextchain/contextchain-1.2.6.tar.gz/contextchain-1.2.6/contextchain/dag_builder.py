import networkx as nx
from typing import Dict, List
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def build_dag(schema: Dict) -> nx.DiGraph:
    """
    Build a directed acyclic graph (DAG) from a schema, including sub-schemas.

    Args:
        schema (Dict): The schema dictionary.

    Returns:
        nx.DiGraph: The constructed DAG.
    """
    dag = nx.DiGraph()
    tasks = schema.get("tasks", [])
    
    # Add tasks from main schema
    for task in tasks:
        task_id = task["task_id"]
        dag.add_node(task_id, task=task)
        for input_id in task.get("inputs", []):
            dag.add_edge(input_id, task_id)
    
    # Process sub-schemas
    sub_schemas = schema.get("metadata", {}).get("sub_schemas", [])
    for sub_schema_path in sub_schemas:
        try:
            with open(sub_schema_path, 'r') as f:
                sub_schema = json.load(f)
            sub_dag = build_dag(sub_schema)  # Recursive call
            dag = nx.compose(dag, sub_dag)
            # Link main schema tasks to sub-schema tasks if specified
            for task in tasks:
                if task.get("sub_schema_inputs"):
                    for input_id in task["sub_schema_inputs"]:
                        dag.add_edge(input_id, task["task_id"])
        except Exception as e:
            logger.error(f"✗ Failed to process sub-schema {sub_schema_path}: {e}")
    
    if not nx.is_directed_acyclic_graph(dag):
        raise ValueError("Schema contains cycles, which is not allowed.")
    
    return dag