import pytz
import datetime

from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.views import generic

from coursemanaging.forms import UserRegisterForm, CourseCreateForm, SessionCreateForm
from coursemanaging.session_calendar import SessionCalendar
from coursemanaging.tokens import account_activation_token
from .models import Course, Session, User
from django.contrib.auth import login

utc = pytz.UTC

"""
USER VIEWS
"""


class UserCreateView(generic.CreateView):
    """Register view for user"""
    template_name = 'coursemanaging/user-create.html'
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('coursemanaging:account-activation-sent')

    def get_form_kwargs(self):
        kwargs = super(UserCreateView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class AccountActivationSentView(generic.TemplateView):
    template_name = 'coursemanaging/account-activation-sent.html'


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('coursemanaging:index')
    else:
        return render(request, 'coursemanaging/account-activation-invalid.html')


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
    success_url = reverse_lazy('coursemanaging:index')
    form_class = CourseCreateForm

    def get_form_kwargs(self):
        kwargs = super(CourseCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class CourseDetailView(generic.DetailView):
    """Detail view of a course"""
    template_name = 'coursemanaging/course-detail.html'
    model = Course

    def get_context_data(self, **kwargs):
        context = super(CourseDetailView, self).get_context_data(**kwargs)
        context['is_teacher'] = self.object.teachers.filter(pk=self.request.user.id).exists()
        context['is_student'] = self.object.students.filter(pk=self.request.user.id).exists()
        sessions_subscribed = dict()
        for session in self.object.sessions.all():
            sessions_subscribed[session.id] = session.subscribed_users.filter(id=self.request.user.id).exists()
        context['sessions_subscribed'] = sessions_subscribed
        return context

    def post(self, request, *args, **kwargs):
        join_session = request.POST.get("join_session")
        join_course = request.POST.get("join_course")
        course = get_object_or_404(Course, pk=self.kwargs['pk'])

        if join_course:
            if course.students.filter(pk=request.user.id).exists():
                return redirect('coursemanaging:impossible')
            course.students.add(self.request.user)
            return redirect('coursemanaging:course-detail', pk=course.id)
        if join_session:
            session = get_object_or_404(Session, pk=join_session)
            if session.subscribed_users.filter(pk=request.user.id).exists():
                return redirect('coursemanaging:impossible')
            session.subscribed_users.add(self.request.user)
            return redirect('coursemanaging:course-detail', pk=course.id)


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
    fields = ['course_name', 'course_level', 'build_up_sessions', 'description']
    success_url = reverse_lazy('coursemanaging:index')


class CourseDeleteView(generic.DeleteView):
    """Delete view of a course"""
    template_name = "coursemanaging/course-delete.html"
    model = Course


class CoursesUserListView(generic.ListView):
    template_name = 'coursemanaging/courses-user.html'
    context_object_name = 'courses_teacher'

    def get_context_data(self, **kwargs):
        context = super(CoursesUserListView, self).get_context_data(**kwargs)
        context['courses_student'] = Course.objects.filter(students=self.request.user)
        return context

    def get_queryset(self):
        return Course.objects.filter(teachers=self.request.user)


"""

SESSION VIEWS

"""


class SessionDetailView(generic.DetailView):
    """Detailview for a session"""
    template_name = "coursemanaging/session-detail.html"
    model = Session


class SessionCreateView(generic.CreateView):
    """create view for a Session"""
    template_name = 'coursemanaging/session-create.html'
    model = Session
    success_url = reverse_lazy('coursemanaging:index')
    form_class = SessionCreateForm

    def get_form_kwargs(self):
        kwargs = super(SessionCreateView, self).get_form_kwargs()
        course = get_object_or_404(Course, id=self.kwargs['pk'])
        kwargs.update({'course': course})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('coursemanaging:course-detail', kwargs={'pk': self.kwargs['pk']})


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


class ImpossibleView(generic.TemplateView):
    """View where the user ends when he does something wrong"""
    template_name = "coursemanaging/impossible.html"
