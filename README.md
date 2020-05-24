# hyperOpt
A simple hyperparameter optimization for classification network.
一个针对分类神经网络的超参数优化器软件.包括图形化操作界面和后台MySQL数据库连接存储.

# 运行开发环境
python version: 3.7
machine learning structure: pytorch GPU(1.4.0)
needed other packages: PyQt5, pymysql, qtawesome, torchvision, pandas, numpy, chardet, matplotlib, sklearn

# 结构说明
mainFrame: 程序入口.图形化主界面.
pre_data: 获取数据集.
train_net: 神经网络训练.
global_variable: 全局变量.

> icon: 图像资源文件.
> style: 应用于主界面显示的QSS文件.
> optimization: 优化器实现.
> Qtwindow: 前端图形化界面.

> result_fig: 优化结果折线图存储文件(初始为空).
> result_csv: 优化过程记录存储文件(初始为空).
> save_model: 存放网络模型原始定义文件,以及生成的模型文件的文件夹.

>> MySQL.txt: 开始时不存在.首次运行后在项目最外层被创建,记录数据库连接信息.
