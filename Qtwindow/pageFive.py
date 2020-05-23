from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class fiveWidget(QWidget):
    def __init__(self):
        super(fiveWidget, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.tipLayout = QVBoxLayout()

        self.lastRowLayout = QHBoxLayout()
        self.informationLayout = QVBoxLayout()

        self.infor1 = QLabel()
        self.infor1.setPixmap(QPixmap('icon/sign.png'))

        self.infor2 = QLabel("使用过程中出现问题请联系:")
        self.infor3 = QLabel("github:@llemontea")
        self.infor4 = QLabel("e-mail:FreedomKoo@163.com")

        self.init_widget()

    def getWidget(self):
        return self.main_widget

    def init_widget(self):
        '''
        self.label_1 = QLabel("1.如果对超参数优化的目标比较宽松,想通过比较少的迭代找到一个较好的超参数即可:建议使用贝叶斯优化或者随机搜索.")
        self.label_2 = QLabel("2.如果希望找到表现尽可能好的超参数,但对时间要求比较紧:建议使用贝叶斯优化.")
        self.label_3 = QLabel("3.如果希望找到表现尽可能好的超参数,但对时间要求比较宽松:建议使用贝叶斯优化或者粒子群算法.")
        self.label_4 = QLabel("4.如果目标是找到一个包含数个超参数取值的,表现较好的超参数取值集合:建议使用遗传算法.")
        self.label_5 = QLabel("5.如果允许进行的优化迭代次数极少,可以考虑使用网格搜索或者随机搜索这类比较简单的优化方法.")
        self.label_6 = QLabel("6.如果待优化的超参数数量较多,不建议使用网格搜索.")
        self.label_7 = QLabel("7.如果初步优化结果发现最优超参数取值集中在极小的范围内,贝叶斯优化的表现可能比较好.")
        self.label_8 = QLabel("8.如果初步优化结果发现在超参数取值在较大范围内都有相近的表现,则不建议使用遗传算法,因为很容易陷入局部最优.")
        self.label_9 = QLabel("9.在网络模型的稳定性非常差或者非常好的情况下,均建议使用贝叶斯优化.前者是因为贝叶斯优化更容易捕捉较优取值的细节,后者是因为可以充分发挥贝叶斯优化的优势.")
        self.label_10 = QLabel("10.单超参数优化问题可以倾向于使用随机搜索和贝叶斯优化,但多参数优化问题中遗传算法和粒子群算法会有同样不错的表现.")
        '''
        self.tiplabel_1 = QLabel("> > > 关于超参数优化相关参数的设置......")

        self.label_1 = QLabel("1.网格搜索的迭代次数和步长大小成反比.为了细化搜索空间可以取较小的步长,但该操作会增加迭代次数,尤其是在多超参数优化情况下.")
        self.label_2 = QLabel("2.使用贝叶斯优化时,在条件允许的情况下,建议适量增加预设值,这样高斯过程建模会更完备.")
        self.label_3 = QLabel("3.贝叶斯优化的三种采集函数:")
        self.label_4 = QLabel("\t> UCB函数:函数参数为κ.κ取值越大,越倾向于在现有的最优结果附近取值;κ取值越小,越倾向于尝试未知的取值区域.")
        self.label_5 = QLabel("\t> PI函数和EI函数:函数参数为χ.χ可以视为偏离现有最优结果的程度,也即χ越小就越容易在靠近现有最优结果的区间内取值.")
        self.label_6 = QLabel("如果采用UCB函数,κ的建议取值是2.5左右.如果采用PI函数或EI函数,χ的建议取值是0.0左右.但两者不允许取负数.")
        self.label_7 = QLabel("4.采用遗传算法时,在迭代次数相同的情况下,种群规模大些，效果会更好.")
        self.label_8 = QLabel("5.遗传算法很容易收敛到局部最优.增加遗传算法的交叉概率和变异概率能够增加算法的随机性,但不建议过大.一般设交叉概率0.5,变异概率0.05.")
        self.label_9 = QLabel("6.遗传算法采用的是二进制编码.编码越长,对应超参数取值就越精细.编码越短,超参数取值就越粗糙.一般设编码长度为10.")
        self.label_10 = QLabel("7.粒子群算法可以向每代粒子群增加新的随机粒子,来提高整个算法的随机性.但不建议增加过多,否则在经过若干次迭代后粒子群规模会剧增.")
        self.label_11 = QLabel("8.粒子群算法的c1和c2分别控制个体和全局信息权重,一般而言两者取值相同的情况下效果会比较好,一般取值2.0.")
        self.label_12 = QLabel("9.粒子群算法的惯性因子w用于在每次迭代过程中保留当前位置的信息.w取值较大时,全局寻优能力强;w取值较小时,局部寻优能力强.")
        self.label_13 = QLabel("所以这里采用的手段是惯性因子递减:迭代过程中w的值不断递减,从上限值到下限值,从全局寻优收缩至局部寻优.建议w取值上下限在0.1~0.9之间.")
        self.label_14 = QLabel("10.针对不同的应用情况,以上参数的选择并不一定是一成不变的.简单的思路是看您想要增加寻优过程中的随机性,还是保持寻优过程中的稳定性.\n")

        self.tiplabel_2 = QLabel("> > > 其他需要说明的......")

        self.label_15 = QLabel("1.超参数优化过程不会对您上传的网络模型进行任何改动.建议您在上传之前,先简单测试,改善一下模型的稳定性.")
        self.label_16 = QLabel("模型稳定性较差的情况下,各个超参数优化方法的效果也会变差.可以通过更改模型结构,增加模型深度或神经元个数等方式来提高稳定性.")
        self.label_17 = QLabel("2.请结合您的运行环境确定batch_size超参数的取值.在运存不足的情况下,过大的batch_size取值会导致超参数优化出现RuntimeError错误.")
        self.label_18 = QLabel("3.除了网格搜索外,其余超参数优化器都建立在随机初始化的基础上,所以有些情况下优化的结果会受到这种随机性的影响.可以采用的解决方法包括:")
        self.label_19 = QLabel("\t> 增加迭代次数.更多的优化次数往往意味着更好的结果.")
        self.label_20 = QLabel("\t> 采用对随机初始化不那么敏感的优化器,如贝叶斯优化算法和粒子群算法.当然随机搜索也是.")
        self.label_21 = QLabel("\t> 在允许的情况下可以多次运行,综合数次运行的结果得到比较理想的优化结果.")

        self.informationLayout.addWidget(self.infor2)
        self.informationLayout.addWidget(self.infor3)
        self.informationLayout.addWidget(self.infor4)

        self.lastRowLayout.addLayout(self.informationLayout)
        self.lastRowLayout.addWidget(self.infor1)
        self.lastRowLayout.setDirection(1)
        self.lastRowLayout.addStretch()
        self.lastRowLayout.addSpacing(15)

        self.main_layout.addWidget(self.tiplabel_1)
        self.main_layout.addWidget(self.label_1)
        self.main_layout.addWidget(self.label_2)
        self.main_layout.addWidget(self.label_3)
        self.main_layout.addWidget(self.label_4)
        self.main_layout.addWidget(self.label_5)
        self.main_layout.addWidget(self.label_6)
        self.main_layout.addWidget(self.label_7)
        self.main_layout.addWidget(self.label_8)
        self.main_layout.addWidget(self.label_9)
        self.main_layout.addWidget(self.label_10)
        self.main_layout.addWidget(self.label_11)
        self.main_layout.addWidget(self.label_12)
        self.main_layout.addWidget(self.label_13)
        self.main_layout.addWidget(self.label_14)
        self.main_layout.addWidget(self.tiplabel_2)
        self.main_layout.addWidget(self.label_15)
        self.main_layout.addWidget(self.label_16)
        self.main_layout.addWidget(self.label_17)
        self.main_layout.addWidget(self.label_18)
        self.main_layout.addWidget(self.label_19)
        self.main_layout.addWidget(self.label_20)
        self.main_layout.addWidget(self.label_21)
        self.main_layout.addSpacing(16)
        self.main_layout.addLayout(self.lastRowLayout)
        self.main_layout.addStretch()
        self.main_layout.setContentsMargins(10, 16, 10, 0)

        self.setboxStyle()

        self.main_widget.setLayout(self.main_layout)

    def setboxStyle(self):
        self.main_widget.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 17px;
                vertical-align: middle;
            }
        ''')
        self.tiplabel_1.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 20px;
                font-weight: bold;
                color: #FF9900;
                vertical-align: middle;
            }
        ''')
        self.tiplabel_2.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 20px;
                font-weight: bold;
                color: #FF9900;
                vertical-align: middle;
            }
        ''')