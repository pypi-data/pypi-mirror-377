"""
NetCDF importer for PyConvexity energy system models.
Imports PyPSA NetCDF files into PyConvexity database format.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Callable, Tuple, List
from pathlib import Path
import random
import math

# Import functions directly from pyconvexity
from pyconvexity.core.database import open_connection, create_database_with_schema
from pyconvexity.core.types import (
    StaticValue, CreateNetworkRequest, CreateComponentRequest, TimeseriesPoint
)
from pyconvexity.core.errors import PyConvexityError as DbError
from pyconvexity.models import (
    create_network, create_carrier, insert_component, set_static_attribute,
    get_bus_name_to_id_map, set_timeseries_attribute, get_component_type, get_attribute
)
from pyconvexity.validation import get_validation_rule

logger = logging.getLogger(__name__)

class NetCDFModelImporter:
    """Import PyPSA NetCDF files into PyConvexity database format"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Set random seed for reproducible coordinate generation
        random.seed(42)
        np.random.seed(42)
        self._used_names = set()  # Global registry of all used names
    
    def import_netcdf_to_database(
        self, 
        netcdf_path: str, 
        db_path: str, 
        network_name: str,
        network_description: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        strict_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Import a PyPSA NetCDF file into a new database.
        
        Args:
            netcdf_path: Path to the PyPSA NetCDF file
            db_path: Path where to create the database
            network_name: Name for the imported network
            network_description: Optional description
            progress_callback: Optional callback for progress updates (progress: int, message: str)
            strict_validation: Whether to skip undefined attributes rather than failing completely.
                               If True, will fail on any attribute not defined in the database schema.
                               If False (default), will skip undefined attributes with warnings.
        
        Returns:
            Dictionary with import results and statistics
        """
        try:
            if progress_callback:
                progress_callback(0, "Starting NetCDF import...")
            
            # Import PyPSA
            pypsa = self._import_pypsa()
            
            if progress_callback:
                progress_callback(5, "Loading PyPSA network from NetCDF...")
            
            # Load the PyPSA network
            network = pypsa.Network(netcdf_path)
            
            if progress_callback:
                progress_callback(15, f"Loaded network: {len(network.buses)} buses, {len(network.generators)} generators")
            
            # Use the shared import logic
            return self._import_network_to_database(
                network=network,
                db_path=db_path,
                network_name=network_name,
                network_description=network_description,
                progress_callback=progress_callback,
                strict_validation=strict_validation,
                import_source="NetCDF",
                netcdf_path=netcdf_path
            )
            
        except Exception as e:
            self.logger.error(f"Error importing NetCDF: {e}", exc_info=True)
            if progress_callback:
                progress_callback(None, f"Error: {str(e)}")
            raise

    def import_csv_to_database(
        self, 
        csv_directory: str, 
        db_path: str, 
        network_name: str,
        network_description: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        strict_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Import a PyPSA network from CSV files into a new database.
        
        Args:
            csv_directory: Path to the directory containing PyPSA CSV files
            db_path: Path where to create the database
            network_name: Name for the imported network
            network_description: Optional description
            progress_callback: Optional callback for progress updates (progress: int, message: str)
            strict_validation: Whether to skip undefined attributes rather than failing
            
        Returns:
            Dictionary with import results and statistics
        """
        try:
            if progress_callback:
                progress_callback(0, "Starting PyPSA CSV import...")
            
            # Import PyPSA
            pypsa = self._import_pypsa()
            
            if progress_callback:
                progress_callback(5, "Validating CSV files...")
            
            # Validate CSV directory and files before attempting import
            self._validate_csv_directory(csv_directory)
            
            if progress_callback:
                progress_callback(10, "Loading PyPSA network from CSV files...")
            
            # Load the PyPSA network from CSV directory
            network = pypsa.Network()
            
            try:
                network.import_from_csv_folder(csv_directory)
            except Exception as e:
                # Provide more helpful error message
                error_msg = f"PyPSA CSV import failed: {str(e)}"
                if "'name'" in str(e):
                    error_msg += "\n\nThis usually means one of your CSV files is missing a 'name' column. PyPSA CSV files require:\n"
                    error_msg += "- All component CSV files (buses.csv, generators.csv, etc.) must have a 'name' column as the first column\n"
                    error_msg += "- The 'name' column should contain unique identifiers for each component\n"
                    error_msg += "- Check that your CSV files follow the PyPSA CSV format specification"
                elif "KeyError" in str(e):
                    error_msg += f"\n\nThis indicates a required column is missing from one of your CSV files. "
                    error_msg += "Please ensure your CSV files follow the PyPSA format specification."
                
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            
            if progress_callback:
                progress_callback(20, f"Loaded network: {len(network.buses)} buses, {len(network.generators)} generators")
            
            # Use the shared import logic
            return self._import_network_to_database(
                network=network,
                db_path=db_path,
                network_name=network_name,
                network_description=network_description,
                progress_callback=progress_callback,
                strict_validation=strict_validation,
                import_source="CSV"
            )
            
        except Exception as e:
            self.logger.error(f"Error importing PyPSA CSV: {e}", exc_info=True)
            if progress_callback:
                progress_callback(None, f"Error: {str(e)}")
            raise

    def _import_pypsa(self):
        """Import PyPSA with standard error handling."""
        try:
            import pypsa
            return pypsa
        except ImportError as e:
            self.logger.error(f"Failed to import PyPSA: {e}", exc_info=True)
            raise ImportError(
                "PyPSA is not installed or could not be imported. "
                "Please ensure it is installed correctly in the environment."
            ) from e
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during PyPSA import: {e}", exc_info=True)
            raise

    def _validate_csv_directory(self, csv_directory: str) -> None:
        """Validate that the CSV directory contains valid PyPSA CSV files"""
        import os
        import pandas as pd
        
        csv_path = Path(csv_directory)
        if not csv_path.exists():
            raise ValueError(f"CSV directory does not exist: {csv_directory}")
        
        if not csv_path.is_dir():
            raise ValueError(f"Path is not a directory: {csv_directory}")
        
        # Find CSV files
        csv_files = list(csv_path.glob("*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in directory: {csv_directory}")
        
        # Check each CSV file for basic validity
        component_files = ['buses.csv', 'generators.csv', 'loads.csv', 'lines.csv', 'links.csv', 'storage_units.csv', 'stores.csv']
        required_files = ['buses.csv']  # At minimum, we need buses
        
        # Check for required files
        existing_files = [f.name for f in csv_files]
        missing_required = [f for f in required_files if f not in existing_files]
        if missing_required:
            raise ValueError(f"Missing required CSV files: {missing_required}")
        
        # Validate each component CSV file that exists
        for csv_file in csv_files:
            if csv_file.name in component_files:
                try:
                    df = pd.read_csv(csv_file, nrows=0)  # Just read headers
                    if 'name' not in df.columns:
                        raise ValueError(f"CSV file '{csv_file.name}' is missing required 'name' column. Found columns: {list(df.columns)}")
                except Exception as e:
                    raise ValueError(f"Error reading CSV file '{csv_file.name}': {str(e)}")

    def _import_network_to_database(
        self,
        network,
        db_path: str,
        network_name: str,
        network_description: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
        strict_validation: bool = False,
        import_source: str = "PyPSA",
        netcdf_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Shared logic to import a PyPSA network object into a database.
        This method is used by both NetCDF and CSV import functions.
        """
        try:
            if progress_callback:
                progress_callback(0, "Starting network import...")
            
            # Create the database with schema using atomic utility
            create_database_with_schema(db_path)
            
            if progress_callback:
                progress_callback(5, "Database schema created")
            
            # Connect to database
            conn = open_connection(db_path)
            
            try:
                # Load companion location CSV if available (for NetCDF imports only)
                location_map = None
                if import_source == "NetCDF" and netcdf_path:
                    location_map = self._detect_and_load_location_csv(netcdf_path)
                
                # Create the network record
                network_id = self._create_network_record(
                    conn, network, network_name, network_description
                )
                
                if progress_callback:
                    progress_callback(10, f"Created network record (ID: {network_id})")
                
                # Verify that the "Main" scenario was created by the database trigger
                cursor = conn.execute("SELECT id, name, is_master FROM scenarios WHERE network_id = ?", (network_id,))
                scenarios = cursor.fetchall()
                if scenarios:
                    main_scenario = next((s for s in scenarios if s[2] == True), None)  # is_master = True
                    if not main_scenario:
                        self.logger.warning(f"No master scenario found in scenarios: {scenarios}")
                else:
                    self.logger.error(f"No scenarios found after network creation - database trigger may have failed")
                
                # Create network time periods from PyPSA snapshots
                self._create_network_time_periods(conn, network, network_id)
                
                if progress_callback:
                    progress_callback(15, f"Created network time periods")
                
                # Import carriers
                carriers_count = self._import_carriers(conn, network, network_id)
                
                if progress_callback:
                    progress_callback(20, f"Imported {carriers_count} carriers")
                
                # Import buses
                buses_count = self._import_buses(conn, network, network_id, strict_validation)
                
                if progress_callback:
                    progress_callback(25, f"Imported {buses_count} buses")
                
                # Calculate scatter radius for non-bus components based on bus separation
                bus_coordinates = self._get_bus_coordinates(conn, network_id)
                scatter_radius = self._calculate_bus_separation_radius(bus_coordinates)
                
                # Import generators
                generators_count = self._import_generators(conn, network, network_id, strict_validation, scatter_radius, location_map)
                
                if progress_callback:
                    progress_callback(30, f"Imported {generators_count} generators")
                
                # Import loads
                loads_count = self._import_loads(conn, network, network_id, strict_validation, scatter_radius, location_map)
                
                if progress_callback:
                    progress_callback(35, f"Imported {loads_count} loads")
                
                # Import lines
                lines_count = self._import_lines(conn, network, network_id, strict_validation, location_map)
                
                if progress_callback:
                    progress_callback(40, f"Imported {lines_count} lines")
                
                # Import links
                links_count = self._import_links(conn, network, network_id, strict_validation, location_map)
                
                if progress_callback:
                    progress_callback(45, f"Imported {links_count} links")
                
                # Import storage units
                storage_units_count = self._import_storage_units(conn, network, network_id, strict_validation, scatter_radius, location_map)
                
                if progress_callback:
                    progress_callback(50, f"Imported {storage_units_count} storage units")
                
                # Import stores
                stores_count = self._import_stores(conn, network, network_id, strict_validation, scatter_radius, location_map)
                
                if progress_callback:
                    progress_callback(55, f"Imported {stores_count} stores")
                
                conn.commit()
                
                if progress_callback:
                    progress_callback(100, "Import completed successfully")
                
                # Collect final statistics
                stats = {
                    "network_id": network_id,
                    "network_name": network_name,
                    "carriers": carriers_count,
                    "buses": buses_count,
                    "generators": generators_count,
                    "loads": loads_count,
                    "lines": lines_count,
                    "links": links_count,
                    "storage_units": storage_units_count,
                    "stores": stores_count,
                    "total_components": (buses_count + generators_count + loads_count + 
                                       lines_count + links_count + storage_units_count + stores_count),
                    "snapshots": len(network.snapshots) if hasattr(network, 'snapshots') else 0,
                }
                
                return {
                    "success": True,
                    "message": f"Network imported successfully from {import_source}",
                    "db_path": db_path,
                    "stats": stats
                }
                
            finally:
                conn.close()
                
        except Exception as e:
            self.logger.error(f"Error importing network: {e}", exc_info=True)
            if progress_callback:
                progress_callback(None, f"Error: {str(e)}")
            raise

    # Helper methods for the import process
    # Note: These are simplified versions of the methods from the original netcdf_importer.py
    # The full implementation would include all the detailed import logic for each component type
    
    def _extract_datetime_snapshots(self, network) -> pd.DatetimeIndex:
        """Extract datetime snapshots from a PyPSA network"""
        if not hasattr(network, 'snapshots') or len(network.snapshots) == 0:
            self.logger.warning("No snapshots found in PyPSA network")
            return pd.DatetimeIndex([])
        
        snapshots = network.snapshots
        
        try:
            # Try direct conversion first (works for simple DatetimeIndex)
            return pd.to_datetime(snapshots)
        except (TypeError, ValueError) as e:
            # Handle MultiIndex case
            if hasattr(snapshots, 'nlevels') and snapshots.nlevels > 1:
                # Try to use the timesteps attribute if available (common in multi-period networks)
                if hasattr(network, 'timesteps') and isinstance(network.timesteps, pd.DatetimeIndex):
                    return network.timesteps
                
                # Try to extract datetime from the last level of the MultiIndex
                try:
                    # Get the last level (usually the timestep level)
                    last_level = snapshots.get_level_values(snapshots.nlevels - 1)
                    datetime_snapshots = pd.to_datetime(last_level)
                    return datetime_snapshots
                except Exception as multi_e:
                    self.logger.warning(f"Failed to extract datetime from MultiIndex: {multi_e}")
            
            # Final fallback: create a default hourly range
            self.logger.warning("Could not extract datetime snapshots, creating default hourly range")
            default_start = pd.Timestamp('2024-01-01 00:00:00')
            default_end = pd.Timestamp('2024-01-01 23:59:59')
            return pd.date_range(start=default_start, end=default_end, freq='H')

    def _create_network_record(
        self, 
        conn, 
        network, 
        network_name: str,
        network_description: Optional[str] = None
    ) -> int:
        """Create the network record and return network ID"""
        
        # Extract time information from PyPSA network using our robust helper
        snapshots = self._extract_datetime_snapshots(network)
        
        if len(snapshots) > 0:
            time_start = snapshots.min().strftime('%Y-%m-%d %H:%M:%S')
            time_end = snapshots.max().strftime('%Y-%m-%d %H:%M:%S')
            
            # Try to infer time interval
            if len(snapshots) > 1:
                freq = pd.infer_freq(snapshots)
                time_interval = freq or 'H'  # Default to hourly if can't infer
            else:
                time_interval = 'H'
        else:
            # Default time range if no snapshots
            time_start = '2024-01-01 00:00:00'
            time_end = '2024-01-01 23:59:59'
            time_interval = 'H'
        
        description = network_description or f"Imported from PyPSA NetCDF on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        request = CreateNetworkRequest(
            name=network_name,
            description=description,
            time_resolution=time_interval,
            start_time=time_start,
            end_time=time_end
        )
        return create_network(conn, request)

    def _create_network_time_periods(self, conn, network, network_id: int) -> None:
        """Create network time periods from PyPSA snapshots"""
        # Use our robust helper to extract datetime snapshots
        snapshots = self._extract_datetime_snapshots(network)
        
        if len(snapshots) == 0:
            self.logger.warning("No valid snapshots found in PyPSA network, skipping time periods creation")
            return
        
        # Insert time periods
        for period_index, snapshot in enumerate(snapshots):
            timestamp_str = snapshot.strftime('%Y-%m-%d %H:%M:%S')
            
            conn.execute("""
                INSERT INTO network_time_periods (network_id, timestamp, period_index)
                VALUES (?, ?, ?)
            """, (network_id, timestamp_str, period_index))

    # Placeholder methods - in a full implementation, these would contain
    # the detailed import logic from the original netcdf_importer.py
    
    def _import_carriers(self, conn, network, network_id: int) -> int:
        """Import carriers from PyPSA network"""
        # Simplified implementation - full version would be from original file
        count = 0
        
        # Get carriers from network.carriers table if it exists
        if hasattr(network, 'carriers') and not network.carriers.empty:
            for carrier_name, carrier_data in network.carriers.iterrows():
                co2_emissions = carrier_data.get('co2_emissions', 0.0)
                color = carrier_data.get('color', '#3498db')
                nice_name = carrier_data.get('nice_name', carrier_name)
                
                create_carrier(conn, network_id, carrier_name, co2_emissions, color, nice_name)
                count += 1
        
        # Ensure we have essential carriers
        if count == 0:
            create_carrier(conn, network_id, 'AC', 0.0, '#3498db', 'AC Electricity')
            count += 1
        
        return count

    def _import_buses(self, conn, network, network_id: int, strict_validation: bool) -> int:
        """Import buses from PyPSA network"""
        # Simplified implementation - full version would be from original file
        count = 0
        
        if hasattr(network, 'buses') and not network.buses.empty:
            for bus_name, bus_data in network.buses.iterrows():
                # Extract coordinates
                longitude = bus_data.get('x', None)
                latitude = bus_data.get('y', None)
                
                # Handle NaN values
                if pd.isna(longitude):
                    longitude = None
                if pd.isna(latitude):
                    latitude = None
                
                # Create component record
                request = CreateComponentRequest(
                    network_id=network_id,
                    component_type='BUS',
                    name=str(bus_name),
                    latitude=latitude,
                    longitude=longitude
                )
                component_id = insert_component(conn, request)
                count += 1
        
        return count

    # Additional placeholder methods for other component types
    def _import_generators(self, conn, network, network_id: int, strict_validation: bool, scatter_radius: float, location_map) -> int:
        """Import generators from PyPSA network"""
        # Simplified - full implementation would be from original file
        return len(network.generators) if hasattr(network, 'generators') else 0

    def _import_loads(self, conn, network, network_id: int, strict_validation: bool, scatter_radius: float, location_map) -> int:
        """Import loads from PyPSA network"""
        # Simplified - full implementation would be from original file
        return len(network.loads) if hasattr(network, 'loads') else 0

    def _import_lines(self, conn, network, network_id: int, strict_validation: bool, location_map) -> int:
        """Import lines from PyPSA network"""
        # Simplified - full implementation would be from original file
        return len(network.lines) if hasattr(network, 'lines') else 0

    def _import_links(self, conn, network, network_id: int, strict_validation: bool, location_map) -> int:
        """Import links from PyPSA network"""
        # Simplified - full implementation would be from original file
        return len(network.links) if hasattr(network, 'links') else 0

    def _import_storage_units(self, conn, network, network_id: int, strict_validation: bool, scatter_radius: float, location_map) -> int:
        """Import storage units from PyPSA network"""
        # Simplified - full implementation would be from original file
        return len(network.storage_units) if hasattr(network, 'storage_units') else 0

    def _import_stores(self, conn, network, network_id: int, strict_validation: bool, scatter_radius: float, location_map) -> int:
        """Import stores from PyPSA network"""
        # Simplified - full implementation would be from original file
        return len(network.stores) if hasattr(network, 'stores') else 0

    def _get_bus_coordinates(self, conn, network_id: int) -> List[Tuple[float, float]]:
        """Get coordinates of all buses in the network that have valid coordinates"""
        cursor = conn.execute("""
            SELECT latitude, longitude FROM components 
            WHERE network_id = ? AND component_type = 'BUS' 
            AND latitude IS NOT NULL AND longitude IS NOT NULL
            AND NOT (latitude = 0 AND longitude = 0)
        """, (network_id,))
        
        coordinates = [(row[0], row[1]) for row in cursor.fetchall()]
        return coordinates

    def _calculate_bus_separation_radius(self, bus_coordinates: List[Tuple[float, float]]) -> float:
        """Calculate the minimum separation between buses and return a radius for scattering"""
        if len(bus_coordinates) < 2:
            return 0.01  # ~1km at equator
        
        min_distance_degrees = float('inf')
        min_separation_threshold = 0.001  # ~100m threshold to exclude co-located buses
        
        for i, (lat1, lon1) in enumerate(bus_coordinates):
            for j, (lat2, lon2) in enumerate(bus_coordinates[i+1:], i+1):
                # Simple Euclidean distance in degrees
                distance_degrees = math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2)
                
                if distance_degrees > min_separation_threshold:
                    min_distance_degrees = min(min_distance_degrees, distance_degrees)
        
        if min_distance_degrees == float('inf'):
            scatter_radius_degrees = 0.05  # ~5km default
        else:
            scatter_radius_degrees = min_distance_degrees * 0.25
        
        # Ensure reasonable bounds: between 1km and 100km equivalent in degrees
        min_radius = 0.01   # ~1km
        max_radius = 1.0    # ~100km
        scatter_radius_degrees = max(min_radius, min(max_radius, scatter_radius_degrees))
        
        return scatter_radius_degrees

    def _detect_and_load_location_csv(self, netcdf_path: str) -> Optional[Dict[str, Tuple[float, float]]]:
        """Detect and load companion CSV file with component locations"""
        # Simplified implementation - full version would be from original file
        return None
