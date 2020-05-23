import numpy as np
import train_net
from .util import ensure_rng
import global_variable

'''
如果一个对象是可哈希的,那么它可以被计算出哈希值,即可以调用__hash__(),而且是可比较的,即可以调用__eq__().
可哈希对象可以作为字典的键,或者集合的成员.
'''


def _hashable(x):
    # 确保数据点在字典中是可哈希的(hashable).
    return tuple(map(float, x))


'''
贝叶斯优化的核心数据结构.
包括全部的计算过程信息,计算过的最优值等.
'''


class TargetSpace(object):
    '''
    path:神经网络模型的存储路径.
    dataSource:取得数据集的函数.
    pbounds:(字典)超参数名称及其取值上下限值(上下限值用元组存储).
    random_state:整数值/随机数发生器/None.用于产生随机数.
    '''

    def __init__(self, path, is_k_fold, is_test, train_data, test_data, pbounds, int_list, random_state=None):
        # 根据参数random_state获取随机数发生器.
        self.random_state = ensure_rng(random_state)

        self.path = path

        self.is_k_fold = is_k_fold
        self.is_test = is_test

        self.train_data = train_data
        self.test_data = test_data

        # 获取超参数名称,并按照首字母顺序排序.
        self._keys = sorted(pbounds)

        # 创建带有参数范围的数组.按照超参数顺序,取得各个超参数的下限取值和上限取值.
        self._bounds = np.array([item[1] for item in sorted(pbounds.items(),
                                                            key=lambda x: x[0])], dtype=np.float)
        # 超参数限定:仅能取整数的超参数值列表.
        self._list = int_list

        # _parms的尺寸为0×len(pbounds),_target的尺寸为0×0.
        # 这里是对其进行初始化,所以没有元素,是空的.后面计算出新的数值点,会被逐个添加到里面.
        self._params = np.empty(shape=(0, self.dim))
        self._target = np.empty(shape=(0))

        # 跟踪迭代过程中的取值点.
        self._cache = {}

    # 确定某个值是否在迭代过程中出现过.
    def __contains__(self, x):
        return _hashable(x) in self._cache

    def __len__(self):
        # len()取第一维的大小.根据__init()__中的定义,两者的len应该相等.
        assert len(self._params) == len(self._target)
        return len(self._target)

    @property
    def empty(self):
        return len(self) == 0

    @property
    def params(self):
        return self._params

    @property
    def target(self):
        return self._target

    # 超参数个数.
    @property
    def dim(self):
        return len(self._keys)

    @property
    def keys(self):
        return self._keys

    @property
    def bounds(self):
        return self._bounds

    # 给出超参数字典,取出这些超参数的值.(前提:和待优化的超参数数量一致)
    def params_to_array(self, params):
        try:
            assert set(params) == set(self.keys)
        except AssertionError:
            raise ValueError(
                "Parameters' keys ({}) do ".format(sorted(params)) + "not match the expected set of keys ({}).".format(
                    self.keys)
            )
        return np.asarray([params[key] for key in self.keys])

    # 给出超参数取值,令其和超参数名称组合,返回超参数字典.(前提:和待优化的超参数数量一致)
    def array_to_params(self, x):
        try:
            assert len(x) == len(self.keys)
        except AssertionError:
            raise ValueError(
                "Size of array ({}) is different than the ".format(
                    len(x)) + "expected number of parameters ({}).".format(len(self.keys))
            )
        return dict(zip(self.keys, x))

    def _as_array(self, x):
        try:
            x = np.asarray(x, dtype=float)
        except TypeError:
            x = self.params_to_array(x)

        # 将多维数组转化为一维数组.
        x = x.ravel()

        try:
            assert x.size == self.dim
        except AssertionError:
            raise ValueError(
                "Size of array ({}) is different than the ".format(len(x)) +
                "expected number of parameters ({}).".format(len(self.keys))
            )
        return x

    def register(self, params, target):
        x = self._as_array(params)
        # 已有的数据点值不会再重复计算.
        if x in self:
            raise KeyError('Data point {} is not unique'.format(x))

        # 添加新数据点值.
        self._cache[_hashable(x.ravel())] = target

        # np.concatenate()用于拼接数组.每次会把新的数值点摞上去,从最初的空数组逐渐填充.
        self._params = np.concatenate([self._params, x.reshape(1, -1)])
        self._target = np.concatenate([self._target, [target]])

    """
    计算单个点x,获得对应的值y,将其记录为观测值.优化函数恒定为train_net.train().
    如果之前已经计算过x的对应值,则直接从历史记录中找到对应的y值返回.
    ----------
    x:(ndarray)数据点,len(x)==self.dim.元素个数等于待优化函数的参数个数.
    y:(float)观测值.
    """

    def probe(self, params, basic_params):
        x = self._as_array(params)
        # try是从历史记录_cache中查找,如果找到了说明这个值已经计算过.反之则需要新加计算.
        try:
            target = self._cache[_hashable(x)]
        except KeyError:
            params = dict(zip(self._keys, x))

            for i, key in enumerate(params.keys()):
                if key in self._list:
                    basic_params[key] = int(params[key])
                    params[key] =int(params[key])
                else:
                    basic_params[key] = params[key]
            print('basic_params:', basic_params)

            Tr = train_net.Train(self.train_data, self.test_data, self.is_k_fold, self.is_test, self.path, basic_params)
            target = Tr.train()

            global_variable.test_acc.append(target)
            if len(global_variable.best_acc) == 0 or global_variable.best_acc[-1] < target:
                global_variable.best_acc.append(target)
                global_variable.best_param = basic_params.copy()
            else:
                temp_best_acc = global_variable.best_acc[-1]
                global_variable.best_acc.append(temp_best_acc)

            # 在历史记录中新加上新数据点的计算.
            self.register(params, target)

        return target

    """
    在空间范围内创建随机点.
    ----------
    data:(ndarray)[num x dim]数组.num此处恒等于1,dim=超参数个数.得到超参数的随机取值.
    """

    def random_sample(self):
        data = np.empty((1, self.dim))
        for col, (lower, upper) in enumerate(self._bounds):
            if self._keys[col] in self._list:
                data.T[col] = self.random_state.randint(lower, upper, size=1)
            else:
                data.T[col] = self.random_state.uniform(lower, upper, size=1)
        # 最终返回的是一个一维数组,每个元素对应的是给每个超参数生成的随机值.

        return data.ravel()

    def maxs(self):
        # 获取最大的目标值和对应的参数.
        try:
            res = {
                'target': self.target.max(),
                'params': dict(
                    zip(self.keys, self.params[self.target.argmax()])
                )
            }
        except ValueError:
            res = {}

        return res

    def res(self):
        # 获取所有的目标值和对应的参数.
        params = [dict(zip(self.keys, p)) for p in self.params]

        return [
            {"target": target, "params": param}
            for target, param in zip(self.target, params)
        ]

    '''
    更改超参数取值的上下限.
    '''

    def set_bounds(self, new_bounds):
        for row, key in enumerate(self.keys):
            if key in new_bounds:
                self._bounds[row] = new_bounds[key]