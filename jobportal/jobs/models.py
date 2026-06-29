"""
models.py - Database tables for our Job Portal
Each class here = one table in the database

Tables we have:
- UserProfile  : extra info for each user (role, phone etc)
- Job          : job postings by recruiters
- Application  : when applicant applies for a job
"""

from django.db import models
from django.contrib.auth.models import User  # Django's built-in User table


class UserProfile(models.Model):
    """
    Django's default User model has: username, email, password, first_name, last_name
    We extend it with extra fields using OneToOneField (one profile per user).
    """
    ROLE_CHOICES = [
        ('applicant', 'Applicant'),    # job seekers
        ('recruiter', 'Recruiter'),    # companies posting jobs
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # link to User table
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)          # optional phone
    company_name = models.CharField(max_length=100, blank=True)  # for recruiters only
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)  # PDF upload
    is_approved = models.BooleanField(default=False)  # admin must approve accounts

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Job(models.Model):
    """
    Job posting created by a recruiter.
    """
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),   # newly posted, needs admin to approve
        ('approved', 'Approved'),           # visible to applicants
        ('rejected', 'Rejected'),           # admin rejected it
    ]

    recruiter = models.ForeignKey(User, on_delete=models.CASCADE)  # who posted this job
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    description = models.TextField()                # full job description
    requirements = models.TextField()              # what skills are needed
    salary = models.CharField(max_length=100, blank=True)  # e.g. "5-8 LPA"
    last_date = models.DateField()                  # application deadline
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)  # auto set when created

    def __str__(self):
        return f"{self.title} at {self.company}"


class Application(models.Model):
    """
    When an applicant applies for a job, this record is created.
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)        # which job
    applicant = models.ForeignKey(User, on_delete=models.CASCADE) # who applied
    cover_letter = models.TextField(blank=True)    # optional message to recruiter
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)          # when applied

    class Meta:
        # One person can apply to one job only once
        unique_together = ('job', 'applicant')

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"
