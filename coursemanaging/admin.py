from django.contrib import admin
from .models import Course, Session, User, NewsItem, NewsBulletin, Event, BuildingDay


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'is_active', 'course_level')


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birthdate', 'email', 'teacher', 'date_joined')


admin.site.register(Course, CourseAdmin)
admin.site.register(Session)
admin.site.register(User, UserAdmin)
admin.site.register(NewsItem)
admin.site.register(NewsBulletin)
admin.site.register(Event)
admin.site.register(BuildingDay)
