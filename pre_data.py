import torch
import torchvision
import torchvision.transforms as transforms
import pandas as pd

'''
读取路径,把最原始的数据读出来,分配到对应的处理函数中.不同类型的数据有不同的处理方式.
1.torchvision自带数据集:
    -> torchvision.MNIST:mnist图像数据集.
    -> torchvision.datasets.FashionMNIST:Fashionmnist图像数据集.
    -> torchvision.CIFAR10:cifar-10数据集.
    -> ......
这些数据集用is_torchvision来表示,然后给出数据集的名称,从torchvision.datasets里面获取数据.
2.文件夹内图片载入:给出文件路径,从文件中提取出训练集图像,标签和测试集图像,标签.
最终返回的一定是dataset类型的数据,可以被torch.utils.data.DataLoader调用.
3..csv文件.这种文件同样是分类问题.要求训练集和测试集是csv文件类型,且不包含id等无效判别特征.
(.data,.txt等文件类型,只要其中的数据形式近似表格状,都可以转为.csv类型)
'''

class PrepareData(object):
    def __init__(self, is_torchvision, is_folder, torchvision_name, train_path, test_path, aim_path=None, resize=None):
        self.is_torchvision = is_torchvision
        self.torchvision_name = torchvision_name

        self.is_folder = is_folder
        self.train_path = train_path
        self.test_path = test_path
        self.aim_path = aim_path

        # 是否要将图片大小统一调整为某尺寸(一般来说是要的,和get_net中的神经网络结构统一).
        self.resize = resize

        self.torchvision_support = ['mnist', 'fashion-mnist', 'cifar-10', 'kmnist', 'emnist-byclass']

    def get_data(self):
        if self.is_torchvision:
            return self.get_torchvision_dataset(self.torchvision_name)

        elif self.is_folder:
            # 如果提供的路径不是.csv文件,就是文件夹,需要从文件夹中读取图片.
            if self.train_path.find('.csv') == -1:
                if self.test_path == None:
                    return self.get_folder_data(self.train_path)
                else:
                    return self.get_folder_data(self.train_path), self.get_folder_data(self.test_path)
            # 如果提供的路径是.csv文件,就是表格类数据.
            else:
                if self.test_path == None:
                    return self.get_csv_data(self.train_path)
                else:
                    return self.get_csv_data(self.train_path), self.get_csv_data(self.test_path)

    def get_torchvision_dataset(self, torchvision_name):
        # 图像处理(在有图像大小调整需要的情况下添加一个图像大小变换的操作).
        trans = []
        if self.resize:
            trans.append(torchvision.transforms.Resize(self.resize))
        trans.append(torchvision.transforms.ToTensor())

        if torchvision_name == 'fashion-mnist':
            train_data = torchvision.datasets.FashionMNIST(root = self.aim_path, train = True, download = True, transform = transforms.Compose(trans))
            test_data = torchvision.datasets.FashionMNIST(root = self.aim_path, train = False, download = True, transform = transforms.Compose(trans))

        elif torchvision_name == 'mnist':
            train_data = torchvision.datasets.MNIST(root = self.aim_path, train = True, download = True, transform = transforms.Compose(trans))
            test_data = torchvision.datasets.MNIST(root = self.aim_path, train = False, download = True, transform = transforms.Compose(trans))

        elif torchvision_name == 'cifar-10':
            train_data = torchvision.datasets.CIFAR10(root = self.aim_path, train = True, download = True, transform = transforms.Compose(trans))
            test_data = torchvision.datasets.CIFAR10(root = self.aim_path, train = False, download = True, transform = transforms.Compose(trans))

        elif torchvision_name == 'kmnist':
            train_data = torchvision.datasets.KMNIST(root = self.aim_path, train = True, download = True, transform = transforms.Compose(trans))
            test_data = torchvision.datasets.KMNIST(root = self.aim_path, train = False, download = True, transform = transforms.Compose(trans))

        elif torchvision_name == 'emnist-byclass':
            train_data = torchvision.datasets.EMNIST(root = self.aim_path, split = 'byclass', train = True, download = True, transform = transforms.Compose(trans))
            test_data = torchvision.datasets.EMNIST(root = self.aim_path, split = 'byclass', train = False, download = True, transform = transforms.Compose(trans))

        elif torchvision_name == 'emnist-byfield':
            train_data = torchvision.datasets.EMNIST(root = self.aim_path, split = 'byfield', train = True, download = True, transform = transforms.Compose(trans))
            test_data = torchvision.datasets.EMNIST(root = self.aim_path, split = 'byfield', train = False, download = True, transform = transforms.Compose(trans))

        print(train_data)
        print(test_data)
        return train_data, test_data

    def get_folder_data(self, path):
        trans = []
        if self.resize:
            trans.append(torchvision.transforms.Resize(self.resize))
        trans.append(torchvision.transforms.ToTensor())

        try:
            data = torchvision.datasets.ImageFolder(root = path, transform = torchvision.transforms.Compose(trans))
            return data
        except FileNotFoundError:
            print('文件路径错误,无法读取图像数据.')

    # 要求:.csv文件中的数据特征不包括id这样的无效特征.
    def get_csv_data(self, path):
        try:
            data = pd.read_csv(path)
        except FileNotFoundError:
            print('文件路径错误,无法读取.csv文件.')

        # 最后一列被排除,所以all_features只包括特征,不包括标签.
        all_features = data.iloc[:, :-1]
        # print(all_features)

        # 最后一列是标签.标签未必是数值型,需要改写成数值型.这里不能用get_dummies,因为那会增加列数.
        all_labels = []
        labels = data.iloc[:, -1]

        # 把第一个标签先提取出来打底,之后的再往里面加.
        labels_dict = {labels[0]: 0}
        all_labels.append(0)
        count = 1

        for i in range(len(labels) - 1):
            # 如果该标签已经被数值化,则直接转换,否则在字典里面新加一项.
            if labels[i + 1] in labels_dict.keys():
                all_labels.append(labels_dict[labels[i + 1]])
            else:
                # 字典新加项.
                labels_dict[labels[i + 1]] = count
                # 标签转换.
                all_labels.append(count)
                # 数值化标签值+1.
                count += 1

        # 数值化特征标准化处理.
        numeric_features = all_features.dtypes[all_features.dtypes != 'object'].index
        all_features[numeric_features] = all_features[numeric_features].apply(lambda x: (x - x.mean()) / (x.std()))
        all_features = all_features.fillna(0)

        # 离散化特征转换为数值化特征.
        all_features = pd.get_dummies(all_features, dummy_na = True)
        print(all_features)
        print(labels_dict)

        # 提取data_features和data_labels,组装成dataset.
        n_data = data.shape[0]
        data_features = torch.tensor(all_features[:n_data].values, dtype = torch.float)
        data_labels = torch.tensor(all_labels[:n_data], dtype = torch.float)
        dataset = torch.utils.data.TensorDataset(data_features, data_labels)

        return dataset