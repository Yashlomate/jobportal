"""
forms.py - HTML forms for our Job Portal
Forms handle user input, validation, and data saving.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Job, Application


class RegisterForm(UserCreationForm):
    """
    Registration form - extends Django's default form
    which already has: username, password1, password2
    We add: email, first_name, last_name, role, phone
    """
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    role = forms.ChoiceField(choices=[('applicant', 'Applicant'), ('recruiter', 'Recruiter')])
    phone = forms.CharField(max_length=15, required=False)
    company_name = forms.CharField(max_length=100, required=False,
                                   help_text="Only for recruiters")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

    def save(self, commit=True):
        # First save the User object
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Then create the linked UserProfile
            UserProfile.objects.create(
                user=user,
                role=self.cleaned_data['role'],
                phone=self.cleaned_data.get('phone', ''),
                company_name=self.cleaned_data.get('company_name', ''),
            )
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Form to update profile details and upload resume."""
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['phone', 'company_name', 'resume']
        widgets = {
            'resume': forms.FileInput(attrs={'accept': '.pdf,.doc,.docx'})
        }

    def __init__(self, *args, **kwargs):
        # We pass the user object separately to pre-fill name/email fields
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
        if commit:
            profile.save()
        return profile


class JobPostForm(forms.ModelForm):
    """Form for recruiters to post new jobs."""
    class Meta:
        model = Job
        # Recruiter fills these fields; status and recruiter are set in the view
        fields = ['title', 'company', 'location', 'job_type',
                  'description', 'requirements', 'salary', 'last_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'last_date': forms.DateInput(attrs={'type': 'date'}),  # date picker
        }


class ApplicationForm(forms.ModelForm):
    """Form for applicants to apply - just a cover letter."""
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Write a brief message to the recruiter...'
            })
        }


class JobSearchForm(forms.Form):
    """Simple search form on the jobs listing page."""
    keyword = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={'placeholder': 'Job title...'}))
    location = forms.CharField(required=False,
                               widget=forms.TextInput(attrs={'placeholder': 'Location...'}))
    job_type = forms.ChoiceField(required=False, choices=[
        ('', 'All Types'),
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
    ])
