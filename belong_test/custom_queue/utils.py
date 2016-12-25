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
LAST_READ_REDIS_KEY='last_read'
LAST_READ_DEFAULT=0
LATEST_ADDED_REDIS_KEY='latest_added'
LATEST_ADDED_DEFAULT=0
PROCESSED=1
PROCESSING=0
IDLE=-1

class SimpleQueueFromRedis(object):
    def __init__(self, redis_object):
        self.redis_object=redis_object
        self.__init_data()

    def __init_data(self):
        if not self.redis_object.exists(LAST_READ_REDIS_KEY):
            self.set_lr_key(LAST_READ_DEFAULT)
        if not self.redis_object.exists(LATEST_ADDED_REDIS_KEY):
            self.set_la_key(LATEST_ADDED_DEFAULT)


    def get_lr_key(self):
        return int(self.get(LAST_READ_REDIS_KEY)[LAST_READ_REDIS_KEY])

    def set_lr_key(self, value):
        self.set(LAST_READ_REDIS_KEY, {LAST_READ_REDIS_KEY:value})

    def get_la_key(self):
        return int(self.get(LATEST_ADDED_REDIS_KEY)[LATEST_ADDED_REDIS_KEY])

    def set_la_key(self, value):
        return self.set(LATEST_ADDED_REDIS_KEY, {LATEST_ADDED_REDIS_KEY:value})

    def pop(self):
        lr_key=self.get_lr_key()
        if self.redis_object.exists(lr_key+1):
            ret_item=self.get(lr_key+1)
            return {'id':lr_key+1, 'item':ret_item}

    def get(self, key):
        return self.redis_object.hgetall(key)

    def set(self, key, val_dict):
        self.redis_object.hmset(key, val_dict)

    def delete_item(self, key):
        self.redis_object.delete(key)

    def add(self, v_list):
        new_key=self.get_la_key()+1
        item={'values':v_list, 'status':IDLE, 'result':''}
        self.set(new_key, item)
        self.set_la_key(new_key)
        return new_key

    def update(self, key, result):
        item=self.get(key)
        item['result']=result
        item['status']=PROCESSED
        self.set(key, item)
        self.set_lr_key(self.get_lr_key()+1)
        return True'''



