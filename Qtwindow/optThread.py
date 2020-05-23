from PyQt5.QtCore import *
import optimization.gridSearchModel as GridSearch
import optimization.randomSearchModel as RandomSearch
import optimization.bayesianModel as BayesianSearch
import optimization.geneticModel as GeneticSearch
import optimization.psoModel as PSOSearch

mustInt_list = ['k', 'num_epochs', 'batch_size']

class gridThread(QThread):
    trigger = pyqtSignal(int)

    def __init__(self, dataset_name, is_k_fold, is_test, basic_params, hyper_dict, net_path, train_data, test_data):
        super(gridThread, self).__init__()
        self.dataset_name = dataset_name
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.hyper_dict = hyper_dict
        self.basic_params = basic_params
        self.net_path = net_path
        self.train_data = train_data
        self.test_data = test_data

    def run(self):
        try:
            GridSearch.grid_search(self.dataset_name, self.is_k_fold, self.is_test, self.basic_params, self.hyper_dict, self.net_path, self.train_data, self.test_data)
        except FileNotFoundError:
            self.trigger.emit(1)
        except RuntimeError:
            self.trigger.emit(2)
        else:
            self.trigger.emit(0)

class randomThread(QThread):
    trigger = pyqtSignal(int)

    def __init__(self, dataset_name, is_k_fold, is_test, num_iter, basic_params, hyper_dict, net_path, train_data, test_data):
        super(randomThread, self).__init__()
        self.dataset_name = dataset_name
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.num_iter = num_iter
        self.basic_params = basic_params
        self.hyper_dict = hyper_dict
        self.net_path = net_path
        self.train_data = train_data
        self.test_data = test_data

    def run(self):
        try:
            RandomSearch.random_search(self.dataset_name, self.is_k_fold, self.is_test, self.num_iter, self.basic_params, self.hyper_dict, self.net_path, mustInt_list, self.train_data, self.test_data)
        except FileNotFoundError:
            self.trigger.emit(1)
        except RuntimeError:
            self.trigger.emit(2)
        else:
            self.trigger.emit(0)

class bayesianThread(QThread):
    trigger = pyqtSignal(int)

    def __init__(self, dataset_name, is_k_fold, is_test, num_init, num_iter, acq, kappa, xi, basic_params, hyper_dict, net_path, train_data, test_data):
        super(bayesianThread, self).__init__()
        self.dataset_name = dataset_name
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.num_init = num_init
        self.num_iter = num_iter
        self.acq = acq
        self.kappa = kappa
        self.xi = xi
        self.basic_params = basic_params
        self.hyper_dict = hyper_dict
        self.net_path = net_path
        self.train_data = train_data
        self.test_data = test_data

    def run(self):
        try:
            BayesianSearch.bayesian_search(self.dataset_name, self.is_k_fold, self.is_test, self.num_init, self.num_iter, self.acq, self.kappa, self.xi, self.basic_params, self.hyper_dict, self.net_path, mustInt_list, self.train_data, self.test_data)
        except FileNotFoundError:
            self.trigger.emit(1)
        except RuntimeError:
            self.trigger.emit(2)
        else:
            self.trigger.emit(0)

class geneticThread(QThread):
    trigger = pyqtSignal(int)

    def __init__(self, dataset_name, is_k_fold, is_test, num_iter, num_population, pc, pm, code_length, basic_params, hyper_dict, net_path, train_data, test_data):
        super(geneticThread, self).__init__()
        self.dataset_name = dataset_name
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.num_iter = num_iter
        self.num_population = num_population
        self.pc = pc
        self.pm = pm
        self.code_length = code_length
        self.basic_params = basic_params
        self.hyper_dict = hyper_dict
        self.net_path = net_path
        self.train_data = train_data
        self.test_data = test_data

    def run(self):
        try:
            GeneticSearch.genetic_search(self.dataset_name, self.is_k_fold, self.is_test, self.num_iter, self.num_population, self.pc, self.pm, self.code_length, self.basic_params, self.hyper_dict, self.net_path, mustInt_list, self.train_data, self.test_data)
        except FileNotFoundError:
            self.trigger.emit(1)
        except RuntimeError:
            self.trigger.emit(2)
        else:
            self.trigger.emit(0)

class psoThread(QThread):
    trigger = pyqtSignal(int)

    def __init__(self, dataset_name, is_k_fold, is_test, num_iter, num_point, c1, c2, w_low, w_high, num_extra, basic_params, hyper_dict, net_path, train_data, test_data):
        super(psoThread, self).__init__()
        self.dataset_name = dataset_name
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.num_iter = num_iter
        self.num_point = num_point
        self.c1 = c1
        self.c2 = c2
        self.w_low = w_low
        self.w_high = w_high
        self.num_extra = num_extra
        self.basic_params = basic_params
        self.hyper_dict = hyper_dict
        self.net_path = net_path
        self.train_data = train_data
        self.test_data = test_data

    def run(self):
        try:
            PSOSearch.pso_search(self.dataset_name, self.is_k_fold, self.is_test, self.num_iter, self.num_point, self.c1, self.c2, self.w_low, self.w_high, self.num_extra, self.basic_params, self.hyper_dict, self.net_path, mustInt_list, self.train_data, self.test_data)
        except FileNotFoundError:
            self.trigger.emit(1)
        except RuntimeError:
            self.trigger.emit(2)
        else:
            self.trigger.emit(0)