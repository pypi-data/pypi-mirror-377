"""
Tests for cicada_script.core module.
"""

import pytest
import json
import tempfile
import os
from cicada_script.core import (
    set_output_mode,
    get_output_mode, 
    clear_all,
    fit_view,
    get_geometry_count,
    get_all_geometry,
    _add_geometry
)


class TestOutputModes:
    """Tests for output mode functionality."""
    
    def setup_method(self):
        """Reset to default state before each test."""
        clear_all()
        set_output_mode("print")
    
    def test_set_get_output_mode_print(self):
        """Test setting and getting print output mode."""
        set_output_mode("print")
        assert get_output_mode() == "print"
    
    def test_set_get_output_mode_json(self):
        """Test setting and getting JSON output mode."""
        set_output_mode("json")
        assert get_output_mode() == "json"
    
    def test_set_get_output_mode_file(self):
        """Test setting and getting file output mode."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            set_output_mode("file", temp_file)
            assert get_output_mode() == "file"
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_set_get_output_mode_cicada(self):
        """Test setting and getting cicada output mode."""
        set_output_mode("cicada")
        assert get_output_mode() == "cicada"
    
    def test_invalid_output_mode(self):
        """Test setting invalid output mode raises error."""
        with pytest.raises(ValueError, match="Invalid output mode"):
            set_output_mode("invalid")


class TestGeometryManagement:
    """Tests for geometry object management."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
        set_output_mode("print")  # Use quiet mode for testing
    
    def test_clear_all(self):
        """Test clearing all geometry objects."""
        _add_geometry("sphere", {"origin": [0, 0, 0], "radius": 5.0})
        _add_geometry("sphere", {"origin": [10, 0, 0], "radius": 3.0})
        assert get_geometry_count() == 2
        
        clear_all()
        assert get_geometry_count() == 0
    
    def test_get_geometry_count_empty(self):
        """Test geometry count when empty."""
        assert get_geometry_count() == 0
    
    def test_get_geometry_count_with_objects(self):
        """Test geometry count with objects."""
        _add_geometry("sphere", {"origin": [0, 0, 0], "radius": 5.0})
        assert get_geometry_count() == 1
        
        _add_geometry("sphere", {"origin": [10, 0, 0], "radius": 3.0})
        assert get_geometry_count() == 2
    
    def test_get_all_geometry(self):
        """Test getting all geometry objects."""
        sphere1_params = {"origin": [0, 0, 0], "radius": 5.0}
        sphere2_params = {"origin": [10, 0, 0], "radius": 3.0}
        
        _add_geometry("sphere", sphere1_params)
        _add_geometry("sphere", sphere2_params)
        
        all_geometry = get_all_geometry()
        assert len(all_geometry) == 2
        assert all_geometry[0]["type"] == "sphere"
        assert all_geometry[0]["parameters"] == sphere1_params
        assert all_geometry[1]["type"] == "sphere"
        assert all_geometry[1]["parameters"] == sphere2_params
    
    def test_add_geometry_assigns_ids(self):
        """Test that geometry objects get unique IDs."""
        _add_geometry("sphere", {"origin": [0, 0, 0], "radius": 5.0})
        _add_geometry("sphere", {"origin": [10, 0, 0], "radius": 3.0})
        
        all_geometry = get_all_geometry()
        assert all_geometry[0]["id"] == 0
        assert all_geometry[1]["id"] == 1


class TestFileOutput:
    """Tests for file output functionality."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_file_output_creates_file(self):
        """Test that file output creates and writes to file."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Remove the file so we can test creation
            os.unlink(temp_file)
            
            set_output_mode("file", temp_file)
            _add_geometry("sphere", {"origin": [0, 0, 0], "radius": 5.0})
            
            # Check file was created and has content
            assert os.path.exists(temp_file)
            
            with open(temp_file, 'r') as f:
                content = f.read().strip()
                assert content  # File should have content
                
                # Parse the JSON line
                geometry_obj = json.loads(content)
                assert geometry_obj["type"] == "sphere"
                assert geometry_obj["parameters"]["origin"] == [0, 0, 0]
                assert geometry_obj["parameters"]["radius"] == 5.0
                
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_file_output_appends_multiple_objects(self):
        """Test that file output appends multiple geometry objects."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            # Remove the file so we can test creation
            os.unlink(temp_file)
            
            set_output_mode("file", temp_file)
            _add_geometry("sphere", {"origin": [0, 0, 0], "radius": 5.0})
            _add_geometry("sphere", {"origin": [10, 0, 0], "radius": 3.0})
            
            # Check file has both objects
            with open(temp_file, 'r') as f:
                lines = f.read().strip().split('\n')
                assert len(lines) == 2
                
                obj1 = json.loads(lines[0])
                obj2 = json.loads(lines[1])
                
                assert obj1["parameters"]["radius"] == 5.0
                assert obj2["parameters"]["radius"] == 3.0
                
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def setup_method(self):
        """Reset state before each test."""
        clear_all()
        set_output_mode("print")
    
    def test_fit_view(self):
        """Test fit_view function runs without error."""
        # This is mainly a smoke test since fit_view just prints
        fit_view()  # Should not raise any exceptions
    
    def test_get_all_geometry_returns_copy(self):
        """Test that get_all_geometry returns a copy, not the original list."""
        _add_geometry("sphere", {"origin": [0, 0, 0], "radius": 5.0})
        
        geometry1 = get_all_geometry()
        geometry2 = get_all_geometry()
        
        # Should be equal but not the same object
        assert geometry1 == geometry2
        assert geometry1 is not geometry2
        
        # Modifying one shouldn't affect the other
        geometry1.append({"test": "object"})
        assert len(geometry2) == 1  # Should still be original length
