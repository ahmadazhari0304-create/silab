import sys
import os

# Tambahkan path root agar bisa import app.py dari folder utama
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import object 'app' dari app.py dan assign ke variable top-level 'app'
import app as my_app
app = my_app.app
