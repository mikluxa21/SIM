from picoscope import ps5000a
import numpy as np
import time


CAPTURE = 1
INTERVAL = 100e-9
DURATION = 2e-3
RESOLUTION = '16'

class PicoWorker():
    def __init__(self):
        global CAPTURE
        global INTERVAL
        global DURATION
        global RESOLUTION
        self.if_stop = False
        self.ps = ps5000a.PS5000a()

        # rapid block mode

        self.ps.setChannel(channel="A", coupling="DC", VRange=15)
        self.ps.setChannel(channel="B", enabled=False)

        self.n_captures = CAPTURE
        sample_interval = INTERVAL  # 100 ns
        sample_duration = DURATION  # 1 ms
        self.ps.setResolution(RESOLUTION)
        self.ps.setSamplingInterval(sample_interval, sample_duration)
        self.ps.setSimpleTrigger("A", threshold_V=0.1, timeout_ms=5)

        self.samples_per_segment = self.ps.memorySegments(self.n_captures)
        self.ps.setNoOfCaptures(self.n_captures)

    def get_data(self):
        while not self.if_stop:
            data = np.zeros((self.n_captures, 100000), dtype=np.int16) #КОСТЫЛЬ!!!!!!!!!!!!!!!!!
            self.ps.runBlock()
            self.ps.waitReady()
            res, num, t = self.ps.getDataRawBulk(data=data)
            #print(t)
            #print(num)
            #print(res)
            yield res[0][:num]

    def stop(self):
        self.if_stop = True


pico_worker = PicoWorker()

if __name__=="__main__":
    for i in pico_worker.get_data():
        print(i)

