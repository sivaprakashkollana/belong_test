from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.http import HttpResponse
from belong_test.settings import MY_REDIS_QUEUE
import json
from rest_framework import status
# Create your views here.

@csrf_exempt
@transaction.atomic
def fetch_pending_job(request):
    item = MY_REDIS_QUEUE.pop()
    return HttpResponse(json.dumps(item),content_type = 'application/json',
                        status=status.HTTP_200_OK)

@csrf_exempt
@transaction.atomic
def update_job_result(request):
    data = request.POST
    job_id = data.get('id')
    result = data.get('result')
    MY_REDIS_QUEUE.update(job_id, result)
    content={'job_id':job_id, 'message':'Result Accepted'}
    return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_202_ACCEPTED)
    