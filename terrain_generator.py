"""
Main terrain map generator - orchestrates the entire process
"""

from typing import Optional, Dict, Any
from elevation_fetcher import ElevationFetcher
from mesh_builder import MeshBuilder
from stl_exporter import STLExporter
import config


class TerrainGenerator:
    """Main class for generating 3D terrain maps"""

    def __init__(
        self,
        output_dir: str = None,
        api_url: str = None
    ):
        """
        Initialize terrain generator

        Args:
            output_dir: Output directory for STL files
            api_url: Elevation API URL (defaults to Open-Elevation)
        """
        self.elevation_fetcher = ElevationFetcher(api_url)
        self.stl_exporter = STLExporter(output_dir)

    def generate(
        self,
        center_lat: float,
        center_lng: float,
        marker_lat: Optional[float] = None,
        marker_lng: Optional[float] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a 3D terrain map

        Args:
            center_lat: Center point latitude
            center_lng: Center point longitude
            marker_lat: Marker latitude (defaults to center)
            marker_lng: Marker longitude (defaults to center)
            options: Generation options dict with keys:
                - area_km: Area size in kilometers (default: 5.0)
                - resolution: Grid resolution or preset name (default: "medium")
                - vertical_exaggeration: Z-axis scale factor (default: 3.0)
                - print_size_mm: Target print size in mm (default: 100)
                - marker_height_mm: Marker height (default: 3.0)
                - marker_radius_mm: Marker radius (default: 2.0)
                - filename: Output filename (default: auto-generated)
                - optimize: Optimize mesh for printing (default: True)

        Returns:
            Dictionary with generation results:
                - success: bool
                - stl_path: Path to generated STL file
                - print_info: Print information dict
                - metadata: Elevation metadata
                - error: Error message (if failed)
        """
        # Default marker to center if not specified
        if marker_lat is None:
            marker_lat = center_lat
        if marker_lng is None:
            marker_lng = center_lng

        # Parse options
        options = options or {}
        area_km = options.get('area_km', config.DEFAULT_AREA_KM)
        resolution = options.get('resolution', 'medium')
        vertical_exaggeration = options.get('vertical_exaggeration', config.DEFAULT_VERTICAL_EXAGGERATION)
        print_size_mm = options.get('print_size_mm', config.PRINT_SIZE_PRESETS['coaster'])
        marker_height_mm = options.get('marker_height_mm', config.DEFAULT_MARKER_HEIGHT_MM)
        marker_radius_mm = options.get('marker_radius_mm', config.DEFAULT_MARKER_RADIUS_MM)
        filename = options.get('filename', None)
        optimize = options.get('optimize', True)

        # Convert resolution preset to number
        if isinstance(resolution, str):
            resolution = config.RESOLUTION_PRESETS.get(resolution, config.DEFAULT_GRID_RESOLUTION)

        print("=" * 60)
        print("3D TERRAIN MAP GENERATOR")
        print("=" * 60)
        print(f"Center: ({center_lat}, {center_lng})")
        print(f"Marker: ({marker_lat}, {marker_lng})")
        print(f"Area: {area_km}km x {area_km}km")
        print(f"Resolution: {resolution}x{resolution} points")
        print(f"Print size: {print_size_mm}mm")
        print(f"Vertical exaggeration: {vertical_exaggeration}x")
        print("=" * 60)

        try:
            # Step 1: Fetch elevation data
            print("\n[1/3] Fetching elevation data...")
            elevation_grid, metadata = self.elevation_fetcher.fetch_elevation_grid(
                center_lat=center_lat,
                center_lng=center_lng,
                area_km=area_km,
                resolution=resolution
            )

            # Step 2: Build 3D mesh
            print("\n[2/3] Building 3D mesh...")
            mesh_builder = MeshBuilder(
                elevation_grid=elevation_grid,
                metadata=metadata,
                vertical_exaggeration=vertical_exaggeration,
                print_size_mm=print_size_mm
            )

            terrain_mesh = mesh_builder.build_terrain_mesh()

            # Add marker
            print("\nAdding marker...")
            final_mesh = mesh_builder.add_marker(
                terrain_mesh,
                marker_lat=marker_lat,
                marker_lng=marker_lng,
                marker_height_mm=marker_height_mm,
                marker_radius_mm=marker_radius_mm
            )

            # Step 3: Export to STL
            print("\n[3/3] Exporting to STL...")

            # Generate filename if not provided
            if not filename:
                filename = f"terrain_{center_lat:.4f}_{center_lng:.4f}.stl"

            stl_path = self.stl_exporter.export(
                final_mesh,
                filename=filename,
                optimize=optimize
            )

            # Get print information
            print_info = self.stl_exporter.get_print_info(final_mesh)

            print("\n" + "=" * 60)
            print("GENERATION COMPLETE!")
            print("=" * 60)
            print(f"STL File: {stl_path}")
            print(f"Size: {print_info['size_mm']['x']:.1f} x {print_info['size_mm']['y']:.1f} x {print_info['size_mm']['z']:.1f} mm")
            print(f"Estimated print time: {print_info['estimated_print_time_hours']:.1f} hours")
            print(f"Estimated material: {print_info['estimated_material_grams']:.1f}g PLA")
            print("=" * 60)

            return {
                'success': True,
                'stl_path': stl_path,
                'print_info': print_info,
                'metadata': metadata,
                'options': {
                    'area_km': area_km,
                    'resolution': resolution,
                    'vertical_exaggeration': vertical_exaggeration,
                    'print_size_mm': print_size_mm
                }
            }

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': str(e)
            }


# Example usage and test
if __name__ == "__main__":
    generator = TerrainGenerator()

    # Test locations
    test_locations = [
        {
            "name": "Central Park, NYC",
            "lat": 40.7829,
            "lng": -73.9654,
            "area_km": 3.0,
            "resolution": "medium"
        },
        {
            "name": "Mount Rainier, WA",
            "lat": 46.8523,
            "lng": -121.7603,
            "area_km": 10.0,
            "resolution": "medium"
        },
        {
            "name": "Grand Canyon, AZ",
            "lat": 36.0544,
            "lng": -112.1401,
            "area_km": 15.0,
            "resolution": "medium"
        }
    ]

    # Generate for one location
    location = test_locations[0]
    print(f"\nGenerating: {location['name']}")

    result = generator.generate(
        center_lat=location['lat'],
        center_lng=location['lng'],
        options={
            'area_km': location['area_km'],
            'resolution': location['resolution'],
            'print_size_mm': 100,
            'vertical_exaggeration': 3.0,
            'filename': f"{location['name'].replace(' ', '_').replace(',', '')}.stl"
        }
    )

    if result['success']:
        print(f"\n✅ Success! STL saved to: {result['stl_path']}")
    else:
        print(f"\n❌ Failed: {result['error']}")
