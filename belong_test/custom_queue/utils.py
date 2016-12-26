import time
import threading
from redis.exceptions import WatchError

PERIODIC_REFRESH_CUTOFF=12000  # seconds
BATCH_SIZE=50


class SimpleRedisWrapper(object):
    job_id_source='job_counter'
    def __init__(self, redis_object):
        self.redis_object=redis_object
        self._check_lock=threading.Lock()

    def compute_job_id(self):
        key=SimpleRedisWrapper.job_id_source

        with self._check_lock:
            v=None
            while v is None:
                try:
                    p=self.redis_object.pipeline()
                    p.watch(key)
                    p.multi()
                    p.incr(key)
                    p.get(key)
                    v=p.execute()
                except WatchError:
                    pass
            if v:
                return v[0]

    def create_jdata(self, v1, v2, result = ''):
        content={'v1':v1, 'v2':v2, 'result':result}
        return content

    def get_max_job_id(self):
        max_id = self.redis_object.get(SimpleRedisWrapper.job_id_source)
        if max_id:
            return int(max_id)
        else:
            return 0

    def add_job(self, v1, v2):
        job_id=self.compute_job_id()
        self.set_job(job_id, v1, v2)
        return job_id

    def set_job(self, job_id, v1, v2, result = ''):
        j_data=self.create_jdata(v1, v2, result)
        return self.redis_object.hmset(job_id, j_data)

    def get_job(self, job_id):
        return self.redis_object.hgetall(job_id)

    def delete_key(self, key):
        return self.redis_object.delete(key)

    def set_job_result(self, job_id, result):
        job_data=self.get_job(job_id)
        return self.set_job(job_id, job_data['v1'], job_data['v2'], result)



class SimpleQueueFromRedis(object):
    job_queue_key='job_queue' # to maintain order
    job_queue_set= 'job_queue_set' # using this to not to add pending jobs again
    waiting_job_set_key='waiting_job_set'
    
    def __init__(self, redis_wrapper):
        self.redis_object=redis_wrapper.redis_object
        self.redis_wrapper=redis_wrapper
        self.last_refresh=time.time()
        self.job_id_counter=0
        self._check_lock=threading.Lock()

    def periodic_refresh(self):
        delta=time.time()-self.last_refresh
        if not self.get_job_queue_size() or delta>PERIODIC_REFRESH_CUTOFF:
            self.refresh_unprocessed()
            self.last_refresh=time.time()

    def refresh_unprocessed(self, limit = BATCH_SIZE):  # TODO: Refactor me
#         all_job_keys=self.redis_object.keys('[1-9]*')

        if self.get_waiting_job_queue_size():
            # before a batch finishes, all items in that batch should be processed, giving more prior based on time
            while self.get_waiting_job_queue_size():
                item=self.redis_object.spop(SimpleQueueFromRedis.waiting_job_set_key)
                if item and not self.is_in_job_queue(item):
                    self.put(item)
        else:
            key=self.job_id_counter  # start adding jobs from this ID
            max_id = self.redis_wrapper.get_max_job_id()
            while max_id and key<= max_id:
                # TODO: optimized key check, not checking all keys
                if self.get_job_queue_size()>BATCH_SIZE:
                    break
                data=self.get(key)
                # data['result'] no need to check, just a precaution, only unprocessed will come
                if data and not data['result']:
                    self.put(key)
                key+=1
            self.job_id_counter=key

    def get_job_queue_size(self):
        return self.redis_object.llen(SimpleQueueFromRedis.job_queue_key)

    def get_waiting_job_queue_size(self):
        return self.redis_object.scard(SimpleQueueFromRedis.waiting_job_set_key)
        
    def is_in_job_queue(self,job_id):
        return self.redis_object.sismember(SimpleQueueFromRedis.job_queue_set, job_id)
    
    def pop_job(self):
        self.periodic_refresh()
        item=None
        with self._check_lock:
            if self.get_job_queue_size():
                item=self.redis_object.lpop(SimpleQueueFromRedis.job_queue_key)
                self.redis_object.srem(SimpleQueueFromRedis.job_queue_set, item)
                self.redis_object.sadd(SimpleQueueFromRedis.waiting_job_set_key, item)
        if item:
            return {'id':item, 'data':self.get(item)}

    def get(self, key):
        return self.redis_wrapper.get_job(key)

    def update_job(self, job_id, result):
        if result:
            self.redis_object.srem(SimpleQueueFromRedis.waiting_job_set_key, job_id)
            return self.redis_wrapper.set_job_result(job_id, result)
            

    def put(self, job_id):
        self.redis_object.rpush(SimpleQueueFromRedis.job_queue_key, job_id)
        self.redis_object.sadd(SimpleQueueFromRedis.job_queue_set, job_id)


'''
Using only Redis for storing, data and to generate unique keys, db was not involved, dropped this,
 cos it didn't function with multiconsumer
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



