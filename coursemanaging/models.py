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
    teachers = models.ManyToManyField(User, related_name='courses_teacher', blank=True)
    students = models.ManyToManyField(User, related_name='courses_student', blank=True)
    single_session_possible = models.BooleanField(null=False, blank=False)
    description = models.TextField()

    def __str__(self):
        return self.course_name


class Session(models.Model):
    course = models.ForeignKey(Course, related_name='sessions', default=1, null=True, blank=True)

    subscribed_users = models.ForeignKey(User, related_name='Sessions', null=True, blank=True)
    start_datetime = models.DateTimeField(null=False, blank=False)
    duration = models.DurationField(null=False, blank=False)
    extra_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.course) + ' ' + str(self.start_datetime.date())
