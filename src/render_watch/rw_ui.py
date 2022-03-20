# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rw_v3.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMenu, QMenuBar, QProgressBar,
    QPushButton, QRadioButton, QSizePolicy, QSlider,
    QSpacerItem, QSpinBox, QSplitter, QStackedWidget,
    QToolBox, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 720)
        self.about_render_watch_action = QAction(MainWindow)
        self.about_render_watch_action.setObjectName(u"about_render_watch_action")
        self.add_action = QAction(MainWindow)
        self.add_action.setObjectName(u"add_action")
        self.quit_action = QAction(MainWindow)
        self.quit_action.setObjectName(u"quit_action")
        self.remove_action = QAction(MainWindow)
        self.remove_action.setObjectName(u"remove_action")
        self.remove_all_action = QAction(MainWindow)
        self.remove_all_action.setObjectName(u"remove_all_action")
        self.preferences_action = QAction(MainWindow)
        self.preferences_action.setObjectName(u"preferences_action")
        self.standard_action = QAction(MainWindow)
        self.standard_action.setObjectName(u"standard_action")
        self.multi_task_action = QAction(MainWindow)
        self.multi_task_action.setObjectName(u"multi_task_action")
        self.actionHost = QAction(MainWindow)
        self.actionHost.setObjectName(u"actionHost")
        self.actionClient = QAction(MainWindow)
        self.actionClient.setObjectName(u"actionClient")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_12 = QGridLayout(self.centralwidget)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.gridLayout_12.setContentsMargins(3, 3, 3, 3)
        self.sidebar_splitter = QSplitter(self.centralwidget)
        self.sidebar_splitter.setObjectName(u"sidebar_splitter")
        self.sidebar_splitter.setOrientation(Qt.Horizontal)
        self.sidebar_splitter.setHandleWidth(3)
        self.preview_splitter = QSplitter(self.sidebar_splitter)
        self.preview_splitter.setObjectName(u"preview_splitter")
        self.preview_splitter.setOrientation(Qt.Vertical)
        self.preview_splitter.setHandleWidth(3)
        self.preview_splitter.setChildrenCollapsible(False)
        self.preview_stack = QStackedWidget(self.preview_splitter)
        self.preview_stack.setObjectName(u"preview_stack")
        self.preview_page = QWidget()
        self.preview_page.setObjectName(u"preview_page")
        self.gridLayout = QGridLayout(self.preview_page)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.preview_page)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.frame)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(-1, -1, -1, 6)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.preview_state_stack = QStackedWidget(self.frame)
        self.preview_state_stack.setObjectName(u"preview_state_stack")
        self.preview_not_ready_page = QWidget()
        self.preview_not_ready_page.setObjectName(u"preview_not_ready_page")
        self.verticalLayout_8 = QVBoxLayout(self.preview_not_ready_page)
        self.verticalLayout_8.setSpacing(10)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(40, 0, 40, 0)
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer)

        self.label_5 = QLabel(self.preview_not_ready_page)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setAlignment(Qt.AlignCenter)

        self.verticalLayout_8.addWidget(self.label_5)

        self.progressBar = QProgressBar(self.preview_not_ready_page)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy1)
        self.progressBar.setMaximum(0)
        self.progressBar.setValue(-1)
        self.progressBar.setTextVisible(False)

        self.verticalLayout_8.addWidget(self.progressBar)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_2)

        self.preview_state_stack.addWidget(self.preview_not_ready_page)
        self.preview_ready_page = QWidget()
        self.preview_ready_page.setObjectName(u"preview_ready_page")
        self.verticalLayout_9 = QVBoxLayout(self.preview_ready_page)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.label_56 = QLabel(self.preview_ready_page)
        self.label_56.setObjectName(u"label_56")

        self.horizontalLayout_2.addWidget(self.label_56)

        self.preview_source_combobox = QComboBox(self.preview_ready_page)
        self.preview_source_combobox.addItem("")
        self.preview_source_combobox.addItem("")
        self.preview_source_combobox.setObjectName(u"preview_source_combobox")

        self.horizontalLayout_2.addWidget(self.preview_source_combobox)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)

        self.label_2 = QLabel(self.preview_ready_page)
        self.label_2.setObjectName(u"label_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy2)
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(Qt.AlignCenter)

        self.verticalLayout_9.addWidget(self.label_2)

        self.preview_state_stack.addWidget(self.preview_ready_page)
        self.preview_no_avail_page = QWidget()
        self.preview_no_avail_page.setObjectName(u"preview_no_avail_page")
        self.verticalLayout_14 = QVBoxLayout(self.preview_no_avail_page)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_6 = QLabel(self.preview_no_avail_page)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setEnabled(False)
        self.label_6.setAlignment(Qt.AlignCenter)

        self.verticalLayout_14.addWidget(self.label_6)

        self.preview_state_stack.addWidget(self.preview_no_avail_page)

        self.verticalLayout.addWidget(self.preview_state_stack)


        self.verticalLayout_5.addLayout(self.verticalLayout)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setEnabled(False)
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_5.addWidget(self.label_3)

        self.preview_position_slider = QSlider(self.frame)
        self.preview_position_slider.setObjectName(u"preview_position_slider")
        self.preview_position_slider.setEnabled(False)
        self.preview_position_slider.setMaximum(100)
        self.preview_position_slider.setValue(25)
        self.preview_position_slider.setOrientation(Qt.Horizontal)
        self.preview_position_slider.setTickPosition(QSlider.NoTicks)

        self.verticalLayout_5.addWidget(self.preview_position_slider)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 4)
        self.preview_live_radiobutton = QRadioButton(self.frame)
        self.preview_live_radiobutton.setObjectName(u"preview_live_radiobutton")
        self.preview_live_radiobutton.setEnabled(False)
        sizePolicy3 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.preview_live_radiobutton.sizePolicy().hasHeightForWidth())
        self.preview_live_radiobutton.setSizePolicy(sizePolicy3)
        self.preview_live_radiobutton.setChecked(True)

        self.horizontalLayout_3.addWidget(self.preview_live_radiobutton)

        self.preview_5s_radiobutton = QRadioButton(self.frame)
        self.preview_5s_radiobutton.setObjectName(u"preview_5s_radiobutton")
        self.preview_5s_radiobutton.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.preview_5s_radiobutton.sizePolicy().hasHeightForWidth())
        self.preview_5s_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.preview_5s_radiobutton)

        self.preview_10s_radiobutton = QRadioButton(self.frame)
        self.preview_10s_radiobutton.setObjectName(u"preview_10s_radiobutton")
        self.preview_10s_radiobutton.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.preview_10s_radiobutton.sizePolicy().hasHeightForWidth())
        self.preview_10s_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.preview_10s_radiobutton)

        self.preview_20s_radiobutton = QRadioButton(self.frame)
        self.preview_20s_radiobutton.setObjectName(u"preview_20s_radiobutton")
        self.preview_20s_radiobutton.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.preview_20s_radiobutton.sizePolicy().hasHeightForWidth())
        self.preview_20s_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.preview_20s_radiobutton)

        self.preview_30s_radiobutton = QRadioButton(self.frame)
        self.preview_30s_radiobutton.setObjectName(u"preview_30s_radiobutton")
        self.preview_30s_radiobutton.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.preview_30s_radiobutton.sizePolicy().hasHeightForWidth())
        self.preview_30s_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_3.addWidget(self.preview_30s_radiobutton)


        self.verticalLayout_5.addLayout(self.horizontalLayout_3)


        self.gridLayout.addWidget(self.frame, 0, 0, 1, 1)

        self.preview_stack.addWidget(self.preview_page)
        self.crop_page = QWidget()
        self.crop_page.setObjectName(u"crop_page")
        self.gridLayout_4 = QGridLayout(self.crop_page)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(self.crop_page)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.crop_groupbox = QGroupBox(self.frame_3)
        self.crop_groupbox.setObjectName(u"crop_groupbox")
        self.crop_groupbox.setEnabled(False)
        self.crop_groupbox.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.crop_groupbox.setFlat(False)
        self.crop_groupbox.setCheckable(True)
        self.crop_groupbox.setChecked(False)
        self.verticalLayout_7 = QVBoxLayout(self.crop_groupbox)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_8 = QLabel(self.crop_groupbox)
        self.label_8.setObjectName(u"label_8")
        self.label_8.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_4.addWidget(self.label_8)

        self.crop_width_spinbox = QSpinBox(self.crop_groupbox)
        self.crop_width_spinbox.setObjectName(u"crop_width_spinbox")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.crop_width_spinbox.sizePolicy().hasHeightForWidth())
        self.crop_width_spinbox.setSizePolicy(sizePolicy4)
        self.crop_width_spinbox.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_4.addWidget(self.crop_width_spinbox)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_9 = QLabel(self.crop_groupbox)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_9)

        self.crop_height_spinbox = QSpinBox(self.crop_groupbox)
        self.crop_height_spinbox.setObjectName(u"crop_height_spinbox")
        sizePolicy4.setHeightForWidth(self.crop_height_spinbox.sizePolicy().hasHeightForWidth())
        self.crop_height_spinbox.setSizePolicy(sizePolicy4)
        self.crop_height_spinbox.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_5.addWidget(self.crop_height_spinbox)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_5)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_4)


        self.verticalLayout_7.addLayout(self.horizontalLayout_6)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_10 = QLabel(self.crop_groupbox)
        self.label_10.setObjectName(u"label_10")

        self.horizontalLayout_7.addWidget(self.label_10)

        self.crop_x_slider = QSlider(self.crop_groupbox)
        self.crop_x_slider.setObjectName(u"crop_x_slider")
        self.crop_x_slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_7.addWidget(self.crop_x_slider)


        self.verticalLayout_7.addLayout(self.horizontalLayout_7)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_11 = QLabel(self.crop_groupbox)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_8.addWidget(self.label_11)

        self.crop_y_slider = QSlider(self.crop_groupbox)
        self.crop_y_slider.setObjectName(u"crop_y_slider")
        self.crop_y_slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_8.addWidget(self.crop_y_slider)


        self.verticalLayout_7.addLayout(self.horizontalLayout_8)

        self.crop_auto_checkbox = QCheckBox(self.crop_groupbox)
        self.crop_auto_checkbox.setObjectName(u"crop_auto_checkbox")
        self.crop_auto_checkbox.setLayoutDirection(Qt.RightToLeft)
        self.crop_auto_checkbox.setChecked(False)

        self.verticalLayout_7.addWidget(self.crop_auto_checkbox)


        self.horizontalLayout_12.addWidget(self.crop_groupbox)

        self.groupBox_2 = QGroupBox(self.frame_3)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setEnabled(False)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setChecked(False)
        self.verticalLayout_10 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_9.addWidget(self.label_12)

        self.scale_width_spinbox = QSpinBox(self.groupBox_2)
        self.scale_width_spinbox.setObjectName(u"scale_width_spinbox")
        sizePolicy4.setHeightForWidth(self.scale_width_spinbox.sizePolicy().hasHeightForWidth())
        self.scale_width_spinbox.setSizePolicy(sizePolicy4)
        self.scale_width_spinbox.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_9.addWidget(self.scale_width_spinbox)


        self.horizontalLayout_11.addLayout(self.horizontalLayout_9)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_10.addWidget(self.label_13)

        self.scale_height_spinbox = QSpinBox(self.groupBox_2)
        self.scale_height_spinbox.setObjectName(u"scale_height_spinbox")
        sizePolicy4.setHeightForWidth(self.scale_height_spinbox.sizePolicy().hasHeightForWidth())
        self.scale_height_spinbox.setSizePolicy(sizePolicy4)
        self.scale_height_spinbox.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_10.addWidget(self.scale_height_spinbox)


        self.horizontalLayout_11.addLayout(self.horizontalLayout_10)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_11.addItem(self.horizontalSpacer_5)


        self.verticalLayout_10.addLayout(self.horizontalLayout_11)


        self.horizontalLayout_12.addWidget(self.groupBox_2)


        self.gridLayout_3.addLayout(self.horizontalLayout_12, 1, 0, 1, 1)

        self.crop_preview_stack = QStackedWidget(self.frame_3)
        self.crop_preview_stack.setObjectName(u"crop_preview_stack")
        self.crop_preview_page = QWidget()
        self.crop_preview_page.setObjectName(u"crop_preview_page")
        self.verticalLayout_15 = QVBoxLayout(self.crop_preview_page)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.crop_preview_label = QLabel(self.crop_preview_page)
        self.crop_preview_label.setObjectName(u"crop_preview_label")
        sizePolicy5 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.crop_preview_label.sizePolicy().hasHeightForWidth())
        self.crop_preview_label.setSizePolicy(sizePolicy5)
        self.crop_preview_label.setScaledContents(True)
        self.crop_preview_label.setAlignment(Qt.AlignCenter)

        self.verticalLayout_15.addWidget(self.crop_preview_label)

        self.crop_preview_stack.addWidget(self.crop_preview_page)
        self.crop_preview_no_avail_page = QWidget()
        self.crop_preview_no_avail_page.setObjectName(u"crop_preview_no_avail_page")
        self.verticalLayout_16 = QVBoxLayout(self.crop_preview_no_avail_page)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.label_24 = QLabel(self.crop_preview_no_avail_page)
        self.label_24.setObjectName(u"label_24")
        self.label_24.setEnabled(False)
        self.label_24.setAlignment(Qt.AlignCenter)

        self.verticalLayout_16.addWidget(self.label_24)

        self.crop_preview_stack.addWidget(self.crop_preview_no_avail_page)

        self.gridLayout_3.addWidget(self.crop_preview_stack, 0, 0, 1, 1)


        self.gridLayout_4.addWidget(self.frame_3, 0, 0, 1, 1)

        self.preview_stack.addWidget(self.crop_page)
        self.trim_page = QWidget()
        self.trim_page.setObjectName(u"trim_page")
        self.gridLayout_5 = QGridLayout(self.trim_page)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.trim_page)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.frame_4)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.trim_preview_stack = QStackedWidget(self.frame_4)
        self.trim_preview_stack.setObjectName(u"trim_preview_stack")
        self.trim_preview_page = QWidget()
        self.trim_preview_page.setObjectName(u"trim_preview_page")
        self.gridLayout_10 = QGridLayout(self.trim_preview_page)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.gridLayout_10.setContentsMargins(0, 0, 0, 0)
        self.trim_preview_label = QLabel(self.trim_preview_page)
        self.trim_preview_label.setObjectName(u"trim_preview_label")
        sizePolicy5.setHeightForWidth(self.trim_preview_label.sizePolicy().hasHeightForWidth())
        self.trim_preview_label.setSizePolicy(sizePolicy5)
        self.trim_preview_label.setScaledContents(True)
        self.trim_preview_label.setAlignment(Qt.AlignCenter)

        self.gridLayout_10.addWidget(self.trim_preview_label, 0, 0, 1, 1)

        self.trim_preview_stack.addWidget(self.trim_preview_page)
        self.trim_preview_no_avail_page = QWidget()
        self.trim_preview_no_avail_page.setObjectName(u"trim_preview_no_avail_page")
        self.verticalLayout_21 = QVBoxLayout(self.trim_preview_no_avail_page)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.label_29 = QLabel(self.trim_preview_no_avail_page)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setEnabled(False)
        self.label_29.setAlignment(Qt.AlignCenter)

        self.verticalLayout_21.addWidget(self.label_29)

        self.trim_preview_stack.addWidget(self.trim_preview_no_avail_page)

        self.verticalLayout_12.addWidget(self.trim_preview_stack)

        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.trim_start_label = QLabel(self.frame_4)
        self.trim_start_label.setObjectName(u"trim_start_label")
        self.trim_start_label.setEnabled(False)

        self.verticalLayout_11.addWidget(self.trim_start_label)

        self.trim_start_slider = QSlider(self.frame_4)
        self.trim_start_slider.setObjectName(u"trim_start_slider")
        self.trim_start_slider.setEnabled(False)
        self.trim_start_slider.setMaximum(100)
        self.trim_start_slider.setValue(0)
        self.trim_start_slider.setSliderPosition(0)
        self.trim_start_slider.setOrientation(Qt.Horizontal)

        self.verticalLayout_11.addWidget(self.trim_start_slider)

        self.trim_end_slider = QSlider(self.frame_4)
        self.trim_end_slider.setObjectName(u"trim_end_slider")
        self.trim_end_slider.setEnabled(False)
        self.trim_end_slider.setMaximum(100)
        self.trim_end_slider.setValue(0)
        self.trim_end_slider.setSliderPosition(0)
        self.trim_end_slider.setOrientation(Qt.Horizontal)
        self.trim_end_slider.setInvertedAppearance(True)
        self.trim_end_slider.setInvertedControls(True)

        self.verticalLayout_11.addWidget(self.trim_end_slider)

        self.trim_end_label = QLabel(self.frame_4)
        self.trim_end_label.setObjectName(u"trim_end_label")
        self.trim_end_label.setEnabled(False)
        self.trim_end_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.verticalLayout_11.addWidget(self.trim_end_label)


        self.verticalLayout_12.addLayout(self.verticalLayout_11)


        self.gridLayout_5.addWidget(self.frame_4, 0, 0, 1, 1)

        self.preview_stack.addWidget(self.trim_page)
        self.benchmark_page = QWidget()
        self.benchmark_page.setObjectName(u"benchmark_page")
        self.gridLayout_6 = QGridLayout(self.benchmark_page)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.frame_5 = QFrame(self.benchmark_page)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.gridLayout_9 = QGridLayout(self.frame_5)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.benchmark_stack = QStackedWidget(self.frame_5)
        self.benchmark_stack.setObjectName(u"benchmark_stack")
        self.benchmark_settings_page = QWidget()
        self.benchmark_settings_page.setObjectName(u"benchmark_settings_page")
        self.verticalLayout_6 = QVBoxLayout(self.benchmark_settings_page)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.frame_6 = QFrame(self.benchmark_settings_page)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.gridLayout_8 = QGridLayout(self.frame_6)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(6, -1, 6, -1)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.label_17 = QLabel(self.frame_6)
        self.label_17.setObjectName(u"label_17")

        self.horizontalLayout_13.addWidget(self.label_17)

        self.benchmark_avg_bitrate_label = QLabel(self.frame_6)
        self.benchmark_avg_bitrate_label.setObjectName(u"benchmark_avg_bitrate_label")

        self.horizontalLayout_13.addWidget(self.benchmark_avg_bitrate_label)


        self.gridLayout_7.addLayout(self.horizontalLayout_13, 0, 0, 1, 1)

        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.label_18 = QLabel(self.frame_6)
        self.label_18.setObjectName(u"label_18")

        self.horizontalLayout_14.addWidget(self.label_18)

        self.benchmark_speed_label = QLabel(self.frame_6)
        self.benchmark_speed_label.setObjectName(u"benchmark_speed_label")

        self.horizontalLayout_14.addWidget(self.benchmark_speed_label)


        self.gridLayout_7.addLayout(self.horizontalLayout_14, 0, 1, 1, 1)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.label_20 = QLabel(self.frame_6)
        self.label_20.setObjectName(u"label_20")

        self.horizontalLayout_15.addWidget(self.label_20)

        self.benchmark_file_size_label = QLabel(self.frame_6)
        self.benchmark_file_size_label.setObjectName(u"benchmark_file_size_label")

        self.horizontalLayout_15.addWidget(self.benchmark_file_size_label)


        self.gridLayout_7.addLayout(self.horizontalLayout_15, 1, 0, 1, 1)

        self.horizontalLayout_16 = QHBoxLayout()
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.label_22 = QLabel(self.frame_6)
        self.label_22.setObjectName(u"label_22")

        self.horizontalLayout_16.addWidget(self.label_22)

        self.benchmark_est_encode_time_label = QLabel(self.frame_6)
        self.benchmark_est_encode_time_label.setObjectName(u"benchmark_est_encode_time_label")

        self.horizontalLayout_16.addWidget(self.benchmark_est_encode_time_label)


        self.gridLayout_7.addLayout(self.horizontalLayout_16, 1, 1, 1, 1)


        self.gridLayout_8.addLayout(self.gridLayout_7, 0, 0, 1, 1)


        self.verticalLayout_6.addWidget(self.frame_6)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout_17 = QHBoxLayout()
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.benchmark_short_radiobutton = QRadioButton(self.benchmark_settings_page)
        self.benchmark_short_radiobutton.setObjectName(u"benchmark_short_radiobutton")
        sizePolicy3.setHeightForWidth(self.benchmark_short_radiobutton.sizePolicy().hasHeightForWidth())
        self.benchmark_short_radiobutton.setSizePolicy(sizePolicy3)
        self.benchmark_short_radiobutton.setChecked(True)

        self.horizontalLayout_17.addWidget(self.benchmark_short_radiobutton)

        self.benchmark_long_radiobutton = QRadioButton(self.benchmark_settings_page)
        self.benchmark_long_radiobutton.setObjectName(u"benchmark_long_radiobutton")

        self.horizontalLayout_17.addWidget(self.benchmark_long_radiobutton)


        self.horizontalLayout_18.addLayout(self.horizontalLayout_17)

        self.benchmark_multitask_checkbox = QCheckBox(self.benchmark_settings_page)
        self.benchmark_multitask_checkbox.setObjectName(u"benchmark_multitask_checkbox")
        self.benchmark_multitask_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_18.addWidget(self.benchmark_multitask_checkbox)


        self.verticalLayout_6.addLayout(self.horizontalLayout_18)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Maximum)

        self.verticalLayout_6.addItem(self.verticalSpacer_3)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(40, -1, 40, -1)
        self.benchmark_progressbar = QProgressBar(self.benchmark_settings_page)
        self.benchmark_progressbar.setObjectName(u"benchmark_progressbar")
        self.benchmark_progressbar.setValue(24)
        self.benchmark_progressbar.setTextVisible(False)

        self.verticalLayout_13.addWidget(self.benchmark_progressbar)


        self.verticalLayout_6.addLayout(self.verticalLayout_13)

        self.verticalSpacer_5 = QSpacerItem(20, 90, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_5)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_19.addItem(self.horizontalSpacer_6)

        self.benchmark_start_stop_pushbutton = QPushButton(self.benchmark_settings_page)
        self.benchmark_start_stop_pushbutton.setObjectName(u"benchmark_start_stop_pushbutton")

        self.horizontalLayout_19.addWidget(self.benchmark_start_stop_pushbutton)


        self.verticalLayout_6.addLayout(self.horizontalLayout_19)

        self.benchmark_stack.addWidget(self.benchmark_settings_page)
        self.benchmark_no_avail_page = QWidget()
        self.benchmark_no_avail_page.setObjectName(u"benchmark_no_avail_page")
        self.verticalLayout_17 = QVBoxLayout(self.benchmark_no_avail_page)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.label_25 = QLabel(self.benchmark_no_avail_page)
        self.label_25.setObjectName(u"label_25")
        self.label_25.setEnabled(False)
        self.label_25.setAlignment(Qt.AlignCenter)

        self.verticalLayout_17.addWidget(self.label_25)

        self.benchmark_stack.addWidget(self.benchmark_no_avail_page)

        self.gridLayout_9.addWidget(self.benchmark_stack, 0, 0, 1, 1)


        self.gridLayout_6.addWidget(self.frame_5, 0, 0, 1, 1)

        self.preview_stack.addWidget(self.benchmark_page)
        self.preview_splitter.addWidget(self.preview_stack)
        self.inputs_treewidget = QTreeWidget(self.preview_splitter)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(1, u"Name");
        self.inputs_treewidget.setHeaderItem(__qtreewidgetitem)
        self.inputs_treewidget.setObjectName(u"inputs_treewidget")
        self.preview_splitter.addWidget(self.inputs_treewidget)
        self.sidebar_splitter.addWidget(self.preview_splitter)
        self.sidebar_frame = QFrame(self.sidebar_splitter)
        self.sidebar_frame.setObjectName(u"sidebar_frame")
        self.sidebar_frame.setFrameShape(QFrame.StyledPanel)
        self.sidebar_frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.sidebar_frame)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.sidebar_toolbox = QToolBox(self.sidebar_frame)
        self.sidebar_toolbox.setObjectName(u"sidebar_toolbox")
        self.sidebar_toolbox.setEnabled(True)
        self.sidebar_toolbox.setFrameShape(QFrame.NoFrame)
        self.sidebar_toolbox.setFrameShadow(QFrame.Plain)
        self.presets = QWidget()
        self.presets.setObjectName(u"presets")
        self.presets.setGeometry(QRect(0, 0, 312, 450))
        self.verticalLayout_3 = QVBoxLayout(self.presets)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.treeWidget_2 = QTreeWidget(self.presets)
        self.treeWidget_2.setObjectName(u"treeWidget_2")

        self.verticalLayout_3.addWidget(self.treeWidget_2)

        self.sidebar_toolbox.addItem(self.presets, u"Presets")
        self.general = QWidget()
        self.general.setObjectName(u"general")
        self.general.setGeometry(QRect(0, 0, 312, 940))
        self.verticalLayout_4 = QVBoxLayout(self.general)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.label = QLabel(self.general)
        self.label.setObjectName(u"label")

        self.horizontalLayout_20.addWidget(self.label)

        self.container_combobox = QComboBox(self.general)
        self.container_combobox.setObjectName(u"container_combobox")

        self.horizontalLayout_20.addWidget(self.container_combobox)


        self.verticalLayout_4.addLayout(self.horizontalLayout_20)

        self.line = QFrame(self.general)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_4.addWidget(self.line)

        self.horizontalLayout_23 = QHBoxLayout()
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.label_28 = QLabel(self.general)
        self.label_28.setObjectName(u"label_28")

        self.horizontalLayout_23.addWidget(self.label_28)

        self.frame_rate_combobox = QComboBox(self.general)
        self.frame_rate_combobox.setObjectName(u"frame_rate_combobox")

        self.horizontalLayout_23.addWidget(self.frame_rate_combobox)


        self.verticalLayout_4.addLayout(self.horizontalLayout_23)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_6)

        self.sidebar_toolbox.addItem(self.general, u"General")
        self.video_codec = QWidget()
        self.video_codec.setObjectName(u"video_codec")
        self.video_codec.setGeometry(QRect(0, 0, 378, 1156))
        self.verticalLayout_18 = QVBoxLayout(self.video_codec)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_22 = QHBoxLayout()
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.label_27 = QLabel(self.video_codec)
        self.label_27.setObjectName(u"label_27")

        self.horizontalLayout_22.addWidget(self.label_27)

        self.video_stream_combobox = QComboBox(self.video_codec)
        self.video_stream_combobox.setObjectName(u"video_stream_combobox")

        self.horizontalLayout_22.addWidget(self.video_stream_combobox)


        self.verticalLayout_18.addLayout(self.horizontalLayout_22)

        self.horizontalLayout_21 = QHBoxLayout()
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.label_26 = QLabel(self.video_codec)
        self.label_26.setObjectName(u"label_26")

        self.horizontalLayout_21.addWidget(self.label_26)

        self.video_codec_combobox = QComboBox(self.video_codec)
        self.video_codec_combobox.setObjectName(u"video_codec_combobox")

        self.horizontalLayout_21.addWidget(self.video_codec_combobox)


        self.verticalLayout_18.addLayout(self.horizontalLayout_21)

        self.line_2 = QFrame(self.video_codec)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_18.addWidget(self.line_2)

        self.video_codec_stack = QStackedWidget(self.video_codec)
        self.video_codec_stack.setObjectName(u"video_codec_stack")
        self.x264_page = QWidget()
        self.x264_page.setObjectName(u"x264_page")
        self.verticalLayout_24 = QVBoxLayout(self.x264_page)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_24 = QHBoxLayout()
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.label_30 = QLabel(self.x264_page)
        self.label_30.setObjectName(u"label_30")

        self.horizontalLayout_24.addWidget(self.label_30)

        self.x264_preset_combobox = QComboBox(self.x264_page)
        self.x264_preset_combobox.setObjectName(u"x264_preset_combobox")

        self.horizontalLayout_24.addWidget(self.x264_preset_combobox)


        self.verticalLayout_24.addLayout(self.horizontalLayout_24)

        self.horizontalLayout_25 = QHBoxLayout()
        self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
        self.label_31 = QLabel(self.x264_page)
        self.label_31.setObjectName(u"label_31")

        self.horizontalLayout_25.addWidget(self.label_31)

        self.x264_profile_combobox = QComboBox(self.x264_page)
        self.x264_profile_combobox.setObjectName(u"x264_profile_combobox")

        self.horizontalLayout_25.addWidget(self.x264_profile_combobox)


        self.verticalLayout_24.addLayout(self.horizontalLayout_25)

        self.horizontalLayout_26 = QHBoxLayout()
        self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
        self.label_32 = QLabel(self.x264_page)
        self.label_32.setObjectName(u"label_32")

        self.horizontalLayout_26.addWidget(self.label_32)

        self.x264_tune_combobox = QComboBox(self.x264_page)
        self.x264_tune_combobox.setObjectName(u"x264_tune_combobox")

        self.horizontalLayout_26.addWidget(self.x264_tune_combobox)


        self.verticalLayout_24.addLayout(self.horizontalLayout_26)

        self.horizontalLayout_27 = QHBoxLayout()
        self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
        self.label_33 = QLabel(self.x264_page)
        self.label_33.setObjectName(u"label_33")

        self.horizontalLayout_27.addWidget(self.label_33)

        self.x264_level_combobox = QComboBox(self.x264_page)
        self.x264_level_combobox.setObjectName(u"x264_level_combobox")

        self.horizontalLayout_27.addWidget(self.x264_level_combobox)


        self.verticalLayout_24.addLayout(self.horizontalLayout_27)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_24.addItem(self.verticalSpacer_9)

        self.verticalLayout_23 = QVBoxLayout()
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.horizontalLayout_28 = QHBoxLayout()
        self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
        self.x264_crf_radiobutton = QRadioButton(self.x264_page)
        self.x264_crf_radiobutton.setObjectName(u"x264_crf_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_crf_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_crf_radiobutton.setSizePolicy(sizePolicy3)
        self.x264_crf_radiobutton.setChecked(True)

        self.horizontalLayout_28.addWidget(self.x264_crf_radiobutton)

        self.x264_qp_radiobutton = QRadioButton(self.x264_page)
        self.x264_qp_radiobutton.setObjectName(u"x264_qp_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_qp_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_qp_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_28.addWidget(self.x264_qp_radiobutton)

        self.x264_bitrate_radiobutton = QRadioButton(self.x264_page)
        self.x264_bitrate_radiobutton.setObjectName(u"x264_bitrate_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_bitrate_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_bitrate_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_28.addWidget(self.x264_bitrate_radiobutton)


        self.verticalLayout_23.addLayout(self.horizontalLayout_28)

        self.x264_rate_type_stack = QStackedWidget(self.x264_page)
        self.x264_rate_type_stack.setObjectName(u"x264_rate_type_stack")
        sizePolicy.setHeightForWidth(self.x264_rate_type_stack.sizePolicy().hasHeightForWidth())
        self.x264_rate_type_stack.setSizePolicy(sizePolicy)
        self.x264_rate_type_stack.setFrameShape(QFrame.StyledPanel)
        self.x264_rate_type_stack.setFrameShadow(QFrame.Sunken)
        self.x264_crf_page = QWidget()
        self.x264_crf_page.setObjectName(u"x264_crf_page")
        self.horizontalLayout_29 = QHBoxLayout(self.x264_crf_page)
        self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
        self.horizontalLayout_29.setContentsMargins(6, 6, 6, 6)
        self.x264_crf_label = QLabel(self.x264_crf_page)
        self.x264_crf_label.setObjectName(u"x264_crf_label")

        self.horizontalLayout_29.addWidget(self.x264_crf_label)

        self.x264_crf_value_label = QLabel(self.x264_crf_page)
        self.x264_crf_value_label.setObjectName(u"x264_crf_value_label")
        sizePolicy6 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.x264_crf_value_label.sizePolicy().hasHeightForWidth())
        self.x264_crf_value_label.setSizePolicy(sizePolicy6)
        self.x264_crf_value_label.setMinimumSize(QSize(20, 0))

        self.horizontalLayout_29.addWidget(self.x264_crf_value_label)

        self.x264_crf_slider = QSlider(self.x264_crf_page)
        self.x264_crf_slider.setObjectName(u"x264_crf_slider")
        self.x264_crf_slider.setMaximum(51)
        self.x264_crf_slider.setPageStep(5)
        self.x264_crf_slider.setValue(23)
        self.x264_crf_slider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_29.addWidget(self.x264_crf_slider)

        self.x264_rate_type_stack.addWidget(self.x264_crf_page)
        self.x264_bitrate_page = QWidget()
        self.x264_bitrate_page.setObjectName(u"x264_bitrate_page")
        self.verticalLayout_22 = QVBoxLayout(self.x264_bitrate_page)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(6, 6, 6, 6)
        self.horizontalLayout_30 = QHBoxLayout()
        self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
        self.label_34 = QLabel(self.x264_bitrate_page)
        self.label_34.setObjectName(u"label_34")

        self.horizontalLayout_30.addWidget(self.label_34)

        self.x264_bitrate_spinbutton = QSpinBox(self.x264_bitrate_page)
        self.x264_bitrate_spinbutton.setObjectName(u"x264_bitrate_spinbutton")

        self.horizontalLayout_30.addWidget(self.x264_bitrate_spinbutton)


        self.verticalLayout_22.addLayout(self.horizontalLayout_30)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.label_35 = QLabel(self.x264_bitrate_page)
        self.label_35.setObjectName(u"label_35")

        self.horizontalLayout_31.addWidget(self.label_35)

        self.x264_max_bitrate_spinbutton = QSpinBox(self.x264_bitrate_page)
        self.x264_max_bitrate_spinbutton.setObjectName(u"x264_max_bitrate_spinbutton")

        self.horizontalLayout_31.addWidget(self.x264_max_bitrate_spinbutton)


        self.verticalLayout_22.addLayout(self.horizontalLayout_31)

        self.horizontalLayout_32 = QHBoxLayout()
        self.horizontalLayout_32.setObjectName(u"horizontalLayout_32")
        self.label_36 = QLabel(self.x264_bitrate_page)
        self.label_36.setObjectName(u"label_36")

        self.horizontalLayout_32.addWidget(self.label_36)

        self.x264_min_bitrate_spinbutton = QSpinBox(self.x264_bitrate_page)
        self.x264_min_bitrate_spinbutton.setObjectName(u"x264_min_bitrate_spinbutton")

        self.horizontalLayout_32.addWidget(self.x264_min_bitrate_spinbutton)


        self.verticalLayout_22.addLayout(self.horizontalLayout_32)

        self.horizontalLayout_33 = QHBoxLayout()
        self.horizontalLayout_33.setObjectName(u"horizontalLayout_33")
        self.x264_average_radiobutton = QRadioButton(self.x264_bitrate_page)
        self.x264_average_radiobutton.setObjectName(u"x264_average_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_average_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_average_radiobutton.setSizePolicy(sizePolicy3)
        self.x264_average_radiobutton.setChecked(True)

        self.horizontalLayout_33.addWidget(self.x264_average_radiobutton)

        self.x264_constant_radiobutton = QRadioButton(self.x264_bitrate_page)
        self.x264_constant_radiobutton.setObjectName(u"x264_constant_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_constant_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_constant_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_33.addWidget(self.x264_constant_radiobutton)

        self.x264_2pass_radiobutton = QRadioButton(self.x264_bitrate_page)
        self.x264_2pass_radiobutton.setObjectName(u"x264_2pass_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_2pass_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_2pass_radiobutton.setSizePolicy(sizePolicy3)

        self.horizontalLayout_33.addWidget(self.x264_2pass_radiobutton)


        self.verticalLayout_22.addLayout(self.horizontalLayout_33)

        self.x264_rate_type_stack.addWidget(self.x264_bitrate_page)

        self.verticalLayout_23.addWidget(self.x264_rate_type_stack)


        self.verticalLayout_24.addLayout(self.verticalLayout_23)

        self.x264_advanced_groupbox = QGroupBox(self.x264_page)
        self.x264_advanced_groupbox.setObjectName(u"x264_advanced_groupbox")
        self.x264_advanced_groupbox.setFlat(False)
        self.x264_advanced_groupbox.setCheckable(True)
        self.x264_advanced_groupbox.setChecked(False)
        self.verticalLayout_25 = QVBoxLayout(self.x264_advanced_groupbox)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.x264_no_fast_p_skip_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_no_fast_p_skip_checkbox.setObjectName(u"x264_no_fast_p_skip_checkbox")
        self.x264_no_fast_p_skip_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_no_fast_p_skip_checkbox, 8, 0, 1, 1)

        self.line_3 = QFrame(self.x264_advanced_groupbox)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.VLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line_3, 0, 1, 16, 1)

        self.groupBox_4 = QGroupBox(self.x264_advanced_groupbox)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setCheckable(True)
        self.verticalLayout_28 = QVBoxLayout(self.groupBox_4)
        self.verticalLayout_28.setObjectName(u"verticalLayout_28")
        self.horizontalLayout_41 = QHBoxLayout()
        self.horizontalLayout_41.setObjectName(u"horizontalLayout_41")
        self.label_44 = QLabel(self.groupBox_4)
        self.label_44.setObjectName(u"label_44")
        self.label_44.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_41.addWidget(self.label_44)

        self.x264_deblock_alpha_spinbutton = QSpinBox(self.groupBox_4)
        self.x264_deblock_alpha_spinbutton.setObjectName(u"x264_deblock_alpha_spinbutton")

        self.horizontalLayout_41.addWidget(self.x264_deblock_alpha_spinbutton)


        self.verticalLayout_28.addLayout(self.horizontalLayout_41)

        self.horizontalLayout_42 = QHBoxLayout()
        self.horizontalLayout_42.setObjectName(u"horizontalLayout_42")
        self.label_45 = QLabel(self.groupBox_4)
        self.label_45.setObjectName(u"label_45")
        self.label_45.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.horizontalLayout_42.addWidget(self.label_45)

        self.x264_deblock_beta_spinbutton = QSpinBox(self.groupBox_4)
        self.x264_deblock_beta_spinbutton.setObjectName(u"x264_deblock_beta_spinbutton")

        self.horizontalLayout_42.addWidget(self.x264_deblock_beta_spinbutton)


        self.verticalLayout_28.addLayout(self.horizontalLayout_42)


        self.gridLayout_2.addWidget(self.groupBox_4, 11, 0, 3, 1)

        self.x264_mixed_refs_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_mixed_refs_checkbox.setObjectName(u"x264_mixed_refs_checkbox")
        self.x264_mixed_refs_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_mixed_refs_checkbox, 1, 2, 1, 1)

        self.horizontalLayout_36 = QHBoxLayout()
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.label_39 = QLabel(self.x264_advanced_groupbox)
        self.label_39.setObjectName(u"label_39")

        self.horizontalLayout_36.addWidget(self.label_39)

        self.x264_b_pyramid_combobox = QComboBox(self.x264_advanced_groupbox)
        self.x264_b_pyramid_combobox.setObjectName(u"x264_b_pyramid_combobox")

        self.horizontalLayout_36.addWidget(self.x264_b_pyramid_combobox)


        self.gridLayout_2.addLayout(self.horizontalLayout_36, 5, 0, 1, 1)

        self.x264_no_dct_decimate_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_no_dct_decimate_checkbox.setObjectName(u"x264_no_dct_decimate_checkbox")
        self.x264_no_dct_decimate_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_no_dct_decimate_checkbox, 10, 0, 1, 1)

        self.horizontalLayout_34 = QHBoxLayout()
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.label_37 = QLabel(self.x264_advanced_groupbox)
        self.label_37.setObjectName(u"label_37")

        self.horizontalLayout_34.addWidget(self.label_37)

        self.x264_b_frames_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_b_frames_spinbutton.setObjectName(u"x264_b_frames_spinbutton")

        self.horizontalLayout_34.addWidget(self.x264_b_frames_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_34, 3, 0, 1, 1)

        self.horizontalLayout_38 = QHBoxLayout()
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.label_41 = QLabel(self.x264_advanced_groupbox)
        self.label_41.setObjectName(u"label_41")

        self.horizontalLayout_38.addWidget(self.label_41)

        self.x264_min_keyint_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_min_keyint_spinbutton.setObjectName(u"x264_min_keyint_spinbutton")

        self.horizontalLayout_38.addWidget(self.x264_min_keyint_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_38, 1, 0, 1, 1)

        self.horizontalLayout_49 = QHBoxLayout()
        self.horizontalLayout_49.setObjectName(u"horizontalLayout_49")
        self.label_52 = QLabel(self.x264_advanced_groupbox)
        self.label_52.setObjectName(u"label_52")

        self.horizontalLayout_49.addWidget(self.label_52)

        self.x264_subme_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_subme_spinbutton.setObjectName(u"x264_subme_spinbutton")

        self.horizontalLayout_49.addWidget(self.x264_subme_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_49, 18, 2, 1, 1)

        self.horizontalLayout_43 = QHBoxLayout()
        self.horizontalLayout_43.setObjectName(u"horizontalLayout_43")
        self.label_46 = QLabel(self.x264_advanced_groupbox)
        self.label_46.setObjectName(u"label_46")

        self.horizontalLayout_43.addWidget(self.label_46)

        self.x264_aq_mode_combobox = QComboBox(self.x264_advanced_groupbox)
        self.x264_aq_mode_combobox.setObjectName(u"x264_aq_mode_combobox")

        self.horizontalLayout_43.addWidget(self.x264_aq_mode_combobox)


        self.gridLayout_2.addLayout(self.horizontalLayout_43, 2, 2, 1, 1)

        self.horizontalLayout_44 = QHBoxLayout()
        self.horizontalLayout_44.setObjectName(u"horizontalLayout_44")
        self.label_47 = QLabel(self.x264_advanced_groupbox)
        self.label_47.setObjectName(u"label_47")

        self.horizontalLayout_44.addWidget(self.label_47)

        self.x264_aq_strength_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_aq_strength_spinbutton.setObjectName(u"x264_aq_strength_spinbutton")

        self.horizontalLayout_44.addWidget(self.x264_aq_strength_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_44, 3, 2, 1, 1)

        self.horizontalLayout_48 = QHBoxLayout()
        self.horizontalLayout_48.setObjectName(u"horizontalLayout_48")
        self.label_51 = QLabel(self.x264_advanced_groupbox)
        self.label_51.setObjectName(u"label_51")

        self.horizontalLayout_48.addWidget(self.label_51)

        self.x264_me_range_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_me_range_spinbutton.setObjectName(u"x264_me_range_spinbutton")

        self.horizontalLayout_48.addWidget(self.x264_me_range_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_48, 17, 2, 1, 1)

        self.horizontalLayout_37 = QHBoxLayout()
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.label_40 = QLabel(self.x264_advanced_groupbox)
        self.label_40.setObjectName(u"label_40")

        self.horizontalLayout_37.addWidget(self.label_40)

        self.x264_keyint_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_keyint_spinbutton.setObjectName(u"x264_keyint_spinbutton")

        self.horizontalLayout_37.addWidget(self.x264_keyint_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_37, 0, 0, 1, 1)

        self.x264_weight_p_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_weight_p_checkbox.setObjectName(u"x264_weight_p_checkbox")
        self.x264_weight_p_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_weight_p_checkbox, 7, 0, 1, 1)

        self.horizontalLayout_40 = QHBoxLayout()
        self.horizontalLayout_40.setObjectName(u"horizontalLayout_40")
        self.label_43 = QLabel(self.x264_advanced_groupbox)
        self.label_43.setObjectName(u"label_43")

        self.horizontalLayout_40.addWidget(self.label_43)

        self.x264_b_adapt_combobox = QComboBox(self.x264_advanced_groupbox)
        self.x264_b_adapt_combobox.setObjectName(u"x264_b_adapt_combobox")

        self.horizontalLayout_40.addWidget(self.x264_b_adapt_combobox)


        self.gridLayout_2.addLayout(self.horizontalLayout_40, 4, 0, 1, 1)

        self.x264_weight_b_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_weight_b_checkbox.setObjectName(u"x264_weight_b_checkbox")
        self.x264_weight_b_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_weight_b_checkbox, 6, 0, 1, 1)

        self.x264_no_cabac_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_no_cabac_checkbox.setObjectName(u"x264_no_cabac_checkbox")
        self.x264_no_cabac_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_no_cabac_checkbox, 9, 0, 1, 1)

        self.label_48 = QLabel(self.x264_advanced_groupbox)
        self.label_48.setObjectName(u"label_48")

        self.gridLayout_2.addWidget(self.label_48, 4, 2, 1, 1)

        self.horizontalLayout_39 = QHBoxLayout()
        self.horizontalLayout_39.setObjectName(u"horizontalLayout_39")
        self.label_42 = QLabel(self.x264_advanced_groupbox)
        self.label_42.setObjectName(u"label_42")

        self.horizontalLayout_39.addWidget(self.label_42)

        self.x264_scenecut_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_scenecut_spinbutton.setObjectName(u"x264_scenecut_spinbutton")

        self.horizontalLayout_39.addWidget(self.x264_scenecut_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_39, 2, 0, 1, 1)

        self.horizontalLayout_35 = QHBoxLayout()
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.label_38 = QLabel(self.x264_advanced_groupbox)
        self.label_38.setObjectName(u"label_38")

        self.horizontalLayout_35.addWidget(self.label_38)

        self.x264_refs_spinbutton = QSpinBox(self.x264_advanced_groupbox)
        self.x264_refs_spinbutton.setObjectName(u"x264_refs_spinbutton")

        self.horizontalLayout_35.addWidget(self.x264_refs_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_35, 0, 2, 1, 1)

        self.horizontalLayout_47 = QHBoxLayout()
        self.horizontalLayout_47.setObjectName(u"horizontalLayout_47")
        self.label_50 = QLabel(self.x264_advanced_groupbox)
        self.label_50.setObjectName(u"label_50")

        self.horizontalLayout_47.addWidget(self.label_50)

        self.x264_me_combobox = QComboBox(self.x264_advanced_groupbox)
        self.x264_me_combobox.setObjectName(u"x264_me_combobox")

        self.horizontalLayout_47.addWidget(self.x264_me_combobox)


        self.gridLayout_2.addLayout(self.horizontalLayout_47, 15, 2, 1, 1)

        self.horizontalLayout_46 = QHBoxLayout()
        self.horizontalLayout_46.setObjectName(u"horizontalLayout_46")
        self.label_49 = QLabel(self.x264_advanced_groupbox)
        self.label_49.setObjectName(u"label_49")

        self.horizontalLayout_46.addWidget(self.label_49)

        self.x264_direct_combobox = QComboBox(self.x264_advanced_groupbox)
        self.x264_direct_combobox.setObjectName(u"x264_direct_combobox")

        self.horizontalLayout_46.addWidget(self.x264_direct_combobox)


        self.gridLayout_2.addLayout(self.horizontalLayout_46, 13, 2, 1, 1)

        self.horizontalLayout_52 = QHBoxLayout()
        self.horizontalLayout_52.setObjectName(u"horizontalLayout_52")
        self.label_55 = QLabel(self.x264_advanced_groupbox)
        self.label_55.setObjectName(u"label_55")

        self.horizontalLayout_52.addWidget(self.label_55)

        self.x264_trellis_combobox = QComboBox(self.x264_advanced_groupbox)
        self.x264_trellis_combobox.setObjectName(u"x264_trellis_combobox")

        self.horizontalLayout_52.addWidget(self.x264_trellis_combobox)


        self.gridLayout_2.addLayout(self.horizontalLayout_52, 12, 2, 1, 1)

        self.horizontalLayout_51 = QHBoxLayout()
        self.horizontalLayout_51.setObjectName(u"horizontalLayout_51")
        self.label_54 = QLabel(self.x264_advanced_groupbox)
        self.label_54.setObjectName(u"label_54")

        self.horizontalLayout_51.addWidget(self.label_54)

        self.x264_psyrd_trellis_spinbutton = QDoubleSpinBox(self.x264_advanced_groupbox)
        self.x264_psyrd_trellis_spinbutton.setObjectName(u"x264_psyrd_trellis_spinbutton")

        self.horizontalLayout_51.addWidget(self.x264_psyrd_trellis_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_51, 11, 2, 1, 1)

        self.horizontalLayout_50 = QHBoxLayout()
        self.horizontalLayout_50.setObjectName(u"horizontalLayout_50")
        self.label_53 = QLabel(self.x264_advanced_groupbox)
        self.label_53.setObjectName(u"label_53")

        self.horizontalLayout_50.addWidget(self.label_53)

        self.x264_psyrd_spinbutton = QDoubleSpinBox(self.x264_advanced_groupbox)
        self.x264_psyrd_spinbutton.setObjectName(u"x264_psyrd_spinbutton")

        self.horizontalLayout_50.addWidget(self.x264_psyrd_spinbutton)


        self.gridLayout_2.addLayout(self.horizontalLayout_50, 10, 2, 1, 1)

        self.x264_8x8dct_checkbox = QCheckBox(self.x264_advanced_groupbox)
        self.x264_8x8dct_checkbox.setObjectName(u"x264_8x8dct_checkbox")
        self.x264_8x8dct_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_2.addWidget(self.x264_8x8dct_checkbox, 9, 2, 1, 1)

        self.frame_7 = QFrame(self.x264_advanced_groupbox)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_26 = QVBoxLayout(self.frame_7)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.horizontalLayout_45 = QHBoxLayout()
        self.horizontalLayout_45.setObjectName(u"horizontalLayout_45")
        self.x264_auto_partitions_radiobutton = QRadioButton(self.frame_7)
        self.x264_auto_partitions_radiobutton.setObjectName(u"x264_auto_partitions_radiobutton")
        sizePolicy3.setHeightForWidth(self.x264_auto_partitions_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_auto_partitions_radiobutton.setSizePolicy(sizePolicy3)
        self.x264_auto_partitions_radiobutton.setLayoutDirection(Qt.LeftToRight)
        self.x264_auto_partitions_radiobutton.setChecked(True)

        self.horizontalLayout_45.addWidget(self.x264_auto_partitions_radiobutton)

        self.x264_custom_partitions_radiobutton = QRadioButton(self.frame_7)
        self.x264_custom_partitions_radiobutton.setObjectName(u"x264_custom_partitions_radiobutton")
        sizePolicy7 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.x264_custom_partitions_radiobutton.sizePolicy().hasHeightForWidth())
        self.x264_custom_partitions_radiobutton.setSizePolicy(sizePolicy7)

        self.horizontalLayout_45.addWidget(self.x264_custom_partitions_radiobutton)


        self.verticalLayout_26.addLayout(self.horizontalLayout_45)

        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.x264_p4x4_checkbox = QCheckBox(self.frame_7)
        self.x264_p4x4_checkbox.setObjectName(u"x264_p4x4_checkbox")
        sizePolicy7.setHeightForWidth(self.x264_p4x4_checkbox.sizePolicy().hasHeightForWidth())
        self.x264_p4x4_checkbox.setSizePolicy(sizePolicy7)
        self.x264_p4x4_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_11.addWidget(self.x264_p4x4_checkbox, 0, 1, 1, 1)

        self.x264_p8x8_checkbox = QCheckBox(self.frame_7)
        self.x264_p8x8_checkbox.setObjectName(u"x264_p8x8_checkbox")
        sizePolicy7.setHeightForWidth(self.x264_p8x8_checkbox.sizePolicy().hasHeightForWidth())
        self.x264_p8x8_checkbox.setSizePolicy(sizePolicy7)
        self.x264_p8x8_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_11.addWidget(self.x264_p8x8_checkbox, 1, 1, 1, 1)

        self.x264_i8x8_checkbox = QCheckBox(self.frame_7)
        self.x264_i8x8_checkbox.setObjectName(u"x264_i8x8_checkbox")
        sizePolicy7.setHeightForWidth(self.x264_i8x8_checkbox.sizePolicy().hasHeightForWidth())
        self.x264_i8x8_checkbox.setSizePolicy(sizePolicy7)
        self.x264_i8x8_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_11.addWidget(self.x264_i8x8_checkbox, 1, 0, 1, 1)

        self.x264_b8x8_checkbox = QCheckBox(self.frame_7)
        self.x264_b8x8_checkbox.setObjectName(u"x264_b8x8_checkbox")
        sizePolicy7.setHeightForWidth(self.x264_b8x8_checkbox.sizePolicy().hasHeightForWidth())
        self.x264_b8x8_checkbox.setSizePolicy(sizePolicy7)
        self.x264_b8x8_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_11.addWidget(self.x264_b8x8_checkbox, 2, 1, 1, 1)

        self.x264_i4x4_checkbox = QCheckBox(self.frame_7)
        self.x264_i4x4_checkbox.setObjectName(u"x264_i4x4_checkbox")
        sizePolicy7.setHeightForWidth(self.x264_i4x4_checkbox.sizePolicy().hasHeightForWidth())
        self.x264_i4x4_checkbox.setSizePolicy(sizePolicy7)
        self.x264_i4x4_checkbox.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout_11.addWidget(self.x264_i4x4_checkbox, 0, 0, 1, 1)

        self.gridLayout_11.setRowStretch(0, 1)
        self.gridLayout_11.setRowStretch(1, 1)

        self.verticalLayout_26.addLayout(self.gridLayout_11)


        self.gridLayout_2.addWidget(self.frame_7, 5, 2, 4, 1)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer_8, 15, 0, 4, 1)


        self.verticalLayout_25.addLayout(self.gridLayout_2)


        self.verticalLayout_24.addWidget(self.x264_advanced_groupbox)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_24.addItem(self.verticalSpacer_7)

        self.video_codec_stack.addWidget(self.x264_page)
        self.page_16 = QWidget()
        self.page_16.setObjectName(u"page_16")
        self.video_codec_stack.addWidget(self.page_16)

        self.verticalLayout_18.addWidget(self.video_codec_stack)

        self.sidebar_toolbox.addItem(self.video_codec, u"Video Codec")
        self.audio_codec = QWidget()
        self.audio_codec.setObjectName(u"audio_codec")
        self.audio_codec.setGeometry(QRect(0, 0, 312, 940))
        self.verticalLayout_19 = QVBoxLayout(self.audio_codec)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.audio_streams_treewidget = QTreeWidget(self.audio_codec)
        self.audio_streams_treewidget.setObjectName(u"audio_streams_treewidget")

        self.verticalLayout_19.addWidget(self.audio_streams_treewidget)

        self.add_audio_stream_toolbutton = QToolButton(self.audio_codec)
        self.add_audio_stream_toolbutton.setObjectName(u"add_audio_stream_toolbutton")
        sizePolicy8 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.add_audio_stream_toolbutton.sizePolicy().hasHeightForWidth())
        self.add_audio_stream_toolbutton.setSizePolicy(sizePolicy8)
        icon = QIcon()
        iconThemeName = u"list-add"
        if QIcon.hasThemeIcon(iconThemeName):
            icon = QIcon.fromTheme(iconThemeName)
        else:
            icon.addFile(u"../../../../../.designer/backup", QSize(), QIcon.Normal, QIcon.Off)
        
        self.add_audio_stream_toolbutton.setIcon(icon)

        self.verticalLayout_19.addWidget(self.add_audio_stream_toolbutton)

        self.sidebar_toolbox.addItem(self.audio_codec, u"Audio Codec")
        self.filters = QWidget()
        self.filters.setObjectName(u"filters")
        self.filters.setGeometry(QRect(0, 0, 312, 940))
        self.sidebar_toolbox.addItem(self.filters, u"Filters")
        self.subtitles = QWidget()
        self.subtitles.setObjectName(u"subtitles")
        self.subtitles.setGeometry(QRect(0, 0, 312, 940))
        self.verticalLayout_20 = QVBoxLayout(self.subtitles)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.subtitle_streams_listwidget = QListWidget(self.subtitles)
        self.subtitle_streams_listwidget.setObjectName(u"subtitle_streams_listwidget")

        self.verticalLayout_20.addWidget(self.subtitle_streams_listwidget)

        self.add_subtitle_stream_toolbutton = QToolButton(self.subtitles)
        self.add_subtitle_stream_toolbutton.setObjectName(u"add_subtitle_stream_toolbutton")
        sizePolicy8.setHeightForWidth(self.add_subtitle_stream_toolbutton.sizePolicy().hasHeightForWidth())
        self.add_subtitle_stream_toolbutton.setSizePolicy(sizePolicy8)
        self.add_subtitle_stream_toolbutton.setIcon(icon)

        self.verticalLayout_20.addWidget(self.add_subtitle_stream_toolbutton)

        self.sidebar_toolbox.addItem(self.subtitles, u"Subtitles")

        self.verticalLayout_2.addWidget(self.sidebar_toolbox)

        self.preview_buttons_hlayout = QHBoxLayout()
        self.preview_buttons_hlayout.setObjectName(u"preview_buttons_hlayout")
        self.preview_buttons_hlayout.setContentsMargins(-1, -1, -1, 6)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.preview_buttons_hlayout.addItem(self.horizontalSpacer)

        self.preview_toolbutton = QToolButton(self.sidebar_frame)
        self.preview_toolbutton.setObjectName(u"preview_toolbutton")
        icon1 = QIcon()
        iconThemeName = u"camera-video"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u"../../../../../.designer/backup/.designer/backup", QSize(), QIcon.Normal, QIcon.Off)
        
        self.preview_toolbutton.setIcon(icon1)

        self.preview_buttons_hlayout.addWidget(self.preview_toolbutton)

        self.crop_toolbutton = QToolButton(self.sidebar_frame)
        self.crop_toolbutton.setObjectName(u"crop_toolbutton")
        icon2 = QIcon()
        iconThemeName = u"zoom-fit-best"
        if QIcon.hasThemeIcon(iconThemeName):
            icon2 = QIcon.fromTheme(iconThemeName)
        else:
            icon2.addFile(u"../../../../../.designer/backup/.designer/backup", QSize(), QIcon.Normal, QIcon.Off)
        
        self.crop_toolbutton.setIcon(icon2)

        self.preview_buttons_hlayout.addWidget(self.crop_toolbutton)

        self.trim_toolbutton = QToolButton(self.sidebar_frame)
        self.trim_toolbutton.setObjectName(u"trim_toolbutton")
        icon3 = QIcon()
        iconThemeName = u"edit-cut"
        if QIcon.hasThemeIcon(iconThemeName):
            icon3 = QIcon.fromTheme(iconThemeName)
        else:
            icon3.addFile(u"../../../../../.designer/backup/.designer/backup", QSize(), QIcon.Normal, QIcon.Off)
        
        self.trim_toolbutton.setIcon(icon3)

        self.preview_buttons_hlayout.addWidget(self.trim_toolbutton)

        self.benchmark_toolbutton = QToolButton(self.sidebar_frame)
        self.benchmark_toolbutton.setObjectName(u"benchmark_toolbutton")
        icon4 = QIcon()
        iconThemeName = u"system-run"
        if QIcon.hasThemeIcon(iconThemeName):
            icon4 = QIcon.fromTheme(iconThemeName)
        else:
            icon4.addFile(u"../../../../../.designer/backup/.designer/backup", QSize(), QIcon.Normal, QIcon.Off)
        
        self.benchmark_toolbutton.setIcon(icon4)
        self.benchmark_toolbutton.setCheckable(False)
        self.benchmark_toolbutton.setChecked(False)

        self.preview_buttons_hlayout.addWidget(self.benchmark_toolbutton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.preview_buttons_hlayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.preview_buttons_hlayout)

        self.sidebar_splitter.addWidget(self.sidebar_frame)

        self.gridLayout_12.addWidget(self.sidebar_splitter, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 29))
        self.file_menu = QMenu(self.menubar)
        self.file_menu.setObjectName(u"file_menu")
        self.edit_menu = QMenu(self.menubar)
        self.edit_menu.setObjectName(u"edit_menu")
        self.help_menu = QMenu(self.menubar)
        self.help_menu.setObjectName(u"help_menu")
        self.encoding_menu = QMenu(self.menubar)
        self.encoding_menu.setObjectName(u"encoding_menu")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.file_menu.menuAction())
        self.menubar.addAction(self.edit_menu.menuAction())
        self.menubar.addAction(self.encoding_menu.menuAction())
        self.menubar.addAction(self.help_menu.menuAction())
        self.file_menu.addAction(self.add_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.quit_action)
        self.edit_menu.addAction(self.remove_action)
        self.edit_menu.addAction(self.remove_all_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.preferences_action)
        self.help_menu.addAction(self.about_render_watch_action)
        self.encoding_menu.addAction(self.standard_action)
        self.encoding_menu.addAction(self.multi_task_action)

        self.retranslateUi(MainWindow)
        self.x264_crf_slider.valueChanged.connect(self.x264_crf_value_label.setNum)

        self.preview_stack.setCurrentIndex(0)
        self.preview_state_stack.setCurrentIndex(2)
        self.crop_preview_stack.setCurrentIndex(1)
        self.trim_preview_stack.setCurrentIndex(1)
        self.benchmark_stack.setCurrentIndex(1)
        self.sidebar_toolbox.setCurrentIndex(0)
        self.x264_rate_type_stack.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Render Watch", None))
        self.about_render_watch_action.setText(QCoreApplication.translate("MainWindow", u"About Render Watch", None))
        self.add_action.setText(QCoreApplication.translate("MainWindow", u"Add...", None))
        self.quit_action.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
        self.remove_action.setText(QCoreApplication.translate("MainWindow", u"Remove", None))
        self.remove_all_action.setText(QCoreApplication.translate("MainWindow", u"Remove All", None))
        self.preferences_action.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.standard_action.setText(QCoreApplication.translate("MainWindow", u"Standard", None))
        self.multi_task_action.setText(QCoreApplication.translate("MainWindow", u"Multi-Task", None))
        self.actionHost.setText(QCoreApplication.translate("MainWindow", u"Host", None))
        self.actionClient.setText(QCoreApplication.translate("MainWindow", u"Client", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Getting preview ready...", None))
        self.label_56.setText(QCoreApplication.translate("MainWindow", u"Source:", None))
        self.preview_source_combobox.setItemText(0, QCoreApplication.translate("MainWindow", u"Output", None))
        self.preview_source_combobox.setItemText(1, QCoreApplication.translate("MainWindow", u"Original", None))

        self.label_2.setText(QCoreApplication.translate("MainWindow", u"PREVIEW", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Preview not available", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"--:--:--.-", None))
        self.preview_live_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Live", None))
        self.preview_5s_radiobutton.setText(QCoreApplication.translate("MainWindow", u"5s", None))
        self.preview_10s_radiobutton.setText(QCoreApplication.translate("MainWindow", u"10s", None))
        self.preview_20s_radiobutton.setText(QCoreApplication.translate("MainWindow", u"20s", None))
        self.preview_30s_radiobutton.setText(QCoreApplication.translate("MainWindow", u"30s", None))
        self.crop_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Width:", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Height:", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"X:", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Y:", None))
        self.crop_auto_checkbox.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Scale", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Width:", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Height:", None))
        self.crop_preview_label.setText(QCoreApplication.translate("MainWindow", u"PREVIEW", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Crop not available", None))
        self.trim_preview_label.setText(QCoreApplication.translate("MainWindow", u"PREVIEW", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"Trim not available", None))
        self.trim_start_label.setText(QCoreApplication.translate("MainWindow", u"00:00:00.00", None))
        self.trim_end_label.setText(QCoreApplication.translate("MainWindow", u"--:--:--.-", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Avg. Bitrate:", None))
        self.benchmark_avg_bitrate_label.setText(QCoreApplication.translate("MainWindow", u"#####.#kbps", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Speed:", None))
        self.benchmark_speed_label.setText(QCoreApplication.translate("MainWindow", u"###.#x", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Est. File Size:", None))
        self.benchmark_file_size_label.setText(QCoreApplication.translate("MainWindow", u"###.#MB", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Est. Encode Time:", None))
        self.benchmark_est_encode_time_label.setText(QCoreApplication.translate("MainWindow", u"##:##:##.#", None))
        self.benchmark_short_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Short", None))
        self.benchmark_long_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Long", None))
        self.benchmark_multitask_checkbox.setText(QCoreApplication.translate("MainWindow", u"Multi-Task", None))
        self.benchmark_start_stop_pushbutton.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"Benchmark not available", None))
        ___qtreewidgetitem = self.inputs_treewidget.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Description", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"#", None));
        ___qtreewidgetitem1 = self.treeWidget_2.headerItem()
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Description", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));
        self.sidebar_toolbox.setItemText(self.sidebar_toolbox.indexOf(self.presets), QCoreApplication.translate("MainWindow", u"Presets", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Container:", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"Frame Rate:", None))
        self.sidebar_toolbox.setItemText(self.sidebar_toolbox.indexOf(self.general), QCoreApplication.translate("MainWindow", u"General", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"Video Stream:", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"Video Codec:", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"Preset:", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"Profile:", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"Tune:", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"Level:", None))
        self.x264_crf_radiobutton.setText(QCoreApplication.translate("MainWindow", u"CRF", None))
        self.x264_qp_radiobutton.setText(QCoreApplication.translate("MainWindow", u"QP", None))
        self.x264_bitrate_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Bitrate", None))
        self.x264_crf_label.setText(QCoreApplication.translate("MainWindow", u"CRF:", None))
        self.x264_crf_value_label.setText(QCoreApplication.translate("MainWindow", u"23", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"Bitrate:", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"Max Bitrate:", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"Min Bitrate:", None))
        self.x264_average_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Average", None))
        self.x264_constant_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Constant", None))
        self.x264_2pass_radiobutton.setText(QCoreApplication.translate("MainWindow", u"2-Pass", None))
        self.x264_advanced_groupbox.setTitle(QCoreApplication.translate("MainWindow", u"Advanced", None))
        self.x264_no_fast_p_skip_checkbox.setText(QCoreApplication.translate("MainWindow", u"No Fast P Skip", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Deblock", None))
        self.label_44.setText(QCoreApplication.translate("MainWindow", u"Alpha:", None))
        self.label_45.setText(QCoreApplication.translate("MainWindow", u"Beta:", None))
        self.x264_mixed_refs_checkbox.setText(QCoreApplication.translate("MainWindow", u"Mixed Refs.", None))
        self.label_39.setText(QCoreApplication.translate("MainWindow", u"B Pyramid:", None))
        self.x264_no_dct_decimate_checkbox.setText(QCoreApplication.translate("MainWindow", u"No DCT Decimate", None))
        self.label_37.setText(QCoreApplication.translate("MainWindow", u"B Frames:", None))
        self.label_41.setText(QCoreApplication.translate("MainWindow", u"Min Keyint:", None))
        self.label_52.setText(QCoreApplication.translate("MainWindow", u"Sub ME:", None))
        self.label_46.setText(QCoreApplication.translate("MainWindow", u"AQ Mode:", None))
        self.label_47.setText(QCoreApplication.translate("MainWindow", u"AQ Strength:", None))
        self.label_51.setText(QCoreApplication.translate("MainWindow", u"ME Range:", None))
        self.label_40.setText(QCoreApplication.translate("MainWindow", u"Keyint:", None))
        self.x264_weight_p_checkbox.setText(QCoreApplication.translate("MainWindow", u"Weight P", None))
        self.label_43.setText(QCoreApplication.translate("MainWindow", u"B Adapt:", None))
        self.x264_weight_b_checkbox.setText(QCoreApplication.translate("MainWindow", u"Weight B", None))
        self.x264_no_cabac_checkbox.setText(QCoreApplication.translate("MainWindow", u"No CABAC", None))
        self.label_48.setText(QCoreApplication.translate("MainWindow", u"Partitions:", None))
        self.label_42.setText(QCoreApplication.translate("MainWindow", u"Scenecut:", None))
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"Ref Frames:", None))
        self.label_50.setText(QCoreApplication.translate("MainWindow", u"ME:", None))
        self.label_49.setText(QCoreApplication.translate("MainWindow", u"Direct:", None))
        self.label_55.setText(QCoreApplication.translate("MainWindow", u"Trellis:", None))
        self.label_54.setText(QCoreApplication.translate("MainWindow", u"Psyrd Trellis:", None))
        self.label_53.setText(QCoreApplication.translate("MainWindow", u"Psyrd:", None))
        self.x264_8x8dct_checkbox.setText(QCoreApplication.translate("MainWindow", u"8x8dct", None))
        self.x264_auto_partitions_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Auto", None))
        self.x264_custom_partitions_radiobutton.setText(QCoreApplication.translate("MainWindow", u"Custom", None))
        self.x264_p4x4_checkbox.setText(QCoreApplication.translate("MainWindow", u"p4x4", None))
        self.x264_p8x8_checkbox.setText(QCoreApplication.translate("MainWindow", u"p8x8", None))
        self.x264_i8x8_checkbox.setText(QCoreApplication.translate("MainWindow", u"i8x8", None))
        self.x264_b8x8_checkbox.setText(QCoreApplication.translate("MainWindow", u"b8x8", None))
        self.x264_i4x4_checkbox.setText(QCoreApplication.translate("MainWindow", u"i4x4", None))
        self.sidebar_toolbox.setItemText(self.sidebar_toolbox.indexOf(self.video_codec), QCoreApplication.translate("MainWindow", u"Video Codec", None))
        ___qtreewidgetitem2 = self.audio_streams_treewidget.headerItem()
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("MainWindow", u"Codec", None));
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Stream", None));
        self.add_audio_stream_toolbutton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.sidebar_toolbox.setItemText(self.sidebar_toolbox.indexOf(self.audio_codec), QCoreApplication.translate("MainWindow", u"Audio Codec", None))
        self.sidebar_toolbox.setItemText(self.sidebar_toolbox.indexOf(self.filters), QCoreApplication.translate("MainWindow", u"Filters", None))
        self.add_subtitle_stream_toolbutton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.sidebar_toolbox.setItemText(self.sidebar_toolbox.indexOf(self.subtitles), QCoreApplication.translate("MainWindow", u"Subtitles", None))
        self.preview_toolbutton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.crop_toolbutton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.trim_toolbutton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.benchmark_toolbutton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.file_menu.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.edit_menu.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.help_menu.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.encoding_menu.setTitle(QCoreApplication.translate("MainWindow", u"Encoding", None))
    # retranslateUi

