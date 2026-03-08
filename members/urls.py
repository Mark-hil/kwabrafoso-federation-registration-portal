# members/urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .views import member_list, add_member, login_view, signup_view, logout_view, admin_signup
from . import views, admin_views

# URL patterns that require login
urlpatterns = [
    path('my_members/', login_required(views.my_members), name='my_members'),
    path('room_division_stats/', login_required(views.room_and_division_stats), name='room_division_stats'),
    path('user_dashboard/', login_required(views.user_dashboard), name='user_dashboard'),
    path('member_list/', login_required(member_list), name='member_list'),  
    path('add/', login_required(add_member), name='add_member'),
    path('edit/<int:pk>/', login_required(views.edit_member), name='edit_member'),
    path('delete/<int:pk>/', login_required(views.delete_member), name='delete_member'),
    path('export/csv/', login_required(views.export_members_csv), name='export_members_csv'),
    path('track_attendance/', login_required(views.track_attendance), name='track_attendance'), 
    path('attendance_report/', login_required(views.attendance_report), name='attendance_report'),
    path('scanner/', login_required(views.scanner), name='scanner'),
    path('set-attendance-type/', login_required(views.set_attendance_type), name='set_attendance_type'),
    path('scan-attendance/', login_required(views.mark_attendance), name='mark_attendance'),
    path('attendance-report/export/', login_required(views.export_attendance_report), name='export_attendance_report'),
    path('print_badges/', login_required(views.print_badges), name='print_badges'),
    path('qr-code/<int:member_id>/', login_required(views.view_qr_code), name='view_qr_code'),
    path('add-visitor/', login_required(views.add_visitor), name='add_visitor'),
    path('visitors/', login_required(views.visitor_list), name='visitor_list'),
    path('follow-up/<int:pk>/', login_required(views.follow_up_visitor), name='follow_up_visitor'),
    path('admin_dashboard/', login_required(views.dashboard), name='admin_dashboard'),
    path('', login_required(views.smart_dashboard), name='smart_dashboard'), # Smart redirect based on user role
    
    # Admin Configuration URLs
    path('config/system/', login_required(admin_views.system_configuration), name='system_configuration'),
    path('config/room-overrides/', login_required(admin_views.room_overrides), name='room_overrides'),
    path('config/room-overrides/<int:pk>/delete/', login_required(admin_views.delete_room_override), name='delete_room_override'),
    path('config/division-overrides/', login_required(admin_views.division_overrides), name='division_overrides'),
    path('config/division-overrides/<int:pk>/delete/', login_required(admin_views.delete_division_override), name='delete_division_override'),
    path('config/unit-overrides/', login_required(admin_views.unit_overrides), name='unit_overrides'),
    path('config/unit-overrides/<int:pk>/delete/', login_required(admin_views.delete_unit_override), name='delete_unit_override'),
    path('config/manual-assignment/', login_required(admin_views.manual_assignment), name='manual_assignment'),
    path('config/bulk-reassignment/', login_required(admin_views.bulk_reassignment), name='bulk_reassignment'),
    
    # Authentication URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_view, name='signup'),
    path('create-admin/', views.admin_signup, name='admin_signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-activation/', views.resend_activation_email, name='resend_activation'),
    
    # Password reset URLs
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url=reverse_lazy('password_reset_done')
         ), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]
