#!/usr/bin/env python3
"""
Command-line interface for terrain map generator
"""

import argparse
import sys
from terrain_generator import TerrainGenerator
import config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate 3D printable terrain maps from coordinates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a terrain map of Central Park, NYC
  python cli.py --lat 40.7829 --lng -73.9654 --area 3 --output central_park.stl

  # Generate with custom marker location
  python cli.py --lat 40.7829 --lng -73.9654 --marker-lat 40.7800 --marker-lng -73.9700

  # Generate with high resolution and larger print size
  python cli.py --lat 46.8523 --lng -121.7603 --area 10 --resolution high --size 200

  # Generate with low vertical exaggeration (for flat areas)
  python cli.py --lat 37.7749 --lng -122.4194 --area 5 --exaggeration 1.5

Preset Examples:
  # Coaster size (100mm)
  python cli.py --lat 40.7829 --lng -73.9654 --preset coaster

  # Desk display (150mm)
  python cli.py --lat 40.7829 --lng -73.9654 --preset desk
        """
    )

    # Required arguments
    parser.add_argument(
        '--lat',
        type=float,
        required=True,
        help='Center latitude (e.g., 40.7829)'
    )
    parser.add_argument(
        '--lng',
        type=float,
        required=True,
        help='Center longitude (e.g., -73.9654)'
    )

    # Marker location (optional)
    parser.add_argument(
        '--marker-lat',
        type=float,
        help='Marker latitude (defaults to center lat)'
    )
    parser.add_argument(
        '--marker-lng',
        type=float,
        help='Marker longitude (defaults to center lng)'
    )

    # Generation options
    parser.add_argument(
        '--area',
        type=float,
        default=config.DEFAULT_AREA_KM,
        help=f'Area size in kilometers (default: {config.DEFAULT_AREA_KM})'
    )
    parser.add_argument(
        '--resolution',
        choices=['low', 'medium', 'high', 'ultra'],
        default='medium',
        help='Grid resolution (default: medium)'
    )
    parser.add_argument(
        '--exaggeration',
        type=float,
        default=config.DEFAULT_VERTICAL_EXAGGERATION,
        help=f'Vertical exaggeration factor (default: {config.DEFAULT_VERTICAL_EXAGGERATION})'
    )
    parser.add_argument(
        '--size',
        type=float,
        default=config.PRINT_SIZE_PRESETS['coaster'],
        help=f'Print size in mm (default: {config.PRINT_SIZE_PRESETS["coaster"]})'
    )

    # Preset options
    parser.add_argument(
        '--preset',
        choices=['coaster', 'desk', 'display', 'wall'],
        help='Use a size preset (overrides --size)'
    )

    # Marker customization
    parser.add_argument(
        '--marker-height',
        type=float,
        default=config.DEFAULT_MARKER_HEIGHT_MM,
        help=f'Marker height in mm (default: {config.DEFAULT_MARKER_HEIGHT_MM})'
    )
    parser.add_argument(
        '--marker-radius',
        type=float,
        default=config.DEFAULT_MARKER_RADIUS_MM,
        help=f'Marker radius in mm (default: {config.DEFAULT_MARKER_RADIUS_MM})'
    )

    # Output options
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output filename (default: auto-generated)'
    )
    parser.add_argument(
        '--split-export',
        action='store_true',
        help='Export terrain, base, and marker as separate STL files in a zip archive'
    )
    parser.add_argument(
        '--no-optimize',
        action='store_true',
        help='Skip mesh optimization'
    )

    args = parser.parse_args()

    # Apply preset if specified
    print_size_mm = args.size
    if args.preset:
        print_size_mm = config.PRINT_SIZE_PRESETS[args.preset]
        print(f"Using {args.preset} preset: {print_size_mm}mm")

    # Create generator
    generator = TerrainGenerator()

    # Build options
    options = {
        'area_km': args.area,
        'resolution': args.resolution,
        'vertical_exaggeration': args.exaggeration,
        'print_size_mm': print_size_mm,
        'marker_height_mm': args.marker_height,
        'marker_radius_mm': args.marker_radius,
        'filename': args.output,
        'split_export': args.split_export,
        'optimize': not args.no_optimize
    }

    # Generate
    result = generator.generate(
        center_lat=args.lat,
        center_lng=args.lng,
        marker_lat=args.marker_lat,
        marker_lng=args.marker_lng,
        options=options
    )

    # Handle result
    if result['success']:
        print("\n✅ SUCCESS!")
        print(f"\nSTL file ready: {result['stl_path']}")
        print("\nReady to slice and print!")
        return 0
    else:
        print(f"\n❌ FAILED: {result['error']}")
        return 1


def interactive_mode():
    """Interactive CLI mode for easier use"""
    print("=" * 60)
    print("3D TERRAIN MAP GENERATOR - Interactive Mode")
    print("=" * 60)

    # Get coordinates
    print("\nEnter location coordinates:")
    try:
        center_lat = float(input("  Center latitude: "))
        center_lng = float(input("  Center longitude: "))
    except ValueError:
        print("Invalid coordinates!")
        return 1

    # Ask about marker
    use_custom_marker = input("\nUse custom marker location? (y/n): ").lower() == 'y'
    marker_lat = None
    marker_lng = None
    if use_custom_marker:
        try:
            marker_lat = float(input("  Marker latitude: "))
            marker_lng = float(input("  Marker longitude: "))
        except ValueError:
            print("Invalid marker coordinates, using center")

    # Get options
    print("\nGeneration options:")
    area_km = input(f"  Area size in km (default: {config.DEFAULT_AREA_KM}): ")
    area_km = float(area_km) if area_km else config.DEFAULT_AREA_KM

    print("  Resolution: low / medium / high / ultra")
    resolution = input(f"  (default: medium): ") or 'medium'

    print("  Size preset: coaster / desk / display / wall")
    preset = input(f"  (default: coaster): ") or 'coaster'
    print_size_mm = config.PRINT_SIZE_PRESETS.get(preset, config.PRINT_SIZE_PRESETS['coaster'])

    exaggeration = input(f"  Vertical exaggeration (default: {config.DEFAULT_VERTICAL_EXAGGERATION}): ")
    exaggeration = float(exaggeration) if exaggeration else config.DEFAULT_VERTICAL_EXAGGERATION

    # Generate
    generator = TerrainGenerator()
    options = {
        'area_km': area_km,
        'resolution': resolution,
        'vertical_exaggeration': exaggeration,
        'print_size_mm': print_size_mm,
        'optimize': True
    }

    result = generator.generate(
        center_lat=center_lat,
        center_lng=center_lng,
        marker_lat=marker_lat,
        marker_lng=marker_lng,
        options=options
    )

    if result['success']:
        print("\n✅ SUCCESS!")
        print(f"\nSTL file ready: {result['stl_path']}")
        return 0
    else:
        print(f"\n❌ FAILED: {result['error']}")
        return 1


if __name__ == "__main__":
    # If no arguments, run interactive mode
    if len(sys.argv) == 1:
        sys.exit(interactive_mode())
    else:
        sys.exit(main())
