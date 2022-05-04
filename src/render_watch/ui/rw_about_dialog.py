# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'rw_about_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.setWindowModality(Qt.ApplicationModal)
        AboutDialog.resize(480, 420)
        icon = QIcon()
        icon.addFile(u"rw_64.png", QSize(), QIcon.Normal, QIcon.Off)
        AboutDialog.setWindowIcon(icon)
        AboutDialog.setModal(True)
        self.verticalLayout_2 = QVBoxLayout(AboutDialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.logo_label = QLabel(AboutDialog)
        self.logo_label.setObjectName(u"logo_label")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.logo_label.sizePolicy().hasHeightForWidth())
        self.logo_label.setSizePolicy(sizePolicy)
        self.logo_label.setMinimumSize(QSize(0, 0))
        self.logo_label.setScaledContents(False)
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.logo_label)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(AboutDialog)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.verticalLayout.addWidget(self.label_2)

        self.label_3 = QLabel(AboutDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.verticalLayout.addWidget(self.label_3)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.frame = QFrame(AboutDialog)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setAlignment(Qt.AlignCenter)
        self.label_4.setWordWrap(True)

        self.verticalLayout_3.addWidget(self.label_4)

        self.verticalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)
        self.label_5.setTextFormat(Qt.RichText)
        self.label_5.setAlignment(Qt.AlignCenter)
        self.label_5.setWordWrap(True)
        self.label_5.setOpenExternalLinks(True)
        self.label_5.setTextInteractionFlags(Qt.TextBrowserInteraction)

        self.verticalLayout_3.addWidget(self.label_5)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setOpenExternalLinks(True)
        self.label.setTextInteractionFlags(Qt.TextBrowserInteraction)

        self.verticalLayout_3.addWidget(self.label)


        self.verticalLayout_2.addWidget(self.frame)

        self.buttonBox = QDialogButtonBox(AboutDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(AboutDialog)
        self.buttonBox.accepted.connect(AboutDialog.accept)
        self.buttonBox.rejected.connect(AboutDialog.reject)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"Dialog", None))
        self.logo_label.setText(QCoreApplication.translate("AboutDialog", u"LOGO", None))
        self.label_2.setText(QCoreApplication.translate("AboutDialog", u"Render Watch", None))
        self.label_3.setText(QCoreApplication.translate("AboutDialog", u"Version 0.3.0-beta", None))
        self.label_4.setText(QCoreApplication.translate("AboutDialog", u"An open source video transcoder for Linux. WAHT", None))
        self.label_5.setText(QCoreApplication.translate("AboutDialog", u"<a href=\"https://github.com/mgregory1994/RenderWatch/\">https://github.com/mgregory1994/RenderWatch</a>", None))
        self.label.setText(QCoreApplication.translate("AboutDialog", u"<a href=\"https://www.gnu.org/licenses/gpl-3.0.en.html\">GPLV3</a>", None))
    # retranslateUi

