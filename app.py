import os
import io
import csv
import time
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from functools import wraps

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

supabase_url = os.getenv("SUPABASE_URL", "https://hxsmcgsmsprguzbuiphy.supabase.co")
supabase_key = os.getenv("SUPABASE_KEY", "sb_publishable_empmzEuTidVkiBUmRErwnQ_5KcI-pwn")
supabase: Client = create_client(supabase_url, supabase_key)

class User(UserMixin):
    def __init__(self, id, username, is_admin):
        self.id = id
        self.username = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    try:
        response = supabase.table('users').select('*').eq('id', user_id).execute()
        if response.data:
            user = response.data[0]
            is_admin = user.get('is_admin', 0)
            return User(id=user['id'], username=user['username'], is_admin=is_admin)
    except Exception as e:
        print(f"Auth error: {e}")
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"status": "error", "message": "Akses ditolak"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- AUTH ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        response = supabase.table('users').select('*').eq('username', username).execute()
        
        if response.data:
            user = response.data[0]
            if check_password_hash(user['password_hash'], password):
                is_admin = user.get('is_admin', 0)
                user_obj = User(id=user['id'], username=user['username'], is_admin=is_admin)
                login_user(user_obj)
                return redirect(url_for('home'))
            else:
                flash('Username atau password salah.')
        else:
            flash('Username atau password salah.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        response = supabase.table('users').select('id').eq('username', username).execute()
        
        if response.data:
            flash('Username sudah digunakan.')
            return redirect(url_for('register'))
            
        supabase.table('users').insert({
            'username': username,
            'password_hash': generate_password_hash(password)
        }).execute()
        
        flash('Registrasi berhasil! Silakan login.')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- PAGES ---
@app.route('/')
@login_required
def home():
    return render_template('index.html', username=current_user.username, is_admin=current_user.is_admin)

# --- API ENDPOINTS ---
@app.route('/api/profile/password', methods=['PUT'])
@login_required
def update_password():
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"status": "error", "message": "Password lama dan baru wajib diisi!"}), 400
        
    response = supabase.table('users').select('*').eq('id', current_user.id).execute()
    
    if response.data:
        user = response.data[0]
        if check_password_hash(user['password_hash'], old_password):
            supabase.table('users').update({
                'password_hash': generate_password_hash(new_password)
            }).eq('id', current_user.id).execute()
            return jsonify({"status": "success", "message": "Password berhasil diubah!"})
            
    return jsonify({"status": "error", "message": "Password lama tidak sesuai!"}), 400

@app.route('/api/labs', methods=['GET'])
@login_required
def get_labs():
    response = supabase.table('labs').select('*').order('id').execute()
    return jsonify(response.data)

@app.route('/api/labs', methods=['POST'])
@login_required
def add_lab():
    data = request.json
    if not data or not data.get('nama_lab'):
        return jsonify({"status": "error", "message": "Nama Lab wajib diisi!"}), 400
    try:
        supabase.table('labs').insert({'nama_lab': data.get('nama_lab')}).execute()
        return jsonify({"status": "success", "message": "Lab berhasil ditambahkan!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/labs/<int:lab_id>', methods=['DELETE'])
@login_required
def delete_lab(lab_id):
    try:
        supabase.table('labs').delete().eq('id', lab_id).execute()
        return jsonify({"status": "success", "message": "Lab berhasil dihapus!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/labs/<int:lab_id>', methods=['PUT'])
@login_required
def edit_lab(lab_id):
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Data tidak valid"}), 400
    
    update_data = {}
    if data.get('nama_lab'): update_data['nama_lab'] = data.get('nama_lab')
    if data.get('status'): update_data['status'] = data.get('status')
    
    try:
        if update_data:
            supabase.table('labs').update(update_data).eq('id', lab_id).execute()
        return jsonify({"status": "success", "message": "Data lab berhasil diperbarui!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/items', methods=['GET'])
@login_required
def get_items():
    response = supabase.table('items').select('*').order('id').execute()
    return jsonify(response.data)

@app.route('/api/items', methods=['POST'])
@login_required
def add_item():
    data = request.json
    if not data or not data.get('nama_barang') or not data.get('value'):
        return jsonify({"status": "error", "message": "Nama Barang dan Value wajib diisi!"}), 400
    try:
        supabase.table('items').insert({
            'nama_barang': data.get('nama_barang'),
            'value': data.get('value')
        }).execute()
        return jsonify({"status": "success", "message": "Barang berhasil ditambahkan!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    try:
        supabase.table('items').delete().eq('id', item_id).execute()
        return jsonify({"status": "success", "message": "Barang berhasil dihapus!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    try:
        if current_user.is_admin:
            response = supabase.table('bookings').select('*, users(username)').order('tanggal', desc=True).order('start_time').execute()
        else:
            response = supabase.table('bookings').select('*, users(username)').or_(f"user_id.eq.{current_user.id},status.eq.approved").order('tanggal', desc=True).order('start_time').execute()
            
        data = response.data
        for d in data:
            if d.get('users'):
                d['peminjam'] = d['users'].get('username', 'Unknown')
            else:
                d['peminjam'] = 'Unknown'
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/book', methods=['POST'])
@login_required
def add_booking():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Data tidak valid!"}), 400
        
    required = ['nama_lab', 'tanggal', 'start_time', 'end_time', 'kelas', 'prodi', 'tujuan']
    if not all(data.get(k) for k in required):
        return jsonify({"status": "error", "message": "Semua field peminjaman wajib diisi!"}), 400

    try:
        # Overlap Checker (Global, ignore rejected bookings)
        overlap = supabase.table('bookings').select('*').eq('nama_lab', data['nama_lab']).eq('tanggal', data['tanggal']).lt('start_time', data['end_time']).gt('end_time', data['start_time']).neq('status', 'rejected').execute()

        if overlap.data:
            return jsonify({"status": "error", "message": f"Maaf, Jadwal {data['nama_lab']} di jam tersebut sudah bentrok!"}), 400

        supabase.table('bookings').insert({
            'user_id': current_user.id,
            'nama_lab': data['nama_lab'],
            'tanggal': data['tanggal'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'kelas': data['kelas'],
            'prodi': data['prodi'],
            'tujuan': data['tujuan'],
            'status': 'pending'
        }).execute()
        
        return jsonify({"status": "success", "message": "Peminjaman berhasil dicatat!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
@login_required
def update_booking(booking_id):
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Data tidak valid!"}), 400
        
    required = ['nama_lab', 'tanggal', 'start_time', 'end_time', 'kelas', 'prodi', 'tujuan']
    if not all(data.get(k) for k in required):
        return jsonify({"status": "error", "message": "Semua field peminjaman wajib diisi!"}), 400

    try:
        overlap = supabase.table('bookings').select('*').eq('nama_lab', data['nama_lab']).eq('tanggal', data['tanggal']).lt('start_time', data['end_time']).gt('end_time', data['start_time']).neq('id', booking_id).execute()

        if overlap.data:
            return jsonify({"status": "error", "message": f"Maaf, Jadwal {data['nama_lab']} di jam tersebut sudah bentrok!"}), 400

        supabase.table('bookings').update({
            'nama_lab': data['nama_lab'],
            'tanggal': data['tanggal'],
            'start_time': data['start_time'],
            'end_time': data['end_time'],
            'kelas': data['kelas'],
            'prodi': data['prodi'],
            'tujuan': data['tujuan']
        }).eq('id', booking_id).eq('user_id', current_user.id).execute()
        
        return jsonify({"status": "success", "message": "Jadwal berhasil diupdate!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
@login_required
def delete_booking(booking_id):
    try:
        supabase.table('bookings').delete().eq('id', booking_id).eq('user_id', current_user.id).execute()
        return jsonify({"status": "success", "message": "Jadwal peminjaman berhasil dihapus!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bhp', methods=['GET'])
@login_required
def get_bhp():
    response = supabase.table('bhp').select('*').eq('user_id', current_user.id).order('id', desc=True).execute()
    return jsonify(response.data)

@app.route('/api/bhp', methods=['POST'])
@login_required
def add_bhp():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Data tidak valid!"}), 400
        
    required = ['nama_barang', 'praktikum', 'jumlah', 'tanggal']
    if not all(data.get(k) for k in required):
        return jsonify({"status": "error", "message": "Semua field pemakaian BHP wajib diisi!"}), 400
        
    try:
        jumlah_int = int(data['jumlah'])
        if jumlah_int <= 0: raise ValueError
    except ValueError:
        return jsonify({"status": "error", "message": "Jumlah barang harus berupa angka positif!"}), 400

    try:
        supabase.table('bhp').insert({
            'user_id': current_user.id,
            'nama_barang': data['nama_barang'],
            'praktikum': data['praktikum'],
            'jumlah': jumlah_int,
            'tanggal': data['tanggal'],
            'prodi': data.get('prodi', 'D3')
        }).execute()
        return jsonify({"status": "success", "message": "Pemakaian BHP berhasil dicatat!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bhp/<int:bhp_id>', methods=['PUT'])
@login_required
def update_bhp(bhp_id):
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Data tidak valid!"}), 400
        
    required = ['nama_barang', 'praktikum', 'jumlah', 'tanggal']
    if not all(data.get(k) for k in required):
        return jsonify({"status": "error", "message": "Semua field wajib diisi!"}), 400
        
    try:
        jumlah_int = int(data['jumlah'])
        if jumlah_int <= 0: raise ValueError
    except ValueError:
        return jsonify({"status": "error", "message": "Jumlah harus berupa angka positif!"}), 400

    try:
        supabase.table('bhp').update({
            'nama_barang': data['nama_barang'],
            'praktikum': data['praktikum'],
            'jumlah': jumlah_int,
            'tanggal': data['tanggal'],
            'prodi': data.get('prodi', 'D3')
        }).eq('id', bhp_id).eq('user_id', current_user.id).execute()
        return jsonify({"status": "success", "message": "Data BHP berhasil diupdate!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/bhp/<int:bhp_id>', methods=['DELETE'])
@login_required
def delete_bhp(bhp_id):
    try:
        supabase.table('bhp').delete().eq('id', bhp_id).eq('user_id', current_user.id).execute()
        return jsonify({"status": "success", "message": "Data pemakaian BHP berhasil dihapus!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/dashboard/export")
@login_required
def export_dashboard():
    try:
        bookings_response = supabase.table("bookings").select("*, users(username)").order('id', desc=True).execute()
        bookings_data = bookings_response.data
        if not bookings_data:
            return jsonify({"status": "error", "message": "Tidak ada data peminjaman untuk diexport!"}), 404

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Peminjam', 'Ruang Lab', 'Tanggal', 'Waktu', 'Keperluan', 'Status', 'Username'])
        
        # Write data
        for b in bookings_data:
            username = b.get('users', {}).get('username', 'N/A') if b.get('users') else 'N/A'
            writer.writerow([
                b.get('id'),
                b.get('peminjam'),
                b.get('ruang_lab'),
                b.get('tanggal'),
                b.get('waktu'),
                b.get('keperluan'),
                b.get('status'),
                username
            ])
            
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=jadwal_peminjaman.csv"}
        )
    except Exception as e:
        print("Export Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/api/bhp/export")
@login_required
def export_bhp():
    try:
        bhp_response = supabase.table("bhp").select("*, users(username)").order('id', desc=True).execute()
        bhp_data = bhp_response.data
        if not bhp_data:
            return jsonify({"status": "error", "message": "Tidak ada data BHP untuk diexport!"}), 404

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Nama Barang', 'Praktikum', 'Jumlah', 'Tanggal', 'Prodi', 'Username'])
        
        # Write data
        for b in bhp_data:
            username = b.get('users', {}).get('username', 'N/A') if b.get('users') else 'N/A'
            writer.writerow([
                b.get('id'),
                b.get('nama_barang'),
                b.get('praktikum'),
                b.get('jumlah'),
                b.get('tanggal'),
                b.get('prodi'),
                username
            ])
            
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=log_bhp.csv"}
        )
    except Exception as e:
        print("Export Error:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads", "sops")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/sops', methods=['GET'])
@login_required
def get_sops():
    response = supabase.table('sops').select('*').order('id', desc=True).execute()
    return jsonify(response.data)

@app.route('/api/sops', methods=['POST'])
@login_required
def add_sop():
    if not current_user.is_admin:
        return jsonify({"status": "error", "message": "Akses ditolak!"}), 403
        
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file yang diupload"}), 400
    file = request.files['file']
    title = request.form.get('title')
    category = request.form.get('category')
    
    if not title or not category or file.filename == '':
        return jsonify({"status": "error", "message": "Semua field dan file wajib diisi!"}), 400
        
    if file and file.filename.lower().endswith('.pdf'):
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        try:
            supabase.table('sops').insert({
                'user_id': current_user.id,
                'title': title,
                'category': category,
                'filename': unique_filename
            }).execute()
            return jsonify({"status": "success", "message": "SOP berhasil diupload!"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Format file harus PDF!"}), 400

@app.route('/api/sops/<int:sop_id>', methods=['DELETE'])
@login_required
def delete_sop(sop_id):
    if not current_user.is_admin:
        return jsonify({"status": "error", "message": "Akses ditolak!"}), 403
        
    try:
        response = supabase.table('sops').select('filename').eq('id', sop_id).execute()
        if response.data:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], response.data[0]['filename'])
            if os.path.exists(file_path):
                os.remove(file_path)
            supabase.table('sops').delete().eq('id', sop_id).execute()
        return jsonify({"status": "success", "message": "SOP berhasil dihapus!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/uploads/sops/<path:filename>')
@login_required
def serve_sop_file(filename):
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- USER MANAGEMENT APIs ---
@app.route('/api/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    response = supabase.table('users').select('id, username, is_admin').order('id').execute()
    return jsonify(response.data)

@app.route('/api/users', methods=['POST'])
@login_required
@admin_required
def create_user():
    data = request.json
    username = data.get('username') if data else None
    password = data.get('password') if data else None
    is_admin = 1 if data and data.get('is_admin') else 0
    
    if not username or not password:
        return jsonify({"status": "error", "message": "Username dan password wajib diisi!"}), 400
        
    existing = supabase.table('users').select('id').eq('username', username).execute()
    if existing.data:
        return jsonify({"status": "error", "message": "Username sudah digunakan!"}), 400
        
    supabase.table('users').insert({
        'username': username,
        'password_hash': generate_password_hash(password),
        'is_admin': is_admin
    }).execute()
    
    return jsonify({"status": "success", "message": "Pengguna berhasil dibuat!"})

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    data = request.json
    
    user_res = supabase.table('users').select('*').eq('id', user_id).execute()
    if not user_res.data:
        return jsonify({"status": "error", "message": "Pengguna tidak ditemukan!"}), 404
    user = user_res.data[0]

    username = data.get('username', user['username'])
    if not username:
        username = user['username']
        
    password = data.get('password')
    
    if 'is_admin' in data:
        is_admin = 1 if data.get('is_admin') else 0
    else:
        is_admin = user.get('is_admin', 0)
        
    if user['username'] == 'admin' and is_admin == 0:
        return jsonify({"status": "error", "message": "Tidak dapat mencabut hak admin dari akun utama!"}), 400
        
    if username != user['username']:
        existing = supabase.table('users').select('id').eq('username', username).execute()
        if existing.data:
            return jsonify({"status": "error", "message": "Username sudah digunakan!"}), 400

    update_payload = {
        'username': username,
        'is_admin': is_admin
    }
    if password:
        update_payload['password_hash'] = generate_password_hash(password)

    supabase.table('users').update(update_payload).eq('id', user_id).execute()
    return jsonify({"status": "success", "message": "Pengguna berhasil diperbarui!"})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    target = supabase.table('users').select('username').eq('id', user_id).execute()
    if target.data and target.data[0]['username'] == 'admin':
        return jsonify({"status": "error", "message": "Tidak dapat menghapus akun admin utama!"}), 400
        
    supabase.table('users').delete().eq('id', user_id).execute()
    return jsonify({"status": "success", "message": "Pengguna berhasil dihapus!"})

@app.route('/api/bookings/<int:id>/status', methods=['PUT'])
@login_required
@admin_required
def update_booking_status(id):
    data = request.json
    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return jsonify({"status": "error", "message": "Status tidak valid"}), 400
    
    supabase.table('bookings').update({'status': status}).eq('id', id).execute()
    return jsonify({"status": "success", "message": f"Peminjaman berhasil di-{status}"})

@app.route('/api/maintenance', methods=['GET', 'POST'])
@login_required
@admin_required
def handle_maintenance():
    if request.method == 'POST':
        data = request.json
        required = ['nama_lab', 'start_date', 'end_date', 'keterangan']
        if not all(data.get(k) for k in required):
            return jsonify({"status": "error", "message": "Semua field wajib diisi!"}), 400
            
        supabase.table('maintenance').insert({
            'nama_lab': data['nama_lab'],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'keterangan': data['keterangan'],
            'user_id': current_user.id
        }).execute()
        return jsonify({"status": "success", "message": "Jadwal perbaikan berhasil ditambahkan!"})
    else:
        response = supabase.table('maintenance').select('*').order('start_date', desc=True).execute()
        return jsonify(response.data)

@app.route('/api/maintenance/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_maintenance(id):
    supabase.table('maintenance').delete().eq('id', id).execute()
    return jsonify({"status": "success", "message": "Jadwal perbaikan dihapus!"})

@app.route('/api/dashboard/summary', methods=['GET'])
@login_required
def dashboard_summary():
    import datetime
    today = datetime.date.today().strftime('%Y-%m-%d')
    
    active_resp = supabase.table('bookings').select('id', count='exact').eq('status', 'approved').eq('tanggal', today).execute()
    active_count = active_resp.count if active_resp.count else 0
    
    pending_resp = supabase.table('bookings').select('id', count='exact').eq('status', 'pending').eq('tanggal', today).execute()
    pending_count = pending_resp.count if pending_resp.count else 0
    
    maint_resp = supabase.table('labs').select('id', count='exact').eq('status', 'Perbaikan').execute()
    maint_count = maint_resp.count if maint_resp.count else 0
    
    return jsonify({
        "active": active_count,
        "pending": pending_count,
        "maintenance": maint_count
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
