from django.conf.urls import url, include

from . import views

app_name = "coursemanaging"
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^course/register$', views.CourseCreateView.as_view(), name='course-create'),
    url(r'^course/(?P<pk>[0-9]+)/$', views.CourseDetailView.as_view(), name='course-detail'),
    url(r'^courses/$', views.CourseListView.as_view(), name='course-list'),
    url(r'^course/update/(?P<pk>[0-9]+)/$', views.CourseUpdateView.as_view(), name='course-update'),
    url(r'^course/delete/(?P<pk>[0-9]+)/$', views.CourseDeleteView.as_view(), name='course-delete'),
    url(r'^session/(?P<pk>[0-9]+)$', views.SessionDetailView.as_view(), name='session-detail'),
    url(r'^calendar/$', views.CalendarView.as_view(), name='calendar'),
]
