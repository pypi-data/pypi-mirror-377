-- ============================================================================
-- DATA STORAGE AND METADATA SCHEMA
-- Auxiliary tables for data storage, notes, audit logging, and analysis caching
-- Optimized for atomic operations and data management
-- Version 2.1.0
-- ============================================================================

-- ============================================================================
-- GENERIC DATA STORAGE
-- ============================================================================

-- Generic data store for arbitrary network-level data
-- Supports storing configuration, results, statistics, scripts, etc.
CREATE TABLE network_data_store (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER NOT NULL,
    category TEXT NOT NULL,          -- 'config', 'results', 'statistics', 'scripts', etc.
    name TEXT NOT NULL,              -- Specific name within category
    data_format TEXT DEFAULT 'json', -- 'json', 'parquet', 'csv', 'binary', 'text'
    data BLOB NOT NULL,              -- Serialized data
    metadata TEXT,                   -- JSON metadata about the data
    checksum TEXT,                   -- Data integrity hash
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    CONSTRAINT fk_datastore_network 
        FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
    CONSTRAINT uq_datastore_network_category_name 
        UNIQUE (network_id, category, name),
    CONSTRAINT valid_data_format 
        CHECK (data_format IN ('json', 'parquet', 'csv', 'binary', 'text', 'yaml', 'toml'))
);

-- Optimized indexes for data retrieval
CREATE INDEX idx_datastore_network ON network_data_store(network_id);
CREATE INDEX idx_datastore_category ON network_data_store(network_id, category);
CREATE INDEX idx_datastore_name ON network_data_store(network_id, category, name);
CREATE INDEX idx_datastore_created_at ON network_data_store(created_at);
CREATE INDEX idx_datastore_format ON network_data_store(data_format);

-- ============================================================================
-- DOCUMENTATION AND NOTES
-- ============================================================================

-- Network-level notes and documentation
CREATE TABLE network_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT,                       -- JSON array of tags
    note_type TEXT DEFAULT 'note',   -- 'note', 'todo', 'warning', 'info'
    priority INTEGER DEFAULT 0,     -- 0=normal, 1=high, -1=low
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    CONSTRAINT fk_notes_network 
        FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
    CONSTRAINT valid_note_type 
        CHECK (note_type IN ('note', 'todo', 'warning', 'info', 'doc'))
);

CREATE INDEX idx_notes_network ON network_notes(network_id);
CREATE INDEX idx_notes_title ON network_notes(network_id, title);
CREATE INDEX idx_notes_type ON network_notes(note_type);
CREATE INDEX idx_notes_priority ON network_notes(priority);
CREATE INDEX idx_notes_created_at ON network_notes(created_at);

-- Component-specific notes and documentation
CREATE TABLE component_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    tags TEXT,                       -- JSON array of tags
    note_type TEXT DEFAULT 'note',   -- 'note', 'todo', 'warning', 'info'
    priority INTEGER DEFAULT 0,     -- 0=normal, 1=high, -1=low
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    CONSTRAINT fk_component_notes_component 
        FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE,
    CONSTRAINT valid_component_note_type 
        CHECK (note_type IN ('note', 'todo', 'warning', 'info', 'doc'))
);

CREATE INDEX idx_component_notes_component ON component_notes(component_id);
CREATE INDEX idx_component_notes_title ON component_notes(component_id, title);
CREATE INDEX idx_component_notes_type ON component_notes(note_type);
CREATE INDEX idx_component_notes_priority ON component_notes(priority);
CREATE INDEX idx_component_notes_created_at ON component_notes(created_at);

-- ============================================================================
-- AUDIT AND CHANGE TRACKING
-- ============================================================================

-- Comprehensive audit log for tracking all database changes
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER,
    table_name TEXT NOT NULL,
    record_id INTEGER,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    
    -- Change data
    old_values TEXT,                 -- JSON of old values for UPDATE/DELETE
    new_values TEXT,                 -- JSON of new values for INSERT/UPDATE
    change_summary TEXT,             -- Human-readable summary of changes
    affected_fields TEXT,            -- JSON array of changed field names
    
    -- Context and metadata
    user_id TEXT,
    session_id TEXT,
    client_info TEXT,                -- Application version, client type, etc.
    transaction_id TEXT,             -- For grouping related changes
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance metrics
    execution_time_ms INTEGER,       -- Time taken for the operation
    
    CONSTRAINT fk_audit_network 
        FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE
);

-- Optimized indexes for audit queries
CREATE INDEX idx_audit_network ON audit_log(network_id);
CREATE INDEX idx_audit_table ON audit_log(table_name);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_operation ON audit_log(operation);
CREATE INDEX idx_audit_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_session ON audit_log(session_id);
CREATE INDEX idx_audit_transaction ON audit_log(transaction_id);

-- Change summary view for recent activity
CREATE VIEW recent_changes AS
SELECT 
    al.id,
    al.network_id,
    n.name as network_name,
    al.table_name,
    al.record_id,
    al.operation,
    al.change_summary,
    al.user_id,
    al.timestamp,
    al.execution_time_ms
FROM audit_log al
LEFT JOIN networks n ON al.network_id = n.id
ORDER BY al.timestamp DESC
LIMIT 1000;

-- ============================================================================
-- NETWORK ANALYSIS AND RESULTS CACHING
-- ============================================================================

-- Cache for storing analysis results and computed data
-- This improves performance by avoiding recomputation of expensive operations
CREATE TABLE network_analysis_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER NOT NULL,
    analysis_type TEXT NOT NULL,     -- 'optimization', 'statistics', 'validation', 'powerflow', etc.
    analysis_key TEXT NOT NULL,      -- Unique key for this analysis (hash of inputs)
    analysis_version TEXT,           -- Version of analysis algorithm
    
    -- Input tracking
    input_hash TEXT,                 -- Hash of inputs that generated this result
    input_summary TEXT,              -- Human-readable summary of inputs
    dependencies TEXT,               -- JSON array of dependent data (components, attributes, etc.)
    
    -- Results storage
    result_data BLOB NOT NULL,       -- Serialized results (typically JSON or Parquet)
    result_format TEXT DEFAULT 'json', -- 'json', 'parquet', 'csv', 'binary'
    result_summary TEXT,             -- Human-readable summary of results
    result_size_bytes INTEGER,       -- Size of result data for management
    
    -- Analysis metadata
    analysis_time_ms INTEGER,        -- Time taken for analysis
    status TEXT DEFAULT 'completed', -- 'completed', 'failed', 'in_progress', 'stale'
    error_message TEXT,              -- If status is 'failed'
    warnings TEXT,                   -- JSON array of warnings
    
    -- Cache management
    hit_count INTEGER DEFAULT 0,     -- Number of times this cache entry was used
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,             -- Optional expiration for cache cleanup
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    
    CONSTRAINT fk_analysis_cache_network 
        FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
    CONSTRAINT uq_analysis_cache_key 
        UNIQUE (network_id, analysis_type, analysis_key),
    CONSTRAINT valid_analysis_status 
        CHECK (status IN ('completed', 'failed', 'in_progress', 'stale')),
    CONSTRAINT valid_result_format 
        CHECK (result_format IN ('json', 'parquet', 'csv', 'binary', 'text'))
);

-- Optimized indexes for cache operations
CREATE INDEX idx_analysis_cache_network ON network_analysis_cache(network_id);
CREATE INDEX idx_analysis_cache_type ON network_analysis_cache(network_id, analysis_type);
CREATE INDEX idx_analysis_cache_key ON network_analysis_cache(analysis_key);
CREATE INDEX idx_analysis_cache_status ON network_analysis_cache(status);
CREATE INDEX idx_analysis_cache_expires ON network_analysis_cache(expires_at);
CREATE INDEX idx_analysis_cache_accessed ON network_analysis_cache(last_accessed);
CREATE INDEX idx_analysis_cache_created ON network_analysis_cache(created_at);
CREATE INDEX idx_analysis_cache_size ON network_analysis_cache(result_size_bytes);

-- ============================================================================
-- SOLVE RESULTS AND STATISTICS
-- ============================================================================

-- Drop the old optimization_results table
DROP TABLE IF EXISTS optimization_results;

-- Network solve results - stores solver outputs and statistics
-- This is where PyPSA solve results are stored after successful solves
CREATE TABLE network_solve_results (
    network_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,  -- References scenarios table (master scenario has explicit ID)
    
    -- Solve metadata
    solved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    solver_name TEXT NOT NULL,          -- 'highs', 'gurobi', 'cplex', etc.
    solve_type TEXT NOT NULL,           -- 'pypsa_optimization', 'monte_carlo', 'sensitivity', etc.
    solve_status TEXT NOT NULL,         -- 'optimal', 'infeasible', 'unbounded', etc.
    objective_value REAL,               -- Objective function value
    solve_time_seconds REAL,            -- Time taken to solve
    
    -- Everything else stored as JSON for maximum flexibility
    results_json TEXT NOT NULL,         -- All results, statistics, whatever the solver produces
    metadata_json TEXT,                 -- Solver settings, input parameters, build info
    
    PRIMARY KEY (network_id, scenario_id),
    
    FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_solve_results_network ON network_solve_results(network_id);
CREATE INDEX idx_solve_results_scenario ON network_solve_results(scenario_id);
CREATE INDEX idx_solve_results_status ON network_solve_results(solve_status);
CREATE INDEX idx_solve_results_solved_at ON network_solve_results(solved_at);

-- ============================================================================
-- YEAR-BASED SOLVE RESULTS
-- ============================================================================

-- Year-based solve results - stores solver outputs and statistics by year
-- This enables capacity expansion analysis and year-over-year comparisons
CREATE TABLE network_solve_results_by_year (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    network_id INTEGER NOT NULL,
    scenario_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    
    -- Year-specific statistics (same structure as main results but year-specific)
    results_json TEXT NOT NULL,         -- All results, statistics for this year only
    metadata_json TEXT,                 -- Solver settings, input parameters for this year
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_solve_results_year_network 
        FOREIGN KEY (network_id) REFERENCES networks(id) ON DELETE CASCADE,
    CONSTRAINT fk_solve_results_year_scenario 
        FOREIGN KEY (scenario_id) REFERENCES scenarios(id) ON DELETE CASCADE,
    CONSTRAINT uq_solve_results_year_unique 
        UNIQUE (network_id, scenario_id, year),
    CONSTRAINT valid_year CHECK (year >= 1900 AND year <= 2100)
);

-- Indexes for performance
CREATE INDEX idx_solve_results_year_network ON network_solve_results_by_year(network_id);
CREATE INDEX idx_solve_results_year_scenario ON network_solve_results_by_year(scenario_id);
CREATE INDEX idx_solve_results_year_year ON network_solve_results_by_year(year);
CREATE INDEX idx_solve_results_year_network_scenario ON network_solve_results_by_year(network_id, scenario_id);
CREATE INDEX idx_solve_results_year_created_at ON network_solve_results_by_year(created_at);

-- Optional: Registry of solve type schemas for frontend introspection
CREATE TABLE solve_type_schemas (
    solve_type TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    description TEXT,
    json_schema TEXT,                   -- JSON Schema describing the expected structure
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/*
SUGGESTED JSON STRUCTURE FOR results_json:

For PyPSA optimization (solve_type = 'pypsa_optimization'):
{
  "core_summary": {
    "total_generation_mwh": 12500.0,
    "total_demand_mwh": 12000.0,
    "total_cost": 1500000.0,
    "load_factor": 0.96,
    "unserved_energy_mwh": 0.0
  },
  
  "pypsa_statistics": {
    "energy_balance": {
      "gas": 5000.0,
      "wind": 7500.0,
      "solar": 0.0
    },
    "supply_by_carrier": {
      "gas": {"total_mwh": 5000.0, "capacity_factor": 0.85},
      "wind": {"total_mwh": 7500.0, "capacity_factor": 0.42}
    },
    "demand_by_carrier": {
      "electricity": 12000.0
    },
    "capacity_factors": {
      "generator_gas_001": 0.85,
      "generator_wind_001": 0.42
    },
    "curtailment": {
      "wind": 250.0,
      "solar": 0.0
    },
    "transmission_utilization": {
      "line_001": 0.75,
      "line_002": 0.32
    }
  },
  
  "custom_statistics": {
    "emissions_by_carrier": {
      "gas": 2500.0,
      "wind": 0.0,
      "solar": 0.0
    },
    "total_emissions_tons_co2": 2500.0,
    "average_price_per_mwh": 125.0,
    "peak_demand_mw": 2500.0,
    "renewable_fraction": 0.6
  },
  
  "runtime_info": {
    "build_time_seconds": 5.2,
    "solve_time_seconds": 45.1,
    "result_processing_seconds": 2.3,
    "component_count": 150,
    "variable_count": 8760,
    "constraint_count": 12500,
    "memory_usage_mb": 256.5
  },
  
  "solver_info": {
    "solver_name": "highs",
    "solver_version": "1.6.0",
    "solver_options": {"presolve": "on", "parallel": "on"},
    "termination_condition": "optimal",
    "iterations": 1247,
    "barrier_iterations": null
  }
}

For Monte Carlo sampling (solve_type = 'monte_carlo'):
{
  "core_summary": {
    "scenario_count": 1000,
    "convergence_achieved": true,
    "confidence_level": 0.95
  },
  
  "probability_distributions": {
    "total_cost": {
      "mean": 1500000.0,
      "std": 150000.0,
      "p05": 1250000.0,
      "p50": 1500000.0,
      "p95": 1750000.0
    },
    "unserved_energy": {
      "mean": 12.5,
      "std": 25.2,
      "p05": 0.0,
      "p50": 0.0,
      "p95": 75.0
    }
  },
  
  "sensitivity_analysis": {
    "most_influential_parameters": [
      {"parameter": "wind_capacity", "sensitivity": 0.85},
      {"parameter": "fuel_price", "sensitivity": 0.72}
    ]
  },
  
  "runtime_info": {
    "total_runtime_seconds": 3600.0,
    "scenarios_per_second": 0.28
  }
}

For sensitivity analysis (solve_type = 'sensitivity'):
{
  "core_summary": {
    "parameters_analyzed": 15,
    "base_case_objective": 1500000.0
  },
  
  "parameter_sensitivities": {
    "fuel_cost_gas": {
      "sensitivity_coefficient": 0.85,
      "objective_range": [1200000.0, 1800000.0],
      "parameter_range": [50.0, 150.0]
    },
    "wind_capacity": {
      "sensitivity_coefficient": -0.72,
      "objective_range": [1300000.0, 1700000.0],
      "parameter_range": [1000.0, 3000.0]
    }
  },
  
  "tornado_chart_data": [
    {"parameter": "fuel_cost_gas", "low": -300000.0, "high": 300000.0},
    {"parameter": "wind_capacity", "low": -200000.0, "high": 200000.0}
  ]
}
*/

-- ============================================================================
-- DATA MANAGEMENT TRIGGERS
-- ============================================================================

-- Note: Access tracking for analysis cache would need to be handled in application code
-- SQLite doesn't support AFTER SELECT triggers

-- Note: Result size calculation should be handled in application code
-- Cannot modify NEW values in SQLite BEFORE INSERT triggers

-- Note: Timestamp updates should be handled in application code or with DEFAULT CURRENT_TIMESTAMP
-- SQLite triggers cannot update the same record being modified without recursion issues

-- ============================================================================
-- UTILITY VIEWS
-- ============================================================================

-- View for network analysis summary
CREATE VIEW network_analysis_summary AS
SELECT 
    n.id as network_id,
    n.name as network_name,
    COUNT(DISTINCT nac.analysis_type) as analysis_types_count,
    COUNT(nac.id) as total_cache_entries,
    SUM(nac.hit_count) as total_cache_hits,
    SUM(nac.result_size_bytes) as total_cache_size_bytes,
    MAX(nac.last_accessed) as last_analysis_accessed,
    COUNT(or1.id) as optimization_runs_count,
    MAX(or1.created_at) as last_optimization_run
FROM networks n
LEFT JOIN network_analysis_cache nac ON n.id = nac.network_id
LEFT JOIN optimization_results or1 ON n.id = or1.network_id
GROUP BY n.id, n.name;

-- View for recent network activity
CREATE VIEW network_activity_summary AS
SELECT 
    n.id as network_id,
    n.name as network_name,
    COUNT(DISTINCT c.id) as components_count,
    COUNT(DISTINCT ca.id) as attributes_count,
    COUNT(DISTINCT nn.id) as notes_count,
    COUNT(DISTINCT nds.id) as data_store_entries_count,
    MAX(c.updated_at) as last_component_update,
    MAX(ca.updated_at) as last_attribute_update,
    MAX(nn.updated_at) as last_note_update,
    MAX(nds.updated_at) as last_data_update
FROM networks n
LEFT JOIN components c ON n.id = c.network_id
LEFT JOIN component_attributes ca ON c.id = ca.component_id
LEFT JOIN network_notes nn ON n.id = nn.network_id
LEFT JOIN network_data_store nds ON n.id = nds.network_id
GROUP BY n.id, n.name;

-- ============================================================================
-- CONNECTIVITY VIEWS - Human-readable bus connections
-- ============================================================================

-- View for components with single bus connections (generators, loads, etc.)
CREATE VIEW components_with_bus AS
SELECT 
    c.*,
    b.name as bus_name
FROM components c
LEFT JOIN components b ON json_extract(c.connectivity, '$.bus_id') = b.id AND b.component_type = 'BUS'
WHERE c.component_type IN ('GENERATOR', 'LOAD', 'STORAGE_UNIT', 'STORE');

-- View for components with dual bus connections (lines, links)
CREATE VIEW components_with_buses AS
SELECT 
    c.*,
    b0.name as bus0_name,
    b1.name as bus1_name
FROM components c
LEFT JOIN components b0 ON json_extract(c.connectivity, '$.bus0_id') = b0.id AND b0.component_type = 'BUS'
LEFT JOIN components b1 ON json_extract(c.connectivity, '$.bus1_id') = b1.id AND b1.component_type = 'BUS'
WHERE c.component_type IN ('LINE', 'LINK');

-- Unified view for all components with resolved bus connections
CREATE VIEW components_with_connectivity AS
SELECT 
    c.*,
    CASE 
        WHEN c.component_type = 'BUS' THEN NULL
        WHEN c.component_type IN ('GENERATOR', 'LOAD', 'STORAGE_UNIT', 'STORE') THEN 
            (SELECT b.name FROM components b WHERE b.id = json_extract(c.connectivity, '$.bus_id') AND b.component_type = 'BUS')
        ELSE NULL
    END as bus_name,
    CASE 
        WHEN c.component_type IN ('LINE', 'LINK') THEN 
            (SELECT b.name FROM components b WHERE b.id = json_extract(c.connectivity, '$.bus0_id') AND b.component_type = 'BUS')
        ELSE NULL
    END as bus0_name,
    CASE 
        WHEN c.component_type IN ('LINE', 'LINK') THEN 
            (SELECT b.name FROM components b WHERE b.id = json_extract(c.connectivity, '$.bus1_id') AND b.component_type = 'BUS')
        ELSE NULL
    END as bus1_name
FROM components c;

-- ============================================================================
-- DEFAULT CARRIERS SETUP
-- ============================================================================

-- Note: Default carriers will be created automatically when a network is created
-- This is handled in the application code to ensure proper network_id assignment
-- The default carriers are:
-- - AC (default for electrical buses and components)
-- - DC (for DC electrical systems)  
-- - heat (for heating systems)
-- - gas (for gas systems)
-- - electricity (generic electrical carrier)

-- These carriers follow PyPSA conventions and ensure all components can have
-- appropriate carrier assignments without requiring manual setup