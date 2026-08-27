import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the start of the dashboard tab and the end (before SOP tab)
start_marker = '<!-- TAB: HOME / DASHBOARD -->\n        <div id="home" class="tab-content active">'
end_marker = '        <!-- TAB: SOP -->'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker)

if start_idx == -1:
    print("start marker not found")
    exit()
if end_idx == -1:
    print("end marker not found")
    exit()

new_dashboard = '''<!-- TAB: HOME / DASHBOARD -->
        <div id="home" class="tab-content active">

            <!-- ====== DASHBOARD HEADER ====== -->
            <div class="dash-topbar">
                <div class="dash-greeting">
                    <div class="greeting-icon">
                        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
                    </div>
                    <div>
                        <h1 class="greeting-title">Halo, {{ username }}! 👋</h1>
                        <p class="greeting-sub">Selamat datang — <span id="current-date">Hari ini</span></p>
                    </div>
                </div>
                <div class="dash-actions">
                    <div class="dash-searchbar">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
                        <input type="text" id="calendar-search" placeholder="Cari peminjaman..." oninput="filterBookings()">
                    </div>
                    <button class="dash-btn-primary" onclick="switchTab('peminjaman')">
                        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        Tambah Peminjaman
                    </button>
                </div>
            </div>

            <!-- ====== STAT CARDS ROW ====== -->
            <div class="stat-cards-row">
                <div class="stat-card stat-card-emerald">
                    <div class="stat-card-icon">
                        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    </div>
                    <div class="stat-card-body">
                        <div class="stat-number" id="total-bookings-count">0</div>
                        <div class="stat-label">Total Peminjaman</div>
                    </div>
                    <div class="stat-card-wave">
                        <svg viewBox="0 0 120 40" preserveAspectRatio="none"><path d="M0 30 Q30 10 60 25 Q90 40 120 15 L120 40 L0 40 Z" fill="rgba(255,255,255,0.12)"/><path d="M0 35 Q30 18 60 30 Q90 42 120 22 L120 40 L0 40 Z" fill="rgba(255,255,255,0.08)"/></svg>
                    </div>
                </div>

                <div class="stat-card stat-card-blue">
                    <div class="stat-card-icon">
                        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
                    </div>
                    <div class="stat-card-body">
                        <div class="stat-number" id="total-labs-count">0</div>
                        <div class="stat-label">Lab Tersedia</div>
                    </div>
                    <div class="stat-card-wave">
                        <svg viewBox="0 0 120 40" preserveAspectRatio="none"><path d="M0 30 Q30 10 60 25 Q90 40 120 15 L120 40 L0 40 Z" fill="rgba(255,255,255,0.12)"/><path d="M0 35 Q30 18 60 30 Q90 42 120 22 L120 40 L0 40 Z" fill="rgba(255,255,255,0.08)"/></svg>
                    </div>
                </div>

                <div class="stat-card stat-card-amber">
                    <div class="stat-card-icon">
                        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                    </div>
                    <div class="stat-card-body">
                        <div class="stat-number" id="count-pending">0</div>
                        <div class="stat-label">Menunggu Konfirmasi</div>
                    </div>
                    <div class="stat-card-wave">
                        <svg viewBox="0 0 120 40" preserveAspectRatio="none"><path d="M0 30 Q30 10 60 25 Q90 40 120 15 L120 40 L0 40 Z" fill="rgba(255,255,255,0.12)"/><path d="M0 35 Q30 18 60 30 Q90 42 120 22 L120 40 L0 40 Z" fill="rgba(255,255,255,0.08)"/></svg>
                    </div>
                </div>

                <div class="stat-card stat-card-red">
                    <div class="stat-card-icon">
                        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    </div>
                    <div class="stat-card-body">
                        <div class="stat-number" id="count-maintenance">0</div>
                        <div class="stat-label">Lab Perbaikan</div>
                    </div>
                    <div class="stat-card-wave">
                        <svg viewBox="0 0 120 40" preserveAspectRatio="none"><path d="M0 30 Q30 10 60 25 Q90 40 120 15 L120 40 L0 40 Z" fill="rgba(255,255,255,0.12)"/><path d="M0 35 Q30 18 60 30 Q90 42 120 22 L120 40 L0 40 Z" fill="rgba(255,255,255,0.08)"/></svg>
                    </div>
                </div>
            </div>

            <!-- ====== MAIN GRID ====== -->
            <div class="dash-main-grid">

                <!-- LEFT COLUMN -->
                <div class="dash-left-col">

                    <!-- Jadwal Hari Ini -->
                    <div class="dash-card">
                        <div class="dash-card-header">
                            <div class="dash-card-title">
                                <span class="dash-card-dot dot-emerald"></span>
                                Jadwal Praktikum Hari Ini
                            </div>
                            <span class="dash-badge-count" id="today-schedule-badge">0</span>
                        </div>
                        <div id="today-schedule-list" class="schedule-list">
                            <div class="dash-empty-state">
                                <svg width="40" height="40" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                                <p>Tidak ada jadwal hari ini.</p>
                            </div>
                        </div>
                    </div>

                    <!-- Donut Utilization + Active Stat -->
                    <div class="dash-card utilization-card">
                        <div class="dash-card-header">
                            <div class="dash-card-title">
                                <span class="dash-card-dot dot-purple"></span>
                                Tingkat Penggunaan Lab
                            </div>
                            <div id="utilization-badge" class="util-badge">Kosong</div>
                        </div>
                        <div class="util-body">
                            <div class="donut-wrap">
                                <svg class="donut-svg" viewBox="0 0 120 120">
                                    <circle cx="60" cy="60" r="50" fill="none" stroke="#f1f5f9" stroke-width="12"/>
                                    <circle id="donut-ring" cx="60" cy="60" r="50" fill="none" stroke="url(#donutGrad)" stroke-width="12" stroke-linecap="round"
                                        stroke-dasharray="314" stroke-dashoffset="314" transform="rotate(-90 60 60)" style="transition: stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)"/>
                                    <defs>
                                        <linearGradient id="donutGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                                            <stop offset="0%" stop-color="#1B8A7A"/>
                                            <stop offset="100%" stop-color="#4EB8A8"/>
                                        </linearGradient>
                                    </defs>
                                    <text x="60" y="56" text-anchor="middle" font-size="18" font-weight="800" fill="#1B8A7A" id="donut-text">0%</text>
                                    <text x="60" y="72" text-anchor="middle" font-size="9" fill="#94a3b8" font-weight="600">TERPAKAI</text>
                                </svg>
                            </div>
                            <div class="util-legend">
                                <div class="util-leg-item">
                                    <div class="util-leg-dot" style="background: linear-gradient(135deg, #1B8A7A, #4EB8A8);"></div>
                                    <span>Lab Aktif</span>
                                    <strong id="count-active" class="util-count">0</strong>
                                </div>
                                <div class="util-leg-item">
                                    <div class="util-leg-dot" style="background: #f59e0b;"></div>
                                    <span>Menunggu</span>
                                    <strong class="util-count">-</strong>
                                </div>
                                <div class="util-leg-item">
                                    <div class="util-leg-dot" style="background: #ef4444;"></div>
                                    <span>Perbaikan</span>
                                    <strong class="util-count">-</strong>
                                </div>
                                <button onclick="switchTab('peminjaman')" class="util-action-btn">
                                    Lihat Semua Jadwal →
                                </button>
                            </div>
                        </div>
                    </div>

                </div>

                <!-- RIGHT COLUMN -->
                <div class="dash-right-col">

                    <!-- Recent Bookings -->
                    <div class="dash-card" style="flex: 1;">
                        <div class="dash-card-header">
                            <div class="dash-card-title">
                                <span class="dash-card-dot dot-blue"></span>
                                Peminjaman Terbaru Anda
                            </div>
                            <button onclick="switchTab('peminjaman')" class="dash-link-btn">Tambah Baru +</button>
                        </div>
                        <div class="list-items" id="active-booking-list" style="display: flex; flex-direction: column; gap: 10px; max-height: 260px; overflow-y: auto;">
                            <div class="dash-empty-state">
                                <svg width="36" height="36" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
                                <p>Belum ada peminjaman.</p>
                            </div>
                        </div>
                        <span id="active-bookings-badge" style="display:none;"></span>
                    </div>

                    <!-- BHP Log -->
                    <div class="dash-card" style="flex: 1;">
                        <div class="dash-card-header">
                            <div class="dash-card-title">
                                <span class="dash-card-dot dot-amber"></span>
                                Log BHP Terbaru
                            </div>
                            <button onclick="switchTab('bhp')" class="dash-link-btn">Lihat Semua</button>
                        </div>
                        <div class="dash-table-wrap">
                            <table class="dash-table">
                                <thead>
                                    <tr>
                                        <th>Tanggal</th>
                                        <th>Laboratorium</th>
                                        <th>Barang</th>
                                        <th style="text-align: right;">Jml</th>
                                    </tr>
                                </thead>
                                <tbody id="dashboard-bhp-list">
                                    <tr><td colspan="4" class="dash-td-empty">Belum ada log BHP.</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>

                </div>

            </div>

        </div>

        '''

html = html[:start_idx] + new_dashboard + html[end_idx:]

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Dashboard HTML replaced!')
