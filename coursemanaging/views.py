import pytz
import datetime

from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views import generic

from coursemanaging.session_calendar import SessionCalendar
from .models import Course, Session

utc = pytz.UTC

"""


COURSE VIEWS


"""


class IndexView(generic.TemplateView):
    """home page of the opengym platform"""
    template_name = 'coursemanaging/index.html'


class CourseCreateView(generic.CreateView):
    """create view for a course"""
    template_name = 'coursemanaging/course-create.html'
    model = Course
    fields = ['course_name', 'course_level', 'single_session_possible', 'description']
    success_url = reverse_lazy('coursemanaging:index')


class CourseDetailView(generic.DetailView):
    """Detail view of a course"""
    template_name = 'coursemanaging/course-detail.html'
    model = Course


class CourseListView(generic.ListView):
    """List view of a course"""
    template_name = 'coursemanaging/course-list.html'
    context_object_name = 'course_list'
    model = Course

    def get_queryset(self):
        return Course.objects.all()


class CourseUpdateView(generic.UpdateView):
    """Update view of a course"""
    template_name = 'coursemanaging/course-update.html'
    model = Course
    fields = ['course_name', 'course_level', 'single_session_possible', 'description']
    success_url = reverse_lazy('coursemanaging:index')


class CourseDeleteView(generic.DeleteView):
    """Delete view of a course"""
    template_name = "coursemanaging/course-delete.html"
    model = Course


"""

SESSION VIEWS

"""


class SessionDetailView(generic.DetailView):
    """Detailview for a session"""
    template_name = "coursemanaging/session-detail.html"
    model = Session


class CalendarView(generic.TemplateView):
    """View that shows a calendar containing all sessions for this month"""
    template_name = "coursemanaging/calendar.html"

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        start_calendar_period = utc.localize(datetime.datetime(2017, 11, 1))
        end_calendar_period = utc.localize(datetime.datetime(2017, 11, 30))

        sessions = Session.objects.filter(start_datetime__lte=end_calendar_period,
                                          start_datetime__gte=start_calendar_period)
        calendar = SessionCalendar(sessions).formatmonth(2017, 11)
        context['calendar'] = mark_safe(calendar)
        return context
