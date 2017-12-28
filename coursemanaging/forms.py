from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from coursemanaging.models import User, Course, Session
from coursemanaging.tokens import account_activation_token


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'birthdate', 'email', 'password1', 'password2', 'volunteer')
        widgets = {
            'password': forms.PasswordInput,
            'birthdate': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),

        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UserRegisterForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        # user.set_password(self.cleaned_data["password"])
        if commit:
            user.is_active = False
            user.save()
            current_site = get_current_site(self.request)
            subject = 'Activate Your Open Gym Account'
            message = render_to_string('coursemanaging/account-activation-email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
        return user


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = {'course_name', 'course_level', 'build_up_sessions', 'description'}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(CourseCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        course = super(CourseCreateForm, self).save()
        course.teachers.add(self.user)
        if commit:
            course.save()
        return course


class SessionCreateForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = {'start_datetime', 'duration', 'extra_info'}

        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course")
        super(SessionCreateForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        session = super(SessionCreateForm, self).save()
        session.course = self.course
        if commit:
            session.save()
        return session

