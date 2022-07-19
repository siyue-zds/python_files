# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEdit_path = QtWidgets.QLineEdit(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(9)
        self.lineEdit_path.setFont(font)
        self.lineEdit_path.setObjectName("lineEdit_path")
        self.gridLayout.addWidget(self.lineEdit_path, 2, 1, 1, 1)
        self.label_path = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.label_path.setFont(font)
        self.label_path.setAlignment(QtCore.Qt.AlignCenter)
        self.label_path.setObjectName("label_path")
        self.gridLayout.addWidget(self.label_path, 2, 0, 1, 1)
        self.radioButton_file = QtWidgets.QRadioButton(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.radioButton_file.setFont(font)
        self.radioButton_file.setObjectName("radioButton_file")
        self.gridLayout.addWidget(self.radioButton_file, 0, 1, 1, 1)
        self.label_name = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.label_name.setFont(font)
        self.label_name.setAlignment(QtCore.Qt.AlignCenter)
        self.label_name.setObjectName("label_name")
        self.gridLayout.addWidget(self.label_name, 3, 0, 1, 1)
        self.radioButton_folder = QtWidgets.QRadioButton(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.radioButton_folder.setFont(font)
        self.radioButton_folder.setObjectName("radioButton_folder")
        self.gridLayout.addWidget(self.radioButton_folder, 1, 1, 1, 1)
        self.lineEdit_name = QtWidgets.QLineEdit(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(9)
        self.lineEdit_name.setFont(font)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.gridLayout.addWidget(self.lineEdit_name, 3, 1, 1, 1)
        self.label_type = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.label_type.setFont(font)
        self.label_type.setAlignment(QtCore.Qt.AlignCenter)
        self.label_type.setObjectName("label_type")
        self.gridLayout.addWidget(self.label_type, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(11)
        self.buttonBox.setFont(font)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_path.setText(_translate("Dialog", "位置"))
        self.radioButton_file.setText(_translate("Dialog", "文件"))
        self.label_name.setText(_translate("Dialog", "名称"))
        self.radioButton_folder.setText(_translate("Dialog", "文件夹"))
        self.label_type.setText(_translate("Dialog", "类型"))