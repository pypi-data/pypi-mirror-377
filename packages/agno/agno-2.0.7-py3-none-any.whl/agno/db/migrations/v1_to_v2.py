"""Migration utility to migrate your Agno tables from v1 to v2"""

import json
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import text

from agno.db.mongo.mongo import MongoDb
from agno.db.mysql.mysql import MySQLDb
from agno.db.postgres.postgres import PostgresDb
from agno.db.schemas.memory import UserMemory
from agno.db.sqlite.sqlite import SqliteDb
from agno.session import AgentSession, TeamSession, WorkflowSession
from agno.utils.log import log_error


def convert_v1_metrics_to_v2(metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Convert v1 metrics dictionary to v2 format by mapping old field names to new ones."""
    if not isinstance(metrics_dict, dict):
        return metrics_dict

    # Create a copy to avoid modifying the original
    v2_metrics = metrics_dict.copy()

    # Map v1 field names to v2 field names
    field_mappings = {
        "time": "duration",
        "audio_tokens": "audio_total_tokens",
        "input_audio_tokens": "audio_input_tokens",
        "output_audio_tokens": "audio_output_tokens",
        "cached_tokens": "cache_read_tokens",
    }

    # Fields to remove (deprecated in v2)
    deprecated_fields = ["prompt_tokens", "completion_tokens", "prompt_tokens_details", "completion_tokens_details"]

    # Apply field mappings
    for old_field, new_field in field_mappings.items():
        if old_field in v2_metrics:
            v2_metrics[new_field] = v2_metrics.pop(old_field)

    # Remove deprecated fields
    for field in deprecated_fields:
        v2_metrics.pop(field, None)

    return v2_metrics


def convert_any_metrics_in_data(data: Any) -> Any:
    """Recursively find and convert any metrics dictionaries in the data structure."""
    if isinstance(data, dict):
        # First filter out deprecated v1 fields
        data = filter_deprecated_v1_fields(data)

        # Check if this looks like a metrics dictionary
        if _is_metrics_dict(data):
            return convert_v1_metrics_to_v2(data)

        # Otherwise, recursively process all values
        converted_dict = {}
        for key, value in data.items():
            # Special handling for 'metrics' keys - always convert their values
            if key == "metrics" and isinstance(value, dict):
                converted_dict[key] = convert_v1_metrics_to_v2(value)
            else:
                converted_dict[key] = convert_any_metrics_in_data(value)
        return converted_dict

    elif isinstance(data, list):
        return [convert_any_metrics_in_data(item) for item in data]

    else:
        # Not a dict or list, return as-is
        return data


def _is_metrics_dict(data: Dict[str, Any]) -> bool:
    """Check if a dictionary looks like a metrics dictionary based on common field names."""
    if not isinstance(data, dict):
        return False

    # Common metrics field names (both v1 and v2)
    metrics_indicators = {
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "time",
        "duration",
        "audio_tokens",
        "audio_total_tokens",
        "audio_input_tokens",
        "audio_output_tokens",
        "cached_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
        "reasoning_tokens",
        "prompt_tokens",
        "completion_tokens",
        "time_to_first_token",
        "provider_metrics",
        "additional_metrics",
    }

    # Deprecated v1 fields that are strong indicators this is a metrics dict
    deprecated_v1_indicators = {"time", "audio_tokens", "cached_tokens", "prompt_tokens", "completion_tokens"}

    # If we find any deprecated v1 field, it's definitely a metrics dict that needs conversion
    if any(field in data for field in deprecated_v1_indicators):
        return True

    # Otherwise, if the dict has at least 2 metrics-related fields, consider it a metrics dict
    matching_fields = sum(1 for field in data.keys() if field in metrics_indicators)
    return matching_fields >= 2


def convert_session_data_comprehensively(session_data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Comprehensively convert any metrics found anywhere in session_data from v1 to v2 format."""
    if not session_data:
        return session_data

    # Use the recursive converter to find and fix all metrics
    return convert_any_metrics_in_data(session_data)


def safe_get_runs_from_memory(memory_data: Any) -> Any:
    """Safely extract runs data from memory field, handling various data types."""
    if memory_data is None:
        return None

    # If memory_data is a string, try to parse it as JSON
    if isinstance(memory_data, str):
        try:
            memory_dict = json.loads(memory_data)
            if isinstance(memory_dict, dict):
                return memory_dict.get("runs")
        except (json.JSONDecodeError, AttributeError):
            # If JSON parsing fails, memory_data might just be a string value
            return None

    # If memory_data is already a dict, access runs directly
    elif isinstance(memory_data, dict):
        return memory_data.get("runs")

    # For any other type, return None
    return None


def filter_deprecated_v1_fields(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove v1-only fields that don't exist in v2 models."""
    if not isinstance(data, dict):
        return data

    # Fields that existed in v1 but were removed in v2
    deprecated_fields = {
        "team_session_id",  # RunOutput v1 field, removed in v2
        "formatted_tool_calls",  # RunOutput v1 field, removed in v2
        # Add other deprecated fields here as needed
    }

    # Create a copy and remove deprecated fields
    filtered_data = {k: v for k, v in data.items() if k not in deprecated_fields}
    return filtered_data


def migrate(
    db: Union[PostgresDb, MySQLDb, SqliteDb, MongoDb],
    v1_db_schema: str,
    agent_sessions_table_name: Optional[str] = None,
    team_sessions_table_name: Optional[str] = None,
    workflow_sessions_table_name: Optional[str] = None,
    memories_table_name: Optional[str] = None,
):
    """Given a database connection and table/collection names, parse and migrate the content to corresponding v2 tables/collections.

    Args:
        db: The database to migrate (PostgresDb, MySQLDb, SqliteDb, or MongoDb)
        v1_db_schema: The schema of the v1 tables (leave empty for SQLite and MongoDB)
        agent_sessions_table_name: The name of the agent sessions table/collection. If not provided, agent sessions will not be migrated.
        team_sessions_table_name: The name of the team sessions table/collection. If not provided, team sessions will not be migrated.
        workflow_sessions_table_name: The name of the workflow sessions table/collection. If not provided, workflow sessions will not be migrated.
        memories_table_name: The name of the memories table/collection. If not provided, memories will not be migrated.
    """
    if agent_sessions_table_name:
        db.migrate_table_from_v1_to_v2(
            v1_db_schema=v1_db_schema,
            v1_table_name=agent_sessions_table_name,
            v1_table_type="agent_sessions",
        )

    if team_sessions_table_name:
        db.migrate_table_from_v1_to_v2(
            v1_db_schema=v1_db_schema,
            v1_table_name=team_sessions_table_name,
            v1_table_type="team_sessions",
        )

    if workflow_sessions_table_name:
        db.migrate_table_from_v1_to_v2(
            v1_db_schema=v1_db_schema,
            v1_table_name=workflow_sessions_table_name,
            v1_table_type="workflow_sessions",
        )

    if memories_table_name:
        db.migrate_table_from_v1_to_v2(
            v1_db_schema=v1_db_schema,
            v1_table_name=memories_table_name,
            v1_table_type="memories",
        )


def get_all_table_content(db, db_schema: str, table_name: str) -> list[dict[str, Any]]:
    """Get all content from the given table/collection"""
    try:
        # Check if this is a MongoDB instance
        if hasattr(db, "database") and hasattr(db, "db_client"):
            # MongoDB implementation
            collection = db.database[table_name]
            # Convert MongoDB documents to dictionaries and handle ObjectId
            documents = list(collection.find({}))
            # Convert ObjectId to string for compatibility
            for doc in documents:
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
            return documents
        else:
            # SQL database implementation (PostgreSQL, MySQL, SQLite)
            with db.Session() as sess:
                # Handle empty schema by omitting the schema prefix (needed for SQLite)
                if db_schema and db_schema.strip():
                    sql_query = f"SELECT * FROM {db_schema}.{table_name}"
                else:
                    sql_query = f"SELECT * FROM {table_name}"

                result = sess.execute(text(sql_query))
                return [row._asdict() for row in result]

    except Exception as e:
        log_error(f"Error getting all content from table/collection {table_name}: {e}")
        return []


def parse_agent_sessions(v1_content: List[Dict[str, Any]]) -> List[AgentSession]:
    """Parse v1 Agent sessions into v2 Agent sessions and Memories"""
    sessions_v2 = []

    for item in v1_content:
        session = {
            "agent_id": item.get("agent_id"),
            "agent_data": item.get("agent_data"),
            "session_id": item.get("session_id"),
            "user_id": item.get("user_id"),
            "session_data": convert_session_data_comprehensively(item.get("session_data")),
            "metadata": convert_any_metrics_in_data(item.get("extra_data")),
            "runs": convert_any_metrics_in_data(safe_get_runs_from_memory(item.get("memory"))),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        }
        agent_session = AgentSession.from_dict(session)
        if agent_session is not None:
            sessions_v2.append(agent_session)

    return sessions_v2


def parse_team_sessions(v1_content: List[Dict[str, Any]]) -> List[TeamSession]:
    """Parse v1 Team sessions into v2 Team sessions and Memories"""
    sessions_v2 = []

    for item in v1_content:
        session = {
            "team_id": item.get("team_id"),
            "team_data": item.get("team_data"),
            "session_id": item.get("session_id"),
            "user_id": item.get("user_id"),
            "session_data": convert_session_data_comprehensively(item.get("session_data")),
            "metadata": convert_any_metrics_in_data(item.get("extra_data")),
            "runs": convert_any_metrics_in_data(safe_get_runs_from_memory(item.get("memory"))),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
        }
        team_session = TeamSession.from_dict(session)
        if team_session is not None:
            sessions_v2.append(team_session)

    return sessions_v2


def parse_workflow_sessions(v1_content: List[Dict[str, Any]]) -> List[WorkflowSession]:
    """Parse v1 Workflow sessions into v2 Workflow sessions"""
    sessions_v2 = []

    for item in v1_content:
        session = {
            "workflow_id": item.get("workflow_id"),
            "workflow_data": item.get("workflow_data"),
            "session_id": item.get("session_id"),
            "user_id": item.get("user_id"),
            "session_data": convert_session_data_comprehensively(item.get("session_data")),
            "metadata": convert_any_metrics_in_data(item.get("extra_data")),
            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            # Workflow v2 specific fields
            "workflow_name": item.get("workflow_name"),
            "runs": convert_any_metrics_in_data(item.get("runs")),
        }
        workflow_session = WorkflowSession.from_dict(session)
        if workflow_session is not None:
            sessions_v2.append(workflow_session)

    return sessions_v2


def parse_memories(v1_content: List[Dict[str, Any]]) -> List[UserMemory]:
    """Parse v1 Memories into v2 Memories"""
    memories_v2 = []

    for item in v1_content:
        memory = {
            "memory_id": item.get("memory_id"),
            "memory": item.get("memory"),
            "input": item.get("input"),
            "updated_at": item.get("updated_at"),
            "agent_id": item.get("agent_id"),
            "team_id": item.get("team_id"),
            "user_id": item.get("user_id"),
        }
        memories_v2.append(UserMemory.from_dict(memory))

    return memories_v2
