import threading
import time
import queue


from examples.test_ps5000a import pico_worker

class Thread(threading.Thread):
    def __init__(self, func_for_work):
        super().__init__()
        self.geted_data = []
        self.func_for_work = func_for_work
        self.flag = threading.Event()
        self.queueu = queue.Queue()

    def stop(self):
        self.flag.set()
        print(self.geted_data)
        return self.geted_data

    def run(self):
        time.sleep(1)
        for i in self.func_for_work():
            self.geted_data.append([i])
            if self.flag.is_set():
                break

    def join(self, *argc):
        self.flag.set()
        threading.Thread.join(self, *argc)
        return self.geted_data



if __name__ == '__main__':
    thread = Thread(pico_worker.get_data)
    thread.start()
    time.sleep(4)
    print(thread.stop())