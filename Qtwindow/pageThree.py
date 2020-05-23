from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PIL import Image
import global_variable
import pymysql
import os

class threeWidget(QWidget):
    def __init__(self):
        super(threeWidget, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.bottom_layout = QHBoxLayout()

        self.label = QLabel('所有历史运行记录均显示在该表中.\n' \
                     '由于优化结果是固定的,所以不允许对已有的优化结果进行修改.如果您需要删除无用的优化记录,请选择要删除的优化记录所在行,并点击下方的删除按钮.\n' \
                     '另外,每次优化运行的折线图和记录优化过程的.csv文件都会显示在表格中.如需查看,直接点击超链接即可.')

        self.resultTable = QTableWidget(global_variable.num_exist, 8)
        self.resultTable.setStyleSheet('''
            QTableWidget{
                background: #ffffff;
                border: 1px solid;
                font-family: "Dengxian";
                font-size: 15px;
            }
            QTableWidget::item:selected{
                background: #cccccc;
            }
            QTableWidget::item:hover{
                background: #ccccff;
            }
            QHeaderView::section {
                border-top-width: 0;
                background: #ffffff;
                text-align: center;
                color: #330033;
            }
        ''')
        self.column_name = ['记录编号', '数据集', '优化器', '最优超参数值', '最优准确率', '准确率折线图', '最优准确率折线图', '训练全过程记录']

        self.deleteButton = QPushButton('删除记录')

        self.init_widget()

    def getWidget(self):
        return self.main_widget

    def init_widget(self):
        self.resultTable.setWindowTitle('超参数优化历史记录详情')
        self.resultTable.setHorizontalHeaderLabels(self.column_name)

        self.resultTable.setEditTriggers(QTableView.NoEditTriggers) # 不可编辑.
        self.resultTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents) # 高度自适应内容.
        self.resultTable.horizontalHeader().setStretchLastSection(True)
        self.resultTable.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.resultTable.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.resultTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.resultTable.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)

        self.deleteButton.setFixedWidth(100)
        self.deleteButton.clicked.connect(lambda: self.deleterows())

        self.bottom_layout.addWidget(self.deleteButton)
        self.bottom_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.resultTable)
        self.main_layout.addLayout(self.bottom_layout)

        self.setwidgetStyle()

        self.main_widget.setLayout(self.main_layout)

    def init_form(self):
        self.resultTable.setRowCount(global_variable.num_exist)
        connection = pymysql.connect(
            host=global_variable.host,
            user=global_variable.user,
            password=global_variable.password,
            database='opt',
            charset='utf8'
        )
        cursor = connection.cursor()

        sql = 'select * from opthistory;'
        cursor.execute(sql)

        row = 0
        for i in cursor:
            col = 0
            for j in i:
                if col < 5:
                    item = QTableWidgetItem(str(j))
                    item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.resultTable.setItem(row, col, item)
                else:
                    item = self.itemWithlink(str(j))
                    self.resultTable.setCellWidget(row, col, item)
                col += 1
            row += 1

        cursor.close()
        connection.close()

    def itemWithlink(self, content):
        item_widget = QWidget()
        item_widget.setStyleSheet('''
        .QWidget {
            border: none;
        }  
        ''')
        item_layout = QHBoxLayout()

        item_label = QLabel("<a href = \"" + content + "\">"+ content + "</a>")
        item_label.linkActivated.connect(lambda: self.link_clicked(content))

        item_layout.addWidget(item_label)
        item_layout.setAlignment(Qt.AlignCenter)
        item_widget.setLayout(item_layout)

        return item_widget

    def link_clicked(self, filename):
        if filename.find('.csv') == -1:
            image = Image.open(filename)
            image.show()
        else:
            current = os.path.dirname(__file__)[:-9] + filename[2:]
            print(current)
            os.startfile(current)

    def deleterows(self):
        message = QMessageBox(QMessageBox.Warning, '是否确认删除?', '是否确认删除选中行的优化记录?\n删除操作将导致数据库内的对应信息一并消失!\n(注意:每次只能删除一行的信息.如果选中多行,则以最后被选中的行为准)')
        message.setWindowIcon(QIcon('icon/tip.png'))
        yes = message.addButton("确定", QMessageBox.YesRole)
        no = message.addButton("取消", QMessageBox.NoRole)
        message.exec_()
        if message.clickedButton() == yes:
            index = self.resultTable.currentIndex()
            if index.row() != -1:
                id = self.resultTable.item(index.row(), 0).text()
                self.resultTable.removeRow(index.row())

                # 删除数据库指定行与对应文件.极大工作量,因为还需要为那些受到影响的testFig,bestFig,result进行重命名,对表格内容进行修正.必须保证文件,表格,数据库的完全一致.
                # 注意这里传入的不能是index.row(),因为第几行并不一定对应着数值为几的id值.必须获取指定行的id号.
                self.deleteData(id)

                # 在删除后刷新页面.这里存在迷之BUG,只刷新一次会导致最后一行的行高短一截.所以得刷新两次.
                self.init_form()
                # self.init_form()
            else:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/error.png'))
                message.setWindowTitle('未选择删除目标')
                message.setText('没有选择要删除的行.')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()

        else:
            pass
    '''
    因为数据库表的id,testFig,bestFig,result都是一致的,而且在删除后也不会发生变化,所以不再整体上调id值.
    换言之,删除的时候不减少opt_num值,继续增加,只是把删除掉的对应文件全删掉.这样,id未必是连续的,但始终在增加.
    但这样一来就必须多一个新的全局变量,用于记录表格中的条目数,从而控制表格显示的长度,始终得到现有的数据库表条目个数.
    '''
    def deleteData(self, id):
        connection = pymysql.connect(
            host=global_variable.host,
            user=global_variable.user,
            password=global_variable.password,
            database='opt',
            charset='utf8'
        )
        cursor = connection.cursor()

        delete_sql = "delete from opthistory where id = " + id + ";"
        print(delete_sql)
        cursor.execute(delete_sql)
        connection.commit()

        cursor.close()
        connection.close()

        basic_path = os.path.dirname(__file__)[:-9]
        csv_path = basic_path + '\\result_csv\\result_' + str(id) + '.csv'
        test_path = basic_path + '\\result_fig\\test_' + str(id) + '.png'
        best_path = basic_path + '\\result_fig\\best_' + str(id) + '.png'
        os.remove(csv_path)
        os.remove(test_path)
        os.remove(best_path)

        global_variable.num_exist -= 1
        # 仅当在删除的条目是最新一条的情况下,才更新global_variable.num_opt的值.
        if int(id) + 1 == global_variable.num_opt:
            global_variable.num_opt -= 1

    def setwidgetStyle(self):
        self.main_widget.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
        ''')