from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from belong_test.settings import MY_REDIS_WRAPPER


@csrf_exempt
def submit_data(request):
    data=request.POST
    item1=int(data.get('k1'))
    item2=int(data.get('k2'))

    job_id=MY_REDIS_WRAPPER.add_job(item1, item2)
    content={'job_id':job_id, 'message':'Request Submitted'}
    return HttpResponse(json.dumps(content), content_type = 'application/json',
                        status = status.HTTP_201_CREATED)

@csrf_exempt
def fetch_job_result(request):
    data=request.POST
    job_id=data.get('id')
    print job_id
    j_data = MY_REDIS_WRAPPER.get_job(job_id)
    result = None
    if j_data:
        if j_data['result']:
            item={'job_id':job_id, 'result':j_data['result']}
            result = HttpResponse(json.dumps(item), content_type = 'application/json',
                            status = status.HTTP_200_OK)
        else:
            content={'job_id':job_id, 'message':'Request still in process'}
            result = HttpResponse(json.dumps(content), content_type = 'application/json',
                            status = status.HTTP_201_CREATED)
    else:
        content={'job_id':job_id, 'message':"Job Id Couldn't be accepted"}
        result =  HttpResponse(json.dumps(content), content_type = 'application/json',
                            status = status.HTTP_404_NOT_FOUND)

    return result