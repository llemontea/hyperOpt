from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import qtawesome

class oneWidget(QWidget):
    def __init__(self):
        super(oneWidget, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setStyleSheet('''
        .QScrollArea {
            border: none;
        }        
        ''')

        # 数据集选择部分.
        self.datasetbox = QGroupBox('数据集设置')
        self.datasetLayout = QVBoxLayout()

        self.radioGroup1 = QButtonGroup(self)
        self.data_radio1 = QRadioButton("torchvision.datasets")
        self.data_radio2 = QRadioButton("图片文件夹")
        self.data_radio3 = QRadioButton(".csv数据表文件")
        self.radioGroup1.addButton(self.data_radio1)
        self.radioGroup1.addButton(self.data_radio2)
        self.radioGroup1.addButton(self.data_radio3)

        # radio1范围内控件.
        self.datasetLayout_1 = QVBoxLayout()
        self.datasetLayout_1_firstRow = QHBoxLayout()
        self.dataSource1 = QComboBox()
        self.filepathEdit1 = QLineEdit()
        self.filepathButton1 = QToolButton()
        self.filepathButton1.setIcon(qtawesome.icon('fa.folder-open', color = 'white'))
        self.label1 = QLabel('请选择要使用的torchvision.datasets数据集,并指定数据集存放的路径.如果尚无数据集,请在训练过程中保持网络畅通,以便下载资源.')
        self.line11 = QFrame(self.main_widget)

        # radio2范围内控件.
        self.datasetLayout_2 = QVBoxLayout()
        self.datasetLayout_2_firstRow = QGridLayout()
        self.label21 = QLabel('训练数据集:')
        self.label22 = QLabel('测试数据集:')
        self.filepathEdit21 = QLineEdit()
        self.filepathEdit22 = QLineEdit()
        self.filepathButton21 = QToolButton()
        self.filepathButton21.setIcon(qtawesome.icon('fa.folder-open', color = 'white'))
        self.filepathButton22 = QToolButton()
        self.filepathButton22.setIcon(qtawesome.icon('fa.folder-open', color = 'white'))
        self.label2 = QLabel('请把不同类别的图像单独放置于子文件夹中.子文件夹的数量等于分类的类别数.其中,测试集不是必须的.')
        self.line12 = QFrame(self.main_widget)

        # radio3范围内控件.
        self.datasetLayout_3 = QVBoxLayout()
        self.datasetLayout_3_firstRow = QGridLayout()
        self.label31 = QLabel('训练数据集:')
        self.label32 = QLabel('测试数据集:')
        self.filepathEdit31 = QLineEdit()
        self.filepathEdit32 = QLineEdit()
        self.filepathButton31 = QToolButton()
        self.filepathButton31.setIcon(qtawesome.icon('fa.folder-open', color = 'white'))
        self.filepathButton32 = QToolButton()
        self.filepathButton32.setIcon(qtawesome.icon('fa.folder-open', color = 'white'))
        self.label33 = QLabel('要求.csv中的每一列表示样本的一个属性,所以请勿引入序号这类非属性列.最后一列为样本标签.')
        self.line13 = QFrame(self.main_widget)

        # 数据集额外选项:
        self.datasetLayout_4 = QVBoxLayout()
        self.datasetLayout_4_firstRow = QHBoxLayout()
        self.label41 = QLabel('图片尺寸调整(.csv数据集无效):')
        self.label42 = QLabel('长:')
        self.label43 = QLabel('宽:')
        self.widthEdit = QLineEdit()
        self.heightEdit = QLineEdit()

        # 网络模型选择部分.
        self.netbox = QGroupBox('网络模型设置')
        self.netLayout = QVBoxLayout()
        self.netLayout_firstRow = QHBoxLayout()
        self.netLayout_secondRow = QHBoxLayout()
        self.net_label1 = QLabel('网络模型定义文件(.py):')
        self.net_label2 = QLabel('注意:请保证您上传的网络模型定义文件中包含完整的网络模型定义,用变量名net对类进行实例化或承接模型定义函数的返回值.点击?按钮查看代码示例.'
                                 '\n优化器会将网络模型文件复制到save_model文件夹下,并自动生成与文件名相同的模型.pt文件,但不会对源文件进行任何改动.'
                                 '\n所以请保证您上传的网络模型和数据集相匹配.如果在运行过程中出现了界面卡死等情形,请优先检查网络模型是否存在问题.')
        self.netFilepathEdit = QLineEdit()
        self.exampleButton = QToolButton()
        self.exampleButton.setIcon(qtawesome.icon('fa.question-circle-o', color = 'white'))
        self.netFilepathButton = QToolButton()
        self.netFilepathButton.setIcon(qtawesome.icon('fa.folder-open', color = 'white'))

        # 超参数选取部分.
        self.hyperbox = QGroupBox('超参数设置')
        self.hyperLayout = QVBoxLayout()

        self.hyperLayout_firstRow = QHBoxLayout()
        self.hyperLayout_secondRow = QHBoxLayout()
        self.hyperLayout_thirdRow = QGridLayout()

        self.hyperCheckbox1 = QCheckBox('k')
        self.hyperCheckbox2 = QCheckBox('num_epochs')
        self.hyperCheckbox3 = QCheckBox('batch_size')
        self.hyperCheckbox4 = QCheckBox('learning_rate')
        self.hyperCheckbox5 = QCheckBox('weight_decay')

        self.hyperlabel_1 = QLabel('要优化的超参数:')
        self.hyperlabel_2 = QLabel('超参数默认取值:')
        self.hyperlabel_3 = QLabel('待优化超参数的取值上下限:')
        self.hyperlabel_4 = QLabel('CPU和GPU的容量有限.如果出现了out of memory的错误提示信息,请适当减小batch_size的取值或者重启优化器,再重新尝试运行.\n其中,超参数k,num_epochs和batch_size要求取值为整数.')
        self.hyperlabel1 = QLabel('k:')
        self.hyperlabel1s = QLabel('k:')
        self.hyperlabel2 = QLabel('num_epochs:')
        self.hyperlabel2s = QLabel('num_epochs:')
        self.hyperlabel3 = QLabel('batch_size:')
        self.hyperlabel3s = QLabel('batch_size:')
        self.hyperlabel4 = QLabel('learning_rate:')
        self.hyperlabel4s = QLabel('learning_rate:')
        self.hyperlabel5 = QLabel('weight_decay:')
        self.hyperlabel5s = QLabel('weight_decay:')

        self.hyperDefault1 = QLineEdit()
        self.hyperDefault2 = QLineEdit()
        self.hyperDefault3 = QLineEdit()
        self.hyperDefault4 = QLineEdit()
        self.hyperDefault5 = QLineEdit()

        self.hyperMin1 = QLineEdit()
        self.hyperMax1 = QLineEdit()
        self.hyperMin2 = QLineEdit()
        self.hyperMax2 = QLineEdit()
        self.hyperMin3 = QLineEdit()
        self.hyperMax3 = QLineEdit()
        self.hyperMin4 = QLineEdit()
        self.hyperMax4 = QLineEdit()
        self.hyperMin5 = QLineEdit()
        self.hyperMax5 = QLineEdit()

        # 超参数优化器选择部分.
        self.optbox = QGroupBox('超参数优化器设置')
        self.optLayout = QVBoxLayout()

        self.radioGroup2 = QButtonGroup(self)
        self.opt_radio1 = QRadioButton('网格搜索')
        self.opt_radio2 = QRadioButton('随机搜索')
        self.opt_radio3 = QRadioButton('贝叶斯优化')
        self.opt_radio4 = QRadioButton('遗传算法')
        self.opt_radio5 = QRadioButton('粒子群算法')
        self.radioGroup2.addButton(self.opt_radio1)
        self.radioGroup2.addButton(self.opt_radio2)
        self.radioGroup2.addButton(self.opt_radio3)
        self.radioGroup2.addButton(self.opt_radio4)
        self.radioGroup2.addButton(self.opt_radio5)

        # 网格搜索部分控件.
        self.optLayout_1 = QGridLayout()
        self.optlabel_11 = QLabel('超参数取值步长:')
        self.optlabel_12 = QLabel('k:')
        self.optlabel_13 = QLabel('num_epochs:')
        self.optlabel_14 = QLabel('batch_size:')
        self.optlabel_15 = QLabel('learning_rate:')
        self.optlabel_16 = QLabel('weight_decay:')
        self.optlabel_17 = QLabel('注意:超参数k,num_epochs和batch_size的步长必须是整数！')
        self.optEdit_11 = QLineEdit()
        self.optEdit_12 = QLineEdit()
        self.optEdit_13 = QLineEdit()
        self.optEdit_14 = QLineEdit()
        self.optEdit_15 = QLineEdit()
        self.line41 = QFrame(self.main_widget)

        # 随机搜索部分控件.
        self.optLayout_2 = QHBoxLayout()
        self.optlabel_2 = QLabel('超参数优化迭代次数:')
        self.optEdit_2 = QLineEdit()
        self.line42 = QFrame(self.main_widget)

        # 贝叶斯优化部分控件.
        self.optLayout_3 = QGridLayout()
        self.optlabel_31 = QLabel('贝叶斯优化预设数:')
        self.optlabel_32 = QLabel('贝叶斯优化预测数:')
        self.optEdit_31 = QLineEdit()
        self.optEdit_32 = QLineEdit()
        self.radioGroup3 = QButtonGroup()
        self.bayesian_radio1 = QRadioButton('UCB')
        self.bayesian_radio2 = QRadioButton('EI')
        self.bayesian_radio3 = QRadioButton('PI')
        self.optlabel_33 = QLabel('选择贝叶斯优化的采集函数:')
        self.optlabel_34 = QLabel('κ(UCB):')
        self.optlabel_35 = QLabel('χ(EI/PI):')
        self.optEdit_33 = QLineEdit()
        self.optEdit_34 = QLineEdit()
        self.line43 = QFrame(self.main_widget)

        # 遗传算法部分控件.
        self.optLayout_4 = QGridLayout()
        self.optlabel_41 = QLabel('遗传算法迭代次数:')
        self.optlabel_42 = QLabel('遗传算法种群个体数:')
        self.optEdit_41 = QLineEdit()
        self.optEdit_42 = QLineEdit()
        self.optlabel_43 = QLabel('个体染色体交叉概率:')
        self.optlabel_44 = QLabel('个体染色体变异概率:')
        self.optlabel_45 = QLabel('个体染色体编码长度:')
        self.optEdit_43 = QLineEdit()
        self.optEdit_44 = QLineEdit()
        self.optEdit_45 = QLineEdit()
        self.line44 = QFrame(self.main_widget)

        # 粒子群算法部分控件.
        self.optLayout_5 = QGridLayout()
        self.optlabel_51 = QLabel('粒子群算法迭代次数:')
        self.optlabel_52 = QLabel('粒子群算法粒子个数:')
        self.optlabel_53 = QLabel('每代新增粒子数:')
        self.optEdit_51 = QLineEdit()
        self.optEdit_52 = QLineEdit()
        self.optEdit_53 = QLineEdit()
        self.optlabel_54 = QLabel('个体信息权重c1:')
        self.optlabel_55 = QLabel('全局信息权重c2:')
        self.optlabel_56 = QLabel('惯性因子w下限:')
        self.optlabel_57 = QLabel('惯性因子w上限:')
        self.optEdit_54 = QLineEdit()
        self.optEdit_55 = QLineEdit()
        self.optEdit_56 = QLineEdit()
        self.optEdit_57 = QLineEdit()

        # 其他设置.
        self.extrabox = QGroupBox('其他设置')
        self.extraLayout = QVBoxLayout()

        self.extraCheckbox_1 = QCheckBox('采用k折交叉验证')
        self.extralabel_1 = QLabel('注意:没有测试集的情况下只能采用k折交叉验证.存在测试集的情况下,是否采用k折交叉验证是可选项.(请保证测试集的样本含标签)')

        # 最下层按钮.
        self.bottomLayout = QHBoxLayout()
        self.bottom_tipButton = QPushButton('  提示(tips)  ')
        self.bottom_clearButton = QPushButton('  清空  ')
        self.bottom_startButton = QPushButton('  开始训练!  ')

        self.init_widget()

    def getWidget(self):
        return self.scrollArea

    def init_widget(self):
        # 数据集子选项一:torchvision.datasets
        self.data_radio1.setChecked(True)
        self.filepathButton1.clicked.connect(lambda: self.chooseFilePath(self.filepathEdit1))

        self.dataSource1.addItems(['mnist','fashion-mnist','cifar-10','kmnist','emnist-byclass','emnist-byfield'])

        self.datasetLayout_1_firstRow.addWidget(self.data_radio1)
        self.datasetLayout_1_firstRow.addWidget(self.dataSource1)
        self.datasetLayout_1_firstRow.addWidget(self.filepathEdit1)
        self.datasetLayout_1_firstRow.addWidget(self.filepathButton1)
        self.line11.setFrameShape(4)
        self.line11.setFrameShadow(0x030)

        self.datasetLayout_1.addLayout(self.datasetLayout_1_firstRow)
        self.datasetLayout_1.addWidget(self.label1)
        self.datasetLayout_1.addWidget(self.line11)
        self.datasetLayout_1.addStretch()

        # 数据集子选项二:图像文件夹.
        self.filepathButton21.clicked.connect(lambda: self.chooseFilePath(self.filepathEdit21))
        self.filepathButton22.clicked.connect(lambda: self.chooseFilePath(self.filepathEdit22))

        self.datasetLayout_2_firstRow.addWidget(self.data_radio2, 0, 0, 2, 1)
        self.datasetLayout_2_firstRow.addWidget(self.label21, 0, 1, 1, 1)
        self.datasetLayout_2_firstRow.addWidget(self.filepathEdit21, 0, 2, 1, 1)
        self.datasetLayout_2_firstRow.addWidget(self.filepathButton21, 0, 3, 1, 1)
        self.datasetLayout_2_firstRow.addWidget(self.label22, 1, 1, 1, 1)
        self.datasetLayout_2_firstRow.addWidget(self.filepathEdit22, 1, 2, 1, 1)
        self.datasetLayout_2_firstRow.addWidget(self.filepathButton22, 1, 3, 1, 1)
        self.line12.setFrameShape(4)
        self.line12.setFrameShadow(0x030)

        self.datasetLayout_2.addLayout(self.datasetLayout_2_firstRow)
        self.datasetLayout_2.addWidget(self.label2)
        self.datasetLayout_2.addWidget(self.line12)
        self.datasetLayout_2.addStretch()

        # 数据集子选项三:.csv文件.
        self.filepathButton31.clicked.connect(lambda: self.choosedatasetFile(self.filepathEdit31))
        self.filepathButton32.clicked.connect(lambda: self.choosedatasetFile(self.filepathEdit32))

        self.datasetLayout_3_firstRow.addWidget(self.data_radio3, 0, 0, 2, 1)
        self.datasetLayout_3_firstRow.addWidget(self.label31, 0, 1, 1, 1)
        self.datasetLayout_3_firstRow.addWidget(self.filepathEdit31, 0, 2, 1, 1)
        self.datasetLayout_3_firstRow.addWidget(self.filepathButton31, 0, 3, 1, 1)
        self.datasetLayout_3_firstRow.addWidget(self.label32, 1, 1, 1, 1)
        self.datasetLayout_3_firstRow.addWidget(self.filepathEdit32, 1, 2, 1, 1)
        self.datasetLayout_3_firstRow.addWidget(self.filepathButton32, 1, 3, 1, 1)
        self.line13.setFrameShape(4)
        self.line13.setFrameShadow(0x030)

        self.datasetLayout_3.addLayout(self.datasetLayout_3_firstRow)
        self.datasetLayout_3.addWidget(self.label33)
        self.datasetLayout_3.addWidget(self.line13)
        self.datasetLayout_3.addStretch()

        # 数据集子选项四:图像尺寸调整.
        self.widthEdit.setValidator(QIntValidator())
        self.heightEdit.setValidator(QIntValidator())

        self.widthEdit.setFixedWidth(160)
        self.heightEdit.setFixedWidth(160)

        self.datasetLayout_4_firstRow.addWidget(self.label41)
        self.datasetLayout_4_firstRow.addWidget(self.label42)
        self.datasetLayout_4_firstRow.addWidget(self.widthEdit)
        self.datasetLayout_4_firstRow.addWidget(self.label43)
        self.datasetLayout_4_firstRow.addWidget(self.heightEdit)
        self.datasetLayout_4_firstRow.addStretch()

        self.datasetLayout_4.addLayout(self.datasetLayout_4_firstRow)
        self.datasetLayout_4.addStretch()

        self.datasetLayout.addLayout(self.datasetLayout_1)
        self.datasetLayout.addLayout(self.datasetLayout_2)
        self.datasetLayout.addLayout(self.datasetLayout_3)
        self.datasetLayout.addLayout(self.datasetLayout_4)
        self.datasetLayout.addStretch()
        self.datasetbox.setLayout(self.datasetLayout)

        # 神经网络设置.
        self.exampleButton.clicked.connect(lambda: self.showExample())
        self.netFilepathButton.clicked.connect(lambda: self.choosenetFile(self.netFilepathEdit))

        self.netLayout_firstRow.addWidget(self.net_label1)
        self.netLayout_firstRow.addWidget(self.netFilepathEdit)
        self.netLayout_firstRow.addWidget(self.exampleButton)
        self.netLayout_firstRow.addWidget(self.netFilepathButton)

        self.netLayout.addLayout(self.netLayout_firstRow)
        self.netLayout.addWidget(self.net_label2)

        self.netbox.setLayout(self.netLayout)

        # 超参数设置.
        self.hyperCheckbox4.setChecked(True)
        self.hyperLayout_firstRow.addWidget(self.hyperlabel_1)
        self.hyperLayout_firstRow.addWidget(self.hyperCheckbox1)
        self.hyperLayout_firstRow.addWidget(self.hyperCheckbox2)
        self.hyperLayout_firstRow.addWidget(self.hyperCheckbox3)
        self.hyperLayout_firstRow.addWidget(self.hyperCheckbox4)
        self.hyperLayout_firstRow.addWidget(self.hyperCheckbox5)
        self.hyperLayout_firstRow.addStretch()

        self.hyperDefault1.setFixedWidth(80)
        self.hyperDefault2.setFixedWidth(80)
        self.hyperDefault3.setFixedWidth(80)
        self.hyperDefault4.setFixedWidth(80)
        self.hyperDefault5.setFixedWidth(80)
        self.hyperMin1.setFixedWidth(80)
        self.hyperMax1.setFixedWidth(80)
        self.hyperMin2.setFixedWidth(80)
        self.hyperMax2.setFixedWidth(80)
        self.hyperMin3.setFixedWidth(80)
        self.hyperMax3.setFixedWidth(80)
        self.hyperMin4.setFixedWidth(80)
        self.hyperMax4.setFixedWidth(80)
        self.hyperMin5.setFixedWidth(80)
        self.hyperMax5.setFixedWidth(80)

        # 超参数默认取值和上下限值只能输入浮点数或整数(整数限定).
        self.hyperDefault1.setValidator(QIntValidator())
        self.hyperDefault2.setValidator(QIntValidator())
        self.hyperDefault3.setValidator(QIntValidator())
        self.hyperDefault4.setValidator(QDoubleValidator())
        self.hyperDefault5.setValidator(QDoubleValidator())
        self.hyperMin1.setValidator(QIntValidator())
        self.hyperMax1.setValidator(QIntValidator())
        self.hyperMin2.setValidator(QIntValidator())
        self.hyperMax2.setValidator(QIntValidator())
        self.hyperMin3.setValidator(QIntValidator())
        self.hyperMax3.setValidator(QIntValidator())
        self.hyperMin4.setValidator(QDoubleValidator())
        self.hyperMax4.setValidator(QDoubleValidator())
        self.hyperMin5.setValidator(QDoubleValidator())
        self.hyperMax5.setValidator(QDoubleValidator())

        self.hyperLayout_secondRow.addWidget(self.hyperlabel_2)
        self.hyperLayout_secondRow.addWidget(self.hyperlabel1)
        self.hyperLayout_secondRow.addWidget(self.hyperDefault1)
        self.hyperLayout_secondRow.addWidget(self.hyperlabel2)
        self.hyperLayout_secondRow.addWidget(self.hyperDefault2)
        self.hyperLayout_secondRow.addWidget(self.hyperlabel3)
        self.hyperLayout_secondRow.addWidget(self.hyperDefault3)
        self.hyperLayout_secondRow.addWidget(self.hyperlabel4)
        self.hyperLayout_secondRow.addWidget(self.hyperDefault4)
        self.hyperLayout_secondRow.addWidget(self.hyperlabel5)
        self.hyperLayout_secondRow.addWidget(self.hyperDefault5)
        self.hyperLayout_secondRow.addStretch()

        self.hyperMin1.setPlaceholderText('下限')
        self.hyperMax1.setPlaceholderText('上限')
        self.hyperMin2.setPlaceholderText('下限')
        self.hyperMax2.setPlaceholderText('上限')
        self.hyperMin3.setPlaceholderText('下限')
        self.hyperMax3.setPlaceholderText('上限')
        self.hyperMin4.setPlaceholderText('下限')
        self.hyperMax4.setPlaceholderText('上限')
        self.hyperMin5.setPlaceholderText('下限')
        self.hyperMax5.setPlaceholderText('上限')
        self.hyperLayout_thirdRow.addWidget(self.hyperlabel_3, 0, 0, 2, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperlabel1s, 0, 1, 2, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMin1, 0, 2, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMax1, 1, 2, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperlabel2s, 0, 3, 2, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMin2, 0, 4, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMax2, 1, 4, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperlabel3s, 0, 5, 2, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMin3, 0, 6, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMax3, 1, 6, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperlabel4s, 0, 7, 2, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMin4, 0, 8, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMax4, 1, 8, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperlabel5s, 0, 9, 2, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMin5, 0, 10, 1, 1)
        self.hyperLayout_thirdRow.addWidget(self.hyperMax5, 1, 10, 1, 1)

        self.hyperLayout.addLayout(self.hyperLayout_firstRow)
        self.hyperLayout.addLayout(self.hyperLayout_secondRow)
        self.hyperLayout.addLayout(self.hyperLayout_thirdRow)
        self.hyperLayout.addWidget(self.hyperlabel_4)
        self.hyperbox.setLayout(self.hyperLayout)

        # 超参数优化器:网格搜索.
        self.opt_radio1.setChecked(True)
        self.optEdit_11.setFixedWidth(80)
        self.optEdit_12.setFixedWidth(80)
        self.optEdit_13.setFixedWidth(80)
        self.optEdit_14.setFixedWidth(80)
        self.optEdit_15.setFixedWidth(80)
        self.line41.setFrameShape(4)
        self.line41.setFrameShadow(0x030)

        self.optEdit_11.setValidator(QIntValidator())
        self.optEdit_12.setValidator(QIntValidator())
        self.optEdit_13.setValidator(QIntValidator())
        self.optEdit_14.setValidator(QDoubleValidator())
        self.optEdit_15.setValidator(QDoubleValidator())

        self.optLayout_1.addWidget(self.opt_radio1, 0, 0, 2, 2)
        self.optLayout_1.addWidget(self.optlabel_11, 0, 2, 1, 1)
        self.optLayout_1.addWidget(self.optlabel_12, 0, 3, 1, 1)
        self.optLayout_1.addWidget(self.optEdit_11, 0, 4, 1, 3)
        self.optLayout_1.addWidget(self.optlabel_13, 0, 7, 1, 2)
        self.optLayout_1.addWidget(self.optEdit_12, 0, 9, 1, 3)
        self.optLayout_1.addWidget(self.optlabel_14, 0, 12, 1, 2)
        self.optLayout_1.addWidget(self.optEdit_13, 0, 14, 1, 3)
        self.optLayout_1.addWidget(self.optlabel_15, 0, 17, 1, 2)
        self.optLayout_1.addWidget(self.optEdit_14, 0, 19, 1, 3)
        self.optLayout_1.addWidget(self.optlabel_16, 0, 22, 1, 2)
        self.optLayout_1.addWidget(self.optEdit_15, 0, 24, 1, 3)
        self.optLayout_1.addWidget(self.optlabel_17, 1, 2, 1, 10)
        self.optLayout_1.setAlignment(Qt.AlignLeft)

        # 超参数优化器:随机搜索.
        self.optEdit_2.setFixedWidth(100)
        self.line42.setFrameShape(4)
        self.line42.setFrameShadow(0x030)

        self.optEdit_2.setValidator(QIntValidator())

        self.optLayout_2.addWidget(self.opt_radio2)
        self.optLayout_2.addWidget(self.optlabel_2)
        self.optLayout_2.addWidget(self.optEdit_2)
        self.optLayout_2.addStretch()

        # 超参数优化器:贝叶斯优化.
        self.bayesian_radio1.setChecked(True)
        self.optEdit_31.setFixedWidth(120)
        self.optEdit_32.setFixedWidth(120)
        self.optEdit_33.setFixedWidth(120)
        self.optEdit_34.setFixedWidth(120)
        self.line43.setFrameShape(4)
        self.line43.setFrameShadow(0x030)

        self.optEdit_31.setValidator(QIntValidator())
        self.optEdit_32.setValidator(QIntValidator())
        self.optEdit_33.setValidator(QDoubleValidator())
        self.optEdit_34.setValidator(QDoubleValidator())

        self.optLayout_3.addWidget(self.opt_radio3, 0, 0, 2, 2)
        self.optLayout_3.addWidget(self.optlabel_31, 0, 2, 1, 2)
        self.optLayout_3.addWidget(self.optEdit_31, 0, 4, 1, 2)
        self.optLayout_3.addWidget(self.optlabel_32, 0, 6, 1, 2)
        self.optLayout_3.addWidget(self.optEdit_32, 0, 8, 1, 2)
        self.optLayout_3.addWidget(self.optlabel_33, 1, 2, 1, 3)
        self.optLayout_3.addWidget(self.bayesian_radio1, 1, 5, 1, 1)
        self.optLayout_3.addWidget(self.bayesian_radio2, 1, 6, 1, 1)
        self.optLayout_3.addWidget(self.bayesian_radio3, 1, 7, 1, 1)
        self.optLayout_3.addWidget(self.optlabel_34, 1, 8, 1, 1)
        self.optLayout_3.addWidget(self.optEdit_33, 1, 9, 1, 2)
        self.optLayout_3.addWidget(self.optlabel_35, 1, 11, 1, 1)
        self.optLayout_3.addWidget(self.optEdit_34, 1, 12, 1, 2)

        # 超参数优化器:遗传算法.
        self.optEdit_41.setFixedWidth(100)
        self.optEdit_42.setFixedWidth(100)
        self.optEdit_43.setFixedWidth(100)
        self.optEdit_44.setFixedWidth(100)
        self.optEdit_45.setFixedWidth(100)
        self.line44.setFrameShape(4)
        self.line44.setFrameShadow(0x030)

        self.optEdit_41.setValidator(QIntValidator())
        self.optEdit_42.setValidator(QIntValidator())
        self.optEdit_43.setValidator(QDoubleValidator())
        self.optEdit_44.setValidator(QDoubleValidator())
        self.optEdit_45.setValidator(QIntValidator())

        self.optLayout_4.addWidget(self.opt_radio4, 0, 0, 2, 2)
        self.optLayout_4.addWidget(self.optlabel_41, 0, 2, 1, 3)
        self.optLayout_4.addWidget(self.optEdit_41, 0, 5, 1, 3)
        self.optLayout_4.addWidget(self.optlabel_42, 0, 8, 1, 3)
        self.optLayout_4.addWidget(self.optEdit_42, 0, 11, 1, 3)
        self.optLayout_4.addWidget(self.optlabel_43, 1, 2, 1, 3)
        self.optLayout_4.addWidget(self.optEdit_43, 1, 5, 1, 3)
        self.optLayout_4.addWidget(self.optlabel_44, 1, 8, 1, 3)
        self.optLayout_4.addWidget(self.optEdit_44, 1, 11, 1, 3)
        self.optLayout_4.addWidget(self.optlabel_45, 1, 14, 1, 3)
        self.optLayout_4.addWidget(self.optEdit_45, 1, 17, 1, 3)

        # 超参数优化器:粒子群算法.
        self.optEdit_51.setFixedWidth(120)
        self.optEdit_52.setFixedWidth(120)
        self.optEdit_53.setFixedWidth(120)
        self.optEdit_54.setFixedWidth(90)
        self.optEdit_55.setFixedWidth(90)
        self.optEdit_56.setFixedWidth(90)
        self.optEdit_57.setFixedWidth(90)

        self.optEdit_51.setValidator(QIntValidator())
        self.optEdit_52.setValidator(QIntValidator())
        self.optEdit_53.setValidator(QIntValidator())
        self.optEdit_54.setValidator(QDoubleValidator())
        self.optEdit_55.setValidator(QDoubleValidator())
        self.optEdit_56.setValidator(QDoubleValidator())
        self.optEdit_57.setValidator(QDoubleValidator())

        self.optLayout_5.addWidget(self.opt_radio5, 0, 0, 2, 4)
        self.optLayout_5.addWidget(self.optlabel_51, 0, 6, 1, 4)
        self.optLayout_5.addWidget(self.optEdit_51, 0, 10, 1, 5)
        self.optLayout_5.addWidget(self.optlabel_52, 0, 15, 1, 4)
        self.optLayout_5.addWidget(self.optEdit_52, 0, 19, 1, 5)
        self.optLayout_5.addWidget(self.optlabel_53, 0, 24, 1, 4)
        self.optLayout_5.addWidget(self.optEdit_53, 0, 28, 1, 5)
        self.optLayout_5.addWidget(self.optlabel_54, 1, 6, 1, 3)
        self.optLayout_5.addWidget(self.optEdit_54, 1, 9, 1, 4)
        self.optLayout_5.addWidget(self.optlabel_55, 1, 13, 1, 3)
        self.optLayout_5.addWidget(self.optEdit_55, 1, 16, 1, 4)
        self.optLayout_5.addWidget(self.optlabel_56, 1, 20, 1, 3)
        self.optLayout_5.addWidget(self.optEdit_56, 1, 23, 1, 4)
        self.optLayout_5.addWidget(self.optlabel_57, 1, 27, 1, 3)
        self.optLayout_5.addWidget(self.optEdit_57, 1, 30, 1, 4)

        self.optLayout.addLayout(self.optLayout_1)
        self.optLayout.addWidget(self.line41)
        self.optLayout.addLayout(self.optLayout_2)
        self.optLayout.addWidget(self.line42)
        self.optLayout.addLayout(self.optLayout_3)
        self.optLayout.addWidget(self.line43)
        self.optLayout.addLayout(self.optLayout_4)
        self.optLayout.addWidget(self.line44)
        self.optLayout.addLayout(self.optLayout_5)
        self.optbox.setLayout(self.optLayout)
        
        # 其他设置.
        self.extraLayout.addWidget(self.extraCheckbox_1)
        self.extraLayout.addWidget(self.extralabel_1)
        self.extraLayout.addStretch()
        self.extrabox.setLayout(self.extraLayout)

        # 最下层按钮.
        self.bottom_tipButton.clicked.connect(lambda: self.showTip())

        self.bottomLayout.addWidget(self.bottom_startButton)
        self.bottomLayout.addWidget(self.bottom_clearButton)
        self.bottomLayout.addWidget(self.bottom_tipButton)
        self.bottomLayout.setDirection(1)
        self.bottomLayout.addStretch(0)

        self.setboxStyle()
        self.setTips()

        self.main_layout.addWidget(self.datasetbox)
        self.main_layout.addWidget(self.netbox)
        self.main_layout.addWidget(self.hyperbox)
        self.main_layout.addWidget(self.optbox)
        self.main_layout.addWidget(self.extrabox)
        self.main_layout.addLayout(self.bottomLayout)

        self.main_widget.setLayout(self.main_layout)
        self.scrollArea.setWidget(self.main_widget)

    def chooseFilePath(self, edit):
        fileName = QFileDialog.getExistingDirectory(self, '选择数据集路径', 'C:/')
        edit.setText(fileName)

    def choosedatasetFile(self, edit):
        fileName, fileType = QFileDialog.getOpenFileName(self, '选择数据集文件', 'C:/')
        edit.setText(fileName)

    def choosenetFile(self, edit):
        fileName, fileType = QFileDialog.getOpenFileName(self, '选择网络模型', 'C:/', 'Python File(*py)')
        edit.setText(fileName)

    def showTip(self):
        dialogLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.tip_dialog = QDialog()
        self.tip_label = QLabel()
        self.tip_button = QPushButton('确定')

        self.tip_label.setText('1.如果对超参数优化的目标比较宽松,想通过比较少的迭代找到一个较好的超参数即可:建议使用贝叶斯优化或者随机搜索.\n'
                           '2.如果希望找到表现尽可能好的超参数,但对时间要求比较紧:建议使用贝叶斯优化.\n'
                           '3.如果希望找到表现尽可能好的超参数,但对时间要求比较宽松:建议使用贝叶斯优化或者粒子群算法.\n'
                           '4.如果目标是找到一个包含数个超参数取值的,表现较好的超参数取值集合:建议使用遗传算法.\n'
                           '5.如果允许进行的优化迭代次数极少,可以考虑使用网格搜索或者随机搜索这类比较简单的优化方法.\n'
                           '6.如果待优化的超参数数量较多,不建议使用网格搜索.\n'
                           '7.如果初步优化结果发现最优超参数取值集中在极小的范围内,贝叶斯优化的表现可能比较好.\n'
                           '8.如果初步优化结果发现在超参数取值在较大范围内都有相近的表现,则不建议使用遗传算法,因为很容易陷入局部最优.\n'
                           '9.在网络模型的稳定性非常差或者非常好的情况下,均建议使用贝叶斯优化.\n'
                               '前者是因为贝叶斯优化更容易捕捉较优取值的细节,后者是因为可以充分发挥贝叶斯优化的优势.\n'
                           '10.单超参数优化问题可以倾向于使用随机搜索和贝叶斯优化,但多参数优化问题中遗传算法和粒子群算法会有同样不错的表现.\n')

        self.tip_label.setStyleSheet('''
                    QLabel {
                        font-family: "Dengxian";
                        font: 16px;
                    }
                ''')
        self.tip_button.setStyleSheet('''
                    QPushButton {
                        background-color: #666666;
                        border: 1px solid #ffffff;
                        color: #F0F0F0;
                        border-radius: 4px;
                        padding: 3px;
                        outline: none;
                        font: 16px;
                        font-family = "Dengxian"
                        min-width: 80px;
                        min-height: 30px;
                    }
                    QPushButton:pressed {
                        background-color: #19232D;
                        border: 1px solid #19232D;
                    }
                    QPushButton:hover {
                        border: 1px solid #000000;
                    }
                ''')

        self.tip_dialog.setWindowTitle('关于超参数优化器选择的提示')
        self.tip_dialog.setWindowIcon(QIcon('icon/example.png'))

        self.tip_button.setFixedWidth(160)
        self.tip_button.clicked.connect(lambda: self.ok(2))

        buttonLayout.addWidget(self.tip_button)
        buttonLayout.setDirection(1)
        buttonLayout.addStretch()

        dialogLayout.addWidget(self.tip_label)
        dialogLayout.addLayout(buttonLayout)
        self.tip_dialog.setLayout(dialogLayout)

        self.tip_dialog.setWindowModality(Qt.ApplicationModal)
        self.tip_dialog.exec_()

    def showExample(self):
        dialogLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()

        self.example_dialog = QDialog()
        self.example_label = QLabel()
        self.example_button = QPushButton('确定')

        self.example_label.setText('from torch import nn\n'
                           'class Net(nn.Module):\n'
                           '\tdef __init__(self):\n'
                           '\t\tsuper(mnistNet, self).__init__()\n'
                           '\t\tself.conv2d = nn.Sequential(\n'
                           '\t\t\tnn.Conv2d(1, 16, kernel_size = 5),\n'
                           '\t\t\tnn.ReLU(),\n'
                           '\t\t\tnn.MaxPool2d(2, 2)\n'
                           '\t\t)\n'
                           '\t\tself.fc=nn.Sequential(\n'
                           '\t\t\tnn.Linear(64 * 12 * 12, 84),\n'
                           '\t\t\tnn.Dropout2d(0.5),\n'
                           '\t\t\tnn.Linear(84, 10)\n'
                           '\t\t)\n\n'
                           '\tdef forward(self, img):\n'
                           '\t\tfeatures = self.conv2d(img)\n'
                           '\t\toutputs = self.fc(features.view(features.shape[0], -1))\n'
                           '\t\treturn outputs\n\n'
                           '# 务必以net变量名赋值!!!!!!!\n'
                           'net = Net()')

        self.example_label.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 16px;
            }
        ''')
        self.example_button.setStyleSheet('''
            QPushButton {
                background-color: #666666;
                border: 1px solid #ffffff;
                color: #F0F0F0;
                border-radius: 4px;
                padding: 3px;
                outline: none;
                font: 16px;
                font-family = "Dengxian"
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:pressed {
                background-color: #19232D;
                border: 1px solid #19232D;
            }
            QPushButton:hover {
                border: 1px solid #000000;
            }
        ''')

        self.example_dialog.setWindowTitle('模型文件代码格式示例')
        self.example_dialog.setWindowIcon(QIcon('icon/example.png'))

        self.example_button.setFixedWidth(100)
        self.example_button.clicked.connect(lambda: self.ok(1))

        buttonLayout.addWidget(self.example_button)
        buttonLayout.setDirection(1)
        buttonLayout.addStretch()

        dialogLayout.addWidget(self.example_label)
        dialogLayout.addLayout(buttonLayout)
        self.example_dialog.setLayout(dialogLayout)

        self.example_dialog.setWindowModality(Qt.ApplicationModal)
        self.example_dialog.exec_()

    def ok(self, num):
        if num == 1:
            self.example_dialog.close()
        elif num == 2:
            self.tip_dialog.close()

    def setboxStyle(self):
        self.datasetbox.setStyleSheet('''
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-family: "Dengxian";
                font: 15px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                margin-top: 0px;
            }
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #666666;
                border-radius: 2px;
                min-height: 22px;
            }
        ''')
        self.netbox.setStyleSheet('''
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-family: "Dengxian";
                font: 15px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                margin-top: 0px;
            }
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #666666;
                border-radius: 2px;
                min-height: 22px;
            }
        ''')
        self.hyperbox.setStyleSheet('''
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-family: "Dengxian";
                font: 15px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                margin-top: 0px;
            }
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #666666;
                border-radius: 2px;
                min-height: 22px;
            }
        ''')
        self.optbox.setStyleSheet('''
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-family: "Dengxian";
                font: 15px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                margin-top: 0px;
            }
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #666666;
                border-radius: 2px;
                min-height: 22px;
            }
        ''')
        self.extrabox.setStyleSheet('''
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-family: "Dengxian";
                font: 15px;
                margin-top: 6px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                margin-top: 0px;
            }
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #666666;
                border-radius: 2px;
                min-height: 22px;
            }
        ''')

    def setTips(self):
        self.optEdit_31.setToolTip("建议适当多取预设数,可以使建模更加完善.")
        self.optEdit_33.setToolTip("κ的取值越小,越偏向探索;取值越大,越偏向利用.中间值建议取2.5左右.")
        self.optEdit_34.setToolTip("χ的取值越小,越偏向利用;取值越大,越偏向探索.建议取值接近于0.0.")

        self.optEdit_42.setToolTip("在超参数取值范围较大或数量较多的情况下,建议适当增加种群数量.")
        self.optEdit_43.setToolTip("建议取值≈0.5.需要更大随机性可以取更高值.")
        self.optEdit_44.setToolTip("建议取值≈0.05.需要更大随机性可以取更高值.")
        self.optEdit_45.setToolTip("建议取值为10.编码长度越大,取值越精细,计算复杂度越高.")

        self.optEdit_54.setToolTip("建议取值2.0.和全局信息权重取相同值有更好的效果.")
        self.optEdit_55.setToolTip("建议取值2.0.和局部信息权重取相同值有更好的效果.")
        self.optEdit_56.setToolTip("建议下限不要过于接近0.")
        self.optEdit_57.setToolTip("建议上限不要过于接近1.")