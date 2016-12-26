from __future__ import unicode_literals
from django.db import models
import django


django.setup()
# Create your models here.


class InputJobs(models.Model):
    created_on=models.DateTimeField(auto_now_add = True)
    updated_on=models.DateTimeField(auto_now = True)
    result=models.IntegerField(null = True, blank = True)
    value1=models.IntegerField(null = True, blank = True)
    value2=models.IntegerField(null = True, blank = True)
    PCD='processed'
    PEN='pending'
    NOT_PCD='not_processed'
    STATUSES=((PCD, 1),
                (PEN, 0),
                (NOT_PCD,-1))
    status=models.IntegerField(choices = STATUSES, blank = True, null = True)

    class Meta:
        ordering=('created_on',)
    
    @classmethod
    def update_result(cls,job_id,val):
        from belong_test.dictionary import PROCESSED
        obj = cls.objects.get(id=job_id)
        obj.status = PROCESSED
        obj.result = val
        obj.save()
        return True
