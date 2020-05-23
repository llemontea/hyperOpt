from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from matplotlib.figure import Figure
import global_variable
import numpy as np
import pymysql

# 绘制图像的面板区域.
class Canvas(FigureCanvas):
    def __init__(self, title, parent = None, width = 5, height = 5, dpi = 100):
        self.fig = Figure(figsize = (width, height), dpi = dpi)
        self.fig.subplots_adjust(left=0.15, bottom=0.08, right=0.95, top=0.93, hspace = 0.2, wspace = 0.3)
        self.fig.suptitle(title)
        self.ax = self.fig.add_subplot()

        FigureCanvas.__init__(self, self.fig)

        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

class twoWidget(QWidget):
    def __init__(self):
        super(twoWidget, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.firstRow_layout = QHBoxLayout()
        self.secondRow_layout = QHBoxLayout()
        self.header_label = QLabel('当前没有正在进行的超参数优化.')
        self.target_label = QLabel('当前最优准确率:')
        self.target_value = QLabel('None')
        self.parameter_label = QLabel('当前最优超参数取值:')
        self.parameter_value = QLabel('None')

        self.thirdRow_layout = QHBoxLayout()
        self.forthRow_layout = QHBoxLayout()

        self.progressBarLabel = QLabel('当前优化进度:')
        self.progressBar = QProgressBar(self)

        self.fifthRow_layout = QHBoxLayout()
        self.stopButton = QPushButton('  停止训练!  ')

        self.test_canvas = Canvas('test_accuracy', self.main_widget, width = 3, height = 5, dpi = 100)
        self.best_canvas = Canvas('best_accuracy', self.main_widget, width = 3, height = 5, dpi = 100)
        self.test_ani = FuncAnimation(self.test_canvas.figure, self.test_update_line, interval = 10000)
        self.best_ani = FuncAnimation(self.best_canvas.figure, self.best_update_line, interval = 10000)

        self.init_widget()

    def getWidget(self):
        return self.main_widget

    def init_widget(self):
        self.firstRow_layout.addWidget(self.target_label)
        self.firstRow_layout.addWidget(self.target_value)
        self.firstRow_layout.addStretch()

        self.secondRow_layout.addWidget(self.parameter_label)
        self.secondRow_layout.addWidget(self.parameter_value)
        self.secondRow_layout.addStretch()

        self.thirdRow_layout.addWidget(self.test_canvas)
        self.thirdRow_layout.addWidget(self.best_canvas)

        self.progressBar.setValue(0)

        self.forthRow_layout.addWidget(self.progressBarLabel)
        self.forthRow_layout.addWidget(self.progressBar)

        self.stopButton.setEnabled(False)

        self.fifthRow_layout.addWidget(self.stopButton)
        self.fifthRow_layout.setDirection(1)
        self.fifthRow_layout.addStretch()

        self.main_layout.addWidget(self.header_label)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.firstRow_layout)
        self.main_layout.addLayout(self.secondRow_layout)
        self.main_layout.addLayout(self.thirdRow_layout)
        self.main_layout.addLayout(self.forthRow_layout)
        self.main_layout.addLayout(self.fifthRow_layout)

        self.main_layout.addStretch()
        self.header_label.setContentsMargins(0, 20, 0, 0)
        self.thirdRow_layout.setContentsMargins(0, 20, 0, 20)
        self.fifthRow_layout.setContentsMargins(0, 20, 0, 0)

        self.setwidgetStyle()

        self.main_widget.setLayout(self.main_layout)

    def test_update_line(self, i):
        test_x = list(np.arange(1, len(global_variable.test_acc) + 1, 1))
        test_y = global_variable.test_acc

        self.test_canvas.ax.clear()
        x_axis = list(np.arange(1, len(test_x) + 1, len(test_x) // 10 + 1))
        if len(x_axis) != 0 and x_axis[-1] != test_x[-1]:
            x_axis.append(test_x[-1])
        self.test_canvas.ax.set_xticks(x_axis)
        self.test_canvas.ax.plot(test_x, test_y)

        if len(global_variable.axv) != 0 and len(x_axis) != 0:
            for i in global_variable.axv:
                if i <= x_axis[-1]:
                    self.test_canvas.ax.axvline(i, linestyle='--')

        path_test = 'result_fig/test_' + str(global_variable.num_opt) + '.png'
        if global_variable.test_over:
            self.test_canvas.fig.savefig(path_test)
            global_variable.test_over = False

        if global_variable.after_create:
            self.update_test(path_test)
            global_variable.after_create = False
            global_variable.after_insert = True

    def best_update_line(self, i):
        best_x = list(np.arange(1, len(global_variable.best_acc) + 1, 1))
        best_y = global_variable.best_acc

        self.best_canvas.ax.clear()
        x_axis = list(np.arange(1, len(best_x) + 1, len(best_x) // 10 + 1))
        if len(x_axis) != 0 and x_axis[-1] != best_x[-1]:
            x_axis.append(best_x[-1])
        self.best_canvas.ax.set_xticks(x_axis)
        self.best_canvas.ax.plot(best_x, best_y)

        if len(global_variable.axv) != 0 and len(x_axis) != 0:
            for i in global_variable.axv:
                if i <= x_axis[-1]:
                    self.best_canvas.ax.axvline(i, linestyle='--')

        # 同步填充进度条.
        if len(x_axis) != 0 and global_variable.full_bar != 0:
            self.progressBar.setValue(best_x[-1] / global_variable.full_bar * 100)

        path_best = 'result_fig/best_' + str(global_variable.num_opt) + '.png'
        if global_variable.best_over:
            self.best_canvas.fig.savefig(path_best)
            global_variable.best_over = False

        if global_variable.after_insert:
            self.update_best(path_best)
            global_variable.after_insert = False
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/over.png'))
            message.setWindowTitle('优化完成')
            message.setText('优化已完成.结果已经写入数据库.')
            message.addButton(QPushButton("确定"), QMessageBox.YesRole)
            message.exec_()
            self.header_label.setText('本次超参数优化已完成.')
            self.stopButton.setEnabled(False)
            global_variable.num_opt += 1
            global_variable.num_exist += 1
            global_variable.full_bar = 0
            self.progressBar.setValue(0)

        if len(global_variable.best_acc) != 0:
            self.target_value.setText(str(global_variable.best_acc[-1]))
            self.parameter_value.setText(str(global_variable.best_param).replace('\'', ''))
        else:
            self.target_value.setText('None')
            self.parameter_value.setText('None')

    def update_test(self, path):
        connection = pymysql.connect(
            host=global_variable.host,
            user=global_variable.user,
            password=global_variable.password,
            database='opt',
            charset='utf8'
        )
        cursor = connection.cursor()

        sql = "update opthistory set testFig = '" + path + "' where id = " + str(global_variable.num_opt) + ";"
        print('test_fig:', sql)
        result = cursor.execute(sql)
        connection.commit()
        if result:
            print('insert row in opthistory successfully.')
        else:
            print('insert row in opthistory unsuccessfully.')

        cursor.close()
        connection.close()

    def update_best(self, path):
        connection = pymysql.connect(
            host=global_variable.host,
            user=global_variable.user,
            password=global_variable.password,
            database='opt',
            charset='utf8'
        )
        cursor = connection.cursor()

        sql = "update opthistory set bestFig = '" + path + "' where id = " + str(global_variable.num_opt) + ";"
        print('best_fig:', sql)
        result = cursor.execute(sql)
        connection.commit()
        if result:
            print('insert row in opthistory successfully.')
        else:
            print('insert row in opthistory unsuccessfully.')

        cursor.close()
        connection.close()

    def setwidgetStyle(self):
        self.main_widget.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 18px;
                vertical-align: middle;
            }
            QProgressBar {
                border: 1px solid #666666;
                text-align: center;
                border-radius: 1px;
                font-family: "Dengxian";
                font: 18px;
            }
            QProgressBar::chunk {
                background-color: #cccccc;
            }
        ''')