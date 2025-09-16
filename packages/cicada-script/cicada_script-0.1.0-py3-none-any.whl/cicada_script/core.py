"""
Core functionality for cicada_script package.

This module provides core utilities and configuration for the cicada_script package.
"""

import sys
import json
from typing import Dict, List, Any, Optional
from enum import Enum


class OutputMode(Enum):
    """Output modes for geometry creation."""
    PRINT = "print"  # Print geometry data to console
    JSON = "json"   # Output geometry as JSON
    FILE = "file"   # Save geometry to file
    CICADA = "cicada"  # Send to Cicada application (if available)


class CicadaScriptCore:
    """Core class managing cicada_script functionality."""
    
    def __init__(self):
        self.output_mode = OutputMode.PRINT
        self.output_file = None
        self.geometry_objects = []
        self.verbose = True
    
    def set_output_mode(self, mode: str, output_file: Optional[str] = None):
        """Set the output mode for geometry creation."""
        if mode.upper() in OutputMode.__members__:
            self.output_mode = OutputMode[mode.upper()]
            self.output_file = output_file
            if self.verbose:
                print(f"✅ Output mode set to: {mode}")
        else:
            raise ValueError(f"Invalid output mode: {mode}. Valid modes: {list(OutputMode.__members__.keys())}")
    
    def get_output_mode(self) -> str:
        """Get the current output mode."""
        return self.output_mode.value
    
    def add_geometry(self, geometry_type: str, parameters: Dict[str, Any]):
        """Add a geometry object to the collection."""
        geometry_obj = {
            'type': geometry_type,
            'parameters': parameters,
            'id': len(self.geometry_objects)
        }
        self.geometry_objects.append(geometry_obj)
        
        # Handle output based on current mode
        if self.output_mode == OutputMode.PRINT:
            self._print_geometry(geometry_obj)
        elif self.output_mode == OutputMode.JSON:
            self._output_json(geometry_obj)
        elif self.output_mode == OutputMode.FILE:
            self._output_file(geometry_obj)
        elif self.output_mode == OutputMode.CICADA:
            self._send_to_cicada(geometry_obj)
    
    def _print_geometry(self, geometry_obj: Dict[str, Any]):
        """Print geometry information to console."""
        print(f"🔵 Created {geometry_obj['type']} with parameters: {geometry_obj['parameters']}")
    
    def _output_json(self, geometry_obj: Dict[str, Any]):
        """Output geometry as JSON."""
        print(json.dumps(geometry_obj, indent=2))
    
    def _output_file(self, geometry_obj: Dict[str, Any]):
        """Save geometry to file."""
        if self.output_file:
            try:
                with open(self.output_file, 'a') as f:
                    json.dump(geometry_obj, f)
                    f.write('\n')
                if self.verbose:
                    print(f"💾 Saved {geometry_obj['type']} to {self.output_file}")
            except Exception as e:
                print(f"❌ Error saving to file: {e}")
    
    def _send_to_cicada(self, geometry_obj: Dict[str, Any]):
        """Send geometry to Cicada application (if available)."""
        # This would integrate with the actual Cicada application
        # For now, we'll just print a message
        print(f"📡 Sending {geometry_obj['type']} to Cicada application...")
        # Future implementation would use IPC, network calls, or direct C++ integration
    
    def clear_all(self):
        """Clear all geometry objects."""
        self.geometry_objects.clear()
        if self.verbose:
            print("🗑️ Cleared all geometry objects")
    
    def fit_view(self):
        """Fit view to show all geometry."""
        if self.verbose:
            print("🔍 Fitting view to show all geometry")
    
    def get_geometry_count(self) -> int:
        """Get the total number of geometry objects."""
        return len(self.geometry_objects)
    
    def get_all_geometry(self) -> List[Dict[str, Any]]:
        """Get all geometry objects."""
        return self.geometry_objects.copy()


# Global instance
_core_instance = CicadaScriptCore()

# Public API functions
def set_output_mode(mode: str, output_file: Optional[str] = None):
    """Set the output mode for geometry creation."""
    _core_instance.set_output_mode(mode, output_file)

def get_output_mode() -> str:
    """Get the current output mode."""
    return _core_instance.get_output_mode()

def clear_all():
    """Clear all geometry objects."""
    _core_instance.clear_all()

def fit_view():
    """Fit view to show all geometry."""
    _core_instance.fit_view()

def get_geometry_count() -> int:
    """Get the total number of geometry objects."""
    return _core_instance.get_geometry_count()

def get_all_geometry() -> List[Dict[str, Any]]:
    """Get all geometry objects."""
    return _core_instance.get_all_geometry()

# Internal function for adding geometry
def _add_geometry(geometry_type: str, parameters: Dict[str, Any]):
    """Internal function to add geometry objects."""
    _core_instance.add_geometry(geometry_type, parameters)
