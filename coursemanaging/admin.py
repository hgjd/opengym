from django.contrib import admin
from .models import Course, Session, User, NewsItem, NewsBulletin


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'is_active', 'course_level')


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birthdate', 'volunteer', 'teacher')


admin.site.register(Course, CourseAdmin)
admin.site.register(Session)
admin.site.register(User, UserAdmin)
admin.site.register(NewsItem)
admin.site.register(NewsBulletin)
