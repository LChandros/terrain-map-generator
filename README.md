# 3D Terrain Map Generator

Generate 3D printable topographical maps from any location on Earth! Perfect for marking first date spots, proposal locations, or any memorable place.

## Features

- ✅ **Any Location** - Works anywhere in the world using Open-Elevation API
- ✅ **Custom Markers** - Mark specific spots on the map (e.g., "we first met here")
- ✅ **Split Export** - Export terrain, base, and marker as separate files for multi-color printing
- ✅ **Customizable** - Control area size, resolution, vertical exaggeration, print size
- ✅ **3D Printable** - Exports optimized STL files ready for slicing
- ✅ **Multiple Interfaces** - CLI, Discord commands, REST API

## Quick Start

### Using the CLI

```bash
# Activate Python environment
cd /root/moneo/terrain-maps
source venv/bin/activate

# Generate a terrain map
python cli.py --lat 40.7829 --lng -73.9654 --area 3 --resolution medium --output central_park.stl

# Interactive mode (no arguments)
python cli.py
```

### Using Discord

```
!terrain generate 40.7829 -73.9654 3 medium
!terrain list
!terrain delete terrain_40.7829_-73.9654.stl
```

### Using the API

```bash
curl -X POST http://localhost:3001/api/terrain/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 40.7829,
    "lng": -73.9654,
    "options": {
      "areaKm": 3,
      "resolution": "medium"
    }
  }'
```

## CLI Options

```
python cli.py --help

Required:
  --lat FLOAT          Center latitude (e.g., 40.7829)
  --lng FLOAT          Center longitude (e.g., -73.9654)

Optional:
  --marker-lat FLOAT   Marker latitude (defaults to center)
  --marker-lng FLOAT   Marker longitude (defaults to center)
  --area FLOAT         Area size in kilometers (default: 5.0)
  --resolution STR     Grid resolution: low/medium/high/ultra (default: medium)
  --exaggeration FLOAT Vertical exaggeration factor (default: 3.0)
  --size FLOAT         Print size in mm (default: 100)
  --preset STR         Size preset: coaster/desk/display/wall
  --output STR         Output filename (default: auto-generated)
  --split-export       Export as separate files for multi-color printing
  --no-optimize        Skip mesh optimization
```

## Split Export for Multi-Color Printing

Use `--split-export` to generate separate STL files for terrain, base, and marker. This allows you to print each component in a different color or material!

```bash
python cli.py --lat 40.7829 --lng -73.9654 --split-export --output my_map
```

**Output:**
- `my_map.zip` - Contains all files
  - `my_map_terrain.stl` - Topographical surface
  - `my_map_base.stl` - Platform/foundation
  - `my_map_marker.stl` - Location marker

**Print in multiple colors:**
1. Print base in black PLA
2. Print terrain in green/brown PLA
3. Print marker in red PLA
4. Assemble the three pieces

**Via API:**
```json
{
  "lat": 40.7829,
  "lng": -73.9654,
  "config": {
    "split_export": true
  }
}
```

## Resolution & Size Presets

**Resolution:**
- `low` - 50x50 grid (fast, draft quality)
- `medium` - 100x100 grid (balanced, recommended)
- `high` - 200x200 grid (detailed, slower)
- `ultra` - 300x300 grid (maximum detail, slow)

**Size Presets:**
- `coaster` - 100mm x 100mm
- `desk` - 150mm x 150mm
- `display` - 200mm x 200mm
- `wall` - 300mm x 300mm

## Example Locations

### Central Park, NYC
```bash
python cli.py --lat 40.7829 --lng -73.9654 --area 3 --preset desk
```
Great for: Urban parks, city views

### Mount Rainier, WA
```bash
python cli.py --lat 46.8523 --lng -121.7603 --area 10 --resolution high --exaggeration 2.0
```
Great for: Dramatic mountain terrain

### Grand Canyon, AZ
```bash
python cli.py --lat 36.0544 --lng -112.1401 --area 15 --resolution medium --exaggeration 4.0
```
Great for: Canyon terrain with high relief

### Coastal Beach
```bash
python cli.py --lat 37.7749 --lng -122.4194 --area 3 --exaggeration 1.5
```
Great for: Flat coastal areas (use lower exaggeration)

## Configuration

Edit `/root/moneo/terrain-maps/config.py` to customize:

- Default area size, resolution, vertical exaggeration
- Marker size and style
- 3D printing optimizations (wall thickness, mesh simplification)
- Output directory

## Output

Generated STL files are saved to: `/root/moneo/data/terrain-maps/`

Each file includes:
- **Terrain mesh** - 3D surface based on elevation data
- **Base** - Solid bottom for printing stability
- **Marker** - Cylinder marking your special spot

## 3D Printing Tips

1. **Material**: PLA recommended (easy to print, good detail)
2. **Layer Height**: 0.2mm for balanced quality/speed
3. **Supports**: Usually not needed (terrain has natural support)
4. **Infill**: 20% is sufficient for structural integrity
5. **Bed Adhesion**: Use brim or raft for large prints

## Customization Ideas

### For Proposals
```bash
# Exact spot where you proposed
python cli.py \
  --lat 40.7580 \
  --lng -73.9855 \
  --marker-lat 40.7580 \
  --marker-lng -73.9855 \
  --area 2 \
  --preset desk
```

### For Anniversaries
Mark the location of your first date with a custom marker:
```bash
python cli.py \
  --lat 37.8044 \
  --lng -122.2712 \
  --marker-lat 37.8045 \
  --marker-lng -122.2710 \
  --area 1 \
  --preset coaster \
  --output our_first_date.stl
```

### For Gifts
Generate multiple locations (childhood home, college, first job):
```bash
for location in "40.7829,-73.9654" "42.3601,-71.0589" "37.7749,-122.4194"; do
  IFS=',' read lat lng <<< "$location"
  python cli.py --lat $lat --lng $lng --preset coaster
done
```

## Future Enhancements

Planned features (not yet implemented):
- [ ] Building integration (OSM 3D buildings)
- [ ] Web frontend with interactive map
- [ ] 3D preview before generation
- [ ] Custom text engraving
- [ ] Texture mapping (satellite imagery overlay)
- [ ] Multiple export formats (OBJ, 3MF)
- [ ] Upgrade to Mapbox Terrain-RGB (higher resolution)

## Technical Details

**Architecture:**
- **Python Backend** - Elevation fetching, mesh generation, STL export
- **Node.js Integration** - API server, Discord bot integration
- **Elevation Data** - Open-Elevation API (90m resolution, global coverage)
- **3D Library** - Trimesh for mesh operations

**Dependencies:**
- numpy - Heightmap processing
- trimesh - 3D mesh operations
- requests - API calls
- scipy - Interpolation/smoothing

**Performance:**
- Low resolution: ~30 seconds
- Medium resolution: ~1-2 minutes
- High resolution: ~3-5 minutes
- Ultra resolution: ~10+ minutes

## Troubleshooting

**"Mesh is not watertight" warning:**
- This is common and usually okay for 3D printing
- Your slicer will handle it automatically
- If you have issues, try reducing resolution or exaggeration

**"Negative volume" warning:**
- Indicates face winding issues (cosmetic)
- STL will still slice and print correctly
- Will be fixed in future updates

**Flat terrain looks boring:**
- Increase vertical exaggeration: `--exaggeration 5.0`
- Reduce area size to focus on subtle features: `--area 2`
- Try different resolutions for better detail

**API timeout:**
- Reduce resolution: use `low` or `medium`
- Reduce area size: use smaller `--area` value
- Elevation API may be slow; just wait and retry

## API Reference

### POST /api/terrain/generate

Generate a terrain map.

**Request:**
```json
{
  "lat": 40.7829,
  "lng": -73.9654,
  "markerLat": 40.7580,
  "markerLng": -73.9855,
  "options": {
    "areaKm": 5,
    "resolution": "medium",
    "verticalExaggeration": 3,
    "printSize": 100,
    "filename": "my_terrain.stl"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "stlPath": "/root/moneo/data/terrain-maps/my_terrain.stl",
    "size": { "x": 98.0, "y": 98.0, "z": 65.0 },
    "estimatedPrintTime": 8.1,
    "estimatedMaterial": 9.0
  }
}
```

### GET /api/terrain/list

List all generated terrain files.

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "terrain_40.7829_-73.9654.stl",
      "path": "/root/moneo/data/terrain-maps/terrain_40.7829_-73.9654.stl",
      "size": 243712,
      "created": "2025-12-04T17:28:00.000Z",
      "modified": "2025-12-04T17:28:00.000Z"
    }
  ],
  "count": 1
}
```

### DELETE /api/terrain/:filename

Delete a terrain file.

**Response:**
```json
{
  "success": true,
  "message": "Deleted terrain_40.7829_-73.9654.stl"
}
```

## Credits

Built for Moneo AI Assistant System

Elevation data provided by Open-Elevation API (open-source)

## License

MIT License - Feel free to use and modify!
