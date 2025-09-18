"""
Scenario management operations for PyConvexity.

Provides operations for creating and managing scenarios within networks.
"""

import sqlite3
import logging
from typing import List, Optional
from datetime import datetime

from pyconvexity.core.errors import ValidationError, DatabaseError

logger = logging.getLogger(__name__)


def create_scenario(
    conn: sqlite3.Connection,
    network_id: int,
    name: str,
    description: Optional[str] = None,
    is_master: bool = False,
) -> int:
    """
    Create a new scenario for a network.
    
    Args:
        conn: Database connection
        network_id: ID of the network
        name: Name of the scenario
        description: Optional description
        is_master: Whether this is a master scenario (default False)
        
    Returns:
        ID of the newly created scenario
        
    Raises:
        ValidationError: If network doesn't exist or scenario name conflicts
        DatabaseError: If creation fails
    """
    
    # Validate network exists
    cursor = conn.execute("SELECT COUNT(*) FROM networks WHERE id = ?", (network_id,))
    if cursor.fetchone()[0] == 0:
        raise ValidationError(f"Network with ID {network_id} not found")
    
    # Check for name conflicts within the network
    cursor = conn.execute(
        "SELECT COUNT(*) FROM scenarios WHERE network_id = ? AND name = ?",
        (network_id, name)
    )
    if cursor.fetchone()[0] > 0:
        raise ValidationError(f"Scenario with name '{name}' already exists in network {network_id}")
    
    # Insert the scenario (database triggers will handle master scenario uniqueness)
    cursor = conn.execute(
        "INSERT INTO scenarios (network_id, name, description, is_master, created_at) "
        "VALUES (?, ?, ?, ?, datetime('now'))",
        (network_id, name, description, is_master)
    )
    
    scenario_id = cursor.lastrowid
    if not scenario_id:
        raise DatabaseError("Failed to create scenario")
    
    logger.info(f"Created scenario '{name}' (ID: {scenario_id}) for network {network_id}")
    return scenario_id


def list_scenarios(conn: sqlite3.Connection, network_id: int) -> List[dict]:
    """
    List all scenarios for a network.
    
    Args:
        conn: Database connection
        network_id: ID of the network
        
    Returns:
        List of scenario dictionaries with keys: id, network_id, name, description, is_master, created_at
        
    Raises:
        DatabaseError: If query fails
    """
    
    cursor = conn.execute(
        "SELECT id, network_id, name, description, is_master, created_at "
        "FROM scenarios "
        "WHERE network_id = ? "
        "ORDER BY is_master DESC, created_at ASC",
        (network_id,)
    )
    
    scenarios = []
    for row in cursor.fetchall():
        scenarios.append({
            'id': row[0],
            'network_id': row[1],
            'name': row[2],
            'description': row[3],
            'is_master': bool(row[4]),
            'created_at': row[5],
        })
    
    logger.debug(f"Found {len(scenarios)} scenarios for network {network_id}")
    return scenarios


def get_scenario(conn: sqlite3.Connection, scenario_id: int) -> dict:
    """
    Get a specific scenario by ID.
    
    Args:
        conn: Database connection
        scenario_id: ID of the scenario
        
    Returns:
        Scenario dictionary with keys: id, network_id, name, description, is_master, created_at
        
    Raises:
        ValidationError: If scenario not found
        DatabaseError: If query fails
    """
    
    cursor = conn.execute(
        "SELECT id, network_id, name, description, is_master, created_at "
        "FROM scenarios "
        "WHERE id = ?",
        (scenario_id,)
    )
    
    row = cursor.fetchone()
    if not row:
        raise ValidationError(f"Scenario with ID {scenario_id} not found")
    
    return {
        'id': row[0],
        'network_id': row[1],
        'name': row[2],
        'description': row[3],
        'is_master': bool(row[4]),
        'created_at': row[5],
    }


def delete_scenario(conn: sqlite3.Connection, scenario_id: int) -> None:
    """
    Delete a scenario (cannot delete master scenarios).
    
    Args:
        conn: Database connection
        scenario_id: ID of the scenario to delete
        
    Raises:
        ValidationError: If scenario not found or is master scenario
        DatabaseError: If deletion fails
    """
    
    # Check if scenario exists and is not master
    cursor = conn.execute(
        "SELECT is_master FROM scenarios WHERE id = ?",
        (scenario_id,)
    )
    
    row = cursor.fetchone()
    if not row:
        raise ValidationError(f"Scenario with ID {scenario_id} not found")
    
    if row[0]:  # is_master
        raise ValidationError("Cannot delete master scenario")
    
    # Delete the scenario (this will cascade to delete related component attributes)
    cursor = conn.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
    
    if cursor.rowcount == 0:
        raise DatabaseError("Failed to delete scenario")
    
    logger.info(f"Deleted scenario {scenario_id}")
