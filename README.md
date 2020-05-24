# hyperOpt
A simple hyperparameter optimization for classification network.

一个针对分类神经网络的超参数优化器软件，基于pytorch框架，包括Grid Search，Random Search，Bayesian optimization，Genetic Algorithm（GA），Particle Swarm Optimization（PSO）五种可行的超参数优化技术，以及图形化操作界面和后台MySQL数据库连接存储。

## 运行开发环境
python version: 3.7

machine learning structure: pytorch GPU（1.4.0）

needed other packages: PyQt5，pymysql，qtawesome，torchvision，pandas，numpy，chardet，matplotlib，sklearn

database: MySQL

## 结构说明
+ mainFrame: 程序入口.图形化主界面。
+ pre_data: 获取数据集。
+ train_net: 神经网络训练。
+ global_variable: 全局变量。

+ icon: 图像资源文件。
+ style: 应用于主界面显示的QSS文件。
+ optimization: 优化器实现。
+ Qtwindow: 前端图形化界面。

+ result_fig: 优化结果折线图存储文件（初始为空）。
+ result_csv: 优化过程记录存储文件（初始为空）。
+ save_model: 存放网络模型原始定义文件，以及生成的模型文件的文件夹。

+ MySQL.txt: 开始时不存在。首次运行后在项目最外层被创建，记录数据库连接信息。

## 使用说明
### 运行程序
配置好相关环境后运行mainFrame.py文件即可。

首次运行时会弹出对话框，要求用户配置数据库连接信息。成功连接到指定数据库后，将会在数据库下自动创建新数据库和数据库表，用于后续优化过程的存储。

运行界面分为五个部分：
+ pageOne：超参数优化预设界面。进行超参数优化的相关预设配置，配置好优化所需信息后即可开始优化。
+ pageTwo：超参数优化过程跟踪界面。在超参数优化过程中显示当前的优化进程。
+ pageThree：历史优化记录查看界面。查看数据库中所有的优化记录。
+ pageFour：文本编辑界面。进行简单的文本文件编辑，保存，另存为等操作。
+ pageFive：信息补充界面。对使用过程中遇到的一些问题进行说明，或许能从这里面找到一些灵感？

### 注意事项说明
\1. 请勿改动项目的目录结构或删改文件。尤其是存储资源文件夹，将用于存放优化结果文件，改动后程序可能无法获取准确路径。
\2. 该软件只针对分类问题的神经网络进行超参数优化，请勿使用不符合条件的机器学习模型，否则优化将会出现错误。
\3. 超参数优化速度很大程度上取决于神经网络的复杂度和数据集的大小。预处理时间较长的情况下请不要贸然退出。
\4. 如果在使用过程中出现问题，欢迎留言说明。
