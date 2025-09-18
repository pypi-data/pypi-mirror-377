"""
Model management module for PyConvexity.

Contains high-level operations for networks, components, and attributes.
"""

from pyconvexity.models.components import (
    get_component_type, get_component, list_components_by_type,
    insert_component, create_component, update_component, delete_component,
    list_component_attributes, get_default_carrier_id, get_bus_name_to_id_map
)

from pyconvexity.models.attributes import (
    set_static_attribute, set_timeseries_attribute, get_attribute, delete_attribute
)

from pyconvexity.models.network import (
    create_network, get_network_info, get_network_time_periods, list_networks,
    create_carrier, list_carriers, get_network_config, set_network_config,
    get_component_counts, get_master_scenario_id, resolve_scenario_id
)

from pyconvexity.models.scenarios import (
    create_scenario, list_scenarios, get_scenario, delete_scenario
)

__all__ = [
    # Component operations
    "get_component_type", "get_component", "list_components_by_type",
    "insert_component", "create_component", "update_component", "delete_component",
    "list_component_attributes", "get_default_carrier_id", "get_bus_name_to_id_map",
    
    # Attribute operations
    "set_static_attribute", "set_timeseries_attribute", "get_attribute", "delete_attribute",
    
    # Network operations
    "create_network", "get_network_info", "get_network_time_periods", "list_networks",
    "create_carrier", "list_carriers", "get_network_config", "set_network_config",
    "get_component_counts", "get_master_scenario_id", "resolve_scenario_id",
    
    # Scenario operations
    "create_scenario", "list_scenarios", "get_scenario", "delete_scenario",
]
