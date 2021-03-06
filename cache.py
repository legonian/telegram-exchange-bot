import threading
import time

class Cache:
    def __init__(self, max_time=10):
        self.lock = threading.Lock()
        self.max_time = max_time
        self.data = {}

    def save_rates(self, rates, base):
        time_now = int(time.time())
        res = {'rates': rates, 'last_updated': time_now}

        with self.lock:
            self.data[base] = res
    
    def rates(self, base):
        time_now = int(time.time())
        
        with self.lock:
            if base not in self.data:
                return None
            res = self.data[base]
            time_since_update = time_now - res['last_updated']
            is_expired = self.max_time < time_since_update
            if is_expired:
                del self.data[base]
                return None
            return res['rates']
