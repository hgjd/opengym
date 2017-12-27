from django.contrib import admin
from .models import Course, Session, User


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_level')


class UserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birthdate', 'volunteer', 'teacher')


admin.site.register(Course, CourseAdmin)
admin.site.register(Session)
admin.site.register(User, UserAdmin)
