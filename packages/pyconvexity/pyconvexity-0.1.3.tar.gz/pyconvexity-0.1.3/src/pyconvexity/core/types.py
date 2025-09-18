"""
Core data types for PyConvexity.

These types mirror the Rust implementation while providing Python-specific
enhancements and better type safety.
"""

import json
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union


class StaticValue:
    """
    Represents a static (non-time-varying) attribute value.
    
    Mirrors the Rust StaticValue enum while providing Python conveniences.
    Supports float, int, bool, and string values with proper type conversion.
    """
    
    def __init__(self, value: Union[float, int, bool, str]):
        # Check bool before int since bool is subclass of int in Python
        if isinstance(value, bool):
            self.data = {"Boolean": value}
        elif isinstance(value, float):
            self.data = {"Float": value}
        elif isinstance(value, int):
            self.data = {"Integer": value}
        elif isinstance(value, str):
            self.data = {"String": value}
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
    
    def to_json(self) -> str:
        """
        Return raw value as JSON to match Rust serialization format.
        
        Rust stores: 123.45, 42, true, "hello"
        Not: {"Float": 123.45}, {"Integer": 42}, etc.
        """
        if "Float" in self.data:
            return json.dumps(self.data["Float"])
        elif "Integer" in self.data:
            return json.dumps(self.data["Integer"])
        elif "Boolean" in self.data:
            return json.dumps(self.data["Boolean"])
        elif "String" in self.data:
            return json.dumps(self.data["String"])
        else:
            # Fallback to original format if unknown
            return json.dumps(self.data)
    
    def data_type(self) -> str:
        """Get data type name - mirrors Rust implementation"""
        if "Float" in self.data:
            return "float"
        elif "Integer" in self.data:
            return "int"
        elif "Boolean" in self.data:
            return "boolean"
        elif "String" in self.data:
            return "string"
        else:
            return "unknown"
    
    def as_f64(self) -> float:
        """Convert to float, mirroring Rust implementation"""
        if "Float" in self.data:
            return self.data["Float"]
        elif "Integer" in self.data:
            return float(self.data["Integer"])
        elif "Boolean" in self.data:
            return 1.0 if self.data["Boolean"] else 0.0
        else:
            try:
                return float(self.data["String"])
            except ValueError:
                return 0.0
    
    def value(self) -> Union[float, int, bool, str]:
        """Get the raw Python value"""
        if "Float" in self.data:
            return self.data["Float"]
        elif "Integer" in self.data:
            return self.data["Integer"]
        elif "Boolean" in self.data:
            return self.data["Boolean"]
        elif "String" in self.data:
            return self.data["String"]
        else:
            raise ValueError("Unknown data type in StaticValue")
    
    def __repr__(self) -> str:
        return f"StaticValue({self.value()})"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, StaticValue):
            return self.data == other.data
        return False


@dataclass
class TimeseriesPoint:
    """
    A single point in a time series.
    
    Mirrors Rust TimeseriesPoint with exact field matching.
    """
    timestamp: int
    value: float
    period_index: int
    
    def __post_init__(self):
        # Ensure types are correct
        self.timestamp = int(self.timestamp)
        self.value = float(self.value)
        self.period_index = int(self.period_index)


@dataclass
class TimePeriod:
    """
    Represents a time period in the network's time axis.
    
    Mirrors Rust TimePeriod structure.
    """
    timestamp: int
    period_index: int
    formatted_time: str


@dataclass
class TimeseriesValidationResult:
    """
    Result of validating timeseries alignment with network time periods.
    
    Mirrors Rust TimeseriesValidationResult.
    """
    is_valid: bool
    missing_periods: List[int]
    extra_periods: List[int]
    total_network_periods: int
    provided_periods: int


@dataclass
class ValidationRule:
    """
    Validation rule for component attributes.
    
    Mirrors Rust ValidationRule with all fields.
    """
    component_type: str
    attribute_name: str
    data_type: str
    unit: Optional[str]
    default_value_string: Optional[str]
    allowed_storage_types: str
    allows_static: bool
    allows_timeseries: bool
    is_required: bool
    is_input: bool
    description: Optional[str]
    default_value: Optional[StaticValue]


class AttributeValue:
    """
    Represents either a static value or timeseries data for a component attribute.
    
    Mirrors Rust AttributeValue enum.
    """
    
    def __init__(self, value: Union[StaticValue, List[TimeseriesPoint]]):
        if isinstance(value, StaticValue):
            self.variant = "Static"
            self.static_value = value
            self.timeseries_value = None
        elif isinstance(value, list) and all(isinstance(p, TimeseriesPoint) for p in value):
            self.variant = "Timeseries"
            self.static_value = None
            self.timeseries_value = value
        else:
            raise ValueError(
                f"AttributeValue must be StaticValue or List[TimeseriesPoint], got {type(value)}"
            )
    
    @classmethod
    def static(cls, value: StaticValue) -> 'AttributeValue':
        """Create a static attribute value"""
        return cls(value)
    
    @classmethod
    def timeseries(cls, points: List[TimeseriesPoint]) -> 'AttributeValue':
        """Create a timeseries attribute value"""
        return cls(points)
    
    def is_static(self) -> bool:
        """Check if this is a static value"""
        return self.variant == "Static"
    
    def is_timeseries(self) -> bool:
        """Check if this is a timeseries value"""
        return self.variant == "Timeseries"
    
    def __repr__(self) -> str:
        if self.is_static():
            return f"AttributeValue.static({self.static_value})"
        else:
            return f"AttributeValue.timeseries({len(self.timeseries_value)} points)"


@dataclass
class Component:
    """
    Represents a component in the energy system model.
    
    Mirrors Rust Component struct exactly.
    """
    id: int
    network_id: int
    component_type: str
    name: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    carrier_id: Optional[int] = None
    bus_id: Optional[int] = None
    bus0_id: Optional[int] = None
    bus1_id: Optional[int] = None


@dataclass
class Network:
    """
    Represents a network/model in the system.
    
    Enhanced version of network information with additional metadata.
    """
    id: int
    name: str
    description: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    time_interval: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class CreateComponentRequest:
    """
    Request structure for creating a new component.
    
    Mirrors Rust CreateComponentRequest.
    """
    network_id: int
    component_type: str
    name: str
    description: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    carrier_id: Optional[int] = None
    bus_id: Optional[int] = None
    bus0_id: Optional[int] = None
    bus1_id: Optional[int] = None


@dataclass
class CreateNetworkRequest:
    """
    Request structure for creating a new network.
    
    Mirrors Rust CreateNetworkRequest.
    """
    name: str
    description: Optional[str] = None
    time_resolution: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


@dataclass
class Carrier:
    """
    Represents an energy carrier (e.g., electricity, heat, gas).
    """
    id: int
    network_id: int
    name: str
    co2_emissions: float = 0.0
    color: Optional[str] = None
    nice_name: Optional[str] = None


@dataclass
class Scenario:
    """
    Represents a scenario within a network.
    """
    id: int
    network_id: int
    name: str
    description: Optional[str] = None
    is_master: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
