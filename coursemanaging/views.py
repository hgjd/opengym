import pytz
import datetime
import calendar

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render, get_object_or_404, render_to_response
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.views import generic

from coursemanaging.forms import UserRegisterForm, CourseCreateForm, SessionCreateForm, UserUpdateForm
from coursemanaging.session_calendar import SessionCalendar
from coursemanaging.tokens import account_activation_token
from .models import Course, Session, User, NewsBulletin, NewsItem
from django.contrib.auth import login

utc = pytz.UTC


class LandingView(generic.TemplateView):
    """home page of the opengym platform"""
    template_name = 'opengym/landing.html'

    def get_context_data(self, **kwargs):
        context = super(LandingView, self).get_context_data(**kwargs)
        today = datetime.datetime.today()
        monthrange = calendar.monthrange(today.year, today.month)
        start_calendar_period = utc.localize(datetime.datetime(today.year, today.month, 1))
        end_calendar_period = utc.localize(
            datetime.datetime(today.year, today.month, monthrange[1], hour=23, minute=59, second=59))

        sessions = Session.objects.filter(start__lte=end_calendar_period,
                                          start__gte=start_calendar_period, course__is_active=True)
        bulletins = NewsBulletin.objects.all().order_by('-bulletin_level')
        cal = SessionCalendar(sessions, self.request.user).formatmonth(today.year, today.month)
        context['calendar'] = mark_safe(cal)
        context['bulletins'] = bulletins
        return context


class NewsView(generic.TemplateView):
    template_name = 'coursemanaging/news.html'

    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        news_items = NewsItem.objects.all().order_by('publication_date')

        if kwargs.get('pk'):
            context['news_item'] = get_object_or_404(NewsItem, pk=kwargs.get('pk'))
        elif news_items:
            context['news_item'] = news_items[0]
        context['current_page'] = 'news'
        context['news_items'] = news_items
        return context

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            news_item = get_object_or_404(NewsItem, pk=request.POST['news_item_id'])
            return render_to_response('coursemanaging/news-item.html', {'news_item': news_item})


"""
USER VIEWS
"""


class RegisterView(generic.CreateView):
    """Register view for user"""
    template_name = 'coursemanaging/user-create.html'
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('coursemanaging:account-activation-sent')

    def get_form_kwargs(self):
        kwargs = super(RegisterView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class UserDetailView(generic.TemplateView):
    template_name = 'coursemanaging/user-detail.html'


class UserUpdateView(generic.UpdateView):
    template_name = 'coursemanaging/user-update.html'
    form_class = UserUpdateForm

    def get_object(self, queryset=None):
        return self.request.user


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
        return redirect('coursemanaging:landing')
    else:
        return render(request, 'coursemanaging/account-activation-invalid.html')


"""
COURSE VIEWS
"""


class IndexView(generic.TemplateView):
    """home page of the opengym platform"""
    template_name = 'coursemanaging/index.html'


class CourseCreateView(UserPassesTestMixin, generic.CreateView):
    """create view for a course"""
    template_name = 'coursemanaging/course-create.html'
    model = Course
    form_class = CourseCreateForm

    def test_func(self):
        return self.request.user.teacher

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('coursemanaging:impossible')

    def get_form_kwargs(self):
        kwargs = super(CourseCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return self.object.get_absolute_url()


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
        remove_session = request.POST.get("remove_session")
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
            session.subscribe_user(self.request.user)
            return redirect('coursemanaging:course-detail', pk=course.id)
        if remove_session:
            if course.teachers.filter(pk=self.request.user.id).exists():
                get_object_or_404(Session, pk=remove_session).delete()
                return redirect('coursemanaging:course-detail', pk=course.id)
            else:
                return redirect('coursemanaging:impossible')


class CourseListView(generic.ListView):
    """List view of a course"""
    template_name = 'coursemanaging/course-list.html'
    context_object_name = 'course_list'
    model = Course

    def get_queryset(self):
        return Course.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        context['current_page'] = 'courses'
        return context


class CourseUpdateView(UserPassesTestMixin, generic.UpdateView):
    def test_func(self):
        return self.request.user.teacher and self.request.user in self.get_object().teachers.all()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('coursemanaging:impossible')

    """Update view of a course"""
    template_name = 'coursemanaging/course-create.html'
    model = Course
    fields = ['course_name', 'course_level', 'build_up_sessions', 'description', 'location_short', 'location_street',
              'location_number', 'location_city']

    def get_success_url(self):
        return self.object.get_absolute_url()


class CoursesUserListView(generic.ListView):
    template_name = 'coursemanaging/courses-user.html'
    context_object_name = 'courses_teacher'

    def get_context_data(self, **kwargs):
        context = super(CoursesUserListView, self).get_context_data(**kwargs)
        context['courses_student'] = Course.objects.filter(students=self.request.user, is_active=True)
        return context

    def get_queryset(self):
        return Course.objects.filter(teachers=self.request.user, is_active=True)


"""

SESSION VIEWS

"""


class SessionCreateView(UserPassesTestMixin, generic.CreateView):
    """create view for a Session"""
    template_name = 'coursemanaging/session-create.html'
    model = Session
    form_class = SessionCreateForm

    def test_func(self):
        course = get_object_or_404(Course, pk=self.kwargs['pk'])
        return self.request.user.teacher and self.request.user in course.teachers.all()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('coursemanaging:impossible')

    def get_form_kwargs(self):
        kwargs = super(SessionCreateView, self).get_form_kwargs()
        course = get_object_or_404(Course, id=self.kwargs['pk'])
        kwargs.update({'course': course})
        return kwargs

    def get_success_url(self):
        return reverse_lazy('coursemanaging:course-detail', kwargs={'pk': self.kwargs['pk']})


class SessionUpdateView(UserPassesTestMixin, generic.UpdateView):
    template_name = 'coursemanaging/session-create.html'
    model = Session
    fields = ['start', 'duration', 'extra_info', 'max_students_diff_course', 'max_students', 'location_diff_course',
              'location_short', 'location_street', 'location_number', 'location_city']

    def test_func(self):
        course = self.get_object().course
        return self.request.user.teacher and self.request.user in course.teachers.all()

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect('coursemanaging:impossible')

    def get_success_url(self):
        return reverse_lazy('coursemanaging:course-detail', kwargs={'pk': self.object.course.id})


class CalendarView(generic.TemplateView):
    template_name = 'coursemanaging/calendar.html'

    def get_context_data(self, **kwargs):
        context = super(CalendarView, self).get_context_data(**kwargs)
        today = datetime.datetime.today()
        monthrange = calendar.monthrange(today.year, today.month)
        start_calendar_period = utc.localize(datetime.datetime(today.year, today.month, 1))
        end_calendar_period = utc.localize(
            datetime.datetime(today.year, today.month, monthrange[1], hour=23, minute=59, second=59))

        sessions = Session.objects.filter(start__lte=end_calendar_period,
                                          start__gte=start_calendar_period, course__is_active=True)
        cal = SessionCalendar(sessions, self.request.user).formatmonth(today.year, today.month)
        context['current_page'] = 'calendar'
        context['calendar'] = mark_safe(cal)
        return context


class AlbumView(generic.TemplateView):
    template_name = 'coursemanaging/album.html'


def get_calendar(request):
    if request.is_ajax():
        month = int(request.GET.get('month'))
        year = int(request.GET.get('year'))
        monthrange = calendar.monthrange(year, month)
        start_calendar_period = utc.localize(datetime.datetime(year, month, 1))
        end_calendar_period = utc.localize(datetime.datetime(year, month, monthrange[1], hour=23, minute=59, second=59))

        sessions = Session.objects.filter(start__lte=end_calendar_period,
                                          start__gte=start_calendar_period, course__is_active=True)

        cal = SessionCalendar(sessions, request.user).formatmonth(year, month)
        return render_to_response('coursemanaging/calendar-ajax.html', {'calendar': mark_safe(cal)})


class ImpossibleView(generic.TemplateView):
    """View where the user ends when he does something wrong"""
    template_name = "coursemanaging/impossible.html"
