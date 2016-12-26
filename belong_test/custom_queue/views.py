from belong_test.settings import MY_REDIS_QUEUE, MY_REDIS_WRAPPER
from client.models import InputJobs
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
# Create your views here.

@csrf_exempt
def fetch_pending_job(request):
    item = MY_REDIS_QUEUE.pop_job()
    return HttpResponse(json.dumps(item),content_type = 'application/json',
                        status=status.HTTP_200_OK)

@csrf_exempt
def update_job_result(request):
    data = request.POST
    print data
    job_id = data.get('id')
    result = data.get('result')
    success = MY_REDIS_QUEUE.update_job(job_id, result)
    if success:
        content={'job_id':job_id, 'message':'Result Accepted'}
        return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_202_ACCEPTED)
    else:
        content={'job_id':job_id, 'message':"Result Couldn't be accepted"}
        return HttpResponse(json.dumps(content), content_type = 'application/json',
                            status = status.HTTP_404_NOT_FOUND)
    