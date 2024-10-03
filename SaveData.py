import os
import numpy as np



class SaveData:
    def __init__(self, path = os.getcwd() + "\\rslt"):
        if not os.path.isdir(path):
            os.mkdir(path)
        self.path = path
        self.expirement_nomber = 0
        for abspath, dirnames, filenames in os.walk(self.path):
            for dirname in dirnames:
                self.expirement_nomber = max(int(dirname), self.expirement_nomber)
        self.expirement_nomber += 1
        self.work_dir = self.path + "\\" + str(self.expirement_nomber)
        os.mkdir(self.work_dir)
        self.name_file_for_save = 0

    def save(self, *data: list, name: str = '0'):
        if name == '0':
            self.name_file_for_save += 1
            self.name = self.name_file_for_save
        else:
            self.name = name
        np.save(self.work_dir + "\\" + str(self.name),
                np.array(data))
