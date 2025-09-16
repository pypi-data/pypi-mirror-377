"""
Command line interface for cicada_script package.

This module provides a CLI interface for the cicada_script package.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .core import set_output_mode, clear_all, fit_view, get_geometry_count
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


def main(argv: Optional[list] = None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='cicada-script',
        description='Python API for parametric CAD design and geometry automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --version
  %(prog)s --output json spiral --count 20 --radius 8 --height 100
  %(prog)s --output file --file output.json fibonacci --count 15
  %(prog)s execute script.py
        """
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--output', 
        choices=['print', 'json', 'file', 'cicada'], 
        default='print',
        help='Output mode (default: print)'
    )
    
    parser.add_argument(
        '--file', 
        type=str, 
        help='Output file (required when --output=file)'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sphere command
    sphere_parser = subparsers.add_parser('sphere', help='Create a single sphere')
    sphere_parser.add_argument('origin', nargs=3, type=float, help='Origin coordinates [x y z]')
    sphere_parser.add_argument('radius', type=float, help='Sphere radius')
    
    # Spiral command  
    spiral_parser = subparsers.add_parser('spiral', help='Create spiral spheres')
    spiral_parser.add_argument('--count', type=int, default=10, help='Number of spheres')
    spiral_parser.add_argument('--radius', type=float, default=5.0, help='Sphere radius')
    spiral_parser.add_argument('--height', type=float, default=50.0, help='Spiral height')
    spiral_parser.add_argument('--spiral-radius', type=float, default=30.0, help='Spiral radius')
    
    # Double helix command
    helix_parser = subparsers.add_parser('helix', help='Create double helix')
    helix_parser.add_argument('--count', type=int, default=20, help='Spheres per helix')
    helix_parser.add_argument('--radius1', type=float, default=4.0, help='First helix radius')
    helix_parser.add_argument('--radius2', type=float, default=6.0, help='Second helix radius')
    helix_parser.add_argument('--height', type=float, default=100.0, help='Helix height')
    
    # Fibonacci command
    fib_parser = subparsers.add_parser('fibonacci', help='Create Fibonacci spiral')
    fib_parser.add_argument('--count', type=int, default=15, help='Number of spheres')
    fib_parser.add_argument('--scale', type=float, default=8.0, help='Spiral scale')
    
    # Tower command
    tower_parser = subparsers.add_parser('tower', help='Create sphere tower')
    tower_parser.add_argument('--x', type=float, default=0.0, help='Base X coordinate')
    tower_parser.add_argument('--y', type=float, default=0.0, help='Base Y coordinate')
    tower_parser.add_argument('--height', type=float, default=100.0, help='Tower height')
    tower_parser.add_argument('--levels', type=int, default=10, help='Number of levels')
    
    # Grid command
    grid_parser = subparsers.add_parser('grid', help='Create grid of spheres')
    grid_parser.add_argument('--rows', type=int, default=5, help='Number of rows')
    grid_parser.add_argument('--cols', type=int, default=5, help='Number of columns')
    grid_parser.add_argument('--spacing', type=float, default=10.0, help='Spacing between spheres')
    grid_parser.add_argument('--radius', type=float, default=2.0, help='Sphere radius')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute Python script')
    execute_parser.add_argument('script', type=str, help='Path to Python script')
    
    # Parse arguments
    if argv is None:
        argv = sys.argv[1:]
    args = parser.parse_args(argv)
    
    # Set output mode
    if args.output == 'file' and not args.file:
        parser.error('--file is required when --output=file')
    
    set_output_mode(args.output, args.file)
    
    # Execute command
    try:
        if args.command == 'sphere':
            sphere(args.origin, args.radius)
            
        elif args.command == 'spiral':
            create_spiral_spheres(args.count, args.radius, args.height, args.spiral_radius)
            
        elif args.command == 'helix':
            create_double_helix(args.count, args.radius1, args.radius2, args.height)
            
        elif args.command == 'fibonacci':
            create_fibonacci_spheres(args.count, args.scale)
            
        elif args.command == 'tower':
            create_tower(args.x, args.y, args.height, args.levels)
            
        elif args.command == 'grid':
            create_grid_spheres(args.rows, args.cols, args.spacing, args.radius)
            
        elif args.command == 'execute':
            script_path = Path(args.script)
            if not script_path.exists():
                print(f"Error: Script file '{args.script}' not found", file=sys.stderr)
                return 1
            
            # Execute the Python script
            with open(script_path, 'r') as f:
                script_content = f.read()
            
            # Create a namespace with cicada_script available
            namespace = {
                'cicada': sys.modules[__name__.split('.')[0]],
                'cicada_script': sys.modules[__name__.split('.')[0]]
            }
            
            try:
                exec(script_content, namespace)
            except Exception as e:
                print(f"Error executing script: {e}", file=sys.stderr)
                return 1
                
        else:
            # No command specified, show help
            parser.print_help()
            return 0
            
        # Show summary
        count = get_geometry_count()
        if count > 0:
            print(f"\n✅ Created {count} geometry objects using cicada-script v{__version__}")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
