from datetime import timedelta

from crispy_forms.bootstrap import TabHolder, Tab
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, ButtonHolder, Submit

from coursemanaging.models import User, Course, Session
from coursemanaging.tokens import account_activation_token

Tab.link_template = 'coursemanaging/%s/tab-link.html'
TabHolder.template = 'coursemanaging/%s/tab.html'

timezone.activate(timezone.get_current_timezone())


def validate_subscription_key(value):
    if value != 'opengymopdendraad':
        raise ValidationError(
            '%(value)s is geen correcte registratie sleutel',
            params={'value': value},
        )


class UserRegisterForm(UserCreationForm):
    # subscription_key = forms.CharField(label="Registratiesleutel", validators=[validate_subscription_key],
    # widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'birthdate', 'email', 'password1', 'password2')
        widgets = {
            'birthdate': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(UserRegisterForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
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


class ContactForm(forms.Form):
    first_name = forms.CharField(label='Voornaam', max_length=100, required=False)
    last_name = forms.CharField(label='Familienaam', max_length=100, required=False)
    phone_nr = forms.CharField(label="Telefoon", required=False)
    email = forms.EmailField(label="email")
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div('first_name', 'last_name', css_class='form-left'),
                Div('phone_nr', 'email', css_class='form-right'), css_class='form-top'),
            'message', ButtonHolder(
                Submit('submit', 'Verstuur', css_class='btn btn-lg')
            ))


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
    multiple_sessions = forms.BooleanField(required=False)
    weekly_until = forms.DateTimeField(required=False)

    class Meta:
        model = Session
        fields = ['start', 'duration', 'extra_info', 'max_students_diff_course', 'max_students', 'location_diff_course',
                  'location_short', 'location_number', 'location_city']

        widgets = {
            'start': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'}),
            'weekly_until': forms.DateTimeInput(attrs={'class': 'datepicker', 'autocomplete': 'off'})
        }

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop("course")
        super(SessionCreateForm, self).__init__(*args, **kwargs)
        self.fields['multiple_sessions'].label = "Meerdere sessies aanmaken"
        self.fields['location_diff_course'].label = "Sessie gaat door op een andere locatie dan beschreven in les"
        self.fields['max_students_diff_course'].label = "Ander maximum aantal deelnemers dan beschreven in les"
        self.fields['weekly_until'].label = "Sessies aanmaken tot en met"
        self.fields['duration'].label = "Duur van deze sessie beschreven in uren:minuten:seconden bv 4:30:0"

    def clean(self):
        multiple_sessions = self.cleaned_data['multiple_sessions']
        weekly_until = self.cleaned_data['weekly_until']
        start = self.cleaned_data['start']

        if multiple_sessions and weekly_until is None:
            raise ValidationError(
                'Als je meerdere sessies wil aanmaken dien je aan te geven tot wanneer je er wil aanmaken')
        if multiple_sessions and weekly_until < start + timedelta(days=7):
            raise ValidationError(
                'Als je meerdere seesie wil aanmaken moet de tot-datum minstens een week na de start'
                ' van de eerste sessie liggen'
            )

    def save(self, commit=True):
        session = super(SessionCreateForm, self).save()
        session.start = timezone.localtime(session.start)
        session.course = self.course
        if commit:
            if self.cleaned_data['multiple_sessions']:
                while session.start <= self.cleaned_data['weekly_until']:
                    session.start = timezone.localtime(session.start)
                    session.save()
                    session.id = None
                    session.start += timedelta(days=7)
            else:
                session.save()
        return session
