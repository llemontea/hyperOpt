from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import chardet

# 自定义编辑区域.附加行号显示,高亮文本等效果.
class CodeEditor(QPlainTextEdit):
    class NumberBar(QWidget):
        def __init__(self, editor):
            QWidget.__init__(self, editor)

            self.editor = editor
            self.editor.blockCountChanged.connect(self.updateWidth)
            self.editor.updateRequest.connect(self.updateContents)
            self.font = QFont()
            self.numberBarColor = QColor("#e8e8e8")

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.numberBarColor)

            block = self.editor.firstVisibleBlock()

            while block.isValid():
                blockNumber = block.blockNumber()
                block_top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
                if blockNumber == self.editor.textCursor().blockNumber():
                    self.font.setBold(True)
                    painter.setPen(QColor("#000000"))
                else:
                    self.font.setBold(False)
                    painter.setPen(QColor("#717171"))

                paint_rect = QRect(0, block_top, self.width(), self.editor.fontMetrics().height())
                painter.drawText(paint_rect, Qt.AlignCenter, str(blockNumber + 1))

                block = block.next()

        def getWidth(self):
            count = self.editor.blockCount()
            if 0 <= count < 99999:
                width = self.fontMetrics().width('99999')
            else:
                width = self.fontMetrics().width(str(count))
            return width

        def updateWidth(self):
            width = self.getWidth()
            self.editor.setViewportMargins(width, 0, 0, 0)

        def updateContents(self, rect, dy):
            if dy:
                self.scroll(0, dy)
            else:
                self.update(0, rect.y(), self.width(), rect.height())
            if rect.contains(self.editor.viewport().rect()):
                fontSize = self.editor.currentCharFormat().font().pointSize()
                self.font.setPointSize(fontSize)
                self.font.setStyle(QFont.StyleNormal)
                self.updateWidth()

    def __init__(self):
        super(CodeEditor, self).__init__()

        self.setFont(QFont("Console", 12))
        # 非自动换行.超出屏幕显示范围的部分会出现滚动条.
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.number_bar = self.NumberBar(self)
        self.currentLineNumber = None

        self.cursorPositionChanged.connect(self.highligtCurrentLine)

        self.setViewportMargins(50, 0, 0, 0)
        self.highligtCurrentLine()

    def resizeEvent(self, *e):
        cr = self.contentsRect()
        rec = QRect(cr.left(), cr.top(), self.number_bar.getWidth(), cr.height())
        self.number_bar.setGeometry(rec)

    def highligtCurrentLine(self):
        newCurrentLineNumber = self.textCursor().blockNumber()
        if newCurrentLineNumber != self.currentLineNumber:
            lineColor = QColor(Qt.lightGray).lighter(120)
            self.currentLineNumber = newCurrentLineNumber
            hi_selection = QTextEdit.ExtraSelection()
            hi_selection.format.setBackground(lineColor)
            hi_selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            hi_selection.cursor = self.textCursor()
            hi_selection.cursor.clearSelection()
            self.setExtraSelections([hi_selection])

class fourWidget(QWidget):
    def __init__(self):
        super(fourWidget, self).__init__()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.headerLabel = QLabel('简易文本编辑区域.适用于.txt和.py等简单文本类文件的编辑.请勿打开.doc等复杂文本文件或者无法转换为文本内容的文件.')

        self.firstRow_layout = QHBoxLayout()
        self.fileButton = QPushButton('打开文件')
        self.newButton = QPushButton('新建文件')
        self.tipLabel = QLabel('当前文件:')
        self.fileLabel = QLabel('当前没有打开或新建的可编辑文件.')

        self.textEdit = CodeEditor()

        self.lastRow_layout = QHBoxLayout()
        self.clearButton = QPushButton('清空内容')
        self.saveButton = QPushButton('保存')
        self.saveasButton = QPushButton('另存为')

        self.code = 'utf-8'

        self.init_widget()

    def getWidget(self):
        return self.main_widget

    def init_widget(self):
        self.fileButton.setFixedWidth(150)
        self.newButton.setFixedWidth(150)
        self.fileButton.clicked.connect(lambda: self.openfile(self.textEdit))
        self.newButton.clicked.connect(lambda: self.newfile(self.textEdit))

        self.firstRow_layout.addWidget(self.fileButton)
        self.firstRow_layout.addWidget(self.newButton)
        self.firstRow_layout.addWidget(self.tipLabel)
        self.firstRow_layout.addWidget(self.fileLabel)

        self.firstRow_layout.addStretch()
        self.newButton.setContentsMargins(10, 0, 0, 0)
        self.tipLabel.setContentsMargins(20, 0, 0, 0)

        self.clearButton.clicked.connect(lambda: self.clearEdit(self.textEdit))
        self.saveButton.clicked.connect(lambda: self.savefile(self.textEdit))
        self.saveasButton.clicked.connect(lambda: self.saveasfile(self.textEdit))

        self.saveButton.setEnabled(False)
        self.saveasButton.setEnabled(False)
        self.textEdit.setEnabled(False)

        self.clearButton.setFixedWidth(150)
        self.saveButton.setFixedWidth(150)
        self.saveasButton.setFixedWidth(150)

        self.lastRow_layout.addWidget(self.saveasButton)
        self.lastRow_layout.addWidget(self.saveButton)
        self.lastRow_layout.addWidget(self.clearButton)

        self.lastRow_layout.setDirection(1)
        self.lastRow_layout.addStretch()
        self.clearButton.setContentsMargins(0, 0, 10, 0)
        self.saveButton.setContentsMargins(0, 0, 10, 0)

        self.setwidgetStyle()

        self.main_layout.addWidget(self.headerLabel)
        self.main_layout.addLayout(self.firstRow_layout)
        self.main_layout.addWidget(self.textEdit)
        self.main_layout.addLayout(self.lastRow_layout)

        self.main_widget.setLayout(self.main_layout)

    def openfile(self, edit):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setFilter(QDir.Files)

        if dialog.exec_():
            try:
                print(dialog.selectedFiles())
                filenames = dialog.selectedFiles()
                with open(filenames[0], 'rb') as fp:
                    # 自适应编码格式读取.有些.txt文件和.py文件是不同的编码,所以不解码的话就无法打开,进而卡死.
                    data = fp.read()
                    f_charinfo = chardet.detect(data)
                    self.code = f_charinfo['encoding']
                    edit.setPlainText(str(data.decode(f_charinfo['encoding'])))
                    edit.setEnabled(True)
                    self.fileLabel.setText(str(filenames[0]))
                    self.saveButton.setEnabled(True)
                    self.saveasButton.setEnabled(True)
            except Exception:
                message = QMessageBox()
                message.setWindowIcon(QIcon('icon/tip.png'))
                message.setWindowTitle('打开文件失败')
                message.setText('编解码及读取过程中出现问题,打开失败.')
                message.addButton(QPushButton("确定"), QMessageBox.YesRole)
                message.exec_()

    def newfile(self, edit):
        if len(edit.toPlainText()) != 0:
            message = QMessageBox()
            message.setWindowIcon(QIcon('icon/tip.png'))
            message.setWindowTitle('新建编辑区域')
            message.setText('新创建编辑区会导致正在编辑的内容清空!\n如果需要保存现有内容,请先保存后再新建编辑区.')
            yes = message.addButton("确定", QMessageBox.YesRole)
            no = message.addButton("取消", QMessageBox.NoRole)
            message.exec_()
            if message.clickedButton() == yes:
                self.code = 'utf-8'
                edit.clear()
                self.fileLabel.setText('新建文件')
                self.saveButton.setEnabled(False)
            else:
                pass
        else:
            self.code = 'utf-8'
            self.fileLabel.setText('新建文件')
            self.saveButton.setEnabled(False)
            self.saveasButton.setEnabled(True)
            edit.setEnabled(True)

    def clearEdit(self, edit):
        edit.clear()

    # 仅在打开文件,或者新建文件已经完成另存为确定位置的情况下,保存文件的按钮才是可以使用的.换言之:右上角显示文件路径的时候.
    def savefile(self, edit):
        aim_file = str(self.fileLabel.text())
        print('save', aim_file)

        fp = open(aim_file, 'w+', encoding = self.code)
        with fp:
            fp.write(str(edit.toPlainText()))

    # 在新建文件时,想要让这个新建的文件成为一个可保存文件的唯一途径就是另存为.
    # 新建文件的另存为操作会改变右上角的文件路径,打开文件的另存为则不会改变右上角的文件路径.
    def saveasfile(self, edit):
        fileName, ok= QFileDialog.getSaveFileName(self, '文件另存为', 'C:/', 'Text Files (*.txt)')
        if ok:
            print('save as', fileName)
            with open(fileName, 'w', encoding = self.code) as fp:
                fp.write(str(edit.toPlainText()))

                if str(self.fileLabel.text()) == '新建文件':
                    self.fileLabel.setText(fileName)
                    self.saveButton.setEnabled(True)

    def setwidgetStyle(self):
        self.main_widget.setStyleSheet('''
            QLabel {
                font-family: "Dengxian";
                font: 16px;
                vertical-align: middle;
            }
        ''')