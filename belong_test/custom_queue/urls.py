from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^pending_job/', views.fetch_pending_job, name='pending_job'),
    url(r'^job_result/', views.update_job_result, name='job_result'),
]