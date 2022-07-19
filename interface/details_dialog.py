from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

from interface.details import Ui_Dialog


class DetailsDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(DetailsDialog, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("文件信息")
        # 文件名称不可编辑
        self.lineEdit_name.setEnabled(False)
        # label文字可复制
        self.label_path_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_type.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_size_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_access_time.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label_modification_time.setTextInteractionFlags(Qt.TextSelectableByMouse)











