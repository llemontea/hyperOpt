import global_variable
import numpy as np
import train_net
import pymysql
import copy
import random
import math
import csv

'''
染色体(个体):一个染色体对应一个超参数.染色体的十进制数值表示的是超参数的实际取值.
基因:每一个染色体包含多个基因.基因的取值长度即为染色体的长度.遗传算法的交叉,变异都是针对基因进行的.
种群:初始化染色体的取值范围.
适应度函数:表征每一组染色体(每一组超参数)对应的模型评价指标.(如k折交叉验证的平均值,可以作为适应度函数值)

比如,假设两个超参数的寻优,设染色体长度为20,种群数为200.
那么就是:初始化两个染色体,每个染色体初始化200个随机取值,每个染色体的十进制取值用20位二进制数表示.
'''
class GeneticModel(object):
    '''
    population_size(int):种群数.=len(population[0])
    x_num(int):染色体数.对应需要寻优的超参数个数.=len(population)
    x_length(int):染色体的基因长度.=len(population[0][0])
    iter_num(int):迭代次数.
    pc(float):交叉概率阈值.(0<pc<1)
    pm(float):变异概率阈值.(0<pm<1)
    '''
    def __init__(self, is_k_fold, is_test, population_size, x_num, x_length, x_limit, x_key, iter_num, pc, pm, basic_params, path, train_data, test_data, mustInt_list):
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        self.population_size = population_size
        self.x_num = x_num
        self.x_length = x_length
        self.x_limit = x_limit
        self.x_key = x_key
        self.iter_num = iter_num
        self.pc = pc
        self.pm = pm
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

    '''
    初始化种群和染色体.
    种群是一个list,其中的元素是染色体.
    每个染色体也是一个list,其中的元素是染色体的一个随机取值,是二进制形式的.
    '''
    def prime_species(self):
        population = []

        for i in range(self.x_num):
            # temp_1:一个染色体的所有可能二进制编码.
            temp_1 = []
            for j in range(self.population_size):
                # temp_2:染色体的一种二进制编码.
                temp_2 = []
                for k in range(self.x_length):
                    temp_2.append(random.randint(0, 1))
                temp_1.append(temp_2)
            population.append(temp_1)

        return population

    '''
    计算染色体的二进制编码对应的十进制数.
    population[]:取染色体.
    population[][]:取染色体的一个随机二进制编码值.
    population[][][]:取染色体的一个随机二进制编码值的某一位.
    '''
    def translation(self, population):
        population_decimalism = []

        for i in range(self.x_num):
            temp = []
            for j in range(self.population_size):
                total = 0.0
                for k in range(self.x_length):
                    # 二进制转十进制.
                    total += population[i][j][k] * (math.pow(2, k))
                temp.append(total)
            population_decimalism.append(temp)

        return population_decimalism

    '''四舍五入,将浮点数转化为整数.'''
    def rounds(self, number):
        str_number = str(number)
        index = str_number.find('.')

        if int(str_number[index + 1]) < 5:
            return int(str_number[:index])
        else:
            return int(str_number[:index]) + 1

    '''计算每一组染色体对应的适应度函数值'''
    def fitness(self, population):
        fitness = []
        # 计算超参数二进制编码对应的十进制数值.
        population_decimalism = self.translation(population)

        for i in range(self.population_size):
            temp = []
            for j in range(self.x_num):
                # 注意循环内外的先后顺序.population_decimalism[j][i]是第j个染色体的第i个随机取值.
                # 所以内层循环取的是所有染色体的随机值.所以temp实际上得到了一组超参数取值.
                # 这里需要注意:十进制数值的范围是[0,2^x_length].
                # 然后需要用乘除法和加减法等操作映射到超参数应该有的取值区间内.
                multi = self.x_limit[j][1] - self.x_limit[j][0]
                add = self.x_limit[j][0]
                value = population_decimalism[j][i] / (math.pow(2, self.x_length) / multi) + add
                if self.x_key[j] in self.mustInt_list:
                    value = self.rounds(value)
                temp.append(value)

            # 防止超参数值为非法值(如零).如果非法,则设为取值范围的中值.(注意整数必须用int()强制取整)
            for j in range(len(temp)):
                if self.x_key[j] in self.mustInt_list:
                    if temp[j] == 0:
                        temp[j] = int((self.x_limit[j][1] - self.x_limit[j][0]) / 2)
                else:
                    if temp[j] == 0.0:
                        temp[j] = (self.x_limit[j][1] - self.x_limit[j][0]) / 2

            params = dict(zip(self.x_key, temp))
            for i, key in enumerate(self.x_key):
                self.basic_params[key] = temp[i]
            print('basic_params:', self.basic_params)

            Tr = train_net.Train(self.train_data, self.test_data, self.is_k_fold, self.is_test, self.path, self.basic_params)

            target_result = Tr.train()
            fitness.append(target_result)

            global_variable.test_acc.append(target_result)
            if len(global_variable.best_acc) == 0 or global_variable.best_acc[-1] < target_result:
                global_variable.best_acc.append(target_result)
                global_variable.best_param = self.basic_params.copy()
            else:
                temp_best_acc = global_variable.best_acc[-1]
                global_variable.best_acc.append(temp_best_acc)

            self.register(params, target_result)

        return fitness

    '''适应度求和'''
    def sum_value(self, fitness_value):
        total = 0.0

        for i in range(len(fitness_value)):
            total += fitness_value[i]

        return total

    '''
    重组fitness内容.
    fitness[最后]=fitness[0]+...+fitness[最后]
    fitness[最后-1]=fitness[0]+...+fitness[最后-1]
    fitness[最后-2]=fitness[0]+...+fitness[最后-2]
    ............
    fitness[2]=fitness[0]+fitness[1]+fitness[2]
    fitness[1]=fitness[0]+fitness[1]
    fitness[0]=fitness[0]
    这也是为什么要对原fitness进行倒序遍历的原因,正序遍历就会发生前后覆盖.
    '''
    def cumsum(self, fitness):
        # range(len(fitness)-1,-1,-1)实现的是倒序索引.
        for i in range(len(fitness) - 1, -1, -1):
            total = 0.0

            j = 0
            while j <= i:
                total += fitness[j]
                j += 1

            fitness[i] = total

    '''
    选择操作:选择留下后代的个体.
    按照原始的轮盘赌规则,最高适应度的个体也未必能存活,因为是根据概率的.
    这里修改了一下,在轮盘赌结束后,手动用当前种群中最优的个体替换掉选出来的个体中最差的那个.
    population是原始的01二进制编码个体集合,population[]为待优化超参数数,population[][]是第x个超参数的全编码,population[][][]是第x个超参数的第y位编码(0或1).
    '''
    def selection(self, population, fitness_value):
        new_fitness = []
        total_fitness = self.sum_value(fitness_value)

        # 计算各个适应度占适应度之和的比例.
        for i in range(len(fitness_value)):
            new_fitness.append(fitness_value[i] / total_fitness)

        # 重组适应度数组.由于浮点计算可能出现问题,所以强制令最后一个值为1.0.
        self.cumsum(new_fitness)
        new_fitness[-1] = 1.0 # 有时候太精细的小数加法会导致最后加和不等于1.0,所以强制改一下.

        new_population = copy.deepcopy(population)
        new_in = 0

        # 最佳适应度个体的下标:从父代个体里面选.
        best_param = np.argmax(fitness_value)

        # i:共有i个超参数组合(种群个体数).但是有x_num个待优化超参数.
        for i in range(self.population_size):
            # 随机生成一个0~1之间的数.看它落在new_fitness的哪个区间内,就选择哪个.
            # 这是模拟轮盘赌的操作.区间更长的更容易被选中.允许重复选,所以理想情况下适应度高的染色体值会越来越多.
            index = random.uniform(0, 1)
            # j:共产生了j个不同的结果.(不同超参数组合的对应结果)
            for j in range(len(new_fitness)):
                # 找到落在哪个区间.
                if new_fitness[j] > index:
                    # 注意超参数可能不止一个,所以在选中的时候要把所有的超参数一块捞过来.
                    # k:共有k个超参数.
                    for k in range(self.x_num):
                        # new_population[k][new_in]是第k个超参数的第new_in个取值.最内层循环会得到这个超参数组合的所有超参数取值.
                        new_population[k][new_in] = population[k][j]

                    new_in += 1
                    break

        return best_param, new_population

    '''交叉操作'''
    def crossover(self, population):
        pop_len = self.population_size

        for i in range(len(population)):
            for j in range(pop_len - 1):
                # 如果随机生成数不超过交叉概率阈值,则进行交叉.
                if random.random() < self.pc:
                    # 从染色体编码上机选择一个交叉位置.
                    cpoint = random.randint(0, len(population[i][j]))

                    temp_1 = []
                    temp_2 = []

                    temp_1.extend(population[i][j][0:cpoint])
                    temp_1.extend(population[i][j + 1][cpoint:len(population[i][j])])

                    temp_2.extend(population[i][j + 1][0:cpoint])
                    temp_2.extend(population[i][j][cpoint:len(population[i][j])])

                    population[i][j] = temp_1
                    population[i][j + 1] = temp_2

    '''变异操作'''
    def mutation(self, population):
        pop_len = self.population_size
        gene_len = self.x_length

        for i in range(len(population)):
            for j in range(pop_len):
                if random.random() < self.pm:
                    mpoint = random.randint(0, gene_len - 1)

                    if population[i][j][mpoint] == 1:
                        population[i][j][mpoint] = 0
                    else:
                        population[i][j][mpoint] = 1

    '''
    替换操作:原本是打算让最优个体不经过交叉和变异,替换掉种群中最差个体直接保存到下一代,但是经过交叉和变异之后,种群中的个体已经翻新了.
    也就是说在这个全新的种群里面,有些新个体的表现是好是坏并不知道.这就没法去找"最差"的个体了.所以这个地方随机选一个新种群中的个体替换掉.
    '''
    def replace(self, best_param, population, origin_population):
        index = random.randint(0, self.population_size - 1)
        for i in range(len(population)):
            population[i][index] = origin_population[i][best_param]

    '''微调操作:后期'''
    def fine_turning(self, population):
        for i in range(self.x_num):
            for j in range(self.population_size):
                # 微调范围仅限于后三位,在原数的+7/-7范围内.(改成4的话就是+15/-15)
                for k in range(3):
                    population[i][j][k] = random.randint(0, 1)

    '''找出当前种群中最佳的适应度个体和其对应的超参数取值'''
    def best(self, population_decimalism, fitness_value):
        # pop_len是每个超参数取值的个数,也就是超参数组合的个数.
        pop_len = len(population_decimalism[0])
        best_params = []
        best_fitness = 0.0

        for i in range(0, pop_len):
            temp = []
            if fitness_value[i] > best_fitness:
                best_fitness = fitness_value[i]

                # len(population_decimalism)是超参数的个数,也就是超参数组合的长度.
                for j in range(len(population_decimalism)):
                    multi = self.x_limit[j][1] - self.x_limit[j][0]
                    add = self.x_limit[j][0]
                    value = population_decimalism[j][i] / (math.pow(2, self.x_length) / multi) + add
                    if self.x_key[j] in self.mustInt_list:
                        value = self.rounds(value)
                    temp.append(value)
                best_params = temp

        return best_params, best_fitness

def genetic_search(dataset_name, is_k_fold, is_test, count_iter, count_population, pc, pm, code_length, basic_params, hyperParams_dict, path, mustInt_list, train_data, test_data):
    init_global_variable()
    x_num = len(hyperParams_dict)
    x_length = code_length
    x_limit = []
    for key in hyperParams_dict.keys():
        x_limit.append(hyperParams_dict[key])
    x_key = list(hyperParams_dict.keys())

    geneticModel = GeneticModel(is_k_fold, is_test, count_population, x_num, x_length, x_limit, x_key, count_iter, pc, pm, basic_params, path, train_data, test_data, mustInt_list)

    best_params = None
    best_fitness = 0.0
    best_acc_history_population = []
    test_acc_history_population = []
    best_acc_history = []
    test_acc_history = []

    # 初始化种群.得到population_size个01串,即超参数取值的二进制编码.
    population = geneticModel.prime_species()
    print(population)
    for i in range(geneticModel.iter_num):
        # 计算适应度函数数值列表.这一步已经完成了超参数组合对应函数值的计算.
        fitness_value = geneticModel.fitness(population)

        # 计算当前种群每个染色体的十进制取值.这里得到的十进制取值尚未映射到指定的取值范围内.
        population_decimalism = geneticModel.translation(population)

        # 寻找当前种群最佳的超参数组合和最优的适应度函数值.
        current_params, current_fitness = geneticModel.best(population_decimalism, fitness_value)

        # 每次迭代找到了当前迭代的最优解和最优值,都要看看是否要更新全局最优解和全局最优值.
        if current_fitness > best_fitness:
            best_fitness = current_fitness
            best_params = current_params

        best_acc_history_population.append(best_fitness)
        test_acc_history_population.append(current_fitness)

        # 种群更新:选择,交叉与变异
        origin_population = copy.deepcopy(population) # 存一个原始的种群.把list类型传参是作为引用传参的,population会随之改变.
        best_param, population = geneticModel.selection(population, fitness_value)
        geneticModel.crossover(population)
        geneticModel.mutation(population)
        geneticModel.replace(best_param, population, origin_population)
        geneticModel.fine_turning(population)

    global_variable.test_over = True
    global_variable.best_over = True
    global_variable.path = None

    best_target = 0.0
    for i, r in enumerate(geneticModel.res):
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
        for i, r in enumerate(geneticModel.res):
            writer.writerow((i + 1, r['params'], r['target']))
    finally:
        csvFile.close()

    best_param = basic_params.copy()
    for key in x_key:
        best_param[key] = (dict(zip(x_key, best_params)))[key]

    updateDatabase(dataset_name, best_param, best_fitness)
    global_variable.after_create = True

    return dict(zip(x_key, best_params)), best_fitness

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

    sql = "insert into opthistory (id, dataset, optimization, best_param, best_acc, testFig, bestFig, result) values (" + str(global_variable.num_opt) +", '" + dataset_name + "', '遗传算法', \"" + str(best_param) + "\", " + str(best_acc) + ", 'None', 'None', '" + result + "');"
    print(sql)
    cursor.execute(sql)
    connection.commit()

    cursor.close()
    connection.close()