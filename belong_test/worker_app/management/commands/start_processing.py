from django.core.management.base import BaseCommand
from belong_test.settings import MY_REDIS_QUEUE
import time
import ast

def compute(val_list):
    return sum(val_list)

class Command(BaseCommand):
    def handle(self, *args, **options):
        while True:
            lr = MY_REDIS_QUEUE.get_lr_key()
            la = MY_REDIS_QUEUE.get_la_key()
            new_item = None
            if lr < la :
                key = lr
                new_item = MY_REDIS_QUEUE.pop()
                if new_item:
                    vals = ast.literal_eval(new_item['values'])
                    r = compute(vals)
                    MY_REDIS_QUEUE.update(key, r)
            
            if not lr < la or not new_item:
                time.sleep(1)
            
            