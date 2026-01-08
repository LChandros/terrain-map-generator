# 🏔️ 3D Terrain Map Generator - Quick Start

## What is This?

Generate 3D printable topographical maps of any location on Earth! Perfect for:
- 💍 Marking proposal spots
- ❤️ Commemorating first date locations
- 🎁 Unique personalized gifts
- 🏔️ Displaying favorite hiking trails

## Try It Now!

### Test with the CLI

```bash
cd /root/moneo/terrain-maps
source venv/bin/activate

# Generate Central Park, NYC (medium resolution, ~1 minute)
python cli.py --lat 40.7829 --lng -73.9654 --area 3 --resolution medium --output test.stl

# Check the output
ls -lh /root/moneo/data/terrain-maps/test.stl
```

### Test via Discord

```
!terrain generate 40.7829 -73.9654 3 medium
```

### Test via API

```bash
# Start API server (if not already running)
pm2 restart moneo-api

# Generate terrain
curl -X POST http://localhost:3001/api/terrain/generate \
  -H "X-API-Key: $MONEO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 40.7829,
    "lng": -73.9654,
    "options": {
      "areaKm": 3,
      "resolution": "medium"
    }
  }'

# List generated files
curl http://localhost:3001/api/terrain/list \
  -H "X-API-Key: $MONEO_API_KEY"
```

## How to Find Coordinates

### Google Maps
1. Right-click on location → "What's here?"
2. Click coordinates at bottom to copy
3. Format: `40.7829, -73.9654`

### Example Coordinates

**Cities:**
- New York, Central Park: `40.7829, -73.9654`
- San Francisco, Golden Gate: `37.8199, -122.4783`
- Paris, Eiffel Tower: `48.8584, 2.2945`

**Mountains:**
- Mount Rainier, WA: `46.8523, -121.7603`
- Mount Everest: `27.9881, 86.9250`
- Matterhorn: `45.9763, 7.6586`

**Natural Wonders:**
- Grand Canyon: `36.0544, -112.1401`
- Yellowstone: `44.4280, -110.5885`
- Yosemite Valley: `37.7455, -119.5933`

## Usage Tips

**For Flat Areas (beaches, cities):**
```bash
python cli.py --lat 37.7749 --lng -122.4194 --exaggeration 1.5
```
Lower exaggeration prevents it from looking too spiky.

**For Dramatic Mountains:**
```bash
python cli.py --lat 46.8523 --lng -121.7603 --exaggeration 3.0 --resolution high
```
Higher exaggeration shows off the terrain features.

**For Gift Coasters:**
```bash
python cli.py --lat 40.7829 --lng -73.9654 --preset coaster --output "our_spot.stl"
```

**Mark Exact Spot:**
```bash
python cli.py \
  --lat 40.7829 \
  --lng -73.9654 \
  --marker-lat 40.7580 \
  --marker-lng -73.9855 \
  --area 2
```
Center the map on one location, but mark a different specific spot.

## 3D Print Settings

**Recommended:**
- Material: PLA
- Layer Height: 0.2mm
- Infill: 20%
- Supports: Not needed
- Print Time: ~3-8 hours (depending on size)

## What's Next?

Full documentation: `/root/moneo/terrain-maps/README.md`

**Future Website Idea:**
1. Add web frontend with map interface
2. Allow users to click on map to select location
3. Offer customization (text engraving, multiple markers)
4. Provide download link or direct-to-print service
5. Potential business: personalized 3D printed maps!

## Example Business Use Cases

### E-commerce Site
- User visits site, enters address or picks location on map
- Customizes: marker position, text, size
- Previews 3D model
- Pays $29.99, receives STL file or physical print

### Gift Shop
- Pre-generated popular locations (NYC, Paris, Tokyo)
- Custom orders for specific locations
- Package as wedding/anniversary gifts

### Real Estate
- Generate 3D maps of properties
- Show terrain context for land sales
- Unique marketing material

## Cost Structure (for website)

**Using Open-Elevation (Current):**
- Free API, unlimited requests
- Can handle ~1000 requests/day
- Good for MVP/prototype

**Upgrading to Mapbox Terrain-RGB:**
- $0.50 per 1000 requests
- 10m resolution (vs 90m)
- Better quality for $0.0005 per map
- Minimal cost at scale

## Ready to Build the Website?

Next steps:
1. Create React frontend with Mapbox/Leaflet
2. Add 3D preview with Three.js
3. Implement payment (Stripe)
4. Deploy to production
5. Market to proposal/anniversary crowd!

You've already got the hard part (the generation engine) done! 🎉
