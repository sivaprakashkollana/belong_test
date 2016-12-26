from django.core.management.base import BaseCommand
import time
import requests
from rest_framework import status
from random import randint

create_job_url='/client/calculator/'

class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument('--job_server',  # "http://127.0.0.1:8000/custom_queue/pending_job/"
                            action = 'store',
                            dest = 'job_server',
                            default = 'http://127.0.0.1:8000',
                            help = 'This variable is used to query client for jobs')
        parser.add_argument('--workers',
                            dest = 'workers',
                            type = int,
                            default = 1,
                            help = 'This variable is used to create number of workers')

    def create_job(self):
        count=0
        while count<3:  # retry count incase of failure
            try:
                data={'k1':randint(1, 1000), 'k2':randint(1, 1000)}
                ret=requests.post(self.job_server+create_job_url, data = data)
                if ret.status_code==status.HTTP_201_CREATED:
                    break
            except :
                pass
            count+=1

    def process_to_call(self):
        i=0
        while i<10:
            new_item=self.create_job()
            i+=1
            if not new_item:
                time.sleep(1)

    def handle(self, *args, **options):

        if options['job_server'] is not None:
            self.job_server=options['job_server']

        workers=int(options['workers'])
        from multiprocessing import Process
        jobs=[]
        for i in xrange(workers):
            p=Process(target = self.process_to_call)
            jobs.append(p)
            p.start()



