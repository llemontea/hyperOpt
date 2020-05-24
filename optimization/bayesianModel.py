from optimization.bayes_opt import bayesian_optimization
import global_variable
import pymysql
import random
import csv

def bayesian_search(dataset_name, is_k_fold, is_test, init_points, n_iter, acq, kappa, xi, basic_params, hyper_dict, path, mustInt_list, train_data, test_data):
    init_global_variable()
    optimizer = bayesian_optimization.BayesianModel(
        path=path,
        is_k_fold=is_k_fold,
        is_test=is_test,
        train_data=train_data,
        test_data=test_data,
        pbounds=hyper_dict,
        mustInt_parameters=mustInt_list,
        random_state=random.randint(0, 100)
    )

    optimizer.maximize(basic_params, init_points=init_points, n_iter=n_iter, acq=acq, kappa=kappa, xi=xi)
    global_variable.test_over = True
    global_variable.best_over = True
    global_variable.path = None

    result = optimizer.max

    for i, r in enumerate(optimizer.res):
        print('Iteration {}: \n\t{}'.format(i + 1, r))

    path_csv = 'result_csv/result_' + str(global_variable.num_opt) + '.csv'
    csvFile = open(path_csv, 'w', newline='')
    try:
        writer = csv.writer(csvFile)
        writer.writerow(('number_iter', 'hyper_parameters', 'test_accuracy'))
        for i, r in enumerate(optimizer.res):
            writer.writerow((i + 1, r['params'], r['target']))
    finally:
        csvFile.close()

    best_param = basic_params.copy()
    for key in result['params'].keys():
        best_param[key] = result['params'][key]

    updateDatabase(dataset_name, best_param, result['target'])
    global_variable.after_create = True

    return result['params'], result['target']

def init_global_variable():
    global_variable.test_acc = []
    global_variable.best_acc = []
    global_variable.best_param = None

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

    sql = "insert into opthistory (id, dataset, optimization, best_param, best_acc, testFig, bestFig, result) values (" + str(global_variable.num_opt) +", '" + dataset_name + "', '贝叶斯优化', \"" + str(best_param) + "\", " + str(best_acc) + ", 'None', 'None', '" + result + "');"
    print(sql)
    cursor.execute(sql)
    connection.commit()

    cursor.close()
    connection.close()