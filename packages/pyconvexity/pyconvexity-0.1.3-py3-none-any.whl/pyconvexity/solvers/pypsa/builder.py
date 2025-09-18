"""
Network building functionality for PyPSA solver integration.

Handles loading data from database and constructing PyPSA Network objects.
"""

import logging
import pandas as pd
from typing import Dict, Any, Optional, Callable

from pyconvexity.models import (
    list_components_by_type, get_network_time_periods, get_network_config
)

logger = logging.getLogger(__name__)


class NetworkBuilder:
    """
    Builds PyPSA networks from database data.
    
    This class handles the complex process of loading network components,
    attributes, and time series data from the database and constructing
    a properly configured PyPSA Network object.
    """
    
    def __init__(self):
        # Import PyPSA with error handling
        try:
            import pypsa
            self.pypsa = pypsa
        except ImportError as e:
            raise ImportError(
                "PyPSA is not installed or could not be imported. "
                "Please ensure it is installed correctly in the environment."
            ) from e
        
        # Import batch loader for efficient data loading
        try:
            from pyconvexity.solvers.pypsa.batch_loader import PyPSABatchLoader
            self.batch_loader = PyPSABatchLoader()
        except ImportError:
            # Fallback to individual loading if batch loader not available
            self.batch_loader = None
            logger.warning("PyPSABatchLoader not available, using individual component loading")
    
    def build_network(
        self, 
        conn, 
        network_id: int, 
        scenario_id: Optional[int] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> 'pypsa.Network':
        """
        Build complete PyPSA network from database.
        
        Args:
            conn: Database connection
            network_id: ID of network to build
            scenario_id: Optional scenario ID
            progress_callback: Optional progress callback
            
        Returns:
            Configured PyPSA Network object
        """
        if progress_callback:
            progress_callback(0, "Loading network metadata...")
        
        # Load network info
        network_info = self._load_network_info(conn, network_id)
        
        if progress_callback:
            progress_callback(5, f"Building network: {network_info['name']}")
        
        # Create PyPSA network
        network = self.pypsa.Network(name=network_info['name'])
        
        # Set time index
        self._set_time_index(conn, network_id, network)
        
        if progress_callback:
            progress_callback(15, "Loading carriers...")
        
        # Load carriers
        self._load_carriers(conn, network_id, network)
        
        if progress_callback:
            progress_callback(20, "Loading components...")
        
        # Load all components
        self._load_components(conn, network_id, network, scenario_id, progress_callback)
        
        # NOTE: Snapshot weightings will be set AFTER multi-period optimization setup
        # in the solver, not here. This matches the old code's approach where PyPSA's
        # multi-period setup can reset snapshot weightings to 1.0
        
        if progress_callback:
            progress_callback(95, "Network build complete")
        
        return network
    
    def load_network_data(
        self, 
        conn, 
        network_id: int, 
        scenario_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Load network data as structured dictionary without building PyPSA network.
        
        Args:
            conn: Database connection
            network_id: ID of network to load
            scenario_id: Optional scenario ID
            
        Returns:
            Dictionary with all network data
        """
        data = {
            "network_info": self._load_network_info(conn, network_id),
            "carriers": self._load_carriers_data(conn, network_id),
            "components": {},
            "time_periods": []
        }
        
        # Load time periods
        try:
            time_periods = get_network_time_periods(conn, network_id)
            data["time_periods"] = [
                {
                    "timestamp": tp.formatted_time,
                    "period_index": tp.period_index,
                    "weight": tp.weight
                }
                for tp in time_periods
            ]
        except Exception as e:
            logger.warning(f"Failed to load time periods: {e}")
        
        # Load all component types
        component_types = ['BUS', 'GENERATOR', 'UNMET_LOAD', 'LOAD', 'LINE', 'LINK', 'STORAGE_UNIT', 'STORE']
        
        for comp_type in component_types:
            try:
                components = list_components_by_type(conn, network_id, comp_type)
                if components:
                    data["components"][comp_type.lower()] = [
                        {
                            "id": comp.id,
                            "name": comp.name,
                            "component_type": comp.component_type,
                            "longitude": comp.longitude,
                            "latitude": comp.latitude,
                            "carrier_id": comp.carrier_id,
                            "bus_id": comp.bus_id,
                            "bus0_id": comp.bus0_id,
                            "bus1_id": comp.bus1_id
                        }
                        for comp in components
                    ]
            except Exception as e:
                logger.warning(f"Failed to load {comp_type} components: {e}")
        
        return data
    
    def _load_network_info(self, conn, network_id: int) -> Dict[str, Any]:
        """Load network metadata."""
        cursor = conn.execute("""
            SELECT name, description, time_start, time_end, time_interval
            FROM networks 
            WHERE id = ?
        """, (network_id,))
        
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Network with ID {network_id} not found")
        
        return {
            'name': row[0],
            'description': row[1],
            'time_start': row[2],
            'time_end': row[3],
            'time_interval': row[4]
        }
    
    def _set_time_index(self, conn, network_id: int, network: 'pypsa.Network'):
        """Set time index from network time periods."""
        try:
            time_periods = get_network_time_periods(conn, network_id)
            if time_periods:
                # Convert to pandas DatetimeIndex
                timestamps = [pd.Timestamp(tp.formatted_time) for tp in time_periods]
                
                # Set the snapshots to the timestamps
                network.set_snapshots(timestamps)
                
                # Extract years for year-based statistics
                try:
                    if hasattr(network.snapshots, 'year'):
                        years = sorted(network.snapshots.year.unique())
                        network._available_years = years
                        logger.info(f"Extracted {len(years)} years from network.snapshots.year: {years}")
                    else:
                        # Manually extract years from timestamps
                        years_from_timestamps = sorted(list(set([ts.year for ts in timestamps])))
                        network._available_years = years_from_timestamps
                        logger.info(f"Extracted {len(years_from_timestamps)} years from timestamps: {years_from_timestamps}")
                        
                except Exception as year_error:
                    logger.warning(f"Failed to extract years for year-based statistics: {year_error}")
                    network._available_years = []
                    
            else:
                logger.warning("No time periods found for network, year-based statistics will not be available")
                network._available_years = []
        except Exception as e:
            logger.error(f"Failed to set time index: {e}")
            network._available_years = []
    
    def _load_carriers(self, conn, network_id: int, network: 'pypsa.Network'):
        """Load carriers into PyPSA network."""
        carriers = self._load_carriers_data(conn, network_id)
        for carrier in carriers:
            filtered_attrs = self._filter_carrier_attrs(carrier)
            network.add("Carrier", carrier['name'], **filtered_attrs)
    
    def _load_carriers_data(self, conn, network_id: int) -> list:
        """Load carrier data from database."""
        cursor = conn.execute("""
            SELECT name, co2_emissions, nice_name, color
            FROM carriers 
            WHERE network_id = ?
            ORDER BY name
        """, (network_id,))
        
        carriers = []
        for row in cursor.fetchall():
            carriers.append({
                'name': row[0],
                'co2_emissions': row[1],
                'nice_name': row[2],
                'color': row[3]
            })
        
        return carriers
    
    def _filter_carrier_attrs(self, carrier: Dict[str, Any]) -> Dict[str, Any]:
        """Filter carrier attributes for PyPSA compatibility."""
        filtered = {}
        for key, value in carrier.items():
            if key != 'name' and value is not None:
                filtered[key] = value
        return filtered
    
    def _load_components(
        self, 
        conn, 
        network_id: int, 
        network: 'pypsa.Network', 
        scenario_id: Optional[int],
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """Load all network components."""
        # Load component connections if batch loader available
        if self.batch_loader:
            connections = self.batch_loader.batch_load_component_connections(conn, network_id)
            bus_id_to_name = connections['bus_id_to_name']
            carrier_id_to_name = connections['carrier_id_to_name']
        else:
            bus_id_to_name = self._build_bus_id_to_name_map(conn, network_id)
            carrier_id_to_name = self._build_carrier_id_to_name_map(conn, network_id)
        
        # Component type mapping for later identification
        component_type_map = {}
        
        # Load buses
        if progress_callback:
            progress_callback(25, "Loading buses...")
        self._load_buses(conn, network_id, network, scenario_id, component_type_map)
        
        # Load generators (including unmet loads)
        if progress_callback:
            progress_callback(35, "Loading generators...")
        self._load_generators(conn, network_id, network, scenario_id, bus_id_to_name, carrier_id_to_name, component_type_map)
        
        # Load loads
        if progress_callback:
            progress_callback(50, "Loading loads...")
        self._load_loads(conn, network_id, network, scenario_id, bus_id_to_name, carrier_id_to_name)
        
        # Load lines
        if progress_callback:
            progress_callback(65, "Loading lines...")
        self._load_lines(conn, network_id, network, scenario_id, bus_id_to_name, carrier_id_to_name)
        
        # Load links
        if progress_callback:
            progress_callback(75, "Loading links...")
        self._load_links(conn, network_id, network, scenario_id, bus_id_to_name, carrier_id_to_name)
        
        # Load storage units
        if progress_callback:
            progress_callback(85, "Loading storage...")
        self._load_storage_units(conn, network_id, network, scenario_id, bus_id_to_name, carrier_id_to_name)
        self._load_stores(conn, network_id, network, scenario_id, bus_id_to_name, carrier_id_to_name)
        
        # Store component type mapping on network
        network._component_type_map = component_type_map
    
    def _load_buses(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int], component_type_map: Dict[str, str]):
        """Load bus components."""
        buses = list_components_by_type(conn, network_id, 'BUS')
        bus_ids = [bus.id for bus in buses]
        
        if self.batch_loader:
            bus_attributes = self.batch_loader.batch_load_component_attributes(conn, bus_ids, scenario_id)
            bus_timeseries = self.batch_loader.batch_load_component_timeseries(conn, bus_ids, scenario_id)
        else:
            bus_attributes = self._load_component_attributes_individually(conn, bus_ids, scenario_id)
            bus_timeseries = {}
        
        for bus in buses:
            attrs = bus_attributes.get(bus.id, {})
            timeseries = bus_timeseries.get(bus.id, {})
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            network.add("Bus", bus.name, **attrs)
            component_type_map[bus.name] = bus.component_type
    
    def _load_generators(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int], 
                        bus_id_to_name: Dict[int, str], carrier_id_to_name: Dict[int, str], component_type_map: Dict[str, str]):
        """Load generator and unmet load components."""
        generators = list_components_by_type(conn, network_id, 'GENERATOR')
        unmet_loads = list_components_by_type(conn, network_id, 'UNMET_LOAD')
        all_generators = generators + unmet_loads
        
        generator_ids = [gen.id for gen in all_generators]
        
        if self.batch_loader:
            generator_attributes = self.batch_loader.batch_load_component_attributes(conn, generator_ids, scenario_id)
            generator_timeseries = self.batch_loader.batch_load_component_timeseries(conn, generator_ids, scenario_id)
        else:
            generator_attributes = self._load_component_attributes_individually(conn, generator_ids, scenario_id)
            generator_timeseries = {}
        
        for gen in all_generators:
            attrs = generator_attributes.get(gen.id, {})
            timeseries = generator_timeseries.get(gen.id, {})
            
            # Set bus connection
            if gen.bus_id:
                bus_name = bus_id_to_name.get(gen.bus_id, f"bus_{gen.bus_id}")
                attrs['bus'] = bus_name
            
            # Set carrier
            if gen.carrier_id:
                carrier_name = carrier_id_to_name.get(gen.carrier_id, '-')
                attrs['carrier'] = carrier_name
            else:
                attrs['carrier'] = '-'
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            component_type_map[gen.name] = gen.component_type
            network.add("Generator", gen.name, **attrs)
    
    def _load_loads(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int],
                   bus_id_to_name: Dict[int, str], carrier_id_to_name: Dict[int, str]):
        """Load load components."""
        loads = list_components_by_type(conn, network_id, 'LOAD')
        load_ids = [load.id for load in loads]
        
        if self.batch_loader:
            load_attributes = self.batch_loader.batch_load_component_attributes(conn, load_ids, scenario_id)
            load_timeseries = self.batch_loader.batch_load_component_timeseries(conn, load_ids, scenario_id)
        else:
            load_attributes = self._load_component_attributes_individually(conn, load_ids, scenario_id)
            load_timeseries = {}
        
        for load in loads:
            attrs = load_attributes.get(load.id, {})
            timeseries = load_timeseries.get(load.id, {})
            
            if load.bus_id:
                bus_name = bus_id_to_name.get(load.bus_id, f"bus_{load.bus_id}")
                attrs['bus'] = bus_name
            
            if load.carrier_id:
                carrier_name = carrier_id_to_name.get(load.carrier_id, '-')
                attrs['carrier'] = carrier_name
            else:
                attrs['carrier'] = '-'
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            network.add("Load", load.name, **attrs)
    
    def _load_lines(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int],
                   bus_id_to_name: Dict[int, str], carrier_id_to_name: Dict[int, str]):
        """Load line components."""
        lines = list_components_by_type(conn, network_id, 'LINE')
        line_ids = [line.id for line in lines]
        
        if self.batch_loader:
            line_attributes = self.batch_loader.batch_load_component_attributes(conn, line_ids, scenario_id)
            line_timeseries = self.batch_loader.batch_load_component_timeseries(conn, line_ids, scenario_id)
        else:
            line_attributes = self._load_component_attributes_individually(conn, line_ids, scenario_id)
            line_timeseries = {}
        
        for line in lines:
            attrs = line_attributes.get(line.id, {})
            timeseries = line_timeseries.get(line.id, {})
            
            if line.bus0_id and line.bus1_id:
                bus0_name = bus_id_to_name.get(line.bus0_id, f"bus_{line.bus0_id}")
                bus1_name = bus_id_to_name.get(line.bus1_id, f"bus_{line.bus1_id}")
                attrs['bus0'] = bus0_name
                attrs['bus1'] = bus1_name
            
            if line.carrier_id:
                carrier_name = carrier_id_to_name.get(line.carrier_id, 'AC')
                attrs['carrier'] = carrier_name
            else:
                attrs['carrier'] = 'AC'
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            network.add("Line", line.name, **attrs)
    
    def _load_links(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int],
                   bus_id_to_name: Dict[int, str], carrier_id_to_name: Dict[int, str]):
        """Load link components."""
        links = list_components_by_type(conn, network_id, 'LINK')
        link_ids = [link.id for link in links]
        
        if self.batch_loader:
            link_attributes = self.batch_loader.batch_load_component_attributes(conn, link_ids, scenario_id)
            link_timeseries = self.batch_loader.batch_load_component_timeseries(conn, link_ids, scenario_id)
        else:
            link_attributes = self._load_component_attributes_individually(conn, link_ids, scenario_id)
            link_timeseries = {}
        
        for link in links:
            attrs = link_attributes.get(link.id, {})
            timeseries = link_timeseries.get(link.id, {})
            
            if link.bus0_id and link.bus1_id:
                bus0_name = bus_id_to_name.get(link.bus0_id, f"bus_{link.bus0_id}")
                bus1_name = bus_id_to_name.get(link.bus1_id, f"bus_{link.bus1_id}")
                attrs['bus0'] = bus0_name
                attrs['bus1'] = bus1_name
            
            if link.carrier_id:
                carrier_name = carrier_id_to_name.get(link.carrier_id, 'DC')
                attrs['carrier'] = carrier_name
            else:
                attrs['carrier'] = 'DC'
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            network.add("Link", link.name, **attrs)
    
    def _load_storage_units(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int],
                           bus_id_to_name: Dict[int, str], carrier_id_to_name: Dict[int, str]):
        """Load storage unit components."""
        storage_units = list_components_by_type(conn, network_id, 'STORAGE_UNIT')
        storage_ids = [storage.id for storage in storage_units]
        
        if self.batch_loader:
            storage_attributes = self.batch_loader.batch_load_component_attributes(conn, storage_ids, scenario_id)
            storage_timeseries = self.batch_loader.batch_load_component_timeseries(conn, storage_ids, scenario_id)
        else:
            storage_attributes = self._load_component_attributes_individually(conn, storage_ids, scenario_id)
            storage_timeseries = {}
        
        for storage in storage_units:
            attrs = storage_attributes.get(storage.id, {})
            timeseries = storage_timeseries.get(storage.id, {})
            
            if storage.bus_id:
                bus_name = bus_id_to_name.get(storage.bus_id, f"bus_{storage.bus_id}")
                attrs['bus'] = bus_name
            
            if storage.carrier_id:
                carrier_name = carrier_id_to_name.get(storage.carrier_id, '-')
                attrs['carrier'] = carrier_name
            else:
                attrs['carrier'] = '-'
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            network.add("StorageUnit", storage.name, **attrs)
    
    def _load_stores(self, conn, network_id: int, network: 'pypsa.Network', scenario_id: Optional[int],
                    bus_id_to_name: Dict[int, str], carrier_id_to_name: Dict[int, str]):
        """Load store components."""
        stores = list_components_by_type(conn, network_id, 'STORE')
        store_ids = [store.id for store in stores]
        
        if self.batch_loader:
            store_attributes = self.batch_loader.batch_load_component_attributes(conn, store_ids, scenario_id)
            store_timeseries = self.batch_loader.batch_load_component_timeseries(conn, store_ids, scenario_id)
        else:
            store_attributes = self._load_component_attributes_individually(conn, store_ids, scenario_id)
            store_timeseries = {}
        
        for store in stores:
            attrs = store_attributes.get(store.id, {})
            timeseries = store_timeseries.get(store.id, {})
            
            if store.bus_id:
                bus_name = bus_id_to_name.get(store.bus_id, f"bus_{store.bus_id}")
                attrs['bus'] = bus_name
            
            if store.carrier_id:
                carrier_name = carrier_id_to_name.get(store.carrier_id, '-')
                attrs['carrier'] = carrier_name
            else:
                attrs['carrier'] = '-'
            
            # Merge timeseries into attributes
            attrs.update(timeseries)
            
            network.add("Store", store.name, **attrs)
    
    def _set_snapshot_weightings(self, conn, network_id: int, network: 'pypsa.Network'):
        """Set snapshot weightings from time periods."""
        try:
            time_periods = get_network_time_periods(conn, network_id)
            if time_periods and len(network.snapshots) > 0:
                # Create weightings array
                weightings = []
                for tp in time_periods:
                    if tp.weight is not None:
                        weightings.append(tp.weight)
                    else:
                        # Calculate from time interval if weight not specified
                        network_config = get_network_config(conn, network_id)
                        time_interval = network_config.get('time_interval', '1H')
                        weight = self._parse_time_interval(time_interval)
                        weightings.append(weight if weight else 1.0)
                
                if len(weightings) == len(network.snapshots):
                    # Set all three columns like the old code - critical for proper objective calculation
                    network.snapshot_weightings.loc[:, 'objective'] = weightings
                    network.snapshot_weightings.loc[:, 'generators'] = weightings  
                    network.snapshot_weightings.loc[:, 'stores'] = weightings
                    logger.info(f"Set snapshot weightings for {len(weightings)} time periods (objective, generators, stores)")
                else:
                    logger.warning(f"Mismatch between weightings ({len(weightings)}) and snapshots ({len(network.snapshots)})")
        except Exception as e:
            logger.warning(f"Failed to set snapshot weightings: {e}")
    
    def _parse_time_interval(self, time_interval: str) -> Optional[float]:
        """Parse time interval string to hours."""
        if not time_interval:
            return None
        
        try:
            # Handle pandas frequency strings
            if time_interval.endswith('H'):
                return float(time_interval[:-1])
            elif time_interval.endswith('D'):
                return float(time_interval[:-1]) * 24
            elif time_interval.endswith('M'):
                return float(time_interval[:-1]) / 60
            elif time_interval.endswith('S'):
                return float(time_interval[:-1]) / 3600
            else:
                # Try to parse as float (assume hours)
                return float(time_interval)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse time interval: {time_interval}")
            return None
    
    def _build_bus_id_to_name_map(self, conn, network_id: int) -> Dict[int, str]:
        """Build mapping from bus IDs to names."""
        buses = list_components_by_type(conn, network_id, 'BUS')
        return {bus.id: bus.name for bus in buses}
    
    def _build_carrier_id_to_name_map(self, conn, network_id: int) -> Dict[int, str]:
        """Build mapping from carrier IDs to names."""
        cursor = conn.execute("SELECT id, name FROM carriers WHERE network_id = ?", (network_id,))
        return {row[0]: row[1] for row in cursor.fetchall()}
    
    def _load_component_attributes_individually(self, conn, component_ids: list, scenario_id: Optional[int]) -> Dict[int, Dict[str, Any]]:
        """Fallback method to load component attributes individually."""
        from pyconvexity.models import get_attribute, list_component_attributes
        from pyconvexity.core.types import AttributeValue
        from pyconvexity.models.network import get_network_time_periods
        import pandas as pd
        
        # Get network time periods for proper timestamp alignment
        network_time_periods = None
        if component_ids:
            cursor = conn.execute("SELECT network_id FROM components WHERE id = ? LIMIT 1", (component_ids[0],))
            result = cursor.fetchone()
            if result:
                network_id = result[0]
                try:
                    network_time_periods = get_network_time_periods(conn, network_id)
                except Exception as e:
                    logger.warning(f"Failed to load network time periods: {e}")
        
        attributes = {}
        for comp_id in component_ids:
            try:
                attr_names = list_component_attributes(conn, comp_id)
                comp_attrs = {}
                for attr_name in attr_names:
                    try:
                        attr_value = get_attribute(conn, comp_id, attr_name, scenario_id)
                        if attr_value is not None:
                            # Handle different attribute value types
                            if hasattr(attr_value, 'static_value') and attr_value.static_value is not None:
                                # Static value
                                comp_attrs[attr_name] = attr_value.static_value.value()
                            elif hasattr(attr_value, 'timeseries_value') and attr_value.timeseries_value is not None:
                                # Timeseries value - convert to pandas Series with proper timestamps
                                timeseries_points = attr_value.timeseries_value
                                if timeseries_points:
                                    # Sort by period_index to ensure correct order
                                    timeseries_points.sort(key=lambda x: x.period_index)
                                    values = [point.value for point in timeseries_points]
                                    
                                    # Create proper timestamps for PyPSA alignment
                                    if network_time_periods:
                                        timestamps = []
                                        for point in timeseries_points:
                                            if point.period_index < len(network_time_periods):
                                                tp = network_time_periods[point.period_index]
                                                timestamps.append(pd.Timestamp(tp.formatted_time))
                                            else:
                                                logger.warning(f"Period index {point.period_index} out of range for network time periods")
                                                timestamps.append(pd.Timestamp.now())  # Fallback
                                        comp_attrs[attr_name] = pd.Series(values, index=timestamps)
                                    else:
                                        # Fallback: use period_index as index
                                        period_indices = [point.period_index for point in timeseries_points]
                                        comp_attrs[attr_name] = pd.Series(values, index=period_indices)
                    except Exception as e:
                        logger.debug(f"Failed to load attribute {attr_name} for component {comp_id}: {e}")
                attributes[comp_id] = comp_attrs
            except Exception as e:
                logger.warning(f"Failed to load attributes for component {comp_id}: {e}")
                attributes[comp_id] = {}
        
        return attributes
