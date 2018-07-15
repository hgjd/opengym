from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views

app_name = "mostaardimgur"

urlpatterns = [
    url(r'^callback', views.CallBackView.as_view()),
    url(r'^catchtoken/$', views.catchtoken,
        name='catchtoken'),
    url(r'^albums/(?P<pk>[0-9]+)$', views.AlbumDetailView.as_view(),
        name='album-detail'),
    url(r'^albums/$', views.AlbumListView.as_view(),
        name='album-list'),
    url(r'^imgur-authorize/$', login_required(views.AuthorizeRedirectView.as_view()),
        name="authorize"),


]
