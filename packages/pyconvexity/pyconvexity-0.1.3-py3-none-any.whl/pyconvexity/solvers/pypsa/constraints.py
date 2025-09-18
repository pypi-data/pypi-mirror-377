"""
Constraint application functionality for PyPSA networks.

Handles loading and applying custom constraints from the database.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List

from pyconvexity.models import list_components_by_type, get_attribute

logger = logging.getLogger(__name__)


class ConstraintApplicator:
    """
    Handles loading and applying custom constraints to PyPSA networks.
    
    This class manages both pre-optimization constraints (applied to network structure)
    and optimization-time constraints (applied during solving via extra_functionality).
    """
    
    def apply_constraints(
        self,
        conn,
        network_id: int,
        network: 'pypsa.Network',
        scenario_id: Optional[int] = None,
        constraints_dsl: Optional[str] = None
    ):
        """
        Apply all constraints to the network.
        
        Args:
            conn: Database connection
            network_id: ID of the network
            network: PyPSA Network object
            scenario_id: Optional scenario ID
            constraints_dsl: Optional DSL constraints string
        """
        # Apply database constraints
        self._apply_database_constraints(conn, network_id, network, scenario_id)
        
        # Apply DSL constraints if provided
        if constraints_dsl:
            self._apply_dsl_constraints(network, constraints_dsl)
    
    def _apply_database_constraints(
        self,
        conn,
        network_id: int,
        network: 'pypsa.Network',
        scenario_id: Optional[int]
    ):
        """Load and apply custom constraints from the database in priority order."""
        try:
            # Load all constraints for this network
            constraints = list_components_by_type(conn, network_id, 'CONSTRAINT')
            
            if not constraints:
                return
            
            # Load constraint attributes and filter active ones
            active_constraints = []
            for constraint in constraints:
                try:
                    # Get constraint attributes
                    is_active = get_attribute(conn, constraint.id, 'is_active', scenario_id)
                    priority = get_attribute(conn, constraint.id, 'priority', scenario_id)
                    constraint_code = get_attribute(conn, constraint.id, 'constraint_code', scenario_id)
                    
                    # Check if constraint is active
                    if is_active.variant == "Static":
                        # Extract boolean value from StaticValue
                        is_active_bool = False
                        if "Boolean" in is_active.static_value.data:
                            is_active_bool = is_active.static_value.data["Boolean"]
                        
                        if is_active_bool:
                            # Extract code value first to check if it's an optimization constraint
                            code_val = ""
                            if constraint_code.variant == "Static":
                                if "String" in constraint_code.static_value.data:
                                    code_val = constraint_code.static_value.data["String"]
                            
                            # Skip optimization-time constraints in pre-optimization phase
                            if 'net.model' in code_val or 'network.model' in code_val or 'n.model' in code_val:
                                continue
                            
                            # Extract priority value
                            priority_val = 0
                            if priority.variant == "Static":
                                if "Integer" in priority.static_value.data:
                                    priority_val = priority.static_value.data["Integer"]
                                elif "Float" in priority.static_value.data:
                                    priority_val = int(priority.static_value.data["Float"])
                            
                            active_constraints.append({
                                'id': constraint.id,
                                'name': constraint.name,
                                'priority': priority_val,
                                'code': code_val
                            })
                        
                except Exception as e:
                    logger.warning(f"Failed to load constraint {constraint.name}: {e}")
                    continue
            
            if not active_constraints:
                return
            
            # Sort constraints by priority (lower numbers first)
            active_constraints.sort(key=lambda x: x['priority'])
            
            # Execute constraints in order
            for constraint in active_constraints:
                try:
                    logger.info(f"Executing constraint '{constraint['name']}' (priority {constraint['priority']})")
                    logger.debug(f"Code: {constraint['code']}")
                    
                    # Execute the constraint code in the normal Python environment
                    # The network object 'n' is available in the global scope
                    exec_globals = {
                        'n': network,
                        'pd': pd,
                        'np': np,
                    }
                    
                    # Execute the constraint code
                    exec(constraint['code'], exec_globals)
                    
                except Exception as e:
                    error_msg = f"Failed to execute constraint '{constraint['name']}': {e}"
                    logger.error(error_msg, exc_info=True)
                    # Continue with other constraints instead of failing the entire solve
                    continue
                
        except Exception as e:
            logger.error(f"Failed to apply custom constraints: {e}", exc_info=True)
    
    def _apply_dsl_constraints(self, network: 'pypsa.Network', constraints_dsl: str):
        """
        Apply DSL constraints to the network.
        
        Args:
            network: PyPSA Network object
            constraints_dsl: DSL constraints string
        """
        try:
            logger.info("Applying DSL constraints")
            logger.debug(f"DSL Code: {constraints_dsl}")
            
            # Execute DSL constraints
            exec_globals = {
                'n': network,
                'network': network,
                'pd': pd,
                'np': np,
            }
            
            exec(constraints_dsl, exec_globals)
            
        except Exception as e:
            logger.error(f"Failed to apply DSL constraints: {e}", exc_info=True)
    
    def get_optimization_constraints(
        self,
        conn,
        network_id: int,
        scenario_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get constraints that need to be applied during optimization (via extra_functionality).
        
        Args:
            conn: Database connection
            network_id: ID of the network
            scenario_id: Optional scenario ID
            
        Returns:
            List of optimization constraints
        """
        try:
            # Load all constraints for this network
            constraints = list_components_by_type(conn, network_id, 'CONSTRAINT')
            
            if not constraints:
                return []
            
            # Load constraint attributes and filter active optimization-time ones
            optimization_constraints = []
            for constraint in constraints:
                try:
                    # Get constraint attributes
                    is_active = get_attribute(conn, constraint.id, 'is_active', scenario_id)
                    priority = get_attribute(conn, constraint.id, 'priority', scenario_id)
                    constraint_code = get_attribute(conn, constraint.id, 'constraint_code', scenario_id)
                    
                    # Check if constraint is active
                    if is_active.variant == "Static":
                        # Extract boolean value from StaticValue
                        is_active_bool = False
                        if "Boolean" in is_active.static_value.data:
                            is_active_bool = is_active.static_value.data["Boolean"]
                        
                        if is_active_bool:
                            # Extract code value
                            code_val = ""
                            if constraint_code.variant == "Static":
                                if "String" in constraint_code.static_value.data:
                                    code_val = constraint_code.static_value.data["String"]
                            
                            # Check if this is an optimization-time constraint
                            # (contains model access patterns like 'net.model' or 'network.model')
                            if 'net.model' in code_val or 'network.model' in code_val or 'n.model' in code_val:
                                # Extract priority value
                                priority_val = 0
                                if priority.variant == "Static":
                                    if "Integer" in priority.static_value.data:
                                        priority_val = priority.static_value.data["Integer"]
                                    elif "Float" in priority.static_value.data:
                                        priority_val = int(priority.static_value.data["Float"])
                                
                                optimization_constraints.append({
                                    'id': constraint.id,
                                    'name': constraint.name,
                                    'priority': priority_val,
                                    'code': code_val
                                })
                        
                except Exception as e:
                    logger.warning(f"Failed to load optimization constraint {constraint.name}: {e}")
                    continue
            
            # Sort constraints by priority (lower numbers first)
            optimization_constraints.sort(key=lambda x: x['priority'])
            return optimization_constraints
            
        except Exception as e:
            logger.error(f"Failed to get optimization constraints: {e}", exc_info=True)
            return []
    
    def apply_optimization_constraints(
        self,
        network: 'pypsa.Network',
        snapshots,
        constraints: List[Dict[str, Any]]
    ):
        """
        Apply constraints during optimization (called via extra_functionality).
        
        Args:
            network: PyPSA Network object
            snapshots: Network snapshots
            constraints: List of constraint dictionaries
        """
        try:
            for constraint in constraints:
                try:
                    logger.info(f"Applying optimization constraint '{constraint['name']}' (priority {constraint['priority']})")
                    logger.debug(f"Code: {constraint['code']}")
                    
                    # Execute the constraint code with network and snapshots available
                    exec_globals = {
                        'net': network,
                        'network': network,
                        'n': network,
                        'snapshots': snapshots,
                        'pd': pd,
                        'np': np,
                    }
                    
                    # Execute the constraint code
                    exec(constraint['code'], exec_globals)
                    
                except Exception as e:
                    error_msg = f"Failed to execute optimization constraint '{constraint['name']}': {e}"
                    logger.error(error_msg, exc_info=True)
                    # Continue with other constraints instead of failing the entire solve
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to apply optimization constraints: {e}", exc_info=True)
    
    def apply_optimization_constraint(
        self,
        network: 'pypsa.Network',
        snapshots,
        constraint: Dict[str, Any]
    ):
        """
        Apply a single optimization constraint during solve.
        
        Args:
            network: PyPSA Network object
            snapshots: Network snapshots
            constraint: Single constraint dictionary
        """
        try:
            logger.info(f"Applying optimization constraint '{constraint.get('name', 'unknown')}' (priority {constraint.get('priority', 0)})")
            logger.debug(f"Code: {constraint.get('code', '')}")
            
            # Execute the constraint code with network and snapshots available
            exec_globals = {
                'net': network,
                'network': network,
                'n': network,
                'snapshots': snapshots,
                'pd': pd,
                'np': np,
            }
            
            # Execute the constraint code
            exec(constraint.get('code', ''), exec_globals)
            
        except Exception as e:
            error_msg = f"Failed to execute optimization constraint '{constraint.get('name', 'unknown')}': {e}"
            logger.error(error_msg, exc_info=True)
            raise  # Re-raise so solver can handle it