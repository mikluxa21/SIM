from SaveData import SaveData
from ParallWorker import Thread
from examples.test_ps5000a import pico_worker
from CardReader import m
from time import sleep
import numpy as np



def run():
    save_data = SaveData()
    thread = Thread(pico_worker.get_data)
    thread.start()
    sleep(5)
    res1 = [np.asarray(m.main(), dtype=np.int16)]
    pico_worker.stop()
    res2 = thread.stop()
    save_data.save(res1, name="commands")
    save_data.save(res2)

if __name__ == "__main__":
    run()