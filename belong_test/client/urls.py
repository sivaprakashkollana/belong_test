from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^calculator/', views.submit_data, name='submit_data'),
    url(r'^job_status/', views.fetch_job_result, name='fetch_job_result')
]