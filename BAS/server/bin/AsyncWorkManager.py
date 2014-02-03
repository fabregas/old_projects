import Queue
import threading
import time

#-----------------------------------------------------------------

AsyncWorkQueue = Queue.Queue()

#-----------------------------------------------------------------

CLOSE_THREAD_FLAG = None

class CheckThread(threading.Thread):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        threading.Thread.__init__(self)

    def run(self):
        min_size = self.thread_pool.min
        max_size = self.thread_pool.max
        get_queue_size = AsyncWorkQueue.qsize
        shrink_thread = self.thread_pool.shrink
        grow_thread = self.thread_pool.grow


        while not self.thread_pool.stoped:
            time.sleep(1)

            size = get_queue_size()

            if size == 0 and size > min_size:
                shrink_thread(1)
            if size > 0 and size < max_size:
                grow_thread((size+1) / 2)


class AsyncWorkerThread(threading.Thread):
    def run(self):
        try:
            while True:
                task = AsyncWorkQueue.get()
                if task is CLOSE_THREAD_FLAG:
                    return

                try:
                    task()
                except:
                    #exceptions must be processed in task body...
                    pass
        except (KeyboardInterrupt, SystemExit), exc:
            pass


class AsyncThreadPool(object):
    def __init__(self, dynamic_threading=True, min=1, max=20):
        self.dynamic_threading = dynamic_threading
        self.min = min
        self.max = max
        self._threads = []
        self._queue = Queue.Queue()
        self.get = AsyncWorkQueue.get
        self.stoped = None

    def start(self):
        """Start the pool of threads."""
        self.stoped = False
        for i in range(self.min):
            self._threads.append(AsyncWorkerThread())

        if self.dynamic_threading:
            self._checker_thread = CheckThread(self)
            self._checker_thread.start()

        for worker in self._threads:
            worker.setName("Async task thread " + worker.getName())
            worker.start()

    def _get_idle(self):
        """Number of worker threads which are idle. Read-only."""
        return len([t for t in self._threads if t.conn is None])
    idle = property(_get_idle, doc=_get_idle.__doc__)


    def grow(self, amount):
        """Spawn new worker threads (not above self.max)."""
        for i in range(amount):
            if self.max > 0 and len(self._threads) >= self.max:
                break
            worker = AsyncWorkerThread()
            worker.setName("Async task thread " + worker.getName())
            self._threads.append(worker)
            worker.start()

    def shrink(self, amount):
        """Kill off worker threads (not below self.min)."""
        # Grow/shrink the pool if necessary.
        # Remove any dead threads from our list
        for t in self._threads:
            if not t.isAlive():
                self._threads.remove(t)
                amount -= 1

        if amount > 0:
            for i in range(min(amount, len(self._threads) - self.min)):
                AsyncWorkQueue.put(CLOSE_THREAD_FLAG)

    def stop(self, timeout=5):
        self.stoped = True
        # Must shut down threads here so the code that calls
        # this method can know when all threads are stopped.
        for worker in self._threads:
            AsyncWorkQueue.put(CLOSE_THREAD_FLAG)

        if self.dynamic_threading and self._checker_thread.isAlive():
            self._checker_thread.join(2)

        # Don't join currentThread (when stop is called inside a request).
        current = threading.currentThread()
        if timeout and timeout >= 0:
            endtime = time.time() + timeout
        while self._threads:
            worker = self._threads.pop()
            if worker is not current and worker.isAlive():
                try:
                    if timeout is None or timeout < 0:
                        worker.join()
                    else:
                        remaining_time = endtime - time.time()
                        if remaining_time > 0:
                            worker.join(remaining_time)
                except:
                    pass
