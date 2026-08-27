import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app
except Exception:
    err = traceback.format_exc()
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/html; charset=utf-8')]
        start_response(status, response_headers)
        return [f"<h1>Vercel Boot Exception:</h1><pre>{err}</pre>".encode('utf-8')]
