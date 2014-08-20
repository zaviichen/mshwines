from django.conf.urls import url
from apps.status.views import ProductRecordView, RecentProductView

urlpatterns = [
    url(r'^popular/$', ProductRecordView.as_view()),
    url(r'^recent/$', RecentProductView.as_view())
]