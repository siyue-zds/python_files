import os
import re
import sys
import time
from pathlib import Path
import interface.images_rc

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QBrush, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QMessageBox, QHeaderView, \
    QAbstractItemView, QTableWidget, QTableWidgetItem, QMenu, QDialog, QInputDialog

from interface.details_dialog import DetailsDialog
from interface.new_dialog import NewDialog
from interface.main_window import Ui_MainWindow
from interface.search_dialog import SearchDialog
from processing import files
from processing.files import bytes_conversion, get_mountpoints, get_files, files_folder_size, files_file_create, \
    files_folder_create, files_file_copy, files_folder_copy, files_move, files_file_delete, files_folder_delete, \
    file_delete, files_same_type
from processing.search import FileSearchThread


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # 主页路径
        self.thread = None
        # 主页路径
        if os.name == 'posix':
            # Linux
            self.home_path = '/home'
        else:
            # Windows
            self.home_path = get_mountpoints()[0]
        # 当前路径
        self.current_path = self.home_path
        # before栈
        self.before_stack = []
        # after栈
        self.after_stack = []

        self.setupUi(self)
        self.resize(1000, 750)
        self.setWindowTitle("Files")
        self.setWindowIcon(QIcon(':/icons/files.ico'))
        self.init_QTreeWidget()
        self.init_QTableWidget()
        self.update_information()

        # 组件
        self.file_menu = None
        self.action_cut = None
        self.action_copy = None
        self.action_paste = None
        self.action_rename = None
        self.action_delete = None
        self.action_details = None
        self.action = None
        # 剪切板
        self.clipboard = QApplication.clipboard()
        self.split_pattern = r'//'
        # 关闭菜单栏
        self.menubar.clear()

        # 响应
        self.treeWidget.clicked.connect(self.tree_clicked)
        self.tableWidget.doubleClicked.connect(self.open_folder)
        # 后退
        self.pushButton_arrowleft.clicked.connect(self.backward)
        # 前进
        self.pushButton_arrowright.clicked.connect(self.forward)
        # 上移
        self.pushButton_arrowup.clicked.connect(self.parent)
        # 刷新
        self.pushButton_refresh.clicked.connect(self.refresh)
        # 复制路径
        self.pushButton_textcopy.clicked.connect(self.copy_path)
        # 路径回车
        self.lineEdit_path.returnPressed.connect(self.move_path)
        # 新建
        self.pushButton_add.clicked.connect(self.add)
        # 剪切
        self.pushButton_cut.clicked.connect(self.cut)
        # 复制
        self.pushButton_copy.clicked.connect(self.copy)
        # 粘贴
        self.pushButton_paste.clicked.connect(self.paste)
        # 重命名
        self.pushButton_rename.clicked.connect(self.rename)
        # 删除
        self.pushButton_delete.clicked.connect(self.delete)
        # 详细信息
        self.pushButton_details.clicked.connect(self.details)
        # 文件搜索
        self.pushButton_search.clicked.connect(self.file_search)
        # 内容搜索
        self.pushButton_setting.clicked.connect(self.file_content_search)

    # 关闭窗口
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "是否要关闭所有窗口?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            sys.exit(0)  # 退出程序
        else:
            event.ignore()

    # 更新路径编辑框
    def update_lineEdit_path(self):
        self.lineEdit_path.setText(self.current_path)

    # 更新状态Label
    def update_label_status(self):
        path = Path(self.current_path)
        count = 0
        if path.is_file():
            count = 1
        elif path.is_dir():
            count = len([file for file in path.iterdir()])
        else:
            return
        self.label_status.setText(f'{count}个项目')
        self.label_status.repaint()

    # 初始化QTreeWidget
    def init_QTreeWidget(self):
        # 设置列数
        self.treeWidget.setColumnCount(1)

        # 设置根节点-主页
        home = QTreeWidgetItem(self.treeWidget)
        home.setText(0, '主页')
        home.setBackground(0, QBrush(Qt.white))
        home.setIcon(0, QIcon(':/icons/home.ico'))

        # 设置根节点-驱动器
        files = QTreeWidgetItem(self.treeWidget)
        files.setText(0, '驱动器')
        files.setBackground(0, QBrush(Qt.white))
        files.setIcon(0, QIcon(':/icons/pc.ico'))

        # 获取系统磁盘
        mountpoints = get_mountpoints()
        for index, mountpoint in enumerate(mountpoints):
            # 设置子节点
            child = QTreeWidgetItem(files)
            child.setText(0, mountpoint)
            child.setIcon(0, QIcon(':/icons/disk_driver.ico'))

        # 全部展开
        self.treeWidget.expandAll()

    def tree_clicked(self):
        tree_item = self.treeWidget.currentItem()
        item_path = tree_item.text(0)
        if item_path == '主页':
            item_path = self.home_path
        elif item_path == '驱动器':
            return
        self.before_stack.append(self.current_path)
        self.current_path = item_path
        self.update_information()

    # 初始化QTableWidget
    def init_QTableWidget(self):
        # 列数和行数
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(0)
        # 表头的显示与隐藏
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.verticalHeader().setVisible(False)
        # 设置水平方向的表头标签
        self.tableWidget.setHorizontalHeaderLabels(['名称', '修改时间', '类型', '大小'])
        # 设置水平方向表格为自适应的伸缩模式
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 将表格设置为禁止编辑
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # 设置表格整行选中
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 设置多行选中
        self.tableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # 将行与列的高度设置为所显示的内容的宽度高度匹配
        QTableWidget.resizeColumnsToContents(self.tableWidget)
        QTableWidget.resizeRowsToContents(self.tableWidget)
        # 表格中不显示分割线
        self.tableWidget.setShowGrid(False)

        # 允许右键产生菜单
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        # 将右键菜单绑定到槽函数generateMenu
        self.tableWidget.customContextMenuRequested.connect(self.tableWidget_menu)
        '''
        #排序
        #Qt.DescendingOrder降序
        #Qt.AscEndingOrder升序
        tableWidget.sortItems(2,Qt.DescendingOrder)
        '''

    def open_folder(self):
        # 当前行索引
        row_num = self.tableWidget.currentRow()
        if self.tableWidget.item(row_num, 2).text() == '文件':
            try:
                if os.name == 'nt':
                    # Windows操作系统
                    os.startfile(str(Path(self.current_path, self.tableWidget.item(row_num, 0).text()).absolute()))
                elif os.name == 'posix':
                    # Linux操作系统
                    # 使用vim打开文件
                    shell = f'vim {str(Path(self.current_path, self.tableWidget.item(row_num, 0).text()).absolute())} '
                    os.popen(f"gnome-terminal -e '{shell}'")

                else:
                    return
            except Exception as e:
                QMessageBox.critical(self, '错误', '文件拒绝访问！', QMessageBox.Yes)
        elif self.tableWidget.item(row_num, 2).text() == '文件夹':
            self.before_stack.append(self.current_path)
            self.current_path = str(Path(self.current_path, self.tableWidget.item(row_num, 0).text()).absolute())
            self.update_information()

    def update_QTableWidget(self):

        files_data = get_files(Path(self.current_path))
        row_count = files_data.shape[0]
        # 列数和行数
        # self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(row_count)
        # 索引
        index = 0
        # 添加数据
        for row in files_data.itertuples():
            nameItem = QTableWidgetItem(getattr(row, 'name'))
            if getattr(row, 'type') == 'file':
                nameItem.setIcon(QIcon(':/icons/file.ico'))
                self.tableWidget.setItem(index, 2, QTableWidgetItem('文件'))
                self.tableWidget.setItem(index, 3, QTableWidgetItem(bytes_conversion(getattr(row, 'size'))))
            else:
                nameItem.setIcon(QIcon(':/icons/folder.ico'))
                self.tableWidget.setItem(index, 2, QTableWidgetItem('文件夹'))
                self.tableWidget.setItem(index, 3, QTableWidgetItem(''))
            self.tableWidget.setItem(index, 0, nameItem)
            self.tableWidget.setItem(index, 1, QTableWidgetItem(getattr(row, 'modified_date')))

            index = index + 1
        # 排序
        self.tableWidget.sortItems(0, Qt.AscendingOrder)

    def tableWidget_menu(self, pos):
        # 创建QMenu
        self.file_menu = QMenu(self)
        self.file_menu.setStyleSheet("QMenu{background:LightSkyBlue;}"  # 选项背景颜色
                                     "QMenu{border:2px solid lightgray;}"  # 设置整个菜单框的边界高亮厚度
                                     "QMenu{border-color:#FAFAFA;}"  # 整个边框的颜色

                                     "QMenu::item{padding:5px 40px 5px 5px;}"  # 上、右、下、左
                                     "QMenu::item{height:25px;}"  # 显示菜单选项高度
                                     "QMenu::item{color:black;}"  # 选项文字颜色
                                     "QMenu::item{background:#FAFAFA;}"  # 选项背景
                                     "QMenu::item{margin:0px 0px 0px 0px;}"  # 每个选项四边的边界厚度，上，右，下，左

                                     "QMenu::item:selected:enabled{background:#F0F0F0;}"
                                     "QMenu::item:selected:enabled{color:black;}"  # 鼠标在选项上面时，文字的颜色
                                     "QMenu::item:selected:!enabled{background:transparent;}"  # 鼠标在上面时，选项背景为不透明

                                     )

        self.action_cut = self.file_menu.addAction(QIcon(":/icons/cut.ico"), u'剪切')
        self.action_copy = self.file_menu.addAction(QIcon(":/icons/copy.ico"), u'复制')
        self.action_paste = self.file_menu.addAction(QIcon(":/icons/paste.ico"), u'粘贴')
        self.action_rename = self.file_menu.addAction(QIcon(":/icons/rename.ico"), u'重命名')
        self.action_delete = self.file_menu.addAction(QIcon(":/icons/delete.ico"), u'删除')
        self.action_details = self.file_menu.addAction(QIcon(":/icons/details.ico"), u'详细信息')
        self.action = self.file_menu.exec_(self.tableWidget.mapToGlobal(pos))

        # 菜单选项
        if self.action == self.action_cut:
            self.cut()
        elif self.action == self.action_copy:
            self.copy()
        elif self.action == self.action_paste:
            self.paste()
        elif self.action == self.action_rename:
            self.rename()
        elif self.action == self.action_delete:
            self.delete()
        elif self.action == self.action_details:
            self.details()

    def update_information(self):
        self.update_QTableWidget()
        self.update_label_status()
        self.update_lineEdit_path()

    def add(self):
        file_type = '文件'
        file_path = ''
        file_name = ''
        dialog = NewDialog()
        dialog.lineEdit_path.setText(self.current_path)
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        dialog.setWindowModality(Qt.ApplicationModal)
        if dialog.exec_() == QDialog.Accepted:
            # 文件类型
            if dialog.radioButton_folder.isChecked():
                file_type = '文件夹'
            # 文件路径
            file_path = dialog.lineEdit_path.text()
            # 文件名称
            file_name = dialog.lineEdit_name.text()
            path = Path(file_path, file_name)
            # 标记
            flag = True
            # 是否新建文件
            if path.exists():
                reply = QMessageBox.information(self, "注意", f'该{file_type}已存在，是否覆盖？', QMessageBox.Yes | QMessageBox.No)
                # 不覆盖已有文件，取消新建
                if reply == QMessageBox.No:
                    flag = False
                else:
                    file_delete(path)
            # 根据判断结果执行操作
            if flag:
                if file_type == '文件':
                    files_file_create(Path(file_path), file_name)
                else:
                    files_folder_create(Path(file_path), file_name)
                self.before_stack.append(self.current_path)
                self.current_path = file_path
                self.update_information()
            else:
                return

    def update_clipboard(self, operation: str):
        # 获取选择的单元格
        selected_items = self.tableWidget.selectedItems()
        if len(selected_items) == 0:
            return
        # 获取选中的文件名
        selected_items = [selected_items[i] for i in range(0, len(selected_items), 4)]
        # 复制文件路径到剪切板
        files_path = ''
        for item in selected_items:
            files_path = files_path + '//' + operation + '//' + str(Path(self.current_path, item.text()))
        self.clipboard.clear()
        self.clipboard.setText(files_path)

    # 剪切
    def cut(self):
        operation = 'cut'
        self.update_clipboard(operation)

    # 复制
    def copy(self):
        operation = 'copy'
        self.update_clipboard(operation)

    # 粘贴
    def paste(self):
        clipboard_text = self.clipboard.text()
        if len(clipboard_text) == 0:
            self.clipboard.clear()
            return
        texts = re.split(self.split_pattern, clipboard_text)
        # 剪切板为空或信息错误
        if len(texts) % 2 == 0:
            self.clipboard.clear()
            return
        # 目标路径
        target_path = self.current_path
        # 遍历
        for i in range(1, len(texts), 2):
            # 操作类型
            operation = texts[i]
            # 文件路径
            source_path = texts[i + 1]
            # 判断操作
            if operation == 'cut':
                # 目标文件已存在
                path = Path(self.current_path, Path(source_path).name)
                # 源文件和目标文件一致
                if str(path) == str(source_path):
                    QMessageBox.warning(self, "警告", f'源文件与目标文件一致', QMessageBox.Yes)
                    continue
                if path.exists():
                    reply = QMessageBox.question(self, "注意", f'文件{path.name}已存在，是否替换？',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                    if reply == QMessageBox.No:
                        continue
                    else:
                        file_delete(path)
                # 移动文件
                files_move(source_path, self.current_path)

            elif operation == 'copy':
                # 文件名称
                file_name = Path(source_path).name
                # 目标文件已存在
                path = Path(self.current_path, file_name)
                # 源文件和目标文件一致
                if str(path) == str(source_path):
                    QMessageBox.warning(self, "警告", f'源文件与目标文件一致', QMessageBox.Yes)
                    continue

                if path.exists():
                    reply = QMessageBox.question(self, "注意", f'文件{path.name}已存在，是否替换？',
                                                 QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.No:
                        continue
                    else:
                        file_delete(path)
                # 复制
                if Path(source_path).is_file():
                    # 复制文件
                    files_file_copy(source_path, str(Path(self.current_path, file_name)))
                elif Path(source_path).is_dir():
                    # 复制目录
                    files_folder_copy(source_path, str(Path(self.current_path, file_name)))
                else:
                    return
            # 刷新界面
            self.update_information()

    def rename(self):
        # 获取选择的单元格
        selected_items = self.tableWidget.selectedItems()
        if len(selected_items) != 4:
            return
        # 获取选中的文件名
        old_name = selected_items[0].text()
        # 新文件名
        new_name = ''
        # 获取新文件名
        text, ok = QInputDialog.getText(self, '重命名', '输入名称：')
        if ok:
            new_name = str(text)
        else:
            return
        # 文件类型不同
        old_path = Path(self.current_path, old_name)
        new_path = Path(self.current_path, new_name)
        if files_same_type(old_path, new_path):
            QMessageBox.warning(self, "警告", '文件类型不同', QMessageBox.Yes)
            return
        # 判断文件是否存在
        if Path(self.current_path, new_name).exists():
            # 确认覆盖
            reply = QMessageBox.question(self, "注意", '该文件已存在，是否覆盖？', QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                # 不覆盖，退出
                return
        # 重命名
        files.file_rename(old_path, new_path)
        # 刷新界面
        self.update_information()

    def delete(self):
        # 确认删除
        reply = QMessageBox.question(self, "注意", '确认删除所选文件？', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.No:
            return
        # 获取选择的单元格
        selected_items = self.tableWidget.selectedItems()
        if len(selected_items) == 0:
            return
        # 获取选中的文件名
        selected_items = [selected_items[i] for i in range(0, len(selected_items), 4)]
        # 遍历
        for item in selected_items:
            # 文件路径
            files_path = Path(self.current_path, item.text())
            # 判断文件/文件夹路径是否存在
            if not files_path.exists():
                QMessageBox.critical(self, '错误', f'文件{str(files_path)}不存在！', QMessageBox.Yes)
                return
            else:
                file_delete(files_path)
            # 刷新界面
            self.update_information()

    def file_num(self, path: Path):
        file_num = 0
        dir_num = 0
        for file in path.iterdir():
            if file.is_file():
                file_num = file_num + 1
            elif file.is_dir():
                dir_num = dir_num + 1
                file_num_new, dir_num_new = self.file_num(file)
                file_num = file_num + file_num_new
                dir_num = dir_num + dir_num_new
        return file_num, dir_num

    def details(self):
        # 获取选择的单元格
        selected_items = self.tableWidget.selectedItems()
        if len(selected_items) != 4:
            return
        # 获取选中的文件名
        file_name = selected_items[0].text()
        # 文件路径
        file_path = Path(self.current_path, file_name)
        # 文件详细详细窗口
        dialog = DetailsDialog()
        # 文件名称
        dialog.lineEdit_name.setText(file_name)
        # 文件类型和大小
        if file_path.is_file():
            dialog.label_ico.setPixmap(QPixmap(":/icons/file.ico"))
            dialog.label_ico.setScaledContents(True)
            dialog.label_type.setText("文件")
            dialog.label_size_value.setText(bytes_conversion(file_path.stat().st_size))
        elif file_path.is_dir():
            dialog.label_ico.setPixmap(QPixmap(":/icons/folder.ico"))
            dialog.label_ico.setScaledContents(True)
            file_num, dir_num = self.file_num(file_path)
            dialog.label_type.setText(f"文件夹 包含{dir_num}个文件夹 {file_num}个文件")
            dialog.label_size_value.setText(bytes_conversion(files_folder_size(file_path)))
        else:
            dialog.label_type.setText('')
            dialog.label_size_value.setText('')
        # 路径
        dialog.label_path_value.setText(str(file_path))
        # 访问时间
        dialog.label_access_time.setText(time.strftime("%Y-%m-%d %H:%M", time.localtime(file_path.stat().st_atime)))
        # 修改时间
        dialog.label_modification_time.setText(
            time.strftime("%Y-%m-%d %H:%M", time.localtime(file_path.stat().st_mtime)))
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def backward(self):
        if self.before_stack:
            path = self.before_stack.pop()
            self.after_stack.append(self.current_path)
            self.current_path = path
            self.update_information()
        else:
            return

    def forward(self):
        if self.after_stack:
            path = self.after_stack.pop()
            self.before_stack.append(self.current_path)
            self.current_path = path
            self.update_information()
        else:
            return

    def parent(self):
        path = str(Path(self.current_path).parent)
        self.before_stack.append(self.current_path)
        self.current_path = path
        self.update_information()

    def refresh(self):
        self.update_information()

    # 复制路径
    def copy_path(self):
        self.clipboard.clear()
        self.clipboard.setText(self.lineEdit_path.text())

    # 转到路径
    def move_path(self):
        path = self.lineEdit_path.text()
        if Path(path).exists():
            # 路径正确
            self.before_stack.append(self.current_path)
            self.current_path = path
            self.update_information()
        else:
            # 路径不存在
            QMessageBox.critical(self, '错误', '文件路径错误！', QMessageBox.Yes)

    # 搜索
    def search(self, search_style: bool):
        file_name = self.lineEdit_search.text()
        if len(file_name) == 0:
            return
        dialog = SearchDialog()
        
        dialog.lineEdit_search.setText(file_name)
        dialog.lineEdit_folder.setText(self.current_path)
        dialog.search_path = self.current_path
        dialog.search_content = file_name
        dialog.search(search_style)
        # 设置窗口的属性为ApplicationModal模态，用户只有关闭弹窗后，才能关闭主界面
        dialog.setWindowModality(Qt.ApplicationModal)
        if dialog.exec_() == QDialog.Accepted:
            # 文件路径
            file_path = Path(dialog.choice_path)
            # 更新界面
            self.current_path = str(file_path.parent)
            self.update_information()
            # 设置选中状态
            for i in range(self.tableWidget.rowCount()):
                if self.tableWidget.item(i, 0).text() == file_path.name:
                    self.tableWidget.selectRow(i)

    # 按文件名查找
    def file_search(self):
        self.search(search_style=True)

    # 文件内容查找
    def file_content_search(self):
        self.search(search_style=False)
