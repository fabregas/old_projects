# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../FablikFramework/forms/groups/form.ui'
#
# Created: Wed Jan 19 21:57:56 2011
#      by: PyQt4 UI code generator 4.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_groups(object):
    def setupUi(self, groups):
        groups.setObjectName(_fromUtf8("groups"))
        groups.resize(641, 661)
        groups.setMinimumSize(QtCore.QSize(300, 500))
        self.verticalLayout_2 = QtGui.QVBoxLayout(groups)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.newGroupBtn = QtGui.QPushButton(groups)
        self.newGroupBtn.setObjectName(_fromUtf8("newGroupBtn"))
        self.horizontalLayout.addWidget(self.newGroupBtn)
        self.remGroupBtn = QtGui.QPushButton(groups)
        self.remGroupBtn.setObjectName(_fromUtf8("remGroupBtn"))
        self.horizontalLayout.addWidget(self.remGroupBtn)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.groupsTree = QtGui.QTreeWidget(groups)
        self.groupsTree.setObjectName(_fromUtf8("groupsTree"))
        self.verticalLayout.addWidget(self.groupsTree)
        self.groupBox = QtGui.QGroupBox(groups)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 200))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.groupNameEdit = QtGui.QLineEdit(self.groupBox)
        self.groupNameEdit.setObjectName(_fromUtf8("groupNameEdit"))
        self.gridLayout_2.addWidget(self.groupNameEdit, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.groupDescriptionEdit = QtGui.QLineEdit(self.groupBox)
        self.groupDescriptionEdit.setObjectName(_fromUtf8("groupDescriptionEdit"))
        self.gridLayout_2.addWidget(self.groupDescriptionEdit, 2, 1, 1, 1)
        self.parentGroupSelector = QtGui.QComboBox(self.groupBox)
        self.parentGroupSelector.setObjectName(_fromUtf8("parentGroupSelector"))
        self.gridLayout_2.addWidget(self.parentGroupSelector, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_4.addWidget(self.label_4)
        self.goupRolesList = QtGui.QListWidget(self.groupBox)
        self.goupRolesList.setObjectName(_fromUtf8("goupRolesList"))
        self.verticalLayout_4.addWidget(self.goupRolesList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.appendRoleBtn = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.appendRoleBtn.sizePolicy().hasHeightForWidth())
        self.appendRoleBtn.setSizePolicy(sizePolicy)
        self.appendRoleBtn.setMinimumSize(QtCore.QSize(60, 0))
        self.appendRoleBtn.setObjectName(_fromUtf8("appendRoleBtn"))
        self.verticalLayout_3.addWidget(self.appendRoleBtn)
        self.removeRoleBtn = QtGui.QPushButton(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.removeRoleBtn.sizePolicy().hasHeightForWidth())
        self.removeRoleBtn.setSizePolicy(sizePolicy)
        self.removeRoleBtn.setMinimumSize(QtCore.QSize(60, 0))
        self.removeRoleBtn.setObjectName(_fromUtf8("removeRoleBtn"))
        self.verticalLayout_3.addWidget(self.removeRoleBtn)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_5.addWidget(self.label_5)
        self.allRolesList = QtGui.QListWidget(self.groupBox)
        self.allRolesList.setObjectName(_fromUtf8("allRolesList"))
        self.verticalLayout_5.addWidget(self.allRolesList)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.applyBtn = QtGui.QPushButton(groups)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.applyBtn.sizePolicy().hasHeightForWidth())
        self.applyBtn.setSizePolicy(sizePolicy)
        self.applyBtn.setMaximumSize(QtCore.QSize(300, 16777215))
        self.applyBtn.setObjectName(_fromUtf8("applyBtn"))
        self.horizontalLayout_3.addWidget(self.applyBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 5)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(groups)
        QtCore.QMetaObject.connectSlotsByName(groups)

    def retranslateUi(self, groups):
        groups.setWindowTitle(QtGui.QApplication.translate("groups", "Groups management", None, QtGui.QApplication.UnicodeUTF8))
        self.newGroupBtn.setText(QtGui.QApplication.translate("groups", "new group...", None, QtGui.QApplication.UnicodeUTF8))
        self.remGroupBtn.setText(QtGui.QApplication.translate("groups", "remove group", None, QtGui.QApplication.UnicodeUTF8))
        self.groupsTree.headerItem().setText(0, QtGui.QApplication.translate("groups", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.groupsTree.headerItem().setText(1, QtGui.QApplication.translate("groups", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("groups", "Group information", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("groups", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("groups", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("groups", "Parent group", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("groups", "Group roles", None, QtGui.QApplication.UnicodeUTF8))
        self.appendRoleBtn.setText(QtGui.QApplication.translate("groups", "<<", None, QtGui.QApplication.UnicodeUTF8))
        self.removeRoleBtn.setText(QtGui.QApplication.translate("groups", ">>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("groups", "All roles", None, QtGui.QApplication.UnicodeUTF8))
        self.applyBtn.setText(QtGui.QApplication.translate("groups", "Apply", None, QtGui.QApplication.UnicodeUTF8))
