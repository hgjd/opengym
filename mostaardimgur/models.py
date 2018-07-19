import base64

from django.db import models
from django.urls import reverse_lazy
from imgurpython import ImgurClient


class ImgurSetting(models.Model):
    LANDING_ALBUM = 1
    CLIENT_ID = 2
    CLIENT_SECRET = 3
    REFRESH_TOKEN = 4
    USERNAME = 5
    ACCOUNT_ID = 6

    SETTINGS = (
        (LANDING_ALBUM, 'landing album id'), (CLIENT_ID, 'client id'), (CLIENT_SECRET, 'client secret'),
        (REFRESH_TOKEN, 'refresh token'), (USERNAME, 'username'), (ACCOUNT_ID, 'accountid'))

    setting = models.SmallIntegerField(choices=SETTINGS, unique=True)
    value = models.CharField(max_length=50)

    @classmethod
    def get_settings_value(cls, setting):
        if cls.objects.filter(setting=setting).exists():
            return cls.objects.get(setting=setting).value
        return None

    @classmethod
    def set_settings_value(cls, setting, value):
        if cls.objects.filter(setting=setting).exists():
            cls.objects.get(setting=setting).value = value
        else:
            cls.objects.create(setting=setting, value=value)


class ImgurAlbumManager(models.Manager):

    def create_imgur_album(self, title, description):
        client = get_imgur_client()
        fields = {
            'title': title,
            'description': description,
            'privacy': 'hidden'
        }
        response = client.create_album(fields)
        imgur_album_id = response['id']
        return ImgurAlbum.objects.create(imgur_id=imgur_album_id, title=title, description=description)

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            return None


class ImgurAlbum(models.Model):
    imgur_id = models.CharField(max_length=10)
    cover_image = models.ForeignKey('ImgurImage', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    is_favourite = models.BooleanField(default=False)

    objects = ImgurAlbumManager()

    def __init__(self, *args, **kwargs):
        super(ImgurAlbum, self).__init__(*args, **kwargs)
        self.__original_cover_image = self.cover_image

    def get_absolute_url(self):
        return reverse_lazy('mostaardimgur:album-detail', args=[self.id])

    def delete(self, using=None, keep_parents=False):
        get_imgur_client().make_request('DELETE', 'album/%s' % self.imgur_id)
        return super(ImgurAlbum, self).delete(using, keep_parents)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.cover_image != self.__original_cover_image:
            data = {
                'cover': self.cover_image.imgur_id,
            }
            get_imgur_client().make_request('POST', 'album/%s' % self.imgur_id, data=data)
        return super(ImgurAlbum, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                            update_fields=update_fields)


class ImgurImageManager(models.Manager):

    def create_imgur_image(self, image, album):
        base64_image = base64.b64encode(image.file.read())
        data = {
            'image': base64_image,
            'type': 'base64',
            'album': album.imgur_id
        }
        image = get_imgur_client().make_request('POST', 'upload', data)
        url = image['link'].rsplit('.', 1)
        thumbs_url = url[0] + 'm.' + url[1]
        return ImgurImage.objects.create(imgur_id=image['id'], thumbs_url=thumbs_url, image_url=image['link'],
                                         imgur_album=album)


class ImgurImage(models.Model):
    imgur_id = models.CharField(max_length=10)
    thumbs_url = models.URLField()
    image_url = models.URLField()
    imgur_album = models.ForeignKey(ImgurAlbum, on_delete=models.CASCADE, related_name='images')

    objects = ImgurImageManager()

    def delete(self, using=None, keep_parents=False):
        get_imgur_client().make_request('DELETE', 'image/%s' % self.imgur_id)
        return super(ImgurImage, self).delete(using, keep_parents)


def get_imgur_client():
    return ImgurClient(client_id=ImgurSetting.get_settings_value(ImgurSetting.CLIENT_ID),
                       client_secret=ImgurSetting.get_settings_value(ImgurSetting.CLIENT_SECRET),
                       refresh_token=ImgurSetting.get_settings_value(ImgurSetting.REFRESH_TOKEN))
