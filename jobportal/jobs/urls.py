"""
urls.py - Maps URLs to view functions
Format: path('url/', view_function, name='url_name')
The 'name' lets us use {% url 'name' %} in templates
"""

from django.urls import path
from . import views

urlpatterns = [
    # Public pages (no login needed)
    path('', views.home_view, name='home'),
    path('jobs/', views.job_list_view, name='job_list'),
    path('jobs/<int:job_id>/', views.job_detail_view, name='job_detail'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Logged-in users
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    # Recruiter: job management
    path('jobs/post/', views.post_job_view, name='post_job'),
    path('jobs/<int:job_id>/edit/', views.edit_job_view, name='edit_job'),
    path('jobs/<int:job_id>/delete/', views.delete_job_view, name='delete_job'),
    path('jobs/<int:job_id>/applications/', views.view_applications_view, name='view_applications'),
    path('applications/<int:app_id>/update/', views.update_application_status_view, name='update_application'),

    # Applicant: apply for jobs
    path('jobs/<int:job_id>/apply/', views.apply_job_view, name='apply_job'),

    # Admin: approve users and jobs
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/users/<int:user_id>/approve/', views.approve_user_view, name='approve_user'),
    path('admin-panel/users/<int:user_id>/reject/', views.reject_user_view, name='reject_user'),
    path('admin-panel/jobs/', views.admin_jobs_view, name='admin_jobs'),
    path('admin-panel/jobs/<int:job_id>/approve/', views.approve_job_view, name='approve_job'),
    path('admin-panel/jobs/<int:job_id>/reject/', views.reject_job_view, name='reject_job'),
]
