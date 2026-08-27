import os

with open('core/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_handle = '''        if file.name.lower().endswith('.pdf'):
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
            return JsonResponse({"status": "error", "message": "Format file harus PDF!"}, status=400)'''

new_handle = '''        if file.name.lower().endswith('.pdf'):
            import base64
            file_data = file.read()
            if len(file_data) > 3 * 1024 * 1024:
                return JsonResponse({"status": "error", "message": "Ukuran maksimal PDF 3MB"}, status=400)
            
            base64_data = base64.b64encode(file_data).decode('utf-8')
            unique_filename = f"b64:{base64_data}"
                    
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
            return JsonResponse({"status": "error", "message": "Format file harus PDF!"}, status=400)'''

content = content.replace(old_handle, new_handle)

old_serve = '''@login_required
def serve_sop_file(request, filename):
    from urllib.parse import unquote
    filename = unquote(filename)
    file_path = os.path.join(settings.MEDIA_ROOT, 'sops', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    raise Http404("File not found")'''

new_serve = '''@login_required
def serve_sop_file(request, filename):
    from urllib.parse import unquote
    import base64
    from django.http import HttpResponse
    filename = unquote(filename)
    
    if filename.startswith("id_"):
        try:
            sop_id = int(filename[3:].replace(".pdf", ""))
            sop = Sops.objects.get(id=sop_id)
            if sop.filename.startswith("b64:"):
                b64_data = sop.filename[4:]
                pdf_data = base64.b64decode(b64_data)
                response = HttpResponse(pdf_data, content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{sop.title}.pdf"'
                return response
        except Exception:
            pass

    file_path = os.path.join(settings.MEDIA_ROOT, 'sops', filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    raise Http404("File not found")'''

content = content.replace(old_serve, new_serve)

old_delete = '''def delete_sop(request, sop_id):
    if not request.session.get('is_admin'):
        return JsonResponse({"status": "error", "message": "Akses ditolak!"}, status=403)
        
    try:
        sop = Sops.objects.get(id=sop_id)
        file_path = os.path.join(settings.MEDIA_ROOT, sop.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        sop.delete()
        return JsonResponse({"status": "success", "message": "SOP berhasil dihapus!"})'''

new_delete = '''def delete_sop(request, sop_id):
    if not request.session.get('is_admin'):
        return JsonResponse({"status": "error", "message": "Akses ditolak!"}, status=403)
        
    try:
        sop = Sops.objects.get(id=sop_id)
        if not sop.filename.startswith("b64:"):
            try:
                file_path = os.path.join(settings.MEDIA_ROOT, 'sops', sop.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                pass
        sop.delete()
        return JsonResponse({"status": "success", "message": "SOP berhasil dihapus!"})'''

content = content.replace(old_delete, new_delete)

with open('core/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
