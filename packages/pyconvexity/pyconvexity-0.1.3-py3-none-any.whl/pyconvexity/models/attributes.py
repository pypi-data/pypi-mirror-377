"""
Attribute management operations for PyConvexity.

Provides operations for setting, getting, and managing component attributes
with support for both static values and timeseries data.
"""

import sqlite3
import json
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
from io import BytesIO
import pyarrow as pa
import pyarrow.parquet as pq

from pyconvexity.core.types import (
    StaticValue, TimeseriesPoint, AttributeValue, TimePeriod
)
from pyconvexity.core.errors import (
    ComponentNotFound, AttributeNotFound, ValidationError, TimeseriesError
)

logger = logging.getLogger(__name__)


def set_static_attribute(
    conn: sqlite3.Connection,
    component_id: int,
    attribute_name: str,
    value: StaticValue,
    scenario_id: Optional[int] = None
) -> None:
    """
    Set a static attribute value for a component in a specific scenario.
    
    Args:
        conn: Database connection
        component_id: Component ID
        attribute_name: Name of the attribute
        value: Static value to set
        scenario_id: Scenario ID (uses master scenario if None)
        
    Raises:
        ComponentNotFound: If component doesn't exist
        ValidationError: If attribute doesn't allow static values or validation fails
    """
    # 1. Get component type
    from pyconvexity.models.components import get_component_type
    component_type = get_component_type(conn, component_id)
    
    # 2. Get validation rule
    from pyconvexity.validation.rules import get_validation_rule, validate_static_value
    rule = get_validation_rule(conn, component_type, attribute_name)
    
    # 3. Check if static values are allowed
    if not rule.allows_static:
        raise ValidationError(f"Attribute '{attribute_name}' for {component_type} does not allow static values")
    
    # 4. Validate data type
    validate_static_value(value, rule)
    
    # 5. Resolve scenario ID (get master scenario if None)
    resolved_scenario_id = resolve_scenario_id(conn, component_id, scenario_id)
    
    # 6. Remove any existing attribute for this scenario
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM component_attributes WHERE component_id = ? AND attribute_name = ? AND scenario_id = ?",
        (component_id, attribute_name, resolved_scenario_id)
    )
    
    # 7. Insert new static attribute (store as JSON in static_value TEXT column)
    json_value = value.to_json()
    
    cursor.execute(
        """INSERT INTO component_attributes 
           (component_id, attribute_name, scenario_id, storage_type, static_value, data_type, unit, is_input) 
           VALUES (?, ?, ?, 'static', ?, ?, ?, ?)""",
        (component_id, attribute_name, resolved_scenario_id, json_value, 
         rule.data_type, rule.unit, rule.is_input)
    )


def set_timeseries_attribute(
    conn: sqlite3.Connection,
    component_id: int,
    attribute_name: str,
    timeseries: List[TimeseriesPoint],
    scenario_id: Optional[int] = None
) -> None:
    """
    Set a timeseries attribute value for a component in a specific scenario.
    
    Args:
        conn: Database connection
        component_id: Component ID
        attribute_name: Name of the attribute
        timeseries: List of timeseries points
        scenario_id: Scenario ID (uses master scenario if None)
        
    Raises:
        ComponentNotFound: If component doesn't exist
        ValidationError: If attribute doesn't allow timeseries values
        TimeseriesError: If timeseries serialization fails
    """
    # 1. Get component type
    from pyconvexity.models.components import get_component_type
    component_type = get_component_type(conn, component_id)
    
    # 2. Get validation rule
    from pyconvexity.validation.rules import get_validation_rule
    rule = get_validation_rule(conn, component_type, attribute_name)
    
    # 3. Check if timeseries values are allowed
    if not rule.allows_timeseries:
        raise ValidationError(f"Attribute '{attribute_name}' for {component_type} does not allow timeseries values")
    
    # 4. Serialize timeseries to Parquet
    parquet_data = serialize_timeseries_to_parquet(timeseries)
    
    # 5. Resolve scenario ID (get master scenario if None)
    resolved_scenario_id = resolve_scenario_id(conn, component_id, scenario_id)
    
    # 6. Remove any existing attribute for this scenario
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM component_attributes WHERE component_id = ? AND attribute_name = ? AND scenario_id = ?",
        (component_id, attribute_name, resolved_scenario_id)
    )
    
    # 7. Insert new timeseries attribute
    cursor.execute(
        """INSERT INTO component_attributes 
           (component_id, attribute_name, scenario_id, storage_type, timeseries_data, data_type, unit, is_input) 
           VALUES (?, ?, ?, 'timeseries', ?, ?, ?, ?)""",
        (component_id, attribute_name, resolved_scenario_id, parquet_data,
         rule.data_type, rule.unit, rule.is_input)
    )


def get_attribute(
    conn: sqlite3.Connection,
    component_id: int,
    attribute_name: str,
    scenario_id: Optional[int] = None
) -> AttributeValue:
    """
    Get an attribute value with scenario fallback logic.
    
    Args:
        conn: Database connection
        component_id: Component ID
        attribute_name: Name of the attribute
        scenario_id: Scenario ID (uses master scenario if None)
        
    Returns:
        AttributeValue containing either static or timeseries data
        
    Raises:
        ComponentNotFound: If component doesn't exist
        AttributeNotFound: If attribute doesn't exist
    """
    
    # Get network_id from component to find master scenario
    cursor = conn.cursor()
    cursor.execute("SELECT network_id FROM components WHERE id = ?", (component_id,))
    result = cursor.fetchone()
    if not result:
        raise ComponentNotFound(component_id)
    
    network_id = result[0]
    
    # Get master scenario ID
    master_scenario_id = get_master_scenario_id(conn, network_id)
    
    # Determine which scenario to check first
    current_scenario_id = scenario_id if scenario_id is not None else master_scenario_id
    
    # First try to get the attribute from the current scenario
    cursor.execute(
        """SELECT storage_type, static_value, timeseries_data, data_type, unit
           FROM component_attributes 
           WHERE component_id = ? AND attribute_name = ? AND scenario_id = ?""",
        (component_id, attribute_name, current_scenario_id)
    )
    result = cursor.fetchone()
    
    # If not found in current scenario and current scenario is not master, try master scenario
    if not result and current_scenario_id != master_scenario_id:
        cursor.execute(
            """SELECT storage_type, static_value, timeseries_data, data_type, unit
               FROM component_attributes 
               WHERE component_id = ? AND attribute_name = ? AND scenario_id = ?""",
            (component_id, attribute_name, master_scenario_id)
        )
        result = cursor.fetchone()
    
    if not result:
        raise AttributeNotFound(component_id, attribute_name)
    
    storage_type, static_value_json, timeseries_data, data_type, unit = result
    
    # Handle the deserialization based on storage type
    if storage_type == "static":
        if not static_value_json:
            raise ValidationError("Static attribute missing value")
        
        # Parse JSON value
        json_value = json.loads(static_value_json)
        
        # Convert based on data type
        if data_type == "float":
            if isinstance(json_value, (int, float)):
                static_value = StaticValue(float(json_value))
            else:
                raise ValidationError("Expected float value")
        elif data_type == "int":
            if isinstance(json_value, (int, float)):
                static_value = StaticValue(int(json_value))
            else:
                raise ValidationError("Expected integer value")
        elif data_type == "boolean":
            if isinstance(json_value, bool):
                static_value = StaticValue(json_value)
            else:
                raise ValidationError("Expected boolean value")
        elif data_type == "string":
            if isinstance(json_value, str):
                static_value = StaticValue(json_value)
            else:
                raise ValidationError("Expected string value")
        else:
            raise ValidationError(f"Unknown data type: {data_type}")
        
        return AttributeValue.static(static_value)
    
    elif storage_type == "timeseries":
        if not timeseries_data:
            raise ValidationError("Timeseries attribute missing data")
        
        # Get network_id from component to load time periods
        cursor = conn.execute("SELECT network_id FROM components WHERE id = ?", (component_id,))
        network_row = cursor.fetchone()
        
        network_time_periods = None
        if network_row:
            network_id = network_row[0]
            try:
                from pyconvexity.models.network import get_network_time_periods
                network_time_periods = get_network_time_periods(conn, network_id)
            except Exception as e:
                logger.warning(f"Failed to load network time periods for timestamp computation: {e}")
        
        # Deserialize from Parquet with proper timestamp computation
        timeseries_points = deserialize_timeseries_from_parquet(timeseries_data, network_time_periods)
        return AttributeValue.timeseries(timeseries_points)
    
    else:
        raise ValidationError(f"Unknown storage type: {storage_type}")


def delete_attribute(
    conn: sqlite3.Connection,
    component_id: int,
    attribute_name: str,
    scenario_id: Optional[int] = None
) -> None:
    """
    Delete an attribute from a specific scenario.
    
    Args:
        conn: Database connection
        component_id: Component ID
        attribute_name: Name of the attribute
        scenario_id: Scenario ID (uses master scenario if None)
        
    Raises:
        AttributeNotFound: If attribute doesn't exist
    """
    # Resolve scenario ID (get master scenario if None)
    resolved_scenario_id = resolve_scenario_id(conn, component_id, scenario_id)
    
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM component_attributes WHERE component_id = ? AND attribute_name = ? AND scenario_id = ?",
        (component_id, attribute_name, resolved_scenario_id)
    )
    
    if cursor.rowcount == 0:
        raise AttributeNotFound(component_id, attribute_name)


# Helper functions

def resolve_scenario_id(conn: sqlite3.Connection, component_id: int, scenario_id: Optional[int]) -> int:
    """Resolve scenario ID - if None, get master scenario ID."""
    if scenario_id is not None:
        return scenario_id
    
    # Get network_id from component, then get master scenario
    cursor = conn.cursor()
    cursor.execute("SELECT network_id FROM components WHERE id = ?", (component_id,))
    result = cursor.fetchone()
    if not result:
        raise ComponentNotFound(component_id)
    
    network_id = result[0]
    return get_master_scenario_id(conn, network_id)


def get_master_scenario_id(conn: sqlite3.Connection, network_id: int) -> int:
    """Get the master scenario ID for a network."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM scenarios WHERE network_id = ? AND is_master = TRUE",
        (network_id,)
    )
    result = cursor.fetchone()
    if not result:
        raise ValidationError(f"No master scenario found for network {network_id}")
    return result[0]


# Timeseries serialization functions

def serialize_timeseries_to_parquet(timeseries: List[TimeseriesPoint]) -> bytes:
    """Serialize timeseries to Parquet format - EXACT MATCH WITH RUST SCHEMA."""
    # Define the exact schema to match Rust expectations
    schema = pa.schema([
        ('period_index', pa.int32()),
        ('value', pa.float64())
        ])
    
    if not timeseries:
        # Return empty parquet file with correct schema
        empty_period_array = pa.array([], type=pa.int32())
        empty_value_array = pa.array([], type=pa.float64())
        table = pa.table([empty_period_array, empty_value_array], schema=schema)
    else:
        # Create PyArrow table with EXPLICIT schema to ensure data types match Rust
        period_indices = [p.period_index for p in timeseries]
        values = [p.value for p in timeseries]
        
        # Create arrays with explicit types to ensure Int32 for period_index
        period_array = pa.array(period_indices, type=pa.int32())
        value_array = pa.array(values, type=pa.float64())
        
        table = pa.table([period_array, value_array], schema=schema)
    
    # Serialize to Parquet bytes with SNAPPY compression (match Rust)
    buffer = BytesIO()
    pq.write_table(table, buffer, compression='snappy')
    return buffer.getvalue()


def deserialize_timeseries_from_parquet(data: bytes, network_time_periods: Optional[List[TimePeriod]] = None) -> List[TimeseriesPoint]:
    """Deserialize timeseries from Parquet format - EXACT MATCH WITH RUST."""
    if not data:
        return []

    buffer = BytesIO(data)
    table = pq.read_table(buffer)

    # Convert to pandas for easier handling
    df = table.to_pandas()

    points = []
    for _, row in df.iterrows():
        period_index = int(row['period_index'])
        
        # Compute timestamp from period_index using network time periods if available
        if network_time_periods and 0 <= period_index < len(network_time_periods):
            timestamp = network_time_periods[period_index].timestamp
        else:
            # Fallback: use period_index as timestamp (matching previous behavior for compatibility)
            timestamp = period_index
        
        points.append(TimeseriesPoint(
            timestamp=timestamp,
            value=float(row['value']),
            period_index=period_index
        ))

    return points
