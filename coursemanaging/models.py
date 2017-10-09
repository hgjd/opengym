from django.contrib.auth.models import User
from django.db import models


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
    teachers = models.ManyToManyField(User, related_name='courses_teacher')
    students = models.ManyToManyField(User, related_name='courses_student')
    single_session_possible = models.BooleanField(null=False, blank=False)
    description = models.TextField()


class Session(models.Model):
    subscribed_users = models.ForeignKey(User, related_name='Sessions')
    start_datetime = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False)
    extra_info = models.TextField()
