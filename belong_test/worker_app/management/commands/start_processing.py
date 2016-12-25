from django.core.management.base import BaseCommand
import time
import requests
from rest_framework import status
import json

pending_job_url='/custom_queue/pending_job/'
post_job_result_url='/custom_queue/job_result/'

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

    def fetch_pending_job(self):
        ret={}
        try:
            ret=json.loads(requests.get(self.job_server+pending_job_url, timeout = 10).text)
        except requests.Timeout:
            pass
        except Exception as exc:
            pass
        return ret

    def post_job_result(self, job_id, result):
        count=0
        while count<3:  # retry count incase of failure
            try:
                data={'id':job_id, 'result':result}
                ret=requests.post(self.job_server+post_job_result_url, data = data)
                if ret.status_code==status.HTTP_202_ACCEPTED:
                    break
            except:
                pass
            count+=1

    def process_to_call(self):
        while True:
            new_item=self.fetch_pending_job()
            if new_item:
                job_id=new_item['id']
                vals=new_item['item']['values']
                r=sum(vals)
                self.post_job_result(job_id, r)

            if not new_item:
                time.sleep(1)

    def handle(self, *args, **options):
        if options['job_server'] is not None:
            self.job_server=options['job_server']
        
        workers=int(options['workers'])
        from multiprocessing import Process
        jobs = []
        for i in xrange(workers):
            p = Process(target=self.process_to_call)
            jobs.append(p)
            p.start()



