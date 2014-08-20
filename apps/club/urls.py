from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^info/$', TemplateView.as_view(template_name='club/info.html'))
]