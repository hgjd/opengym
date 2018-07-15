from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic

from mostaardimgur.forms import AlbumForm
from mostaardimgur.models import ImgurAlbum, ImgurSetting, ImgurImage, get_imgur_client


def catchtoken(request):
    if request.user.is_staff:
        ImgurSetting.set_settings_value(ImgurSetting.REFRESH_TOKEN, request.GET['refresh_token'])
        ImgurSetting.set_settings_value(ImgurSetting.USERNAME, request.GET['account_username'])
        ImgurSetting.set_settings_value(ImgurSetting.USERNAME, request.GET['account_id'])
        return HttpResponse('ok', status=200, content_type='text/plain')


class CallBackView(generic.TemplateView):
    template_name = "mostaardimgur/callback.html"


class AlbumDetailView(generic.DetailView):
    model = ImgurAlbum
    context_object_name = 'album'
    template_name = "mostaardimgur/album.html"

    def post(self, request, *args, **kwargs):
        album = self.get_object()
        if self.request.user.is_staff:
            if 'remove' in request.POST:
                image = get_object_or_404(ImgurImage, pk=request.POST['remove'])
                image.delete()
                return redirect(self.get_object().get_absolute_url())
            if 'star' in request.POST:
                album.cover_image = get_object_or_404(ImgurImage, pk=request.POST['star'])
                album.save()
                return redirect('mostaardimgur:album-list')


class AlbumListView(generic.ListView):
    model = ImgurAlbum
    context_object_name = 'albums'
    template_name = "mostaardimgur/albums.html"

    def get_queryset(self):
        return ImgurAlbum.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AlbumListView, self).get_context_data(**kwargs)
        context['images_form'] = AlbumForm()
        context['albums'] = ImgurAlbum.objects.all()
        context['current_page'] = 'album'

        return context

    def post(self, request, *args, **kwargs):
        images_form = AlbumForm(request.POST, request.FILES)

        if self.request.user.is_staff:
            if 'remove' in request.POST:
                album_id = request.POST['remove']
                ImgurAlbum.objects.get(id=album_id).delete()
                return redirect(request.path)
            elif 'star' in request.POST:
                album_id = request.POST['star']
                ImgurSetting.set_settings_value(ImgurSetting.LANDING_ALBUM, album_id)
                return redirect(request.path)
            elif images_form.is_valid():
                images = request.FILES.getlist('images')
                album = ImgurAlbum.objects.create_imgur_album(title=images_form.cleaned_data['album_name'],
                                                              description=images_form.cleaned_data['album_description'])
                for image in images:
                    ImgurImage.objects.create_imgur_image(image, album)
                return redirect('mostaardimgur:album-list')


class AuthorizeRedirectView(generic.RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return get_imgur_client().get_auth_url(response_type='token')
