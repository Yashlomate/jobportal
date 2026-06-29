# JobPortal - Django Project

A simple job portal built with Django + SQLite for resume/internship purposes.

## Features
- Recruiter & Applicant accounts
- Resume upload (PDF/DOC)
- Job posting by recruiters
- Job applications by applicants
- Search jobs by keyword, location, type
- Admin approval for users and jobs

## How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create admin account
```bash
python manage.py createsuperuser
```
Enter: username, email, password when prompted.

### 4. Run the server
```bash
python manage.py runserver
```

### 5. Open in browser
```
http://127.0.0.1:8000/
```

## How to Use

### As Admin:
- Login at /login/ with your superuser credentials
- Go to Dashboard -> Manage Users to approve registrations
- Go to Dashboard -> Approve Jobs to approve job postings
- Or use /admin/ for full Django admin access

### As Recruiter:
1. Register at /register/ (select Recruiter)
2. Wait for admin approval (admin must approve your account)
3. Login -> Dashboard -> Post New Job
4. View applications for your jobs

### As Applicant:
1. Register at /register/ (select Applicant)
2. Wait for admin approval
3. Login -> Profile -> Upload your resume
4. Browse Jobs -> Apply

## Project Structure
```
jobportal/
├── manage.py              <- Run commands from here
├── requirements.txt       <- Install these packages
├── db.sqlite3             <- Auto-created database file
├── media/                 <- Uploaded resumes saved here
│   └── resumes/
├── jobportal/             <- Project config folder
│   ├── settings.py        <- All settings
│   ├── urls.py            <- Main URL routing
│   └── wsgi.py
└── jobs/                  <- Main app folder
    ├── models.py          <- Database tables
    ├── views.py           <- All page logic
    ├── urls.py            <- App URL routing
    ├── forms.py           <- HTML form definitions
    ├── admin.py           <- Django admin setup
    └── templates/
        └── jobs/          <- All HTML files
            ├── base.html
            ├── home.html
            ├── login.html
            ├── register.html
            ├── profile.html
            ├── job_list.html
            ├── job_detail.html
            ├── post_job.html
            ├── apply_job.html
            ├── applications.html
            ├── dashboard_applicant.html
            ├── dashboard_recruiter.html
            ├── dashboard_admin.html
            ├── admin_users.html
            └── admin_jobs.html
```

## Tech Stack
- **Backend:** Python 3, Django 4.2
- **Database:** SQLite (built-in, no setup needed)
- **Frontend:** HTML, Bootstrap 5 (via CDN)
- **File Storage:** Local filesystem (media/ folder)
