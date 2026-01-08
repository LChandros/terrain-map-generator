"""
STL file exporter for terrain meshes
"""

import os
import trimesh
from typing import Optional
import config


class STLExporter:
    """Export trimesh objects to STL files optimized for 3D printing"""

    def __init__(self, output_dir: str = None):
        """
        Initialize STL exporter

        Args:
            output_dir: Output directory for STL files
        """
        self.output_dir = output_dir or config.OUTPUT_DIR

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

    def export(
        self,
        mesh: trimesh.Trimesh,
        filename: str,
        optimize: bool = True
    ) -> str:
        """
        Export mesh to STL file

        Args:
            mesh: Trimesh object to export
            filename: Output filename (without path)
            optimize: Whether to optimize mesh for 3D printing

        Returns:
            Full path to exported STL file
        """
        # Ensure filename ends with .stl
        if not filename.endswith('.stl'):
            filename += '.stl'

        output_path = os.path.join(self.output_dir, filename)

        print(f"Exporting STL to: {output_path}")

        # Optimize mesh if requested
        if optimize:
            mesh = self._optimize_for_printing(mesh)

        # Validate mesh
        if not self._validate_mesh(mesh):
            print("Warning: Mesh may have issues for 3D printing")

        # Export to STL (binary format for smaller files)
        mesh.export(output_path, file_type='stl')

        # Get file size
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  File size: {file_size_mb:.2f} MB")
        print(f"  Vertices: {len(mesh.vertices)}")
        print(f"  Faces: {len(mesh.faces)}")

        return output_path

    def _optimize_for_printing(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """
        Optimize mesh for 3D printing

        Args:
            mesh: Input mesh

        Returns:
            Optimized mesh
        """
        print("Optimizing mesh for 3D printing...")

        # Fix normals (ensure they point outward)
        mesh.fix_normals()

        # Remove duplicate vertices
        mesh.merge_vertices()

        # Remove degenerate faces (keep only non-degenerate)
        if hasattr(mesh, 'nondegenerate_faces'):
            valid_faces = mesh.nondegenerate_faces()
            if len(valid_faces) < len(mesh.faces):
                print(f"  Removing {len(mesh.faces) - len(valid_faces)} degenerate faces...")
                mesh.update_faces(valid_faces)

        # Fill holes if not watertight
        if not mesh.is_watertight:
            print("  Filling holes to make watertight...")
            trimesh.repair.fill_holes(mesh)

        # Simplify mesh if too many faces (optional)
        if config.MESH_SIMPLIFICATION and len(mesh.faces) > 100000:
            print(f"  Simplifying mesh (from {len(mesh.faces)} faces)...")
            # Target 50k faces
            target_faces = 50000
            ratio = target_faces / len(mesh.faces)
            mesh = mesh.simplify_quadric_decimation(target_faces)
            print(f"  Simplified to {len(mesh.faces)} faces")

        return mesh

    def _validate_mesh(self, mesh: trimesh.Trimesh) -> bool:
        """
        Validate mesh for 3D printing

        Args:
            mesh: Mesh to validate

        Returns:
            True if valid, False if issues detected
        """
        print("Validating mesh...")

        issues = []

        # Check if watertight
        if not mesh.is_watertight:
            issues.append("Mesh is not watertight (has holes)")

        # Check if manifold
        if not mesh.is_winding_consistent:
            issues.append("Mesh has inconsistent winding")

        # Check for zero-area faces
        face_areas = mesh.area_faces
        if (face_areas < 1e-10).any():
            issues.append("Mesh has zero-area faces")

        # Check volume (should be positive)
        if mesh.volume <= 0:
            issues.append("Mesh has negative or zero volume")

        # Check for self-intersections (expensive, skip for now)
        # if mesh.is_self_intersecting():
        #     issues.append("Mesh has self-intersections")

        if issues:
            print("  Issues detected:")
            for issue in issues:
                print(f"    - {issue}")
            return False
        else:
            print("  ✓ Mesh is valid for 3D printing")
            return True

    def get_print_info(self, mesh: trimesh.Trimesh) -> dict:
        """
        Get print information for a mesh

        Args:
            mesh: Mesh to analyze

        Returns:
            Dictionary with print information
        """
        bounds = mesh.bounds
        size = bounds[1] - bounds[0]

        return {
            "size_mm": {
                "x": float(size[0]),
                "y": float(size[1]),
                "z": float(size[2])
            },
            "volume_mm3": float(mesh.volume),
            "surface_area_mm2": float(mesh.area),
            "vertices": len(mesh.vertices),
            "faces": len(mesh.faces),
            "is_watertight": mesh.is_watertight,
            "is_winding_consistent": mesh.is_winding_consistent,
            "estimated_print_time_hours": self._estimate_print_time(mesh),
            "estimated_material_grams": self._estimate_material(mesh)
        }

    def _estimate_print_time(self, mesh: trimesh.Trimesh) -> float:
        """
        Rough estimate of 3D print time

        Args:
            mesh: Mesh to estimate

        Returns:
            Estimated print time in hours
        """
        # Very rough estimate based on volume and layer height
        # Assume 0.2mm layer height, 50mm/s print speed
        bounds = mesh.bounds
        height_mm = bounds[1][2] - bounds[0][2]
        layers = height_mm / 0.2

        # Rough approximation: 1-2 minutes per layer for this size
        minutes_per_layer = 1.5
        total_minutes = layers * minutes_per_layer

        return total_minutes / 60.0

    def _estimate_material(self, mesh: trimesh.Trimesh) -> float:
        """
        Rough estimate of material needed

        Args:
            mesh: Mesh to estimate

        Returns:
            Estimated material in grams (PLA)
        """
        # PLA density: ~1.24 g/cm³
        volume_cm3 = mesh.volume / 1000.0  # mm³ to cm³
        pla_density = 1.24  # g/cm³

        # Account for infill (assume 20%)
        infill_ratio = 0.20

        # Rough estimate
        material_grams = volume_cm3 * pla_density * infill_ratio

        return material_grams


# Example usage
if __name__ == "__main__":
    from elevation_fetcher import ElevationFetcher
    from mesh_builder import MeshBuilder

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
    mesh_with_marker = builder.add_marker(mesh, center_lat, center_lng)

    # Export
    exporter = STLExporter()
    output_path = exporter.export(mesh_with_marker, "central_park_test.stl")

    # Get print info
    print_info = exporter.get_print_info(mesh_with_marker)
    print("\nPrint Information:")
    print(f"  Size: {print_info['size_mm']['x']:.1f}mm x {print_info['size_mm']['y']:.1f}mm x {print_info['size_mm']['z']:.1f}mm")
    print(f"  Estimated print time: {print_info['estimated_print_time_hours']:.1f} hours")
    print(f"  Estimated material: {print_info['estimated_material_grams']:.1f}g")
    print(f"\nSTL exported successfully to: {output_path}")
