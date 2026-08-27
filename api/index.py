import sys
import os
import traceback
from flask import Flask

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
except Exception:
    err_tb = traceback.format_exc()
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return f"<h1>Deployment Error Traceback:</h1><pre>{err_tb}</pre>", 500
