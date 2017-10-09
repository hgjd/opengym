from django.urls import reverse_lazy
from django.views import generic
from .models import Course


class IndexView(generic.TemplateView):
    """home page of the opengym platform"""
    template_name = 'coursemanaging/index.html'


class CourseCreateView(generic.CreateView):
    """create view for a course"""
    template_name = 'coursemanaging/course-create.html'
    model = Course
    fields = ['course_name', 'course_level', 'single_session_possible', 'description']
    success_url = reverse_lazy('coursemanaging:index')


class CourseDetailView(generic.DetailView):
    """Detail view of a course"""
    template_name = 'coursemanaging/course-detail.html'
    model = Course


class CourseListView(generic.ListView):
    """List view of a course"""
    template_name = 'coursemanaging/course-list.html'
    context_object_name = 'course_list'
    model = Course

    def get_queryset(self):
        return Course.objects.all()


class CourseUpdateView(generic.UpdateView):
    """Update view of a course"""
    template_name = 'coursemanaging/course-update.html'
    model = Course
    fields = ['course_name', 'course_level', 'single_session_possible', 'description']
    success_url = reverse_lazy('coursemanaging:index')


class CourseDeleteView(generic.DeleteView):
    """Delete view of a course"""
    template_name = "coursemanaging/course-delete.html"
    model = Course


