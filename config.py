"""
Configuration settings for terrain map generator
"""

# Elevation API settings
OPEN_ELEVATION_API = "https://api.open-elevation.com/api/v1/lookup"

# Default generation settings
DEFAULT_AREA_KM = 5.0  # Area size in kilometers (square)
DEFAULT_GRID_RESOLUTION = 100  # Number of points per side (100x100 = 10,000 points)
DEFAULT_VERTICAL_EXAGGERATION = 3.0  # Multiply Z-axis by this factor
DEFAULT_BASE_HEIGHT_MM = 5.0  # Base thickness in mm for 3D printing

# Marker settings
DEFAULT_MARKER_HEIGHT_MM = 3.0  # Height of marker above terrain
DEFAULT_MARKER_RADIUS_MM = 2.0  # Radius of marker cylinder

# 3D printing optimizations
MIN_WALL_THICKNESS_MM = 1.0  # Minimum printable wall thickness
MESH_SIMPLIFICATION = True  # Reduce polygon count for faster slicing
ENSURE_MANIFOLD = True  # Ensure watertight mesh for printing

# Output settings
OUTPUT_DIR = "/root/moneo/data/terrain-maps"
STL_UNITS = "mm"  # millimeters

# Resolution presets
RESOLUTION_PRESETS = {
    "low": 50,      # 50x50 grid - fast, draft quality
    "medium": 100,  # 100x100 grid - balanced
    "high": 200,    # 200x200 grid - detailed, slower
    "ultra": 300    # 300x300 grid - maximum detail
}

# Area size presets (in kilometers)
AREA_PRESETS = {
    "intimate": 1.0,    # Single block/small park
    "local": 3.0,       # Neighborhood
    "standard": 5.0,    # Few neighborhoods
    "wide": 10.0,       # City district
    "panoramic": 20.0   # Full city view
}

# Target print sizes (in mm)
PRINT_SIZE_PRESETS = {
    "coaster": 100,     # 100mm x 100mm
    "desk": 150,        # 150mm x 150mm
    "display": 200,     # 200mm x 200mm
    "wall": 300         # 300mm x 300mm
}
