# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widget_explore.ui',
# licensing of 'widget_explore.ui' applies.
#
# Created: Fri May 29 08:47:57 2020
#      by: pyside2-uic  running on PySide2 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_widgetExplore11(object):
    def setupUi(self, widgetExplore11):
        widgetExplore11.setObjectName("widgetExplore11")
        widgetExplore11.resize(593, 1102)
        widgetExplore11.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtWidgets.QVBoxLayout(widgetExplore11)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(widgetExplore11)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.widget = QtWidgets.QWidget(widgetExplore11)
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(self.widget)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.editSet = QtWidgets.QLineEdit(self.widget)
        self.editSet.setObjectName("editSet")
        self.gridLayout.addWidget(self.editSet, 0, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.editEvaluate = QtWidgets.QPlainTextEdit(self.widget)
        self.editEvaluate.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        self.editEvaluate.setObjectName("editEvaluate")
        self.gridLayout.addWidget(self.editEvaluate, 1, 1, 1, 1)
        self.editResult = QtWidgets.QPlainTextEdit(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editResult.sizePolicy().hasHeightForWidth())
        self.editResult.setSizePolicy(sizePolicy)
        self.editResult.setMaximumSize(QtCore.QSize(16777215, 40))
        self.editResult.setObjectName("editResult")
        self.gridLayout.addWidget(self.editResult, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.widget)
        self.toolBox = QtWidgets.QToolBox(widgetExplore11)
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 567, 416))
        self.page.setObjectName("page")
        self.formLayout = QtWidgets.QFormLayout(self.page)
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtWidgets.QLabel(self.page)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.editFrom = QtWidgets.QDoubleSpinBox(self.page)
        self.editFrom.setDecimals(3)
        self.editFrom.setMinimum(-1e+17)
        self.editFrom.setMaximum(1e+23)
        self.editFrom.setObjectName("editFrom")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.editFrom)
        self.label_5 = QtWidgets.QLabel(self.page)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.editTo = QtWidgets.QDoubleSpinBox(self.page)
        self.editTo.setDecimals(3)
        self.editTo.setMinimum(-1e+17)
        self.editTo.setMaximum(1e+23)
        self.editTo.setProperty("value", 20.0)
        self.editTo.setObjectName("editTo")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.editTo)
        self.label_6 = QtWidgets.QLabel(self.page)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.editSteps = QtWidgets.QSpinBox(self.page)
        self.editSteps.setMaximum(100)
        self.editSteps.setProperty("value", 10)
        self.editSteps.setObjectName("editSteps")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.editSteps)
        self.btnGraph = QtWidgets.QPushButton(self.page)
        self.btnGraph.setObjectName("btnGraph")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.btnGraph)
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 567, 401))
        self.page_2.setObjectName("page_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.page_2)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_7 = QtWidgets.QLabel(self.page_2)
        self.label_7.setObjectName("label_7")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.editTarget = QtWidgets.QDoubleSpinBox(self.page_2)
        self.editTarget.setDecimals(3)
        self.editTarget.setMinimum(-1e+17)
        self.editTarget.setMaximum(1e+23)
        self.editTarget.setObjectName("editTarget")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.editTarget)
        self.btnGoalSeek = QtWidgets.QPushButton(self.page_2)
        self.btnGoalSeek.setObjectName("btnGoalSeek")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.btnGoalSeek)
        self.toolBox.addItem(self.page_2, "")
        self.verticalLayout.addWidget(self.toolBox)

        self.retranslateUi(widgetExplore11)
        self.toolBox.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(widgetExplore11)
        widgetExplore11.setTabOrder(self.editSet, self.editEvaluate)
        widgetExplore11.setTabOrder(self.editEvaluate, self.editFrom)
        widgetExplore11.setTabOrder(self.editFrom, self.editTo)
        widgetExplore11.setTabOrder(self.editTo, self.editSteps)
        widgetExplore11.setTabOrder(self.editSteps, self.btnGraph)
        widgetExplore11.setTabOrder(self.btnGraph, self.editTarget)
        widgetExplore11.setTabOrder(self.editTarget, self.btnGoalSeek)
        widgetExplore11.setTabOrder(self.btnGoalSeek, self.editResult)

    def retranslateUi(self, widgetExplore11):
        widgetExplore11.setWindowTitle(QtWidgets.QApplication.translate("widgetExplore11", "Form", None, -1))
        self.label.setText(QtWidgets.QApplication.translate("widgetExplore11", "<html><head/><body><p><span style=\" text-decoration: underline;\">Explore or solve 1-to-1 relations</span></p><p>Set any settable scalar property in the scene, for example s[\'cable\'].length</p><p>Solve statics</p><p>Evaluate another property of the scene (scalar) or python expression</p></body></html>", None, -1))
        self.label_8.setText(QtWidgets.QApplication.translate("widgetExplore11", "Evaluation result", None, -1))
        self.label_2.setText(QtWidgets.QApplication.translate("widgetExplore11", "Set", None, -1))
        self.editSet.setPlaceholderText(QtWidgets.QApplication.translate("widgetExplore11", " (Hint, drag and drop this from the \"derived properties\" widget).", None, -1))
        self.label_3.setText(QtWidgets.QApplication.translate("widgetExplore11", "Evaluate", None, -1))
        self.editEvaluate.setPlaceholderText(QtWidgets.QApplication.translate("widgetExplore11", "(Hint, drag and drop this from the \"derived properties\" widget).", None, -1))
        self.editResult.setPlaceholderText(QtWidgets.QApplication.translate("widgetExplore11", "The result of the evaluation will appear here", None, -1))
        self.label_4.setText(QtWidgets.QApplication.translate("widgetExplore11", "From value", None, -1))
        self.label_5.setText(QtWidgets.QApplication.translate("widgetExplore11", "To value", None, -1))
        self.label_6.setText(QtWidgets.QApplication.translate("widgetExplore11", "number of steps", None, -1))
        self.btnGraph.setText(QtWidgets.QApplication.translate("widgetExplore11", "produce graph", None, -1))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), QtWidgets.QApplication.translate("widgetExplore11", "Graph", None, -1))
        self.label_7.setText(QtWidgets.QApplication.translate("widgetExplore11", "Target value:", None, -1))
        self.btnGoalSeek.setText(QtWidgets.QApplication.translate("widgetExplore11", "Goal-seek", None, -1))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), QtWidgets.QApplication.translate("widgetExplore11", "Goal-seek", None, -1))

