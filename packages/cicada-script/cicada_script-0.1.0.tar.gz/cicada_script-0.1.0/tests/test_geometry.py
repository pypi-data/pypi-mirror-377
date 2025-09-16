"""
Tests for cicada_script.geometry module.
"""

import pytest
import math
from cicada_script.geometry import (
    sphere,
    create_spiral_spheres,
    create_double_helix, 
    create_fibonacci_spheres,
    create_tower,
    create_sine_wave_spheres,
    create_grid_spheres,
    create_random_spheres
)
from cicada_script.core import get_geometry_count, clear_all


class TestSphere:
    """Tests for sphere function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_sphere_basic(self):
        """Test basic sphere creation."""
        sphere([0, 0, 0], 5.0)
        assert get_geometry_count() == 1
    
    def test_sphere_list_origin(self):
        """Test sphere with list origin."""
        sphere([10, 20, 30], 15.0)
        assert get_geometry_count() == 1
    
    def test_sphere_tuple_origin(self):
        """Test sphere with tuple origin.""" 
        sphere((5, 10, 15), 8.0)
        assert get_geometry_count() == 1
    
    def test_sphere_invalid_origin_length(self):
        """Test sphere with invalid origin length."""
        with pytest.raises(ValueError, match="Origin must be a list or tuple of 3 numbers"):
            sphere([0, 0], 5.0)
    
    def test_sphere_invalid_origin_type(self):
        """Test sphere with invalid origin type."""
        with pytest.raises(ValueError, match="Origin must be a list or tuple of 3 numbers"):
            sphere("invalid", 5.0)
    
    def test_sphere_negative_radius(self):
        """Test sphere with negative radius."""
        with pytest.raises(ValueError, match="Radius must be a positive number"):
            sphere([0, 0, 0], -5.0)
    
    def test_sphere_zero_radius(self):
        """Test sphere with zero radius."""
        with pytest.raises(ValueError, match="Radius must be a positive number"):
            sphere([0, 0, 0], 0.0)


class TestSpiralSpheres:
    """Tests for create_spiral_spheres function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_spiral_basic(self):
        """Test basic spiral creation."""
        create_spiral_spheres(5, 2.0, 20.0, 10.0)
        assert get_geometry_count() == 5
    
    def test_spiral_defaults(self):
        """Test spiral with default parameters."""
        create_spiral_spheres()
        assert get_geometry_count() == 10  # default count
    
    def test_spiral_invalid_count(self):
        """Test spiral with invalid count."""
        with pytest.raises(ValueError, match="Count must be positive"):
            create_spiral_spheres(0)
    
    def test_spiral_invalid_radius(self):
        """Test spiral with invalid radius."""
        with pytest.raises(ValueError, match="Radius must be positive"):
            create_spiral_spheres(5, -1.0)
    
    def test_spiral_invalid_height(self):
        """Test spiral with invalid height."""
        with pytest.raises(ValueError, match="Height must be positive"):
            create_spiral_spheres(5, 2.0, -10.0)


class TestDoubleHelix:
    """Tests for create_double_helix function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_helix_basic(self):
        """Test basic double helix creation."""
        create_double_helix(5, 2.0, 3.0, 50.0, 20.0)
        assert get_geometry_count() == 10  # 5 per helix = 10 total
    
    def test_helix_defaults(self):
        """Test helix with default parameters."""
        create_double_helix()
        assert get_geometry_count() == 40  # 20 per helix = 40 total
    
    def test_helix_invalid_count(self):
        """Test helix with invalid count."""
        with pytest.raises(ValueError, match="Count must be positive"):
            create_double_helix(0)


class TestFibonacciSpheres:
    """Tests for create_fibonacci_spheres function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_fibonacci_basic(self):
        """Test basic Fibonacci spiral creation."""
        create_fibonacci_spheres(8, 5.0, 2.0)
        assert get_geometry_count() == 8
    
    def test_fibonacci_defaults(self):
        """Test Fibonacci with default parameters."""
        create_fibonacci_spheres()
        assert get_geometry_count() == 15  # default count
    
    def test_fibonacci_invalid_count(self):
        """Test Fibonacci with invalid count."""
        with pytest.raises(ValueError, match="Count must be positive"):
            create_fibonacci_spheres(-1)


class TestTower:
    """Tests for create_tower function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_tower_basic(self):
        """Test basic tower creation."""
        create_tower(0, 0, 100, 5)
        assert get_geometry_count() == 5
    
    def test_tower_defaults(self):
        """Test tower with default parameters."""
        create_tower()
        assert get_geometry_count() == 10  # default levels
    
    def test_tower_invalid_levels(self):
        """Test tower with invalid levels."""
        with pytest.raises(ValueError, match="Levels must be positive"):
            create_tower(levels=0)


class TestGridSpheres:
    """Tests for create_grid_spheres function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_grid_basic(self):
        """Test basic grid creation."""
        create_grid_spheres(3, 4, 5.0, 1.0)
        assert get_geometry_count() == 12  # 3 * 4 = 12
    
    def test_grid_defaults(self):
        """Test grid with default parameters."""
        create_grid_spheres()
        assert get_geometry_count() == 25  # 5 * 5 = 25
    
    def test_grid_invalid_rows(self):
        """Test grid with invalid rows."""
        with pytest.raises(ValueError, match="Rows and columns must be positive"):
            create_grid_spheres(0, 5)
    
    def test_grid_invalid_cols(self):
        """Test grid with invalid columns."""
        with pytest.raises(ValueError, match="Rows and columns must be positive"):
            create_grid_spheres(5, 0)


class TestRandomSpheres:
    """Tests for create_random_spheres function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_random_basic(self):
        """Test basic random sphere creation."""
        create_random_spheres(10, (50, 50, 50), 2.0, 5.0, 42)
        assert get_geometry_count() == 10
    
    def test_random_defaults(self):
        """Test random spheres with default parameters."""
        create_random_spheres(seed=42)  # Use seed for reproducibility
        assert get_geometry_count() == 20  # default count
    
    def test_random_invalid_count(self):
        """Test random spheres with invalid count."""
        with pytest.raises(ValueError, match="Count must be positive"):
            create_random_spheres(0)
    
    def test_random_invalid_bounds(self):
        """Test random spheres with invalid bounds."""
        with pytest.raises(ValueError, match="All bounds must be positive"):
            create_random_spheres(5, (-10, 20, 30))
    
    def test_random_invalid_radius_range(self):
        """Test random spheres with invalid radius range."""
        with pytest.raises(ValueError, match="Invalid radius range"):
            create_random_spheres(5, (50, 50, 50), 10.0, 5.0)  # max < min


class TestSineWaveSpheres:
    """Tests for create_sine_wave_spheres function."""
    
    def setup_method(self):
        """Clear geometry before each test."""
        clear_all()
    
    def test_sine_wave_basic(self):
        """Test basic sine wave creation."""
        create_sine_wave_spheres(10, 15.0, 0.2, 1.0)
        assert get_geometry_count() == 10
    
    def test_sine_wave_defaults(self):
        """Test sine wave with default parameters."""
        create_sine_wave_spheres()
        assert get_geometry_count() == 50  # default count
    
    def test_sine_wave_invalid_count(self):
        """Test sine wave with invalid count."""
        with pytest.raises(ValueError, match="Count must be positive"):
            create_sine_wave_spheres(0)
