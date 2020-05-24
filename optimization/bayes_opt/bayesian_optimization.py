import warnings
from .target_space import TargetSpace
from .util import UtilityFunction, acq_max, ensure_rng
from sklearn.gaussian_process.kernels import Matern
from sklearn.gaussian_process import GaussianProcessRegressor

# 队列.本质上是list,相关的操作都是list的操作.
class Queue:
    def __init__(self):
        self._queue = []

    @property
    def empty(self):
        return len(self) == 0

    def __len__(self):
        return len(self._queue)

    def __next__(self):
        # 如果队列为空,无法进行遍历.
        if self.empty:
            raise StopIteration("队列已空,无法继续遍历.")

        # 每次迭代取出队首的元素,然后移除之.这样可以保证每次调用__next__()都往前推一步.
        obj = self._queue[0]
        self._queue = self._queue[1:]
        return obj

    def next(self):
        return self.__next__()

    def add(self, obj):
        self._queue.append(obj)


class BayesianModel():
    '''
    path:神经网络模型结构存储路径,调用load(path)即可获取模型.
    train_data:训练集.dataset类型.
    test_data:测试集.dataset类型.
    pbounds:字典.键指出所有需要优化的超参数,值给出这个超参数的取值范围.
    random_state:随机数发生器.
    '''

    def __init__(self, path, is_k_fold, is_test, train_data, test_data, pbounds, mustInt_parameters, random_state=None):
        # 获取随机数发生器.
        self._random_state = ensure_rng(random_state)

        # 数据结构.包含了获取数据集的函数,超参数及取值范围,以及所有的历史记录.
        self._space = TargetSpace(path, is_k_fold, is_test, train_data, test_data, pbounds, mustInt_parameters, random_state)

        # 队列.
        self._queue = Queue()

        # 定义高斯过程.
        self._gp = GaussianProcessRegressor(
            # 核函数.参数为核函数的超参数取值.这些超参数在拟合过程中会自动优化.
            kernel=Matern(nu=2.5),
            # 在拟合期间将值添加到核矩阵的对角线.确保计算值形成正定矩阵,防止潜在的数值问题.
            alpha=1e-6,
            # 目标值y是否被归一化.如果预期目标值的均值和零相差较大,建议设为True.
            normalize_y=True,
            # 优化程序重新启动的次数.
            n_restarts_optimizer=5,
            # 用于初始化的生成器,即上面得到的随机数生成器.
            random_state=self._random_state,
        )

        self._list = mustInt_parameters

    # @property的作用是将类函数转换为类属性,直接像使用类属性一样使用.
    @property
    def space(self):
        return self._space

    @property
    def max(self):
        # 取优化过程中的最大值.
        return self._space.max()

    @property
    def res(self):
        # 取优化的全历史纪录.
        return self._space.res()

    def register(self, params, target):
        # _space.register()将新计算值添加到历史记录中.
        self._space.register(params, target)

    '''下一步最有可能取得最优值的点.'''
    def suggest(self, utility_function):
        if len(self._space) == 0:
            # 如果_space为空,则用.random_sample()在范围内创建随机点.
            return self._space.array_to_params(self._space.random_sample())

        # sklearn的GP会产生大量的warning,这里将它们全部屏蔽掉.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._gp.fit(self._space.params, self._space.target)

        # 查找acquisition function可能取得最大值的数值点.
        suggestion = acq_max(
            ac=utility_function.utility,
            gp=self._gp,
            # _space.target.max(),从target(所有的数据点的历史函数值)中选出最值.
            y_max=self._space.target.max(),
            bounds=self._space.bounds,
            random_state=self._random_state
        )

        return self._space.array_to_params(suggestion)

    """
    确保队列在最开始的时候就包含元素(非空).
    给定init_points值,也就是事先往队列中填充的元素个数.填充的都是随机数.
    """
    def prime_queue(self, init_points):
        if self._queue.empty and self._space.empty:
            init_points = max(init_points, 1)

        for _ in range(init_points):
            self._queue.add(self._space.random_sample())

    # 最大化函数值.
    def maximize(self, basic_params, init_points=5, n_iter=25, acq = None, kappa = None, xi = None):
        self.prime_queue(init_points)

        # 获取acquisition function.
        util = UtilityFunction(kind = acq, kappa = kappa, xi = xi)
        iteration = 0

        # 如果队列非空,或迭代数<n_iter,就仍在循环体内.
        while not self._queue.empty or iteration < n_iter:
            # 尝试取队列的队首元素值.
            try:
                x_probe = next(self._queue)
            # 如果next无效,即队列已空,但仍在循环体内,说明iteration<n_iter.
            except StopIteration:
                x_probe = self.suggest(util)
                iteration += 1
            self._space.probe(x_probe, basic_params)