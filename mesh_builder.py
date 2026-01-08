"""
3D mesh builder for terrain from elevation data
"""

import numpy as np
import trimesh
from typing import Optional, Tuple
import config


class MeshBuilder:
    """Builds 3D meshes from elevation data"""

    def __init__(
        self,
        elevation_grid: np.ndarray,
        metadata: dict,
        vertical_exaggeration: float = config.DEFAULT_VERTICAL_EXAGGERATION,
        print_size_mm: float = 100.0
    ):
        """
        Initialize mesh builder

        Args:
            elevation_grid: 2D array of elevations in meters
            metadata: Metadata from elevation fetcher
            vertical_exaggeration: Z-axis scale factor
            print_size_mm: Target print size in millimeters
        """
        self.elevation_grid = elevation_grid
        self.metadata = metadata
        self.vertical_exaggeration = vertical_exaggeration
        self.print_size_mm = print_size_mm
        self.resolution = elevation_grid.shape[0]

        # Calculate scale factor to achieve target print size
        # Grid is resolution x resolution, scale to print_size_mm
        self.xy_scale = print_size_mm / self.resolution

    def build_terrain_mesh(self, include_base: bool = True) -> trimesh.Trimesh:
        """
        Convert elevation grid to 3D mesh

        Args:
            include_base: Whether to include the base (default True)

        Returns:
            Trimesh object of terrain
        """
        print(f"Building terrain mesh...")
        print(f"  Resolution: {self.resolution}x{self.resolution}")
        print(f"  Target size: {self.print_size_mm}mm x {self.print_size_mm}mm")
        print(f"  Vertical exaggeration: {self.vertical_exaggeration}x")

        # Normalize elevation data
        min_elev = np.min(self.elevation_grid)
        max_elev = np.max(self.elevation_grid)
        elev_range = max_elev - min_elev

        if elev_range == 0:
            print("Warning: Flat terrain detected, adding minimal variation")
            elev_range = 1.0

        # Normalize to 0-1 range
        normalized_grid = (self.elevation_grid - min_elev) / elev_range

        # Apply vertical exaggeration and scale to mm
        # Use a reasonable height (e.g., 20% of print size)
        max_height_mm = self.print_size_mm * 0.2 * self.vertical_exaggeration
        z_grid = normalized_grid * max_height_mm

        # Add base thickness
        z_grid += config.DEFAULT_BASE_HEIGHT_MM

        # Create vertices
        vertices = []
        for i in range(self.resolution):
            for j in range(self.resolution):
                x = j * self.xy_scale
                y = i * self.xy_scale
                z = z_grid[i, j]
                vertices.append([x, y, z])

        vertices = np.array(vertices)

        # Create faces (two triangles per grid cell)
        faces = []
        for i in range(self.resolution - 1):
            for j in range(self.resolution - 1):
                # Current cell corners
                top_left = i * self.resolution + j
                top_right = top_left + 1
                bottom_left = (i + 1) * self.resolution + j
                bottom_right = bottom_left + 1

                # Two triangles per cell
                faces.append([top_left, bottom_left, top_right])
                faces.append([top_right, bottom_left, bottom_right])

        faces = np.array(faces)

        # Create terrain mesh
        terrain_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Add bottom face (for 3D printing) if requested
        if include_base:
            terrain_mesh = self._add_base(terrain_mesh)

        print(f"  Vertices: {len(terrain_mesh.vertices)}")
        print(f"  Faces: {len(terrain_mesh.faces)}")

        # Ensure manifold (watertight) for 3D printing
        if config.ENSURE_MANIFOLD:
            if not terrain_mesh.is_watertight:
                print("  Making mesh watertight...")
                trimesh.repair.fill_holes(terrain_mesh)
                trimesh.repair.fix_normals(terrain_mesh)

        return terrain_mesh

    def _add_base(self, terrain_mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Add solid base to terrain mesh for 3D printing

        Args:
            terrain_mesh: Terrain surface mesh

        Returns:
            Complete mesh with base
        """
        # Get bounds
        bounds = terrain_mesh.bounds
        min_pt = bounds[0]
        max_pt = bounds[1]

        # Create base vertices at z=0
        base_height = 0.0
        base_vertices = []

        # Bottom corners
        base_vertices.append([min_pt[0], min_pt[1], base_height])  # 0
        base_vertices.append([max_pt[0], min_pt[1], base_height])  # 1
        base_vertices.append([max_pt[0], max_pt[1], base_height])  # 2
        base_vertices.append([min_pt[0], max_pt[1], base_height])  # 3

        base_vertices = np.array(base_vertices)

        # Bottom face
        base_faces = [
            [0, 2, 1],
            [0, 3, 2]
        ]

        # Create base mesh
        base_mesh = trimesh.Trimesh(vertices=base_vertices, faces=base_faces)

        # Combine with terrain
        combined = trimesh.util.concatenate([terrain_mesh, base_mesh])

        return combined

    def add_marker(
        self,
        mesh: trimesh.Trimesh,
        marker_lat: float,
        marker_lng: float,
        marker_height_mm: float = config.DEFAULT_MARKER_HEIGHT_MM,
        marker_radius_mm: float = config.DEFAULT_MARKER_RADIUS_MM
    ) -> trimesh.Trimesh:
        """
        Add a marker cylinder at specified location

        Args:
            mesh: Terrain mesh
            marker_lat: Marker latitude
            marker_lng: Marker longitude
            marker_height_mm: Height of marker in mm
            marker_radius_mm: Radius of marker in mm

        Returns:
            Mesh with marker added
        """
        print(f"Adding marker at ({marker_lat}, {marker_lng})")

        # Convert lat/lng to grid coordinates
        from elevation_fetcher import ElevationFetcher
        fetcher = ElevationFetcher()
        grid_x, grid_y = fetcher.lat_lng_to_grid_coords(
            marker_lat, marker_lng, self.metadata, self.resolution
        )

        # Convert grid coords to mesh coordinates
        mesh_x = grid_x * self.xy_scale
        mesh_y = grid_y * self.xy_scale

        # Get elevation at marker position
        terrain_z = self.elevation_grid[grid_y, grid_x]
        min_elev = np.min(self.elevation_grid)
        max_elev = np.max(self.elevation_grid)
        elev_range = max(max_elev - min_elev, 1.0)

        normalized_z = (terrain_z - min_elev) / elev_range
        max_height_mm = self.print_size_mm * 0.2 * self.vertical_exaggeration
        marker_base_z = normalized_z * max_height_mm + config.DEFAULT_BASE_HEIGHT_MM

        # Create marker cylinder
        marker = trimesh.creation.cylinder(
            radius=marker_radius_mm,
            height=marker_height_mm,
            sections=16
        )

        # Position marker
        marker.apply_translation([
            mesh_x,
            mesh_y,
            marker_base_z + marker_height_mm / 2
        ])

        print(f"  Marker position: ({mesh_x:.1f}, {mesh_y:.1f}, {marker_base_z:.1f})mm")

        # Combine with terrain
        combined = trimesh.util.concatenate([mesh, marker])

        return combined

    def build_separate_components(
        self,
        marker_lat: Optional[float] = None,
        marker_lng: Optional[float] = None,
        marker_height_mm: float = config.DEFAULT_MARKER_HEIGHT_MM,
        marker_radius_mm: float = config.DEFAULT_MARKER_RADIUS_MM
    ) -> Tuple[trimesh.Trimesh, trimesh.Trimesh, Optional[trimesh.Trimesh]]:
        """
        Build terrain, base, and marker as separate meshes for multi-part printing

        Args:
            marker_lat: Optional marker latitude
            marker_lng: Optional marker longitude
            marker_height_mm: Height of marker in mm
            marker_radius_mm: Radius of marker in mm

        Returns:
            Tuple of (terrain_only_mesh, base_mesh, marker_mesh)
            marker_mesh is None if no marker coordinates provided
        """
        print("Building separate components for split export...")

        # Build terrain surface only (no base)
        terrain_only = self.build_terrain_mesh(include_base=False)

        # Build separate base
        base_mesh = self._build_separate_base()

        # Build separate marker if coordinates provided
        marker_mesh = None
        if marker_lat is not None and marker_lng is not None:
            marker_mesh = self._build_separate_marker(
                marker_lat, marker_lng,
                marker_height_mm, marker_radius_mm
            )

        return terrain_only, base_mesh, marker_mesh

    def _build_separate_base(self) -> trimesh.Trimesh:
        """
        Build just the base as a separate mesh

        Returns:
            Base mesh as a box
        """
        # Create a solid box for the base
        base_height = config.DEFAULT_BASE_HEIGHT_MM

        # Box dimensions match the terrain
        box_size = [self.print_size_mm, self.print_size_mm, base_height]

        # Create box centered at origin, then shift
        base_mesh = trimesh.creation.box(extents=box_size)

        # Position it correctly (bottom at z=0, top at z=base_height)
        base_mesh.apply_translation([
            self.print_size_mm / 2,
            self.print_size_mm / 2,
            base_height / 2
        ])

        return base_mesh

    def _build_separate_marker(
        self,
        marker_lat: float,
        marker_lng: float,
        marker_height_mm: float,
        marker_radius_mm: float
    ) -> trimesh.Trimesh:
        """
        Build just the marker cylinder as a separate mesh

        Args:
            marker_lat: Marker latitude
            marker_lng: Marker longitude
            marker_height_mm: Height of marker in mm
            marker_radius_mm: Radius of marker in mm

        Returns:
            Marker mesh
        """
        # Convert lat/lng to grid coordinates
        from elevation_fetcher import ElevationFetcher
        fetcher = ElevationFetcher()
        grid_x, grid_y = fetcher.lat_lng_to_grid_coords(
            marker_lat, marker_lng, self.metadata, self.resolution
        )

        # Convert grid coords to mesh coordinates
        mesh_x = grid_x * self.xy_scale
        mesh_y = grid_y * self.xy_scale

        # Get elevation at marker position
        terrain_z = self.elevation_grid[grid_y, grid_x]
        min_elev = np.min(self.elevation_grid)
        max_elev = np.max(self.elevation_grid)
        elev_range = max(max_elev - min_elev, 1.0)

        normalized_z = (terrain_z - min_elev) / elev_range
        max_height_mm = self.print_size_mm * 0.2 * self.vertical_exaggeration
        marker_base_z = normalized_z * max_height_mm + config.DEFAULT_BASE_HEIGHT_MM

        # Create marker cylinder
        marker = trimesh.creation.cylinder(
            radius=marker_radius_mm,
            height=marker_height_mm,
            sections=16
        )

        # Position marker
        marker.apply_translation([
            mesh_x,
            mesh_y,
            marker_base_z + marker_height_mm / 2
        ])

        return marker


# Example usage
if __name__ == "__main__":
    from elevation_fetcher import ElevationFetcher

    # Fetch elevation data
    fetcher = ElevationFetcher()
    center_lat = 40.7829
    center_lng = -73.9654

    grid, metadata = fetcher.fetch_elevation_grid(
        center_lat, center_lng,
        area_km=3.0,
        resolution=50
    )

    # Build mesh
    builder = MeshBuilder(
        elevation_grid=grid,
        metadata=metadata,
        vertical_exaggeration=3.0,
        print_size_mm=100.0
    )

    mesh = builder.build_terrain_mesh()

    # Add marker
    marker_lat = 40.7829
    marker_lng = -73.9654
    mesh_with_marker = builder.add_marker(mesh, marker_lat, marker_lng)

    print(f"\nFinal mesh:")
    print(f"  Vertices: {len(mesh_with_marker.vertices)}")
    print(f"  Faces: {len(mesh_with_marker.faces)}")
    print(f"  Watertight: {mesh_with_marker.is_watertight}")
