"""Workflow execution engine.

Executes workflow graphs by:
1. Validating the graph
2. Sorting nodes in topological order
3. Executing each node sequentially
4. Tracking task runs and results
5. Handling errors and failures
"""
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import WorkflowRun, TaskRun, RunStatus
from app.services.graph_validator import validate_workflow_graph, topological_sort
import logging

logger = logging.getLogger(__name__)


async def execute_workflow(
    run_id: str,
    graph_json: Dict[str, Any],
    db: AsyncSession,
):
    """Execute a workflow asynchronously.

    Args:
        run_id: Workflow run ID
        graph_json: React Flow graph JSON
        db: Database session
    """
    try:
        # Get workflow run
        result = await db.execute(
            select(WorkflowRun).where(WorkflowRun.id == run_id)
        )
        workflow_run = result.scalar_one()

        # Update status to running
        workflow_run.status = RunStatus.RUNNING
        workflow_run.started_at = datetime.now(timezone.utc)
        await db.commit()

        # Validate graph
        validation = validate_workflow_graph(graph_json)
        if not validation["valid"]:
            workflow_run.status = RunStatus.FAILED
            workflow_run.error_message = f"Graph validation failed: {', '.join(validation['errors'])}"
            workflow_run.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return

        # Get execution order
        nodes = graph_json.get("nodes", [])
        edges = graph_json.get("edges", [])
        execution_order = topological_sort(nodes, edges)

        # Build node lookup
        node_lookup = {node["id"]: node for node in nodes}

        # Execute nodes in order
        node_outputs: Dict[str, Any] = {}
        for node_id in execution_order:
            node = node_lookup[node_id]

            # Create task run
            task_run = TaskRun(
                workflow_run_id=run_id,
                node_id=node_id,
                node_type=node.get("type", "default"),
                status=RunStatus.PENDING,
            )
            db.add(task_run)
            await db.commit()
            await db.refresh(task_run)

            try:
                # Execute node
                task_run.status = RunStatus.RUNNING
                task_run.started_at = datetime.now(timezone.utc)
                await db.commit()

                # Get inputs from connected nodes
                inputs = _get_node_inputs(node_id, edges, node_outputs)

                # Execute the node (simplified execution)
                output = await _execute_node(node, inputs, db)

                # Store output
                node_outputs[node_id] = output

                # Update task run
                task_run.status = RunStatus.COMPLETED
                task_run.output_data = {"result": output}
                task_run.completed_at = datetime.now(timezone.utc)
                task_run.logs = f"Node executed successfully"
                await db.commit()

            except Exception as e:
                logger.error(f"Task {task_run.id} failed: {str(e)}")
                task_run.status = RunStatus.FAILED
                task_run.error_message = str(e)
                task_run.completed_at = datetime.now(timezone.utc)
                await db.commit()

                # Fail the entire workflow
                workflow_run.status = RunStatus.FAILED
                workflow_run.error_message = f"Node '{node_id}' failed: {str(e)}"
                workflow_run.completed_at = datetime.now(timezone.utc)
                await db.commit()
                return

        # Workflow completed successfully
        workflow_run.status = RunStatus.COMPLETED
        workflow_run.result_json = {"outputs": node_outputs}
        workflow_run.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        try:
            workflow_run.status = RunStatus.FAILED
            workflow_run.error_message = str(e)
            workflow_run.completed_at = datetime.now(timezone.utc)
            await db.commit()
        except:
            pass


def _get_node_inputs(
    node_id: str,
    edges: List[Dict],
    node_outputs: Dict[str, Any],
) -> Dict[str, Any]:
    """Get input data for a node from connected upstream nodes.

    Args:
        node_id: Target node ID
        edges: Workflow edges
        node_outputs: Outputs from previously executed nodes

    Returns:
        Dictionary of input data
    """
    inputs = {}
    for edge in edges:
        if edge["target"] == node_id:
            source_id = edge["source"]
            if source_id in node_outputs:
                handle = edge.get("targetHandle", "default")
                inputs[handle] = node_outputs[source_id]
    return inputs


async def _execute_node(
    node: Dict[str, Any],
    inputs: Dict[str, Any],
    db: AsyncSession,
) -> Any:
    """Execute a single workflow node.

    This is a simplified executor for M1. In production, this would:
    - Run in isolated Docker containers
    - Use actual ML libraries for training
    - Process real data files
    - Store artifacts in object storage

    For M1, we simulate execution with placeholder logic.

    Args:
        node: Node configuration
        inputs: Input data from upstream nodes
        db: Database session

    Returns:
        Node output data
    """
    node_type = node.get("type", "default")
    node_data = node.get("data", {})
    parameters = node_data.get("parameters", {})

    # Simulate execution delay
    await asyncio.sleep(1)

    # Simplified execution logic by node type
    if node_type == "data-source":
        # Simulate loading data
        return {
            "type": "dataframe",
            "rows": 100,
            "columns": ["id", "feature1", "feature2", "target"],
            "preview": "Sample data loaded successfully",
        }

    elif node_type == "transform":
        # Simulate data transformation
        input_data = inputs.get("data", {})
        return {
            "type": "dataframe",
            "rows": input_data.get("rows", 0),
            "columns": input_data.get("columns", []),
            "preview": f"Transformed data with condition: {parameters.get('condition', 'N/A')}",
        }

    elif node_type == "ml-model":
        # Simulate model training
        model_type = parameters.get("model_type", "linear_regression")
        return {
            "type": "model",
            "model_type": model_type,
            "accuracy": 0.85,
            "metrics": {
                "rmse": 0.25,
                "r2_score": 0.82,
            },
            "status": "trained",
        }

    elif node_type == "output":
        # Simulate saving output
        return {
            "type": "output",
            "status": "saved",
            "path": parameters.get("output_path", "output.csv"),
        }

    else:
        # Default execution
        return {
            "type": "generic",
            "status": "completed",
            "inputs": inputs,
            "parameters": parameters,
        }
