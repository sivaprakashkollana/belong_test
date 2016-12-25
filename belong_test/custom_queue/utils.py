import time
import threading
from client.models import InputJobs

PROCESSED = 1
PERIODIC_REFRESH_CUTOFF=120 # seconds
BATCH_SIZE=50

class SimpleQueueFromRedis(object):
    def __init__(self, redis_object):
        self.redis_object=redis_object
        self.un_processed_items=[]
        self.last_refresh=time.time()
        self.redis_key='jobs'
        self.__init_data()
        self._check_lock=threading.Lock()

    def __init_data(self):
        self.redis_object.delete(self.redis_key)
        self.refresh_unprocessed()

    def periodic_refresh(self):
        delta=time.time()-self.last_refresh
        if not self.un_processed_items or delta>PERIODIC_REFRESH_CUTOFF:
            self.refresh_unprocessed()
            self.last_refresh=time.time()

    def add_to_processed(self, job_id):
        self.under_process_items.remove(job_id)

    def refresh_unprocessed(self, limit = BATCH_SIZE):  # TODO: Refactor me
        objs=list(InputJobs.objects.exclude(status = PROCESSED).values_list('id', flat = True)[:BATCH_SIZE])
        [self.put(job_id) for job_id in objs]
        self.un_processed_items=objs

    def pop(self):
        self.periodic_refresh()
        item = None
        with self._check_lock:
            if self.un_processed_items:
                item=self.un_processed_items.pop(0)
#           item = self.redis_object.lpop(self.redis_key) # not sure, I can use this functionality, it implies queue func
        if item:
            obj=InputJobs.objects.get(id = item)
            item={'values':[obj.value1, obj.value2]}
            return {'id':obj.id, 'item':item}

    def get(self, key):
        return self.redis_object.hgetall(key)

    def set(self, key, val_dict):
        self.redis_object.hmset(key, val_dict)

    def delete_item(self, key):
        self.redis_object.delete(key)

    def put(self, job_id):
        self.redis_object.rpush(self.redis_key, job_id)


'''
Using only Redis for storing, data and to generate unique keys, db was not involved, dropped this, cos it didn't function with multiconsumer
import time
import threading
from client.models import InputJobs

PROCESSED = 1
PERIODIC_REFRESH_CUTOFF=120 # seconds
BATCH_SIZE=50

class SimpleQueueFromRedis(object):
    def __init__(self, redis_object):
        self.redis_object=redis_object
        self.un_processed_items=[]
        self.last_refresh=time.time()
        self.redis_key='jobs'
        self.__init_data()
        self._check_lock=threading.Lock()

    def __init_data(self):
        self.redis_object.delete(self.redis_key)
        self.refresh_unprocessed()

    def periodic_refresh(self):
        delta=time.time()-self.last_refresh
        if not self.un_processed_items or delta>PERIODIC_REFRESH_CUTOFF:
            self.refresh_unprocessed()
            self.last_refresh=time.time()

    def add_to_processed(self, job_id):
        self.under_process_items.remove(job_id)

    def refresh_unprocessed(self, limit = BATCH_SIZE):  # TODO: Refactor me
        objs=list(InputJobs.objects.exclude(status = PROCESSED).values_list('id', flat = True)[:BATCH_SIZE])
        [self.put(job_id) for job_id in objs]
        self.un_processed_items=objs

    def pop(self):
        self.periodic_refresh()
        item = None
        with self._check_lock:
            if self.un_processed_items:
                item=self.un_processed_items.pop(0)
#           item = self.redis_object.lpop(self.redis_key) # not sure, I can use this functionality, it implies queue func
        if item:
            obj=InputJobs.objects.get(id = item)
            item={'values':[obj.value1, obj.value2]}
            return {'id':obj.id, 'item':item}

    def get(self, key):
        return self.redis_object.hgetall(key)

    def set(self, key, val_dict):
        self.redis_object.hmset(key, val_dict)

    def delete_item(self, key):
        self.redis_object.delete(key)

    def put(self, job_id):
        self.redis_object.rpush(self.redis_key, job_id)
'''



