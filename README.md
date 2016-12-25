Instruction Before Usage:
-----
Following are the steps to use this package
cd belong_test/ # you can find requirements.txt here
1) sudo apt-get install redis-tools, redis-server
2) pip install -r requirements.txt
3) ./start.sh # if it fails here run 'chmod a+x start.sh'

-----
```python # Please have a look at worker_app/tests.py for more information
import requests
server = '127.0.0.1:8000' # default server
submit_job_url = 'http://%s/client/calculator/' % server
fetch_status_url = 'http://%s/client/job_status/'% server
```
# To submit a job
```
data = {'k1':val1,'k2':val2}
req = requests.post(submit_job_url, data=data)
```
# To query for a job
```
data = {'id':job_id}
job_result = requests.post(fetch_status_url, data=jdata)

```