from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidget, QAbstractItemView, QHeaderView, QTableWidgetItem

from interface.search import Ui_Dialog
from processing.files import bytes_conversion
from processing.search import FileSearchThread
import interface.images_rc


class SearchDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(SearchDialog, self).__init__(parent)
        self.thread = None
        self.setupUi(self)
        self.setWindowTitle("搜索")
        # 目录位置不可编辑
        self.lineEdit_folder.setEnabled(False)
        # 搜索名称不可编辑
        self.lineEdit_search.setEnabled(False)
        # 初始化
        self.init_QTableWidget()
        # 搜索
        self.search_path = ''
        self.search_content = ''
        # 选择
        self.choice_path = ''
        # 打开
        self.tableWidget.doubleClicked.connect(self.open_file)

    # 初始化QTableWidget
    def init_QTableWidget(self):
        # 列数和行数
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        # 表头的显示与隐藏
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)
        # 设置水平方向的表头标签
        self.tableWidget.setHorizontalHeaderLabels(['名称', '路径'])
        # 设置水平方向表格为自适应的伸缩模式
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 将表格设置为禁止编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置表格整行选中
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.tableWidget)
        QTableWidget.resizeRowsToContents(self.tableWidget)
        # 表格中不显示分割线
        self.tableWidget.setShowGrid(False)

    # 搜索
    def search(self, search_style: bool):
        # 清除tableWidget内容
        self.tableWidget.setRowCount(0)
        # 显示status_label
        self.label_num.setText(f'{0}个项目')
        # 创建文件搜索进程
        self.thread = FileSearchThread(self.search_path, self.search_content, style=search_style)
        self.thread.sinOut.connect(self.slotAdd)
        self.thread.start()

    def slotAdd(self, path: str):
        # tableWidge末尾插入一行
        row_count = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(row_count + 1)
        file_path = Path(path)
        # 添加文件信息
        nameItem = QTableWidgetItem(str(file_path.name))
        # 文件类型
        if file_path.is_file():
            nameItem.setIcon(QIcon(':/icons/file.ico'))
            self.tableWidget.setItem(row_count, 0, nameItem)
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem(str(file_path)))
        else:
            nameItem.setIcon(QIcon(':/icons/folder.ico'))
            self.tableWidget.setItem(row_count, 0, nameItem)
            self.tableWidget.setItem(row_count, 1, QTableWidgetItem(str(file_path)))
        self.tableWidget.viewport().update()
        # 显示status_label
        self.label_num.setText(f'{row_count + 1}个项目')
        return

    def open_file(self):
        row_num = self.tableWidget.currentRow()
        self.choice_path = self.tableWidget.item(row_num, 1).text()
        self.accept()
