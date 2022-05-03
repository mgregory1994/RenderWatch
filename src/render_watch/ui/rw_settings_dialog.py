# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rw_settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.2.3
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QScrollArea, QSizePolicy, QSpacerItem, QSpinBox,
    QTabWidget, QToolButton, QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.setWindowModality(Qt.ApplicationModal)
        SettingsDialog.resize(640, 580)
        icon = QIcon()
        icon.addFile(u"rw_64.png", QSize(), QIcon.Normal, QIcon.Off)
        SettingsDialog.setWindowIcon(icon)
        SettingsDialog.setModal(True)
        self.verticalLayout = QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(SettingsDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.general = QWidget()
        self.general.setObjectName(u"general")
        self.gridLayout_2 = QGridLayout(self.general)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.scrollArea = QScrollArea(self.general)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShadow(QFrame.Plain)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 616, 488))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(16)
        self.label.setFont(font)

        self.verticalLayout_2.addWidget(self.label)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(12, -1, -1, -1)
        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.output_dir_line_edit = QLineEdit(self.scrollAreaWidgetContents)
        self.output_dir_line_edit.setObjectName(u"output_dir_line_edit")
        self.output_dir_line_edit.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.output_dir_line_edit)

        self.output_dir_chooser_button = QToolButton(self.scrollAreaWidgetContents)
        self.output_dir_chooser_button.setObjectName(u"output_dir_chooser_button")
        icon1 = QIcon()
        iconThemeName = u"document-open"
        if QIcon.hasThemeIcon(iconThemeName):
            icon1 = QIcon.fromTheme(iconThemeName)
        else:
            icon1.addFile(u".", QSize(), QIcon.Normal, QIcon.Off)
        
        self.output_dir_chooser_button.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.output_dir_chooser_button)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)


        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer, 2, 0, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.temp_dir_line_edit = QLineEdit(self.scrollAreaWidgetContents)
        self.temp_dir_line_edit.setObjectName(u"temp_dir_line_edit")

        self.horizontalLayout.addWidget(self.temp_dir_line_edit)

        self.temp_dir_chooser_button = QToolButton(self.scrollAreaWidgetContents)
        self.temp_dir_chooser_button.setObjectName(u"temp_dir_chooser_button")
        self.temp_dir_chooser_button.setIcon(icon1)

        self.horizontalLayout.addWidget(self.temp_dir_chooser_button)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)

        self.overwrite_existing_outputs_checkbox = QCheckBox(self.scrollAreaWidgetContents)
        self.overwrite_existing_outputs_checkbox.setObjectName(u"overwrite_existing_outputs_checkbox")

        self.gridLayout.addWidget(self.overwrite_existing_outputs_checkbox, 1, 1, 1, 1)

        self.clear_temp_dir_checkbox = QCheckBox(self.scrollAreaWidgetContents)
        self.clear_temp_dir_checkbox.setObjectName(u"clear_temp_dir_checkbox")

        self.gridLayout.addWidget(self.clear_temp_dir_checkbox, 4, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_2, 5, 0, 1, 2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_3, 7, 0, 1, 2)

        self.dark_theme_checkbox = QCheckBox(self.scrollAreaWidgetContents)
        self.dark_theme_checkbox.setObjectName(u"dark_theme_checkbox")
        self.dark_theme_checkbox.setLayoutDirection(Qt.LeftToRight)
        self.dark_theme_checkbox.setChecked(True)

        self.gridLayout.addWidget(self.dark_theme_checkbox, 6, 0, 1, 2)


        self.verticalLayout_2.addLayout(self.gridLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_2.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.tabWidget.addTab(self.general, "")
        self.encoding = QWidget()
        self.encoding.setObjectName(u"encoding")
        self.gridLayout_4 = QGridLayout(self.encoding)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_2 = QScrollArea(self.encoding)
        self.scrollArea_2.setObjectName(u"scrollArea_2")
        self.scrollArea_2.setFrameShadow(QFrame.Plain)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 616, 488))
        self.verticalLayout_3 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_6 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setFont(font)

        self.verticalLayout_3.addWidget(self.label_6)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(12, -1, -1, -1)
        self.label_4 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_4.addWidget(self.label_4)

        self.per_codec_list = QListWidget(self.scrollAreaWidgetContents_2)
        self.per_codec_list.setObjectName(u"per_codec_list")

        self.verticalLayout_4.addWidget(self.per_codec_list)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_4.addItem(self.verticalSpacer_4)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.parallel_nvenc_checkbox = QCheckBox(self.scrollAreaWidgetContents_2)
        self.parallel_nvenc_checkbox.setObjectName(u"parallel_nvenc_checkbox")
        self.parallel_nvenc_checkbox.setLayoutDirection(Qt.LeftToRight)
        self.parallel_nvenc_checkbox.setChecked(True)

        self.gridLayout_3.addWidget(self.parallel_nvenc_checkbox, 0, 0, 1, 1)

        self.label_5 = QLabel(self.scrollAreaWidgetContents_2)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setLayoutDirection(Qt.LeftToRight)
        self.label_5.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.parallel_nvenc_tasks_spinbutton = QSpinBox(self.scrollAreaWidgetContents_2)
        self.parallel_nvenc_tasks_spinbutton.setObjectName(u"parallel_nvenc_tasks_spinbutton")
        self.parallel_nvenc_tasks_spinbutton.setMinimum(2)
        self.parallel_nvenc_tasks_spinbutton.setMaximum(8)

        self.horizontalLayout_3.addWidget(self.parallel_nvenc_tasks_spinbutton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.gridLayout_3.addLayout(self.horizontalLayout_3, 1, 1, 1, 1)


        self.verticalLayout_4.addLayout(self.gridLayout_3)


        self.verticalLayout_3.addLayout(self.verticalLayout_4)

        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)

        self.gridLayout_4.addWidget(self.scrollArea_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.encoding, "")
        self.watch_folder = QWidget()
        self.watch_folder.setObjectName(u"watch_folder")
        self.gridLayout_7 = QGridLayout(self.watch_folder)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(0, 0, 0, 0)
        self.scrollArea_3 = QScrollArea(self.watch_folder)
        self.scrollArea_3.setObjectName(u"scrollArea_3")
        self.scrollArea_3.setFrameShadow(QFrame.Plain)
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QWidget()
        self.scrollAreaWidgetContents_3.setObjectName(u"scrollAreaWidgetContents_3")
        self.scrollAreaWidgetContents_3.setGeometry(QRect(0, 0, 616, 488))
        self.gridLayout_6 = QGridLayout(self.scrollAreaWidgetContents_3)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_7 = QLabel(self.scrollAreaWidgetContents_3)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)

        self.verticalLayout_5.addWidget(self.label_7)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(12, -1, -1, -1)
        self.parallel_watch_folders_checkbox = QCheckBox(self.scrollAreaWidgetContents_3)
        self.parallel_watch_folders_checkbox.setObjectName(u"parallel_watch_folders_checkbox")

        self.gridLayout_5.addWidget(self.parallel_watch_folders_checkbox, 0, 0, 1, 1)

        self.move_watch_folder_tasks_to_done_checkbox = QCheckBox(self.scrollAreaWidgetContents_3)
        self.move_watch_folder_tasks_to_done_checkbox.setObjectName(u"move_watch_folder_tasks_to_done_checkbox")
        self.move_watch_folder_tasks_to_done_checkbox.setChecked(True)

        self.gridLayout_5.addWidget(self.move_watch_folder_tasks_to_done_checkbox, 1, 0, 1, 1)

        self.watch_folder_wait_for_tasks_checkbox = QCheckBox(self.scrollAreaWidgetContents_3)
        self.watch_folder_wait_for_tasks_checkbox.setObjectName(u"watch_folder_wait_for_tasks_checkbox")
        self.watch_folder_wait_for_tasks_checkbox.setChecked(True)

        self.gridLayout_5.addWidget(self.watch_folder_wait_for_tasks_checkbox, 2, 0, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_5)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_5)


        self.gridLayout_6.addLayout(self.verticalLayout_5, 0, 0, 1, 1)

        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)

        self.gridLayout_7.addWidget(self.scrollArea_3, 0, 0, 1, 1)

        self.tabWidget.addTab(self.watch_folder, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.settings_dialog_buttonbox = QDialogButtonBox(SettingsDialog)
        self.settings_dialog_buttonbox.setObjectName(u"settings_dialog_buttonbox")
        self.settings_dialog_buttonbox.setOrientation(Qt.Horizontal)
        self.settings_dialog_buttonbox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.verticalLayout.addWidget(self.settings_dialog_buttonbox)


        self.retranslateUi(SettingsDialog)
        self.settings_dialog_buttonbox.accepted.connect(SettingsDialog.accept)
        self.settings_dialog_buttonbox.rejected.connect(SettingsDialog.reject)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Render Watch Settings", None))
        self.label.setText(QCoreApplication.translate("SettingsDialog", u"General", None))
        self.label_3.setText(QCoreApplication.translate("SettingsDialog", u"Temp. Directory:", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Output Directory:", None))
        self.output_dir_chooser_button.setText(QCoreApplication.translate("SettingsDialog", u"...", None))
        self.temp_dir_chooser_button.setText(QCoreApplication.translate("SettingsDialog", u"...", None))
        self.overwrite_existing_outputs_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Overwrite Existing Output Files", None))
        self.clear_temp_dir_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Clear Temp. Directory When Closing", None))
        self.dark_theme_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Dark Theme", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.general), QCoreApplication.translate("SettingsDialog", u"General", None))
        self.label_6.setText(QCoreApplication.translate("SettingsDialog", u"Encoding", None))
        self.label_4.setText(QCoreApplication.translate("SettingsDialog", u"Parallel Encoding:", None))
        self.parallel_nvenc_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Parallel NVENC Encoding", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"Parallel NVENC Tasks:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.encoding), QCoreApplication.translate("SettingsDialog", u"Encoding", None))
        self.label_7.setText(QCoreApplication.translate("SettingsDialog", u"Watch Folder", None))
        self.parallel_watch_folders_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Run Watch Folders in Parallel", None))
        self.move_watch_folder_tasks_to_done_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Move Finished Inputs to a Done Folder", None))
        self.watch_folder_wait_for_tasks_checkbox.setText(QCoreApplication.translate("SettingsDialog", u"Wait For Other Running Tasks", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.watch_folder), QCoreApplication.translate("SettingsDialog", u"Watch Folder", None))
    # retranslateUi

