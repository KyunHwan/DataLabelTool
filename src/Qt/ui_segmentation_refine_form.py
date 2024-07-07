# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'segmentation_refine_form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGroupBox,
    QLabel, QListWidget, QListWidgetItem, QPushButton,
    QSizePolicy, QSpinBox, QTabWidget, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1459, 816)
        self.tabWidget = QTabWidget(Form)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(20, 10, 1421, 801))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.frame = QFrame(self.tab)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(10, 10, 1181, 681))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayoutWidget = QWidget(self.frame)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 1161, 651))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_loadImage = QPushButton(self.tab)
        self.pushButton_loadImage.setObjectName(u"pushButton_loadImage")
        self.pushButton_loadImage.setGeometry(QRect(1250, 10, 111, 31))
        self.spinBox_brushSize = QSpinBox(self.tab)
        self.spinBox_brushSize.setObjectName(u"spinBox_brushSize")
        self.spinBox_brushSize.setGeometry(QRect(1310, 220, 88, 22))
        self.spinBox_brushSize.setMinimum(1)
        self.spinBox_brushSize.setMaximum(30)
        self.spinBox_brushSize.setValue(6)
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(1230, 220, 71, 20))
        self.spinBox_segId = QSpinBox(self.tab)
        self.spinBox_segId.setObjectName(u"spinBox_segId")
        self.spinBox_segId.setGeometry(QRect(1310, 280, 88, 22))
        self.spinBox_segId.setMaximum(255)
        self.spinBox_segId.setSingleStep(1)
        self.spinBox_segId.setValue(0)
        self.label_2 = QLabel(self.tab)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(1230, 280, 81, 20))
        self.pushButton_loadMasks = QPushButton(self.tab)
        self.pushButton_loadMasks.setObjectName(u"pushButton_loadMasks")
        self.pushButton_loadMasks.setEnabled(True)
        self.pushButton_loadMasks.setGeometry(QRect(1250, 50, 111, 31))
        self.pushButton_saveMasks = QPushButton(self.tab)
        self.pushButton_saveMasks.setObjectName(u"pushButton_saveMasks")
        self.pushButton_saveMasks.setGeometry(QRect(1250, 130, 111, 31))
        self.checkBox_overlaySegMask = QCheckBox(self.tab)
        self.checkBox_overlaySegMask.setObjectName(u"checkBox_overlaySegMask")
        self.checkBox_overlaySegMask.setGeometry(QRect(30, 740, 181, 20))
        self.checkBox_overlaySegMask.setChecked(True)
        self.listWidget_segIdPaletteList = QListWidget(self.tab)
        self.listWidget_segIdPaletteList.setObjectName(u"listWidget_segIdPaletteList")
        self.listWidget_segIdPaletteList.setGeometry(QRect(1224, 318, 171, 201))
        self.label_curPos = QLabel(self.tab)
        self.label_curPos.setObjectName(u"label_curPos")
        self.label_curPos.setGeometry(QRect(1320, 710, 81, 20))
        self.label_curSegID = QLabel(self.tab)
        self.label_curSegID.setObjectName(u"label_curSegID")
        self.label_curSegID.setGeometry(QRect(1320, 740, 81, 20))
        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(1204, 540, 211, 151))
        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 70, 91, 16))
        self.spinBox_curBlobID = QSpinBox(self.groupBox_2)
        self.spinBox_curBlobID.setObjectName(u"spinBox_curBlobID")
        self.spinBox_curBlobID.setGeometry(QRect(110, 40, 88, 22))
        self.spinBox_curBlobID.setMaximum(255)
        self.pushButton_updateBlobID = QPushButton(self.groupBox_2)
        self.pushButton_updateBlobID.setObjectName(u"pushButton_updateBlobID")
        self.pushButton_updateBlobID.setGeometry(QRect(100, 105, 75, 24))
        self.spinBox_newBlobID = QSpinBox(self.groupBox_2)
        self.spinBox_newBlobID.setObjectName(u"spinBox_newBlobID")
        self.spinBox_newBlobID.setGeometry(QRect(110, 70, 88, 21))
        self.spinBox_newBlobID.setMaximum(255)
        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 40, 91, 16))
        self.pushButton_autoSeg = QPushButton(self.tab)
        self.pushButton_autoSeg.setObjectName(u"pushButton_autoSeg")
        self.pushButton_autoSeg.setGeometry(QRect(1250, 90, 111, 31))
        self.checkBox_eraserEnabled = QCheckBox(self.tab)
        self.checkBox_eraserEnabled.setObjectName(u"checkBox_eraserEnabled")
        self.checkBox_eraserEnabled.setGeometry(QRect(1230, 250, 161, 21))
        self.pushButton_clear = QPushButton(self.tab)
        self.pushButton_clear.setObjectName(u"pushButton_clear")
        self.pushButton_clear.setGeometry(QRect(1250, 170, 111, 31))
        self.tabWidget.addTab(self.tab, "")

        self.retranslateUi(Form)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"AI Segmentation Review", None))
        self.pushButton_loadImage.setText(QCoreApplication.translate("Form", u"Load Image", None))
        self.label.setText(QCoreApplication.translate("Form", u"Brush (-=) :", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"Seg ID ([]) :", None))
        self.pushButton_loadMasks.setText(QCoreApplication.translate("Form", u"Load masks", None))
        self.pushButton_saveMasks.setText(QCoreApplication.translate("Form", u"Save masks", None))
        self.checkBox_overlaySegMask.setText(QCoreApplication.translate("Form", u"Overlay seg mask (Rt)", None))
        self.label_curPos.setText(QCoreApplication.translate("Form", u"Pos (0, 0)", None))
        self.label_curSegID.setText(QCoreApplication.translate("Form", u"Seg ID = 0", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Form", u"Edit Blob ID ", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"New Blob ID:", None))
        self.pushButton_updateBlobID.setText(QCoreApplication.translate("Form", u"Update", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Cur Blob ID:", None))
        self.pushButton_autoSeg.setText(QCoreApplication.translate("Form", u"Auto Seg", None))
        self.checkBox_eraserEnabled.setText(QCoreApplication.translate("Form", u"Eraser Enabled", None))
        self.pushButton_clear.setText(QCoreApplication.translate("Form", u"Clear", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("Form", u"Slice View", None))
    # retranslateUi

