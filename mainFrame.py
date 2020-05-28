import os
import sys
import Qtwindow.pageOne as one
import Qtwindow.pageTwo as two
import Qtwindow.pageThree as three
import Qtwindow.pageFour as four
import Qtwindow.pageFive as five
from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import shutil
import pymysql
import qtawesome
import global_variable
import Qtwindow.optThread as optThread
import Qtwindow.datasetThread as datasetThread

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setFixedSize(1358, 800)
        self.setWindowTitle('Hyperparameter optimization')
        self.setWindowIcon(QIcon('icon/logo.png'))
        self.setWindowOpacity(0.9) # 设置窗口透明度
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.mysql_flag = True

        self.MySQL_init()

        self.DB_init()
        self.UI_init()
        self.logical_init()

    def MySQL_init(self):
        if not(os.path.exists('MySQL.txt')):
            self.getMySQL()

        else:
            with open('MySQL.txt', 'r') as f:
                global_variable.host = f.readline()[:-1]
                global_variable.user = f.readline()[:-1]
                global_variable.password = f.readline()[:-1]
                self.mysql_flag = False

    def DB_init(self):
        # 如果用户根本没有设置数据库相关内容直接关闭窗口,则整个程序直接关闭.
        if self.mysql_flag:
            sys.exit(0)

        else:
            connection = pymysql.connect(
                host=global_variable.host,
                user=global_variable.user,
                password=global_variable.password,
                charset='utf8'
            )
            cursor = connection.cursor()

            # 如果目前数据库中不存在指定的数据库和数据库表,则需要创建一个.
            cursor.execute("create database if not exists opt;")
            cursor.execute("use opt;")

            cursor.execute("select count(*) from information_schema.TABLES t where t.TABLE_SCHEMA = 'opt' and t.TABLE_NAME = 'opthistory';")
            if int((cursor.fetchone())[0]) == 0:
                cursor.execute("create table opthistory(id int not null auto_increment, dataset varchar(50) not null, optimization varchar(20) not null, best_param varchar(200) not null, best_acc double not null, testFig varchar(50), bestFig varchar(50), result varchar(50), primary key (id));")

            # 获取数据库表中现有的条目数.用于在pageThree.py中显示表格.
            cursor.execute("select count(*) from opthistory;")
            global_variable.num_exist = int((cursor.fetchone())[0])
            print('start: global_variable.num_exist = ' + str(global_variable.num_exist))

            # 获取数据库表中下一个应该被插入的id数.是当前数据库表中最新条目的id值+1.
            cursor.execute("select max(id) from opthistory;")
            global_variable.num_opt = int((cursor.fetchone())[0]) + 1
            print('start: global_variable.num_opt = ' + str(global_variable.num_opt))

            cursor.close()
            connection.close()

    def UI_init(self):
        # 窗口主部件.
        self.mainWidget = QWidget()
        self.mainLayout = QGridLayout()
        self.mainWidget.setLayout(self.mainLayout)

        # 窗口左侧按钮边栏.
        self.sideWidget = QWidget()
        self.sideLayout = QGridLayout()
        self.sideWidget.setLayout(self.sideLayout)

        # 实体化子界面widget.
        self.firstWidget = one.oneWidget()
        self.secondWidget = two.twoWidget()
        self.thirdWidget = three.threeWidget()
        self.forthWidget = four.fourWidget()
        self.fifthWidget = five.fiveWidget()

        # 窗口右侧显示区域.
        self.stackWidget = QStackedWidget()
        self.stackWidget.addWidget(self.firstWidget.getWidget())
        self.stackWidget.addWidget(self.secondWidget.getWidget())
        self.stackWidget.addWidget(self.thirdWidget.getWidget())
        self.stackWidget.addWidget(self.forthWidget.getWidget())
        self.stackWidget.addWidget(self.fifthWidget.getWidget())

        self.mainLayout.addWidget(self.sideWidget, 0, 0, 12, 2)
        self.mainLayout.addWidget(self.stackWidget, 0, 2, 12, 10)
        self.mainLayout.setSpacing(0)
        self.setCentralWidget(self.mainWidget)

        self.setStyle()

        self.header_image = QLabel()
        self.header_image.setPixmap(QPixmap('icon/tiger.jpg'))

        self.button_1 = QPushButton(qtawesome.icon('fa.star', color = 'white', scale_factor = 1.2), '新建超参数优化')
        self.button_1.setObjectName("button_1")
        self.button_1.clicked.connect(self.on_pushButton1_clicked)

        self.button_2 = QPushButton(qtawesome.icon('fa.legal', color = 'white', scale_factor = 1.2), '正在优化...')
        self.button_2.setObjectName("button_2")
        self.button_2.clicked.connect(self.on_pushButton2_clicked)

        self.button_3 = QPushButton(qtawesome.icon('fa.flag', color = 'white', scale_factor = 1.2), '历史优化记录')
        self.button_3.setObjectName("button_3")
        self.button_3.clicked.connect(self.on_pushButton3_clicked)

        self.button_4 = QPushButton(qtawesome.icon('fa.tasks', color = 'white', scale_factor = 1.2), '文本编辑区')
        self.button_4.setObjectName("button_4")
        self.button_4.clicked.connect(self.on_pushButton4_clicked)

        self.button_5 = QPushButton(qtawesome.icon('fa.link', color = 'white', scale_factor = 1.2), '获取帮助')
        self.button_5.setObjectName("button_5")
        self.button_5.clicked.connect(self.on_pushButton5_clicked)

        self.button_mini = QPushButton("")
        self.button_close = QPushButton("")
        self.button_mini.clicked.connect(lambda: self.miniButton())
        self.button_close.clicked.connect(self.close)
        self.button_mini.setFixedSize(25, 25)
        self.button_close.setFixedSize(25, 25)
        self.button_mini.setStyleSheet('''
            QPushButton {
                background: #6DDF6D;
                border-radius: 5px;
            }
            QPushButton:hover  {
                background: green;
                border-left: 0px;
            }
        ''')
        self.button_close.setStyleSheet('''
            QPushButton {
                background: #F76677;
                border-radius: 5px;
            }
            QPushButton:hover  {
                background: red;
                border-left: 0px;
            }
        ''')

        self.sideLayout.addWidget(self.button_mini, 0, 1, 1, 1)
        self.sideLayout.addWidget(self.button_close, 0, 3, 1, 1)
        self.sideLayout.addWidget(self.header_image, 1, 0, 1, 5)
        self.sideLayout.addWidget(self.button_1, 2, 0, 2, 5)
        self.sideLayout.addWidget(self.button_2, 4, 0, 2, 5)
        self.sideLayout.addWidget(self.button_3, 6, 0, 2, 5)
        self.sideLayout.addWidget(self.button_4, 8, 0, 2, 5)
        self.sideLayout.addWidget(self.button_5, 10, 0, 2, 5)

    def logical_init(self):
        # 第一子界面按钮跳转第二子界面.
        self.firstWidget.bottom_startButton.clicked.connect(lambda: self.startTrain())
        # 清空所有输入框信息.
        self.firstWidget.bottom_clearButton.clicked.connect(lambda: self.clearEdit())
        # 限制k折交叉验证按钮是否可选.
        self.firstWidget.data_radio1.toggled.connect(lambda: self.k_fold_enabled())
        self.firstWidget.data_radio2.toggled.connect(lambda: self.k_fold_enabled())
        self.firstWidget.data_radio3.toggled.connect(lambda: self.k_fold_enabled())
        self.firstWidget.filepathEdit22.textChanged.connect(lambda: self.k_fold_enabled())
        self.firstWidget.filepathEdit32.textChanged.connect(lambda: self.k_fold_enabled())
        # 训练中途退出.
        self.secondWidget.stopButton.clicked.connect(lambda: self.onclicked_stop())

    def on_pushButton1_clicked(self):
        if self.stackWidget.currentIndex() != 0:
            self.stackWidget.setCurrentIndex(0)

    def on_pushButton2_clicked(self):
        if self.stackWidget.currentIndex() != 1:
            self.stackWidget.setCurrentIndex(1)

    def on_pushButton3_clicked(self):
        if self.stackWidget.currentIndex() != 2:
            self.stackWidget.setCurrentIndex(2)
            self.thirdWidget.init_form()

    def on_pushButton4_clicked(self):
        if self.stackWidget.currentIndex() != 3:
            self.stackWidget.setCurrentIndex(3)

    def on_pushButton5_clicked(self):
        if self.stackWidget.currentIndex() != 4:
            self.stackWidget.setCurrentIndex(4)

    def startTrain(self):
        # 标识符.如果出现任何设定错误,都不能跳转界面.
        flag = True

        # 判断数据集输入是否存在问题.
        if not(self.firstWidget.data_radio1.isChecked()) and not(self.firstWidget.data_radio2.isChecked()) and not(self.firstWidget.data_radio3.isChecked()):
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/tip.png'))
            message.setWindowTitle('数据集设定错误')
            message.setText('请选择一个数据集来源！')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
            flag = False
        elif self.firstWidget.data_radio1.isChecked():
            if self.firstWidget.filepathEdit1.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('未选择torchvision.datasets数据集的存储路径！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif not(os.path.exists(str(self.firstWidget.filepathEdit1.text()))):
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('torchvision.datasets数据集的存储路径不存在！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
        elif self.firstWidget.data_radio2.isChecked():
            if self.firstWidget.filepathEdit21.text() == '' and self.firstWidget.filepathEdit22.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('未选择训练集和测试集图像的存储文件夹路径！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif self.firstWidget.filepathEdit21.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('未选择训练集图像的存储文件夹路径！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif not(os.path.exists(str(self.firstWidget.filepathEdit21.text()))):
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('训练集图像的存储文件夹路径不存在！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif self.firstWidget.filepathEdit22.text() != '' and not(os.path.exists(str(self.firstWidget.filepathEdit22.text()))):
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('测试集图像的存储文件夹路径不存在！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
        elif self.firstWidget.data_radio3.isChecked():
            if self.firstWidget.filepathEdit31.text() == '' and self.firstWidget.filepathEdit32.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('未选择作为训练集和测试集的.csv文件！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif self.firstWidget.filepathEdit31.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('未选择作为训练集的.csv文件！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif str(self.firstWidget.filepathEdit31.text()).find('.csv') == -1 or str(self.firstWidget.filepathEdit32.text()).find('.csv') == -1:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('上传的文件不是.csv类型的文件！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif not(os.path.exists(str(self.firstWidget.filepathEdit31.text()))):
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('作为训练集的.csv文件不存在！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif self.firstWidget.filepathEdit32.text() != '' and not(os.path.exists(str(self.firstWidget.filepathEdit32.text()))):
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('数据集设定错误')
                message.setText('作为测试集的.csv文件不存在！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False

        # 判断网络模型输入是否存在问题.
        if flag:
            if self.firstWidget.netFilepathEdit.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('网络定义文件设定错误')
                message.setText('未选择网络模型定义文件！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif str(self.firstWidget.netFilepathEdit.text()).find('.py') == -1:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('网络定义文件设定错误')
                message.setText('请上传.py类型的模型文件！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False

        # 判断超参数设定是否存在问题.
        if flag:
            if self.firstWidget.hyperDefault1.text() == '' or self.firstWidget.hyperDefault2.text() == '' or self.firstWidget.hyperDefault3.text() == '' or self.firstWidget.hyperDefault4.text() == '' or self.firstWidget.hyperDefault5.text() == '':
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('超参数设定错误')
                message.setText('请为所有超参数设定默认值！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif int(self.firstWidget.hyperDefault1.text()) <= 0:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('超参数设定错误')
                message.setText('超参数k的取值必须是非负整数！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif int(self.firstWidget.hyperDefault2.text()) <= 0:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('超参数设定错误')
                message.setText('超参数num_epochs的取值必须是非负整数！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif int(self.firstWidget.hyperDefault3.text()) <= 0:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('超参数设定错误')
                message.setText('超参数batch_size的取值必须是非负整数！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif float(self.firstWidget.hyperDefault4.text()) <= 0.0:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('超参数设定错误')
                message.setText('超参数learning_rate的取值必须是非负数！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False
            elif float(self.firstWidget.hyperDefault5.text()) < 0.0:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('超参数设定错误')
                message.setText('超参数weight_decay的取值必须是零或正数！')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
                flag = False

        if flag:
            if self.firstWidget.hyperCheckbox1.isChecked():
                if self.firstWidget.hyperMin1.text() == '' or self.firstWidget.hyperMax1.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('请为待优化超参数k设定取值上下限！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.hyperMin1.text()) >= int(self.firstWidget.hyperMax1.text()):
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('Qtwindow/icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数k的下限取值不能大于上限取值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.hyperMin1.text()) <=0 or int(self.firstWidget.hyperMax1.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数k的取值必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False

        if flag:
            if self.firstWidget.hyperCheckbox2.isChecked():
                if self.firstWidget.hyperMin2.text() == '' or self.firstWidget.hyperMax2.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('请为待优化超参数num_epochs设定取值上下限！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.hyperMin2.text()) >= int(self.firstWidget.hyperMax2.text()):
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数num_epochs的下限取值不能大于上限取值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.hyperMin2.text()) <= 0 or int(self.firstWidget.hyperMax2.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数num_epochs的取值必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False

        if flag:
            if self.firstWidget.hyperCheckbox3.isChecked():
                if self.firstWidget.hyperMin3.text() == '' or self.firstWidget.hyperMax3.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('请为待优化超参数batch_size设定取值上下限！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.hyperMin3.text()) >= int(self.firstWidget.hyperMax3.text()):
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数batch_size的下限取值不能大于上限取值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.hyperMin3.text()) <= 0 or int(self.firstWidget.hyperMax3.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数batch_size的取值必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False

        if flag:
            if self.firstWidget.hyperCheckbox4.isChecked():
                if self.firstWidget.hyperMin4.text() == '' or self.firstWidget.hyperMax4.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('请为待优化超参数learning_rate设定取值上下限！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.hyperMin4.text()) >= float(self.firstWidget.hyperMax4.text()):
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数learning_rate的下限取值不能大于上限取值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.hyperMin4.text()) <= 0.0 or float(self.firstWidget.hyperMax4.text()) <= 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数learning_rate的取值必须是非负数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False

        if flag:
            if self.firstWidget.hyperCheckbox5.isChecked():
                if self.firstWidget.hyperMin5.text() == '' or self.firstWidget.hyperMax5.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('请为待优化超参数weight_decay设定取值上下限！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.hyperMin5.text()) >= float(self.firstWidget.hyperMax5.text()):
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数weight_decay的下限取值不能大于上限取值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.hyperMin5.text()) <= 0.0 or float(self.firstWidget.hyperMax5.text()) <= 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数设定错误')
                    message.setText('超参数weight_decay的取值必须是非负数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False

        # 判断超参数优化器设定是否存在问题.
        if flag:
            # 网格搜索.
            if self.firstWidget.opt_radio1.isChecked():
                if self.firstWidget.hyperCheckbox1.isChecked():
                    if self.firstWidget.optEdit_11.text() == '':
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('请指定超参数k的取值步长！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                    elif int(self.firstWidget.optEdit_11.text()) <= 0:
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('超参数k的取值步长必须是非负整数！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                elif self.firstWidget.hyperCheckbox2.isChecked():
                    if self.firstWidget.optEdit_12.text() == '':
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('请指定超参数num_epochs的取值步长！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                    elif int(self.firstWidget.optEdit_12.text()) <= 0:
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('超参数num_epochs的取值步长必须是非负整数！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                elif self.firstWidget.hyperCheckbox3.isChecked():
                    if self.firstWidget.optEdit_13.text() == '':
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('请指定超参数batch_size的取值步长！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                    elif int(self.firstWidget.optEdit_13.text()) <= 0:
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('超参数batch_size的取值步长必须是非负整数！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                elif self.firstWidget.hyperCheckbox4.isChecked():
                    if self.firstWidget.optEdit_14.text() == '':
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('请指定超参数learning_rate的取值步长！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                    elif float(self.firstWidget.optEdit_14.text()) <= 0.0:
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('超参数learning_rate的取值步长必须是非负数！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                elif self.firstWidget.hyperCheckbox5.isChecked():
                    if self.firstWidget.optEdit_15.text() == '':
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('请指定超参数weight_decay的取值步长！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
                    elif float(self.firstWidget.optEdit_15.text()) <= 0.0:
                        message = QMessageBox()
                        message.setWindowIcon(QIcon('icon/tip.png'))
                        message.setWindowTitle('超参数优化器设定错误')
                        message.setText('超参数weight_decay的取值步长必须是非负数！')
                        message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                        message.exec_()
                        flag = False
            # 随机搜索.
            elif self.firstWidget.opt_radio2.isChecked():
                if self.firstWidget.optEdit_2.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定随机搜索的次数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_2.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('随机搜索的次数必须是非负数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
            # 贝叶斯优化.
            elif self.firstWidget.opt_radio3.isChecked():
                if self.firstWidget.optEdit_31.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定贝叶斯优化的预设数量！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_31.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('贝叶斯优化的预设数量必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_32.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定贝叶斯优化的预测数量！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_32.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('贝叶斯优化的预测数量必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                else:
                    if self.firstWidget.bayesian_radio1.isChecked():
                        if self.firstWidget.optEdit_33.text() == '':
                            message = QMessageBox()
                            message.setWindowIcon(QIcon('icon/tip.png'))
                            message.setWindowTitle('超参数优化器设定错误')
                            message.setText('请指定UCB采集函数的κ参数值！')
                            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                            message.exec_()
                            flag = False
                    elif self.firstWidget.bayesian_radio2.isChecked():
                        if self.firstWidget.optEdit_34.text() == '':
                            message = QMessageBox()
                            message.setWindowIcon(QIcon('icon/tip.png'))
                            message.setWindowTitle('超参数优化器设定错误')
                            message.setText('请指定EI采集函数的χ参数值！')
                            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                            message.exec_()
                            flag = False
                    elif self.firstWidget.bayesian_radio3.isChecked():
                        if self.firstWidget.optEdit_34.text() == '':
                            message = QMessageBox()
                            message.setWindowIcon(QIcon('icon/tip.png'))
                            message.setWindowTitle('超参数优化器设定错误')
                            message.setText('请指定PI采集函数的χ参数值！')
                            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                            message.exec_()
                            flag = False
            # 遗传算法.
            elif self.firstWidget.opt_radio4.isChecked():
                if self.firstWidget.optEdit_41.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定遗传算法的迭代次数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_41.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('遗传算法的迭代次数必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_42.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定遗传算法的种群大小！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_42.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('遗传算法的种群大小必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_43.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定遗传算法的个体染色体交叉概率！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_43.text()) < 0.0 or float(self.firstWidget.optEdit_43.text()) > 1.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('遗传算法的交叉概率必须在0到1之间！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_44.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定遗传算法的个体染色体变异概率！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_44.text()) < 0.0 or float(self.firstWidget.optEdit_44.text()) > 1.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('遗传算法的变异概率必须在0到1之间！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_45.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定遗传算法的个体染色体编码长度！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_45.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('遗传算法的染色体编码长度必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
            # 粒子群算法.
            elif self.firstWidget.opt_radio5.isChecked():
                if self.firstWidget.optEdit_51.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的迭代次数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_51.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的迭代次数必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_52.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的粒子群粒子数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_52.text()) <= 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的粒子群粒子数必须是非负整数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_53.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的每代新增粒子数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif int(self.firstWidget.optEdit_53.text()) < 0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的每代新增粒子数必须是零或正数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_54.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的个体信息权重c1！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_54.text()) < 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的个体信息权重c1必须是零或正数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_55.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的全局信息权重c2！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_55.text()) < 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的全局信息权重c2必须是零或正数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_54.text()) == 0.0 and float(self.firstWidget.optEdit_55.text()) == 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的个体信息权重c1和全局信息权重c2不能同时为零！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_56.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的惯性因子w的下限值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_56.text()) < 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的惯性因子w必须是零或正数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif self.firstWidget.optEdit_57.text() == '':
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('请指定粒子群算法的惯性因子w的上限值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_57.text()) < 0.0:
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的惯性因子w必须是零或正数！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False
                elif float(self.firstWidget.optEdit_56.text()) > float(self.firstWidget.optEdit_57.text()):
                    message = QMessageBox()
                    message.setWindowIcon(QIcon('icon/tip.png'))
                    message.setWindowTitle('超参数优化器设定错误')
                    message.setText('粒子群算法的惯性因子w下限值不能超过上限值！')
                    message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                    message.exec_()
                    flag = False

        # 若设定不存在输入格式错误,则整理相关参数,开始准备进行训练.
        if flag:
            if self.firstWidget.data_radio1.isChecked():
                if not(self.firstWidget.widthEdit.text() == '') and not(self.firstWidget.heightEdit.text() == ''):
                    dataset_param = {'is_torchvision': True, 'is_folder': False, 'torchvision_name': str(self.firstWidget.dataSource1.currentText()), 'train_path': None, 'test_path': None, 'aim_path': str(self.firstWidget.filepathEdit1.text()), 'resize': (int(self.firstWidget.widthEdit.text()), int(self.firstWidget.heightEdit.text()))}
                else:
                    dataset_param = {'is_torchvision': True, 'is_folder': False, 'torchvision_name': str(self.firstWidget.dataSource1.currentText()), 'train_path': None, 'test_path': None, 'aim_path': str(self.firstWidget.filepathEdit1.text()), 'resize': None}
                dataset_name = str(self.firstWidget.dataSource1.currentText())
            elif self.firstWidget.data_radio2.isChecked():
                if not(self.firstWidget.widthEdit.text() == '') and not(self.firstWidget.heightEdit.text() == ''):
                    if not(self.firstWidget.filepathEdit22.text() == ''):
                        dataset_param = {'is_torchvision': False, 'is_folder': True, 'torchvision_name': None, 'train_path': str(self.firstWidget.filepathEdit21.text()), 'test_path': str(self.firstWidget.filepathEdit22.text()), 'aim_path': None, 'resize': (int(self.firstWidget.widthEdit.text()), int(self.firstWidget.heightEdit.text()))}
                    else:
                        dataset_param = {'is_torchvision': False, 'is_folder': True, 'torchvision_name': None, 'train_path': str(self.firstWidget.filepathEdit21.text()), 'test_path': None, 'aim_path': None, 'resize': (int(self.firstWidget.widthEdit.text()), int(self.firstWidget.heightEdit.text()))}
                else:
                    if not(self.firstWidget.filepathEdit22.text() == ''):
                        dataset_param = {'is_torchvision': False, 'is_folder': True, 'torchvision_name': None, 'train_path': str(self.firstWidget.filepathEdit21.text()), 'test_path': str(self.firstWidget.filepathEdit22.text()), 'aim_path': None, 'resize': None}
                    else:
                        dataset_param = {'is_torchvision': False, 'is_folder': True, 'torchvision_name': None, 'train_path': str(self.firstWidget.filepathEdit21.text()), 'test_path': None, 'aim_path': None, 'resize': None}
                dataset_name = str(self.firstWidget.filepathEdit21.text())[str(self.firstWidget.filepathEdit21.text()).rfind('/') + 1 : ]
            elif self.firstWidget.data_radio3.isChecked():
                if not(self.firstWidget.filepathEdit32.text() == ''):
                    dataset_param = {'is_torchvision': False, 'is_folder': True, 'torchvision_name': None, 'train_path': str(self.firstWidget.filepathEdit31.text()), 'test_path': str(self.firstWidget.filepathEdit32.text()), 'aim_path': None, 'resize': None}
                else:
                    dataset_param = {'is_torchvision': False, 'is_folder': True, 'torchvision_name': None, 'train_path': str(self.firstWidget.filepathEdit31.text()), 'test_path': None, 'aim_path': None, 'resize': None}
                dataset_name = str(self.firstWidget.filepathEdit31.text())[str(self.firstWidget.filepathEdit31.text()).rfind('/') + 1 : ]

            self.dataset_thread = datasetThread.dataThread(dataset_param['is_torchvision'], dataset_param['is_folder'], dataset_param['torchvision_name'], dataset_param['train_path'], dataset_param['test_path'], dataset_param['aim_path'], dataset_param['resize'])
            self.dataset_thread.start()
            self.dialog = QDialog()
            self.showDialog()
            self.dataset_thread.wait()
            self.dialog.close()
            train_data, test_data = global_variable.train_data, global_variable.test_data

            print("train_data:", train_data)
            print("test_data:", test_data)
            print("dataset_name:", dataset_name)

            if self.firstWidget.data_radio1.isChecked():
                if self.firstWidget.extraCheckbox_1.isChecked():
                    is_k_fold = True
                    is_test = True
                else:
                    is_k_fold = False
                    is_test = True
            elif self.firstWidget.data_radio2.isChecked():
                if self.firstWidget.filepathEdit22.text() == '':
                    is_k_fold = True
                    is_test = False
                else:
                    if self.firstWidget.extraCheckbox_1.isChecked():
                        is_k_fold = True
                        is_test = True
                    else:
                        is_k_fold = False
                        is_test = True
            elif self.firstWidget.data_radio3.isChecked():
                if self.firstWidget.filepathEdit32.text() == '':
                    is_k_fold = True
                    is_test = False
                else:
                    if self.firstWidget.extraCheckbox_1.isChecked():
                        is_k_fold = True
                        is_test = True
                    else:
                        is_k_fold = False
                        is_test = True
            print('is_k_fold:', is_k_fold)
            print('is_test:', is_test)

            # 获取模型原始定义.py文件,复制到save_model文件夹下.
            net_path = str(self.firstWidget.netFilepathEdit.text())
            _, fname = os.path.split(net_path)
            aim_path = 'save_model/' + fname
            net_path = shutil.copyfile(net_path, aim_path)
            print('model_name:', net_path)

            basic_params = {'k':int(self.firstWidget.hyperDefault1.text()), 'num_epochs':int(self.firstWidget.hyperDefault2.text()), 'batch_size':int(self.firstWidget.hyperDefault3.text()), 'lr':float(self.firstWidget.hyperDefault4.text()), 'weight_decay': float(self.firstWidget.hyperDefault5.text())}
            print('basic_params:', basic_params)

            hyper_dict = {}
            if self.firstWidget.opt_radio1.isChecked():
                if self.firstWidget.hyperCheckbox1.isChecked():
                    hyper_dict['k'] = [int(self.firstWidget.hyperMin1.text()), int(self.firstWidget.hyperMax1.text()), int(self.firstWidget.optEdit_11.text())]
                if self.firstWidget.hyperCheckbox2.isChecked():
                    hyper_dict['num_epochs'] = [int(self.firstWidget.hyperMin2.text()), int(self.firstWidget.hyperMax2.text()), int(self.firstWidget.optEdit_12.text())]
                if self.firstWidget.hyperCheckbox3.isChecked():
                    hyper_dict['batch_size'] = [int(self.firstWidget.hyperMin3.text()), int(self.firstWidget.hyperMax3.text()), int(self.firstWidget.optEdit_13.text())]
                if self.firstWidget.hyperCheckbox4.isChecked():
                    hyper_dict['lr'] = [float(self.firstWidget.hyperMin4.text()), float(self.firstWidget.hyperMax4.text()), float(self.firstWidget.optEdit_14.text())]
                if self.firstWidget.hyperCheckbox1.isChecked():
                    hyper_dict['weight_decay'] = [float(self.firstWidget.hyperMin5.text()), float(self.firstWidget.hyperMax5.text()), float(self.firstWidget.optEdit_15.text())]
            elif self.firstWidget.opt_radio2.isChecked() or self.firstWidget.opt_radio3.isChecked() or self.firstWidget.opt_radio4.isChecked() or self.firstWidget.opt_radio5.isChecked():
                if self.firstWidget.hyperCheckbox1.isChecked():
                    hyper_dict['k'] = [int(self.firstWidget.hyperMin1.text()), int(self.firstWidget.hyperMax1.text())]
                if self.firstWidget.hyperCheckbox2.isChecked():
                    hyper_dict['num_epochs'] = [int(self.firstWidget.hyperMin2.text()), int(self.firstWidget.hyperMax2.text())]
                if self.firstWidget.hyperCheckbox3.isChecked():
                    hyper_dict['batch_size'] = [int(self.firstWidget.hyperMin3.text()), int(self.firstWidget.hyperMax3.text())]
                if self.firstWidget.hyperCheckbox4.isChecked():
                    hyper_dict['lr'] = [float(self.firstWidget.hyperMin4.text()), float(self.firstWidget.hyperMax4.text())]
                if self.firstWidget.hyperCheckbox1.isChecked():
                    hyper_dict['weight_decay'] = [float(self.firstWidget.hyperMin5.text()), float(self.firstWidget.hyperMax5.text())]
            print('hyper_dict:', hyper_dict)

            # 计算总共需要进行的优化次数.根据选取的优化器和相关设定值计算而出.
            if self.firstWidget.opt_radio1.isChecked():
                if self.firstWidget.hyperCheckbox1.isChecked():
                    mul_1 = int((int(self.firstWidget.hyperMax1.text()) - int(self.firstWidget.hyperMin1.text())) // int(self.firstWidget.optEdit_11.text())) + 1
                else:
                    mul_1 = 1
                if self.firstWidget.hyperCheckbox2.isChecked():
                    mul_2 = int((int(self.firstWidget.hyperMax2.text()) - int(self.firstWidget.hyperMin2.text())) // int(self.firstWidget.optEdit_12.text())) + 1
                else:
                    mul_2 = 1
                if self.firstWidget.hyperCheckbox3.isChecked():
                    mul_3 = int((int(self.firstWidget.hyperMax3.text()) - int(self.firstWidget.hyperMin3.text())) // int(self.firstWidget.optEdit_13.text())) + 1
                else:
                    mul_3 = 1
                if self.firstWidget.hyperCheckbox4.isChecked():
                    mul_4 = int((float(self.firstWidget.hyperMax4.text()) - float(self.firstWidget.hyperMin4.text())) // float(self.firstWidget.optEdit_14.text())) + 1
                else:
                    mul_4 = 1
                if self.firstWidget.hyperCheckbox5.isChecked():
                    mul_5 = int((float(self.firstWidget.hyperMax5.text()) - float(self.firstWidget.hyperMin5.text())) // float(self.firstWidget.optEdit_15.text())) + 1
                else:
                    mul_5 = 1
                num_iter = mul_1 * mul_2 * mul_3 * mul_4 * mul_5
            elif self.firstWidget.opt_radio2.isChecked():
                num_iter = int(self.firstWidget.optEdit_2.text())
            elif self.firstWidget.opt_radio3.isChecked():
                num_iter = int(self.firstWidget.optEdit_31.text()) + int(self.firstWidget.optEdit_32.text())
            elif self.firstWidget.opt_radio4.isChecked():
                num_iter = int(self.firstWidget.optEdit_41.text()) * int(self.firstWidget.optEdit_42.text())
            elif self.firstWidget.opt_radio5.isChecked():
                num_iter = int(int(self.firstWidget.optEdit_51.text()) * int(self.firstWidget.optEdit_52.text()) + (int(self.firstWidget.optEdit_51.text()) * (int(self.firstWidget.optEdit_51.text()) - 1) * int(self.firstWidget.optEdit_53.text())) / 2)
            global_variable.full_bar = num_iter
            print('num_iter:', num_iter)

            # 如果是遗传算法或者粒子群算法,绘图需要加虚线.
            if self.firstWidget.opt_radio3.isChecked():
                global_variable.axv = []
                global_variable.axv.append(int(self.firstWidget.optEdit_31.text()))
            elif self.firstWidget.opt_radio4.isChecked():
                global_variable.axv = []
                for i in range(int(self.firstWidget.optEdit_41.text())):
                    global_variable.axv.append((i + 1) * int(self.firstWidget.optEdit_42.text()))
            elif self.firstWidget.opt_radio5.isChecked():
                global_variable.axv = []
                for i in range(int(self.firstWidget.optEdit_51.text())):
                    global_variable.axv.append((i + 1) * int(self.firstWidget.optEdit_52.text()) + (i * (i + 1) / 2) * int(self.firstWidget.optEdit_53.text()))
            print("global_variable.axv:", global_variable.axv)

            '''截止上述内容为止,优化器预设值确定完毕.在数据集路径获取正确的情况下,根据用户选择的优化器信息,调用相应的优化器,开始训练.'''
            # 界面跳转.跳转时要禁止对超参数进行重复设定,除非训练正常结束或者在训练过程中手动确认退出.
            self.stackWidget.setCurrentIndex(1)
            self.secondWidget.header_label.setText('超参数优化正在进行中......')
            self.secondWidget.stopButton.setEnabled(True)
            self.banSet()

            # 线程设定.在另一个线程中进行训练.
            if self.firstWidget.opt_radio1.isChecked():
                self.train_thread = optThread.gridThread(dataset_name, is_k_fold, is_test, basic_params, hyper_dict, net_path, train_data, test_data)
            elif self.firstWidget.opt_radio2.isChecked():
                self.train_thread = optThread.randomThread(dataset_name, is_k_fold, is_test, int(self.firstWidget.optEdit_2.text()), basic_params, hyper_dict, net_path, train_data, test_data)
            elif self.firstWidget.opt_radio3.isChecked():
                if self.firstWidget.bayesian_radio1.isChecked():
                    self.train_thread = optThread.bayesianThread(dataset_name, is_k_fold, is_test, int(self.firstWidget.optEdit_31.text()), int(self.firstWidget.optEdit_32.text()), 'ucb', float(self.firstWidget.optEdit_33.text()), None, basic_params, hyper_dict, net_path, train_data, test_data)
                elif self.firstWidget.bayesian_radio2.isChecked():
                    self.train_thread = optThread.bayesianThread(dataset_name, is_k_fold, is_test, int(self.firstWidget.optEdit_31.text()), int(self.firstWidget.optEdit_32.text()), 'ei', None, float(self.firstWidget.optEdit_34.text()), basic_params, hyper_dict, net_path, train_data, test_data)
                elif self.firstWidget.bayesian_radio3.isChecked():
                    self.train_thread = optThread.bayesianThread(dataset_name, is_k_fold, is_test, int(self.firstWidget.optEdit_31.text()), int(self.firstWidget.optEdit_32.text()), 'pi', None, float(self.firstWidget.optEdit_34.text()), basic_params, hyper_dict, net_path, train_data, test_data)
            elif self.firstWidget.opt_radio4.isChecked():
                self.train_thread = optThread.geneticThread(dataset_name, is_k_fold, is_test, int(self.firstWidget.optEdit_41.text()), int(self.firstWidget.optEdit_42.text()), float(self.firstWidget.optEdit_43.text()), float(self.firstWidget.optEdit_44.text()), int(self.firstWidget.optEdit_45.text()), basic_params, hyper_dict, net_path, train_data, test_data)
            elif self.firstWidget.opt_radio5.isChecked():
                self.train_thread = optThread.psoThread(dataset_name, is_k_fold, is_test, int(self.firstWidget.optEdit_51.text()), int(self.firstWidget.optEdit_52.text()), float(self.firstWidget.optEdit_54.text()), float(self.firstWidget.optEdit_55.text()), float(self.firstWidget.optEdit_56.text()), float(self.firstWidget.optEdit_57.text()), int(self.firstWidget.optEdit_53.text()), basic_params, hyper_dict, net_path, train_data, test_data)

            # 运行获取到的优化器线程.
            self.train_thread.trigger.connect(self.overback)
            self.train_thread.start()

    def showDialog(self):
        self.dialog.setWindowTitle('正在获取数据集......')
        self.dialog.setWindowIcon(QIcon('icon/tip.png'))
        self.dialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.dialog.setFixedSize(600, 60)

        dialogLayout = QHBoxLayout()

        tipLabel = QLabel("正在获取指定数据集,该窗口关闭时说明数据集已获取完毕.请耐心等待......")
        tipLabel.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 17px;
            }
        ''')
        dialogLayout.addWidget(tipLabel)
        self.dialog.setLayout(dialogLayout)
        self.dialog.show()

    def clearEdit(self):
        self.firstWidget.filepathEdit1.clear()
        self.firstWidget.filepathEdit21.clear()
        self.firstWidget.filepathEdit22.clear()
        self.firstWidget.filepathEdit31.clear()
        self.firstWidget.filepathEdit32.clear()
        self.firstWidget.widthEdit.clear()
        self.firstWidget.heightEdit.clear()
        self.firstWidget.netFilepathEdit.clear()
        self.firstWidget.hyperDefault1.clear()
        self.firstWidget.hyperDefault2.clear()
        self.firstWidget.hyperDefault3.clear()
        self.firstWidget.hyperDefault4.clear()
        self.firstWidget.hyperDefault5.clear()
        self.firstWidget.hyperMin1.clear()
        self.firstWidget.hyperMin2.clear()
        self.firstWidget.hyperMin3.clear()
        self.firstWidget.hyperMin4.clear()
        self.firstWidget.hyperMin5.clear()
        self.firstWidget.hyperMax1.clear()
        self.firstWidget.hyperMax2.clear()
        self.firstWidget.hyperMax3.clear()
        self.firstWidget.hyperMax4.clear()
        self.firstWidget.hyperMax5.clear()
        self.firstWidget.optEdit_11.clear()
        self.firstWidget.optEdit_12.clear()
        self.firstWidget.optEdit_13.clear()
        self.firstWidget.optEdit_14.clear()
        self.firstWidget.optEdit_15.clear()
        self.firstWidget.optEdit_2.clear()
        self.firstWidget.optEdit_31.clear()
        self.firstWidget.optEdit_32.clear()
        self.firstWidget.optEdit_33.clear()
        self.firstWidget.optEdit_34.clear()
        self.firstWidget.optEdit_41.clear()
        self.firstWidget.optEdit_42.clear()
        self.firstWidget.optEdit_43.clear()
        self.firstWidget.optEdit_44.clear()
        self.firstWidget.optEdit_45.clear()
        self.firstWidget.optEdit_51.clear()
        self.firstWidget.optEdit_52.clear()
        self.firstWidget.optEdit_53.clear()
        self.firstWidget.optEdit_54.clear()
        self.firstWidget.optEdit_55.clear()
        self.firstWidget.optEdit_56.clear()
        self.firstWidget.optEdit_57.clear()

    def k_fold_enabled(self):
        if self.firstWidget.data_radio1.isChecked():
            self.firstWidget.extraCheckbox_1.setChecked(False)
            self.firstWidget.extraCheckbox_1.setEnabled(True)
        elif self.firstWidget.data_radio2.isChecked():
            if self.firstWidget.filepathEdit22.text() == '':
                self.firstWidget.extraCheckbox_1.setChecked(True)
                self.firstWidget.extraCheckbox_1.setEnabled(False)
            elif not(self.firstWidget.filepathEdit22.text() == ''):
                self.firstWidget.extraCheckbox_1.setChecked(False)
                self.firstWidget.extraCheckbox_1.setEnabled(True)
        elif self.firstWidget.data_radio3.isChecked():
            if self.firstWidget.filepathEdit32.text() == '':
                self.firstWidget.extraCheckbox_1.setChecked(True)
                self.firstWidget.extraCheckbox_1.setEnabled(False)
            elif not(self.firstWidget.filepathEdit32.text() == ''):
                self.firstWidget.extraCheckbox_1.setChecked(False)
                self.firstWidget.extraCheckbox_1.setEnabled(True)

    def allowSet(self):
        self.firstWidget.data_radio1.setEnabled(True)
        self.firstWidget.data_radio2.setEnabled(True)
        self.firstWidget.data_radio3.setEnabled(True)
        self.firstWidget.dataSource1.setEnabled(True)
        self.firstWidget.filepathEdit1.setEnabled(True)
        self.firstWidget.filepathButton1.setEnabled(True)
        self.firstWidget.filepathEdit21.setEnabled(True)
        self.firstWidget.filepathEdit22.setEnabled(True)
        self.firstWidget.filepathButton21.setEnabled(True)
        self.firstWidget.filepathButton22.setEnabled(True)
        self.firstWidget.filepathEdit31.setEnabled(True)
        self.firstWidget.filepathEdit32.setEnabled(True)
        self.firstWidget.filepathButton31.setEnabled(True)
        self.firstWidget.filepathButton32.setEnabled(True)
        self.firstWidget.widthEdit.setEnabled(True)
        self.firstWidget.heightEdit.setEnabled(True)
        self.firstWidget.netFilepathEdit.setEnabled(True)
        self.firstWidget.netFilepathButton.setEnabled(True)
        self.firstWidget.hyperCheckbox1.setEnabled(True)
        self.firstWidget.hyperCheckbox2.setEnabled(True)
        self.firstWidget.hyperCheckbox3.setEnabled(True)
        self.firstWidget.hyperCheckbox4.setEnabled(True)
        self.firstWidget.hyperCheckbox5.setEnabled(True)
        self.firstWidget.hyperDefault1.setEnabled(True)
        self.firstWidget.hyperDefault2.setEnabled(True)
        self.firstWidget.hyperDefault3.setEnabled(True)
        self.firstWidget.hyperDefault4.setEnabled(True)
        self.firstWidget.hyperDefault5.setEnabled(True)
        self.firstWidget.hyperMin1.setEnabled(True)
        self.firstWidget.hyperMax1.setEnabled(True)
        self.firstWidget.hyperMin2.setEnabled(True)
        self.firstWidget.hyperMax2.setEnabled(True)
        self.firstWidget.hyperMin3.setEnabled(True)
        self.firstWidget.hyperMax3.setEnabled(True)
        self.firstWidget.hyperMin4.setEnabled(True)
        self.firstWidget.hyperMax4.setEnabled(True)
        self.firstWidget.hyperMin5.setEnabled(True)
        self.firstWidget.hyperMax5.setEnabled(True)
        self.firstWidget.opt_radio1.setEnabled(True)
        self.firstWidget.opt_radio2.setEnabled(True)
        self.firstWidget.opt_radio3.setEnabled(True)
        self.firstWidget.opt_radio4.setEnabled(True)
        self.firstWidget.opt_radio5.setEnabled(True)
        self.firstWidget.optEdit_11.setEnabled(True)
        self.firstWidget.optEdit_12.setEnabled(True)
        self.firstWidget.optEdit_13.setEnabled(True)
        self.firstWidget.optEdit_14.setEnabled(True)
        self.firstWidget.optEdit_15.setEnabled(True)
        self.firstWidget.optEdit_2.setEnabled(True)
        self.firstWidget.optEdit_31.setEnabled(True)
        self.firstWidget.optEdit_32.setEnabled(True)
        self.firstWidget.optEdit_33.setEnabled(True)
        self.firstWidget.optEdit_34.setEnabled(True)
        self.firstWidget.bayesian_radio1.setEnabled(True)
        self.firstWidget.bayesian_radio2.setEnabled(True)
        self.firstWidget.bayesian_radio3.setEnabled(True)
        self.firstWidget.optEdit_41.setEnabled(True)
        self.firstWidget.optEdit_42.setEnabled(True)
        self.firstWidget.optEdit_43.setEnabled(True)
        self.firstWidget.optEdit_44.setEnabled(True)
        self.firstWidget.optEdit_45.setEnabled(True)
        self.firstWidget.optEdit_51.setEnabled(True)
        self.firstWidget.optEdit_52.setEnabled(True)
        self.firstWidget.optEdit_53.setEnabled(True)
        self.firstWidget.optEdit_54.setEnabled(True)
        self.firstWidget.optEdit_55.setEnabled(True)
        self.firstWidget.optEdit_56.setEnabled(True)
        self.firstWidget.optEdit_57.setEnabled(True)
        self.firstWidget.extraCheckbox_1.setEnabled(True)
        self.firstWidget.bottom_clearButton.setEnabled(True)
        self.firstWidget.bottom_startButton.setEnabled(True)

    def banSet(self):
        self.firstWidget.data_radio1.setEnabled(False)
        self.firstWidget.data_radio2.setEnabled(False)
        self.firstWidget.data_radio3.setEnabled(False)
        self.firstWidget.dataSource1.setEnabled(False)
        self.firstWidget.filepathEdit1.setEnabled(False)
        self.firstWidget.filepathButton1.setEnabled(False)
        self.firstWidget.filepathEdit21.setEnabled(False)
        self.firstWidget.filepathEdit22.setEnabled(False)
        self.firstWidget.filepathButton21.setEnabled(False)
        self.firstWidget.filepathButton22.setEnabled(False)
        self.firstWidget.filepathEdit31.setEnabled(False)
        self.firstWidget.filepathEdit32.setEnabled(False)
        self.firstWidget.filepathButton31.setEnabled(False)
        self.firstWidget.filepathButton32.setEnabled(False)
        self.firstWidget.widthEdit.setEnabled(False)
        self.firstWidget.heightEdit.setEnabled(False)
        self.firstWidget.netFilepathEdit.setEnabled(False)
        self.firstWidget.netFilepathButton.setEnabled(False)
        self.firstWidget.hyperCheckbox1.setEnabled(False)
        self.firstWidget.hyperCheckbox2.setEnabled(False)
        self.firstWidget.hyperCheckbox3.setEnabled(False)
        self.firstWidget.hyperCheckbox4.setEnabled(False)
        self.firstWidget.hyperCheckbox5.setEnabled(False)
        self.firstWidget.hyperDefault1.setEnabled(False)
        self.firstWidget.hyperDefault2.setEnabled(False)
        self.firstWidget.hyperDefault3.setEnabled(False)
        self.firstWidget.hyperDefault4.setEnabled(False)
        self.firstWidget.hyperDefault5.setEnabled(False)
        self.firstWidget.hyperMin1.setEnabled(False)
        self.firstWidget.hyperMax1.setEnabled(False)
        self.firstWidget.hyperMin2.setEnabled(False)
        self.firstWidget.hyperMax2.setEnabled(False)
        self.firstWidget.hyperMin3.setEnabled(False)
        self.firstWidget.hyperMax3.setEnabled(False)
        self.firstWidget.hyperMin4.setEnabled(False)
        self.firstWidget.hyperMax4.setEnabled(False)
        self.firstWidget.hyperMin5.setEnabled(False)
        self.firstWidget.hyperMax5.setEnabled(False)
        self.firstWidget.opt_radio1.setEnabled(False)
        self.firstWidget.opt_radio2.setEnabled(False)
        self.firstWidget.opt_radio3.setEnabled(False)
        self.firstWidget.opt_radio4.setEnabled(False)
        self.firstWidget.opt_radio5.setEnabled(False)
        self.firstWidget.optEdit_11.setEnabled(False)
        self.firstWidget.optEdit_12.setEnabled(False)
        self.firstWidget.optEdit_13.setEnabled(False)
        self.firstWidget.optEdit_14.setEnabled(False)
        self.firstWidget.optEdit_15.setEnabled(False)
        self.firstWidget.optEdit_2.setEnabled(False)
        self.firstWidget.optEdit_31.setEnabled(False)
        self.firstWidget.optEdit_32.setEnabled(False)
        self.firstWidget.optEdit_33.setEnabled(False)
        self.firstWidget.optEdit_34.setEnabled(False)
        self.firstWidget.bayesian_radio1.setEnabled(False)
        self.firstWidget.bayesian_radio2.setEnabled(False)
        self.firstWidget.bayesian_radio3.setEnabled(False)
        self.firstWidget.optEdit_41.setEnabled(False)
        self.firstWidget.optEdit_42.setEnabled(False)
        self.firstWidget.optEdit_43.setEnabled(False)
        self.firstWidget.optEdit_44.setEnabled(False)
        self.firstWidget.optEdit_45.setEnabled(False)
        self.firstWidget.optEdit_51.setEnabled(False)
        self.firstWidget.optEdit_52.setEnabled(False)
        self.firstWidget.optEdit_53.setEnabled(False)
        self.firstWidget.optEdit_54.setEnabled(False)
        self.firstWidget.optEdit_55.setEnabled(False)
        self.firstWidget.optEdit_56.setEnabled(False)
        self.firstWidget.optEdit_57.setEnabled(False)
        self.firstWidget.extraCheckbox_1.setEnabled(False)
        self.firstWidget.bottom_clearButton.setEnabled(False)
        self.firstWidget.bottom_startButton.setEnabled(False)

    def getMySQL(self):
        dialogLayout = QVBoxLayout()
        firstRowLayout = QHBoxLayout()
        secondRowLayout = QHBoxLayout()
        thirdRowLayout = QHBoxLayout()
        forthRowLayout = QHBoxLayout()

        self.mysql_dialog = QDialog()
        self.mysql_label1 = QLabel("该对话框只在最初使用时出现一次.之后会在当前目录下生成记录上述信息的MySQL.txt文件,请不要随意改动.\n\n"
                        "您只需要确定连接的MySQL数据库信息即可.数据库和数据表等会自动在您指定的数据库内创建.")
        self.mysql_label2 = QLabel("请输入MySQL主机名(本机请输入localhost):")
        self.mysql_label3 = QLabel("请输入MySQL用户名:")
        self.mysql_label4 = QLabel("请输入MySQL密码:")

        self.mysql_edit1 = QLineEdit()
        self.mysql_edit1.setFixedWidth(240)
        self.mysql_edit2 = QLineEdit()
        self.mysql_edit2.setFixedWidth(240)
        self.mysql_edit3 = QLineEdit()
        self.mysql_edit3.setFixedWidth(240)
        self.mysql_button = QPushButton("确定")
        self.mysql_button.setFixedWidth(120)

        self.mysql_dialog.setWindowTitle('初始化:数据库连接设置')
        self.mysql_dialog.setWindowIcon(QIcon('icon/over.png'))

        self.mysql_button.clicked.connect(lambda: self.mysql_init())

        firstRowLayout.addWidget(self.mysql_label2)
        firstRowLayout.addWidget(self.mysql_edit1)
        firstRowLayout.addStretch()
        secondRowLayout.addWidget(self.mysql_label3)
        secondRowLayout.addWidget(self.mysql_edit2)
        secondRowLayout.addStretch()
        thirdRowLayout.addWidget(self.mysql_label4)
        thirdRowLayout.addWidget(self.mysql_edit3)
        thirdRowLayout.addStretch()
        forthRowLayout.addWidget(self.mysql_button)
        forthRowLayout.addStretch()
        forthRowLayout.setDirection(1)

        dialogLayout.addWidget(self.mysql_label1)
        dialogLayout.addLayout(firstRowLayout)
        dialogLayout.addLayout(secondRowLayout)
        dialogLayout.addLayout(thirdRowLayout)
        dialogLayout.addLayout(forthRowLayout)

        self.mysql_dialog.setStyleSheet('''
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
            QLabel {
                font-family: "Dengxian";
                font: 17px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #666666;
                border-radius: 2px;
                min-height: 22px;
            }
        ''')

        self.mysql_dialog.setLayout(dialogLayout)

        self.mysql_dialog.setWindowModality(Qt.ApplicationModal)
        self.mysql_dialog.exec_()

    def mysql_init(self):
        if len(self.mysql_edit1.text()) == 0 or len(self.mysql_edit2.text()) == 0 or len(self.mysql_edit3.text()) == 0:
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/error.png'))
            message.setWindowTitle('数据缺失')
            message.setText('请填写完整的MySQL数据库主机名,用户名和密码.')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
        else:
            global_variable.host = str(self.mysql_edit1.text())
            global_variable.user = str(self.mysql_edit2.text())
            global_variable.password = str(self.mysql_edit3.text())
            try:
                connection = pymysql.connect(
                    host=str(self.mysql_edit1.text()),
                    user=str(self.mysql_edit2.text()),
                    password=str(self.mysql_edit3.text()),
                    charset='utf8'
                )
            except Exception:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/error.png'))
                message.setWindowTitle('数据库连接错误')
                message.setText('数据库连接失败.请您检查数据库相关信息无误,以及目标数据库已经开启服务后重新尝试连接.')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()
            else:
                global_variable.host = str(self.mysql_edit1.text())
                global_variable.user = str(self.mysql_edit2.text())
                global_variable.password = str(self.mysql_edit3.text())

                with open('MySQL.txt', 'w') as f:
                    f.write(global_variable.host + "\n")
                    f.write(global_variable.user + "\n")
                    f.write(global_variable.password + "\n")

                connection.close()
                self.mysql_flag = False
                self.mysql_dialog.close()

    def onclicked_stop(self):
        message = QMessageBox()
        message.setWindowIcon(QIcon('icon/tip.png'))
        message.setWindowTitle('确认停止优化')
        message.setText('确定停止训练吗?\n如果停止,现有的训练结果将会丢失,不会写入数据库.')
        yes = message.addButton("确定", QMessageBox.YesRole)
        no = message.addButton("取消", QMessageBox.NoRole)
        message.exec_()
        # 如果用户选择了"是",那么优化器的子线程将会被中止.
        # 在.terminate()后跟.wait()的目的是保证中止时不丢失必要信息,.wait()给线程终止时进行其他操作的空间,保证退出的安全.
        if message.clickedButton() == yes:
            self.train_thread.terminate()
            self.train_thread.wait()
            self.secondWidget.header_label.setText('超参数优化进程已人为终止.')
            self.secondWidget.progressBar.setValue(0)
            # self.stackWidget.setCurrentIndex(0)
            self.allowSet()
        else:
            pass

    def overback(self, val):
        # self.stackWidget.setCurrentIndex(0)
        self.allowSet()
        if val == 1:
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/error.png'))
            message.setWindowTitle('优化错误!')
            message.setText('找不到所需文件.请检查您上传的文件路径是否有误.')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
            self.secondWidget.header_label.setText('优化过程出现异常,已退出.')
        elif val == 2:
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/error.png'))
            message.setWindowTitle('优化错误!')
            message.setText('模型计算出现错误.请检查您的模型结构和数据集样本是否匹配.\n在两者不匹配的情况下,计算过程中会出现此类错误.\n另一个原因可能是batch_size设置的值过大,可以适当减小后再次尝试.')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
            self.secondWidget.header_label.setText('优化过程出现异常,已退出.')
        elif val == 3:
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/error.png'))
            message.setWindowTitle('优化错误!')
            message.setText('您提供的模型文件出现了问题.请务必确保您的模型文件中已经对模型实例化处理,并用net变量名承接.')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
            self.secondWidget.header_label.setText('优化过程出现异常,已退出.')
        elif val == 4:
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/error.png'))
            message.setWindowTitle('优化错误!')
            message.setText('未知错误.请仔细查看您的模型,数据集,超参数设定等是否存在问题.')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
            self.secondWidget.header_label.setText('优化过程出现异常,已退出.')

    def miniButton(self):
        self.setWindowState(Qt.WindowMinimized)

    def setStyle(self):
        leftStyle = 'style/leftSide.qss'
        with open(leftStyle, 'r') as f:
            left = f.read()
        self.sideWidget.setStyleSheet(left)

        stackStyle = 'style/stackSide.qss'
        with open(stackStyle, 'r') as f:
            stack = f.read()
        self.stackWidget.setStyleSheet(stack)

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()