import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silab.settings')

from django.core.wsgi import get_wsgi_application
app = application = get_wsgi_application()
