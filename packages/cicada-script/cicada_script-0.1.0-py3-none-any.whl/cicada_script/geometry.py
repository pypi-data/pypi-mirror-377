"""
Geometry creation functions for cicada_script package.

This module provides functions for creating 3D geometry objects including spheres,
parametric designs, and complex geometric patterns.
"""

import math
from typing import List, Union, Tuple
from .core import _add_geometry


def sphere(origin: Union[List[float], Tuple[float, float, float]], radius: float):
    """
    Create a sphere with specified origin and radius.
    
    Args:
        origin: Center point of the sphere as [x, y, z] or (x, y, z)
        radius: Radius of the sphere (must be positive)
    
    Returns:
        None
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.sphere([0, 0, 0], 25.0)
        >>> cicada.sphere([10, 20, 30], 15.0)
    """
    # Validate inputs
    if not isinstance(origin, (list, tuple)) or len(origin) != 3:
        raise ValueError("Origin must be a list or tuple of 3 numbers [x, y, z]")
    
    if not isinstance(radius, (int, float)) or radius <= 0:
        raise ValueError("Radius must be a positive number")
    
    # Convert to list for JSON serialization
    origin_list = list(origin)
    
    # Add geometry to core system
    _add_geometry("sphere", {
        "origin": origin_list,
        "radius": float(radius)
    })


def create_spiral_spheres(count: int = 10, radius: float = 5.0, height: float = 50.0, spiral_radius: float = 30.0):
    """
    Create a spiral arrangement of spheres.
    
    Args:
        count: Number of spheres to create
        radius: Radius of each sphere
        height: Total height of the spiral
        spiral_radius: Radius of the spiral path
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_spiral_spheres(20, 8.0, 100.0, 30.0)
    """
    if count <= 0:
        raise ValueError("Count must be positive")
    if radius <= 0:
        raise ValueError("Radius must be positive")
    if height <= 0:
        raise ValueError("Height must be positive")
    if spiral_radius <= 0:
        raise ValueError("Spiral radius must be positive")
    
    print(f"Creating spiral with {count} spheres, radius {radius}, height {height}")
    
    for i in range(count):
        angle = (i * 2 * math.pi) / count
        z = (i * height) / count
        x = spiral_radius * math.cos(angle)
        y = spiral_radius * math.sin(angle)
        
        print(f"Creating sphere {i+1}/{count} at ({x:.2f}, {y:.2f}, {z:.2f})")
        sphere([x, y, z], radius)


def create_double_helix(count: int = 20, radius1: float = 4.0, radius2: float = 6.0, 
                       height: float = 100.0, helix_radius: float = 25.0):
    """
    Create a double helix pattern with spheres.
    
    Args:
        count: Number of spheres per helix
        radius1: Radius of spheres in first helix
        radius2: Radius of spheres in second helix
        height: Total height of the double helix
        helix_radius: Radius of the helix path
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_double_helix(15, 3.0, 4.0, 80.0, 25.0)
    """
    if count <= 0:
        raise ValueError("Count must be positive")
    if any(r <= 0 for r in [radius1, radius2, height, helix_radius]):
        raise ValueError("All radius and height values must be positive")
    
    print(f"Creating double helix with {count} spheres per helix")
    
    for i in range(count):
        angle = (i * 4 * math.pi) / count  # Two full rotations
        z = (i * height) / count
        
        # First helix
        x1 = helix_radius * math.cos(angle)
        y1 = helix_radius * math.sin(angle)
        sphere([x1, y1, z], radius1)
        
        # Second helix (offset by pi)
        x2 = helix_radius * math.cos(angle + math.pi)
        y2 = helix_radius * math.sin(angle + math.pi)
        sphere([x2, y2, z], radius2)


def create_fibonacci_spheres(count: int = 15, scale: float = 8.0, vertical_spacing: float = 3.0):
    """
    Create spheres arranged in a Fibonacci spiral pattern.
    
    Args:
        count: Number of spheres to create
        scale: Scale factor for the spiral
        vertical_spacing: Vertical spacing between spheres
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_fibonacci_spheres(12, 6.0, 3.0)
    """
    if count <= 0:
        raise ValueError("Count must be positive")
    if scale <= 0:
        raise ValueError("Scale must be positive")
    if vertical_spacing <= 0:
        raise ValueError("Vertical spacing must be positive")
    
    print(f"Creating Fibonacci spiral with {count} spheres")
    
    golden_ratio = (1 + math.sqrt(5)) / 2
    
    for i in range(count):
        # Fibonacci spiral coordinates
        theta = 2 * math.pi * i / golden_ratio
        radius_spiral = scale * math.sqrt(i)
        
        x = radius_spiral * math.cos(theta)
        y = radius_spiral * math.sin(theta)
        z = i * vertical_spacing  # Vertical spacing
        
        sphere_radius = 2.0 + i * 0.3  # Growing sphere size
        sphere([x, y, z], sphere_radius)


def create_tower(base_x: float = 0, base_y: float = 0, height: float = 100.0, levels: int = 10):
    """
    Create a tower of spheres with decreasing radius.
    
    Args:
        base_x: X coordinate of tower base
        base_y: Y coordinate of tower base  
        height: Total height of the tower
        levels: Number of levels in the tower
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_tower(0, 0, 100, 8)
    """
    if levels <= 0:
        raise ValueError("Levels must be positive")
    if height <= 0:
        raise ValueError("Height must be positive")
    
    for level in range(levels):
        z = (height * level) / levels
        radius = 10 - (level * 0.8)  # Decreasing radius
        if radius > 1.0:  # Minimum radius
            sphere([base_x, base_y, z], radius)


def create_sine_wave_spheres(count: int = 50, amplitude: float = 20.0, frequency: float = 0.1, spacing: float = 2.0):
    """
    Create spheres following a sine wave pattern.
    
    Args:
        count: Number of spheres to create
        amplitude: Amplitude of the sine wave
        frequency: Frequency of the sine wave  
        spacing: Spacing between spheres along X axis
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_sine_wave_spheres(50, 20.0, 0.1, 2.0)
    """
    if count <= 0:
        raise ValueError("Count must be positive")
    if amplitude <= 0:
        raise ValueError("Amplitude must be positive")
    if spacing <= 0:
        raise ValueError("Spacing must be positive")
    
    for i in range(count):
        x = i * spacing  # Step along X axis
        y = amplitude * math.sin(x * frequency)  # Sine wave in Y
        z = amplitude * 0.5 * math.cos(x * frequency)  # Cosine wave in Z
        sphere([x, y, z], 3.0)


def create_grid_spheres(rows: int = 5, cols: int = 5, spacing: float = 10.0, radius: float = 2.0):
    """
    Create a grid of spheres.
    
    Args:
        rows: Number of rows
        cols: Number of columns
        spacing: Spacing between spheres
        radius: Radius of each sphere
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_grid_spheres(5, 5, 10.0, 2.0)
    """
    if rows <= 0 or cols <= 0:
        raise ValueError("Rows and columns must be positive")
    if spacing <= 0:
        raise ValueError("Spacing must be positive")
    if radius <= 0:
        raise ValueError("Radius must be positive")
    
    for i in range(rows):
        for j in range(cols):
            x = j * spacing
            y = i * spacing
            z = 0
            sphere([x, y, z], radius)


def create_random_spheres(count: int = 20, bounds: Tuple[float, float, float] = (100.0, 100.0, 100.0), 
                         min_radius: float = 2.0, max_radius: float = 8.0, seed: int = None):
    """
    Create randomly placed spheres within specified bounds.
    
    Args:
        count: Number of spheres to create
        bounds: Bounding box dimensions (width, height, depth)
        min_radius: Minimum sphere radius
        max_radius: Maximum sphere radius
        seed: Random seed for reproducible results
    
    Example:
        >>> import cicada_script as cicada
        >>> cicada.create_random_spheres(20, (100, 100, 100), 2.0, 8.0, 42)
    """
    import random
    
    if seed is not None:
        random.seed(seed)
    
    if count <= 0:
        raise ValueError("Count must be positive")
    if any(b <= 0 for b in bounds):
        raise ValueError("All bounds must be positive")
    if min_radius <= 0 or max_radius <= min_radius:
        raise ValueError("Invalid radius range")
    
    for i in range(count):
        x = random.uniform(-bounds[0]/2, bounds[0]/2)
        y = random.uniform(-bounds[1]/2, bounds[1]/2)
        z = random.uniform(0, bounds[2])
        radius = random.uniform(min_radius, max_radius)
        sphere([x, y, z], radius)
