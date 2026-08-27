from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path('', views.dashboard, name='dashboard'),
    path('login', views.login_view, name='login'),
    path('user-management', views.user_management, name='user_management'),
    path('jadwal', views.schedule, name='schedule'),
    path('riwayat', views.request_history, name='request_history'),
    path('sop-management', views.sop_management, name='sop_management'),
    path('sops', views.sops_view, name='sops_view'),
    path('admin-jadwal', views.admin_schedule, name='admin_schedule'),
    path('request-management', views.request_management, name='request_management'),
    path('pbb', views.pbb_page, name='pbb_page'),
    path('admin-maintenance', views.admin_maintenance, name='admin_maintenance'),

    # Auth
    path('api/login', views.api_login, name='api_login'),
    path('api/logout', views.api_logout, name='api_logout'),

    # APIs
    path('api/labs', views.handle_labs, name='handle_labs'),
    path('api/labs/<int:lab_id>', views.handle_lab_detail, name='handle_lab_detail'),
    path('api/items', views.handle_items, name='handle_items'),
    path('api/items/<int:item_id>', views.handle_item_detail, name='handle_item_detail'),
    path('api/bookings', views.handle_bookings, name='handle_bookings'),
    path('api/bookings/<int:id>/status', views.update_booking_status, name='update_booking_status'),
    path('api/bhp', views.handle_bhp, name='handle_bhp'),
    path('api/bhp/<int:bhp_id>', views.delete_bhp, name='delete_bhp'),
    path('api/sops', views.handle_sops, name='handle_sops'),
    path('api/sops/<int:sop_id>', views.delete_sop, name='delete_sop'),
    path('uploads/sops/<str:filename>', views.serve_sop_file, name='serve_sop_file'),
    path('api/users', views.handle_users, name='handle_users'),
    path('api/users/<int:user_id>', views.handle_user_detail, name='handle_user_detail'),
    path('api/maintenance', views.handle_maintenance, name='handle_maintenance'),
    path('api/maintenance/<int:id>', views.delete_maintenance, name='delete_maintenance'),
    path('api/dashboard/summary', views.dashboard_summary, name='dashboard_summary'),
]
