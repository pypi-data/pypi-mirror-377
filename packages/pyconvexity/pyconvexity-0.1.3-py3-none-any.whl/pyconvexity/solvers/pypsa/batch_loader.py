"""
PyPSA Batch Data Loader
Optimized batch loading functions for PyPSA network construction.
Eliminates N+1 query patterns for improved performance.
"""

import logging
import pandas as pd
import json
from typing import Dict, Any, List, Optional

# Import functions directly from pyconvexity
from pyconvexity.models.attributes import deserialize_timeseries_from_parquet

logger = logging.getLogger(__name__)


class PyPSABatchLoader:
    """
    Optimized batch data loader for PyPSA network construction.
    Eliminates N+1 query patterns by loading data in batches.
    """
    
    def __init__(self):
        pass
    
    def batch_load_component_attributes(self, conn, component_ids: List[int], scenario_id: Optional[int]) -> Dict[int, Dict[str, Any]]:
        """Batch load all static attributes for multiple components to avoid N+1 queries"""
        if not component_ids:
            return {}
        
        # Build a single query to get all attributes for all components
        placeholders = ','.join(['?' for _ in component_ids])
        
        # Get all attribute names for all components in one query
        cursor = conn.execute(f"""
            SELECT DISTINCT attribute_name 
            FROM component_attributes 
            WHERE component_id IN ({placeholders}) AND storage_type = 'static'
        """, component_ids)
        all_attribute_names = [row[0] for row in cursor.fetchall()]
        
        if not all_attribute_names:
            return {comp_id: {} for comp_id in component_ids}
        
        # Build query to get all attributes for all components
        attr_placeholders = ','.join(['?' for _ in all_attribute_names])
        
        # Resolve scenario IDs for fallback logic
        scenario_filter_values = []
        master_id = None
        if scenario_id is not None:
            # Get master scenario ID for fallback
            cursor = conn.execute("SELECT id FROM scenarios WHERE network_id = (SELECT network_id FROM components WHERE id = ?) AND is_master = 1", (component_ids[0],))
            result = cursor.fetchone()
            if result:
                master_id = result[0]
                scenario_filter_values = [scenario_id, master_id]
            else:
                scenario_filter_values = [scenario_id]
        else:
            # Get master scenario ID
            cursor = conn.execute("SELECT id FROM scenarios WHERE network_id = (SELECT network_id FROM components WHERE id = ?) AND is_master = 1", (component_ids[0],))
            result = cursor.fetchone()
            if result:
                master_id = result[0]
                scenario_filter_values = [master_id]
            else:
                return {comp_id: {} for comp_id in component_ids}
        
        scen_placeholders = ','.join(['?' for _ in scenario_filter_values])
        
        # Single query to get all attributes
        # CRITICAL: Order by scenario_id DESC to prioritize current scenario over master
        query = f"""
            SELECT component_id, attribute_name, static_value, data_type, scenario_id
            FROM component_attributes 
            WHERE component_id IN ({placeholders}) 
            AND attribute_name IN ({attr_placeholders})
            AND scenario_id IN ({scen_placeholders})
            AND storage_type = 'static'
            ORDER BY component_id, attribute_name, 
                     CASE WHEN scenario_id = ? THEN 0 ELSE 1 END
        """
        
        # Parameters must match the order of placeholders in the query
        query_params = component_ids + all_attribute_names + scenario_filter_values + [scenario_id if scenario_id is not None else master_id]
        
        cursor = conn.execute(query, query_params)
        
        # Group by component_id, preferring current scenario over master
        component_attributes = {}
        for comp_id in component_ids:
            component_attributes[comp_id] = {}
        
        # Process results, preferring current scenario over master
        rows = cursor.fetchall()
        
        for row in rows:
            comp_id, attr_name, static_value_json, data_type, row_scenario_id = row
            
            # Ensure component exists in our dictionary (safety check)
            if comp_id not in component_attributes:
                continue
            
            # Skip if we already have this attribute from a preferred scenario
            if attr_name in component_attributes[comp_id]:
                continue
            
            # Parse JSON value
            json_value = json.loads(static_value_json)
            
            # Convert based on data type
            if data_type == "float":
                value = float(json_value) if isinstance(json_value, (int, float)) else 0.0
            elif data_type == "int":
                value = int(json_value) if isinstance(json_value, (int, float)) else 0
            elif data_type == "boolean":
                value = bool(json_value) if isinstance(json_value, bool) else False
            elif data_type == "string":
                value = str(json_value) if isinstance(json_value, str) else ""
            else:
                value = json_value
            
            component_attributes[comp_id][attr_name] = value
        
        return component_attributes
    
    def batch_load_component_connections(self, conn, network_id: int) -> Dict[str, Dict[str, str]]:
        """Batch load bus and carrier connections to avoid individual lookups"""
        # Get all bus names in one query
        cursor = conn.execute("""
            SELECT id, name FROM components 
            WHERE network_id = ? AND component_type = 'BUS'
        """, (network_id,))
        bus_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Get all carrier names in one query
        cursor = conn.execute("""
            SELECT id, name FROM carriers 
            WHERE network_id = ?
        """, (network_id,))
        carrier_id_to_name = {row[0]: row[1] for row in cursor.fetchall()}
        
        return {
            'bus_id_to_name': bus_id_to_name,
            'carrier_id_to_name': carrier_id_to_name
        }
    
    def batch_load_component_timeseries(self, conn, component_ids: List[int], scenario_id: Optional[int]) -> Dict[int, Dict[str, pd.Series]]:
        """Batch load all timeseries attributes for multiple components to avoid N+1 queries"""
        if not component_ids:
            return {}
        
        # Get network time periods for proper timestamp alignment
        network_time_periods = None
        if component_ids:
            cursor = conn.execute("SELECT network_id FROM components WHERE id = ? LIMIT 1", (component_ids[0],))
            result = cursor.fetchone()
            if result:
                network_id = result[0]
                try:
                    from pyconvexity.models.network import get_network_time_periods
                    network_time_periods = get_network_time_periods(conn, network_id)
                    logger.debug(f"Loaded {len(network_time_periods)} time periods for timeseries alignment")
                except Exception as e:
                    logger.warning(f"Failed to load network time periods: {e}")
        
        # Build a single query to get all timeseries attributes for all components
        placeholders = ','.join(['?' for _ in component_ids])
        
        # Get all attribute names for all components in one query
        cursor = conn.execute(f"""
            SELECT DISTINCT attribute_name 
            FROM component_attributes 
            WHERE component_id IN ({placeholders}) AND storage_type = 'timeseries'
        """, component_ids)
        all_attribute_names = [row[0] for row in cursor.fetchall()]
        
        if not all_attribute_names:
            return {comp_id: {} for comp_id in component_ids}
        
        # Build query to get all timeseries for all components
        attr_placeholders = ','.join(['?' for _ in all_attribute_names])
        
        # Resolve scenario IDs for fallback logic
        scenario_filter_values = []
        master_id = None
        if scenario_id is not None:
            # Get master scenario ID for fallback
            cursor = conn.execute("SELECT id FROM scenarios WHERE network_id = (SELECT network_id FROM components WHERE id = ?) AND is_master = 1", (component_ids[0],))
            result = cursor.fetchone()
            if result:
                master_id = result[0]
                scenario_filter_values = [scenario_id, master_id]
            else:
                scenario_filter_values = [scenario_id]
        else:
            # Get master scenario ID
            cursor = conn.execute("SELECT id FROM scenarios WHERE network_id = (SELECT network_id FROM components WHERE id = ?) AND is_master = 1", (component_ids[0],))
            result = cursor.fetchone()
            if result:
                master_id = result[0]
                scenario_filter_values = [master_id]
            else:
                return {comp_id: {} for comp_id in component_ids}
        
        scen_placeholders = ','.join(['?' for _ in scenario_filter_values])
        
        # Single query to get all timeseries
        # CRITICAL: Order by scenario_id to prioritize current scenario over master
        query = f"""
            SELECT component_id, attribute_name, timeseries_data, scenario_id
            FROM component_attributes 
            WHERE component_id IN ({placeholders}) 
            AND attribute_name IN ({attr_placeholders})
            AND scenario_id IN ({scen_placeholders})
            AND storage_type = 'timeseries'
            ORDER BY component_id, attribute_name, 
                     CASE WHEN scenario_id = ? THEN 0 ELSE 1 END
        """
        
        # Parameters must match the order of placeholders in the query
        query_params = component_ids + all_attribute_names + scenario_filter_values + [scenario_id if scenario_id is not None else master_id]
        
        cursor = conn.execute(query, query_params)
        
        # Group by component_id, preferring current scenario over master
        component_timeseries = {}
        for comp_id in component_ids:
            component_timeseries[comp_id] = {}
        
        # Process results, preferring current scenario over master
        rows = cursor.fetchall()
        
        for row in rows:
            comp_id, attr_name, timeseries_data, row_scenario_id = row
            
            # Ensure component exists in our dictionary (safety check)
            if comp_id not in component_timeseries:
                continue
            
            # Skip if we already have this attribute from a preferred scenario
            if attr_name in component_timeseries[comp_id]:
                continue
            
            # Deserialize timeseries data
            try:
                timeseries_points = deserialize_timeseries_from_parquet(timeseries_data, network_time_periods)
                if timeseries_points:
                    # Create pandas Series from timeseries points
                    # Sort by period_index to ensure correct order
                    timeseries_points.sort(key=lambda x: x.period_index)
                    values = [point.value for point in timeseries_points]
                    
                    # Create proper timestamps for PyPSA alignment
                    if network_time_periods:
                        # Use formatted timestamps from network time periods
                        timestamps = []
                        for point in timeseries_points:
                            if point.period_index < len(network_time_periods):
                                tp = network_time_periods[point.period_index]
                                timestamps.append(pd.Timestamp(tp.formatted_time))
                            else:
                                logger.warning(f"Period index {point.period_index} out of range for network time periods")
                                timestamps.append(pd.Timestamp.now())  # Fallback
                        component_timeseries[comp_id][attr_name] = pd.Series(values, index=timestamps)
                    else:
                        # Fallback: use period_index as index
                        period_indices = [point.period_index for point in timeseries_points]
                        component_timeseries[comp_id][attr_name] = pd.Series(values, index=period_indices)
            except Exception as e:
                logger.warning(f"Failed to deserialize timeseries {attr_name} for component {comp_id}: {e}")
                continue
        
        return component_timeseries
    
    def batch_load_all_component_timeseries_by_type(self, conn, network_id: int, component_type: str, scenario_id: Optional[int]) -> Dict[str, pd.DataFrame]:
        """
        Load all timeseries attributes for a component type and organize by attribute name.
        This is a compatibility method for the existing _load_all_component_timeseries interface.
        """
        from pyconvexity.models import list_components_by_type
        
        components = list_components_by_type(conn, network_id, component_type)
        component_ids = [comp.id for comp in components]
        
        # Use batch loading
        component_timeseries = self.batch_load_component_timeseries(conn, component_ids, scenario_id)
        
        # Reorganize by attribute name (matching original interface)
        timeseries_by_attr = {}
        
        for component in components:
            comp_timeseries = component_timeseries.get(component.id, {})
            
            for attr_name, series in comp_timeseries.items():
                if attr_name not in timeseries_by_attr:
                    timeseries_by_attr[attr_name] = {}
                
                # Store series in dict first
                timeseries_by_attr[attr_name][component.name] = series
        
        # Convert to DataFrames all at once to avoid fragmentation
        for attr_name in timeseries_by_attr:
            if timeseries_by_attr[attr_name]:
                timeseries_by_attr[attr_name] = pd.DataFrame(timeseries_by_attr[attr_name])
            else:
                timeseries_by_attr[attr_name] = pd.DataFrame()
        
        return timeseries_by_attr
