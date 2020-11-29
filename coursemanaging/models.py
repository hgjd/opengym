from datetime import date
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext as _
from markdown import markdown


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

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    SEX_CHOICES = (
        ('F', 'Female',),
        ('M', 'Male',),
        ('U', 'Unsure',),
    )

    email = models.EmailField(unique=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    birthdate = models.DateField()
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
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='date joined', null=True)

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
    build_up_sessions = models.BooleanField(default=False)
    max_students_session = models.PositiveSmallIntegerField(null=True, blank=True)
    max_students_course = models.PositiveSmallIntegerField(null=True, blank=True)
    description = models.TextField()
    location_short = models.CharField(max_length=30, null=True, blank=True)
    location_street = models.CharField(max_length=50, null=True, blank=True)
    location_number = models.CharField(max_length=5, null=True, blank=True)
    location_city = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    teachers = models.ManyToManyField(User, related_name='courses_teacher', blank=True)
    students = models.ManyToManyField(User, related_name='courses_student', blank=True)

    def __str__(self):
        return self.course_name

    def is_full(self):
        if self.max_students_course:
            return self.max_students_course <= self.students.count()
        return False

    def get_next_session(self):
        if Session.objects.filter(course=self, start__gte=timezone.now()).exists():
            return Session.objects.filter(course=self, start__gte=timezone.now()).order_by('start')[0]
        else:
            return None

    def get_future_sessions(self):
        return Session.objects.filter(start__gte=timezone.now(), course=self).order_by('start')

    def user_is_subscribed(self, user):
        return self.students.filter(id=user.id).exists()

    def user_is_teacher(self, user):
        return self.teachers.filter(id=user.id).exists()

    def subscribe_user(self, user):
        if self.max_students_course and self.students.count() >= self.max_students_course:
            raise ValidationError(
                "This course is full",
                code='full',
            )
        self.students.add(user)

    def unsubscribe_user(self, user):
        if user not in self.students.all():
            raise ValidationError(
                "User not in session ",
                code='not found',
            )
        self.students.remove(user)

    def clean(self):
        if self.max_students_course and self.students.count() > self.max_students_course:
            raise ValidationError(
                "This course has more students than possible",
                code='full',
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Course, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('coursemanaging:course-detail', args=[self.id])


class Event(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False, default=timedelta())
    facebook_event_url = models.URLField(null=True, blank=True)
    event_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    def get_calendar_url(self):
        return self.get_absolute_url()

    def get_absolute_url(self):
        return reverse_lazy('coursemanaging:event-detail', args=[self.id])

    def get_entry_title(self):
        return self.event_name

    def get_end(self):
        return self.start + self.duration

    def __str__(self):
        return self.event_name


class BuildingDay(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False, default=timedelta())
    description = models.TextField()
    responsible_users = models.ManyToManyField(User, related_name='building_responsibilitites', blank=True)
    subscribed_users = models.ManyToManyField(User, related_name='building_days', blank=True)

    def user_is_subscribed(self, user):
        return self.subscribed_users.filter(id=user.id).exists()

    def subscribe_user(self, user):
        if not self.user_is_subscribed(user):
            self.subscribed_users.add(user)
            self.save()

    def get_absolute_url(self):
        return reverse_lazy('coursemanaging:building-day-detail', args=[self.id])

    def get_end(self):
        return self.start + self.duration

    def __str__(self):
        return 'bouwdag op ' + str(self.start)


class Session(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False, default=timedelta())
    extra_info = models.TextField(null=True, blank=True)
    max_students_diff_course = models.BooleanField(default=False)
    max_students = models.PositiveSmallIntegerField(null=True, blank=True)
    location_diff_course = models.BooleanField(default=False)
    location_short = models.CharField(max_length=30, null=True, blank=True)
    location_street = models.CharField(max_length=50, null=True, blank=True)
    location_number = models.CharField(max_length=5, null=True, blank=True)
    location_city = models.CharField(max_length=50, null=True, blank=True)

    course = models.ForeignKey(Course, related_name='sessions', default=1, blank=True)
    subscribed_users = models.ManyToManyField(User, related_name='sessions', blank=True)

    class Meta:
        ordering = ["start"]

    def extra_info_rendered(self):
        return markdown(self.extra_info)

    def user_is_subscribed(self, user):
        return self.subscribed_users.filter(id=user.id).exists()

    def time_until(self):
        return self.start - timezone.now()

    def subscribe_user(self, user):
        if self.max_students and self.subscribed_users.count() >= self.max_students:
            raise ValidationError(
                "This session is full",
                code='full',
            )
        self.subscribed_users.add(user)

    def unsubscribe_user(self, user):
        if user not in self.subscribed_users.all():
            raise ValidationError(
                "User not in session ",
                code='not found',
            )
        self.subscribed_users.remove(user)

    def get_location_short(self):
        if self.location_diff_course:
            return self.location_short
        else:
            return self.course.location_short

    def get_location_street(self):
        if self.location_diff_course:
            return self.location_street
        else:
            return self.course.location_street

    def get_location_number(self):
        if self.location_diff_course:
            return self.location_number
        else:
            return self.course.location_number

    def get_location_city(self):
        if self.location_diff_course:
            return self.location_city
        else:
            return self.course.location_city

    def get_max_students(self):
        if self.max_students_diff_course:
            return self.max_students
        else:
            return self.course.max_students_session

    def is_full(self):
        if self.max_students_diff_course:
            if self.max_students:
                return self.max_students <= self.subscribed_users.count()
            return False
        else:
            if self.course.max_students_session:
                return self.course.max_students_session <= self.subscribed_users.count()
            return False

    def clean(self):
        if self.max_students and self.subscribed_users.count() > self.max_students:
            raise ValidationError(
                "This session has more students than possible",
                code='full',
            )

    def save(self, *args, **kwargs):
        if not self.max_students_diff_course:
            self.max_students = self.course.max_students_session
        self.full_clean()
        super(Session, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('coursemanaging:session-detail', args=[self.id])

    def get_calendar_url(self):
        return self.course.get_absolute_url()

    def __str__(self):
        return str(self.course) + ' ' + str(self.start.date())


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

        if not self.news_item.image:
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
