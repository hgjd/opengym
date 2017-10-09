from django.contrib import admin
from .models import Course, Session


class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_level')


admin.site.register(Course, CourseAdmin)
admin.site.register(Session)
