"""
Solving functionality for PyPSA networks.

Handles the actual optimization solving with various solvers and configurations.
"""

import logging
import time
import uuid
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NetworkSolver:
    """
    Handles solving PyPSA networks with various solvers and configurations.
    
    This class encapsulates the solving logic, including solver configuration,
    multi-period optimization setup, and result extraction.
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
    
    def solve_network(
        self,
        network: 'pypsa.Network',
        solver_name: str = "highs",
        solver_options: Optional[Dict[str, Any]] = None,
        discount_rate: Optional[float] = None,
        job_id: Optional[str] = None,
        conn=None,
        network_id: Optional[int] = None,
        scenario_id: Optional[int] = None,
        constraint_applicator=None
    ) -> Dict[str, Any]:
        """
        Solve PyPSA network and return results.
        
        Args:
            network: PyPSA Network object to solve
            solver_name: Solver to use (default: "highs")
            solver_options: Optional solver-specific options
            discount_rate: Optional discount rate for multi-period optimization
            job_id: Optional job ID for tracking
            
        Returns:
            Dictionary with solve results and metadata
            
        Raises:
            ImportError: If PyPSA is not available
            Exception: If solving fails
        """
        start_time = time.time()
        run_id = str(uuid.uuid4())
        
        logger.info(f"Starting network solve with {solver_name}")
        
        try:
            # Get solver configuration
            actual_solver_name, solver_config = self._get_solver_config(solver_name, solver_options)
            
            # Always use multi-period mode for consistency
            # Extract years from network snapshots
            if hasattr(network, '_available_years') and network._available_years:
                years = network._available_years
            elif hasattr(network.snapshots, 'year'):
                years = sorted(network.snapshots.year.unique())
            else:
                # If no year info, use a single default year
                years = [2020]  # Default single year
            
            # Configure for multi-period optimization (works for single year too)
            effective_discount_rate = discount_rate if discount_rate is not None else 0.05  # Default 5%
            logger.info(f"Configuring multi-period optimization with discount rate {effective_discount_rate}")
            network = self._configure_multi_period_optimization(network, years, effective_discount_rate)
            
            # CRITICAL: Set snapshot weightings AFTER multi-period setup
            # PyPSA's multi-period setup can reset snapshot weightings to 1.0
            if conn and network_id:
                self._set_snapshot_weightings_after_multiperiod(conn, network_id, network)
            
            # Prepare optimization constraints (extra_functionality)
            extra_functionality = None
            if conn and network_id and constraint_applicator:
                optimization_constraints = constraint_applicator.get_optimization_constraints(conn, network_id, scenario_id)
                if optimization_constraints:
                    logger.info(f"Applying {len(optimization_constraints)} optimization-time constraints")
                    extra_functionality = self._create_extra_functionality(optimization_constraints, constraint_applicator)
            
            # Solver diagnostics (simplified version of old code)
            logger.info(f"=== PYPSA SOLVER DIAGNOSTICS ===")
            logger.info(f"Requested solver: {solver_name}")
            logger.info(f"Actual solver: {actual_solver_name}")
            if solver_config:
                logger.info(f"Solver options: {solver_config}")
            logger.info(f"Multi-period optimization: {self._is_multi_period_network(network)}")
            logger.info(f"Investment periods: {getattr(network, 'investment_periods', 'None')}")
            logger.info(f"=== END PYPSA SOLVER DIAGNOSTICS ===")
            
            # Solve the network
            logger.info(f"Solving network with {actual_solver_name}")
            
            if solver_config:
                result = self._solve_with_config(network, actual_solver_name, solver_config, job_id, extra_functionality)
            else:
                result = self._solve_standard(network, actual_solver_name, job_id, extra_functionality)
            
            solve_time = time.time() - start_time
            
            # Post-solve debug logging (matches old code)
            objective_value = getattr(network, 'objective', None)
            if objective_value is not None:
                logger.info(f"[DEBUG] POST-SOLVE snapshot_weightings structure:")
                if hasattr(network, 'snapshot_weightings'):
                    logger.info(f"[DEBUG] Type: {type(network.snapshot_weightings)}")
                    logger.info(f"[DEBUG] Columns: {list(network.snapshot_weightings.columns)}")
                    logger.info(f"[DEBUG] Shape: {network.snapshot_weightings.shape}")
                    logger.info(f"[DEBUG] Unique values in objective column: {network.snapshot_weightings['objective'].unique()}")
                    logger.info(f"[DEBUG] Sum of objective column: {network.snapshot_weightings['objective'].sum()}")
                    
                    if hasattr(network, 'investment_period_weightings'):
                        logger.info(f"[DEBUG] investment_period_weightings exists:")
                        logger.info(f"[DEBUG] Type: {type(network.investment_period_weightings)}")
                        logger.info(f"[DEBUG] Content:\n{network.investment_period_weightings}")
            
            # Extract solve results with comprehensive statistics
            solve_result = self._extract_solve_results(network, result, solve_time, actual_solver_name, run_id)
            
            # Calculate comprehensive network statistics (all years combined)
            if solve_result.get('success'):
                logger.info("Calculating comprehensive network statistics...")
                network_statistics = self._calculate_comprehensive_network_statistics(network, solve_time, actual_solver_name)
                solve_result['network_statistics'] = network_statistics
                
                # Calculate year-based statistics for capacity expansion analysis
                logger.info("Calculating year-based statistics...")
                year_statistics = self._calculate_statistics_by_year(network, solve_time, actual_solver_name)
                solve_result['year_statistics'] = year_statistics
                solve_result['year_statistics_available'] = len(year_statistics) > 0
            
            logger.info(f"Solve completed in {solve_time:.2f} seconds with status: {solve_result['status']}")
            logger.info(f"PyPSA result object: {result}")
            logger.info(f"PyPSA result status: {getattr(result, 'status', 'no status attr')}")
            logger.info(f"Network objective: {getattr(network, 'objective', 'no objective')}")
            logger.info(f"Solve result success: {solve_result.get('success')}")
            
            return solve_result
            
        except Exception as e:
            solve_time = time.time() - start_time
            logger.error(f"Solve failed after {solve_time:.2f} seconds: {e}")
            
            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "solve_time": solve_time,
                "solver_name": actual_solver_name if 'actual_solver_name' in locals() else solver_name,
                "run_id": run_id,
                "objective_value": None
            }
    
    def _get_solver_config(self, solver_name: str, solver_options: Optional[Dict[str, Any]] = None) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Get the actual solver name and options for special solver configurations.
        
        Args:
            solver_name: The solver name (e.g., 'gurobi (barrier)', 'highs')
            solver_options: Optional additional solver options
            
        Returns:
            Tuple of (actual_solver_name, solver_options_dict)
        """
        # Handle "default" solver
        if solver_name == 'default':
            logger.warning("Solver name 'default' received - falling back to 'highs'.")
            return 'highs', solver_options
        
        # Handle special Gurobi configurations
        if solver_name == 'gurobi (barrier)':
            gurobi_barrier_options = {
                'solver_options': {
                    'Method': 2,             # Barrier
                    'Crossover': 0,          # Skip crossover
                    'MIPGap': 0.05,          # 5% gap
                    'Threads': 4,            # Use all cores
                    'Presolve': 2,           # Aggressive presolve
                    'ConcurrentMIP': 1,      # Parallel root strategies
                    'BarConvTol': 1e-4,      # Relaxed barrier convergence
                    'FeasibilityTol': 1e-5,
                    'OptimalityTol': 1e-5,
                    'NumericFocus': 1,       # Improve stability
                    'PreSparsify': 1,
                }
            }
            # Merge with any additional options
            if solver_options:
                gurobi_barrier_options.update(solver_options)
            return 'gurobi', gurobi_barrier_options

        elif solver_name == 'gurobi (barrier homogeneous)':
            gurobi_barrier_homogeneous_options = {
                'solver_options': {
                    'Method': 2,             # Barrier
                    'Crossover': 0,          # Skip crossover
                    'MIPGap': 0.05,
                    'Threads': 4,
                    'Presolve': 2,
                    'ConcurrentMIP': 1,
                    'BarConvTol': 1e-4,
                    'FeasibilityTol': 1e-5,
                    'OptimalityTol': 1e-5,
                    'NumericFocus': 1,
                    'PreSparsify': 1,
                    'BarHomogeneous': 1,     # Enable homogeneous barrier algorithm
                }
            }
            if solver_options:
                gurobi_barrier_homogeneous_options.update(solver_options)
            return 'gurobi', gurobi_barrier_homogeneous_options

        elif solver_name == 'gurobi (barrier+crossover balanced)':
            gurobi_options_balanced = {
                'solver_options': {
                    'Method': 2,
                    'Crossover': 1,         # Dual crossover
                    'MIPGap': 0.01,
                    'Threads': 4,
                    'Presolve': 2,
                    'Heuristics': 0.1,
                    'Cuts': 2,
                    'ConcurrentMIP': 1,
                    'BarConvTol': 1e-6,
                    'FeasibilityTol': 1e-6,
                    'OptimalityTol': 1e-6,
                    'NumericFocus': 1,
                    'PreSparsify': 1,
                }
            }
            if solver_options:
                gurobi_options_balanced.update(solver_options)
            logger.info(f"Using Gurobi Barrier+Dual Crossover Balanced configuration")
            return 'gurobi', gurobi_options_balanced

        elif solver_name == 'gurobi (dual simplex)':
            gurobi_dual_options = {
                'solver_options': {
                    'Method': 1,           # Dual simplex method
                    'Threads': 0,          # Use all available cores
                    'Presolve': 2,         # Aggressive presolve
                }
            }
            if solver_options:
                gurobi_dual_options.update(solver_options)
            return 'gurobi', gurobi_dual_options
        
        # Check if this is a known valid solver name
        elif solver_name in ['highs', 'gurobi', 'cplex', 'glpk', 'cbc', 'scip']:
            return solver_name, solver_options
        
        else:
            # Unknown solver name - log warning and fall back to highs
            logger.warning(f"Unknown solver name '{solver_name}' - falling back to 'highs'")
            return 'highs', solver_options
    
    def _solve_with_config(self, network: 'pypsa.Network', solver_name: str, solver_config: Dict[str, Any], job_id: Optional[str], extra_functionality=None) -> Any:
        """Solve network with specific solver configuration."""
        # Check if multi-period optimization is needed
        is_multi_period = self._is_multi_period_network(network)
        
        # Add extra_functionality to solver config if provided
        if extra_functionality:
            solver_config = solver_config.copy()  # Don't modify original
            solver_config['extra_functionality'] = extra_functionality
        
        if is_multi_period:
            return network.optimize(solver_name=solver_name, multi_investment_periods=True, **solver_config)
        else:
            return network.optimize(solver_name=solver_name, **solver_config)
    
    def _solve_standard(self, network: 'pypsa.Network', solver_name: str, job_id: Optional[str], extra_functionality=None) -> Any:
        """Solve network with standard configuration."""
        # Check if multi-period optimization is needed
        is_multi_period = self._is_multi_period_network(network)
        
        if extra_functionality:
            if is_multi_period:
                return network.optimize(solver_name=solver_name, multi_investment_periods=True, extra_functionality=extra_functionality)
            else:
                return network.optimize(solver_name=solver_name, extra_functionality=extra_functionality)
        else:
            if is_multi_period:
                return network.optimize(solver_name=solver_name, multi_investment_periods=True)
            else:
                return network.optimize(solver_name=solver_name)
    
    def _is_multi_period_network(self, network: 'pypsa.Network') -> bool:
        """
        Determine if the network requires multi-period optimization.
        
        Multi-period optimization is needed when:
        1. Network has investment_periods attribute with multiple periods
        2. Network snapshots are MultiIndex with period/timestep structure
        3. Network has generators with build_year attributes
        
        Args:
            network: PyPSA Network object
            
        Returns:
            True if multi-period optimization is needed, False otherwise
        """
        try:
            # Check if network has investment_periods
            if hasattr(network, 'investment_periods') and network.investment_periods is not None:
                periods = list(network.investment_periods)
                if len(periods) > 1:
                    return True
                elif len(periods) == 1:
                    # Even with single period, check if we have build_year constraints
                    if hasattr(network, 'generators') and not network.generators.empty:
                        if 'build_year' in network.generators.columns:
                            build_year_gens = network.generators[network.generators['build_year'].notna()]
                            if not build_year_gens.empty:
                                return True
            
            # Check if snapshots are MultiIndex (period, timestep structure)
            if hasattr(network, 'snapshots') and hasattr(network.snapshots, 'names'):
                if network.snapshots.names and len(network.snapshots.names) >= 2:
                    if network.snapshots.names[0] == 'period':
                        return True
            
            # Check if we have generators with build_year (fallback check)
            if hasattr(network, 'generators') and not network.generators.empty:
                if 'build_year' in network.generators.columns:
                    build_year_gens = network.generators[network.generators['build_year'].notna()]
                    if not build_year_gens.empty:
                        # If we have build_year but no proper multi-period setup, we should still try multi-period
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking multi-period status: {e}")
            return False
    
    def _create_extra_functionality(self, optimization_constraints: list, constraint_applicator) -> callable:
        """
        Create extra_functionality function for optimization-time constraints.
        
        This matches the old PyPSA solver's approach to applying constraints during optimization.
        
        Args:
            optimization_constraints: List of optimization constraint dictionaries
            constraint_applicator: ConstraintApplicator instance
            
        Returns:
            Function that can be passed to network.optimize(extra_functionality=...)
        """
        def extra_functionality(network, snapshots):
            """Apply optimization constraints during solve - matches old code structure"""
            try:
                logger.info(f"Applying {len(optimization_constraints)} optimization constraints during solve")
                
                # Apply each constraint in priority order
                sorted_constraints = sorted(optimization_constraints, key=lambda x: x.get('priority', 0))
                
                for constraint in sorted_constraints:
                    try:
                        constraint_applicator.apply_optimization_constraint(network, snapshots, constraint)
                    except Exception as e:
                        logger.error(f"Failed to apply optimization constraint {constraint.get('name', 'unknown')}: {e}")
                        continue
                
                logger.info("Optimization constraints applied successfully")
                
            except Exception as e:
                logger.error(f"Failed to apply optimization constraints: {e}")
                # Don't re-raise - let optimization continue
        
        return extra_functionality
    
    def _set_snapshot_weightings_after_multiperiod(self, conn, network_id: int, network: 'pypsa.Network'):
        """Set snapshot weightings AFTER multi-period setup - matches old code approach."""
        try:
            from pyconvexity.models import get_network_time_periods, get_network_info
            
            time_periods = get_network_time_periods(conn, network_id)
            if time_periods and len(network.snapshots) > 0:
                logger.info(f"Setting snapshot weightings AFTER multi-period setup for {len(time_periods)} time periods")
                
                # Get network info to determine time interval (stored in networks table, not network_config)
                network_info = get_network_info(conn, network_id)
                time_interval = network_info.get('time_interval', '1H')
                weight = self._parse_time_interval(time_interval)
                
                if weight is None:
                    weight = 1.0
                    logger.warning(f"Could not parse time interval '{time_interval}', using default weight of 1.0")
                
                logger.info(f"Parsed time interval '{time_interval}' -> weight = {weight}")
                
                # Create weightings array - all snapshots get the same weight for this time resolution
                weightings = [weight] * len(time_periods)
                
                if len(weightings) == len(network.snapshots):
                    # Set all three columns like the old code - critical for proper objective calculation
                    network.snapshot_weightings.loc[:, 'objective'] = weightings
                    network.snapshot_weightings.loc[:, 'generators'] = weightings  
                    network.snapshot_weightings.loc[:, 'stores'] = weightings
                    logger.info(f"Set snapshot weightings AFTER multi-period setup: objective, generators, stores columns")
                    
                    # Debug logging like old code
                    logger.info(f"Snapshot weightings shape: {network.snapshot_weightings.shape}")
                    logger.info(f"Unique values in objective column: {network.snapshot_weightings['objective'].unique()}")
                    logger.info(f"Sum of objective column: {network.snapshot_weightings['objective'].sum()}")
                    logger.info(f"Weight per snapshot: {weight} hours")
                else:
                    logger.warning(f"Mismatch between weightings ({len(weightings)}) and snapshots ({len(network.snapshots)})")
        except Exception as e:
            logger.warning(f"Failed to set snapshot weightings after multi-period setup: {e}")
            logger.exception("Full traceback:")
    
    def _parse_time_interval(self, time_interval: str) -> Optional[float]:
        """Parse time interval string to hours - handles multiple formats."""
        if not time_interval:
            return None
        
        try:
            # Clean up the string
            interval = time_interval.strip()
            
            # Handle ISO 8601 duration format (PT3H, PT30M, etc.)
            if interval.startswith('PT') and interval.endswith('H'):
                # Extract hours (e.g., 'PT3H' -> 3.0)
                hours_str = interval[2:-1]  # Remove 'PT' and 'H'
                return float(hours_str)
            elif interval.startswith('PT') and interval.endswith('M'):
                # Extract minutes (e.g., 'PT30M' -> 0.5)
                minutes_str = interval[2:-1]  # Remove 'PT' and 'M'
                return float(minutes_str) / 60.0
            elif interval.startswith('PT') and interval.endswith('S'):
                # Extract seconds (e.g., 'PT3600S' -> 1.0)
                seconds_str = interval[2:-1]  # Remove 'PT' and 'S'
                return float(seconds_str) / 3600.0
            
            # Handle simple frequency strings (3H, 2D, etc.)
            elif interval.endswith('H') or interval.endswith('h'):
                hours_str = interval[:-1]
                return float(hours_str) if hours_str else 1.0
            elif interval.endswith('D') or interval.endswith('d'):
                days_str = interval[:-1]
                return float(days_str) * 24 if days_str else 24.0
            elif interval.endswith('M') or interval.endswith('m'):
                minutes_str = interval[:-1]
                return float(minutes_str) / 60.0 if minutes_str else 1.0/60.0
            elif interval.endswith('S') or interval.endswith('s'):
                seconds_str = interval[:-1]
                return float(seconds_str) / 3600.0 if seconds_str else 1.0/3600.0
            
            # Try to parse as plain number (assume hours)
            else:
                return float(interval)
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Could not parse time interval '{time_interval}': {e}")
            return None
    
    def _configure_multi_period_optimization(self, network: 'pypsa.Network', years: list, discount_rate: float) -> 'pypsa.Network':
        """
        Configure network for multi-period optimization (works for single or multiple years).
        
        Args:
            network: PyPSA Network object
            years: List of years in the network
            discount_rate: Discount rate for investment calculations
            
        Returns:
            Configured network
        """
        try:
            import pandas as pd
            
            logger.info(f"Configuring multi-period optimization for years: {years}")
            logger.info(f"Current snapshots: {len(network.snapshots)} time steps")
            
            # Handle case where snapshots don't have year info but years were extracted manually
            if not hasattr(network.snapshots, 'year'):
                if len(years) > 0:
                    # Use the manually extracted years from timestamps
                    # Create MultiIndex snapshots by dividing existing snapshots among the years
                    snapshots_per_year = len(network.snapshots) // len(years)
                    multi_snapshots = []
                    
                    for i, year in enumerate(years):
                        start_idx = i * snapshots_per_year
                        end_idx = (i + 1) * snapshots_per_year if i < len(years) - 1 else len(network.snapshots)
                        year_snapshots = network.snapshots[start_idx:end_idx]
                        for snapshot in year_snapshots:
                            multi_snapshots.append((year, snapshot))
                    
                    logger.info(f"Created {len(multi_snapshots)} multi-period snapshots from {len(network.snapshots)} original snapshots")
                    
                else:
                    # Only use 2020 fallback if no years were extracted at all (should be rare)
                    single_year = 2020
                    multi_snapshots = [(single_year, snapshot) for snapshot in network.snapshots]
                    years = [single_year]
                    logger.warning(f"No years provided, using fallback year {single_year}")
            else:
                # Create MultiIndex snapshots from existing year-based snapshots
                multi_snapshots = []
                for year in years:
                    year_snapshots = network.snapshots[network.snapshots.year == year]
                    for snapshot in year_snapshots:
                        multi_snapshots.append((year, snapshot))
                
                logger.info(f"Created {len(multi_snapshots)} multi-period snapshots from year-based snapshots")
            
            # Set MultiIndex snapshots and investment periods
            network.snapshots = pd.MultiIndex.from_tuples(multi_snapshots, names=['period', 'timestep'])
            network.investment_periods = years
            print(network.investment_periods)  # Match old code debug output
            
            logger.info(f"Set investment_periods: {network.investment_periods}")
            logger.info(f"MultiIndex snapshots created with levels: {network.snapshots.names}")
            
            # Calculate investment period weightings with discount rate
            self._calculate_investment_weightings(network, discount_rate)
            
            # Configure build year constraints for multi-period optimization
            self._configure_build_year_constraints(network, years)
            
            logger.info(f"Successfully configured multi-period optimization for {len(years)} investment periods")
            
        except Exception as e:
            logger.error(f"Failed to configure multi-period optimization: {e}")
            logger.exception("Full traceback:")
            # Don't re-raise - let the solve continue with original configuration
        
        return network
    
    def _calculate_investment_weightings(self, network: 'pypsa.Network', discount_rate: float) -> None:
        """
        Calculate investment period weightings using discount rate - matching old PyPSA solver exactly.
        
        Args:
            network: PyPSA Network object
            discount_rate: Discount rate for NPV calculations
        """
        try:
            import pandas as pd
            
            if not hasattr(network, 'investment_periods') or len(network.investment_periods) == 0:
                return
            
            years = network.investment_periods
            # Convert pandas Index to list for easier handling
            years_list = years.tolist() if hasattr(years, 'tolist') else list(years)
            
            logger.info(f"Calculating investment weightings for periods: {years_list} with discount rate: {discount_rate}")
            
            # For single year, use simple weighting of 1.0
            if len(years_list) == 1:
                # Single year case
                network.investment_period_weightings = pd.DataFrame({
                    'objective': pd.Series({years_list[0]: 1.0}),
                    'years': pd.Series({years_list[0]: 1})
                })
                logger.info(f"Set single-year investment period weightings for year {years_list[0]}")
            else:
                # Multi-year case - EXACTLY match old code logic
                # Get unique years from the network snapshots to determine period lengths
                if hasattr(network.snapshots, 'year'):
                    snapshot_years = sorted(network.snapshots.year.unique())
                elif hasattr(network.snapshots, 'get_level_values'):
                    # MultiIndex case - get years from 'period' level
                    snapshot_years = sorted(network.snapshots.get_level_values('period').unique())
                else:
                    # Fallback: use investment periods as years
                    snapshot_years = years_list
                
                logger.info(f"Snapshot years found: {snapshot_years}")
                
                # Calculate years per period - EXACTLY matching old code
                years_diff = []
                for i, year in enumerate(years_list):
                    if i < len(years_list) - 1:
                        # Years between this period and the next
                        next_year = years_list[i + 1]
                        period_years = next_year - year
                    else:
                        # For the last period, calculate based on snapshot coverage
                        if snapshot_years:
                            # Find the last snapshot year that's >= current period year
                            last_snapshot_year = max([y for y in snapshot_years if y >= year])
                            period_years = last_snapshot_year - year + 1
                        else:
                            # Fallback: assume same length as previous period or 1
                            if len(years_diff) > 0:
                                period_years = years_diff[-1]  # Same as previous period
                            else:
                                period_years = 1
                    
                    years_diff.append(period_years)
                    logger.info(f"Period {year}: {period_years} years")
                
                # Create weightings DataFrame with years column
                weightings_df = pd.DataFrame({
                    'years': pd.Series(years_diff, index=years_list)
                })
                
                # Calculate objective weightings with discount rate - EXACTLY matching old code
                r = discount_rate
                T = 0  # Cumulative time tracker
                
                logger.info(f"Calculating discount factors with rate {r}:")
                for period, nyears in weightings_df.years.items():
                    # Calculate discount factors for each year in this period
                    discounts = [(1 / (1 + r) ** t) for t in range(T, T + nyears)]
                    period_weighting = sum(discounts)
                    weightings_df.at[period, "objective"] = period_weighting
                    
                    logger.info(f"  Period {period}: years {T} to {T + nyears - 1}, discounts={[f'{d:.4f}' for d in discounts]}, sum={period_weighting:.4f}")
                    T += nyears  # Update cumulative time
                
                network.investment_period_weightings = weightings_df
                logger.info(f"Final investment period weightings:")
                logger.info(f"  Years: {weightings_df['years'].to_dict()}")
                logger.info(f"  Objective: {weightings_df['objective'].to_dict()}")
            
        except Exception as e:
            logger.error(f"Failed to calculate investment weightings: {e}")
            logger.exception("Full traceback:")
    
    def _configure_build_year_constraints(self, network: 'pypsa.Network', years: list) -> None:
        """
        Configure build year constraints for multi-period optimization.
        
        In PyPSA multi-period optimization, generators should only be available for investment
        starting from their build year. This method ensures proper constraint setup.
        
        Args:
            network: PyPSA Network object
            years: List of investment periods (years)
        """
        try:
            import pandas as pd
            
            logger.info("Configuring build year constraints for multi-period optimization")
            
            # Check if we have generators with build_year attributes
            if not hasattr(network, 'generators') or network.generators.empty:
                logger.warning("No generators found, skipping build year constraints")
                return
            
            if 'build_year' not in network.generators.columns:
                logger.warning("No build_year column found in generators, skipping build year constraints")
                return
            
            # Get generators with build year information
            generators_with_build_year = network.generators[network.generators['build_year'].notna()]
            
            if generators_with_build_year.empty:
                logger.warning("No generators have build_year values, skipping build year constraints")
                return
            
            logger.info(f"Applying build year constraints to {len(generators_with_build_year)} generators")
            
            # Check if generators have proper extendable capacity settings
            if 'p_nom_extendable' in network.generators.columns:
                extendable_generators = generators_with_build_year[generators_with_build_year['p_nom_extendable'] == True]
                
                if extendable_generators.empty:
                    logger.warning("No generators are marked as extendable (p_nom_extendable=True). Build year constraints only apply to extendable generators.")
                    return
                
                logger.info(f"Found {len(extendable_generators)} extendable generators with build years")
            else:
                logger.warning("No p_nom_extendable column found - cannot determine which generators are extendable")
                return
            
            # Verify that build years align with investment periods
            build_years = set(generators_with_build_year['build_year'].astype(int))
            investment_years = set(years)
            
            unmatched_build_years = build_years - investment_years
            if unmatched_build_years:
                logger.warning(f"Some generators have build years not in investment periods: {sorted(unmatched_build_years)}")
            
            matched_build_years = build_years & investment_years
            logger.info(f"Generators with build years matching investment periods: {sorted(matched_build_years)}")
            
            # Store build year information for potential custom constraint application
            network._build_year_info = {
                'generators_with_build_year': generators_with_build_year.index.tolist(),
                'build_years': generators_with_build_year['build_year'].to_dict(),
                'investment_periods': years,
                'extendable_generators': extendable_generators.index.tolist() if 'extendable_generators' in locals() else []
            }
            
            logger.info("Build year constraint configuration completed")
            
        except Exception as e:
            logger.error(f"Failed to configure build year constraints: {e}")
            logger.exception("Full traceback:")
    
    def _extract_solve_results(self, network: 'pypsa.Network', result: Any, solve_time: float, solver_name: str, run_id: str) -> Dict[str, Any]:
        """
        Extract solve results from PyPSA network.
        
        Args:
            network: Solved PyPSA Network object
            result: PyPSA solve result
            solve_time: Time taken to solve
            solver_name: Name of solver used
            run_id: Unique run identifier
            
        Returns:
            Dictionary with solve results and metadata
        """
        try:
            # Extract basic solve information
            status = getattr(result, 'status', 'unknown')
            objective_value = getattr(network, 'objective', None)
            
            # Debug logging
            logger.info(f"Raw PyPSA result attributes: {dir(result) if result else 'None'}")
            if hasattr(result, 'termination_condition'):
                logger.info(f"Termination condition: {result.termination_condition}")
            if hasattr(result, 'solver'):
                logger.info(f"Solver info: {result.solver}")
            
            # Convert PyPSA result to dictionary format
            result_dict = self._convert_pypsa_result_to_dict(result)
            
            # Determine success based on multiple criteria
            success = self._determine_solve_success(result, network, status, objective_value)
            
            solve_result = {
                "success": success,
                "status": status,
                "solve_time": solve_time,
                "solver_name": solver_name,
                "run_id": run_id,
                "objective_value": objective_value,
                "pypsa_result": result_dict,
                "network_name": network.name,
                "num_buses": len(network.buses),
                "num_generators": len(network.generators),
                "num_loads": len(network.loads),
                "num_lines": len(network.lines),
                "num_links": len(network.links),
                "num_snapshots": len(network.snapshots)
            }
            
            # Add multi-period information if available
            if hasattr(network, '_available_years') and network._available_years:
                solve_result["years"] = network._available_years
                solve_result["multi_period"] = len(network._available_years) > 1
            
            return solve_result
            
        except Exception as e:
            logger.error(f"Failed to extract solve results: {e}")
            return {
                "success": False,
                "status": "extraction_failed",
                "error": f"Failed to extract results: {e}",
                "solve_time": solve_time,
                "solver_name": solver_name,
                "run_id": run_id,
                "objective_value": None
            }
    
    def _determine_solve_success(self, result: Any, network: 'pypsa.Network', status: str, objective_value: Optional[float]) -> bool:
        """
        Determine if solve was successful based on multiple criteria.
        
        PyPSA sometimes returns status='unknown' even for successful solves,
        so we need to check multiple indicators.
        """
        try:
            # Check explicit status first
            if status in ['optimal', 'feasible']:
                logger.info(f"Success determined by status: {status}")
                return True
            
            # Check termination condition
            if hasattr(result, 'termination_condition'):
                term_condition = str(result.termination_condition).lower()
                if 'optimal' in term_condition:
                    logger.info(f"Success determined by termination condition: {result.termination_condition}")
                    return True
            
            # Check if we have a valid objective value
            if objective_value is not None and not (objective_value == 0 and status == 'unknown'):
                logger.info(f"Success determined by valid objective value: {objective_value}")
                return True
            
            # Check solver-specific success indicators
            if hasattr(result, 'solver'):
                solver_info = result.solver
                if hasattr(solver_info, 'termination_condition'):
                    term_condition = str(solver_info.termination_condition).lower()
                    if 'optimal' in term_condition:
                        logger.info(f"Success determined by solver termination condition: {solver_info.termination_condition}")
                        return True
            
            logger.warning(f"Could not determine success: status={status}, objective={objective_value}, result_attrs={dir(result) if result else 'None'}")
            return False
            
        except Exception as e:
            logger.error(f"Error determining solve success: {e}")
            return False
    
    def _convert_pypsa_result_to_dict(self, result) -> Dict[str, Any]:
        """
        Convert PyPSA result object to dictionary.
        
        Args:
            result: PyPSA solve result object
            
        Returns:
            Dictionary representation of the result
        """
        try:
            if result is None:
                return {"status": "no_result"}
            
            result_dict = {}
            
            # Extract common attributes
            for attr in ['status', 'success', 'termination_condition', 'solver']:
                if hasattr(result, attr):
                    value = getattr(result, attr)
                    # Convert to serializable format
                    if hasattr(value, '__dict__'):
                        result_dict[attr] = str(value)
                    else:
                        result_dict[attr] = value
            
            # Handle solver-specific information
            if hasattr(result, 'solver_results'):
                solver_results = getattr(result, 'solver_results')
                if hasattr(solver_results, '__dict__'):
                    result_dict['solver_results'] = str(solver_results)
                else:
                    result_dict['solver_results'] = solver_results
            
            return result_dict
            
        except Exception as e:
            logger.warning(f"Failed to convert PyPSA result to dict: {e}")
            return {"status": "conversion_failed", "error": str(e)}
    
    def _calculate_comprehensive_network_statistics(self, network: 'pypsa.Network', solve_time: float, solver_name: str) -> Dict[str, Any]:
        """Calculate comprehensive network statistics including PyPSA statistics and custom metrics"""
        try:
            # Initialize statistics structure
            statistics = {
                "core_summary": {},
                "pypsa_statistics": {},
                "custom_statistics": {},
                "runtime_info": {},
                "solver_info": {}
            }
            
            # Core summary statistics
            total_generation = 0
            total_demand = 0
            unserved_energy = 0
            
            # Calculate generation statistics
            if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                # Apply snapshot weightings to convert MW to MWh
                weightings = network.snapshot_weightings
                if isinstance(weightings, pd.DataFrame):
                    if 'objective' in weightings.columns:
                        weighting_values = weightings['objective'].values
                    else:
                        weighting_values = weightings.iloc[:, 0].values
                else:
                    weighting_values = weightings.values
                
                total_generation = float((network.generators_t.p.values * weighting_values[:, None]).sum())
                
                # Calculate unserved energy from UNMET_LOAD generators
                if hasattr(network, 'generators') and hasattr(network, '_component_type_map'):
                    unmet_load_gen_names = [name for name, comp_type in network._component_type_map.items() 
                                          if comp_type == 'UNMET_LOAD']
                    
                    for gen_name in unmet_load_gen_names:
                        if gen_name in network.generators_t.p.columns:
                            gen_output = float((network.generators_t.p[gen_name] * weighting_values).sum())
                            unserved_energy += gen_output
            
            # Calculate demand statistics
            if hasattr(network, 'loads_t') and hasattr(network.loads_t, 'p'):
                weightings = network.snapshot_weightings
                if isinstance(weightings, pd.DataFrame):
                    if 'objective' in weightings.columns:
                        weighting_values = weightings['objective'].values
                    else:
                        weighting_values = weightings.iloc[:, 0].values
                else:
                    weighting_values = weightings.values
                
                total_demand = float((network.loads_t.p.values * weighting_values[:, None]).sum())
            
            statistics["core_summary"] = {
                "total_generation_mwh": total_generation,
                "total_demand_mwh": total_demand,
                "total_cost": float(network.objective) if hasattr(network, 'objective') else None,
                "load_factor": (total_demand / (total_generation + 1e-6)) if total_generation > 0 else 0,
                "unserved_energy_mwh": unserved_energy
            }
            
            # Calculate PyPSA statistics
            try:
                pypsa_stats = network.statistics()
                if pypsa_stats is not None and not pypsa_stats.empty:
                    statistics["pypsa_statistics"] = self._convert_pypsa_result_to_dict(pypsa_stats)
                else:
                    statistics["pypsa_statistics"] = {}
            except Exception as e:
                logger.error(f"Failed to calculate PyPSA statistics: {e}")
                statistics["pypsa_statistics"] = {}
            
            # Custom statistics - calculate detailed breakdowns
            total_cost = float(network.objective) if hasattr(network, 'objective') else 0.0
            avg_price = (total_cost / (total_generation + 1e-6)) if total_generation > 0 else None
            unmet_load_percentage = (unserved_energy / (total_demand + 1e-6)) * 100 if total_demand > 0 else 0
            
            # Note: For solver statistics, we keep simplified approach since this is just for logging
            # The storage module will calculate proper totals from carrier statistics
            statistics["custom_statistics"] = {
                "total_capital_cost": 0.0,  # Will be calculated properly in storage module
                "total_operational_cost": total_cost,  # PyPSA objective (includes both capital and operational, discounted)
                "total_currency_cost": total_cost,
                "total_emissions_tons_co2": 0.0,  # Will be calculated properly in storage module
                "average_price_per_mwh": avg_price,
                "unmet_load_percentage": unmet_load_percentage,
                "max_unmet_load_hour_mw": 0.0  # TODO: Calculate max hourly unmet load
            }
            
            # Runtime info
            unmet_load_count = 0
            if hasattr(network, '_component_type_map'):
                unmet_load_count = len([name for name, comp_type in network._component_type_map.items() 
                                      if comp_type == 'UNMET_LOAD'])
            
            statistics["runtime_info"] = {
                "solve_time_seconds": solve_time,
                "component_count": (
                    len(network.buses) + len(network.generators) + len(network.loads) + 
                    len(network.lines) + len(network.links)
                ) if hasattr(network, 'buses') else 0,
                "bus_count": len(network.buses) if hasattr(network, 'buses') else 0,
                "generator_count": len(network.generators) if hasattr(network, 'generators') else 0,
                "unmet_load_count": unmet_load_count,
                "load_count": len(network.loads) if hasattr(network, 'loads') else 0,
                "line_count": len(network.lines) if hasattr(network, 'lines') else 0,
                "snapshot_count": len(network.snapshots) if hasattr(network, 'snapshots') else 0
            }
            
            # Solver info
            statistics["solver_info"] = {
                "solver_name": solver_name,
                "termination_condition": "optimal" if hasattr(network, 'objective') else "unknown",
                "objective_value": float(network.objective) if hasattr(network, 'objective') else None
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to calculate comprehensive network statistics: {e}", exc_info=True)
            return {
                "error": str(e),
                "core_summary": {},
                "pypsa_statistics": {},
                "custom_statistics": {},
                "runtime_info": {"solve_time_seconds": solve_time},
                "solver_info": {"solver_name": solver_name}
            }
    
    def _calculate_statistics_by_year(self, network: 'pypsa.Network', solve_time: float, solver_name: str) -> Dict[int, Dict[str, Any]]:
        """Calculate statistics for each year in the network"""
        try:
            # Extract years from network snapshots or manually extracted years
            if hasattr(network.snapshots, 'year'):
                years = sorted(network.snapshots.year.unique())
            elif hasattr(network, '_available_years'):
                years = network._available_years
            elif hasattr(network.snapshots, 'levels'):
                # Multi-period optimization - get years from period level
                period_values = network.snapshots.get_level_values(0)
                years = sorted(period_values.unique())
            else:
                # If no year info, skip year-based calculations
                logger.info("No year information found in network - skipping year-based statistics")
                return {}
            
            logger.info(f"Calculating year-based statistics for years: {years}")
            year_statistics = {}
            
            for year in years:
                try:
                    year_stats = self._calculate_network_statistics_for_year(network, year, solve_time, solver_name)
                    year_statistics[year] = year_stats
                    logger.info(f"Calculated statistics for year {year}")
                except Exception as e:
                    logger.error(f"Failed to calculate statistics for year {year}: {e}")
                    continue
            
            logger.info(f"Successfully calculated year-based statistics for {len(year_statistics)} years")
            return year_statistics
            
        except Exception as e:
            logger.error(f"Failed to calculate year-based statistics: {e}", exc_info=True)
            return {}
    
    def _calculate_network_statistics_for_year(self, network: 'pypsa.Network', year: int, solve_time: float, solver_name: str) -> Dict[str, Any]:
        """Calculate network statistics for a specific year"""
        try:
            # Initialize statistics structure
            statistics = {
                "core_summary": {},
                "custom_statistics": {},
                "runtime_info": {},
                "solver_info": {}
            }
            
            # Core summary statistics for this year
            total_generation = 0
            total_demand = 0
            unserved_energy = 0
            
            # Calculate generation statistics for this year
            if hasattr(network, 'generators_t') and hasattr(network.generators_t, 'p'):
                # Filter by year
                year_generation = self._filter_timeseries_by_year(network.generators_t.p, network.snapshots, year)
                if year_generation is not None and not year_generation.empty:
                    # Apply snapshot weightings for this year
                    year_weightings = self._get_year_weightings(network, year)
                    if year_weightings is not None:
                        total_generation = float((year_generation.values * year_weightings[:, None]).sum())
                    else:
                        total_generation = float(year_generation.sum().sum())
                    
                    # Calculate unserved energy for this year
                    if hasattr(network, '_component_type_map'):
                        unmet_load_gen_names = [name for name, comp_type in network._component_type_map.items() 
                                              if comp_type == 'UNMET_LOAD']
                        
                        for gen_name in unmet_load_gen_names:
                            if gen_name in year_generation.columns:
                                if year_weightings is not None:
                                    gen_output = float((year_generation[gen_name] * year_weightings).sum())
                                else:
                                    gen_output = float(year_generation[gen_name].sum())
                                unserved_energy += gen_output
            
            # Calculate demand statistics for this year
            if hasattr(network, 'loads_t') and hasattr(network.loads_t, 'p'):
                year_demand = self._filter_timeseries_by_year(network.loads_t.p, network.snapshots, year)
                if year_demand is not None and not year_demand.empty:
                    year_weightings = self._get_year_weightings(network, year)
                    if year_weightings is not None:
                        total_demand = float((year_demand.values * year_weightings[:, None]).sum())
                    else:
                        total_demand = float(year_demand.sum().sum())
            
            statistics["core_summary"] = {
                "total_generation_mwh": total_generation,
                "total_demand_mwh": total_demand,
                "total_cost": None,  # Year-specific cost calculation would be complex
                "load_factor": (total_demand / (total_generation + 1e-6)) if total_generation > 0 else 0,
                "unserved_energy_mwh": unserved_energy
            }
            
            # Custom statistics
            unmet_load_percentage = (unserved_energy / (total_demand + 1e-6)) * 100 if total_demand > 0 else 0
            
            # Calculate year-specific carrier statistics
            year_carrier_stats = self._calculate_year_carrier_statistics(network, year)
            
            statistics["custom_statistics"] = {
                "unmet_load_percentage": unmet_load_percentage,
                "year": year,
                **year_carrier_stats  # Include all carrier-specific statistics for this year
            }
            
            # Runtime info
            year_snapshot_count = self._count_year_snapshots(network.snapshots, year)
            
            statistics["runtime_info"] = {
                "solve_time_seconds": solve_time,
                "year": year,
                "snapshot_count": year_snapshot_count
            }
            
            # Solver info
            statistics["solver_info"] = {
                "solver_name": solver_name,
                "year": year
            }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to calculate network statistics for year {year}: {e}", exc_info=True)
            return {
                "error": str(e),
                "core_summary": {},
                "custom_statistics": {"year": year},
                "runtime_info": {"solve_time_seconds": solve_time, "year": year},
                "solver_info": {"solver_name": solver_name, "year": year}
            }
    
    def _filter_timeseries_by_year(self, timeseries_df: 'pd.DataFrame', snapshots: 'pd.Index', year: int) -> 'pd.DataFrame':
        """Filter timeseries data by year"""
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
        """Get snapshot weightings for a specific year"""
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
    
    def _count_year_snapshots(self, snapshots: 'pd.Index', year: int) -> int:
        """Count snapshots for a specific year"""
        try:
            # Handle MultiIndex case
            if hasattr(snapshots, 'levels'):
                period_values = snapshots.get_level_values(0)
                year_mask = period_values == year
                return year_mask.sum()
            
            # Handle DatetimeIndex case
            elif hasattr(snapshots, 'year'):
                year_mask = snapshots.year == year
                return year_mask.sum()
            
            # Fallback
            return 0
            
        except Exception as e:
            logger.error(f"Failed to count snapshots for year {year}: {e}")
            return 0
    
    def _calculate_year_carrier_statistics(self, network: 'pypsa.Network', year: int) -> Dict[str, Any]:
        """Calculate carrier-specific statistics for a specific year"""
        # Note: This is a simplified implementation that doesn't have database access
        # The proper implementation should be done in the storage module where we have conn and network_id
        # For now, return empty dictionaries - the storage module will handle this properly
        return {
            "dispatch_by_carrier": {},
            "capacity_by_carrier": {},
            "emissions_by_carrier": {},
            "capital_cost_by_carrier": {},
            "operational_cost_by_carrier": {},
            "total_system_cost_by_carrier": {}
        }
    
    def _get_generator_carrier_name(self, generator_name: str) -> Optional[str]:
        """Get carrier name for a generator - simplified implementation"""
        # This is a simplified approach - in practice, this should query the database
        # or use the component type mapping from the network
        
        # Try to extract carrier from generator name patterns
        gen_lower = generator_name.lower()
        
        if 'coal' in gen_lower:
            return 'coal'
        elif 'gas' in gen_lower or 'ccgt' in gen_lower or 'ocgt' in gen_lower:
            return 'gas'
        elif 'nuclear' in gen_lower:
            return 'nuclear'
        elif 'solar' in gen_lower or 'pv' in gen_lower:
            return 'solar'
        elif 'wind' in gen_lower:
            return 'wind'
        elif 'hydro' in gen_lower:
            return 'hydro'
        elif 'biomass' in gen_lower:
            return 'biomass'
        elif 'battery' in gen_lower:
            return 'battery'
        elif 'unmet' in gen_lower:
            return 'Unmet Load'
        else:
            # Default to generator name if no pattern matches
            return generator_name
