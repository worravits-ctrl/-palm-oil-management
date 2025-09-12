#!/usr/bin/env python3

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("App created successfully")
    print("Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
