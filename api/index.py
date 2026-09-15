import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class VercelMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        # Vercel provides the original client requested path in HTTP_X_FORWARDED_URI or HTTP_X_MATCHED_PATH
        forwarded_uri = environ.get('HTTP_X_FORWARDED_URI')
        matched_path = environ.get('HTTP_X_MATCHED_PATH')
        
        target_path = forwarded_uri or matched_path
        if target_path:
            environ['PATH_INFO'] = target_path.split('?')[0]
        elif environ.get('PATH_INFO', '').startswith('/api'):
            environ['PATH_INFO'] = '/'

        return self.wsgi_app(environ, start_response)

app.wsgi_app = VercelMiddleware(app.wsgi_app)
