"""
admin.py - Register our models with Django's built-in admin interface
Visit /admin/ after creating superuser to manage data directly
"""

from django.contrib import admin
from .models import UserProfile, Job, Application

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_approved', 'company_name']
    list_filter = ['role', 'is_approved']
    search_fields = ['user__username', 'user__email']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'recruiter', 'status', 'created_at']
    list_filter = ['status', 'job_type']
    search_fields = ['title', 'company']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_at']
    list_filter = ['status']
