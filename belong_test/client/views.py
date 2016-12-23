from django.http import HttpResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from belong_test.settings import MY_REDIS, LATEST_ADDED_REDIS_KEY

import json

def index(request):
    return HttpResponse("Hello, world. You're at the client index.")

@csrf_exempt
def compute_sum(request):
    data=request.POST
    item1=int(data.get('k1'))
    item2=int(data.get('k2'))
    
    latest_key=MY_REDIS.get(LATEST_ADDED_REDIS_KEY)
    new_key=int(latest_key)+1
    MY_REDIS.set(new_key, "%s:%s"%(item1, item2))
    MY_REDIS.set(LATEST_ADDED_REDIS_KEY, new_key)


    content={'job_id':new_key, 'message':'Request Submitted'}
    return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_201_CREATED)
