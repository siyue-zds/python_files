from PyQt5.QtWidgets import QDialog

from interface.new import Ui_Dialog


class NewDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(NewDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("新建")
        # 文件类型
        self.type = '文件'
        # 类型按钮默认状态
        self.radioButton_file.setChecked(True)
        self.radioButton_folder.setChecked(False)
        # 文件位置不可编辑
        self.lineEdit_path.setEnabled(False)
