import datetime
from django.test import TestCase
import logging
from datetime import timedelta

from coursemanaging.models import Course, Session, User

logger = logging.getLogger(__name__)


class SessionTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(course_name="test_course", course_level=1, build_up_sessions=False,
                                            description="test_description")
        self.session = Session.objects.create(course=self.course, start_datetime=datetime.datetime(2017, 12, 1),
                                              duration=timedelta(hours=4))
        self.user = User.objects.create(email="john", first_name="john", last_name="doe",
                                        birthdate=datetime.datetime(2017, 12, 1), volunteer=True, )

    def test_user_is_subscribed(self):
        self.session.subscribed_users.add(self.user)
        self.assertEquals(self.session.user_is_subscribed(self.user), True)

    def test_user_is_not_subscribed(self):
        self.assertEquals(self.session.user_is_subscribed(self.user), False)



