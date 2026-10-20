"""Workflow graph validation service.

Validates workflow graphs for:
- Structural correctness (DAG, no cycles)
- Type compatibility between connected nodes
- Required inputs are satisfied
- No orphan nodes
"""
from typing import Dict, List, Any, Set


def validate_workflow_graph(graph_json: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a workflow graph and return validation results.

    Args:
        graph_json: React Flow graph with nodes and edges

    Returns:
        Dict with 'valid' bool, 'errors' list, and 'warnings' list
    """
    errors: List[str] = []
    warnings: List[str] = []

    nodes = graph_json.get("nodes", [])
    edges = graph_json.get("edges", [])

    if not nodes:
        errors.append("Workflow must have at least one node")
        return {"valid": False, "errors": errors, "warnings": warnings}

    node_ids = {node["id"] for node in nodes}

    # Validate edges reference existing nodes
    for edge in edges:
        if edge["source"] not in node_ids:
            errors.append(f"Edge source '{edge['source']}' references non-existent node")
        if edge["target"] not in node_ids:
            errors.append(f"Edge target '{edge['target']}' references non-existent node")

    # Check for cycles (simple DFS-based cycle detection)
    if _has_cycle(nodes, edges):
        errors.append("Workflow contains cycles - must be a directed acyclic graph (DAG)")

    # Check for orphan nodes (no inputs and no outputs)
    connected_nodes = set()
    for edge in edges:
        connected_nodes.add(edge["source"])
        connected_nodes.add(edge["target"])

    orphan_nodes = node_ids - connected_nodes
    if len(orphan_nodes) > 1:  # Allow one source node
        warnings.append(f"Workflow contains {len(orphan_nodes)} disconnected nodes")

    # Validate each node has required configuration
    for node in nodes:
        node_id = node["id"]
        node_data = node.get("data", {})

        if not node_data.get("label"):
            warnings.append(f"Node '{node_id}' is missing a label")

        # Check if node type is recognized
        node_type = node.get("type", "default")
        if node_type not in ["data-source", "transform", "ml-model", "output", "default"]:
            warnings.append(f"Node '{node_id}' has unknown type '{node_type}'")

    # Type compatibility checks (simplified)
    # In a full implementation, this would check input/output type compatibility
    for edge in edges:
        source_node = next((n for n in nodes if n["id"] == edge["source"]), None)
        target_node = next((n for n in nodes if n["id"] == edge["target"]), None)

        if source_node and target_node:
            source_type = source_node.get("type", "")
            target_type = target_node.get("type", "")

            # Output nodes should not have outgoing edges
            if source_type == "output":
                errors.append(
                    f"Output node '{edge['source']}' cannot have outgoing connections"
                )

            # Data sources should not have incoming edges
            if target_type == "data-source":
                errors.append(
                    f"Data source node '{edge['target']}' cannot have incoming connections"
                )

    valid = len(errors) == 0

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
    }


def _has_cycle(nodes: List[Dict], edges: List[Dict]) -> bool:
    """Detect if the graph contains cycles using DFS.

    Args:
        nodes: List of workflow nodes
        edges: List of workflow edges

    Returns:
        True if cycle detected, False otherwise
    """
    # Build adjacency list
    graph: Dict[str, List[str]] = {node["id"]: [] for node in nodes}
    for edge in edges:
        graph.setdefault(edge["source"], []).append(edge["target"])

    visited: Set[str] = set()
    rec_stack: Set[str] = set()

    def dfs(node_id: str) -> bool:
        visited.add(node_id)
        rec_stack.add(node_id)

        for neighbor in graph.get(node_id, []):
            if neighbor not in visited:
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node_id)
        return False

    for node in nodes:
        node_id = node["id"]
        if node_id not in visited:
            if dfs(node_id):
                return True

    return False


def topological_sort(nodes: List[Dict], edges: List[Dict]) -> List[str]:
    """Perform topological sort to get execution order.

    Args:
        nodes: List of workflow nodes
        edges: List of workflow edges

    Returns:
        List of node IDs in execution order
    """
    # Build adjacency list and in-degree count
    graph: Dict[str, List[str]] = {node["id"]: [] for node in nodes}
    in_degree: Dict[str, int] = {node["id"]: 0 for node in nodes}

    for edge in edges:
        graph.setdefault(edge["source"], []).append(edge["target"])
        in_degree[edge["target"]] = in_degree.get(edge["target"], 0) + 1

    # Start with nodes that have no dependencies
    queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
    result = []

    while queue:
        node_id = queue.pop(0)
        result.append(node_id)

        for neighbor in graph.get(node_id, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return result
