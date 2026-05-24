from app import app
from waitress import serve
import os

if __name__ == "__main__":
    # Production configuration
    port = int(os.environ.get("PORT", 5003))
    host = "0.0.0.0"
    
    print(f" * Starting Production Server (Waitress)")
    print(f" * Serving on http://{host}:{port}")
    print(f" * Environment: Production")
    
    # Run Waitress
    serve(app, host=host, port=port, threads=6)
