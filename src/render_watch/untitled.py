# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rw.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QButtonGroup,
    QCheckBox, QComboBox, QDockWidget, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QRadioButton, QScrollArea, QSizePolicy,
    QSlider, QSpacerItem, QSpinBox, QStackedWidget,
    QTabWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1624, 1005)
        self.actionStandard_Tasks = QAction(MainWindow)
        self.actionStandard_Tasks.setObjectName(u"actionStandard_Tasks")
        self.actionStandard_Tasks.setCheckable(True)
        self.actionStandard_Tasks.setChecked(True)
        self.actionStandard_Tasks.setMenuRole(QAction.ApplicationSpecificRole)
        self.actionMulti_Task = QAction(MainWindow)
        self.actionMulti_Task.setObjectName(u"actionMulti_Task")
        self.actionMulti_Task.setCheckable(True)
        self.actionRender_Watch_Help = QAction(MainWindow)
        self.actionRender_Watch_Help.setObjectName(u"actionRender_Watch_Help")
        self.actionAbout_Render_Watch = QAction(MainWindow)
        self.actionAbout_Render_Watch.setObjectName(u"actionAbout_Render_Watch")
        self.actionAdd = QAction(MainWindow)
        self.actionAdd.setObjectName(u"actionAdd")
        self.actionRemove = QAction(MainWindow)
        self.actionRemove.setObjectName(u"actionRemove")
        self.actionRemove_All = QAction(MainWindow)
        self.actionRemove_All.setObjectName(u"actionRemove_All")
        self.actionQuit = QAction(MainWindow)
        self.actionQuit.setObjectName(u"actionQuit")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionPreview = QAction(MainWindow)
        self.actionPreview.setObjectName(u"actionPreview")
        self.actionPreview.setCheckable(True)
        self.actionPreview.setChecked(True)
        self.actionPreview.setVisible(True)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.treeWidget_2 = QTreeWidget(self.centralwidget)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"#");
        self.treeWidget_2.setHeaderItem(__qtreewidgetitem)
        self.treeWidget_2.setObjectName(u"treeWidget_2")
        self.treeWidget_2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeWidget_2.setDragDropMode(QAbstractItemView.DropOnly)
        self.treeWidget_2.setAlternatingRowColors(True)
        self.treeWidget_2.setSelectionMode(QAbstractItemView.MultiSelection)
        self.treeWidget_2.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.treeWidget_2.setTextElideMode(Qt.ElideLeft)
        self.treeWidget_2.header().setVisible(True)
        self.treeWidget_2.header().setCascadingSectionResizes(True)
        self.treeWidget_2.header().setMinimumSectionSize(40)
        self.treeWidget_2.header().setStretchLastSection(True)

        self.gridLayout.addWidget(self.treeWidget_2, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1624, 29))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        self.menuEncoder = QMenu(self.menubar)
        self.menuEncoder.setObjectName(u"menuEncoder")
        MainWindow.setMenuBar(self.menubar)
        self.dockWidget_4 = QDockWidget(MainWindow)
        self.dockWidget_4.setObjectName(u"dockWidget_4")
        self.dockWidgetContents_4 = QWidget()
        self.dockWidgetContents_4.setObjectName(u"dockWidgetContents_4")
        self.gridLayout_11 = QGridLayout(self.dockWidgetContents_4)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.stackedWidget_2 = QStackedWidget(self.dockWidgetContents_4)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.gridLayout_10 = QGridLayout(self.page_4)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget = QStackedWidget(self.page_4)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.gridLayout_2 = QGridLayout(self.page_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.page_2)
        self.label.setObjectName(u"label")
        self.label.setScaledContents(True)
        self.label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.label)


        self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_2)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout_3 = QGridLayout(self.page)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(40, -1, 40, -1)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.label_2 = QLabel(self.page)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_3.addWidget(self.label_2)

        self.progressBar_2 = QProgressBar(self.page)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setMaximum(0)
        self.progressBar_2.setValue(0)
        self.progressBar_2.setTextVisible(False)

        self.verticalLayout_3.addWidget(self.progressBar_2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.gridLayout_3.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.gridLayout_4 = QGridLayout(self.page_3)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_3 = QLabel(self.page_3)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setEnabled(False)
        self.label_3.setAlignment(Qt.AlignCenter)

        self.verticalLayout_4.addWidget(self.label_3)


        self.gridLayout_4.addLayout(self.verticalLayout_4, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.page_3)

        self.verticalLayout.addWidget(self.stackedWidget)

        self.frame_5 = QFrame(self.page_4)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.frame_5)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_4 = QLabel(self.frame_5)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_6.addWidget(self.label_4)

        self.horizontalSlider = QSlider(self.frame_5)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.horizontalSlider.sizePolicy().hasHeightForWidth())
        self.horizontalSlider.setSizePolicy(sizePolicy2)
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.verticalLayout_6.addWidget(self.horizontalSlider)

        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer)

        self.radioButton_2 = QRadioButton(self.frame_5)
        self.radioButton_2.setObjectName(u"radioButton_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.radioButton_2.sizePolicy().hasHeightForWidth())
        self.radioButton_2.setSizePolicy(sizePolicy3)
        self.radioButton_2.setChecked(True)

        self.horizontalLayout_17.addWidget(self.radioButton_2)

        self.radioButton_5 = QRadioButton(self.frame_5)
        self.radioButton_5.setObjectName(u"radioButton_5")
        sizePolicy3.setHeightForWidth(self.radioButton_5.sizePolicy().hasHeightForWidth())
        self.radioButton_5.setSizePolicy(sizePolicy3)

        self.horizontalLayout_17.addWidget(self.radioButton_5)

        self.radioButton_4 = QRadioButton(self.frame_5)
        self.radioButton_4.setObjectName(u"radioButton_4")
        sizePolicy3.setHeightForWidth(self.radioButton_4.sizePolicy().hasHeightForWidth())
        self.radioButton_4.setSizePolicy(sizePolicy3)

        self.horizontalLayout_17.addWidget(self.radioButton_4)

        self.radioButton_3 = QRadioButton(self.frame_5)
        self.radioButton_3.setObjectName(u"radioButton_3")
        sizePolicy3.setHeightForWidth(self.radioButton_3.sizePolicy().hasHeightForWidth())
        self.radioButton_3.setSizePolicy(sizePolicy3)

        self.horizontalLayout_17.addWidget(self.radioButton_3)

        self.radioButton = QRadioButton(self.frame_5)
        self.radioButton.setObjectName(u"radioButton")
        sizePolicy3.setHeightForWidth(self.radioButton.sizePolicy().hasHeightForWidth())
        self.radioButton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_17.addWidget(self.radioButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout_17.addItem(self.horizontalSpacer_2)


        self.verticalLayout_6.addLayout(self.horizontalLayout_17)


        self.verticalLayout.addWidget(self.frame_5)


        self.gridLayout_10.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.stackedWidget_2.addWidget(self.page_4)
        self.page_5 = QWidget()
        self.page_5.setObjectName(u"page_5")
        self.verticalLayout_5 = QVBoxLayout(self.page_5)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label_23 = QLabel(self.page_5)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setEnabled(False)
        self.label_23.setAlignment(Qt.AlignCenter)

        self.verticalLayout_5.addWidget(self.label_23)

        self.stackedWidget_2.addWidget(self.page_5)

        self.gridLayout_11.addWidget(self.stackedWidget_2, 0, 0, 1, 1)

        self.dockWidget_4.setWidget(self.dockWidgetContents_4)
        MainWindow.addDockWidget(Qt.TopDockWidgetArea, self.dockWidget_4)
        self.dockWidget_3 = QDockWidget(MainWindow)
        self.dockWidget_3.setObjectName(u"dockWidget_3")
        self.dockWidgetContents_3 = QWidget()
        self.dockWidgetContents_3.setObjectName(u"dockWidgetContents_3")
        self.gridLayout_17 = QGridLayout(self.dockWidgetContents_3)
        self.gridLayout_17.setObjectName(u"gridLayout_17")
        self.stackedWidget_7 = QStackedWidget(self.dockWidgetContents_3)
        self.stackedWidget_7.setObjectName(u"stackedWidget_7")
        self.page_14 = QWidget()
        self.page_14.setObjectName(u"page_14")
        self.gridLayout_18 = QGridLayout(self.page_14)
        self.gridLayout_18.setObjectName(u"gridLayout_18")
        self.gridLayout_18.setHorizontalSpacing(0)
        self.gridLayout_18.setContentsMargins(0, 0, 0, 0)
        self.tabWidget = QTabWidget(self.page_14)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setElideMode(Qt.ElideNone)
        self.presets_tab = QWidget()
        self.presets_tab.setObjectName(u"presets_tab")
        self.gridLayout_19 = QGridLayout(self.presets_tab)
        self.gridLayout_19.setObjectName(u"gridLayout_19")
        self.gridLayout_19.setContentsMargins(0, 0, 0, 0)
        self.treeWidget = QTreeWidget(self.presets_tab)
        __qtreewidgetitem1 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(self.treeWidget)
        self.treeWidget.setObjectName(u"treeWidget")
        self.treeWidget.setFrameShape(QFrame.NoFrame)
        self.treeWidget.setAlternatingRowColors(True)

        self.gridLayout_19.addWidget(self.treeWidget, 0, 0, 1, 1)

        self.tabWidget.addTab(self.presets_tab, "")
        self.general_tab = QWidget()
        self.general_tab.setObjectName(u"general_tab")
        self.gridLayout_20 = QGridLayout(self.general_tab)
        self.gridLayout_20.setObjectName(u"gridLayout_20")
        self.gridLayout_20.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.general_tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 372, 216))
        self.verticalLayout_14 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_11 = QLabel(self.scrollAreaWidgetContents)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout.addWidget(self.label_11)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_3)

        self.comboBox = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)


        self.verticalLayout_14.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_12 = QLabel(self.scrollAreaWidgetContents)
        self.label_12.setObjectName(u"label_12")

        self.horizontalLayout_2.addWidget(self.label_12)

        self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_7)

        self.comboBox_2 = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_2.setObjectName(u"comboBox_2")

        self.horizontalLayout_2.addWidget(self.comboBox_2)


        self.verticalLayout_14.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, -1, -1, -1)
        self.label_31 = QLabel(self.scrollAreaWidgetContents)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMargin(0)

        self.horizontalLayout_5.addWidget(self.label_31)

        self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_12)

        self.comboBox_4 = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_4.setObjectName(u"comboBox_4")

        self.horizontalLayout_5.addWidget(self.comboBox_4)


        self.verticalLayout_14.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, -1, -1, -1)
        self.label_30 = QLabel(self.scrollAreaWidgetContents)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMargin(0)

        self.horizontalLayout_4.addWidget(self.label_30)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_10)

        self.comboBox_3 = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_3.setObjectName(u"comboBox_3")

        self.horizontalLayout_4.addWidget(self.comboBox_3)


        self.verticalLayout_14.addLayout(self.horizontalLayout_4)

        self.line_2 = QFrame(self.scrollAreaWidgetContents)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_14.addWidget(self.line_2)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, -1, -1, -1)
        self.label_32 = QLabel(self.scrollAreaWidgetContents)
        self.label_32.setObjectName(u"label_32")
        self.label_32.setMargin(0)

        self.horizontalLayout_8.addWidget(self.label_32)

        self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_13)

        self.comboBox_5 = QComboBox(self.scrollAreaWidgetContents)
        self.comboBox_5.setObjectName(u"comboBox_5")

        self.horizontalLayout_8.addWidget(self.comboBox_5)


        self.verticalLayout_14.addLayout(self.horizontalLayout_8)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_9)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_20.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.tabWidget.addTab(self.general_tab, "")
        self.video_codec_tab = QWidget()
        self.video_codec_tab.setObjectName(u"video_codec_tab")
        self.gridLayout_21 = QGridLayout(self.video_codec_tab)
        self.gridLayout_21.setObjectName(u"gridLayout_21")
        self.stackedWidget_8 = QStackedWidget(self.video_codec_tab)
        self.stackedWidget_8.setObjectName(u"stackedWidget_8")
        self.page_16 = QWidget()
        self.page_16.setObjectName(u"page_16")
        self.stackedWidget_8.addWidget(self.page_16)
        self.page_17 = QWidget()
        self.page_17.setObjectName(u"page_17")
        self.verticalLayout_15 = QVBoxLayout(self.page_17)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.label_33 = QLabel(self.page_17)
        self.label_33.setObjectName(u"label_33")
        self.label_33.setEnabled(False)
        self.label_33.setAlignment(Qt.AlignCenter)

        self.verticalLayout_15.addWidget(self.label_33)

        self.stackedWidget_8.addWidget(self.page_17)

        self.gridLayout_21.addWidget(self.stackedWidget_8, 0, 0, 1, 1)

        self.tabWidget.addTab(self.video_codec_tab, "")
        self.audio_codec_tab = QWidget()
        self.audio_codec_tab.setObjectName(u"audio_codec_tab")
        self.gridLayout_22 = QGridLayout(self.audio_codec_tab)
        self.gridLayout_22.setObjectName(u"gridLayout_22")
        self.stackedWidget_9 = QStackedWidget(self.audio_codec_tab)
        self.stackedWidget_9.setObjectName(u"stackedWidget_9")
        self.page_18 = QWidget()
        self.page_18.setObjectName(u"page_18")
        self.verticalLayout_16 = QVBoxLayout(self.page_18)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.label_34 = QLabel(self.page_18)
        self.label_34.setObjectName(u"label_34")
        self.label_34.setEnabled(False)
        self.label_34.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_34)

        self.stackedWidget_9.addWidget(self.page_18)
        self.page_19 = QWidget()
        self.page_19.setObjectName(u"page_19")
        self.stackedWidget_9.addWidget(self.page_19)

        self.gridLayout_22.addWidget(self.stackedWidget_9, 0, 0, 1, 1)

        self.tabWidget.addTab(self.audio_codec_tab, "")
        self.filters_tab = QWidget()
        self.filters_tab.setObjectName(u"filters_tab")
        self.gridLayout_23 = QGridLayout(self.filters_tab)
        self.gridLayout_23.setObjectName(u"gridLayout_23")
        self.stackedWidget_10 = QStackedWidget(self.filters_tab)
        self.stackedWidget_10.setObjectName(u"stackedWidget_10")
        self.page_20 = QWidget()
        self.page_20.setObjectName(u"page_20")
        self.verticalLayout_18 = QVBoxLayout(self.page_20)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.label_35 = QLabel(self.page_20)
        self.label_35.setObjectName(u"label_35")
        self.label_35.setEnabled(False)
        self.label_35.setAlignment(Qt.AlignCenter)

        self.verticalLayout_18.addWidget(self.label_35)

        self.stackedWidget_10.addWidget(self.page_20)
        self.page_21 = QWidget()
        self.page_21.setObjectName(u"page_21")
        self.stackedWidget_10.addWidget(self.page_21)

        self.gridLayout_23.addWidget(self.stackedWidget_10, 0, 0, 1, 1)

        self.tabWidget.addTab(self.filters_tab, "")
        self.subtitles_tab = QWidget()
        self.subtitles_tab.setObjectName(u"subtitles_tab")
        self.gridLayout_24 = QGridLayout(self.subtitles_tab)
        self.gridLayout_24.setObjectName(u"gridLayout_24")
        self.stackedWidget_11 = QStackedWidget(self.subtitles_tab)
        self.stackedWidget_11.setObjectName(u"stackedWidget_11")
        self.page_22 = QWidget()
        self.page_22.setObjectName(u"page_22")
        self.gridLayout_25 = QGridLayout(self.page_22)
        self.gridLayout_25.setObjectName(u"gridLayout_25")
        self.gridLayout_25.setContentsMargins(0, 0, 0, 0)
        self.label_36 = QLabel(self.page_22)
        self.label_36.setObjectName(u"label_36")
        self.label_36.setEnabled(False)
        self.label_36.setAlignment(Qt.AlignCenter)

        self.gridLayout_25.addWidget(self.label_36, 0, 0, 1, 1)

        self.stackedWidget_11.addWidget(self.page_22)
        self.page_23 = QWidget()
        self.page_23.setObjectName(u"page_23")
        self.stackedWidget_11.addWidget(self.page_23)

        self.gridLayout_24.addWidget(self.stackedWidget_11, 0, 0, 1, 1)

        self.tabWidget.addTab(self.subtitles_tab, "")

        self.gridLayout_18.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.stackedWidget_7.addWidget(self.page_14)
        self.page_15 = QWidget()
        self.page_15.setObjectName(u"page_15")
        self.verticalLayout_13 = QVBoxLayout(self.page_15)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_9 = QLabel(self.page_15)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setEnabled(False)
        self.label_9.setAlignment(Qt.AlignCenter)

        self.verticalLayout_13.addWidget(self.label_9)

        self.stackedWidget_7.addWidget(self.page_15)

        self.gridLayout_17.addWidget(self.stackedWidget_7, 0, 0, 1, 1)

        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget_3)
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout_16 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_16.setObjectName(u"gridLayout_16")
        self.stackedWidget_6 = QStackedWidget(self.dockWidgetContents)
        self.stackedWidget_6.setObjectName(u"stackedWidget_6")
        self.page_12 = QWidget()
        self.page_12.setObjectName(u"page_12")
        self.verticalLayout_11 = QVBoxLayout(self.page_12)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_5)

        self.frame = QFrame(self.page_12)
        self.frame.setObjectName(u"frame")
        sizePolicy4 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy4)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_5 = QGridLayout(self.frame)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.label_17 = QLabel(self.frame)
        self.label_17.setObjectName(u"label_17")
        sizePolicy5 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.label_17.sizePolicy().hasHeightForWidth())
        self.label_17.setSizePolicy(sizePolicy5)
        self.label_17.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_18.addWidget(self.label_17)

        self.label_18 = QLabel(self.frame)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_18.addWidget(self.label_18)


        self.gridLayout_5.addLayout(self.horizontalLayout_18, 0, 1, 1, 1)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label_21 = QLabel(self.frame)
        self.label_21.setObjectName(u"label_21")
        sizePolicy5.setHeightForWidth(self.label_21.sizePolicy().hasHeightForWidth())
        self.label_21.setSizePolicy(sizePolicy5)
        self.label_21.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_20.addWidget(self.label_21)

        self.label_22 = QLabel(self.frame)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_20.addWidget(self.label_22)


        self.gridLayout_5.addLayout(self.horizontalLayout_20, 1, 1, 1, 1)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_15 = QLabel(self.frame)
        self.label_15.setObjectName(u"label_15")
        sizePolicy5.setHeightForWidth(self.label_15.sizePolicy().hasHeightForWidth())
        self.label_15.setSizePolicy(sizePolicy5)
        self.label_15.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_14.addWidget(self.label_15)

        self.label_16 = QLabel(self.frame)
        self.label_16.setObjectName(u"label_16")
        sizePolicy4.setHeightForWidth(self.label_16.sizePolicy().hasHeightForWidth())
        self.label_16.setSizePolicy(sizePolicy4)

        self.horizontalLayout_14.addWidget(self.label_16)


        self.gridLayout_5.addLayout(self.horizontalLayout_14, 0, 0, 1, 1)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.label_19 = QLabel(self.frame)
        self.label_19.setObjectName(u"label_19")
        sizePolicy5.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy5)
        self.label_19.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_19.addWidget(self.label_19)

        self.label_20 = QLabel(self.frame)
        self.label_20.setObjectName(u"label_20")
        sizePolicy4.setHeightForWidth(self.label_20.sizePolicy().hasHeightForWidth())
        self.label_20.setSizePolicy(sizePolicy4)

        self.horizontalLayout_19.addWidget(self.label_20)


        self.gridLayout_5.addLayout(self.horizontalLayout_19, 1, 0, 1, 1)


        self.verticalLayout_11.addWidget(self.frame)

        self.progressBar = QProgressBar(self.page_12)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(24)
        self.progressBar.setTextVisible(False)

        self.verticalLayout_11.addWidget(self.progressBar)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.radioButton_11 = QRadioButton(self.page_12)
        self.buttonGroup_2 = QButtonGroup(MainWindow)
        self.buttonGroup_2.setObjectName(u"buttonGroup_2")
        self.buttonGroup_2.addButton(self.radioButton_11)
        self.radioButton_11.setObjectName(u"radioButton_11")
        sizePolicy6 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.radioButton_11.sizePolicy().hasHeightForWidth())
        self.radioButton_11.setSizePolicy(sizePolicy6)
        self.radioButton_11.setChecked(True)

        self.horizontalLayout_23.addWidget(self.radioButton_11)

        self.radioButton_10 = QRadioButton(self.page_12)
        self.buttonGroup_2.addButton(self.radioButton_10)
        self.radioButton_10.setObjectName(u"radioButton_10")
        sizePolicy6.setHeightForWidth(self.radioButton_10.sizePolicy().hasHeightForWidth())
        self.radioButton_10.setSizePolicy(sizePolicy6)
        self.radioButton_10.setChecked(False)

        self.horizontalLayout_23.addWidget(self.radioButton_10)

        self.horizontalSpacer_11 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_23.addItem(self.horizontalSpacer_11)


        self.verticalLayout_11.addLayout(self.horizontalLayout_23)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_6)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(-1, 0, -1, 0)
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_21.addItem(self.horizontalSpacer_9)

        self.radioButton_9 = QRadioButton(self.page_12)
        self.buttonGroup = QButtonGroup(MainWindow)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radioButton_9)
        self.radioButton_9.setObjectName(u"radioButton_9")
        self.radioButton_9.setChecked(True)
        self.radioButton_9.setAutoExclusive(False)

        self.horizontalLayout_21.addWidget(self.radioButton_9)

        self.radioButton_8 = QRadioButton(self.page_12)
        self.buttonGroup.addButton(self.radioButton_8)
        self.radioButton_8.setObjectName(u"radioButton_8")
        self.radioButton_8.setAutoExclusive(False)

        self.horizontalLayout_21.addWidget(self.radioButton_8)

        self.stackedWidget_3 = QStackedWidget(self.page_12)
        self.stackedWidget_3.setObjectName(u"stackedWidget_3")
        sizePolicy7 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.stackedWidget_3.sizePolicy().hasHeightForWidth())
        self.stackedWidget_3.setSizePolicy(sizePolicy7)
        self.page_8 = QWidget()
        self.page_8.setObjectName(u"page_8")
        self.gridLayout_6 = QGridLayout(self.page_8)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.pushButton_5 = QPushButton(self.page_8)
        self.pushButton_5.setObjectName(u"pushButton_5")

        self.gridLayout_6.addWidget(self.pushButton_5, 0, 0, 1, 1)

        self.stackedWidget_3.addWidget(self.page_8)
        self.page_9 = QWidget()
        self.page_9.setObjectName(u"page_9")
        self.gridLayout_7 = QGridLayout(self.page_9)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.pushButton_6 = QPushButton(self.page_9)
        self.pushButton_6.setObjectName(u"pushButton_6")

        self.gridLayout_7.addWidget(self.pushButton_6, 0, 0, 1, 1)

        self.stackedWidget_3.addWidget(self.page_9)

        self.horizontalLayout_21.addWidget(self.stackedWidget_3)


        self.verticalLayout_11.addLayout(self.horizontalLayout_21)

        self.stackedWidget_6.addWidget(self.page_12)
        self.page_13 = QWidget()
        self.page_13.setObjectName(u"page_13")
        self.verticalLayout_12 = QVBoxLayout(self.page_13)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_8 = QLabel(self.page_13)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setEnabled(False)
        self.label_8.setAlignment(Qt.AlignCenter)

        self.verticalLayout_12.addWidget(self.label_8)

        self.stackedWidget_6.addWidget(self.page_13)

        self.gridLayout_16.addWidget(self.stackedWidget_6, 0, 0, 1, 1)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)
        self.dockWidget_2 = QDockWidget(MainWindow)
        self.dockWidget_2.setObjectName(u"dockWidget_2")
        self.dockWidget_2.setFloating(False)
        self.dockWidget_2.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dockWidgetContents_2 = QWidget()
        self.dockWidgetContents_2.setObjectName(u"dockWidgetContents_2")
        self.gridLayout_13 = QGridLayout(self.dockWidgetContents_2)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.stackedWidget_4 = QStackedWidget(self.dockWidgetContents_2)
        self.stackedWidget_4.setObjectName(u"stackedWidget_4")
        self.page_6 = QWidget()
        self.page_6.setObjectName(u"page_6")
        self.gridLayout_12 = QGridLayout(self.page_6)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.frame_2 = QFrame(self.page_6)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout_8 = QGridLayout(self.frame_2)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_5 = QLabel(self.frame_2)
        self.label_5.setObjectName(u"label_5")
        font = QFont()
        font.setPointSize(12)
        self.label_5.setFont(font)

        self.verticalLayout_7.addWidget(self.label_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.checkBox = QCheckBox(self.frame_2)
        self.checkBox.setObjectName(u"checkBox")
        self.checkBox.setChecked(True)

        self.horizontalLayout_3.addWidget(self.checkBox)

        self.line = QFrame(self.frame_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.radioButton_7 = QRadioButton(self.frame_2)
        self.radioButton_7.setObjectName(u"radioButton_7")
        self.radioButton_7.setChecked(True)

        self.horizontalLayout_3.addWidget(self.radioButton_7)

        self.radioButton_6 = QRadioButton(self.frame_2)
        self.radioButton_6.setObjectName(u"radioButton_6")

        self.horizontalLayout_3.addWidget(self.radioButton_6)


        self.verticalLayout_7.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_10 = QLabel(self.frame_2)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_6.addWidget(self.label_10)

        self.spinBox_7 = QSpinBox(self.frame_2)
        self.spinBox_7.setObjectName(u"spinBox_7")
        sizePolicy3.setHeightForWidth(self.spinBox_7.sizePolicy().hasHeightForWidth())
        self.spinBox_7.setSizePolicy(sizePolicy3)
        self.spinBox_7.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_6.addWidget(self.spinBox_7)


        self.horizontalLayout_10.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_24 = QLabel(self.frame_2)
        self.label_24.setObjectName(u"label_24")
        sizePolicy4.setHeightForWidth(self.label_24.sizePolicy().hasHeightForWidth())
        self.label_24.setSizePolicy(sizePolicy4)
        self.label_24.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.horizontalLayout_9.addWidget(self.label_24)

        self.spinBox_8 = QSpinBox(self.frame_2)
        self.spinBox_8.setObjectName(u"spinBox_8")
        sizePolicy3.setHeightForWidth(self.spinBox_8.sizePolicy().hasHeightForWidth())
        self.spinBox_8.setSizePolicy(sizePolicy3)
        self.spinBox_8.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_9.addWidget(self.spinBox_8)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_4)


        self.horizontalLayout_10.addLayout(self.horizontalLayout_9)


        self.verticalLayout_7.addLayout(self.horizontalLayout_10)

        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_25 = QLabel(self.frame_2)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_22.addWidget(self.label_25)

        self.horizontalSlider_4 = QSlider(self.frame_2)
        self.horizontalSlider_4.setObjectName(u"horizontalSlider_4")
        self.horizontalSlider_4.setOrientation(Qt.Horizontal)

        self.horizontalLayout_22.addWidget(self.horizontalSlider_4)


        self.verticalLayout_7.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_26 = QLabel(self.frame_2)
        self.label_26.setObjectName(u"label_26")
        self.label_26.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_24.addWidget(self.label_26)

        self.horizontalSlider_5 = QSlider(self.frame_2)
        self.horizontalSlider_5.setObjectName(u"horizontalSlider_5")
        self.horizontalSlider_5.setOrientation(Qt.Horizontal)

        self.horizontalLayout_24.addWidget(self.horizontalSlider_5)


        self.verticalLayout_7.addLayout(self.horizontalLayout_24)


        self.gridLayout_8.addLayout(self.verticalLayout_7, 0, 0, 1, 1)


        self.horizontalLayout_28.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.page_6)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_9 = QGridLayout(self.frame_3)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_27 = QLabel(self.frame_3)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setFont(font)

        self.verticalLayout_8.addWidget(self.label_27)

        self.checkBox_2 = QCheckBox(self.frame_3)
        self.checkBox_2.setObjectName(u"checkBox_2")

        self.verticalLayout_8.addWidget(self.checkBox_2)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_28 = QLabel(self.frame_3)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_25.addWidget(self.label_28)

        self.spinBox_9 = QSpinBox(self.frame_3)
        self.spinBox_9.setObjectName(u"spinBox_9")
        sizePolicy3.setHeightForWidth(self.spinBox_9.sizePolicy().hasHeightForWidth())
        self.spinBox_9.setSizePolicy(sizePolicy3)
        self.spinBox_9.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_25.addWidget(self.spinBox_9)


        self.horizontalLayout_27.addLayout(self.horizontalLayout_25)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.label_29 = QLabel(self.frame_3)
        self.label_29.setObjectName(u"label_29")

        self.horizontalLayout_26.addWidget(self.label_29)

        self.spinBox_10 = QSpinBox(self.frame_3)
        self.spinBox_10.setObjectName(u"spinBox_10")
        sizePolicy3.setHeightForWidth(self.spinBox_10.sizePolicy().hasHeightForWidth())
        self.spinBox_10.setSizePolicy(sizePolicy3)
        self.spinBox_10.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_26.addWidget(self.spinBox_10)


        self.horizontalLayout_27.addLayout(self.horizontalLayout_26)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_27.addItem(self.horizontalSpacer_6)


        self.verticalLayout_8.addLayout(self.horizontalLayout_27)


        self.gridLayout_9.addLayout(self.verticalLayout_8, 0, 0, 1, 1)


        self.horizontalLayout_28.addWidget(self.frame_3)


        self.gridLayout_12.addLayout(self.horizontalLayout_28, 1, 0, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.pushButton_8 = QPushButton(self.page_6)
        self.pushButton_8.setObjectName(u"pushButton_8")

        self.horizontalLayout_15.addWidget(self.pushButton_8)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout_15.addItem(self.horizontalSpacer_5)

        self.pushButton_2 = QPushButton(self.page_6)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout_15.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(self.page_6)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_15.addWidget(self.pushButton)


        self.gridLayout_12.addLayout(self.horizontalLayout_15, 3, 0, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_12.addItem(self.verticalSpacer_7, 0, 0, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_12.addItem(self.verticalSpacer_8, 2, 0, 1, 1)

        self.stackedWidget_4.addWidget(self.page_6)
        self.page_7 = QWidget()
        self.page_7.setObjectName(u"page_7")
        self.verticalLayout_9 = QVBoxLayout(self.page_7)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_6 = QLabel(self.page_7)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setEnabled(False)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.label_6)

        self.stackedWidget_4.addWidget(self.page_7)

        self.gridLayout_13.addWidget(self.stackedWidget_4, 0, 0, 1, 1)

        self.dockWidget_2.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(Qt.TopDockWidgetArea, self.dockWidget_2)
        self.dockWidget_8 = QDockWidget(MainWindow)
        self.dockWidget_8.setObjectName(u"dockWidget_8")
        self.dockWidgetContents_8 = QWidget()
        self.dockWidgetContents_8.setObjectName(u"dockWidgetContents_8")
        self.gridLayout_15 = QGridLayout(self.dockWidgetContents_8)
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.stackedWidget_5 = QStackedWidget(self.dockWidgetContents_8)
        self.stackedWidget_5.setObjectName(u"stackedWidget_5")
        self.page_10 = QWidget()
        self.page_10.setObjectName(u"page_10")
        self.gridLayout_14 = QGridLayout(self.page_10)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.gridLayout_14.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_14.addItem(self.verticalSpacer_3, 0, 0, 1, 1)

        self.frame_4 = QFrame(self.page_10)
        self.frame_4.setObjectName(u"frame_4")
        sizePolicy4.setHeightForWidth(self.frame_4.sizePolicy().hasHeightForWidth())
        self.frame_4.setSizePolicy(sizePolicy4)
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_17 = QVBoxLayout(self.frame_4)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_13 = QLabel(self.frame_4)
        self.label_13.setObjectName(u"label_13")
        sizePolicy1.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy1)

        self.verticalLayout_17.addWidget(self.label_13)

        self.horizontalSlider_3 = QSlider(self.frame_4)
        self.horizontalSlider_3.setObjectName(u"horizontalSlider_3")
        self.horizontalSlider_3.setMaximum(100)
        self.horizontalSlider_3.setSliderPosition(100)
        self.horizontalSlider_3.setOrientation(Qt.Horizontal)
        self.horizontalSlider_3.setInvertedAppearance(True)
        self.horizontalSlider_3.setInvertedControls(False)

        self.verticalLayout_17.addWidget(self.horizontalSlider_3)

        self.horizontalSlider_2 = QSlider(self.frame_4)
        self.horizontalSlider_2.setObjectName(u"horizontalSlider_2")
        self.horizontalSlider_2.setMaximum(100)
        self.horizontalSlider_2.setValue(100)
        self.horizontalSlider_2.setSliderPosition(100)
        self.horizontalSlider_2.setOrientation(Qt.Horizontal)
        self.horizontalSlider_2.setInvertedAppearance(False)
        self.horizontalSlider_2.setInvertedControls(False)

        self.verticalLayout_17.addWidget(self.horizontalSlider_2)

        self.label_14 = QLabel(self.frame_4)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy1)
        self.label_14.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_17.addWidget(self.label_14)


        self.gridLayout_14.addWidget(self.frame_4, 1, 0, 1, 1)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.pushButton_9 = QPushButton(self.page_10)
        self.pushButton_9.setObjectName(u"pushButton_9")

        self.horizontalLayout_16.addWidget(self.pushButton_9)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_8)

        self.pushButton_3 = QPushButton(self.page_10)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout_16.addWidget(self.pushButton_3)

        self.pushButton_4 = QPushButton(self.page_10)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_16.addWidget(self.pushButton_4)


        self.gridLayout_14.addLayout(self.horizontalLayout_16, 3, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_14.addItem(self.verticalSpacer_4, 2, 0, 1, 1)

        self.stackedWidget_5.addWidget(self.page_10)
        self.page_11 = QWidget()
        self.page_11.setObjectName(u"page_11")
        self.verticalLayout_10 = QVBoxLayout(self.page_11)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_7 = QLabel(self.page_11)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setEnabled(False)
        self.label_7.setAlignment(Qt.AlignCenter)

        self.verticalLayout_10.addWidget(self.label_7)

        self.stackedWidget_5.addWidget(self.page_11)

        self.gridLayout_15.addWidget(self.stackedWidget_5, 1, 0, 1, 1)

        self.dockWidget_8.setWidget(self.dockWidgetContents_8)
        MainWindow.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget_8)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuEncoder.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionAdd)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionRemove)
        self.menuFile.addAction(self.actionRemove_All)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionPreferences)
        self.menuView.addAction(self.actionPreview)
        self.menuHelp.addAction(self.actionRender_Watch_Help)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionAbout_Render_Watch)
        self.menuEncoder.addAction(self.actionStandard_Tasks)
        self.menuEncoder.addAction(self.actionMulti_Task)

        self.retranslateUi(MainWindow)

        self.stackedWidget_2.setCurrentIndex(1)
        self.stackedWidget.setCurrentIndex(1)
        self.stackedWidget_7.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget_8.setCurrentIndex(1)
        self.stackedWidget_11.setCurrentIndex(0)
        self.stackedWidget_6.setCurrentIndex(1)
        self.stackedWidget_3.setCurrentIndex(0)
        self.stackedWidget_4.setCurrentIndex(1)
        self.stackedWidget_5.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Render Watch", None))
        self.actionStandard_Tasks.setText(QCoreApplication.translate("MainWindow", u"Standard Tasks", None))
        self.actionMulti_Task.setText(QCoreApplication.translate("MainWindow", u"Multi-Task", None))
        self.actionRender_Watch_Help.setText(QCoreApplication.translate("MainWindow", u"Render Watch Help", None))
        self.actionAbout_Render_Watch.setText(QCoreApplication.translate("MainWindow", u"About Render Watch", None))
        self.actionAdd.setText(QCoreApplication.translate("MainWindow", u"Add...", None))
        self.actionRemove.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.actionRemove_All.setText(QCoreApplication.translate("MainWindow", u"Remove All", None))
        self.actionQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionPreview.setText(QCoreApplication.translate("MainWindow", u"Preview", None))
        ___qtreewidgetitem = self.treeWidget_2.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Info.", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"File Path", None));
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.menuEncoder.setTitle(QCoreApplication.translate("MainWindow", u"Encoder", None))
        self.dockWidget_4.setWindowTitle(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"PREVIEW", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Getting preview ready...", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Wrong video codec settings", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"##:##:##.#", None))
        self.radioButton_2.setText(QCoreApplication.translate("MainWindow", u"Live", None))
        self.radioButton_5.setText(QCoreApplication.translate("MainWindow", u"5s", None))
        self.radioButton_4.setText(QCoreApplication.translate("MainWindow", u"10s", None))
        self.radioButton_3.setText(QCoreApplication.translate("MainWindow", u"20s", None))
        self.radioButton.setText(QCoreApplication.translate("MainWindow", u"30s", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"No input selected", None))
        self.dockWidget_3.setWindowTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        ___qtreewidgetitem1 = self.treeWidget.headerItem()
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Description", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem2 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Common", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem2.child(0)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("MainWindow", u"H264 Copy", None));
        ___qtreewidgetitem4 = ___qtreewidgetitem2.child(1)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("MainWindow", u"H264 Quality", None));
        ___qtreewidgetitem5 = ___qtreewidgetitem2.child(2)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("MainWindow", u"H264 Compression", None));
        ___qtreewidgetitem6 = self.treeWidget.topLevelItem(1)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("MainWindow", u"Devices", None));
        ___qtreewidgetitem7 = self.treeWidget.topLevelItem(2)
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("MainWindow", u"Web", None));
        self.treeWidget.setSortingEnabled(__sortingEnabled)

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.presets_tab), QCoreApplication.translate("MainWindow", u"Presets", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Container:", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Video Codec:", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Audio Codec:", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Video Stream:", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Frame Rate:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general_tab), QCoreApplication.translate("MainWindow", u"General", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Not available with copy codec", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.video_codec_tab), QCoreApplication.translate("MainWindow", u"VIdeo Codec", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"Not available with copy codec", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.audio_codec_tab), QCoreApplication.translate("MainWindow", u"Audio Codec", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"Not available with copy codec", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.filters_tab), QCoreApplication.translate("MainWindow", u"Filters", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"Subtitles not available", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.subtitles_tab), QCoreApplication.translate("MainWindow", u"Subtitles", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"No input selected", None))
        self.dockWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Benchmark", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Speed:", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"###.#x", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Est. Task Duration:", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"##:##:##.#", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Bitrate:", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"#####.#kbps", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Est. File Size:", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"###.#MB", None))
        self.radioButton_11.setText(QCoreApplication.translate("MainWindow", u"Short", None))
        self.radioButton_10.setText(QCoreApplication.translate("MainWindow", u"Long", None))
        self.radioButton_9.setText(QCoreApplication.translate("MainWindow", u"Standard Task", None))
        self.radioButton_8.setText(QCoreApplication.translate("MainWindow", u"Multi-Task", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.pushButton_6.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"No input selected", None))
        self.dockWidget_2.setWindowTitle(QCoreApplication.translate("MainWindow", u"Picture", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.checkBox.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.radioButton_7.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.radioButton_6.setText(QCoreApplication.translate("MainWindow", u"Custom", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Width:", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Height:", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Padding X:", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"Padding Y:", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.checkBox_2.setText(QCoreApplication.translate("MainWindow", u"Enabled", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Width:", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Height:", None))
        self.pushButton_8.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"No input selected", None))
        self.dockWidget_8.setWindowTitle(QCoreApplication.translate("MainWindow", u"Trim", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"00:00:00.0", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"##:##:##.#", None))
        self.pushButton_9.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.pushButton_4.setText(QCoreApplication.translate("MainWindow", u"Cancel", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"No input selected", None))
    # retranslateUi

