#!/usr/bin/env python3
"""
Flask API server for terrain map generation
Provides REST endpoints for the Valentine's Day map e-commerce site
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from terrain_generator import TerrainGenerator
import config

app = Flask(__name__)
CORS(app)  # Allow requests from frontend

# Initialize generator
generator = TerrainGenerator(
    output_dir=config.OUTPUT_DIR
)

@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'service': 'terrain-map-generator'
    })


@app.route('/api/generate', methods=['POST'])
def generate_map():
    """
    Generate a 3D terrain map

    Expected request body:
    {
        "lat": 40.7580,
        "lon": -73.9855,
        "radius": 500,
        "config": {
            "area_km": 5.0,
            "resolution": "medium",
            "vertical_exaggeration": 3.0,
            "print_size_mm": 100,
            "marker_lat": 40.7580,
            "marker_lon": -73.9855,
            "marker_height_mm": 3.0,
            "marker_radius_mm": 2.0
        }
    }
    """
    try:
        data = request.json

        # Extract coordinates
        center_lat = data.get('lat')
        center_lng = data.get('lon')

        if center_lat is None or center_lng is None:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters: lat, lon'
            }), 400

        # Extract config
        user_config = data.get('config', {})

        # Generate unique order code
        order_code = f"MAP{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Build options
        split_export = user_config.get('split_export', False)
        options = {
            'area_km': user_config.get('area_km', config.DEFAULT_AREA_KM),
            'resolution': user_config.get('resolution', 'medium'),
            'vertical_exaggeration': user_config.get('vertical_exaggeration', config.DEFAULT_VERTICAL_EXAGGERATION),
            'print_size_mm': user_config.get('print_size_mm', config.PRINT_SIZE_PRESETS['coaster']),
            'marker_height_mm': user_config.get('marker_height_mm', config.DEFAULT_MARKER_HEIGHT_MM),
            'marker_radius_mm': user_config.get('marker_radius_mm', config.DEFAULT_MARKER_RADIUS_MM),
            'filename': f"{order_code}.{'zip' if split_export else 'stl'}",
            'split_export': split_export,
            'optimize': True
        }

        # Get marker coordinates (defaults to center)
        marker_lat = user_config.get('marker_lat', center_lat)
        marker_lng = user_config.get('marker_lon', center_lng)

        print(f"\n{'='*60}")
        print(f"NEW MAP GENERATION REQUEST")
        print(f"Order Code: {order_code}")
        print(f"Location: ({center_lat}, {center_lng})")
        print(f"Marker: ({marker_lat}, {marker_lng})")
        print(f"Options: {options}")
        print(f"{'='*60}\n")

        # Generate the map
        result = generator.generate(
            center_lat=center_lat,
            center_lng=center_lng,
            marker_lat=marker_lat,
            marker_lng=marker_lng,
            options=options
        )

        if not result['success']:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error occurred')
            }), 500

        # Save metadata
        metadata = {
            'order_code': order_code,
            'center_lat': center_lat,
            'center_lng': center_lng,
            'marker_lat': marker_lat,
            'marker_lng': marker_lng,
            'options': options,
            'created_at': datetime.now().isoformat(),
            'stl_file': f"{order_code}.stl",
            'print_info': result['print_info']
        }

        metadata_path = os.path.join(config.OUTPUT_DIR, f"{order_code}.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return jsonify({
            'success': True,
            'order_code': order_code,
            'preview_url': f'/api/preview/{order_code}',
            'download_url': f'/api/download/{order_code}',
            'print_info': result['print_info'],
            'message': 'Map generated successfully!'
        })

    except Exception as e:
        print(f"ERROR generating map: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/download/<order_code>', methods=['GET'])
def download_stl(order_code):
    """Download STL file for a given order code"""
    try:
        stl_path = os.path.join(config.OUTPUT_DIR, f"{order_code}.stl")

        if not os.path.exists(stl_path):
            return jsonify({
                'success': False,
                'error': 'STL file not found'
            }), 404

        return send_file(
            stl_path,
            as_attachment=True,
            download_name=f"{order_code}.stl",
            mimetype='application/octet-stream'
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preview/<order_code>', methods=['GET'])
def get_preview(order_code):
    """
    Get preview image for a map
    Note: Preview generation not yet implemented
    Returns placeholder for now
    """
    # TODO: Implement preview image generation
    # For now, return metadata as JSON
    try:
        metadata_path = os.path.join(config.OUTPUT_DIR, f"{order_code}.json")

        if not os.path.exists(metadata_path):
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        return jsonify({
            'success': True,
            'order_code': order_code,
            'metadata': metadata,
            'note': 'Preview image generation coming soon'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/orders/<order_code>', methods=['GET'])
def get_order_info(order_code):
    """Get information about a specific order"""
    try:
        metadata_path = os.path.join(config.OUTPUT_DIR, f"{order_code}.json")
        stl_path = os.path.join(config.OUTPUT_DIR, f"{order_code}.stl")

        if not os.path.exists(metadata_path):
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        # Add file info
        metadata['stl_exists'] = os.path.exists(stl_path)
        if metadata['stl_exists']:
            metadata['stl_size_mb'] = os.path.getsize(stl_path) / (1024 * 1024)

        return jsonify({
            'success': True,
            'order': metadata
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    # Create output directory if it doesn't exist
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    print("\n" + "="*60)
    print("TERRAIN MAP API SERVER")
    print("="*60)
    print(f"Output directory: {config.OUTPUT_DIR}")
    print(f"Starting server on http://0.0.0.0:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
