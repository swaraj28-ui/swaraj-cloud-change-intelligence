import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Retrieve port from env, fallback to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run server locally, exposing host for potential network reviews
    app.run(host='0.0.0.0', port=port, debug=True)
