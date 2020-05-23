import warnings
import numpy as np

from scipy.stats import norm
from scipy.optimize import minimize

'''
寻找acquisition function的最大值.
方法是随机采样n_warmup(1e5)个随机点,然后从n_iter(100)个随机起点出发,运行L-BFGS-B.
L-BFGS-B是牛顿法的一种变种,是一种最优化的手段,给定一个出发点,通过数次迭代寻找最优.
acquistion function可以看作一个一元函数,自变量是超参数的一个组合.
----------
ac:acquisition function.
gp:拟合相关数据的高斯过程.
y_max:目标函数的当前已知最大值.
bounds:参数边界值,限制acquisition function的搜索.
random_state:np.RandomState随机数生成器的实例.
n_warmup:为acquisition function随机采样的次数.
n_iter:运行scipy.minimize的次数.
----------
return:x_max,采集函数得到的,下一个预测观测点.
'''


def acq_max(ac, gp, y_max, bounds, random_state, n_warmup=10000, n_iter=100):
    '''
    bounds是按照超参数名称的字母顺序排列好后,对应的上下限值.
    _bounds[:,0]下限值列表,_bounds[:,1]是上限值列表.
    x_tries是一个大小为[n_warmup x bounds.shape[0]]的矩阵,行数=n_warmup,列数=bounds.shape[0]=超参数个数.
    x_tries的每一列都是对应于某一个超参数的随机取值,取值范围由bounds中的上下限决定.
    所以x_tries的每一行,对应了一个超参数组合(随机赋值).
    '''
    x_tries = random_state.uniform(bounds[:, 0], bounds[:, 1], size=(n_warmup, bounds.shape[0]))
    ys = ac(x_tries, gp=gp, y_max=y_max)

    # 取出使acquisition function取最值的超参数组合和对应的acquisition function值.
    x_max = x_tries[ys.argmax()]
    max_acq = ys.max()

    '''
    这里可以理解为:acquistion function的形状是通过n_warmup(1e5)个随机点构建而成的.
    然后在这个acquisition function的基础上,计算出acquistion function的最大值.
    '''
    x_seeds = random_state.uniform(bounds[:, 0], bounds[:, 1], size=(n_iter, bounds.shape[0]))
    for x_try in x_seeds:
        '''
        scipy.optimize.minimize()的参数:
        function:求最小值的目标函数.
        x_0:变量的初始化猜测值.
        bounds:变量取值范围.
        method:求极值的方法.
        '''
        res = minimize(lambda x: -ac(x.reshape(1, -1), gp=gp, y_max=y_max),
                       x_try.reshape(1, -1),
                       bounds=bounds,
                       method="L-BFGS-B")

        # 如果没达到success就继续.
        if not res.success:
            continue

        # 如果新计算的数据点比之前最优的值更优,则更新最优值.从不同的起点可能得到不同的结果,所以多跑些是好的.
        if max_acq is None or -res.fun[0] >= max_acq:
            x_max = res.x
            max_acq = -res.fun[0]

    # 裁剪输出值,确保其在取值范围内.浮点数有时不能保证这一点,加了保险.
    return np.clip(x_max, bounds[:, 0], bounds[:, 1])


'''获取并计算acquisition function.'''


class UtilityFunction(object):
    def __init__(self, kind, kappa, xi):
        """
        如果使用的是UCB,需要一个kappa的常数值.
        """
        self.kappa = kappa
        self.xi = xi

        # 只支持三种acquisition function:UCB,EI和POI.
        if kind not in ['ucb', 'ei', 'pi']:
            err = "你所需要的采集函数{}不被支持,请选择ucb,ei或者poi.".format(kind)
            raise NotImplementedError(err)
        else:
            self.kind = kind

    # 取得所用的acquisition function.
    def utility(self, x, gp, y_max):
        if self.kind == 'ucb':
            return self._ucb(x, gp, self.kappa)
        if self.kind == 'ei':
            return self._ei(x, gp, y_max, self.xi)
        if self.kind == 'pi':
            return self._pi(x, gp, y_max, self.xi)

    @staticmethod
    def _ucb(x, gp, kappa):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mean, std = gp.predict(x, return_std=True)

        # UCB公式.
        return mean + kappa * std

    @staticmethod
    def _ei(x, gp, y_max, xi):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mean, std = gp.predict(x, return_std=True)

        # EI公式.
        z = (mean - y_max - xi) / std
        return (mean - y_max - xi) * norm.cdf(z) + std * norm.pdf(z)

    @staticmethod
    def _pi(x, gp, y_max, xi):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            mean, std = gp.predict(x, return_std=True)

        # POI公式.
        z = (mean - y_max - xi) / std
        return norm.cdf(z)


'''
根据可选种子值创建一个随机数发生器.
np.random.RandomState()是一个伪随机数生成器.
如果是None,就返回默认随机数发生器.如果提供种子值,就根据种子值创建随机数发生器.
'''


def ensure_rng(random_state=None):
    if random_state is None:
        random_state = np.random.RandomState()
    elif isinstance(random_state, int):
        random_state = np.random.RandomState(random_state)
    else:
        assert isinstance(random_state, np.random.RandomState)
    return random_state