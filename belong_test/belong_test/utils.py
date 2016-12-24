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
        ret_item=self.get(lr_key+1)
        return ret_item

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
        return True
