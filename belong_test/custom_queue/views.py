from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from belong_test.settings import MY_REDIS_QUEUE
import json
from rest_framework import status
from client.models import InputJobs
# Create your views here.

@csrf_exempt
def fetch_pending_job(request):
    item = MY_REDIS_QUEUE.pop()
    return HttpResponse(json.dumps(item),content_type = 'application/json',
                        status=status.HTTP_200_OK)

@csrf_exempt
def update_job_result(request):
    data = request.POST
    job_id = data.get('id')
    result = data.get('result')
    
    try:
        success = InputJobs.update_result(job_id, result)
    except InputJobs.DoesNotExist:
        success = False
    
    if success:
        content={'job_id':job_id, 'message':'Result Accepted'}
        return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_202_ACCEPTED)
    else:
        content={'job_id':job_id, 'message':"Result Couldn't be accepted"}
    return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_404_NOT_FOUND)
    