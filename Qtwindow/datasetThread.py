from PyQt5.QtCore import *
import global_variable
import pre_data

class dataThread(QThread):
    def __init__(self, is_torchvision, is_folder, torchvision_name, train_path, test_path, aim_path, resize):
        super(dataThread, self).__init__()
        self.is_torchvision = is_torchvision
        self.is_folder = is_folder
        self.torchvision_name = torchvision_name
        self.train_path = train_path
        self.test_path = test_path
        self.aim_path = aim_path
        self.resize = resize

    def run(self):
        pre = pre_data.PrepareData(self.is_torchvision, self.is_folder, self.torchvision_name, self.train_path, self.test_path, self.aim_path, self.resize)
        train_data, test_data = pre.get_data()
        global_variable.train_data = train_data
        global_variable.test_data = test_data