from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required


from . import views

app_name = "coursemanaging"
urlpatterns = [
    url(r'^$', views.IndexView.as_view(),
        name='index'),
    url(r'^course/register$', login_required(views.CourseCreateView.as_view()),
        name='course-create'),
    url(r'^course/(?P<pk>[0-9]+)/$', login_required(views.CourseDetailView.as_view()),
        name='course-detail'),
    url(r'^courses/$', views.CourseListView.as_view(),
        name='course-list'),
    url(r'^course/update/(?P<pk>[0-9]+)/$', login_required(views.CourseUpdateView.as_view()),
        name='course-update'),
    url(r'^courses$', login_required(views.CoursesUserListView.as_view()),
        name='courses-user'),
    url(r'^course/(?P<pk>[0-9]+)/session-create$', login_required(views.SessionCreateView.as_view()),
        name='session-create'),
    url(r'^session/(?P<pk>[0-9]+)/session-update$', login_required(views.SessionUpdateView.as_view()),
        name='session-update'),
    url(r'^register/$', views.UserCreateView.as_view(),
        name='user-register'),
    url(r'^user/$', login_required(views.UserDetailView.as_view()),
        name='user-detail'),
    url(r'^user-update/$', login_required(views.UserUpdateView.as_view()),
        name='user-update'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='user-activate'),
    url(r'^login/$', auth_views.login, {'template_name': 'coursemanaging/user-login.html'},
        name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'},
        name='logout'),
    url('^account-activation-sent', views.AccountActivationSentView.as_view(),
        name='account-activation-sent'),

    url(r'^landing/', views.LandingView.as_view(),
        name='landing'),
    url(r'^calendar/', views.CalendarView.as_view(),
        name='calendar'),
    url(r'^album/', views.AlbumView.as_view(),
        name='album'),
    url(r'^news/$', views.NewsView.as_view(),
        name='news'),
    url(r'^news/(?P<pk>[0-9]+)$', views.NewsView.as_view(),
        name='news'),

    url(r'^impossible/$', views.ImpossibleView.as_view(),
        name='impossible'),

    url(r'^ajax-calendar/$', views.get_calendar,
        name='ajax-calendar'),
]
