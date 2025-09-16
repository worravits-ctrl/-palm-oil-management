#!/usr/bin/env python3
"""
Palm Oil Management System - Production Server with Turso Support
"""

import os
from app import create_app

# Create Flask app
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable (for cloud deployment)
    port = int(os.environ.get('PORT', 5000))

    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    )