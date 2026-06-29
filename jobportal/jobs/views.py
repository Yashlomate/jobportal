"""
views.py - All the logic for handling requests
Each function = one page/action in our website

Flow:
  User visits URL -> urls.py routes to a view function -> view returns HTML page
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q  # for search with OR conditions
from .models import UserProfile, Job, Application
from .forms import RegisterForm, ProfileUpdateForm, JobPostForm, ApplicationForm, JobSearchForm


# ─────────────────────────────────────────────
#  Helper: get user's profile safely
# ─────────────────────────────────────────────

def get_profile(user):
    """Returns UserProfile or None. Avoids crash if profile missing."""
    try:
        return user.userprofile
    except UserProfile.DoesNotExist:
        return None


# ─────────────────────────────────────────────
#  Auth Views: Register, Login, Logout
# ─────────────────────────────────────────────

def register_view(request):
    """
    GET  -> show blank registration form
    POST -> validate form, save user, redirect to login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created! Wait for admin approval before logging in.')
            return redirect('login')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'jobs/register.html', {'form': form})


def login_view(request):
    """Simple login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            profile = get_profile(user)
            # Admin users can always login
            if user.is_superuser or (profile and profile.is_approved):
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is pending admin approval.')
        else:
            messages.error(request, 'Wrong username or password.')

    return render(request, 'jobs/login.html')


def logout_view(request):
    """Log out and go to homepage."""
    logout(request)
    return redirect('home')


# ─────────────────────────────────────────────
#  Home & Dashboard
# ─────────────────────────────────────────────

def home_view(request):
    """Homepage - shows some stats and recent jobs."""
    recent_jobs = Job.objects.filter(status='approved').order_by('-created_at')[:6]
    total_jobs = Job.objects.filter(status='approved').count()
    total_users = User.objects.filter(is_superuser=False).count()
    return render(request, 'jobs/home.html', {
        'recent_jobs': recent_jobs,
        'total_jobs': total_jobs,
        'total_users': total_users,
    })


@login_required
def dashboard_view(request):
    """
    Smart dashboard - shows different content based on user role.
    Applicant sees: recent applications, job count
    Recruiter sees: their posted jobs, application count
    Admin sees: everything pending approval
    """
    profile = get_profile(request.user)

    if request.user.is_superuser:
        # Admin dashboard
        pending_users = UserProfile.objects.filter(is_approved=False).count()
        pending_jobs = Job.objects.filter(status='pending').count()
        return render(request, 'jobs/dashboard_admin.html', {
            'pending_users': pending_users,
            'pending_jobs': pending_jobs,
        })

    if profile and profile.role == 'recruiter':
        # Recruiter dashboard
        my_jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
        total_applications = Application.objects.filter(job__recruiter=request.user).count()
        return render(request, 'jobs/dashboard_recruiter.html', {
            'my_jobs': my_jobs,
            'total_applications': total_applications,
        })

    # Applicant dashboard
    my_applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')
    return render(request, 'jobs/dashboard_applicant.html', {
        'my_applications': my_applications,
        'profile': profile,
    })


# ─────────────────────────────────────────────
#  Profile
# ─────────────────────────────────────────────

@login_required
def profile_view(request):
    """View and update user profile + resume upload."""
    profile = get_profile(request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'jobs/profile.html', {'form': form, 'profile': profile})


# ─────────────────────────────────────────────
#  Jobs - Listing & Search
# ─────────────────────────────────────────────

def job_list_view(request):
    """
    Show all approved jobs.
    Also handles search by keyword, location, and job type.
    """
    jobs = Job.objects.filter(status='approved').order_by('-created_at')
    form = JobSearchForm(request.GET)  # GET because search params are in URL

    if form.is_valid():
        keyword = form.cleaned_data.get('keyword')
        location = form.cleaned_data.get('location')
        job_type = form.cleaned_data.get('job_type')

        if keyword:
            # Q objects let us do OR search across multiple fields
            jobs = jobs.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(company__icontains=keyword)
            )
        if location:
            jobs = jobs.filter(location__icontains=location)
        if job_type:
            jobs = jobs.filter(job_type=job_type)

    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'form': form})


def job_detail_view(request, job_id):
    """Show full details of one job."""
    job = get_object_or_404(Job, id=job_id, status='approved')
    already_applied = False

    if request.user.is_authenticated:
        already_applied = Application.objects.filter(
            job=job, applicant=request.user
        ).exists()

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'already_applied': already_applied,
    })


# ─────────────────────────────────────────────
#  Job Posting (Recruiter Only)
# ─────────────────────────────────────────────

@login_required
def post_job_view(request):
    """Recruiter posts a new job. Needs admin approval before visible."""
    profile = get_profile(request.user)

    # Only recruiters can post jobs
    if not profile or profile.role != 'recruiter':
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user  # set who posted it
            job.status = 'pending'        # needs admin approval
            job.save()
            messages.success(request, 'Job posted! It will be visible after admin approval.')
            return redirect('dashboard')
    else:
        form = JobPostForm()

    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def edit_job_view(request, job_id):
    """Recruiter edits their own job posting."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            job.status = 'pending'  # re-submit for approval after edit
            job.save()
            messages.success(request, 'Job updated! Pending approval again.')
            return redirect('dashboard')
    else:
        form = JobPostForm(instance=job)

    return render(request, 'jobs/post_job.html', {'form': form, 'edit': True})


@login_required
def delete_job_view(request, job_id):
    """Recruiter deletes their job posting."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted.')
    return redirect('dashboard')


# ─────────────────────────────────────────────
#  Applications
# ─────────────────────────────────────────────

@login_required
def apply_job_view(request, job_id):
    """Applicant applies for a job."""
    job = get_object_or_404(Job, id=job_id, status='approved')
    profile = get_profile(request.user)

    # Only applicants can apply
    if not profile or profile.role != 'applicant':
        messages.error(request, 'Only applicants can apply for jobs.')
        return redirect('job_detail', job_id=job_id)

    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You already applied for this job.')
        return redirect('job_detail', job_id=job_id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('dashboard')
    else:
        form = ApplicationForm()

    return render(request, 'jobs/apply_job.html', {'job': job, 'form': form})


@login_required
def view_applications_view(request, job_id):
    """Recruiter views all applications for their job."""
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    applications = Application.objects.filter(job=job).select_related('applicant__userprofile')
    return render(request, 'jobs/applications.html', {'job': job, 'applications': applications})


@login_required
def update_application_status_view(request, app_id):
    """Recruiter changes status of application (shortlist/reject etc)."""
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    new_status = request.POST.get('status')
    valid_statuses = ['applied', 'reviewed', 'shortlisted', 'rejected']

    if new_status in valid_statuses:
        application.status = new_status
        application.save()
        messages.success(request, f'Application marked as {new_status}.')
    return redirect('view_applications', job_id=application.job.id)


# ─────────────────────────────────────────────
#  Admin Views
# ─────────────────────────────────────────────

@login_required
def admin_users_view(request):
    """Admin approves/rejects user registrations."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    profiles = UserProfile.objects.select_related('user').all()
    return render(request, 'jobs/admin_users.html', {'profiles': profiles})


@login_required
def approve_user_view(request, user_id):
    """Admin approves a user."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    profile = get_object_or_404(UserProfile, user_id=user_id)
    profile.is_approved = True
    profile.save()
    messages.success(request, f'{profile.user.username} approved!')
    return redirect('admin_users')


@login_required
def reject_user_view(request, user_id):
    """Admin rejects (deletes) a user."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'User removed.')
    return redirect('admin_users')


@login_required
def admin_jobs_view(request):
    """Admin sees all pending jobs."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    pending_jobs = Job.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'jobs/admin_jobs.html', {'jobs': pending_jobs})


@login_required
def approve_job_view(request, job_id):
    """Admin approves a job - it becomes visible to applicants."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    job = get_object_or_404(Job, id=job_id)
    job.status = 'approved'
    job.save()
    messages.success(request, f'Job "{job.title}" approved!')
    return redirect('admin_jobs')


@login_required
def reject_job_view(request, job_id):
    """Admin rejects a job."""
    if not request.user.is_superuser:
        return redirect('dashboard')

    job = get_object_or_404(Job, id=job_id)
    job.status = 'rejected'
    job.save()
    messages.success(request, f'Job "{job.title}" rejected.')
    return redirect('admin_jobs')
