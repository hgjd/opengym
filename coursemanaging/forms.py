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


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class UserUpdateForm(forms.ModelForm):
    nameform = NameForm()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'birthdate', 'volunteer']
        widgets = {
            'birthdate': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),

        }


class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_level', 'build_up_sessions', 'description', 'location_short',
                  'location_street', 'location_number', 'location_city']

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
        fields = ['start', 'duration', 'extra_info', 'max_students_diff_course', 'max_students', 'location_diff_course',
                  'location_short', 'location_number', 'location_city']

        widgets = {
            'start': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course")
        super(SessionCreateForm, self).__init__(*args, **kwargs)
        labels = {
            'max_students_diff_course': _('Writer'),
        }
        help_texts = {
            'name': _('Some useful help text.'),
        }

    def save(self, commit=True):
        session = super(SessionCreateForm, self).save()
        session.course = self.course
        if commit:
            session.save()
        return session
