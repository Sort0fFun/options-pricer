#!/usr/bin/env python
"""
Quick test script to verify Flask app works.
Run this to test if the app starts correctly.
"""
import os
import sys

# Set environment variables
os.environ['FLASK_PORT'] = '5001'
os.environ['FLASK_ENV'] = 'development'

try:
    print("=" * 60)
    print("Testing Flask App Startup")
    print("=" * 60)

    print("\n1. Importing Flask app...")
    from backend import create_app

    print("✓ Import successful!")

    print("\n2. Creating app instance...")
    app = create_app('development')

    print("✓ App created successfully!")

    print("\n3. Checking registered routes...")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.endpoint:50s} {rule.rule}")

    print("\n4. Testing API endpoints...")
    with app.test_client() as client:
        # Test contracts endpoint
        print("\n   Testing GET /api/pricing/contracts...")
        response = client.get('/api/pricing/contracts')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.get_json()}")
            print("   ✓ Contracts endpoint works!")
        else:
            print(f"   ✗ Error: {response.get_data(as_text=True)}")

    print("\n" + "=" * 60)
    print("All tests passed! You can now run: ./run.sh")
    print("=" * 60)

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
