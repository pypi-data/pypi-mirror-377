"""
Result storage functionality for PyPSA solver integration.

Handles storing solve results back to the database with proper validation and error handling.
"""

import logging
import uuid
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Callable

from pyconvexity.core.types import StaticValue, TimeseriesPoint
from pyconvexity.models import (
    list_components_by_type, set_static_attribute, set_timeseries_attribute
)
from pyconvexity.validation import get_validation_rule

logger = logging.getLogger(__name__)


class ResultStorage:
    """
    Handles storing PyPSA solve results back to the database.
    
    This class manages the complex process of extracting results from PyPSA networks
    and storing them back to the database with proper validation and error handling.
    """
    
    def store_results(
        self,
        conn,
        network_id: int,
        network: 'pypsa.Network',
        solve_result: Dict[str, Any],
        scenario_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Store complete solve results back to database.
        
        Args:
            conn: Database connection
            network_id: ID of the network
            network: Solved PyPSA Network object
            solve_result: Solve result metadata
            scenario_id: Optional scenario ID
            
        Returns:
            Dictionary with storage statistics
        """
        run_id = solve_result.get('run_id', str(uuid.uuid4()))
        
        try:
            # Store component results
            component_stats = self._store_component_results(
                conn, network_id, network, scenario_id
            )
            
            # Calculate network statistics first
            network_stats = self._calculate_network_statistics(
                conn, network_id, network, solve_result
            )
            
            # Store solve summary with network statistics
            self._store_solve_summary(
                conn, network_id, solve_result, scenario_id, network_stats
            )
            
            # Store year-based statistics if available
            year_stats_stored = 0
            if solve_result.get('year_statistics'):
                year_stats_stored = self._store_year_based_statistics(
                    conn, network_id, network, solve_result['year_statistics'], scenario_id
                )
            
            return {
                "component_stats": component_stats,
                "network_stats": network_stats,
                "year_stats_stored": year_stats_stored,
                "run_id": run_id,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Failed to store solve results: {e}", exc_info=True)
            return {
                "component_stats": {},
                "network_stats": {},
                "run_id": run_id,
                "success": False,
                "error": str(e)
            }
    
    def _store_component_results(
        self,
        conn,
        network_id: int,
        network: 'pypsa.Network',
        scenario_id: Optional[int]
    ) -> Dict[str, int]:
        """Store results for all component types."""
        results_stats = {
            "stored_bus_results": 0,
            "stored_generator_results": 0,
            "stored_unmet_load_results": 0,
            "stored_load_results": 0,
            "stored_line_results": 0,
            "stored_link_results": 0,
            "stored_storage_unit_results": 0,
            "stored_store_results": 0,
            "skipped_attributes": 0,
            "errors": 0
        }
        
        try:
            # Store bus results
            if hasattr(network, 'buses_t') and network.buses_t:
                results_stats["stored_bus_results"] = self._store_component_type_results(
                    conn, network_id, 'BUS', network.buses, network.buses_t, scenario_id
                )
            
            # Store generator results (includes regular generators)
            if hasattr(network, 'generators_t') and network.generators_t:
                results_stats["stored_generator_results"] = self._store_component_type_results(
                    conn, network_id, 'GENERATOR', network.generators, network.generators_t, scenario_id
                )
                
                # Store UNMET_LOAD results (these are also stored as generators in PyPSA)
                results_stats["stored_unmet_load_results"] = self._store_component_type_results(
                    conn, network_id, 'UNMET_LOAD', network.generators, network.generators_t, scenario_id
                )
            
            # Store load results
            if hasattr(network, 'loads_t') and network.loads_t:
                results_stats["stored_load_results"] = self._store_component_type_results(
                    conn, network_id, 'LOAD', network.loads, network.loads_t, scenario_id
                )
            
            # Store line results
            if hasattr(network, 'lines_t') and network.lines_t:
                results_stats["stored_line_results"] = self._store_component_type_results(
                    conn, network_id, 'LINE', network.lines, network.lines_t, scenario_id
                )
            
            # Store link results
            if hasattr(network, 'links_t') and network.links_t:
                results_stats["stored_link_results"] = self._store_component_type_results(
                    conn, network_id, 'LINK', network.links, network.links_t, scenario_id
                )
            
            # Store storage unit results
            if hasattr(network, 'storage_units_t') and network.storage_units_t:
                results_stats["stored_storage_unit_results"] = self._store_component_type_results(
                    conn, network_id, 'STORAGE_UNIT', network.storage_units, network.storage_units_t, scenario_id
                )
            
            # Store store results
            if hasattr(network, 'stores_t') and network.stores_t:
                results_stats["stored_store_results"] = self._store_component_type_results(
                    conn, network_id, 'STORE', network.stores, network.stores_t, scenario_id
                )
            
            return results_stats
            
        except Exception as e:
            logger.error(f"Error storing solve results: {e}", exc_info=True)
            results_stats["errors"] += 1
            return results_stats
    
    def _store_component_type_results(
        self,
        conn,
        network_id: int,
        component_type: str,
        static_df: pd.DataFrame,
        timeseries_dict: Dict[str, pd.DataFrame],
        scenario_id: Optional[int]
    ) -> int:
        """Store results for a specific component type - only store OUTPUT attributes."""
        stored_count = 0
        
        try:
            # Get component name to ID mapping
            components = list_components_by_type(conn, network_id, component_type)
            name_to_id = {comp.name: comp.id for comp in components}
            
            # Store timeseries results - ONLY OUTPUT ATTRIBUTES (is_input=FALSE)
            for attr_name, timeseries_df in timeseries_dict.items():
                if timeseries_df.empty:
                    continue
                
                # Check if this attribute is an output attribute (not an input)
                try:
                    rule = get_validation_rule(conn, component_type, attr_name)
                    if rule.is_input:
                        # Skip input attributes to preserve original input data
                        continue
                except Exception:
                    # If no validation rule found, skip to be safe
                    continue
                
                for component_name in timeseries_df.columns:
                    if component_name not in name_to_id:
                        continue
                    
                    component_id = name_to_id[component_name]
                    component_series = timeseries_df[component_name]
                    
                    # Skip if all values are NaN
                    if component_series.isna().all():
                        continue
                    
                    # Convert to TimeseriesPoint list
                    timeseries_points = []
                    for period_index, (timestamp_idx, value) in enumerate(component_series.items()):
                        if pd.isna(value):
                            continue
                        
                        timestamp = int(timestamp_idx.timestamp()) if hasattr(timestamp_idx, 'timestamp') else period_index
                        timeseries_points.append(TimeseriesPoint(
                            timestamp=timestamp,
                            value=float(value),
                            period_index=period_index
                        ))
                    
                    if not timeseries_points:
                        continue
                    
                    # Store using atomic utility
                    try:
                        set_timeseries_attribute(conn, component_id, attr_name, timeseries_points, scenario_id)
                        stored_count += 1
                    except Exception as e:
                        # Handle validation errors gracefully
                        if ("No validation rule found" in str(e) or 
                            "does not allow" in str(e) or
                            "ValidationError" in str(type(e).__name__)):
                            continue
                        else:
                            logger.warning(f"Error storing timeseries {attr_name} for {component_type} '{component_name}': {e}")
                            continue
            
            # Store static optimization results - ONLY OUTPUT ATTRIBUTES (is_input=FALSE)
            if not static_df.empty:
                for attr_name in static_df.columns:
                    # Check if this attribute is an output attribute (not an input)
                    try:
                        rule = get_validation_rule(conn, component_type, attr_name)
                        if rule.is_input:
                            # Skip input attributes to preserve original input data
                            continue
                    except Exception:
                        # If no validation rule found, skip to be safe
                        continue
                    
                    for component_name, value in static_df[attr_name].items():
                        if component_name not in name_to_id or pd.isna(value):
                            continue
                        
                        component_id = name_to_id[component_name]
                        
                        try:
                            # Convert value to StaticValue
                            if isinstance(value, (int, np.integer)):
                                static_value = StaticValue(int(value))
                            elif isinstance(value, (float, np.floating)):
                                if np.isfinite(value):
                                    static_value = StaticValue(float(value))
                                else:
                                    continue  # Skip infinite/NaN values
                            elif isinstance(value, bool):
                                static_value = StaticValue(bool(value))
                            else:
                                static_value = StaticValue(str(value))
                            
                            # Store using atomic utility
                            set_static_attribute(conn, component_id, attr_name, static_value, scenario_id)
                            stored_count += 1
                            
                        except Exception as e:
                            # Handle validation errors gracefully
                            if ("No validation rule found" in str(e) or 
                                "does not allow" in str(e) or
                                "ValidationError" in str(type(e).__name__)):
                                continue
                            else:
                                logger.warning(f"Error storing static {attr_name} for {component_type} '{component_name}': {e}")
                                continue
            
            return stored_count
            
        except Exception as e:
            logger.error(f"Error storing results for {component_type}: {e}", exc_info=True)
            return stored_count
    
    def _store_solve_summary(
        self,
        conn,
        network_id: int,
        solve_result: Dict[str, Any],
        scenario_id: Optional[int],
        network_stats: Optional[Dict[str, Any]] = None
    ):
        """Store solve summary to network_solve_results table."""
        try:
            # Prepare solve summary data
            solver_name = solve_result.get('solver_name', 'unknown')
            solve_status = solve_result.get('status', 'unknown')
            objective_value = solve_result.get('objective_value')
            solve_time = solve_result.get('solve_time', 0.0)
            
            # Use master scenario if no scenario specified
            if scenario_id is None:
                from pyconvexity.models import get_master_scenario_id
                scenario_id = get_master_scenario_id(conn, network_id)
            
            # Create enhanced solve result with network statistics for serialization
            enhanced_solve_result = {
                **solve_result,
                "network_statistics": network_stats or {}
            }
            
            # Store solve results summary
            conn.execute("""
                INSERT OR REPLACE INTO network_solve_results (
                    network_id, scenario_id, solver_name, solve_type, solve_status,
                    objective_value, solve_time_seconds, results_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                network_id,
                scenario_id,
                solver_name,
                'pypsa_optimization',
                solve_status,
                objective_value,
                solve_time,
                self._serialize_results_json(enhanced_solve_result),
                self._serialize_metadata_json(enhanced_solve_result)
            ))
            
            logger.info(f"Stored solve summary for network {network_id}, scenario {scenario_id}")
            
        except Exception as e:
            logger.error(f"Failed to store solve summary: {e}", exc_info=True)
    
    def _calculate_network_statistics(
        self,
        conn,
        network_id: int,
        network: 'pypsa.Network',
        solve_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate network statistics in the format expected by the frontend."""
        try:
            # Calculate basic statistics
            total_generation_mwh = 0.0
            total_load_mwh = 0.0
            unmet_load_mwh = 0.0
            
            # Calculate generation statistics (simple sum of all positive generator output)
            if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                gen_data = network.generators_t.p
                if not gen_data.empty:
                    # Debug: Log what's in the generators DataFrame
                    logger.info(f"Generators DataFrame columns: {list(gen_data.columns)}")
                    logger.info(f"Generators DataFrame shape: {gen_data.shape}")
                    
                    # Total generation - only count positive generation (ignore negative values like storage charging)
                    # CRITICAL: Apply snapshot weightings to convert MW to MWh
                    weightings = network.snapshot_weightings
                    if isinstance(weightings, pd.DataFrame):
                        if 'objective' in weightings.columns:
                            weighting_values = weightings['objective'].values
                        else:
                            weighting_values = weightings.iloc[:, 0].values
                    else:
                        weighting_values = weightings.values
                    
                    # Apply weightings and clip to positive values
                    total_generation_mwh = float((gen_data.clip(lower=0).values * weighting_values[:, None]).sum())
                    
                    # Debug logging
                    raw_sum = gen_data.sum().sum()
                    clipped_sum = gen_data.clip(lower=0).sum().sum()
                    
                    logger.info(f"Generation calculation: raw_sum={raw_sum}, clipped_sum={clipped_sum}")
                    
                    # Check for negative generator values
                    negative_gen_columns = []
                    for col in gen_data.columns:
                        if (gen_data[col] < 0).any():
                            negative_gen_columns.append(col)
                            min_val = gen_data[col].min()
                            logger.warning(f"Generator column '{col}' has negative values (min: {min_val})")
                    
                    if negative_gen_columns:
                        logger.info(f"Found {len(negative_gen_columns)} generator columns with negative values: {negative_gen_columns}")
                    
                    # Calculate unmet load if component type mapping available
                    if hasattr(network, '_component_type_map'):
                        unmet_load_total = 0.0
                        for gen_name, gen_type in network._component_type_map.items():
                            if gen_type == 'UNMET_LOAD' and gen_name in gen_data.columns:
                                # Unmet load should be positive (it's generation to meet unserved demand)
                                unmet_load_total += max(0, gen_data[gen_name].sum())
                        unmet_load_mwh = float(unmet_load_total)
            
            # Calculate load statistics
            if hasattr(network, 'loads_t') and hasattr(network.loads_t, 'p'):
                load_data = network.loads_t.p
                if not load_data.empty:
                    # Debug: Log what's in the loads DataFrame
                    logger.info(f"Loads DataFrame columns: {list(load_data.columns)}")
                    logger.info(f"Loads DataFrame shape: {load_data.shape}")
                    logger.info(f"Sample loads data (first 5 columns): {load_data.iloc[:3, :5].to_dict()}")
                    
                    # CRITICAL: Apply snapshot weightings to convert MW to MWh
                    weightings = network.snapshot_weightings
                    if isinstance(weightings, pd.DataFrame):
                        if 'objective' in weightings.columns:
                            weighting_values = weightings['objective'].values
                        else:
                            weighting_values = weightings.iloc[:, 0].values
                    else:
                        weighting_values = weightings.values
                    
                    total_load_mwh = float(abs((load_data.values * weighting_values[:, None]).sum()))
                    logger.info(f"Total load calculation with weightings: {total_load_mwh} MWh")
                    logger.info(f"Total load calculation without weightings: {abs(load_data.sum().sum())} MW")
                    
                    # Check if any columns have negative values (which shouldn't be in loads)
                    negative_columns = []
                    for col in load_data.columns:
                        if (load_data[col] < 0).any():
                            negative_columns.append(col)
                            min_val = load_data[col].min()
                            logger.warning(f"Load column '{col}' has negative values (min: {min_val})")
                    
                    if negative_columns:
                        logger.error(f"Found {len(negative_columns)} load columns with negative values: {negative_columns}")
                else:
                    total_load_mwh = 0.0
            
            # Calculate transmission losses from links (CORRECTED)
            total_link_losses_mwh = 0.0
            total_link_flow_mwh = 0.0
            if hasattr(network, 'links_t') and hasattr(network.links_t, 'p0'):
                link_p0_data = network.links_t.p0  # Power at bus0
                link_p1_data = network.links_t.p1  # Power at bus1
                
                if not link_p0_data.empty and not link_p1_data.empty:
                    logger.info(f"Links p0 DataFrame columns: {list(link_p0_data.columns)}")
                    logger.info(f"Links p0 DataFrame shape: {link_p0_data.shape}")
                    logger.info(f"Links p1 DataFrame columns: {list(link_p1_data.columns)}")
                    logger.info(f"Links p1 DataFrame shape: {link_p1_data.shape}")
                    
                    # CORRECT calculation: For each link and timestep, calculate losses properly
                    # Losses occur when power flows through a link with efficiency < 1.0
                    # p1 = p0 * efficiency, so losses = p0 - p1 = p0 * (1 - efficiency)
                    
                    link_losses_by_link = {}
                    total_losses = 0.0
                    total_flow = 0.0
                    
                    for link_name in link_p0_data.columns:
                        p0_series = link_p0_data[link_name]  # Power input to link
                        p1_series = link_p1_data[link_name]  # Power output from link
                        
                        # Calculate losses for this link across all timesteps
                        # Losses should always be positive regardless of flow direction
                        # For each timestep: losses = abs(p0) * (1 - efficiency)
                        # But we don't have efficiency here, so use: losses = abs(p0) - abs(p1)
                        
                        # Calculate losses properly for each timestep
                        timestep_losses = abs(p0_series) - abs(p1_series)
                        link_losses = timestep_losses.sum()
                        link_flow = abs(p0_series).sum()  # Total absolute flow through this link
                        
                        link_losses_by_link[link_name] = {
                            'losses_mwh': link_losses,
                            'flow_mwh': link_flow,
                            'loss_rate': (link_losses / link_flow * 100) if link_flow > 0 else 0
                        }
                        
                        total_losses += link_losses
                        total_flow += link_flow
                        
                        # Log details for first few links
                        if len(link_losses_by_link) <= 5:
                            avg_p0 = p0_series.mean()
                            avg_p1 = p1_series.mean()
                            logger.info(f"  Link '{link_name}': avg_p0={avg_p0:.1f}MW, avg_p1={avg_p1:.1f}MW, losses={link_losses:.1f}MWh, flow={link_flow:.1f}MWh")
                    
                    total_link_losses_mwh = total_losses
                    total_link_flow_mwh = total_flow
                    
                    # Summary statistics
                    logger.info(f"Link transmission analysis:")
                    logger.info(f"  Total link flow: {total_link_flow_mwh:.1f} MWh")
                    logger.info(f"  Total link losses: {total_link_losses_mwh:.1f} MWh")
                    logger.info(f"  Average loss rate: {(total_link_losses_mwh/total_link_flow_mwh*100):.2f}%")
                    logger.info(f"  Number of links: {len(link_losses_by_link)}")
                    
                    # Show top 5 links by losses
                    top_loss_links = sorted(link_losses_by_link.items(), key=lambda x: x[1]['losses_mwh'], reverse=True)[:5]
                    logger.info(f"  Top 5 links by losses:")
                    for link_name, stats in top_loss_links:
                        logger.info(f"    {link_name}: {stats['losses_mwh']:.1f} MWh ({stats['loss_rate']:.2f}%)")
            
            # Calculate storage losses if any
            total_storage_losses_mwh = 0.0
            storage_charging_mwh = 0.0
            storage_discharging_mwh = 0.0
            
            # Check for storage units
            if hasattr(network, 'storage_units_t') and hasattr(network.storage_units_t, 'p'):
                storage_data = network.storage_units_t.p
                if not storage_data.empty:
                    logger.info(f"Storage units DataFrame columns: {list(storage_data.columns)}")
                    logger.info(f"Storage units DataFrame shape: {storage_data.shape}")
                    
                    # Storage: positive = discharge (generation), negative = charge (consumption)
                    total_storage_power = storage_data.sum().sum()
                    storage_discharging_mwh = storage_data.clip(lower=0).sum().sum()  # Positive values
                    storage_charging_mwh = abs(storage_data.clip(upper=0).sum().sum())  # Negative values made positive
                    
                    logger.info(f"Storage analysis:")
                    logger.info(f"  Total storage net: {total_storage_power:.1f} MWh")
                    logger.info(f"  Storage discharging: {storage_discharging_mwh:.1f} MWh")
                    logger.info(f"  Storage charging: {storage_charging_mwh:.1f} MWh")
                    
                    # Storage losses = charging - discharging (due to round-trip efficiency)
                    total_storage_losses_mwh = storage_charging_mwh - storage_discharging_mwh
                    if total_storage_losses_mwh < 0:
                        logger.warning(f"Negative storage losses: {total_storage_losses_mwh:.1f} MWh (net discharge)")
                        total_storage_losses_mwh = 0.0  # Don't count net discharge as negative loss
            
            # Check for other PyPSA components that might consume energy
            other_consumption_mwh = 0.0
            
            # Check stores
            if hasattr(network, 'stores_t') and hasattr(network.stores_t, 'p'):
                stores_data = network.stores_t.p
                if not stores_data.empty:
                    stores_consumption = abs(stores_data.sum().sum())
                    other_consumption_mwh += stores_consumption
                    logger.info(f"Stores consumption: {stores_consumption:.1f} MWh")
            
            # Total consumption (link losses already accounted for in PyPSA generation)
            total_consumption_with_losses_mwh = (total_load_mwh + total_storage_losses_mwh + other_consumption_mwh)
            
            # Detailed energy balance analysis
            logger.info(f"=== DETAILED ENERGY BALANCE ANALYSIS ===")
            logger.info(f"GENERATION SIDE:")
            logger.info(f"  Total generation: {total_generation_mwh:.1f} MWh")
            logger.info(f"  Storage discharging: {storage_discharging_mwh:.1f} MWh")
            logger.info(f"  Total supply: {total_generation_mwh + storage_discharging_mwh:.1f} MWh")
            logger.info(f"")
            logger.info(f"CONSUMPTION SIDE:")
            logger.info(f"  Load demand: {total_load_mwh:.1f} MWh")
            logger.info(f"  Storage charging: {storage_charging_mwh:.1f} MWh")
            logger.info(f"  Link losses: {total_link_losses_mwh:.1f} MWh (for info only - already in generation)")
            logger.info(f"  Storage losses: {total_storage_losses_mwh:.1f} MWh")
            logger.info(f"  Other consumption: {other_consumption_mwh:.1f} MWh")
            logger.info(f"  Total consumption: {total_load_mwh + storage_charging_mwh + total_storage_losses_mwh + other_consumption_mwh:.1f} MWh")
            logger.info(f"")
            logger.info(f"BALANCE CHECK:")
            total_supply = total_generation_mwh + storage_discharging_mwh
            total_consumption = total_load_mwh + storage_charging_mwh + total_storage_losses_mwh + other_consumption_mwh
            balance_error = total_supply - total_consumption
            logger.info(f"  Supply - Consumption = {balance_error:.1f} MWh")
            logger.info(f"  Balance error %: {(balance_error/total_supply*100):.3f}%")
            logger.info(f"=========================================")
            
            # Calculate carrier-specific statistics first
            carrier_stats = self._calculate_carrier_statistics(conn, network_id, network)
            
            # Calculate totals from carrier statistics
            total_capital_cost = sum(carrier_stats["capital_cost_by_carrier"].values())
            total_operational_cost = sum(carrier_stats["operational_cost_by_carrier"].values())
            total_emissions = sum(carrier_stats["emissions_by_carrier"].values())
            
            # Calculate derived statistics
            total_cost = solve_result.get('objective_value', 0.0)
            unmet_load_percentage = (unmet_load_mwh / total_load_mwh * 100) if total_load_mwh > 0 else 0.0
            load_factor = (total_generation_mwh / total_load_mwh) if total_load_mwh > 0 else 0.0
            
            logger.info(f"Cost breakdown: Capital=${total_capital_cost:.0f}, Operational=${total_operational_cost:.0f}, Total Objective=${total_cost:.0f}")
            
            # Create nested structure expected by frontend
            network_statistics = {
                "core_summary": {
                    "total_generation_mwh": total_generation_mwh,
                    "total_demand_mwh": total_load_mwh,  # Frontend expects "demand" not "load"
                    "total_cost": total_cost,
                    "load_factor": load_factor,
                    "unserved_energy_mwh": unmet_load_mwh
                },
                "custom_statistics": {
                    # Include carrier-specific statistics
                    **carrier_stats,
                    "total_capital_cost": total_capital_cost,  # Sum from carriers
                    "total_operational_cost": total_operational_cost,  # Sum from carriers  
                    "total_currency_cost": total_cost,  # PyPSA objective (discounted total)
                    "total_emissions_tons_co2": total_emissions,  # Sum from carriers
                    "average_price_per_mwh": (total_cost / total_generation_mwh) if total_generation_mwh > 0 else 0.0,
                    "unmet_load_percentage": unmet_load_percentage,
                    "max_unmet_load_hour_mw": 0.0  # TODO: Calculate max hourly unmet load
                },
                "runtime_info": {
                    "component_count": (
                        len(network.buses) + len(network.generators) + len(network.loads) + 
                        len(network.lines) + len(network.links)
                    ) if hasattr(network, 'buses') else 0,
                    "bus_count": len(network.buses) if hasattr(network, 'buses') else 0,
                    "generator_count": len(network.generators) if hasattr(network, 'generators') else 0,
                    "load_count": len(network.loads) if hasattr(network, 'loads') else 0,
                    "snapshot_count": len(network.snapshots) if hasattr(network, 'snapshots') else 0
                }
            }
            
            logger.info(f"Calculated network statistics: core_summary={network_statistics['core_summary']}")
            logger.info(f"Calculated custom statistics: custom_statistics={network_statistics['custom_statistics']}")
            return network_statistics
            
        except Exception as e:
            logger.error(f"Failed to calculate network statistics: {e}", exc_info=True)
            # Return empty structure matching expected format
            return {
                "core_summary": {
                    "total_generation_mwh": 0.0,
                    "total_demand_mwh": 0.0,
                    "total_cost": solve_result.get('objective_value', 0.0),
                    "load_factor": 0.0,
                    "unserved_energy_mwh": 0.0
                },
                "custom_statistics": {
                    "total_capital_cost": 0.0,
                    "total_operational_cost": 0.0,
                    "total_currency_cost": 0.0,
                    "total_emissions_tons_co2": 0.0,
                    "average_price_per_mwh": 0.0,
                    "unmet_load_percentage": 0.0,
                    "max_unmet_load_hour_mw": 0.0
                },
                "runtime_info": {
                    "component_count": 0,
                    "bus_count": 0,
                    "generator_count": 0,
                    "load_count": 0,
                    "snapshot_count": 0
                },
                "error": str(e)
            }
    
    def _serialize_results_json(self, solve_result: Dict[str, Any]) -> str:
        """Serialize solve results to JSON string."""
        import json
        try:
            # Create a clean results dictionary
            results = {
                "success": solve_result.get("success", False),
                "status": solve_result.get("status", "unknown"),
                "solve_time": solve_result.get("solve_time", 0.0),
                "objective_value": solve_result.get("objective_value"),
                "solver_name": solve_result.get("solver_name", "unknown"),
                "run_id": solve_result.get("run_id"),
                "network_statistics": solve_result.get("network_statistics", {}),
                "pypsa_result": solve_result.get("pypsa_result", {})
            }
            return json.dumps(results, default=self._json_serializer)
        except Exception as e:
            logger.warning(f"Failed to serialize results JSON: {e}")
            return json.dumps({"error": "serialization_failed"})
    
    def _serialize_metadata_json(self, solve_result: Dict[str, Any]) -> str:
        """Serialize solve metadata to JSON string."""
        import json
        try:
            metadata = {
                "solver_name": solve_result.get("solver_name", "unknown"),
                "run_id": solve_result.get("run_id"),
                "multi_period": solve_result.get("multi_period", False),
                "years": solve_result.get("years", []),
                "network_name": solve_result.get("network_name"),
                "num_snapshots": solve_result.get("num_snapshots", 0)
            }
            return json.dumps(metadata, default=self._json_serializer)
        except Exception as e:
            logger.warning(f"Failed to serialize metadata JSON: {e}")
            return json.dumps({"error": "serialization_failed"})
    
    def _calculate_carrier_statistics(self, conn, network_id: int, network: 'pypsa.Network') -> Dict[str, Any]:
        """Calculate carrier-specific statistics that the frontend expects."""
        try:
            # Initialize carrier statistics (separate power and energy capacity like old solver)
            carrier_stats = {
                "dispatch_by_carrier": {},
                "power_capacity_by_carrier": {},  # MW - Generators + Storage Units (power)
                "energy_capacity_by_carrier": {},  # MWh - Stores + Storage Units (energy)
                "emissions_by_carrier": {},
                "capital_cost_by_carrier": {},
                "operational_cost_by_carrier": {},
                "total_system_cost_by_carrier": {}
            }
            
            # Get all carriers from database
            cursor = conn.execute("""
                SELECT DISTINCT name FROM carriers WHERE network_id = ?
            """, (network_id,))
            all_carriers = [row[0] for row in cursor.fetchall()]
            
            # Initialize all carriers with zero values
            for carrier in all_carriers:
                carrier_stats["dispatch_by_carrier"][carrier] = 0.0
                carrier_stats["power_capacity_by_carrier"][carrier] = 0.0
                carrier_stats["energy_capacity_by_carrier"][carrier] = 0.0
                carrier_stats["emissions_by_carrier"][carrier] = 0.0
                carrier_stats["capital_cost_by_carrier"][carrier] = 0.0
                carrier_stats["operational_cost_by_carrier"][carrier] = 0.0
                carrier_stats["total_system_cost_by_carrier"][carrier] = 0.0
            
            # Calculate dispatch by carrier (generation + storage discharge)
            
            # 1. GENERATORS - All generation
            if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                # Get generator-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'GENERATOR'
                """, (network_id,))
                
                generator_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate dispatch for each generator
                for gen_name in network.generators_t.p.columns:
                    if gen_name in generator_carriers:
                        carrier_name = generator_carriers[gen_name]
                        # Apply snapshot weightings to convert MW to MWh
                        weightings = network.snapshot_weightings
                        if isinstance(weightings, pd.DataFrame):
                            if 'objective' in weightings.columns:
                                weighting_values = weightings['objective'].values
                            else:
                                weighting_values = weightings.iloc[:, 0].values
                        else:
                            weighting_values = weightings.values
                        
                        generation_mwh = float((network.generators_t.p[gen_name].values * weighting_values).sum())
                        if carrier_name in carrier_stats["dispatch_by_carrier"]:
                            carrier_stats["dispatch_by_carrier"][carrier_name] += generation_mwh
            
            # 2. STORAGE_UNITS - Discharge only (positive values)
            if hasattr(network, 'storage_units_t') and hasattr(network.storage_units_t, 'p'):
                # Get storage unit-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORAGE_UNIT'
                """, (network_id,))
                
                storage_unit_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate dispatch for each storage unit (discharge only)
                for su_name in network.storage_units_t.p.columns:
                    if su_name in storage_unit_carriers:
                        carrier_name = storage_unit_carriers[su_name]
                        # Apply snapshot weightings and only count positive discharge
                        weightings = network.snapshot_weightings
                        if isinstance(weightings, pd.DataFrame):
                            if 'objective' in weightings.columns:
                                weighting_values = weightings['objective'].values
                            else:
                                weighting_values = weightings.iloc[:, 0].values
                        else:
                            weighting_values = weightings.values
                        
                        # Only count positive values (discharge)
                        su_power = network.storage_units_t.p[su_name]
                        discharge_mwh = float((su_power.clip(lower=0) * weighting_values).sum())
                        
                        if carrier_name in carrier_stats["dispatch_by_carrier"]:
                            carrier_stats["dispatch_by_carrier"][carrier_name] += discharge_mwh
            
            # 3. STORES - Discharge only (positive values)
            if hasattr(network, 'stores_t') and hasattr(network.stores_t, 'p'):
                # Get store-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORE'
                """, (network_id,))
                
                store_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate dispatch for each store (discharge only)
                for store_name in network.stores_t.p.columns:
                    if store_name in store_carriers:
                        carrier_name = store_carriers[store_name]
                        # Apply snapshot weightings and only count positive discharge
                        weightings = network.snapshot_weightings
                        if isinstance(weightings, pd.DataFrame):
                            if 'objective' in weightings.columns:
                                weighting_values = weightings['objective'].values
                            else:
                                weighting_values = weightings.iloc[:, 0].values
                        else:
                            weighting_values = weightings.values
                        
                        # Only count positive values (discharge)
                        store_power = network.stores_t.p[store_name]
                        discharge_mwh = float((store_power.clip(lower=0) * weighting_values).sum())
                        
                        if carrier_name in carrier_stats["dispatch_by_carrier"]:
                            carrier_stats["dispatch_by_carrier"][carrier_name] += discharge_mwh
            
            # Calculate capacity by carrier (power + energy capacity)
            
            # 1. GENERATORS - Power capacity (MW)
            if hasattr(network, 'generators') and not network.generators.empty:
                # Get generator-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'GENERATOR'
                """, (network_id,))
                
                generator_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate capacity for each generator
                for gen_name in network.generators.index:
                    if gen_name in generator_carriers:
                        carrier_name = generator_carriers[gen_name]
                        # Use p_nom_opt if available, otherwise p_nom (POWER capacity)
                        if 'p_nom_opt' in network.generators.columns:
                            capacity_mw = float(network.generators.loc[gen_name, 'p_nom_opt'])
                        else:
                            capacity_mw = float(network.generators.loc[gen_name, 'p_nom']) if 'p_nom' in network.generators.columns else 0.0
                        
                        if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                            carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # 2. STORAGE_UNITS - Power capacity (MW) + Energy capacity (MWh)
            if hasattr(network, 'storage_units') and not network.storage_units.empty:
                # Get storage unit-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORAGE_UNIT'
                """, (network_id,))
                
                storage_unit_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate capacity for each storage unit
                for su_name in network.storage_units.index:
                    if su_name in storage_unit_carriers:
                        carrier_name = storage_unit_carriers[su_name]
                        
                        # Power capacity (MW)
                        if 'p_nom_opt' in network.storage_units.columns:
                            p_nom_opt = float(network.storage_units.loc[su_name, 'p_nom_opt'])
                        else:
                            p_nom_opt = float(network.storage_units.loc[su_name, 'p_nom']) if 'p_nom' in network.storage_units.columns else 0.0
                        
                        if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                            carrier_stats["power_capacity_by_carrier"][carrier_name] += p_nom_opt
                        
                        # Energy capacity (MWh) using max_hours (matching old solver)
                        max_hours = 1.0  # Default from validation data
                        if 'max_hours' in network.storage_units.columns:
                            max_hours = float(network.storage_units.loc[su_name, 'max_hours'])
                        energy_capacity_mwh = p_nom_opt * max_hours
                        
                        if carrier_name in carrier_stats["energy_capacity_by_carrier"]:
                            carrier_stats["energy_capacity_by_carrier"][carrier_name] += energy_capacity_mwh
            
            # 3. STORES - Energy capacity (MWh) only
            if hasattr(network, 'stores') and not network.stores.empty:
                # Get store-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORE'
                """, (network_id,))
                
                store_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate energy capacity for each store
                for store_name in network.stores.index:
                    if store_name in store_carriers:
                        carrier_name = store_carriers[store_name]
                        
                        # Energy capacity (MWh) - stores don't have power capacity, only energy
                        if 'e_nom_opt' in network.stores.columns:
                            e_nom_opt = float(network.stores.loc[store_name, 'e_nom_opt'])
                        else:
                            e_nom_opt = float(network.stores.loc[store_name, 'e_nom']) if 'e_nom' in network.stores.columns else 0.0
                        
                        # Stores contribute only to energy capacity
                        if carrier_name in carrier_stats["energy_capacity_by_carrier"]:
                            carrier_stats["energy_capacity_by_carrier"][carrier_name] += e_nom_opt
            
            # 4. LINES - Apparent power capacity (MVA)
            if hasattr(network, 'lines') and not network.lines.empty:
                # Get line-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINE'
                """, (network_id,))
                
                line_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate capacity for each line
                for line_name in network.lines.index:
                    if line_name in line_carriers:
                        carrier_name = line_carriers[line_name]
                        
                        # Apparent power capacity (MVA) - convert to MW equivalent for consistency
                        if 's_nom_opt' in network.lines.columns:
                            capacity_mva = float(network.lines.loc[line_name, 's_nom_opt'])
                        else:
                            capacity_mva = float(network.lines.loc[line_name, 's_nom']) if 's_nom' in network.lines.columns else 0.0
                        
                        # Convert MVA to MW (assume power factor = 1 for simplicity)
                        capacity_mw = capacity_mva
                        
                        if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                            carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # 5. LINKS - Power capacity (MW)
            if hasattr(network, 'links') and not network.links.empty:
                # Get link-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINK'
                """, (network_id,))
                
                link_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate capacity for each link
                for link_name in network.links.index:
                    if link_name in link_carriers:
                        carrier_name = link_carriers[link_name]
                        
                        # Power capacity (MW)
                        if 'p_nom_opt' in network.links.columns:
                            capacity_mw = float(network.links.loc[link_name, 'p_nom_opt'])
                        else:
                            capacity_mw = float(network.links.loc[link_name, 'p_nom']) if 'p_nom' in network.links.columns else 0.0
                        
                        if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                            carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # Calculate emissions by carrier
            cursor = conn.execute("""
                SELECT name, co2_emissions
                FROM carriers 
                WHERE network_id = ? AND co2_emissions IS NOT NULL
                ORDER BY name
            """, (network_id,))
            
            emission_factors = {}
            for row in cursor.fetchall():
                carrier_name, co2_emissions = row
                emission_factors[carrier_name] = co2_emissions
            
            # Calculate emissions = dispatch * emission_factor
            for carrier, dispatch_mwh in carrier_stats["dispatch_by_carrier"].items():
                emission_factor = emission_factors.get(carrier, 0.0)
                emissions = dispatch_mwh * emission_factor
                carrier_stats["emissions_by_carrier"][carrier] = emissions
            
            # Calculate cost statistics by carrier (all component types)
            
            # 1. GENERATORS - Operational and capital costs
            if hasattr(network, 'generators') and not network.generators.empty:
                # Get generator-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'GENERATOR'
                """, (network_id,))
                
                generator_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate operational costs based on dispatch and marginal costs
                if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                    for gen_name in network.generators.index:
                        if gen_name in generator_carriers and gen_name in network.generators_t.p.columns:
                            carrier_name = generator_carriers[gen_name]
                            
                            # Get marginal cost for this generator
                            marginal_cost = 0.0
                            if 'marginal_cost' in network.generators.columns:
                                marginal_cost = float(network.generators.loc[gen_name, 'marginal_cost'])
                            
                            # Calculate operational cost = dispatch * marginal_cost (with weightings)
                            weightings = network.snapshot_weightings
                            if isinstance(weightings, pd.DataFrame):
                                if 'objective' in weightings.columns:
                                    weighting_values = weightings['objective'].values
                                else:
                                    weighting_values = weightings.iloc[:, 0].values
                            else:
                                weighting_values = weightings.values
                            
                            dispatch_mwh = float((network.generators_t.p[gen_name].values * weighting_values).sum())
                            operational_cost = dispatch_mwh * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                
                # Calculate annual capital costs for all operational generators (matching old solver per-year logic)
                for gen_name in network.generators.index:
                    if gen_name in generator_carriers:
                        carrier_name = generator_carriers[gen_name]
                        
                        # Get capital cost and capacity
                        capital_cost_per_mw = 0.0
                        if 'capital_cost' in network.generators.columns:
                            capital_cost_per_mw = float(network.generators.loc[gen_name, 'capital_cost'])
                        
                        capacity_mw = 0.0
                        if 'p_nom_opt' in network.generators.columns:
                            capacity_mw = float(network.generators.loc[gen_name, 'p_nom_opt'])
                        elif 'p_nom' in network.generators.columns:
                            capacity_mw = float(network.generators.loc[gen_name, 'p_nom'])
                        
                        # Annual capital cost for operational assets (undiscounted)
                        annual_capital_cost = capital_cost_per_mw * capacity_mw
                        
                        if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                            carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
                
                # Calculate operational costs including fixed costs (matching old solver)
                for gen_name in network.generators.index:
                    if gen_name in generator_carriers:
                        carrier_name = generator_carriers[gen_name]
                        
                        # Fixed O&M costs (annual cost per MW of capacity)
                        fixed_cost_per_mw = 0.0
                        if 'fixed_cost' in network.generators.columns:
                            fixed_cost_per_mw = float(network.generators.loc[gen_name, 'fixed_cost'])
                        
                        capacity_mw = 0.0
                        if 'p_nom_opt' in network.generators.columns:
                            capacity_mw = float(network.generators.loc[gen_name, 'p_nom_opt'])
                        elif 'p_nom' in network.generators.columns:
                            capacity_mw = float(network.generators.loc[gen_name, 'p_nom'])
                        
                        fixed_cost_total = fixed_cost_per_mw * capacity_mw
                        
                        if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                            carrier_stats["operational_cost_by_carrier"][carrier_name] += fixed_cost_total
            
            # 2. STORAGE_UNITS - Operational and capital costs
            if hasattr(network, 'storage_units') and not network.storage_units.empty:
                # Get storage unit-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORAGE_UNIT'
                """, (network_id,))
                
                storage_unit_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate operational costs (marginal costs for storage units)
                if hasattr(network, 'storage_units_t') and hasattr(network.storage_units_t, 'p'):
                    for su_name in network.storage_units.index:
                        if su_name in storage_unit_carriers and su_name in network.storage_units_t.p.columns:
                            carrier_name = storage_unit_carriers[su_name]
                            
                            # Get marginal cost for this storage unit
                            marginal_cost = 0.0
                            if 'marginal_cost' in network.storage_units.columns:
                                marginal_cost = float(network.storage_units.loc[su_name, 'marginal_cost'])
                            
                            # Calculate operational cost = dispatch * marginal_cost (discharge only)
                            weightings = network.snapshot_weightings
                            if isinstance(weightings, pd.DataFrame):
                                if 'objective' in weightings.columns:
                                    weighting_values = weightings['objective'].values
                                else:
                                    weighting_values = weightings.iloc[:, 0].values
                            else:
                                weighting_values = weightings.values
                            
                            su_power = network.storage_units_t.p[su_name]
                            discharge_mwh = float((su_power.clip(lower=0) * weighting_values).sum())
                            operational_cost = discharge_mwh * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                
                # Calculate fixed O&M costs for storage units (matching old solver)
                for su_name in network.storage_units.index:
                    if su_name in storage_unit_carriers:
                        carrier_name = storage_unit_carriers[su_name]
                        
                        # Fixed O&M costs (annual cost per MW of capacity)
                        fixed_cost_per_mw = 0.0
                        if 'fixed_cost' in network.storage_units.columns:
                            fixed_cost_per_mw = float(network.storage_units.loc[su_name, 'fixed_cost'])
                        
                        capacity_mw = 0.0
                        if 'p_nom_opt' in network.storage_units.columns:
                            capacity_mw = float(network.storage_units.loc[su_name, 'p_nom_opt'])
                        elif 'p_nom' in network.storage_units.columns:
                            capacity_mw = float(network.storage_units.loc[su_name, 'p_nom'])
                        
                        fixed_cost_total = fixed_cost_per_mw * capacity_mw
                        
                        if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                            carrier_stats["operational_cost_by_carrier"][carrier_name] += fixed_cost_total
                
                # Calculate annual capital costs for all operational storage units
                for su_name in network.storage_units.index:
                    if su_name in storage_unit_carriers:
                        carrier_name = storage_unit_carriers[su_name]
                        
                        # Get capital cost for this storage unit
                        capital_cost_per_mw = 0.0
                        if 'capital_cost' in network.storage_units.columns:
                            capital_cost_per_mw = float(network.storage_units.loc[su_name, 'capital_cost'])
                        
                        # Get capacity
                        capacity_mw = 0.0
                        if 'p_nom_opt' in network.storage_units.columns:
                            capacity_mw = float(network.storage_units.loc[su_name, 'p_nom_opt'])
                        elif 'p_nom' in network.storage_units.columns:
                            capacity_mw = float(network.storage_units.loc[su_name, 'p_nom'])
                        
                        # Annual capital cost for operational assets (undiscounted)
                        annual_capital_cost = capital_cost_per_mw * capacity_mw
                        
                        if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                            carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 3. STORES - Operational and capital costs
            if hasattr(network, 'stores') and not network.stores.empty:
                # Get store-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORE'
                """, (network_id,))
                
                store_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate operational costs (marginal costs for stores)
                if hasattr(network, 'stores_t') and hasattr(network.stores_t, 'p'):
                    for store_name in network.stores.index:
                        if store_name in store_carriers and store_name in network.stores_t.p.columns:
                            carrier_name = store_carriers[store_name]
                            
                            # Get marginal cost for this store
                            marginal_cost = 0.0
                            if 'marginal_cost' in network.stores.columns:
                                marginal_cost = float(network.stores.loc[store_name, 'marginal_cost'])
                            
                            # Calculate operational cost = dispatch * marginal_cost (discharge only)
                            weightings = network.snapshot_weightings
                            if isinstance(weightings, pd.DataFrame):
                                if 'objective' in weightings.columns:
                                    weighting_values = weightings['objective'].values
                                else:
                                    weighting_values = weightings.iloc[:, 0].values
                            else:
                                weighting_values = weightings.values
                            
                            store_power = network.stores_t.p[store_name]
                            discharge_mwh = float((store_power.clip(lower=0) * weighting_values).sum())
                            operational_cost = discharge_mwh * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                
                # Calculate annual capital costs for all operational stores (based on energy capacity)
                for store_name in network.stores.index:
                    if store_name in store_carriers:
                        carrier_name = store_carriers[store_name]
                        
                        # Get capital cost for this store (per MWh)
                        capital_cost_per_mwh = 0.0
                        if 'capital_cost' in network.stores.columns:
                            capital_cost_per_mwh = float(network.stores.loc[store_name, 'capital_cost'])
                        
                        # Get energy capacity
                        energy_capacity_mwh = 0.0
                        if 'e_nom_opt' in network.stores.columns:
                            energy_capacity_mwh = float(network.stores.loc[store_name, 'e_nom_opt'])
                        elif 'e_nom' in network.stores.columns:
                            energy_capacity_mwh = float(network.stores.loc[store_name, 'e_nom'])
                        
                        # Annual capital cost for operational assets (undiscounted)
                        annual_capital_cost = capital_cost_per_mwh * energy_capacity_mwh
                        
                        if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                            carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 4. LINES - Capital costs only (no operational costs for transmission lines)
            if hasattr(network, 'lines') and not network.lines.empty:
                # Get line-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINE'
                """, (network_id,))
                
                line_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate capital costs for lines (based on s_nom_opt capacity)
                for line_name in network.lines.index:
                    if line_name in line_carriers:
                        carrier_name = line_carriers[line_name]
                        
                        # Get capital cost for this line (per MVA)
                        capital_cost_per_mva = 0.0
                        if 'capital_cost' in network.lines.columns:
                            capital_cost_per_mva = float(network.lines.loc[line_name, 'capital_cost'])
                        
                        # Get apparent power capacity (MVA)
                        capacity_mva = 0.0
                        if 's_nom_opt' in network.lines.columns:
                            capacity_mva = float(network.lines.loc[line_name, 's_nom_opt'])
                        elif 's_nom' in network.lines.columns:
                            capacity_mva = float(network.lines.loc[line_name, 's_nom'])
                        
                        # Annual capital cost for operational assets (undiscounted)
                        annual_capital_cost = capacity_mva * capital_cost_per_mva
                        
                        if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                            carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 5. LINKS - Capital and operational costs
            if hasattr(network, 'links') and not network.links.empty:
                # Get link-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINK'
                """, (network_id,))
                
                link_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Calculate operational costs (marginal costs for links)
                if hasattr(network, 'links_t') and hasattr(network.links_t, 'p0'):
                    for link_name in network.links.index:
                        if link_name in link_carriers and link_name in network.links_t.p0.columns:
                            carrier_name = link_carriers[link_name]
                            
                            # Get marginal cost for this link
                            marginal_cost = 0.0
                            if 'marginal_cost' in network.links.columns:
                                marginal_cost = float(network.links.loc[link_name, 'marginal_cost'])
                            
                            # Calculate operational cost = flow * marginal_cost (use absolute flow)
                            weightings = network.snapshot_weightings
                            if isinstance(weightings, pd.DataFrame):
                                if 'objective' in weightings.columns:
                                    weighting_values = weightings['objective'].values
                                else:
                                    weighting_values = weightings.iloc[:, 0].values
                            else:
                                weighting_values = weightings.values
                            
                            # Use absolute flow for cost calculation
                            link_flow = abs(network.links_t.p0[link_name])
                            flow_mwh = float((link_flow * weighting_values).sum())
                            operational_cost = flow_mwh * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                
                # Calculate capital costs for links
                for link_name in network.links.index:
                    if link_name in link_carriers:
                        carrier_name = link_carriers[link_name]
                        
                        # Get capital cost for this link (per MW)
                        capital_cost_per_mw = 0.0
                        if 'capital_cost' in network.links.columns:
                            capital_cost_per_mw = float(network.links.loc[link_name, 'capital_cost'])
                        
                        # Get power capacity (MW)
                        capacity_mw = 0.0
                        if 'p_nom_opt' in network.links.columns:
                            capacity_mw = float(network.links.loc[link_name, 'p_nom_opt'])
                        elif 'p_nom' in network.links.columns:
                            capacity_mw = float(network.links.loc[link_name, 'p_nom'])
                        
                        # Annual capital cost for operational assets (undiscounted)
                        annual_capital_cost = capacity_mw * capital_cost_per_mw
                        
                        if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                            carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # Calculate total system cost = capital + operational
            for carrier in all_carriers:
                capital = carrier_stats["capital_cost_by_carrier"][carrier]
                operational = carrier_stats["operational_cost_by_carrier"][carrier]
                carrier_stats["total_system_cost_by_carrier"][carrier] = capital + operational
            
            logger.info(f"Calculated carrier statistics for {len(all_carriers)} carriers")
            logger.info(f"Total dispatch: {sum(carrier_stats['dispatch_by_carrier'].values()):.2f} MWh")
            logger.info(f"Total power capacity: {sum(carrier_stats['power_capacity_by_carrier'].values()):.2f} MW")
            logger.info(f"Total energy capacity: {sum(carrier_stats['energy_capacity_by_carrier'].values()):.2f} MWh")
            logger.info(f"Total emissions: {sum(carrier_stats['emissions_by_carrier'].values()):.2f} tCO2")
            logger.info(f"Total capital cost: {sum(carrier_stats['capital_cost_by_carrier'].values()):.2f} USD")
            logger.info(f"Total operational cost: {sum(carrier_stats['operational_cost_by_carrier'].values()):.2f} USD")
            logger.info(f"Total system cost: {sum(carrier_stats['total_system_cost_by_carrier'].values()):.2f} USD")
            
            return carrier_stats
            
        except Exception as e:
            logger.error(f"Failed to calculate carrier statistics: {e}", exc_info=True)
            return {
                "dispatch_by_carrier": {},
                "power_capacity_by_carrier": {},
                "energy_capacity_by_carrier": {},
                "emissions_by_carrier": {},
                "capital_cost_by_carrier": {},
                "operational_cost_by_carrier": {},
                "total_system_cost_by_carrier": {}
            }
    
    def _store_year_based_statistics(
        self,
        conn,
        network_id: int,
        network: 'pypsa.Network',
        year_statistics: Dict[int, Dict[str, Any]],
        scenario_id: Optional[int]
    ) -> int:
        """Store year-based statistics to database"""
        try:
            import json
            stored_count = 0
            
            # Use master scenario if no scenario specified
            if scenario_id is None:
                from pyconvexity.models import get_master_scenario_id
                scenario_id = get_master_scenario_id(conn, network_id)
            
            # Check if network_solve_results_by_year table exists, create if not
            conn.execute("""
                CREATE TABLE IF NOT EXISTS network_solve_results_by_year (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    network_id INTEGER NOT NULL,
                    scenario_id INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    results_json TEXT,
                    metadata_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (network_id) REFERENCES networks(id),
                    FOREIGN KEY (scenario_id) REFERENCES scenarios(id),
                    UNIQUE(network_id, scenario_id, year)
                )
            """)
            
            for year, stats in year_statistics.items():
                try:
                    # Calculate proper year-specific carrier statistics
                    year_carrier_stats = self._calculate_year_carrier_statistics(conn, network_id, network, year)
                    
                    # Merge year-specific carrier stats into the statistics
                    if "custom_statistics" in stats:
                        stats["custom_statistics"].update(year_carrier_stats)
                    else:
                        stats["custom_statistics"] = year_carrier_stats
                    
                    # Wrap the year statistics in the same structure as overall results for consistency
                    year_result_wrapper = {
                        "success": True,
                        "year": year,
                        "network_statistics": stats
                    }
                    
                    metadata = {
                        "year": year,
                        "network_id": network_id,
                        "scenario_id": scenario_id
                    }
                    
                    conn.execute("""
                        INSERT OR REPLACE INTO network_solve_results_by_year 
                        (network_id, scenario_id, year, results_json, metadata_json)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        network_id,
                        scenario_id,
                        year,
                        json.dumps(year_result_wrapper, default=self._json_serializer),
                        json.dumps(metadata, default=self._json_serializer)
                    ))
                    
                    stored_count += 1
                    logger.info(f"Stored year-based statistics for year {year}")
                    
                except Exception as e:
                    logger.error(f"Failed to store statistics for year {year}: {e}")
                    continue
            
            logger.info(f"Successfully stored year-based statistics for {stored_count} years")
            return stored_count
            
        except Exception as e:
            logger.error(f"Failed to store year-based statistics: {e}", exc_info=True)
            return 0
    
    def _calculate_year_carrier_statistics(self, conn, network_id: int, network: 'pypsa.Network', year: int) -> Dict[str, Any]:
        """
        Calculate carrier-specific statistics for a specific year with proper database access.
        
        CRITICAL: This method now consistently applies snapshot weightings to ALL energy calculations
        to convert MW to MWh, matching the old PyPSA solver behavior. This is essential for 
        multi-hourly models (e.g., 3-hourly models where each timestep = 3 hours).
        """
        try:
            # Initialize carrier statistics (separate power and energy capacity like old solver)
            carrier_stats = {
                "dispatch_by_carrier": {},
                "power_capacity_by_carrier": {},  # MW - Generators + Storage Units (power)
                "energy_capacity_by_carrier": {},  # MWh - Stores + Storage Units (energy)
                "emissions_by_carrier": {},
                "capital_cost_by_carrier": {},
                "operational_cost_by_carrier": {},
                "total_system_cost_by_carrier": {}
            }
            
            # Get all carriers from database
            cursor = conn.execute("""
                SELECT DISTINCT name FROM carriers WHERE network_id = ?
            """, (network_id,))
            all_carriers = [row[0] for row in cursor.fetchall()]
            
            # Initialize all carriers with zero values
            for carrier in all_carriers:
                carrier_stats["dispatch_by_carrier"][carrier] = 0.0
                carrier_stats["power_capacity_by_carrier"][carrier] = 0.0
                carrier_stats["energy_capacity_by_carrier"][carrier] = 0.0
                carrier_stats["emissions_by_carrier"][carrier] = 0.0
                carrier_stats["capital_cost_by_carrier"][carrier] = 0.0
                carrier_stats["operational_cost_by_carrier"][carrier] = 0.0
                carrier_stats["total_system_cost_by_carrier"][carrier] = 0.0
            
            # Get generator-carrier mapping from database
            cursor = conn.execute("""
                SELECT c.name as component_name, carr.name as carrier_name
                FROM components c
                JOIN carriers carr ON c.carrier_id = carr.id
                WHERE c.network_id = ? AND c.component_type = 'GENERATOR'
            """, (network_id,))
            generator_carriers = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Calculate year-specific dispatch by carrier (all component types)
            
            # 1. GENERATORS - Year-specific generation
            if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                # Filter generation data for this specific year
                year_generation = self._filter_timeseries_by_year(network.generators_t.p, network.snapshots, year)
                if year_generation is not None and not year_generation.empty:
                    for gen_name in year_generation.columns:
                        if gen_name in generator_carriers:
                            carrier_name = generator_carriers[gen_name]
                            # Calculate generation for this year (ALWAYS apply snapshot weightings to convert MW to MWh)
                            year_weightings = self._get_year_weightings(network, year)
                            if year_weightings is not None:
                                generation_mwh = float((year_generation[gen_name].values * year_weightings).sum())
                            else:
                                # Fallback: use all-year weightings if year-specific not available
                                weightings = network.snapshot_weightings
                                if isinstance(weightings, pd.DataFrame):
                                    if 'objective' in weightings.columns:
                                        weighting_values = weightings['objective'].values
                                    else:
                                        weighting_values = weightings.iloc[:, 0].values
                                else:
                                    weighting_values = weightings.values
                                # Apply weightings to the filtered year data
                                if len(weighting_values) == len(year_generation):
                                    generation_mwh = float((year_generation[gen_name].values * weighting_values).sum())
                                else:
                                    # Last resort: simple sum (will be incorrect for non-1H models)
                                    generation_mwh = float(year_generation[gen_name].sum())
                                    logger.warning(f"Could not apply snapshot weightings for {gen_name} in year {year} - energy may be incorrect")
                            
                            if carrier_name in carrier_stats["dispatch_by_carrier"]:
                                carrier_stats["dispatch_by_carrier"][carrier_name] += generation_mwh
            
            # 2. STORAGE_UNITS - Year-specific discharge
            if hasattr(network, 'storage_units_t') and hasattr(network.storage_units_t, 'p'):
                # Get storage unit-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORAGE_UNIT'
                """, (network_id,))
                storage_unit_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Filter storage unit data for this specific year
                year_storage = self._filter_timeseries_by_year(network.storage_units_t.p, network.snapshots, year)
                if year_storage is not None and not year_storage.empty:
                    for su_name in year_storage.columns:
                        if su_name in storage_unit_carriers:
                            carrier_name = storage_unit_carriers[su_name]
                            # Calculate discharge for this year (positive values only, ALWAYS apply snapshot weightings)
                            year_weightings = self._get_year_weightings(network, year)
                            if year_weightings is not None:
                                discharge_mwh = float((year_storage[su_name].clip(lower=0).values * year_weightings).sum())
                            else:
                                # Fallback: use all-year weightings if year-specific not available
                                weightings = network.snapshot_weightings
                                if isinstance(weightings, pd.DataFrame):
                                    if 'objective' in weightings.columns:
                                        weighting_values = weightings['objective'].values
                                    else:
                                        weighting_values = weightings.iloc[:, 0].values
                                else:
                                    weighting_values = weightings.values
                                # Apply weightings to the filtered year data
                                if len(weighting_values) == len(year_storage):
                                    discharge_mwh = float((year_storage[su_name].clip(lower=0).values * weighting_values).sum())
                                else:
                                    discharge_mwh = float(year_storage[su_name].clip(lower=0).sum())
                                    logger.warning(f"Could not apply snapshot weightings for storage unit {su_name} in year {year} - energy may be incorrect")
                            
                            if carrier_name in carrier_stats["dispatch_by_carrier"]:
                                carrier_stats["dispatch_by_carrier"][carrier_name] += discharge_mwh
            
            # 3. STORES - Year-specific discharge
            if hasattr(network, 'stores_t') and hasattr(network.stores_t, 'p'):
                # Get store-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORE'
                """, (network_id,))
                store_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Filter store data for this specific year
                year_stores = self._filter_timeseries_by_year(network.stores_t.p, network.snapshots, year)
                if year_stores is not None and not year_stores.empty:
                    for store_name in year_stores.columns:
                        if store_name in store_carriers:
                            carrier_name = store_carriers[store_name]
                            # Calculate discharge for this year (positive values only, ALWAYS apply snapshot weightings)
                            year_weightings = self._get_year_weightings(network, year)
                            if year_weightings is not None:
                                discharge_mwh = float((year_stores[store_name].clip(lower=0).values * year_weightings).sum())
                            else:
                                # Fallback: use all-year weightings if year-specific not available
                                weightings = network.snapshot_weightings
                                if isinstance(weightings, pd.DataFrame):
                                    if 'objective' in weightings.columns:
                                        weighting_values = weightings['objective'].values
                                    else:
                                        weighting_values = weightings.iloc[:, 0].values
                                else:
                                    weighting_values = weightings.values
                                # Apply weightings to the filtered year data
                                if len(weighting_values) == len(year_stores):
                                    discharge_mwh = float((year_stores[store_name].clip(lower=0).values * weighting_values).sum())
                                else:
                                    discharge_mwh = float(year_stores[store_name].clip(lower=0).sum())
                                    logger.warning(f"Could not apply snapshot weightings for store {store_name} in year {year} - energy may be incorrect")
                            
                            if carrier_name in carrier_stats["dispatch_by_carrier"]:
                                carrier_stats["dispatch_by_carrier"][carrier_name] += discharge_mwh
            
            # Calculate year-specific capacity by carrier (capacity available in this year)
            
            # 1. GENERATORS - Year-specific power capacity
            if hasattr(network, 'generators') and not network.generators.empty:
                for gen_name in network.generators.index:
                    if gen_name in generator_carriers:
                        carrier_name = generator_carriers[gen_name]
                        
                        # Check if this generator is available in this year (build_year <= year)
                        is_available = True
                        if 'build_year' in network.generators.columns:
                            build_year = network.generators.loc[gen_name, 'build_year']
                            if pd.notna(build_year) and int(build_year) > year:
                                is_available = False
                        
                        if is_available:
                            # Use p_nom_opt if available, otherwise p_nom
                            if 'p_nom_opt' in network.generators.columns:
                                capacity_mw = float(network.generators.loc[gen_name, 'p_nom_opt'])
                            else:
                                capacity_mw = float(network.generators.loc[gen_name, 'p_nom']) if 'p_nom' in network.generators.columns else 0.0
                            
                            if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                                carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # 2. STORAGE_UNITS - Year-specific power capacity
            if hasattr(network, 'storage_units') and not network.storage_units.empty:
                # Get storage unit-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORAGE_UNIT'
                """, (network_id,))
                storage_unit_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for su_name in network.storage_units.index:
                    if su_name in storage_unit_carriers:
                        carrier_name = storage_unit_carriers[su_name]
                        
                        # Check if this storage unit is available in this year
                        is_available = True
                        if 'build_year' in network.storage_units.columns:
                            build_year = network.storage_units.loc[su_name, 'build_year']
                            if pd.notna(build_year) and int(build_year) > year:
                                is_available = False
                        
                        if is_available:
                            # Use p_nom_opt if available, otherwise p_nom
                            if 'p_nom_opt' in network.storage_units.columns:
                                capacity_mw = float(network.storage_units.loc[su_name, 'p_nom_opt'])
                            else:
                                capacity_mw = float(network.storage_units.loc[su_name, 'p_nom']) if 'p_nom' in network.storage_units.columns else 0.0
                            
                            if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                                carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # 3. STORES - Year-specific energy capacity
            if hasattr(network, 'stores') and not network.stores.empty:
                # Get store-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORE'
                """, (network_id,))
                store_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for store_name in network.stores.index:
                    if store_name in store_carriers:
                        carrier_name = store_carriers[store_name]
                        
                        # Check if this store is available in this year
                        is_available = True
                        if 'build_year' in network.stores.columns:
                            build_year = network.stores.loc[store_name, 'build_year']
                            if pd.notna(build_year) and int(build_year) > year:
                                is_available = False
                        
                        if is_available:
                            # Use e_nom_opt if available, otherwise e_nom (energy capacity)
                            if 'e_nom_opt' in network.stores.columns:
                                capacity_mwh = float(network.stores.loc[store_name, 'e_nom_opt'])
                            else:
                                capacity_mwh = float(network.stores.loc[store_name, 'e_nom']) if 'e_nom' in network.stores.columns else 0.0
                            
                            # Add to capacity (stores contribute energy capacity to the general "capacity" metric)
                            if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                                carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mwh
            
            # 4. LINES - Year-specific apparent power capacity
            if hasattr(network, 'lines') and not network.lines.empty:
                # Get line-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINE'
                """, (network_id,))
                line_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for line_name in network.lines.index:
                    if line_name in line_carriers:
                        carrier_name = line_carriers[line_name]
                        
                        # Check if this line is available in this year
                        is_available = True
                        if 'build_year' in network.lines.columns:
                            build_year = network.lines.loc[line_name, 'build_year']
                            if pd.notna(build_year) and int(build_year) > year:
                                is_available = False
                        
                        if is_available:
                            # Use s_nom_opt if available, otherwise s_nom (convert MVA to MW)
                            if 's_nom_opt' in network.lines.columns:
                                capacity_mva = float(network.lines.loc[line_name, 's_nom_opt'])
                            else:
                                capacity_mva = float(network.lines.loc[line_name, 's_nom']) if 's_nom' in network.lines.columns else 0.0
                            
                            # Convert MVA to MW (assume power factor = 1)
                            capacity_mw = capacity_mva
                            
                            if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                                carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # 5. LINKS - Year-specific power capacity
            if hasattr(network, 'links') and not network.links.empty:
                # Get link-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINK'
                """, (network_id,))
                link_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for link_name in network.links.index:
                    if link_name in link_carriers:
                        carrier_name = link_carriers[link_name]
                        
                        # Check if this link is available in this year
                        is_available = True
                        if 'build_year' in network.links.columns:
                            build_year = network.links.loc[link_name, 'build_year']
                            if pd.notna(build_year) and int(build_year) > year:
                                is_available = False
                        
                        if is_available:
                            # Use p_nom_opt if available, otherwise p_nom
                            if 'p_nom_opt' in network.links.columns:
                                capacity_mw = float(network.links.loc[link_name, 'p_nom_opt'])
                            else:
                                capacity_mw = float(network.links.loc[link_name, 'p_nom']) if 'p_nom' in network.links.columns else 0.0
                            
                            if carrier_name in carrier_stats["power_capacity_by_carrier"]:
                                carrier_stats["power_capacity_by_carrier"][carrier_name] += capacity_mw
            
            # Calculate year-specific emissions (based on year-specific dispatch)
            cursor = conn.execute("""
                SELECT name, co2_emissions
                FROM carriers 
                WHERE network_id = ? AND co2_emissions IS NOT NULL
                ORDER BY name
            """, (network_id,))
            
            emission_factors = {}
            for row in cursor.fetchall():
                carrier_name, co2_emissions = row
                emission_factors[carrier_name] = co2_emissions
            
            # Calculate emissions = year_dispatch * emission_factor
            for carrier, dispatch_mwh in carrier_stats["dispatch_by_carrier"].items():
                emission_factor = emission_factors.get(carrier, 0.0)
                emissions = dispatch_mwh * emission_factor
                carrier_stats["emissions_by_carrier"][carrier] = emissions
            
            # Calculate year-specific costs (all component types)
            # For multi-period models, costs are complex - capital costs are incurred at build time
            # but operational costs are incurred when generating
            
            # 1. GENERATORS - Year-specific operational and capital costs
            if hasattr(network, 'generators') and not network.generators.empty:
                for gen_name in network.generators.index:
                    if gen_name in generator_carriers:
                        carrier_name = generator_carriers[gen_name]
                        
                        # Operational costs = year_dispatch * marginal_cost
                        if 'marginal_cost' in network.generators.columns:
                            year_dispatch = 0.0
                            if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                                year_generation = self._filter_timeseries_by_year(network.generators_t.p, network.snapshots, year)
                                if year_generation is not None and gen_name in year_generation.columns:
                                    year_weightings = self._get_year_weightings(network, year)
                                    if year_weightings is not None:
                                        year_dispatch = float((year_generation[gen_name].values * year_weightings).sum())
                                    else:
                                        # Fallback: use all-year weightings if year-specific not available
                                        weightings = network.snapshot_weightings
                                        if isinstance(weightings, pd.DataFrame):
                                            if 'objective' in weightings.columns:
                                                weighting_values = weightings['objective'].values
                                            else:
                                                weighting_values = weightings.iloc[:, 0].values
                                        else:
                                            weighting_values = weightings.values
                                        # Apply weightings to the filtered year data
                                        if len(weighting_values) == len(year_generation):
                                            year_dispatch = float((year_generation[gen_name].values * weighting_values).sum())
                                        else:
                                            year_dispatch = float(year_generation[gen_name].sum())
                                            logger.warning(f"Could not apply snapshot weightings for operational cost calc of {gen_name} in year {year} - cost may be incorrect")
                            
                            marginal_cost = float(network.generators.loc[gen_name, 'marginal_cost'])
                            operational_cost = year_dispatch * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                        
                        # Capital costs - include if asset is operational in this year (matching old solver)
                        if 'capital_cost' in network.generators.columns:
                            # Check if this generator is operational in this year
                            is_operational = True
                            if 'build_year' in network.generators.columns:
                                build_year = network.generators.loc[gen_name, 'build_year']
                                if pd.notna(build_year) and int(build_year) > year:
                                    is_operational = False  # Not built yet
                            
                            if is_operational:
                                capital_cost_per_mw = float(network.generators.loc[gen_name, 'capital_cost'])
                                
                                if 'p_nom_opt' in network.generators.columns:
                                    capacity_mw = float(network.generators.loc[gen_name, 'p_nom_opt'])
                                elif 'p_nom' in network.generators.columns:
                                    capacity_mw = float(network.generators.loc[gen_name, 'p_nom'])
                                else:
                                    capacity_mw = 0.0
                                
                                # Annual capital cost for operational assets (undiscounted)
                                annual_capital_cost = capacity_mw * capital_cost_per_mw
                                
                                if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                                    carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 2. STORAGE_UNITS - Year-specific operational and capital costs
            if hasattr(network, 'storage_units') and not network.storage_units.empty:
                # Get storage unit-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORAGE_UNIT'
                """, (network_id,))
                storage_unit_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for su_name in network.storage_units.index:
                    if su_name in storage_unit_carriers:
                        carrier_name = storage_unit_carriers[su_name]
                        
                        # Operational costs = year_discharge * marginal_cost
                        if 'marginal_cost' in network.storage_units.columns:
                            year_discharge = 0.0
                            if hasattr(network, 'storage_units_t') and hasattr(network.storage_units_t, 'p'):
                                year_storage = self._filter_timeseries_by_year(network.storage_units_t.p, network.snapshots, year)
                                if year_storage is not None and su_name in year_storage.columns:
                                    year_weightings = self._get_year_weightings(network, year)
                                    if year_weightings is not None:
                                        year_discharge = float((year_storage[su_name].clip(lower=0).values * year_weightings).sum())
                                    else:
                                        # Fallback: use all-year weightings if year-specific not available
                                        weightings = network.snapshot_weightings
                                        if isinstance(weightings, pd.DataFrame):
                                            if 'objective' in weightings.columns:
                                                weighting_values = weightings['objective'].values
                                            else:
                                                weighting_values = weightings.iloc[:, 0].values
                                        else:
                                            weighting_values = weightings.values
                                        # Apply weightings to the filtered year data
                                        if len(weighting_values) == len(year_storage):
                                            year_discharge = float((year_storage[su_name].clip(lower=0).values * weighting_values).sum())
                                        else:
                                            year_discharge = float(year_storage[su_name].clip(lower=0).sum())
                                            logger.warning(f"Could not apply snapshot weightings for operational cost calc of storage unit {su_name} in year {year} - cost may be incorrect")
                            
                            marginal_cost = float(network.storage_units.loc[su_name, 'marginal_cost'])
                            operational_cost = year_discharge * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                        
                        # Capital costs - include if asset is operational in this year (matching old solver)
                        if 'capital_cost' in network.storage_units.columns:
                            # Check if this storage unit is operational in this year
                            is_operational = True
                            if 'build_year' in network.storage_units.columns:
                                build_year = network.storage_units.loc[su_name, 'build_year']
                                if pd.notna(build_year) and int(build_year) > year:
                                    is_operational = False  # Not built yet
                            
                            if is_operational:
                                capital_cost_per_mw = float(network.storage_units.loc[su_name, 'capital_cost'])
                                
                                if 'p_nom_opt' in network.storage_units.columns:
                                    capacity_mw = float(network.storage_units.loc[su_name, 'p_nom_opt'])
                                elif 'p_nom' in network.storage_units.columns:
                                    capacity_mw = float(network.storage_units.loc[su_name, 'p_nom'])
                                else:
                                    capacity_mw = 0.0
                                
                                # Annual capital cost for operational assets (undiscounted)
                                annual_capital_cost = capacity_mw * capital_cost_per_mw
                                
                                if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                                    carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 3. STORES - Year-specific operational and capital costs
            if hasattr(network, 'stores') and not network.stores.empty:
                # Get store-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'STORE'
                """, (network_id,))
                store_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for store_name in network.stores.index:
                    if store_name in store_carriers:
                        carrier_name = store_carriers[store_name]
                        
                        # Operational costs = year_discharge * marginal_cost
                        if 'marginal_cost' in network.stores.columns:
                            year_discharge = 0.0
                            if hasattr(network, 'stores_t') and hasattr(network.stores_t, 'p'):
                                year_stores = self._filter_timeseries_by_year(network.stores_t.p, network.snapshots, year)
                                if year_stores is not None and store_name in year_stores.columns:
                                    year_weightings = self._get_year_weightings(network, year)
                                    if year_weightings is not None:
                                        year_discharge = float((year_stores[store_name].clip(lower=0).values * year_weightings).sum())
                                    else:
                                        # Fallback: use all-year weightings if year-specific not available
                                        weightings = network.snapshot_weightings
                                        if isinstance(weightings, pd.DataFrame):
                                            if 'objective' in weightings.columns:
                                                weighting_values = weightings['objective'].values
                                            else:
                                                weighting_values = weightings.iloc[:, 0].values
                                        else:
                                            weighting_values = weightings.values
                                        # Apply weightings to the filtered year data
                                        if len(weighting_values) == len(year_stores):
                                            year_discharge = float((year_stores[store_name].clip(lower=0).values * weighting_values).sum())
                                        else:
                                            year_discharge = float(year_stores[store_name].clip(lower=0).sum())
                                            logger.warning(f"Could not apply snapshot weightings for operational cost calc of store {store_name} in year {year} - cost may be incorrect")
                            
                            marginal_cost = float(network.stores.loc[store_name, 'marginal_cost'])
                            operational_cost = year_discharge * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                        
                        # Capital costs - include if asset is operational in this year (matching old solver)
                        if 'capital_cost' in network.stores.columns:
                            # Check if this store is operational in this year
                            is_operational = True
                            if 'build_year' in network.stores.columns:
                                build_year = network.stores.loc[store_name, 'build_year']
                                if pd.notna(build_year) and int(build_year) > year:
                                    is_operational = False  # Not built yet
                            
                            if is_operational:
                                capital_cost_per_mwh = float(network.stores.loc[store_name, 'capital_cost'])
                                
                                if 'e_nom_opt' in network.stores.columns:
                                    capacity_mwh = float(network.stores.loc[store_name, 'e_nom_opt'])
                                elif 'e_nom' in network.stores.columns:
                                    capacity_mwh = float(network.stores.loc[store_name, 'e_nom'])
                                else:
                                    capacity_mwh = 0.0
                                
                                # Annual capital cost for operational assets (undiscounted)
                                annual_capital_cost = capacity_mwh * capital_cost_per_mwh
                                
                                if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                                    carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 4. LINES - Year-specific capital costs (only count if built in this year)
            if hasattr(network, 'lines') and not network.lines.empty:
                # Get line-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINE'
                """, (network_id,))
                line_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                for line_name in network.lines.index:
                    if line_name in line_carriers:
                        carrier_name = line_carriers[line_name]
                        
                        # Capital costs - include if asset is operational in this year (matching old solver)
                        if 'capital_cost' in network.lines.columns:
                            # Check if this line is operational in this year
                            is_operational = True
                            if 'build_year' in network.lines.columns:
                                build_year = network.lines.loc[line_name, 'build_year']
                                if pd.notna(build_year) and int(build_year) > year:
                                    is_operational = False  # Not built yet
                            
                            if is_operational:
                                capital_cost_per_mva = float(network.lines.loc[line_name, 'capital_cost'])
                                
                                if 's_nom_opt' in network.lines.columns:
                                    capacity_mva = float(network.lines.loc[line_name, 's_nom_opt'])
                                elif 's_nom' in network.lines.columns:
                                    capacity_mva = float(network.lines.loc[line_name, 's_nom'])
                                else:
                                    capacity_mva = 0.0
                                
                                # Annual capital cost for operational assets (undiscounted)
                                annual_capital_cost = capacity_mva * capital_cost_per_mva
                                
                                if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                                    carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # 5. LINKS - Year-specific operational and capital costs
            if hasattr(network, 'links') and not network.links.empty:
                # Get link-carrier mapping
                cursor = conn.execute("""
                    SELECT c.name as component_name, carr.name as carrier_name
                    FROM components c
                    JOIN carriers carr ON c.carrier_id = carr.id
                    WHERE c.network_id = ? AND c.component_type = 'LINK'
                """, (network_id,))
                link_carriers = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Operational costs for links (year-specific flow)
                if hasattr(network, 'links_t') and hasattr(network.links_t, 'p0'):
                    for link_name in network.links.index:
                        if link_name in link_carriers:
                            carrier_name = link_carriers[link_name]
                            
                            # Get marginal cost for this link
                            marginal_cost = 0.0
                            if 'marginal_cost' in network.links.columns:
                                marginal_cost = float(network.links.loc[link_name, 'marginal_cost'])
                            
                            # Calculate operational cost = year_flow * marginal_cost
                            year_flow = 0.0
                            if link_name in network.links_t.p0.columns:
                                year_links = self._filter_timeseries_by_year(network.links_t.p0, network.snapshots, year)
                                if year_links is not None and link_name in year_links.columns:
                                    year_weightings = self._get_year_weightings(network, year)
                                    if year_weightings is not None:
                                        year_flow = float((abs(year_links[link_name]).values * year_weightings).sum())
                                    else:
                                        # Fallback: use all-year weightings if year-specific not available
                                        weightings = network.snapshot_weightings
                                        if isinstance(weightings, pd.DataFrame):
                                            if 'objective' in weightings.columns:
                                                weighting_values = weightings['objective'].values
                                            else:
                                                weighting_values = weightings.iloc[:, 0].values
                                        else:
                                            weighting_values = weightings.values
                                        # Apply weightings to the filtered year data
                                        if len(weighting_values) == len(year_links):
                                            year_flow = float((abs(year_links[link_name]).values * weighting_values).sum())
                                        else:
                                            year_flow = float(abs(year_links[link_name]).sum())
                                            logger.warning(f"Could not apply snapshot weightings for operational cost calc of link {link_name} in year {year} - cost may be incorrect")
                            
                            operational_cost = year_flow * marginal_cost
                            
                            if carrier_name in carrier_stats["operational_cost_by_carrier"]:
                                carrier_stats["operational_cost_by_carrier"][carrier_name] += operational_cost
                
                # Capital costs for links - only count if built in this year
                for link_name in network.links.index:
                    if link_name in link_carriers:
                        carrier_name = link_carriers[link_name]
                        
                        # Capital costs - include if asset is operational in this year (matching old solver)
                        if 'capital_cost' in network.links.columns:
                            # Check if this link is operational in this year
                            is_operational = True
                            if 'build_year' in network.links.columns:
                                build_year = network.links.loc[link_name, 'build_year']
                                if pd.notna(build_year) and int(build_year) > year:
                                    is_operational = False  # Not built yet
                            
                            if is_operational:
                                capital_cost_per_mw = float(network.links.loc[link_name, 'capital_cost'])
                                
                                if 'p_nom_opt' in network.links.columns:
                                    capacity_mw = float(network.links.loc[link_name, 'p_nom_opt'])
                                elif 'p_nom' in network.links.columns:
                                    capacity_mw = float(network.links.loc[link_name, 'p_nom'])
                                else:
                                    capacity_mw = 0.0
                                
                                # Annual capital cost for operational assets (undiscounted)
                                annual_capital_cost = capacity_mw * capital_cost_per_mw
                                
                                if carrier_name in carrier_stats["capital_cost_by_carrier"]:
                                    carrier_stats["capital_cost_by_carrier"][carrier_name] += annual_capital_cost
            
            # Calculate total system cost = capital + operational (for this year)
            for carrier in all_carriers:
                capital = carrier_stats["capital_cost_by_carrier"][carrier]
                operational = carrier_stats["operational_cost_by_carrier"][carrier]
                carrier_stats["total_system_cost_by_carrier"][carrier] = capital + operational
            
            logger.info(f"Calculated year {year} carrier statistics:")
            logger.info(f"  Dispatch: {sum(carrier_stats['dispatch_by_carrier'].values()):.2f} MWh")
            logger.info(f"  Power capacity: {sum(carrier_stats['power_capacity_by_carrier'].values()):.2f} MW")
            logger.info(f"  Energy capacity: {sum(carrier_stats['energy_capacity_by_carrier'].values()):.2f} MWh")
            logger.info(f"  Emissions: {sum(carrier_stats['emissions_by_carrier'].values()):.2f} tCO2")
            logger.info(f"  Capital cost: {sum(carrier_stats['capital_cost_by_carrier'].values()):.2f} USD")
            logger.info(f"  Operational cost: {sum(carrier_stats['operational_cost_by_carrier'].values()):.2f} USD")
            
            return carrier_stats
            
        except Exception as e:
            logger.error(f"Failed to calculate year {year} carrier statistics: {e}", exc_info=True)
            return {
                "dispatch_by_carrier": {},
                "power_capacity_by_carrier": {},
                "energy_capacity_by_carrier": {},
                "emissions_by_carrier": {},
                "capital_cost_by_carrier": {},
                "operational_cost_by_carrier": {},
                "total_system_cost_by_carrier": {}
            }
    
    def _filter_timeseries_by_year(self, timeseries_df: 'pd.DataFrame', snapshots: 'pd.Index', year: int) -> 'pd.DataFrame':
        """Filter timeseries data by year - copied from solver for consistency"""
        try:
            
            # Handle MultiIndex case (multi-period optimization)
            if hasattr(snapshots, 'levels'):
                period_values = snapshots.get_level_values(0)
                year_mask = period_values == year
                if year_mask.any():
                    year_snapshots = snapshots[year_mask]
                    return timeseries_df.loc[year_snapshots]
            
            # Handle DatetimeIndex case (regular time series)
            elif hasattr(snapshots, 'year'):
                year_mask = snapshots.year == year
                if year_mask.any():
                    return timeseries_df.loc[year_mask]
            
            # Fallback - return None if can't filter
            return None
            
        except Exception as e:
            logger.error(f"Failed to filter timeseries by year {year}: {e}")
            return None
    
    def _get_year_weightings(self, network: 'pypsa.Network', year: int) -> 'np.ndarray':
        """Get snapshot weightings for a specific year - copied from solver for consistency"""
        try:
            
            # Filter snapshot weightings by year
            if hasattr(network.snapshots, 'levels'):
                period_values = network.snapshots.get_level_values(0)
                year_mask = period_values == year
                if year_mask.any():
                    year_snapshots = network.snapshots[year_mask]
                    year_weightings = network.snapshot_weightings.loc[year_snapshots]
                    if isinstance(year_weightings, pd.DataFrame):
                        if 'objective' in year_weightings.columns:
                            return year_weightings['objective'].values
                        else:
                            return year_weightings.iloc[:, 0].values
                    else:
                        return year_weightings.values
            
            elif hasattr(network.snapshots, 'year'):
                year_mask = network.snapshots.year == year
                if year_mask.any():
                    year_weightings = network.snapshot_weightings.loc[year_mask]
                    if isinstance(year_weightings, pd.DataFrame):
                        if 'objective' in year_weightings.columns:
                            return year_weightings['objective'].values
                        else:
                            return year_weightings.iloc[:, 0].values
                    else:
                        return year_weightings.values
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get year weightings for year {year}: {e}")
            return None
    
    
    def _json_serializer(self, obj):
        """Convert numpy/pandas types to JSON serializable types"""
        import numpy as np
        import pandas as pd
        
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Series):
            return obj.to_dict()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        elif hasattr(obj, 'item'):  # Handle numpy scalars
            return obj.item()
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
