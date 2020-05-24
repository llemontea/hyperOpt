import random
import train_net
import numpy as np
import pymysql
import csv
import global_variable

class PSOModel(object):
    '''
    particle_num(int):粒子群的粒子数量.
    particle_dim(int):粒子群所在空间的维度.等于待优化的超参数个数.
    iter_num(int):最大迭代次数.
    c1(float):局部学习因子,表示粒子向该粒子的最优历史位置(pbest)移动的加速项的权重.
    c2(float):全局学习因子,表示粒子向所有粒子的最优历史位置(gbest)移动的加速项的权重.
    w(float):惯性因子,表示粒子之前运动方向在本次方向上的惯性大小.
    particle_limit(list):超参数取值范围.
    '''
    def __init__(self, is_k_fold, is_test, particle_num, particle_dim, iter_num, c1, c2, extra_num, key, particle_limit, basic_params, path, train_data, test_data, mustInt_list):
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.particle_num = particle_num
        self.particle_dim = particle_dim
        self.iter_num = iter_num
        self.c1 = c1  # 通常设为2.0
        self.c2 = c2  # 通常设为2.0
        self.extra_num = extra_num
        self.key = key
        self.particle_limit = particle_limit
        self.basic_params = basic_params
        self.path = path
        self.train_data = train_data
        self.test_data = test_data
        self.mustInt_list = mustInt_list

        self.result = []

    @property
    def res(self):
        return self.result

    '''记录历史计算信息.'''
    def register(self, hyper_dic, target):
        res_dic = {}
        res_dic['target'] = target
        res_dic['params'] = hyper_dic
        self.res.append(res_dic)

    '''四舍五入,将浮点数转化为整数.'''
    def rounds(self, number):
        str_number = str(number)
        index = str_number.find('.')

        if int(str_number[index + 1]) < 5:
            return int(str_number[:index])
        else:
            return int(str_number[:index]) + 1

    '''
    粒子群初始化.
    注意初始化两个内容:一个是位置,一个是速度.
    位置是有限制的:位置的各个维度对应了各个超参数,所以必须位于超参数的范围内.
    '''
    def swarm_origin(self):
        particle_x = []
        particle_v = []

        # 每一个粒子包含一个位置值和一个速度值.一共particle_num个粒子.
        for i in range(self.particle_num):
            temp_1 = []
            temp_2 = []
            # 粒子所处的空间是n维的,则它的位置和速度也都是n维的.n表示待优化超参数个数.
            for j in range(self.particle_dim):
                x = random.random()
                v = random.random()

                # random.random()获取一个[0,1)范围内的随机值,然后根据超参数的取值上下限映射到指定范围内.
                # 如果超参数取值要求是整数,则用四舍五入将其转换为整数.
                x = x * (self.particle_limit[j][1] - self.particle_limit[j][0]) + self.particle_limit[j][0]
                if self.key[j] in self.mustInt_list:
                    x = self.rounds(x)

                temp_1.append(x)
                temp_2.append(v)

            particle_x.append(temp_1)
            particle_v.append(temp_2)

        return particle_x, particle_v

    '''
    添加额外的随机粒子.
    这会导致self.particle_num的值发生变化.
    '''
    def add_extra(self):
        extra_x = []
        extra_v = []

        # 每一个粒子包含一个位置值和一个速度值.一共particle_num个粒子.
        for i in range(self.extra_num):
            temp_1 = []
            temp_2 = []
            # 粒子所处的空间是n维的,则它的位置和速度也都是n维的.n表示待优化超参数个数.
            for j in range(self.particle_dim):
                x = random.random()
                v = random.random()

                # random.random()获取一个[0,1)范围内的随机值,然后根据超参数的取值上下限映射到指定范围内.
                # 如果超参数取值要求是整数,则用四舍五入将其转换为整数.
                x = x * (self.particle_limit[j][1] - self.particle_limit[j][0]) + self.particle_limit[j][0]
                if self.key[j] in self.mustInt_list:
                    x = self.rounds(x)

                temp_1.append(x)
                temp_2.append(v)

            extra_x.append(temp_1)
            extra_v.append(temp_2)

        return extra_x, extra_v

    '''
    计算适应度函数值,初始化pbest和gbest.
    粒子的位置就是各个待优化超参数的取值,所以需要把particle_x的各个值取出来,用适应度函数去求.
    '''
    def fitness(self, particle_x):
        fitness_value = []

        # 每个粒子的位置对应的是一组超参数取值.
        for i in range(self.particle_num):
            # 取出超参数,代入到机器学习模型中计算出准确率.
            params = dict(zip(self.key, particle_x[i]))
            for j, key in enumerate(self.key):
                self.basic_params[key] = particle_x[i][j]
            print('self.basic_params:', self.basic_params)

            Tr = train_net.Train(self.train_data, self.test_data, self.is_k_fold, self.is_test, self.path, self.basic_params)

            fitness = Tr.train()
            fitness_value.append(fitness)

            global_variable.test_acc.append(fitness)
            if len(global_variable.best_acc) == 0 or global_variable.best_acc[-1] < fitness:
                global_variable.best_acc.append(fitness)
                global_variable.best_param = self.basic_params.copy()
            else:
                temp_best_acc = global_variable.best_acc[-1]
                global_variable.best_acc.append(temp_best_acc)

            # 将每一个超参数组合的计算结果存入历史信息.
            self.register(params, fitness)

        # 当前粒子群最优适应度函数值和对应的参数.
        current_fitness = 0.0
        current_parameter = []

        for i in range(self.particle_num):
            if current_fitness < fitness_value[i]:
                current_fitness = fitness_value[i]
                current_parameter = particle_x[i]

        # 返回的是当前迭代中,各个粒子的适应度,和这些粒子中适应度最好的那个.
        return fitness_value, current_fitness, current_parameter

    '''
    粒子位置更新:
    v=ω×v+c1×rand()×(pbest-x)+c2×rand()×(gbest−x)
    x+=v
    注意gbest是全局最优值,只有一个;而pbest是各个粒子的历史最优值,每个粒子各有一个.
    这里x和v都是一个向量,长度=particle_dim.
    '''
    def update(self, particle_x, particle_v, gbest_parameter, pbest_parameters, w):
        for i in range(self.particle_num):
            # a1:particle_v的记忆项.
            a1 = [x * w for x in particle_v[i]]
            # a2:particle_v的自身认知项.
            a2 = [y * self.c1 * random.random() for y in list(np.array(pbest_parameters[i]) - np.array(particle_x[i]))]
            # a3:particle_v的群体认知项.
            a3 = [z * self.c2 * random.random() for z in list(np.array(gbest_parameter) - np.array(particle_x[i]))]

            particle_v[i] = list((np.array(a1) + np.array(a2) + np.array(a3)))

            for j in range(len(particle_v[i])):
                # 把取值上下限差值的2/3作为速度的上下限.超过上下限则截断之.速度限制在前几代迭代中作用比较明显,后期随着粒子收敛,速度也不会超限了.
                vMax = (self.particle_limit[j][1] - self.particle_limit[j][0]) * 2 / 3
                if particle_v[i][j] > vMax:
                    print("too fast!")
                    particle_v[i][j] = vMax
                elif particle_v[i][j] < -vMax:
                    print("too slow!")
                    particle_v[i][j] = -vMax

            particle_x[i] = list(np.array(particle_x[i]) + np.array(particle_v[i]))

        # 将更新后的粒子位置固定在指定范围内.另一种约束方式是设置最大值边界,保证取值更新后不越界.
        # 这个方法有一个最大的问题在于,它是影响到所有粒子的,无论粒子是不是超出了指定范围,都会在这一步骤中进行更新.
        parameter_list = []
        for i in range(self.particle_dim):
            temp = []
            for j in range(self.particle_num):
                # particle_x[j][i]是第i个超参数的第j个取值.
                # 所以temp每次得到的是某一个超参数的全部取值.
                temp.append(particle_x[j][i])
            parameter_list.append(temp)

        value = []
        for i in range(self.particle_dim):
            temp = []
            # temp每次获得某一个超参数的最大值和最小值.(按照要求,值应该位于超参数取值范围内)
            temp.append(max(parameter_list[i]))
            temp.append(min(parameter_list[i]))
            # value[i][1]是第i个超参数的最小值,value[i][0]是第i个超参数的最大值.
            value.append(temp)

        for i in range(self.particle_num):
            for j in range(self.particle_dim):
                if value[j][0] != value[j][1]:
                    if particle_x[i][j] > self.particle_limit[j][1] or particle_x[i][j] < self.particle_limit[j][0]:
                        print("这个粒子需要调整.")
                        # 调整粒子位置,保证它位于超参数取值范围内.
                        particle_x[i][j] = (particle_x[i][j] - value[j][1]) / (value[j][0] - value[j][1]) * (self.particle_limit[j][1] - self.particle_limit[j][0]) + self.particle_limit[j][0]
                        if self.key[j] in self.mustInt_list:
                            particle_x[i][j] = self.rounds(particle_x[i][j])

        # 每次随机新增几个粒子,增加算法的随机性.
        extra_x, extra_v = self.add_extra()
        particle_x += extra_x
        particle_v += extra_v
        self.particle_num += self.extra_num

        return particle_x, particle_v

def pso_search(dataset_name, is_k_fold, is_test, count_iter, count_point, c1, c2, w_low, w_high, extra_num, basic_params, hyperParams_dict, path, mustInt_list, train_data, test_data):
    init_global_variable()
    particle_dim = len(hyperParams_dict)
    key = list(hyperParams_dict.keys())
    particle_limit = list(hyperParams_dict.values())

    # 计算每次迭代使用的惯性因子值.
    new_w = []
    for i in range(count_iter):
        new_w.append((w_high - w_low) * (count_iter - i) / count_iter + w_low)

    psoModel = PSOModel(is_k_fold, is_test, count_point, particle_dim, count_iter, c1, c2, extra_num, key, particle_limit, basic_params, path, train_data, test_data, mustInt_list)

    # best_params=None这里不需要,因为gbest_parameter就是best_params.
    best_fitness = 0.0
    best_acc_history_pso = []
    test_acc_history_pso = []
    best_acc_history = []
    test_acc_history = []

    # 初始化particle_x和particle_v.
    particle_x, particle_v = psoModel.swarm_origin()

    # 初始化gbest_parameter.
    gbest_parameter = []
    for i in range(psoModel.particle_dim):
        gbest_parameter.append(0.0)

    # 初始化pbest_parameters.
    pbest_parameters = []
    for i in range(psoModel.particle_num):
        temp = []
        for j in range(psoModel.particle_dim):
            temp.append(0.0)
        pbest_parameters.append(temp)

    # 初始化fitness_value.
    fitness_value = []
    for i in range(psoModel.particle_num):
        fitness_value.append(0.0)

    for i in range(psoModel.iter_num):
        # 计算当前各个粒子的适应度,这一批次粒子的最佳适应度和最佳适应度对应的粒子位置.
        current_fitness_value, current_best_fitness, current_best_parameter = psoModel.fitness(particle_x)

        # 更新pbest_parameters.
        for j in range(psoModel.particle_num):
            if current_fitness_value[j] > fitness_value[j]:
                pbest_parameters[j] = particle_x[j]

        # 更新gbest_parameter和对应的best_fitness.
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            gbest_parameter = current_best_parameter

        best_acc_history_pso.append(best_fitness)
        test_acc_history_pso.append(current_best_fitness)

        fitness_value = current_fitness_value

        w = new_w[i]
        particle_x, particle_v = psoModel.update(particle_x, particle_v, gbest_parameter, pbest_parameters, w)

        # 每次迭代后会导致particle_num的变化,所以gbest,pbest和fitness_value的长度相应的也要变化.
        for i in range(psoModel.particle_num - len(pbest_parameters)):
            temp = []
            for j in range(psoModel.particle_dim):
                temp.append(0.0)
            pbest_parameters.append(temp)

        for i in range(psoModel.particle_num - len(fitness_value)):
            fitness_value.append(0.0)

    global_variable.test_over = True
    global_variable.best_over = True
    global_variable.path = None

    best_target = 0.0
    for i, r in enumerate(psoModel.res):
        print('Iteration {}: \n\t{}'.format(i + 1, r))

        test_acc_history.append(r['target'])
        if r['target'] > best_target:
            best_target = r['target']
        best_acc_history.append(best_target)

    path_csv = 'result_csv/result_' + str(global_variable.num_opt) + '.csv'
    csvFile = open(path_csv, 'w', newline='')
    try:
        writer = csv.writer(csvFile)
        writer.writerow(('number_iter', 'hyper_parameters', 'test_accuracy'))
        for i, r in enumerate(psoModel.res):
            writer.writerow((i + 1, r['params'], r['target']))
    finally:
        csvFile.close()

    best_param = basic_params.copy()
    for k in key:
        best_param[k] = (dict(zip(key, gbest_parameter)))[k]

    updateDatabase(dataset_name, best_param, best_fitness)
    global_variable.after_create = True

    return dict(zip(key, gbest_parameter)), best_fitness

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

    sql = "insert into opthistory (id, dataset, optimization, best_param, best_acc, testFig, bestFig, result) values (" + str(global_variable.num_opt) +", '" + dataset_name + "', '粒子群算法', \"" + str(best_param) + "\", " + str(best_acc) + ", 'None', 'None', '" + result + "');"
    print(sql)
    cursor.execute(sql)
    connection.commit()

    cursor.close()
    connection.close()