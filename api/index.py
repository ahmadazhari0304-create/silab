import sys
import os

# Tambahkan path root agar bisa import app.py dari folder utama
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import object 'app' dari app.py
from app import app
