import pytz
import datetime

from django.utils.safestring import mark_safe
from django.views import generic

from coursemanaging.models import Session
from coursemanaging.session_calendar import SessionCalendar

utc = pytz.UTC


class LandingView(generic.TemplateView):
    """home page of the opengym platform"""
    template_name = 'opengym/landing.html'

    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)
        start_calendar_period = utc.localize(datetime.datetime(2017, 11, 1))
        end_calendar_period = utc.localize(datetime.datetime(2017, 11, 30))

        sessions = Session.objects.filter(start_datetime__lte=end_calendar_period,
                                          start_datetime__gte=start_calendar_period)
        calendar = SessionCalendar(sessions).formatmonth(2017, 11)
        context['calendar'] = mark_safe(calendar)
        return context
