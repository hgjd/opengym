from datetime import date

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils.translation import gettext as _


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('birthdate', date.today())
        extra_fields.setdefault('volunteer', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    birthdate = models.DateField()
    volunteer = models.BooleanField()
    teacher = models.BooleanField(default=False)
    email_confirmed = models.BooleanField(default=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    USERNAME_FIELD = 'email'
    objects = MyUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Course(models.Model):
    BEGINNER = 1
    INTERMEDIATE = 2
    ADVANCED = 3

    LEVEL_CHOICES = ((BEGINNER, 'Beginner'),
                     (INTERMEDIATE, 'Intermediate'),
                     (ADVANCED, 'Advanced'),
                     )

    course_name = models.CharField(max_length=100, null=False, blank=False)
    course_level = models.SmallIntegerField(null=False, blank=False, choices=LEVEL_CHOICES)
    teachers = models.ManyToManyField(User, related_name='courses_teacher', blank=True)
    students = models.ManyToManyField(User, related_name='courses_student', blank=True)
    build_up_sessions = models.BooleanField(null=False, blank=False)
    description = models.TextField()

    def __str__(self):
        return self.course_name


class Session(models.Model):
    course = models.ForeignKey(Course, related_name='sessions', default=1, null=True, blank=True)

    subscribed_users = models.ManyToManyField(User, related_name='sessions', null=True, blank=True)
    start_datetime = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False)
    extra_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.course) + ' ' + str(self.start_datetime.date())
