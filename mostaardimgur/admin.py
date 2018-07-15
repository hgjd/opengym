from django.contrib import admin

# Register your models here.
from mostaardimgur.models import ImgurAlbum, ImgurSetting


class ImgurSettingAdmin(admin.ModelAdmin):
    list_display = ('setting', 'value')


admin.site.register(ImgurAlbum)
admin.site.register(ImgurSetting, ImgurSettingAdmin)
