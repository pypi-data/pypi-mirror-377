# Cicada-Script

[![PyPI version](https://badge.fury.io/py/cicada-script.svg)](https://badge.fury.io/py/cicada-script)
[![Python Support](https://img.shields.io/pypi/pyversions/cicada-script.svg)](https://pypi.org/project/cicada-script/)
[![License: BSL-1.1](https://img.shields.io/badge/License-BSL--1.1-blue.svg)](https://mariadb.com/bsl11/)

**Python API for parametric CAD design and geometry automation**

Cicada-Script is a powerful Python library that provides an intuitive API for creating 3D geometry and parametric designs. Originally developed as the scripting interface for the Cicada CAD application, it can be used as a standalone library for geometry generation, prototyping, and automation.

## 🚀 Features

- **Simple API**: Clean, intuitive functions for 3D geometry creation
- **Parametric Design**: Create complex geometric patterns with mathematical functions  
- **Multiple Output Modes**: Print, JSON, file output, or integration with Cicada CAD
- **Rich Pattern Library**: Built-in functions for spirals, helixes, Fibonacci patterns, and more
- **Extensible**: Easy to extend with custom geometric functions
- **Type Hints**: Full type annotation support for better IDE integration
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 📦 Installation

Install Cicada-Script using pip:

```bash
pip install cicada-script
```

Or install the development version from GitHub:

```bash
pip install git+https://github.com/cicada-cad/cicada-script.git
```

> **⚠️ Note**: You may see a harmless warning about `jupyter-cadquery` dependency parsing during installation. This is from a different package and does not affect cicada-script. See [INSTALLATION_FAQ.md](./INSTALLATION_FAQ.md) for details.

## 🎯 Quick Start

### Basic Usage

```python
import cicada_script as cicada

# Create a sphere at origin
cicada.sphere([0, 0, 0], 25.0)

# Create spheres at different positions
cicada.sphere([50, 0, 0], 15.0)
cicada.sphere([0, 50, 0], 20.0)
```

### Parametric Design Example

```python
import math
import cicada_script as cicada

def create_spiral_tower(levels=10, radius=30):
    """Create a spiral tower of spheres"""
    for i in range(levels):
        angle = (i * 2 * math.pi) / levels
        height = i * 10
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        sphere_radius = 8 - (i * 0.5)  # Decreasing size
        cicada.sphere([x, y, height], sphere_radius)

# Create the tower
create_spiral_tower(15, 40)
```

### Built-in Pattern Functions

```python
import cicada_script as cicada

# Spiral arrangement of spheres  
cicada.create_spiral_spheres(count=20, radius=8.0, height=100.0)

# Double helix pattern
cicada.create_double_helix(count=15, radius1=3.0, radius2=4.0, height=80.0)

# Fibonacci spiral
cicada.create_fibonacci_spheres(count=12, scale=6.0)

# Grid of spheres
cicada.create_grid_spheres(rows=5, cols=5, spacing=10.0, radius=2.0)

# Random spheres
cicada.create_random_spheres(count=20, bounds=(100, 100, 100), seed=42)
```

## 🔧 Configuration

### Output Modes

Cicada-Script supports multiple output modes:

```python
import cicada_script as cicada

# Print geometry info to console (default)
cicada.set_output_mode("print")

# Output geometry as JSON
cicada.set_output_mode("json")

# Save geometry to file
cicada.set_output_mode("file", "geometry.json")

# Send to Cicada CAD application (if available)
cicada.set_output_mode("cicada")
```

### Utility Functions

```python
import cicada_script as cicada

# Clear all geometry objects
cicada.clear_all()

# Get current output mode
mode = cicada.get_output_mode()

# Get geometry count
count = cicada.get_geometry_count()

# Fit view (for compatible outputs)
cicada.fit_view()
```

## 📚 API Reference

### Core Functions

#### `sphere(origin, radius)`
Create a sphere with specified origin and radius.

- **origin**: `List[float] | Tuple[float, float, float]` - Center point [x, y, z]
- **radius**: `float` - Sphere radius (must be positive)

### Pattern Functions

#### `create_spiral_spheres(count, radius, height, spiral_radius)`
Create a spiral arrangement of spheres.

#### `create_double_helix(count, radius1, radius2, height, helix_radius)`
Create a double helix pattern with spheres.

#### `create_fibonacci_spheres(count, scale, vertical_spacing)`
Create spheres arranged in a Fibonacci spiral pattern.

#### `create_tower(base_x, base_y, height, levels)`
Create a tower of spheres with decreasing radius.

#### `create_sine_wave_spheres(count, amplitude, frequency, spacing)`
Create spheres following a sine wave pattern.

See the [API documentation](https://cicada-script.readthedocs.io) for complete details.

## 🧪 Examples

### Mathematical Patterns

```python
import math
import cicada_script as cicada

def create_rose_curve(n=5, k=3, scale=20, spheres=100):
    """Create spheres following a rose curve pattern"""
    for i in range(spheres):
        t = (i * 4 * math.pi) / spheres
        r = scale * math.cos(k * t)
        x = r * math.cos(n * t)
        y = r * math.sin(n * t)
        z = i * 0.5  # Slight vertical progression
        cicada.sphere([x, y, z], 2.0)

create_rose_curve()
```

### Architectural Structures

```python
import cicada_script as cicada

def create_dome(radius=50, levels=10):
    """Create a dome structure"""
    for level in range(levels):
        height = radius * math.sin((level * math.pi) / (2 * levels))
        level_radius = radius * math.cos((level * math.pi) / (2 * levels))
        circumference = 2 * math.pi * level_radius
        spheres_in_level = max(8, int(circumference / 10))
        
        for i in range(spheres_in_level):
            angle = (i * 2 * math.pi) / spheres_in_level
            x = level_radius * math.cos(angle)
            y = level_radius * math.sin(angle)
            cicada.sphere([x, y, height], 3.0)

create_dome()
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/cicada-cad/cicada-script.git
cd cicada-script
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## 📄 License

This project is licensed under the **Business Source License 1.1** - see the [LICENSE](LICENSE) file for details.

### What does BSL 1.1 mean?

- **✅ Free for non-production use** - Development, testing, research, and personal projects
- **✅ Limited production use** - You can use it in production as long as you're not offering it as a Database-as-a-Service
- **✅ Becomes open source** - Automatically converts to GPL 2.0+ on January 1, 2029
- **ℹ️ Commercial licenses available** - Contact us for unrestricted commercial use

The Business Source License ensures sustainable development while keeping the software accessible for most use cases. Learn more at [mariadb.com/bsl11/](https://mariadb.com/bsl11/).

## 🔗 Links

- **Homepage**: https://github.com/cicada-cad/cicada-script
- **Documentation**: https://cicada-script.readthedocs.io
- **PyPI**: https://pypi.org/project/cicada-script/
- **Bug Reports**: https://github.com/cicada-cad/cicada-script/issues

## 🙏 Acknowledgments

- Part of the Cicada CAD project ecosystem
- Inspired by parametric design tools and computational geometry libraries
- Built with modern Python packaging best practices
