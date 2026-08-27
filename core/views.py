import os
import time
from functools import wraps
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden, FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import Users, Labs, Items, Bookings, Bhp, Sops, Maintenance
from datetime import date
import json

# Decorator Custom untuk Login
def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('user_id'):
            if request.path.startswith('/api/'):
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        is_admin = request.session.get('is_admin')
        if not is_admin:
            if request.path.startswith('/api/'):
                return JsonResponse({"status": "error", "message": "Access denied"}, status=403)
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- PAGE ROUTES ---
@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {
        'is_admin': request.session.get('is_admin'),
        'username': request.session.get('username')
    })

from django.contrib import messages

def login_view(request):
    if request.session.get('user_id'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = Users.objects.get(username=username)
            if check_password_hash(user.password_hash, password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['is_admin'] = bool(user.is_admin)
                return redirect('dashboard')
            else:
                messages.error(request, 'Username atau password salah!')
        except Users.DoesNotExist:
            messages.error(request, 'Username atau password salah!')
            
    return render(request, 'login.html')

@login_required
def user_management(request):
    if not request.session.get('is_admin'):
        return redirect('dashboard')
    return render(request, 'user_management.html', {'is_admin': True, 'username': request.session.get('username')})

@login_required
def schedule(request):
    return render(request, 'schedule.html', {
        'is_admin': request.session.get('is_admin'),
        'username': request.session.get('username')
    })

@login_required
def request_history(request):
    return render(request, 'request_history.html', {
        'is_admin': request.session.get('is_admin'),
        'username': request.session.get('username')
    })

@login_required
def sop_management(request):
    return render(request, 'sop_management.html', {
        'is_admin': request.session.get('is_admin'),
        'username': request.session.get('username')
    })

@login_required
def sops_view(request):
    return render(request, 'sops.html', {
        'is_admin': request.session.get('is_admin'),
        'username': request.session.get('username')
    })

@login_required
def admin_schedule(request):
    if not request.session.get('is_admin'):
        return redirect('dashboard')
    return render(request, 'admin_schedule.html', {'is_admin': True, 'username': request.session.get('username')})

@login_required
def request_management(request):
    if not request.session.get('is_admin'):
        return redirect('dashboard')
    return render(request, 'request_management.html', {'is_admin': True, 'username': request.session.get('username')})

@login_required
def pbb_page(request):
    return render(request, 'pbb.html', {
        'is_admin': request.session.get('is_admin'),
        'username': request.session.get('username')
    })

@login_required
def admin_maintenance(request):
    if not request.session.get('is_admin'):
        return redirect('dashboard')
    return render(request, 'admin_maintenance.html', {'is_admin': True, 'username': request.session.get('username')})


# --- API ROUTES ---

@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        try:
            user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Username atau password salah!"}, status=401)
            
        if check_password_hash(user.password_hash, password):
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_admin'] = bool(user.is_admin)
            return JsonResponse({
                "status": "success", 
                "is_admin": bool(user.is_admin), 
                "redirect_url": "/"
            })
        else:
            return JsonResponse({"status": "error", "message": "Username atau password salah!"}, status=401)
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
def api_logout(request):
    request.session.flush()
    return redirect('login')

@login_required
@require_http_methods(["GET"])
def get_labs(request):
    labs = list(Labs.objects.values())
    return JsonResponse(labs, safe=False)

@login_required
@require_http_methods(["GET"])
def get_items(request):
    items = list(Items.objects.values())
    return JsonResponse(items, safe=False)

@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def handle_bookings(request):
    if request.method == 'GET':
        bookings = Bookings.objects.select_related('user').all()
        result = []
        for b in bookings:
            result.append({
                'id': b.id,
                'nama_lab': b.nama_lab,
                'tanggal': b.tanggal.strftime('%Y-%m-%d'),
                'start_time': b.start_time.strftime('%H:%M:%S'),
                'end_time': b.end_time.strftime('%H:%M:%S'),
                'kelas': b.kelas,
                'prodi': b.prodi,
                'tujuan': b.tujuan,
                'status': b.status,
                'users': {'username': b.user.username} if b.user else None
            })
        return JsonResponse(result, safe=False)
        
    elif request.method == 'POST':
        data = json.loads(request.body)
        required_fields = ['nama_lab', 'tanggal', 'start_time', 'end_time', 'kelas', 'prodi', 'tujuan']
        if not all(data.get(field) for field in required_fields):
            return JsonResponse({"status": "error", "message": "Semua field wajib diisi!"}, status=400)
            
        try:
            booking = Bookings(
                nama_lab=data['nama_lab'],
                tanggal=data['tanggal'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                kelas=data['kelas'],
                prodi=data['prodi'],
                tujuan=data['tujuan'],
                user_id=request.session['user_id'],
                status='pending'
            )
            booking.save()
            return JsonResponse({"status": "success", "message": "Pendaftaran berhasil, menunggu persetujuan Admin!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def handle_bhp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            bhp = Bhp(
                nama_barang=data['nama_barang'],
                praktikum=data['praktikum'],
                jumlah=data['jumlah'],
                tanggal=data['tanggal'],
                prodi=data.get('prodi', 'D3'),
                user_id=request.session['user_id']
            )
            bhp.save()
            return JsonResponse({"status": "success", "message": "Permintaan BHP berhasil!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        bhps = Bhp.objects.select_related('user').all().order_by('-tanggal')
        res = []
        for b in bhps:
            res.append({
                'id': b.id,
                'nama_barang': b.nama_barang,
                'praktikum': b.praktikum,
                'jumlah': b.jumlah,
                'tanggal': b.tanggal.strftime('%Y-%m-%d'),
                'prodi': b.prodi,
                'users': {'username': b.user.username} if b.user else None
            })
        return JsonResponse(res, safe=False)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_bhp(request, bhp_id):
    try:
        bhp = Bhp.objects.get(id=bhp_id)
        if request.session['user_id'] == bhp.user_id or request.session.get('is_admin'):
            bhp.delete()
            return JsonResponse({"status": "success", "message": "BHP berhasil dihapus!"})
        return JsonResponse({"status": "error", "message": "Akses ditolak"}, status=403)
    except Bhp.DoesNotExist:
        return JsonResponse({"status": "error", "message": "BHP tidak ditemukan"}, status=404)

@login_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def handle_sops(request):
    if request.method == 'GET':
        sops = Sops.objects.select_related('user').all()
        res = []
        for s in sops:
            res.append({
                'id': s.id,
                'title': s.title,
                'category': s.category,
                'filename': s.filename,
                'users': {'username': s.user.username} if s.user else None
            })
        return JsonResponse(res, safe=False)
        
    elif request.method == 'POST':
        if not request.session.get('is_admin'):
            return JsonResponse({"status": "error", "message": "Akses ditolak!"}, status=403)
            
        if 'file' not in request.FILES:
            return JsonResponse({"status": "error", "message": "Tidak ada file yang diupload"}, status=400)
            
        file = request.FILES['file']
        title = request.POST.get('title')
        category = request.POST.get('category')
        
        if not title or not category or file.name == '':
            return JsonResponse({"status": "error", "message": "Semua field dan file wajib diisi!"}, status=400)
            
        if file.name.lower().endswith('.pdf'):
            filename = secure_filename(file.name)
            unique_filename = f"{int(time.time())}_{filename}"
            upload_path = os.path.join(settings.MEDIA_ROOT, unique_filename)
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            with open(upload_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                    
            try:
                sop = Sops(
                    title=title,
                    category=category,
                    filename=unique_filename,
                    user_id=request.session['user_id']
                )
                sop.save()
                return JsonResponse({"status": "success", "message": "SOP berhasil diupload!"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
        else:
            return JsonResponse({"status": "error", "message": "Format file harus PDF!"}, status=400)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_sop(request, sop_id):
    if not request.session.get('is_admin'):
        return JsonResponse({"status": "error", "message": "Akses ditolak!"}, status=403)
        
    try:
        sop = Sops.objects.get(id=sop_id)
        file_path = os.path.join(settings.MEDIA_ROOT, sop.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        sop.delete()
        return JsonResponse({"status": "success", "message": "SOP berhasil dihapus!"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@login_required
def serve_sop_file(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    raise Http404("File not found")

@login_required
@admin_required
@require_http_methods(["GET", "POST"])
@csrf_exempt
def handle_users(request):
    if request.method == 'GET':
        users = list(Users.objects.values('id', 'username', 'is_admin').order_by('id'))
        return JsonResponse(users, safe=False)
        
    elif request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        is_admin = 1 if data.get('is_admin') else 0
        
        if not username or not password:
            return JsonResponse({"status": "error", "message": "Username dan password wajib diisi!"}, status=400)
            
        if Users.objects.filter(username=username).exists():
            return JsonResponse({"status": "error", "message": "Username sudah digunakan!"}, status=400)
            
        Users.objects.create(
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=is_admin
        )
        return JsonResponse({"status": "success", "message": "Pengguna berhasil dibuat!"})

@login_required
@admin_required
@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def handle_user_detail(request, user_id):
    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Pengguna tidak ditemukan!"}, status=404)
        
    if request.method == 'PUT':
        data = json.loads(request.body)
        username = data.get('username', user.username)
        password = data.get('password')
        is_admin = 1 if data.get('is_admin') else 0
        
        if user.username == 'admin' and is_admin == 0:
            return JsonResponse({"status": "error", "message": "Tidak dapat mencabut hak admin dari akun utama!"}, status=400)
            
        if username != user.username and Users.objects.filter(username=username).exists():
            return JsonResponse({"status": "error", "message": "Username sudah digunakan!"}, status=400)

        user.username = username
        user.is_admin = is_admin
        if password:
            user.password_hash = generate_password_hash(password)
        user.save()
        
        return JsonResponse({"status": "success", "message": "Pengguna berhasil diperbarui!"})
        
    elif request.method == 'DELETE':
        if user.username == 'admin':
            return JsonResponse({"status": "error", "message": "Tidak dapat menghapus akun admin utama!"}, status=400)
            
        user.delete()
        return JsonResponse({"status": "success", "message": "Pengguna berhasil dihapus!"})

@login_required
@admin_required
@csrf_exempt
@require_http_methods(["PUT"])
def update_booking_status(request, id):
    data = json.loads(request.body)
    status = data.get('status')
    if status not in ['approved', 'rejected']:
        return JsonResponse({"status": "error", "message": "Status tidak valid"}, status=400)
    
    try:
        booking = Bookings.objects.get(id=id)
        booking.status = status
        booking.save()
        return JsonResponse({"status": "success", "message": f"Peminjaman berhasil di-{status}"})
    except Bookings.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Booking not found"}, status=404)

@login_required
@admin_required
@csrf_exempt
@require_http_methods(["GET", "POST"])
def handle_maintenance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        required = ['nama_lab', 'start_date', 'end_date', 'keterangan']
        if not all(data.get(k) for k in required):
            return JsonResponse({"status": "error", "message": "Semua field wajib diisi!"}, status=400)
            
        Maintenance.objects.create(
            nama_lab=data['nama_lab'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            keterangan=data['keterangan'],
            user_id=request.session['user_id']
        )
        return JsonResponse({"status": "success", "message": "Jadwal perbaikan berhasil ditambahkan!"})
    else:
        maint = list(Maintenance.objects.values().order_by('-start_date'))
        return JsonResponse(maint, safe=False)

@login_required
@admin_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_maintenance(request, id):
    try:
        Maintenance.objects.get(id=id).delete()
        return JsonResponse({"status": "success", "message": "Jadwal perbaikan dihapus!"})
    except Maintenance.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Not found"}, status=404)

@login_required
def dashboard_summary(request):
    today = date.today()
    active_count = Bookings.objects.filter(status='approved', tanggal=today).count()
    pending_count = Bookings.objects.filter(status='pending', tanggal=today).count()
    maint_count = Labs.objects.filter(status='Perbaikan').count()
    
    return JsonResponse({
        "active": active_count,
        "pending": pending_count,
        "maintenance": maint_count
    })
