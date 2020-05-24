from itertools import product as product
import global_variable
import pymysql
import train_net
import csv

# 根据提供的超参数的取值范围,步长进行网格搜索.
class GridModel(object):
    def __init__(self, is_k_fold, is_test, path, basic_params, hyperparameters, combinations, train_data, test_data):
        self.is_k_fold = is_k_fold
        self.is_test = is_test

        self.path = path
        self.train_data = train_data
        self.test_data = test_data

        # 超参数名称列表和超参数组合列表.
        self.basic_params = basic_params
        self.hyperparameters = hyperparameters
        self.combinations = combinations

        self.result = []

    @property
    def res(self):
        return self.result

    def register(self, hyper_dic, target):
        res_dic = {}
        res_dic['target'] = target
        res_dic['params'] = hyper_dic
        self.res.append(res_dic)

    # 网络模型训练.
    def train(self):
        best_combination = None
        best_test_acc = 0.0
        best_acc_history = []
        test_acc_history = []

        for combination in self.combinations:
            params = dict(zip(self.hyperparameters, combination))
            for i, key in enumerate(self.hyperparameters):
                self.basic_params[key] = combination[i]
            print(self.basic_params)

            Tr = train_net.Train(self.train_data, self.test_data, self.is_k_fold, self.is_test, self.path, self.basic_params)
            test_acc = Tr.train()

            test_acc_history.append(test_acc)
            global_variable.test_acc.append(test_acc)
            if test_acc > best_test_acc:
                best_test_acc = test_acc
                best_combination = self.basic_params.copy()
                global_variable.best_param = best_combination
            global_variable.best_acc.append(best_test_acc)
            best_acc_history.append(best_test_acc)

            self.register(params, test_acc)

        return best_combination, best_test_acc, best_acc_history, test_acc_history

# 获取超参数名称.
def get_hyperparameter(hyperParams_dict):
    return hyperParams_dict.keys()

def get_values(hyperParams_dict):
    values = []

    for value in hyperParams_dict.values():
        assert value[0] <= value[1]

        fix_value = []
        step_value = value[0]

        while step_value <= value[1]:
            fix_value.append(step_value)
            step_value += value[2]
        values.append(fix_value)

    return (item for item in values)

# 获取全部的超参数组合.
def get_combinations(hyperParams_dict):
    values = get_values(hyperParams_dict)
    return product(*values)

# hyperParams_dict是超参数字典,键是超参数名称,值是列表[a,b,c],a和b表示取值上下限,c表示步长.
def grid_search(dataset_name, is_k_fold, is_test, basic_params, hyperParams_dict, path, train_data, test_data):
    init_global_variable()
    hyperparameters = get_hyperparameter(hyperParams_dict)
    combinations = list(get_combinations(hyperParams_dict))

    gridModel = GridModel(is_k_fold, is_test, path, basic_params, hyperparameters, combinations, train_data, test_data)

    best_combination, best_test_acc, best_acc_history, test_acc_history = gridModel.train()
    global_variable.test_over = True
    global_variable.best_over = True
    global_variable.path = None

    for i, r in enumerate(gridModel.res):
        print('Iteration {}: \n\t{}'.format(i + 1, r))

    path_csv = 'result_csv/result_' + str(global_variable.num_opt) + '.csv'
    csvFile = open(path_csv, 'w', newline='')
    try:
        writer = csv.writer(csvFile)
        writer.writerow(('number_iter', 'hyper_parameters', 'test_accuracy'))
        for i, r in enumerate(gridModel.res):
            writer.writerow((i + 1, r['params'], r['target']))
    finally:
        csvFile.close()

    updateDatabase(dataset_name, best_combination, best_test_acc)
    global_variable.after_create = True

    return best_combination, best_test_acc

def init_global_variable():
    global_variable.test_acc = []
    global_variable.best_acc = []
    global_variable.best_param = None
    global_variable.axv = []

def updateDatabase(dataset_name, best_param, best_acc):
    connection = pymysql.connect(
        host=global_variable.host,
        user=global_variable.user,
        password=global_variable.password,
        database='opt',
        charset='utf8'
    )
    cursor = connection.cursor()
    result = '../result_csv/result_' + str(global_variable.num_opt) + '.csv'

    sql = "insert into opthistory (id, dataset, optimization, best_param, best_acc, testFig, bestFig, result) values (" + str(global_variable.num_opt) +", '" + dataset_name + "', '网格搜索', \"" + str(best_param) + "\", " + str(best_acc) + ", 'None', 'None', '" + result + "');"
    print(sql)
    cursor.execute(sql)
    connection.commit()

    cursor.close()
    connection.close()