import json
import requests
import time
import sys

if __name__=='__main__':
    server = sys.argv[1]
    print 'Test Cases Started, please wait few seconds for result...'
    test=[{'values':[1, 2], 'result':3,'job_id':None},
           {'values':[3, 4], 'result':7,'job_id':None},
           {'values':[13, 4], 'result':17,'job_id':None},
           {'values':[3, 11], 'result':14,'job_id':None}]
    submit_job_url = 'http://%s/client/calculator/' % server
    fetch_status_url = 'http://%s/client/job_status/'% server
    
    for item in test:
        vals = item['values']
        data = {'k1':vals[0],'k2':vals[1]}
        req = requests.post(submit_job_url, data=data)
        job_id = json.loads(req.text)['job_id']
        item['job_id'] = job_id
    
    time.sleep(5)
    success = True
    for item in test:
        expected_res = item['result']
        jdata = {'id':item['job_id']}
        job_result = requests.post(fetch_status_url, data=jdata)
        server_result = json.loads(job_result.text)['result']
        if expected_res != server_result:
            success = False
            break
        
    if success:
        print 'Test Cases Successfully Finished'
    else:
        print 'Test Cases Failed'