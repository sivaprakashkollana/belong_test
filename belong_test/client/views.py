from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from belong_test.settings import MY_REDIS_QUEUE

import json
from client.models import InputJobs


@csrf_exempt
def submit_data(request):
    data=request.POST
    item1=int(data.get('k1'))
    item2=int(data.get('k2'))
    obj = InputJobs(value1=item1, value2=item2)
    obj.save()
    job_id = obj.id
#     job_id = MY_REDIS_QUEUE.add([item1,item2])
    content={'job_id':job_id, 'message':'Request Submitted'}
    return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_201_CREATED)

@csrf_exempt
def fetch_job_result(request):
    data =request.GET
    job_id = data.get('id')
    item = MY_REDIS_QUEUE.get(job_id)
    if item['result']:
        return HttpResponse(json.dumps(item), content_type = 'application/json',
                        status = status.HTTP_200_OK)
    else:
        content={'job_id':job_id, 'message':'Request still in process'}
        return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_201_CREATED)
