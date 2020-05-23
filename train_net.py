'''
模型训练模块.包括三个不同形式的模型训练:
    1.测试集没有标签,仅使用有标签训练集,对训练集划分为训练集和验证集,采用k折交叉验证来训练模型.
    2.测试集有标签,在对有标签训练集采用k折交叉验证训练后,再拿到测试集上,得到测试集准确率.
    3.测试集有标签,但不采用k折交叉验证,只用训练集进行训练后,直接拿到测试集上,得到测试集准确率.
'''
import os
import time
import torch
from torch import nn
from torch import optim
import global_variable

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Train(object):
    def __init__(self, train_data, test_data, is_k_fold, is_test, path, params):
        self.train_data = train_data
        self.test_data = test_data
        self.is_k_fold = is_k_fold
        self.is_test = is_test
        if global_variable.path == None:
            global_variable.path = self.getModel(path)
        self.path = global_variable.path
        self.params = params

    '''
    调用训练函数:根据是否有测试集和是否使用k折交叉验证,来调用对应的训练函数.
    '''
    def train(self):
        if self.is_test:
            if self.is_k_fold:
                Acc = self.k_fold_with_test(self.path, self.train_data, self.test_data, self.params)
            else:
                # 没有k折交叉验证,不需要参数k.
                # k = self.params['k']
                num_epochs = self.params['num_epochs']
                batch_size = self.params['batch_size']
                lr = self.params['lr']
                weight_decay = self.params['weight_decay']
                train_iter = torch.utils.data.DataLoader(self.train_data, batch_size = batch_size, shuffle = True)
                test_iter = torch.utils.data.DataLoader(self.test_data, batch_size = batch_size, shuffle = True)
                net = torch.load(self.path)
                net = net.to(device)
                optimizer = optim.Adam(net.parameters(), lr = lr, weight_decay = weight_decay)
                train_acc, Acc = self.train_net(net, optimizer, train_iter, test_iter, num_epochs)
                print('单纯训练集测试集训练,训练集准确率=%f,验证集准确率=%f' % (train_acc, Acc))
        else:
            Acc = self.k_fold_without_test(self.path, self.train_data, self.params)

        return Acc

    '''
    模型验证效果函数.
    把训练后的模型传入,看它在验证集或者测试集上的表现.
    '''

    def evaluate_accuracy(self, net, exam_iter):
        acc_sum = 0.0
        n = 0

        with torch.no_grad():
            for X, y in exam_iter:
                net.eval()
                acc_sum += (net(X.to(device)).argmax(dim=1) == y.to(device)).float().sum().cpu().item()
                net.train()
                n += y.shape[0]

        return acc_sum / n

    '''
    模型训练函数.
    接收一个训练集和一个验证集/测试集.训练集用来训练模型,更新网络参数,再拿到验证集或测试集上验证效果.
    '''

    def train_net(self, net, optimizer, train_iter, exam_iter, num_epochs):
        print('training on', device)

        loss = nn.CrossEntropyLoss()
        batch_count = 0

        # 记录本次num_epochs次训练之后,最终的训练集准确率和验证集/测试集准确率.
        evTrain_acc = 0.0
        evExam_acc = 0.0

        for epoch in range(num_epochs):
            train_loss_sum = 0.0
            train_acc_sum = 0.0
            n = 0
            start = time.time()

            for X, y in train_iter:
                X = X.to(device)
                y = y.to(device)

                y_hat = net(X)
                L = loss(y_hat, y.long())

                optimizer.zero_grad()
                L.backward()
                optimizer.step()

                # 损失是以批量为单位计算的.每次的L得到的是这个批量的损失值,所以需要除以batch_count.
                train_loss_sum += L.cpu().item()
                # 准确率是逐个样本比较的.y含有若干个样本,这些样本会一一被拿出来比较,所以最后要除以n.
                train_acc_sum += (y_hat.argmax(dim=1) == y).sum().cpu().item()

                n += y.shape[0]
                batch_count += 1

            exam_acc = self.evaluate_accuracy(net, exam_iter)

            print('epoch %d, train loss %.4f, train acc %.3f, test acc %.4f, time %.2f sec'
                  % (epoch + 1, train_loss_sum / batch_count, train_acc_sum / n, exam_acc, time.time() - start))

            evTrain_acc = train_acc_sum / n
            evExam_acc = exam_acc

        return evTrain_acc, evExam_acc

    '''
    k折交叉验证.
    k折交叉验证的实质是对训练样本集合进行k次训练.每一次选择一部分作为验证集,其他部分仍留作训练集.
    这里同样提供了一种额外的方式:只进行一次训练.这样能够减少运行时间.
    但是一次训练的结果存在随机性,在计算能力充足的时候还是建议k折交叉验证取平均.
    --------------------
    parameter list:
        -> path:保存用pytorch方式定义的网络模型的文件路径.
        -> mnist_train:训练集.dataset类型.可以被torch.utils.data.DataLoader调用.一定有.
        -> mnist_test:测试集.dataset类型.可以被torch.utils.data.DataLoader调用.未必有.
        -> **hyperparams:超参数取值字典.所有可以被优化的超参数都包括在内.
    '''

    def k_fold_without_test(self, path, train_data, hyperparams):
        # 支持的超参数优化有:k,num_epochs,batch_size,lr,weight_decay.
        # 以上超参数都有默认值,如果不指定的话统一采用默认值(但是都得有,不能是空的).
        k = hyperparams['k']
        num_epochs = hyperparams['num_epochs']
        batch_size = hyperparams['batch_size']
        lr = hyperparams['lr']
        weight_decay = hyperparams['weight_decay']

        # 如果k==1,则将训练集进行10等分,然后用其中的9/10作为训练集,1/10作为验证集,只跑一次,节省时间,但有随机性.
        if k == 1:
            # 训练集每折的长度.
            fold_size = len(train_data) // 10

            # 将训练集分成训练集(9/10)和验证集(1/10).
            train_data, _ = torch.utils.data.random_split(train_data,
                                                          [10 * fold_size, len(train_data) - 10 * fold_size])

            valid_acc_sum = 0.0

            for i in range(3):
                train, valid = torch.utils.data.random_split(train_data, [9 * fold_size, fold_size])
                train_iter = torch.utils.data.DataLoader(train, batch_size=batch_size, shuffle=True)
                valid_iter = torch.utils.data.DataLoader(valid, batch_size=batch_size, shuffle=True)

                # 取得网络模型和优化器.
                net = torch.load(path)
                net = net.to(device)
                optimizer = optim.Adam(net.parameters(), lr=lr, weight_decay=weight_decay)

                train_acc, valid_acc = self.train_net(net, optimizer, train_iter, valid_iter, num_epochs)
                valid_acc_sum += valid_acc

                print('10折交叉验证取单折,训练集准确率=%f,验证集准确率=%f' % (train_acc, valid_acc))
            return valid_acc_sum / 3

        elif k > 1:
            # 训练集准确率之和.
            train_acc_sum = 0.0
            # 验证集准确率之和.
            valid_acc_sum = 0.0

            fold_size = len(train_data) // k
            # data获取当前这次所需的训练样本集和验证样本集.
            train_data, _ = torch.utils.data.random_split(train_data, [k * fold_size, len(train_data) - k * fold_size])

            for i in range(k):
                train, valid = torch.utils.data.random_split(train_data, [(k - 1) * fold_size, fold_size])
                train_iter = torch.utils.data.DataLoader(train, batch_size=batch_size, shuffle=True)
                valid_iter = torch.utils.data.DataLoader(valid, batch_size=batch_size, shuffle=True)

                # 取得网络模型和优化器.
                net = torch.load(path)
                net = net.to(device)
                optimizer = optim.Adam(net.parameters(), lr=lr, weight_decay=weight_decay)

                train_acc, valid_acc = self.train_net(net, optimizer, train_iter, valid_iter, num_epochs)
                train_acc_sum += train_acc
                valid_acc_sum += valid_acc

                print('%d折交叉训练第%d折,训练集准确率=%f,验证集准确率=%f' % (k, i + 1, train_acc, valid_acc))

            return valid_acc_sum / k

    def k_fold_with_test(self, path, train_data, test_data, hyperparams):
        # 支持的超参数优化有:k,num_epochs,batch_size,lr,weight_decay.
        # 以上超参数都有默认值,如果不指定的话统一采用默认值(但是都得有,不能是空的).
        k = hyperparams['k']
        num_epochs = hyperparams['num_epochs']
        batch_size = hyperparams['batch_size']
        lr = hyperparams['lr']
        weight_decay = hyperparams['weight_decay']

        # 如果k==1,则将训练集进行10等分,然后用其中的9/10作为训练集,1/10作为验证集,如此循环x次,节省时间,但有随机性.
        # (一般x取2~5,比10折交叉验证要少一截,但是也算是引入了多重验证,消解了随机性的影响.)
        if k == 1:
            # 训练集每折的长度.
            fold_size = len(train_data) // 10
            # 将训练集分成训练集(9/10)和验证集(1/10).
            train_data, _ = torch.utils.data.random_split(train_data,
                                                          [10 * fold_size, len(train_data) - 10 * fold_size])

            test_acc_sum = 0.0

            for i in range(3):
                train, valid = torch.utils.data.random_split(train_data, [9 * fold_size, fold_size])
                train_iter = torch.utils.data.DataLoader(train, batch_size=batch_size, shuffle=True)
                valid_iter = torch.utils.data.DataLoader(valid, batch_size=batch_size, shuffle=True)
                test_iter = torch.utils.data.DataLoader(test_data, batch_size=batch_size, shuffle=True)
                # 取得网络模型和优化器.
                net = torch.load(path)
                net = net.to(device)
                optimizer = optim.SGD(net.parameters(), lr=lr, weight_decay=weight_decay)
                train_acc, valid_acc = self.train_net(net, optimizer, train_iter, valid_iter, num_epochs)
                test_acc = self.evaluate_accuracy(net, test_iter)
                test_acc_sum += test_acc

                print('10折交叉验证取单折,训练集准确率=%f,验证集准确率=%f,测试集准确率=%f' % (train_acc, valid_acc, test_acc))
            return test_acc_sum / 3

        elif k > 1:
            # 训练集准确率之和.
            train_acc_sum = 0.0
            # 验证集准确率之和.
            valid_acc_sum = 0.0
            # 测试集准确率之和.
            test_acc_sum = 0.0

            fold_size = len(train_data) // k
            # data获取当前这次所需的训练样本集和验证样本集.
            train_data, _ = torch.utils.data.random_split(train_data, [k * fold_size, len(train_data) - k * fold_size])

            for i in range(k):
                train, valid = torch.utils.data.random_split(train_data, [(k - 1) * fold_size, fold_size])
                train_iter = torch.utils.data.DataLoader(train, batch_size=batch_size, shuffle=True)
                valid_iter = torch.utils.data.DataLoader(valid, batch_size=batch_size, shuffle=True)
                test_iter = torch.utils.data.DataLoader(test_data, batch_size=batch_size, shuffle=True)

                # 取得网络模型和优化器.
                net = torch.load(path)
                net = net.to(device)
                optimizer = optim.Adam(net.parameters(), lr=lr, weight_decay=weight_decay)

                train_acc, valid_acc = self.train_net(net, optimizer, train_iter, valid_iter, num_epochs)
                train_acc_sum += train_acc
                valid_acc_sum += valid_acc

                test_acc = self.evaluate_accuracy(net, test_iter)
                test_acc_sum += test_acc

                print('%d折交叉训练第%d折,训练集准确率=%f,验证集准确率=%f,测试集准确率=%f' % (k, i + 1, train_acc, valid_acc, test_acc))

            return test_acc_sum / k

    def getModel(self, modelName):
        # 导入网络模型所在模块.位于save_model文件夹下.
        _, modelName = os.path.split(modelName)
        get_net = "import save_model." + modelName[:-3] + " as " + modelName[:-3]
        print(get_net)
        exec(get_net)

        # 确定存储网络模型的文件名,获取.py文件中的网络模型实例,调用.save().
        net = eval(modelName[:-3] + '.net')
        print('net:', net)

        saveName = 'save_model/' + modelName[:-3] + '.pt'
        # saveName = modelName[:-3] + '.pt'
        print('saveName:', saveName)

        torch.save(net, saveName)

        return saveName
