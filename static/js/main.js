
    // =============================================
    // MAIN APPLICATION JAVASCRIPT
    // =============================================

    // --- Globals ---
    // Custom Confirm Logic
    let confirmCallback = null;
    function showCustomConfirm(message, callback) {
        document.getElementById('confirm-message').innerText = message;
        confirmCallback = callback;
        document.getElementById('modal-confirm').style.display = 'flex';
    }
    function executeConfirm() {
        document.getElementById('modal-confirm').style.display = 'none';
        if (confirmCallback) {
            confirmCallback();
            confirmCallback = null;
        }
    }
    function closeConfirmModal(e) {
        if (e.target.id === 'modal-confirm') {
            document.getElementById('modal-confirm').style.display = 'none';
        }
    }
    window.currentUserIsAdmin = window.APP_CONFIG.isAdmin;
    let currentBookings = [];
    let currentBHP = [];
    let currentCalendarDate = new Date();
    let currentBhpProdi = 'D3';
    let isAdmin = false;

    async function loadMaintenance() {
        try {
            const res = await fetch('/api/maintenance');
            const data = await res.json();
            const tbody = document.getElementById('table-maint-body');
            if (tbody) {
                tbody.innerHTML = '';
                data.forEach(m => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${m.nama_lab}</td>
                        <td>${m.start_date}</td>
                        <td>${m.end_date}</td>
                        <td>${m.keterangan}</td>
                        <td style="text-align: center;">
                            <button class="btn-table" onclick="deleteMaintenance(${m.id})" style="color:#C53030; background: rgba(197,48,48,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer;">Hapus</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }
            
            // Also populate select
            const labsRes = await fetch('/api/labs');
            const labs = await labsRes.json();
            const sel = document.getElementById('maint-lab');
            if (sel) {
                sel.innerHTML = '<option value="">Pilih Lab</option>';
                labs.forEach(l => {
                    let optColor = l.status === 'Perbaikan' ? 'color: #d9534f;' : 'color: #10b981;';
                    sel.innerHTML += `<option value="${l.nama_lab}" style="${optColor} font-weight: 500;">${l.nama_lab} ${l.status === 'Perbaikan' ? '(Perbaikan)' : ''}</option>`;
                });
            }
        } catch(e) { console.error('Error loading maintenance:', e); }
    }

    async function submitMaintenance(e) {
        e.preventDefault();
        const body = {
            nama_lab: document.getElementById('maint-lab').value,
            start_date: document.getElementById('maint-start').value,
            end_date: document.getElementById('maint-end').value,
            keterangan: document.getElementById('maint-ket').value
        };
        const res = await fetch('/api/maintenance', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        });
        const data = await res.json();
        showToast(data.message, data.status === 'error');
        if(data.status === 'success') {
            document.getElementById('form-add-maintenance').reset();
            loadMaintenance();
            if (typeof updateDashboardSummary === 'function') updateDashboardSummary();
        }
    }

    function deleteMaintenance(id) { 
        showCustomConfirm('Hapus jadwal perbaikan ini?', async () => { 
            const res = await fetch(`/api/maintenance/${id}`, {method: 'DELETE'});
            const data = await res.json();
            showToast(data.message, data.status === 'error');
            if(data.status === 'success') {
                loadMaintenance();
                if (typeof updateDashboardSummary === 'function') updateDashboardSummary();
            }
        });
    }


    function openEditLabModal(id, nama_lab, status) {
        document.getElementById('edit-lab-id').value = id;
        document.getElementById('edit-lab-name').value = nama_lab;
        document.getElementById('edit-lab-status').value = status || 'Tersedia';
        document.getElementById('modal-edit-lab').style.display = 'flex';
    }

    async function submitEditLab(e) {
        e.preventDefault();
        const id = document.getElementById('edit-lab-id').value;
        const data = {
            nama_lab: document.getElementById('edit-lab-name').value,
            status: document.getElementById('edit-lab-status').value
        };
        try {
            const res = await fetch(`/api/labs/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const resData = await res.json();
            if (resData.status === 'success') {
                showToast(resData.message);
                document.getElementById('modal-edit-lab').style.display = 'none';
                loadLabs();
            } else {
                showToast(resData.message, true);
            }
        } catch (e) { showToast('Gagal update lab', true); }
    }


    function openAddBookingModal(dateStr) {
        document.getElementById('form-booking').reset();
        document.getElementById('book-tanggal').value = dateStr;
        document.getElementById('modal-add-booking').style.display = 'flex';
    }

    // --- Init ---
    document.addEventListener('DOMContentLoaded', function() {
        const activeUser = window.APP_CONFIG.username;
        const isUserAdmin = window.currentUserIsAdmin;
        if (isUserAdmin) {
            activateAdminMode();
        }

        switchTab('home');
        loadLabs();
        loadItems();
        loadBookings();
        loadBHP();
        loadSOP();
        updateDashboard();

        // Init timepicker if available
        if (typeof mdtimepicker !== 'undefined') {
            try {
                mdtimepicker('#book-start', { format: 'hh:mm', is24hour: true });
                mdtimepicker('#book-end', { format: 'hh:mm', is24hour: true });
                mdtimepicker('#edit-book-start', { format: 'hh:mm', is24hour: true });
                mdtimepicker('#edit-book-end', { format: 'hh:mm', is24hour: true });
            } catch(e) { console.warn('MDTimePicker init error:', e); }
        }
    });

    // --- Sidebar Toggle ---
    function toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('expanded');
        if (!sidebar.classList.contains('expanded')) {
            const dropdown = document.getElementById('profile-dropdown');
            if (dropdown) dropdown.style.display = 'none';
        }
    }

    // --- Profile Dropdown Toggle ---
    function toggleProfileDropdown() {
        const sidebar = document.querySelector('.sidebar');
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown.style.display === 'none' || dropdown.style.display === '') {
            sidebar.classList.add('expanded');
            dropdown.style.display = 'block';
        } else {
            dropdown.style.display = 'none';
        }
    }

    // --- Tab Navigation ---
    function switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
        document.querySelectorAll('.menu-btn').forEach(el => el.classList.remove('active'));

        const tabEl = document.getElementById(tabId);
        if (tabEl) tabEl.classList.add('active');

        const btn = document.querySelector(`.menu-btn[onclick*="'${tabId}'"]`);
        if (btn) btn.classList.add('active');

        if (tabId === 'peminjaman') { loadBookings(); renderCalendar(); }
        if (tabId === 'bhp') loadBHP();
        if (tabId === 'sop') loadSOP();
        if (tabId === 'home') updateDashboard();
        if (tabId === 'data-silab') { loadLabs(); loadItems(); }
        if (tabId === 'kelola-pengguna') { loadUsers();
            loadMaintenance(); }
        
    }

    // --- Toast Notification ---
    function showToast(msg, isError = false) {
        let toast = document.getElementById('toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'toast';
            toast.style.cssText = 'position:fixed;bottom:30px;right:30px;padding:14px 24px;border-radius:12px;color:#fff;font-weight:600;font-size:14px;z-index:9999;transition:all 0.4s ease;opacity:0;transform:translateY(20px);max-width:400px;box-shadow:0 8px 32px rgba(0,0,0,0.15);';
            document.body.appendChild(toast);
        }
        toast.innerText = msg;
        toast.style.background = isError ? '#E07B5F' : '#1B8A7A';
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
        }, 3000);
    }

    // --- Admin Check ---
    function verifyAdmin(e) {
        if (e) e.preventDefault();
        const pw = document.getElementById('admin-password');
        if (pw) {
            checkAdmin(pw.value);
            pw.value = '';
        }
    }

    function activateAdminMode() {
        isAdmin = true;
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = '');
        const bhpAksiTh = document.getElementById('bhp-aksi-th');
        if (bhpAksiTh) bhpAksiTh.style.display = '';
        const btnExport = document.getElementById('btn-export-excel');
        if (btnExport) btnExport.style.display = '';
        loadUsers();
            loadMaintenance();
        const navKelolaPengguna = document.getElementById('nav-kelola-pengguna');
        if (navKelolaPengguna) navKelolaPengguna.style.display = 'flex';
        const navDataSilab = document.getElementById('nav-data-silab');
        if (navDataSilab) navDataSilab.style.display = 'flex';
        
        loadBookings();
        loadBHP();
    }

    function checkAdmin(password) {
        if (password === 'admin123') {
            activateAdminMode();
            showToast('Mode admin aktif!');
            const modal = document.getElementById('admin-modal');
            if (modal) modal.style.display = 'none';
        } else {
            showToast('Password admin salah!', true);
        }
    }

    // --- Load Labs ---
    async function loadLabs() {
        try {
            const res = await fetch('/api/labs');
            const labs = await res.json();

            const bookLabSelect = document.getElementById('book-lab');
            if (bookLabSelect) {
                bookLabSelect.innerHTML = '<option value="">Pilih Lab</option>';
                labs.forEach(lab => {
                    let optColor = lab.status === 'Perbaikan' ? 'color: #d9534f;' : 'color: #10b981;';
                    bookLabSelect.innerHTML += `<option value="${lab.nama_lab}" style="${optColor} font-weight: 500;">${lab.nama_lab} ${lab.status === 'Perbaikan' ? '(Perbaikan)' : ''}</option>`;
                });
            }

            const calFilter = document.getElementById('calendar-lab-filter');
            if (calFilter) {
                const currentVal = calFilter.value;
                calFilter.innerHTML = '<option value="">Semua Lab</option>';
                labs.forEach(lab => {
                    let optColor = lab.status === 'Perbaikan' ? 'color: #d9534f;' : 'color: #10b981;';
                    calFilter.innerHTML += `<option value="${lab.nama_lab}" style="${optColor} font-weight: 500;">${lab.nama_lab} ${lab.status === 'Perbaikan' ? '(Perbaikan)' : ''}</option>`;
                });
                calFilter.value = currentVal;
            }

            const labBody = document.getElementById('table-lab-body');
            if (labBody) {
                labBody.innerHTML = '';
                labs.forEach(lab => {
                    let statusBadge = lab.status === 'Perbaikan' 
                        ? '<span class="status-badge pending">Perbaikan</span>' 
                        : '<span class="status-badge approved">Tersedia</span>';
                        
                    labBody.innerHTML += `<tr>
                        <td><strong>${lab.nama_lab}</strong></td>
                        <td>${statusBadge}</td>
                        <td style="text-align:center;">
                            <div style="display:flex; justify-content:center; gap:8px;">
                                <button onclick="openEditLabModal(${lab.id}, '${lab.nama_lab}', '${lab.status || 'Tersedia'}')" class="btn-table" title="Edit" style="color:var(--primary); background: rgba(33, 150, 243, 0.1); border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s;">
                                    <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                                    Edit
                                </button>
                                <button onclick="deleteLab(${lab.id})" class="btn-table" title="Hapus" style="color:#d9534f; background: rgba(217,83,79,0.1); border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s;">
                                    <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                    Hapus
                                </button>
                            </div>
                        </td>
                    </tr>`;
                });
            }
        } catch (e) { console.error('Error loading labs:', e); }
    }

    async function submitLab(e) {
        e.preventDefault();
        const name = document.getElementById('new-lab-name').value;
        try {
            const res = await fetch('/api/labs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nama_lab: name })
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('new-lab-name').value = '';
                loadLabs();
            } else { showToast(data.message, true); }
        } catch (e) { showToast('Gagal menambah lab', true); }
    }

    function deleteLab(id) { 
        showCustomConfirm('Hapus lab ini?', async () => { 
            try {
                const res = await fetch(`/api/labs/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === 'success') { showToast(data.message); loadLabs(); }
                else { showToast(data.message, true); }
            } catch (e) { showToast('Gagal hapus lab', true); }
        });
    }

    // --- Load Items ---
    async function loadItems() {
        try {
            const res = await fetch('/api/items');
            const items = await res.json();

            const selectBhp = document.getElementById('bhp-barang');
            if (selectBhp) {
                selectBhp.innerHTML = '<option value="">Pilih Barang...</option>';
                items.forEach(item => {
                    selectBhp.innerHTML += `<option value="${item.nama_barang}">${item.nama_barang} (${item.value})</option>`;
                });
            }

            const itemBody = document.getElementById('table-item-body');
            if (itemBody) {
                itemBody.innerHTML = '';
                items.forEach(item => {
                    itemBody.innerHTML += `<tr>
                        <td><strong>${item.nama_barang}</strong></td>
                        <td><span style="background: rgba(138, 133, 126, 0.1); color: var(--text-main); padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 500;">${item.value}</span></td>
                        <td style="text-align:center;">
                            <button onclick="deleteItem(${item.id})" class="btn-table" title="Hapus" style="color:#d9534f; background: rgba(217,83,79,0.1); border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; display:inline-flex; align-items:center; gap:6px; transition:all 0.2s;">
                                <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                Hapus
                            </button>
                        </td>
                    </tr>`;
                });
            }
        } catch (e) { console.error('Error loading items:', e); }
    }

    async function submitItem(e) {
        e.preventDefault();
        const name = document.getElementById('new-item-name').value;
        const val = document.getElementById('new-item-val').value;
        try {
            const res = await fetch('/api/items', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nama_barang: name, value: val })
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('new-item-name').value = '';
                document.getElementById('new-item-val').value = '';
                loadItems();
            } else { showToast(data.message, true); }
        } catch (e) { showToast('Gagal menambah barang', true); }
    }

    function deleteItem(id) { 
        showCustomConfirm('Hapus item ini?', async () => { 
            try {
                const res = await fetch(`/api/items/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === 'success') { showToast(data.message); loadItems(); }
                else { showToast(data.message, true); }
            } catch (e) { showToast('Gagal hapus item', true); }
        });
    }

    // Sub-tab toggler for Data SILAB
    function switchSilabTab(tab) {
        const labTab = document.getElementById('silab-tab-lab');
        const bhpTab = document.getElementById('silab-tab-bhp');
        const labBtn = document.getElementById('tab-btn-lab');
        const bhpBtn = document.getElementById('tab-btn-bhp');

        if (tab === 'lab') {
            labTab.style.display = 'block';
            bhpTab.style.display = 'none';
            labBtn.style.color = 'var(--primary)';
            labBtn.style.borderBottom = '2px solid var(--primary)';
            labBtn.style.fontWeight = '700';
            bhpBtn.style.color = 'var(--text-muted)';
            bhpBtn.style.borderBottom = '2px solid transparent';
            bhpBtn.style.fontWeight = '600';
        } else {
            labTab.style.display = 'none';
            bhpTab.style.display = 'block';
            bhpBtn.style.color = 'var(--primary)';
            bhpBtn.style.borderBottom = '2px solid var(--primary)';
            bhpBtn.style.fontWeight = '700';
            labBtn.style.color = 'var(--text-muted)';
            labBtn.style.borderBottom = '2px solid transparent';
            labBtn.style.fontWeight = '600';
        }
    }

    // =============================================
    // BOOKINGS (Peminjaman)
    // =============================================
    
    // Sub-tab toggler for Peminjaman
    function switchPinjamTab(tab) {
        const formTab = document.getElementById('pinjam-tab-form');
        const riwayatTab = document.getElementById('pinjam-tab-riwayat');
        const formBtn = document.getElementById('tab-btn-pinjam-form');
        const riwayatBtn = document.getElementById('tab-btn-pinjam-riwayat');

        if (tab === 'form') {
            formTab.style.display = 'block';
            riwayatTab.style.display = 'none';
            formBtn.style.color = 'var(--primary)';
            formBtn.style.borderBottom = '2px solid var(--primary)';
            formBtn.style.fontWeight = '700';
            riwayatBtn.style.color = 'var(--text-muted)';
            riwayatBtn.style.borderBottom = '2px solid transparent';
            riwayatBtn.style.fontWeight = '600';
        } else {
            formTab.style.display = 'none';
            riwayatTab.style.display = 'block';
            riwayatBtn.style.color = 'var(--primary)';
            riwayatBtn.style.borderBottom = '2px solid var(--primary)';
            riwayatBtn.style.fontWeight = '700';
            formBtn.style.color = 'var(--text-muted)';
            formBtn.style.borderBottom = '2px solid transparent';
            formBtn.style.fontWeight = '600';
        }
    }

    function updateBookingStatus(id, status) { 
        showCustomConfirm(`Apakah Anda yakin ingin ${status === 'approved' ? 'menyetujui' : 'menolak'} peminjaman ini?`, async () => { 
            try {
                const res = await fetch(`/api/bookings/${id}/status`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({status})
                });
                const data = await res.json();
                showToast(data.message, data.status === 'error');
                if(data.status === 'success') {
                    loadBookings();
                    updateDashboardSummary();
                }
            } catch(e) {
                showToast('Gagal memproses peminjaman', true);
            }
        });
    }

    async function loadBookings() {
        const res = await fetch('/api/bookings');
        const bookings = await res.json();
        
        // Simpan ke state global untuk digunakan oleh Calendar
        currentBookings = bookings;
        if (typeof renderCalendar === 'function') {
            renderCalendar();
        }
        
        const tbody = document.getElementById('table-bookings-body');
        tbody.innerHTML = '';
        
        bookings.forEach((b, index) => {
            const tr = document.createElement('tr');
            
            let actionBtn = '';
            
            if (window.currentUserIsAdmin) {
                if (b.status === 'pending') {
                    actionBtn = `
                        <div style="display: flex; gap: 6px; justify-content: center;">
                            <button class="btn-table" onclick="updateBookingStatus(${b.id}, 'approved')" style="color:#1B8A7A; background: rgba(27,138,122,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px;">Setujui</button>
                            <button class="btn-table" onclick="updateBookingStatus(${b.id}, 'rejected')" style="color:#C53030; background: rgba(197,48,48,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px;">Tolak</button>
                        </div>
                    `;
                } else {
                    actionBtn = `<span style="font-size:12px; color:var(--text-muted);">-</span>`;
                }
            } else {
                if (b.status === 'pending') {
                    actionBtn = `
                        <button class="btn-table" onclick="deleteBooking(${b.id})" style="color:#C53030; background: rgba(197,48,48,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;" title="Batalkan Peminjaman">Batalkan</button>
                    `;
                } else {
                    actionBtn = `<span style="font-size:12px; color:var(--text-muted);">-</span>`;
                }
            }
            
            let statusBadge = '';
            if (b.status === 'pending') {
                statusBadge = `<span style="background:#FEFCBF; color:#B7791F; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:600;">Menunggu</span>`;
            } else if (b.status === 'approved') {
                statusBadge = `<span style="background:#C6F6D5; color:#22543D; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:600;">Disetujui</span>`;
            } else {
                statusBadge = `<span style="background:#FED7D7; color:#822727; padding:4px 8px; border-radius:12px; font-size:12px; font-weight:600;">Ditolak</span>`;
            }
            
            let peminjamHtml = window.currentUserIsAdmin ? `<div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Oleh: ${b.peminjam || 'Anda'}</div>` : '';

            tr.innerHTML = `
                <td><div style="font-weight:600; color:var(--text-main);">${b.nama_lab}</div>${peminjamHtml}</td>
                <td><div style="font-weight:500;">${b.tanggal}</div></td>
                <td>
                    <div style="display:inline-flex; align-items:center; gap:6px; background:#F7FAFC; padding:4px 8px; border-radius:6px; font-size:13px; font-weight:500; color:var(--text-main);">
                        <span>${b.start_time}</span>
                        <span style="color:var(--text-muted);">-</span>
                        <span>${b.end_time}</span>
                    </div>
                </td>
                <td>${statusBadge}</td>
                <td style="text-align: center;">
                    ${actionBtn}
                </td>
            `;
            tbody.appendChild(tr);
        });
    }


    async function submitBooking(e) {
        e.preventDefault();
        const payload = {
            nama_lab: document.getElementById('book-lab').value,
            tanggal: document.getElementById('book-tanggal').value,
            start_time: document.getElementById('book-start').value,
            end_time: document.getElementById('book-end').value,
            kelas: document.getElementById('book-kelas').value,
            prodi: document.getElementById('book-prodi').value,
            tujuan: document.getElementById('book-tujuan').value
        };

        try {
            const res = await fetch('/api/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('form-booking').reset();
                loadBookings();
                document.getElementById('modal-add-booking').style.display='none';
                updateDashboard();
            } else {
                showToast(data.message, true);
                showToast(data.message, true);
            }
        } catch (err) { showToast('Gagal mencatat peminjaman', true); }
    }

    async function deleteBooking(id) {
        try {
            const res = await fetch(`/api/bookings/${id}`, { method: 'DELETE' });
            if (!res.ok) {
                showToast('Gagal menghubungi server.', true);
                return;
            }
            const data = await res.json();
            if (data.status === 'success') { 
                showToast(data.message);
                const modal = document.getElementById('modal-day-detail');
                if (modal) modal.style.display = 'none';
                loadBookings(); 
                updateDashboard(); 
            } else {
                showToast(data.message, true);
            }
        } catch (e) { 
            showToast('Gagal menghapus peminjaman', true);
            showToast('Gagal hapus peminjaman', true); 
        }
    }

    // =============================================
    // BHP
    // =============================================
    function switchBhpProdi(prodi) {
        currentBhpProdi = prodi;
        const btnD3 = document.getElementById('btn-bhp-d3');
        const btnS1 = document.getElementById('btn-bhp-s1');
        
        if(prodi === 'D3') {
            btnD3.style.color = 'var(--primary)';
            btnD3.style.borderBottom = '2px solid var(--primary)';
            btnD3.style.fontWeight = '700';
            btnS1.style.color = 'var(--text-muted)';
            btnS1.style.borderBottom = '2px solid transparent';
            btnS1.style.fontWeight = '600';
        } else {
            btnS1.style.color = 'var(--primary)';
            btnS1.style.borderBottom = '2px solid var(--primary)';
            btnS1.style.fontWeight = '700';
            btnD3.style.color = 'var(--text-muted)';
            btnD3.style.borderBottom = '2px solid transparent';
            btnD3.style.fontWeight = '600';
        }

        const logTitle = document.getElementById('bhp-log-title');
        if (logTitle) logTitle.innerText = `Riwayat Log Pemakaian (${prodi === 'D3' ? 'D3' : 'S1'} Keperawatan)`;

        loadBHP();
    }

    async function loadBHP() {
        try {
            const res = await fetch('/api/bhp');
            const allBhp = await res.json();
            currentBHP = allBhp;

            const filtered = allBhp.filter(b => b.prodi && b.prodi.startsWith(currentBhpProdi));
            const tbody = document.getElementById('table-bhp-body');
            if (!tbody) return;
            tbody.innerHTML = '';

            if (filtered.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#8a857e;">Belum ada data BHP.</td></tr>';
                return;
            }

            filtered.forEach(b => {
                const aksiCell = `<td style="text-align:center; white-space: nowrap;">
                        <button onclick="editBhp(${b.id})" class="btn-table" title="Edit" style="color:#1B8A7A; background: rgba(27,138,122,0.1); border:none; padding:8px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>
                        <button onclick="deleteBHP(${b.id})" class="btn-table" title="Hapus" style="color:#d9534f; background: rgba(217,83,79,0.1); border:none; padding:8px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg></button>
                       </td>`;
                tbody.innerHTML += `<tr>
                    <td><strong>${b.nama_barang}</strong></td>
                    <td>${b.praktikum}</td>
                    <td style="text-align:center;">${b.jumlah}</td>
                    <td>${b.tanggal}</td>
                    ${aksiCell}
                </tr>`;
            });
        } catch (e) { console.error('Error loading BHP:', e); }
    }

    async function submitBHP(e) {
        e.preventDefault();
        const payload = {
            nama_barang: document.getElementById('bhp-barang').value,
            praktikum: document.getElementById('bhp-praktikum').value,
            jumlah: document.getElementById('bhp-jumlah').value,
            tanggal: document.getElementById('bhp-tanggal').value,
            prodi: currentBhpProdi === 'D3' ? 'D3 Keperawatan' : 'S1 Keperawatan'
        };

        try {
            const res = await fetch('/api/bhp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('form-bhp').reset();
                loadBHP();
                updateDashboard();
            } else { showToast(data.message, true); }
        } catch (err) { showToast('Gagal mencatat BHP', true); }
    }

    function deleteBHP(id) {
        showCustomConfirm('Hapus BHP ini?', async () => {
            try {
                const res = await fetch(`/api/bhp/${id}`, { method: 'DELETE' });
                if (!res.ok) {
                    showToast('Gagal menghubungi server.', true);
                    return;
                }
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message);
                    loadBHP();
                    updateDashboard();
                } else {
                    showToast(data.message, true);
                }
            } catch (e) {
                showToast('Gagal hapus BHP', true);
            }
        });
    }

    async function exportBhpExcel() {
        try {
            const res = await fetch(`/api/bhp/export?prodi=${currentBhpProdi}`);
            if (res.ok) {
                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `BHP_${currentBhpProdi}_Export.xlsx`;
                a.click();
                showToast('Export berhasil!');
            } else { showToast('Gagal export', true); }
        } catch (e) { showToast('Gagal export', true); }
    }

    // =============================================
    // SOP
    // =============================================
    async function loadSOP() {
        try {
            const res = await fetch('/api/sops');
            const sops = await res.json();
            const tbody = document.getElementById('table-sop-body');
            if (!tbody) return;
            tbody.innerHTML = '';

            if (sops.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#8a857e;">Belum ada SOP.</td></tr>';
                return;
            }

            sops.forEach((s, i) => {
                let deleteBtn = window.currentUserIsAdmin ? `<button onclick="deleteSOP(${s.id})" class="btn-table" title="Hapus" style="color:#d9534f; background: rgba(217,83,79,0.1); border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; display:flex; align-items:center; gap:6px; transition:all 0.2s;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg> Hapus</button>` : '';
                let pdfUrl = s.filename.startsWith('b64:') ? `/uploads/sops/id_${s.id}.pdf` : `/uploads/sops/${s.filename}`;
            tbody.innerHTML += `<tr>
                <td style="text-align: center;">${i + 1}</td>
                <td>${s.title}</td>
                <td>${s.category}</td>
                <td style="text-align: center; display: flex; justify-content: center; gap: 8px;">
                    <a href="${pdfUrl}" target="_blank" class="btn-table" title="Lihat PDF" style="color:#1B8A7A; background: rgba(27,138,122,0.1); text-decoration:none; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; display:flex; align-items:center; gap:6px; transition:all 0.2s;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> Lihat PDF</a>
                    ${deleteBtn}
                </td>
            </tr>`;
            });
        } catch (e) { console.error('Error loading SOP:', e); }
    }

    async function submitSOP(e) {
        e.preventDefault();
        const title = document.getElementById('sop-title').value;
        const category = document.getElementById('sop-category').value;
        const fileInput = document.getElementById('sop-file');
        
        if (!fileInput.files.length) {
            showToast('Pilih file PDF terlebih dahulu', true);
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('category', category);
        formData.append('file', fileInput.files[0]);

        try {
            const res = await fetch('/api/sops', { method: 'POST', body: formData });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('form-sop').reset();
                loadSOP();
                const modal = document.getElementById('sop-upload-modal');
                if (modal) modal.style.display = 'none';
            } else { showToast(data.message, true); }
        } catch (err) { showToast('Gagal upload SOP', true); }
    }

    function deleteSOP(id) { 
        showCustomConfirm('Hapus SOP ini?', async () => { 
            try {
                const res = await fetch(`/api/sops/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === 'success') { showToast(data.message); loadSOP(); }
            } catch (e) { showToast('Gagal hapus SOP', true); }
        });
    }

    // =============================================
    // CALENDAR
    // =============================================
    function changeMonth(dir) {
        currentCalendarDate.setMonth(currentCalendarDate.getMonth() + dir);
        renderCalendar();
    }

    function renderCalendar() {
        const grid = document.getElementById('monthly-calendar-grid');
        const monthYearLabel = document.getElementById('calendar-month-year');
        if (!grid || !monthYearLabel) return;

        const year = currentCalendarDate.getFullYear();
        const month = currentCalendarDate.getMonth();
        const months = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember'];
        monthYearLabel.innerText = `${months[month]} ${year}`;

        const firstDay = new Date(year, month, 1).getDay();
        const totalDays = new Date(year, month + 1, 0).getDate();
        const today = new Date();

        const labFilter = document.getElementById('calendar-lab-filter');
        const filterLab = labFilter ? labFilter.value : '';

        let filteredBookings = currentBookings;
        if (filterLab) {
            filteredBookings = currentBookings.filter(b => b.nama_lab === filterLab);
        }

        grid.innerHTML = '';

        // Empty cells for days before 1st
        for (let i = 0; i < firstDay; i++) {
            const cell = document.createElement('div');
            cell.className = 'cal-day empty';
            grid.appendChild(cell);
        }

        for (let day = 1; day <= totalDays; day++) {
            const cell = document.createElement('div');
            cell.className = 'cal-day';

            const monthStr = String(month + 1).padStart(2, '0');
            const dayStr = String(day).padStart(2, '0');
            const dateKey = `${year}-${monthStr}-${dayStr}`;

            if (today.getFullYear() === year && today.getMonth() === month && today.getDate() === day) {
                cell.classList.add('today');
            }

            cell.innerText = day;

            const dateBookings = filteredBookings.filter(b => b.tanggal === dateKey);
            if (dateBookings.length > 0) {
                if (dateBookings.some(b => b.status === 'pending')) {
                    cell.classList.add('has-pending');
                } else {
                    cell.classList.add('has-booking');
                }
            }

            cell.addEventListener('click', () => {
                openDayDetailModal(dateKey, dateBookings);
            });
            grid.appendChild(cell);
        }
    }

    function filterBookings() {
        renderCalendar();
    }

    function openDayDetailModal(dateKey, bookings) {
        let modal = document.getElementById('modal-day-detail');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'modal-day-detail';
            modal.className = 'modal-overlay';
            modal.onclick = function(e) { if (e.target === modal) modal.style.display = 'none'; };
            modal.innerHTML = `<div class="modal-content" onclick="event.stopPropagation()">
                <button class="modal-close" onclick="document.getElementById('modal-day-detail').style.display='none'">&times;</button>
                <div class="modal-header"><h2 id="day-detail-title"></h2></div>
                <div id="day-detail-body" style="max-height: 350px; overflow-y: auto; padding-right: 8px;"></div>
            </div>`;
            document.body.appendChild(modal);
        }

        document.getElementById('day-detail-title').innerText = `Jadwal ${dateKey}`;
        const body = document.getElementById('day-detail-body');

        let buttonHtml = `
            <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid #e2e8f0;">
                <button onclick="document.getElementById('modal-day-detail').style.display='none'; openAddBookingModal('${dateKey}');" class="btn-submit" style="width: 100%; justify-content: center;">
                    <svg style="width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2;margin-right:4px;" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"></path></svg>
                    Pinjam Lab di Tanggal Ini
                </button>
            </div>
        `;

        if (bookings.length === 0) {
            body.innerHTML = '<p style="color:#8a857e;">Tidak ada jadwal di tanggal ini.</p>' + buttonHtml;
        } else {
            let html = '<div style="display:flex;flex-direction:column;gap:12px;">';
            bookings.forEach(b => {
                let statusColor, statusText, textColor;
                if(b.status === 'pending') { statusColor = '#FEFCBF'; textColor = '#B7791F'; statusText = 'Menunggu'; }
                else if(b.status === 'approved') { statusColor = '#C6F6D5'; textColor = '#22543D'; statusText = 'Disetujui'; }
                else { statusColor = '#FED7D7'; textColor = '#822727'; statusText = 'Ditolak'; }
                
                let statusBadge = `<span style="background:${statusColor}; color:${textColor}; padding:4px 8px; border-radius:12px; font-size:11px; font-weight:600;">${statusText}</span>`;

                let actionButtons = '';
                if(window.currentUserIsAdmin && b.status === 'pending') {
                    actionButtons += `<button onclick="updateBookingStatus(${b.id}, 'approved');document.getElementById('modal-day-detail').style.display='none';" class="btn-table" style="color:#22543D; background: #C6F6D5; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;">Setujui</button>`;
                    actionButtons += `<button onclick="updateBookingStatus(${b.id}, 'rejected');document.getElementById('modal-day-detail').style.display='none';" class="btn-table" style="color:#822727; background: #FED7D7; border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;">Tolak</button>`;
                }
                
                const isOwner = (b.peminjam && b.peminjam === window.APP_CONFIG.username) || (!b.peminjam);
                if (window.currentUserIsAdmin || isOwner) {
                    actionButtons += `<button onclick="editBooking(${b.id});document.getElementById('modal-day-detail').style.display='none';" class="btn-table" style="color:#1B8A7A; background: rgba(27,138,122,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2" style="vertical-align:-2px;margin-right:4px;"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg> Edit</button>`;
                    actionButtons += `<button onclick="deleteBooking(${b.id});" class="btn-table" style="color:#d9534f; background: rgba(217,83,79,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2" style="vertical-align:-2px;margin-right:4px;"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg> Hapus</button>`;
                }

                html += `<div style="padding:16px;background:#f8f9fa;border:1px solid #e2e8f0;border-radius:12px;display:flex;flex-direction:column;gap:8px;box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <strong style="color:var(--text-dark);font-size:15px;">${b.nama_lab}</strong>
                            <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">Oleh: ${b.peminjam || 'Peminjam'}</div>
                        </div>
                        ${statusBadge}
                    </div>
                    <div style="font-size:13px;font-weight:600;color:var(--primary);"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2" style="vertical-align:-2px;margin-right:4px;"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> ${b.start_time} - ${b.end_time}</div>
                    <div style="font-size:13px;color:#8a857e;"><svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2" style="vertical-align:-2px;margin-right:4px;"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg> ${b.kelas} | ${b.tujuan}</div>
                    <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
                        ${actionButtons}
                    </div>
                </div>`;
            });

            html += '</div>';
            html += buttonHtml;
            body.innerHTML = html;
        }

        modal.style.display = 'flex';
    }

    // =============================================
    // DASHBOARD
    // =============================================
    async function updateDashboard() {
        try {
            const [bookingsRes, bhpRes, labsRes, summaryRes] = await Promise.all([
                fetch('/api/bookings'),
                fetch('/api/bhp'),
                fetch('/api/labs'),
                fetch('/api/dashboard/summary')
            ]);
            const bookings = await bookingsRes.json();
            const bhp = await bhpRes.json();
            const labs = await labsRes.json();
            const summary = await summaryRes.json();

            const today = new Date().toISOString().split('T')[0];
            const todayBookings = bookings.filter(b => b.tanggal === today);

            // Summary card metrics
            const countActive = document.getElementById('count-active');
            if (countActive) countActive.innerText = summary.active || 0;
            const countPending = document.getElementById('count-pending');
            if (countPending) countPending.innerText = summary.pending || 0;
            const countMaintenance = document.getElementById('count-maintenance');
            if (countMaintenance) countMaintenance.innerText = summary.maintenance || 0;

            // Summary card
            const summaryCount = document.getElementById('total-bookings-count');
            if (summaryCount) summaryCount.innerText = todayBookings.length;

            const summaryLab = document.getElementById('total-labs-count');
            if (summaryLab) summaryLab.innerText = labs.length;

            // Today's schedule
            const scheduleList = document.getElementById('today-schedule-list');
            if (scheduleList) {
                if (todayBookings.length === 0) {
                    scheduleList.innerHTML = `<div class="dash-empty-state">
                        <svg width="40" height="40" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        <p>Tidak ada jadwal hari ini.</p>
                    </div>`;
                } else {
                    scheduleList.innerHTML = '';
                    todayBookings.forEach(b => {
                        scheduleList.innerHTML += `
                        <div style="display:flex; align-items:center; gap:12px; padding:10px 14px; background:#f8fafc; border-radius:12px; border-left: 4px solid #1B8A7A;">
                            <div style="flex:1;">
                                <div style="font-size:14px; font-weight:700; color:#1e293b;">${b.nama_lab}</div>
                                <div style="font-size:12px; color:#64748b; margin-top:2px;">${b.start_time} â€“ ${b.end_time} &middot; ${b.kelas || ''}</div>
                            </div>
                            <span style="font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px; background:rgba(27,138,122,0.12); color:#1B8A7A;">Aktif</span>
                        </div>`;
                    });
                }
            }

            const todayCount = document.getElementById('today-schedule-badge');
            if (todayCount) todayCount.innerText = todayBookings.length;

            // Usage percentage + animate SVG donut
            const usageBadge = document.getElementById('utilization-badge');
            const donutRing = document.getElementById('donut-ring');
            const donutText = document.getElementById('donut-text');
            if (labs.length > 0) {
                const usedLabs = new Set(todayBookings.map(b => b.nama_lab)).size;
                const pct = Math.round((usedLabs / labs.length) * 100);
                const circumference = 314;
                const offset = circumference - (pct / 100) * circumference;
                if (donutRing) { donutRing.style.strokeDashoffset = offset; }
                if (donutText) { donutText.textContent = pct + '%'; }
                
                if (usageBadge) {
                    if (pct === 0) { usageBadge.innerText = 'Kosong'; }
                    else if (pct < 50) { usageBadge.innerText = 'Renggang'; }
                    else if (pct < 80) { usageBadge.innerText = 'Padat'; }
                    else { usageBadge.innerText = 'Penuh'; }
                }
            }

            // Recent BHP
            const bhpList = document.getElementById('dashboard-bhp-list');
            if (bhpList) {
                if (bhp.length === 0) {
                    bhpList.innerHTML = '<tr><td colspan="4" class="dash-td-empty">Belum ada log BHP.</td></tr>';
                } else {
                    bhpList.innerHTML = '';
                    bhp.slice(0, 5).forEach(b => {
                        bhpList.innerHTML += `<tr>
                            <td>${b.tanggal}</td>
                            <td>${b.prodi || '-'}</td>
                            <td>${b.nama_barang}</td>
                            <td style="text-align:right;font-weight:700;color:#1B8A7A;">${b.jumlah}</td>
                        </tr>`;
                    });
                }
            }

            // Recent Bookings (Peminjaman Terbaru Anda)
            const recentBookingsList = document.getElementById('active-booking-list');
            if (recentBookingsList) {
                if (bookings.length === 0) {
                    recentBookingsList.innerHTML = '<div style="font-size:13px; color:#8a857e;">Belum ada peminjaman terbaru.</div>';
                } else {
                    recentBookingsList.innerHTML = '';
                    const recent = [...bookings].reverse().slice(0, 5);
                    recent.forEach(b => {
                        let statusColor = b.status === 'approved' ? '#C6F6D5' : b.status === 'rejected' ? '#FED7D7' : '#FEFCBF';
                        let textColor = b.status === 'approved' ? '#22543D' : b.status === 'rejected' ? '#822727' : '#744210';
                        let statusText = b.status === 'approved' ? 'Disetujui' : b.status === 'rejected' ? 'Ditolak' : 'Menunggu';
                        
                        recentBookingsList.innerHTML += `<div class="list-item">
                            <div class="item-icon" style="background: rgba(27,138,122,0.1); color: #1B8A7A;">
                                <svg style="width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:2" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                            </div>
                            <div class="item-details">
                                <div class="item-title">${b.nama_lab}</div>
                                <div class="item-subtitle">${b.tanggal} | ${b.start_time} - ${b.end_time}</div>
                            </div>
                            <div class="item-action">
                                <span style="background:${statusColor}; color:${textColor}; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:600;">${statusText}</span>
                            </div>
                        </div>`;
                    });
                }
            }
        } catch (e) { console.error('Error updating dashboard:', e); }
    }

    // =============================================
    // MODALS & EDIT FUNCTIONS
    // =============================================
    function closeModals(e) {
        if (e.target.classList.contains('modal-overlay')) {
            e.target.style.display = 'none';
        }
    }

    function openAdminModal() {
        const dd = document.getElementById('profile-dropdown');
        if (dd) dd.style.display = 'none';
        const modal = document.getElementById('admin-modal');
        if (modal) modal.style.display = 'flex';
    }

    function closeAdminModal() {
        const modal = document.getElementById('admin-modal');
        if (modal) modal.style.display = 'none';
    }

    function openProfileModal() {
        const dd = document.getElementById('profile-dropdown');
        if (dd) dd.style.display = 'none';
        const modal = document.getElementById('modal-profile');
        if (modal) modal.style.display = 'flex';
    }

    async function submitPassword(e) {
        e.preventDefault();
        const oldPw = document.getElementById('old-password').value;
        const newPw = document.getElementById('new-password').value;
        try {
            const res = await fetch('/api/profile/password', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ old_password: oldPw, new_password: newPw })
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('modal-profile').style.display = 'none';
                document.getElementById('form-password').reset();
            } else { showToast(data.message, true); }
        } catch (err) { showToast('Gagal update password', true); }
    }

    // --- Edit Booking ---
    async function editBooking(id) {
        const booking = currentBookings.find(b => b.id === id);
        if (!booking) return;

        document.getElementById('edit-book-id').value = booking.id;
        document.getElementById('edit-book-tanggal').value = booking.tanggal;
        document.getElementById('edit-book-start').value = booking.start_time;
        document.getElementById('edit-book-end').value = booking.end_time;
        document.getElementById('edit-book-tujuan').value = booking.tujuan;

        const select = document.getElementById('edit-book-lab');
        if (select) {
            select.innerHTML = '<option value="">Pilih Lab</option>';
            try {
                const res = await fetch('/api/labs');
                const labs = await res.json();
                labs.forEach(lab => {
                    let optColor = lab.status === 'Perbaikan' ? 'color: #d9534f;' : 'color: #10b981;';
                    select.innerHTML += `<option value="${lab.nama_lab}" style="${optColor} font-weight: 500;" ${lab.nama_lab === booking.nama_lab ? 'selected' : ''}>${lab.nama_lab} ${lab.status === 'Perbaikan' ? '(Perbaikan)' : ''}</option>`;
                });
            } catch (e) {}
        }
        document.getElementById('modal-edit-booking').style.display = 'flex';
    }

    async function submitEditBooking(e) {
        e.preventDefault();
        const id = document.getElementById('edit-book-id').value;
        const booking = currentBookings.find(b => b.id == id);

        const payload = {
            nama_lab: document.getElementById('edit-book-lab').value,
            tanggal: document.getElementById('edit-book-tanggal').value,
            start_time: document.getElementById('edit-book-start').value,
            end_time: document.getElementById('edit-book-end').value,
            tujuan: document.getElementById('edit-book-tujuan').value,
            kelas: booking ? booking.kelas : '',
            prodi: booking ? booking.prodi : ''
        };

        try {
            const res = await fetch(`/api/bookings/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('modal-edit-booking').style.display = 'none';
                loadBookings();
                updateDashboard();
            } else { 
                showToast(data.message, true);
                showToast(data.message, true); 
            }
        } catch (err) { showToast('Gagal edit jadwal', true); }
    }

    // --- Edit BHP ---
    async function editBhp(id) {
        const bhp = currentBHP.find(b => b.id === id);
        if (!bhp) return;

        document.getElementById('edit-bhp-id').value = bhp.id;
        document.getElementById('edit-bhp-tanggal').value = bhp.tanggal;
        document.getElementById('edit-bhp-jumlah').value = bhp.jumlah;
        document.getElementById('edit-bhp-praktikum').value = bhp.praktikum;

        const select = document.getElementById('edit-bhp-barang');
        if (select) {
            select.innerHTML = '<option value="">Pilih Barang</option>';
            try {
                const res = await fetch('/api/items');
                const items = await res.json();
                items.forEach(item => {
                    select.innerHTML += `<option value="${item.nama_barang}" ${item.nama_barang === bhp.nama_barang ? 'selected' : ''}>${item.nama_barang} (${item.value})</option>`;
                });
            } catch (e) {}
        }
        document.getElementById('modal-edit-bhp').style.display = 'flex';
    }

    async function submitEditBHP(e) {
        e.preventDefault();
        const id = document.getElementById('edit-bhp-id').value;
        const bhp = currentBHP.find(b => b.id == id);
        const payload = {
            nama_barang: document.getElementById('edit-bhp-barang').value,
            tanggal: document.getElementById('edit-bhp-tanggal').value,
            jumlah: document.getElementById('edit-bhp-jumlah').value,
            praktikum: document.getElementById('edit-bhp-praktikum').value,
            prodi: bhp ? bhp.prodi : currentBhpProdi
        };
        try {
            const res = await fetch(`/api/bhp/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('modal-edit-bhp').style.display = 'none';
                loadBHP();
            } else { showToast(data.message, true); }
        } catch (err) { showToast('Gagal edit BHP', true); }
    }

    // --- Search Filtering ---
    const searchInput = document.querySelector('.search-bar input');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('tbody tr').forEach(row => {
                if (row.closest('.tab-content.active') || row.closest('#home')) {
                    row.style.display = row.innerText.toLowerCase().includes(term) ? '' : 'none';
                }
            });
        });
    }


    // =============================================
    // USER MANAGEMENT
    // =============================================
    let currentUsers = [];
    
    async function loadUsers() {
        if (!isAdmin) return;
        try {
            const res = await fetch('/api/users');
            if (res.ok) {
                currentUsers = await res.json();
                renderUsers();
            }
        } catch (e) {
            console.error('Error loading users:', e);
        }
    }
    
    function renderUsers() {
        const tbody = document.getElementById('table-user-body');
        if (!tbody) return;
        tbody.innerHTML = '';
        currentUsers.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${u.id}</td>
                <td><strong>${u.username}</strong></td>
                <td>
                    <span class="badge" style="background: ${u.is_admin ? '#1B8A7A' : '#e0e0e0'}; color: ${u.is_admin ? '#fff' : '#2A2A2E'}; display:inline-block; padding:4px 8px; border-radius:12px; font-size:11px;">
                        ${u.is_admin ? 'Admin' : 'User'}
                    </span>
                </td>
                <td style="text-align:center;">
                    <div style="display: flex; gap: 6px; justify-content: center;">
                        <button type="button" class="btn-table" onclick="deleteUser(${u.id}, '${u.username}')" style="color:#d9534f; background: rgba(217,83,79,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;" title="Hapus">
                            Hapus
                        </button>
                        <button type="button" class="btn-table" onclick="openEditUserModal(${u.id}, '${u.username}', ${u.is_admin})" style="color:#E2C36B; background: rgba(226,195,107,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;" title="Edit">
                            Edit
                        </button>
                        <button type="button" class="btn-table" onclick="toggleAdminRole(${u.id}, ${u.is_admin}, '${u.username}')" style="color:#1B8A7A; background: rgba(27,138,122,0.1); border:none; padding:6px 12px; border-radius:6px; cursor:pointer; font-weight:600; font-size:12px; transition:all 0.2s;" title="Ubah Role">
                            Role
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    async function submitUser(e) {
        e.preventDefault();
        const username = document.getElementById('add-user-username').value;
        const password = document.getElementById('add-user-password').value;
        const is_admin = document.getElementById('add-user-is-admin').checked;
        
        console.log("Submitting User:", { username, password, is_admin });
        
        try {
            const res = await fetch('/api/users', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, is_admin})
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('form-add-user').reset();
                loadUsers();
                loadMaintenance();
            } else {
                showToast(data.message, true);
            }
        } catch (err) {
            showToast('Gagal menambah pengguna', true);
        }
    }
    
    function deleteUser(id, username) { 
        showCustomConfirm(`Yakin ingin menghapus pengguna '${username}'?`, async () => { 
            try {
                const res = await fetch(`/api/users/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message);
                    loadUsers();
                    loadMaintenance();
                } else {
                    showToast(data.message, true);
                }
            } catch(e) {
                showToast('Gagal menghapus pengguna', true);
            }
        });
    }

    function toggleAdminRole(id, currentIsAdmin, username) { 
        const newRole = !currentIsAdmin; 
        showCustomConfirm(`Ubah role '${username}' menjadi ${newRole ? 'Admin' : 'User biasa'}?`, async () => { 
            try {
                const res = await fetch(`/api/users/${id}`, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({is_admin: newRole})
                });
                const data = await res.json();
                if (data.status === 'success') {
                    showToast(data.message);
                    loadUsers();
                    loadMaintenance();
                } else {
                    showToast(data.message, true);
                }
            } catch(e) {
                showToast('Gagal mengubah role', true);
            }
        });
    }


    function openEditUserModal(id, username, is_admin) {
        document.getElementById('edit-user-id').value = id;
        document.getElementById('edit-user-username').value = username;
        document.getElementById('edit-user-password').value = '';
        document.getElementById('edit-user-is-admin').checked = is_admin ? true : false;
        document.getElementById('modal-edit-user').style.display = 'flex';
    }

    async function submitEditUser(e) {
        e.preventDefault();
        const id = document.getElementById('edit-user-id').value;
        const username = document.getElementById('edit-user-username').value;
        const password = document.getElementById('edit-user-password').value;
        const is_admin = document.getElementById('edit-user-is-admin').checked;
        
        try {
            const res = await fetch(`/api/users/${id}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, is_admin})
            });
            const data = await res.json();
            if (data.status === 'success') {
                showToast(data.message);
                document.getElementById('modal-edit-user').style.display = 'none';
                loadUsers();
            loadMaintenance();
            } else {
                showToast(data.message, true);
            }
        } catch (err) {
            showToast('Gagal mengubah pengguna', true);
        }
    }

function openSopUploadModal() {
    document.getElementById('sop-title').value = '';
    document.getElementById('sop-category').value = 'Prosedur Medis';
    document.getElementById('sop-file').value = '';
    document.getElementById('sop-upload-modal').style.display = 'flex';
}

function closeSopUploadModal() {
    document.getElementById('sop-upload-modal').style.display = 'none';
}




