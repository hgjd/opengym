import datetime
import pytz

from django.core.exceptions import ValidationError
from django.test import TestCase
import logging
from datetime import timedelta

from coursemanaging.models import Course, Session, User

logger = logging.getLogger(__name__)
utc = pytz.UTC


class SessionTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(course_name="test_course", course_level=1, build_up_sessions=False,
                                            description="test_description")
        self.session = Session.objects.create(course=self.course,
                                              start=utc.localize(datetime.datetime(2017, 12, 1)),
                                              duration=timedelta(hours=4))
        self.user = User.objects.create(email="john", first_name="john", last_name="doe",
                                        birthdate=utc.localize(datetime.datetime(2017, 12, 1)))

    def test_user_is_subscribed(self):
        self.session.subscribed_users.add(self.user)
        self.assertEquals(self.session.user_is_subscribed(self.user), True)

    def test_user_is_not_subscribed(self):
        self.assertEquals(self.session.user_is_subscribed(self.user), False)

    def test_subscribe_user_full(self):
        self.session.max_students = 3
        user_a = User.objects.create(email="jub", first_name="john", last_name="doe",
                                     birthdate=utc.localize(datetime.datetime(2017, 12, 1)))
        user_b = User.objects.create(email="jab", first_name="john", last_name="doe",
                                     birthdate=utc.localize(datetime.datetime(2017, 12, 1)))
        user_c = User.objects.create(email="job", first_name="john", last_name="doe",
                                     birthdate=utc.localize(datetime.datetime(2017, 12, 1)))
        self.session.subscribe_user(user_a)
        self.session.subscribe_user(user_b)
        self.session.subscribe_user(user_c)

        with self.assertRaises(ValidationError) as error:
            self.session.subscribe_user(self.user)
        self.assertEqual(error.exception.messages[0],
                         "This session is full")
