"""
Elevation data fetcher using Open-Elevation API
"""

import requests
import numpy as np
from typing import Tuple, List
import config


class ElevationFetcher:
    """Fetches elevation data from Open-Elevation API"""

    def __init__(self, api_url: str = None):
        self.api_url = api_url or config.OPEN_ELEVATION_API

    def fetch_elevation_grid(
        self,
        center_lat: float,
        center_lng: float,
        area_km: float = config.DEFAULT_AREA_KM,
        resolution: int = config.DEFAULT_GRID_RESOLUTION
    ) -> Tuple[np.ndarray, dict]:
        """
        Fetch a grid of elevation data around a center point

        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            area_km: Area size in kilometers (square)
            resolution: Grid resolution (points per side)

        Returns:
            Tuple of (elevation_grid, metadata)
            - elevation_grid: 2D numpy array of elevations in meters
            - metadata: dict with bounds, resolution, etc.
        """
        # Calculate lat/lng bounds
        # Approximate: 1 degree latitude ≈ 111 km
        # 1 degree longitude varies by latitude
        lat_km_per_degree = 111.0
        lng_km_per_degree = 111.0 * np.cos(np.radians(center_lat))

        lat_range = area_km / lat_km_per_degree
        lng_range = area_km / lng_km_per_degree

        min_lat = center_lat - lat_range / 2
        max_lat = center_lat + lat_range / 2
        min_lng = center_lng - lng_range / 2
        max_lng = center_lng + lng_range / 2

        # Generate grid of lat/lng points
        lats = np.linspace(min_lat, max_lat, resolution)
        lngs = np.linspace(min_lng, max_lng, resolution)

        # Create coordinate pairs
        locations = []
        for lat in lats:
            for lng in lngs:
                locations.append({"latitude": lat, "longitude": lng})

        print(f"Fetching elevation data for {len(locations)} points...")
        print(f"Area: {area_km}km x {area_km}km around ({center_lat}, {center_lng})")

        # Fetch elevation data (API accepts max ~1000 points per request)
        # Split into batches if needed
        batch_size = 1000
        all_elevations = []

        for i in range(0, len(locations), batch_size):
            batch = locations[i:i + batch_size]
            print(f"Fetching batch {i//batch_size + 1}/{(len(locations)-1)//batch_size + 1}...")

            try:
                response = requests.post(
                    self.api_url,
                    json={"locations": batch},
                    timeout=30
                )
                response.raise_for_status()

                results = response.json()["results"]
                elevations = [r["elevation"] for r in results]
                all_elevations.extend(elevations)

            except Exception as e:
                print(f"Error fetching elevation data: {e}")
                # Fill with zeros if request fails
                all_elevations.extend([0.0] * len(batch))

        # Reshape into 2D grid
        elevation_grid = np.array(all_elevations).reshape((resolution, resolution))

        # Create metadata
        metadata = {
            "center_lat": center_lat,
            "center_lng": center_lng,
            "area_km": area_km,
            "resolution": resolution,
            "bounds": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lng": min_lng,
                "max_lng": max_lng
            },
            "elevation_range": {
                "min": float(np.min(elevation_grid)),
                "max": float(np.max(elevation_grid)),
                "mean": float(np.mean(elevation_grid))
            }
        }

        print(f"Elevation data fetched successfully")
        print(f"  Min elevation: {metadata['elevation_range']['min']:.1f}m")
        print(f"  Max elevation: {metadata['elevation_range']['max']:.1f}m")
        print(f"  Elevation range: {metadata['elevation_range']['max'] - metadata['elevation_range']['min']:.1f}m")

        return elevation_grid, metadata

    def lat_lng_to_grid_coords(
        self,
        lat: float,
        lng: float,
        metadata: dict,
        resolution: int
    ) -> Tuple[int, int]:
        """
        Convert lat/lng coordinates to grid indices

        Args:
            lat: Latitude
            lng: Longitude
            metadata: Metadata from fetch_elevation_grid
            resolution: Grid resolution

        Returns:
            Tuple of (x_index, y_index) in grid coordinates
        """
        bounds = metadata["bounds"]

        # Normalize to 0-1 range
        lat_norm = (lat - bounds["min_lat"]) / (bounds["max_lat"] - bounds["min_lat"])
        lng_norm = (lng - bounds["min_lng"]) / (bounds["max_lng"] - bounds["min_lng"])

        # Convert to grid indices
        y_index = int(lat_norm * (resolution - 1))
        x_index = int(lng_norm * (resolution - 1))

        # Clamp to valid range
        x_index = max(0, min(resolution - 1, x_index))
        y_index = max(0, min(resolution - 1, y_index))

        return x_index, y_index


# Example usage
if __name__ == "__main__":
    fetcher = ElevationFetcher()

    # Example: Central Park, NYC
    center_lat = 40.7829
    center_lng = -73.9654

    grid, metadata = fetcher.fetch_elevation_grid(
        center_lat, center_lng,
        area_km=3.0,
        resolution=50
    )

    print("\nGrid shape:", grid.shape)
    print("Metadata:", metadata)
