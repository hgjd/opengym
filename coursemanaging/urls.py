from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = "coursemanaging"
urlpatterns = [
    url(r'^$', views.IndexView.as_view(),
        name='index'),
    url(r'^course/register$', views.CourseCreateView.as_view(),
        name='course-create'),
    url(r'^course/(?P<pk>[0-9]+)/$', views.CourseDetailView.as_view(),
        name='course-detail'),
    url(r'^courses/$', views.CourseListView.as_view(),
        name='course-list'),
    url(r'^course/update/(?P<pk>[0-9]+)/$', views.CourseUpdateView.as_view(),
        name='course-update'),
    url(r'^course/delete/(?P<pk>[0-9]+)/$', views.CourseDeleteView.as_view(),
        name='course-delete'),
    url(r'^courses$', views.CoursesUserListView.as_view(),
        name='courses-user'),
    url(r'^session/(?P<pk>[0-9]+)$', views.SessionDetailView.as_view(),
        name='session-detail'),
    url(r'^register/$', views.UserCreateView.as_view(),
        name='user-register'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
        name='user-activate'),
    url(r'^login/$', auth_views.login, {'template_name': 'coursemanaging/user-login.html'},
        name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'},
        name='logout'),
    url('^account-activation-sent', views.AccountActivationSentView.as_view(),
        name='account-activation-sent'),
    url(r'^calendar/$', views.CalendarView.as_view(),
        name='calendar'),
]
