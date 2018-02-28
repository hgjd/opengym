import datetime
import pytz
from django.core.exceptions import ValidationError

from django.test import TestCase
import logging

from coursemanaging.models import Course, User

logger = logging.getLogger(__name__)
utc = pytz.utc


class CourseTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(course_name="test_course", course_level=1, build_up_sessions=False,
                                            description="test_description")

        self.user = User.objects.create(email="john", first_name="john", last_name="doe",
                                        birthdate=utc.localize(datetime.datetime(2017, 12, 1)), volunteer=True, )

    def test_user_is_subscribed(self):
        self.course.students.add(self.user)
        self.assertEquals(self.course.user_is_subscribed(self.user), True)

    def test_user_is_not_subscribed(self):
        self.assertEquals(self.course.user_is_subscribed(self.user), False)

    def test_course_full(self):
        self.course.max_students_course = 3
        user_a = User.objects.create(email="jub", first_name="john", last_name="doe",
                                     birthdate=utc.localize(datetime.datetime(2017, 12, 1)), volunteer=True)
        user_b = User.objects.create(email="jab", first_name="john", last_name="doe",
                                     birthdate=utc.localize(datetime.datetime(2017, 12, 1)), volunteer=True)
        user_c = User.objects.create(email="job", first_name="john", last_name="doe",
                                     birthdate=utc.localize(datetime.datetime(2017, 12, 1)), volunteer=True)
        self.course.subscribe_user(user_a)
        self.course.subscribe_user(user_b)
        self.course.subscribe_user(user_c)

        with self.assertRaises(ValidationError) as error:
            self.course.subscribe_user(self.user)
        self.assertEqual(error.exception.messages[0],
                         "This course is full")
