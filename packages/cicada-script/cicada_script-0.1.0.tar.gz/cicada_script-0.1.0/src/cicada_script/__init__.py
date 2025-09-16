"""
Cicada-Script: Python API for parametric CAD design and geometry automation.

This package provides a clean Python interface for creating 3D geometry that can be
used with Cicada CAD application or as a standalone geometry creation library.
"""

__version__ = "0.1.0"
__author__ = "Cicada CAD Project"
__email__ = "contact@cicada-cad.org"
__description__ = "Python API for parametric CAD design and geometry automation"

# Import main functions to package level for easy access
from .geometry import (
    sphere, 
    create_spiral_spheres, 
    create_double_helix, 
    create_fibonacci_spheres,
    create_tower,
    create_sine_wave_spheres,
    create_grid_spheres,
    create_random_spheres
)
from .core import (
    set_output_mode, 
    get_output_mode, 
    clear_all, 
    fit_view, 
    get_geometry_count,
    get_all_geometry
)

# Make key functions available at package level
__all__ = [
    'sphere',
    'create_spiral_spheres', 
    'create_double_helix',
    'create_fibonacci_spheres',
    'create_tower',
    'create_sine_wave_spheres',
    'create_grid_spheres',
    'create_random_spheres',
    'set_output_mode',
    'get_output_mode',
    'clear_all',
    'fit_view',
    'get_geometry_count',
    'get_all_geometry',
]

# Package metadata
__package_info__ = {
    'name': 'cicada-script',
    'version': __version__,
    'description': __description__,
    'author': __author__,
    'author_email': __email__,
    'url': 'https://github.com/cicada-cad/cicada-script',
    'license': 'Business Source License 1.1',
    'python_requires': '>=3.8',
}
