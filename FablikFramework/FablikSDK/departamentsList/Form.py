# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'departamentsList/form.ui'
#
# Created: Wed Sep 29 15:05:24 2010
#      by: PyQt4 UI code generator 4.7.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_departamentsList(object):
    def setupUi(self, departamentsList):
        departamentsList.setObjectName(_fromUtf8("departamentsList"))
        departamentsList.resize(400, 301)
        departamentsList.setMinimumSize(QtCore.QSize(400, 300))
        self.verticalLayout_2 = QtGui.QVBoxLayout(departamentsList)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.treeWidget = QtGui.QTreeWidget(departamentsList)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.header().setDefaultSectionSize(200)
        self.verticalLayout.addWidget(self.treeWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.insertButton = QtGui.QPushButton(departamentsList)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.insertButton.sizePolicy().hasHeightForWidth())
        self.insertButton.setSizePolicy(sizePolicy)
        self.insertButton.setMinimumSize(QtCore.QSize(0, 30))
        self.insertButton.setObjectName(_fromUtf8("insertButton"))
        self.horizontalLayout.addWidget(self.insertButton)
        self.modifyButton = QtGui.QPushButton(departamentsList)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modifyButton.sizePolicy().hasHeightForWidth())
        self.modifyButton.setSizePolicy(sizePolicy)
        self.modifyButton.setMinimumSize(QtCore.QSize(0, 30))
        self.modifyButton.setObjectName(_fromUtf8("modifyButton"))
        self.horizontalLayout.addWidget(self.modifyButton)
        self.deleteButton = QtGui.QPushButton(departamentsList)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deleteButton.sizePolicy().hasHeightForWidth())
        self.deleteButton.setSizePolicy(sizePolicy)
        self.deleteButton.setMinimumSize(QtCore.QSize(0, 30))
        self.deleteButton.setObjectName(_fromUtf8("deleteButton"))
        self.horizontalLayout.addWidget(self.deleteButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(departamentsList)
        QtCore.QMetaObject.connectSlotsByName(departamentsList)

    def retranslateUi(self, departamentsList):
        departamentsList.setWindowTitle(QtGui.QApplication.translate("departamentsList", "Departaments", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("departamentsList", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1, QtGui.QApplication.translate("departamentsList", "Description", None, QtGui.QApplication.UnicodeUTF8))
        self.insertButton.setText(QtGui.QApplication.translate("departamentsList", "Insert", None, QtGui.QApplication.UnicodeUTF8))
        self.modifyButton.setText(QtGui.QApplication.translate("departamentsList", "Modify", None, QtGui.QApplication.UnicodeUTF8))
        self.deleteButton.setText(QtGui.QApplication.translate("departamentsList", "Delete", None, QtGui.QApplication.UnicodeUTF8))

