from datetime import date

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
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

    def get_next_session(self):
        if Session.objects.filter(course=self).exists():
            return Session.objects.filter(course=self).order_by('-start_datetime')[0]
        else:
            return None

    def user_is_subscribed(self, user):
        return self.students.filter(id=user.id).exists()

    def user_is_teacher(self, user):
        return self.teachers.filter(id=user.id).exists()


class Session(models.Model):
    course = models.ForeignKey(Course, related_name='sessions', default=1, blank=True)

    subscribed_users = models.ManyToManyField(User, related_name='sessions', blank=True)
    start_datetime = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False)
    extra_info = models.TextField(null=True, blank=True)

    def user_is_subscribed(self, user):
        return self.subscribed_users.filter(id=user.id).exists()

    def __str__(self):
        return str(self.course) + ' ' + str(self.start_datetime.date())


class NewsItem(models.Model):
    text = models.TextField()
    short_text = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=200)
    image = models.ImageField(null=True, blank=True)
    publication_date = models.DateTimeField(default=timezone.now, null=False, blank=False)

    def __str__(self):
        return self.title


class NewsBulletin(models.Model):
    FIRST = 1
    SECOND = 2
    THIRD = 3

    BULLETIN_CHOICES = ((FIRST, '  First'),
                        (SECOND, 'Second'),
                        (THIRD, 'Third'),
                        )

    bulletin_level = models.SmallIntegerField(choices=BULLETIN_CHOICES)
    news_item = models.OneToOneField(NewsItem, null=True, blank=True)

    def clean(self):
        if self.news_item.short_text is None:
            raise ValidationError(
                "news item : %(news_item)s needs to have a short_text in order to become a bulletin",
                code='invalid short_text',
                params={'news_item': self.news_item}
            )

        try:
            self.news_item.url
        except AttributeError:
            raise ValidationError(
                "news item : %(news_item)s needs to have an image in order to become a bulletin",
                code='missing image',
                params={'news_item': self.news_item}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        if NewsBulletin.objects.filter(bulletin_level=self.bulletin_level).exists():
            NewsBulletin.objects.filter(bulletin_level=self.bulletin_level).delete()
        super(NewsBulletin, self).save(*args, **kwargs)

    def __str__(self):
        return self.get_bulletin_level_display()
