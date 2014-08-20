from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^browse/$', TemplateView.as_view(template_name='news/browse.html'))
]