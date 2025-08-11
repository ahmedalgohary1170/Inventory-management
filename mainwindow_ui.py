# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QStackedWidget,
    QStatusBar, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 820)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setLayoutDirection(Qt.RightToLeft)
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sidebar = QFrame(self.centralwidget)
        self.sidebar.setObjectName(u"sidebar")
        self.sidebar.setMinimumSize(QSize(240, 0))
        self.sidebar.setMaximumSize(QSize(280, 16777215))
        self.verticalLayout_sidebar = QVBoxLayout(self.sidebar)
        self.verticalLayout_sidebar.setObjectName(u"verticalLayout_sidebar")
        self.logoLabel = QLabel(self.sidebar)
        self.logoLabel.setObjectName(u"logoLabel")
        self.logoLabel.setAlignment(Qt.AlignCenter)
        self.logoLabel.setMinimumSize(QSize(0, 84))

        self.verticalLayout_sidebar.addWidget(self.logoLabel)

        self.btn_dashboard = QPushButton(self.sidebar)
        self.btn_dashboard.setObjectName(u"btn_dashboard")

        self.verticalLayout_sidebar.addWidget(self.btn_dashboard)

        self.btn_inventory = QPushButton(self.sidebar)
        self.btn_inventory.setObjectName(u"btn_inventory")

        self.verticalLayout_sidebar.addWidget(self.btn_inventory)

        self.btn_customers = QPushButton(self.sidebar)
        self.btn_customers.setObjectName(u"btn_customers")

        self.verticalLayout_sidebar.addWidget(self.btn_customers)

        self.btn_invoices = QPushButton(self.sidebar)
        self.btn_invoices.setObjectName(u"btn_invoices")

        self.verticalLayout_sidebar.addWidget(self.btn_invoices)

        self.btn_reports = QPushButton(self.sidebar)
        self.btn_reports.setObjectName(u"btn_reports")

        self.verticalLayout_sidebar.addWidget(self.btn_reports)

        self.btn_settings = QPushButton(self.sidebar)
        self.btn_settings.setObjectName(u"btn_settings")

        self.verticalLayout_sidebar.addWidget(self.btn_settings)

        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_sidebar.addItem(self.verticalSpacer)

        self.btn_logout = QPushButton(self.sidebar)
        self.btn_logout.setObjectName(u"btn_logout")

        self.verticalLayout_sidebar.addWidget(self.btn_logout)


        self.horizontalLayout.addWidget(self.sidebar)

        self.mainArea = QWidget(self.centralwidget)
        self.mainArea.setObjectName(u"mainArea")
        self.verticalLayout_main = QVBoxLayout(self.mainArea)
        self.verticalLayout_main.setObjectName(u"verticalLayout_main")
        self.verticalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.headerFrame = QFrame(self.mainArea)
        self.headerFrame.setObjectName(u"headerFrame")
        self.headerFrame.setMinimumSize(QSize(0, 72))
        self.horizontalLayout_header = QHBoxLayout(self.headerFrame)
        self.horizontalLayout_header.setObjectName(u"horizontalLayout_header")
        self.titleLabel = QLabel(self.headerFrame)
        self.titleLabel.setObjectName(u"titleLabel")

        self.horizontalLayout_header.addWidget(self.titleLabel)

        self.spacer_header = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_header.addItem(self.spacer_header)


        self.verticalLayout_main.addWidget(self.headerFrame)

        self.stacked_widget = QStackedWidget(self.mainArea)
        self.stacked_widget.setObjectName(u"stacked_widget")
        self.page_dashboard = QWidget()
        self.page_dashboard.setObjectName(u"page_dashboard")
        self.v_dashboard = QVBoxLayout(self.page_dashboard)
        self.v_dashboard.setObjectName(u"v_dashboard")
        self.cardsArea = QWidget(self.page_dashboard)
        self.cardsArea.setObjectName(u"cardsArea")
        self.h_cards = QHBoxLayout(self.cardsArea)
        self.h_cards.setObjectName(u"h_cards")
        self.h_cards.setContentsMargins(0, 0, 0, 0)

        self.v_dashboard.addWidget(self.cardsArea)

        self.alertsFrame = QFrame(self.page_dashboard)
        self.alertsFrame.setObjectName(u"alertsFrame")
        self.alertsFrame.setMinimumSize(QSize(0, 260))
        self.v_alerts_layout = QVBoxLayout(self.alertsFrame)
        self.v_alerts_layout.setObjectName(u"v_alerts_layout")
        self.alertsTitle = QLabel(self.alertsFrame)
        self.alertsTitle.setObjectName(u"alertsTitle")

        self.v_alerts_layout.addWidget(self.alertsTitle)

        self.table_alerts = QTableWidget(self.alertsFrame)
        self.table_alerts.setObjectName(u"table_alerts")

        self.v_alerts_layout.addWidget(self.table_alerts)


        self.v_dashboard.addWidget(self.alertsFrame)

        self.stacked_widget.addWidget(self.page_dashboard)
        self.page_inventory = QWidget()
        self.page_inventory.setObjectName(u"page_inventory")
        self.v_inventory = QVBoxLayout(self.page_inventory)
        self.v_inventory.setObjectName(u"v_inventory")
        self.invHeader = QFrame(self.page_inventory)
        self.invHeader.setObjectName(u"invHeader")
        self.h_inv_hdr = QHBoxLayout(self.invHeader)
        self.h_inv_hdr.setObjectName(u"h_inv_hdr")
        self.btn_add_inventory = QPushButton(self.invHeader)
        self.btn_add_inventory.setObjectName(u"btn_add_inventory")

        self.h_inv_hdr.addWidget(self.btn_add_inventory)

        self.search_inventory = QLineEdit(self.invHeader)
        self.search_inventory.setObjectName(u"search_inventory")

        self.h_inv_hdr.addWidget(self.search_inventory)

        self.spacer_inv = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.h_inv_hdr.addItem(self.spacer_inv)


        self.v_inventory.addWidget(self.invHeader)

        self.table_inventory = QTableWidget(self.page_inventory)
        self.table_inventory.setObjectName(u"table_inventory")

        self.v_inventory.addWidget(self.table_inventory)

        self.stacked_widget.addWidget(self.page_inventory)
        self.page_customers = QWidget()
        self.page_customers.setObjectName(u"page_customers")
        self.v_customers = QVBoxLayout(self.page_customers)
        self.v_customers.setObjectName(u"v_customers")
        self.custHeader = QFrame(self.page_customers)
        self.custHeader.setObjectName(u"custHeader")
        self.h_cust_hdr = QHBoxLayout(self.custHeader)
        self.h_cust_hdr.setObjectName(u"h_cust_hdr")
        self.btn_add_customer = QPushButton(self.custHeader)
        self.btn_add_customer.setObjectName(u"btn_add_customer")

        self.h_cust_hdr.addWidget(self.btn_add_customer)

        self.search_customers = QLineEdit(self.custHeader)
        self.search_customers.setObjectName(u"search_customers")

        self.h_cust_hdr.addWidget(self.search_customers)

        self.spacer_cust = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.h_cust_hdr.addItem(self.spacer_cust)


        self.v_customers.addWidget(self.custHeader)

        self.table_customers = QTableWidget(self.page_customers)
        self.table_customers.setObjectName(u"table_customers")

        self.v_customers.addWidget(self.table_customers)

        self.stacked_widget.addWidget(self.page_customers)
        self.page_invoices = QWidget()
        self.page_invoices.setObjectName(u"page_invoices")
        self.v_invoices = QVBoxLayout(self.page_invoices)
        self.v_invoices.setObjectName(u"v_invoices")
        self.invHeader2 = QFrame(self.page_invoices)
        self.invHeader2.setObjectName(u"invHeader2")
        self.h_inv2_hdr = QHBoxLayout(self.invHeader2)
        self.h_inv2_hdr.setObjectName(u"h_inv2_hdr")
        self.btn_add_invoice = QPushButton(self.invHeader2)
        self.btn_add_invoice.setObjectName(u"btn_add_invoice")

        self.h_inv2_hdr.addWidget(self.btn_add_invoice)

        self.search_invoices = QLineEdit(self.invHeader2)
        self.search_invoices.setObjectName(u"search_invoices")

        self.h_inv2_hdr.addWidget(self.search_invoices)

        self.spacer_inv2 = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.h_inv2_hdr.addItem(self.spacer_inv2)


        self.v_invoices.addWidget(self.invHeader2)

        self.table_invoices = QTableWidget(self.page_invoices)
        self.table_invoices.setObjectName(u"table_invoices")

        self.v_invoices.addWidget(self.table_invoices)

        self.invoice_panel = QFrame(self.page_invoices)
        self.invoice_panel.setObjectName(u"invoice_panel")
        self.v_invoice_panel = QVBoxLayout(self.invoice_panel)
        self.v_invoice_panel.setObjectName(u"v_invoice_panel")

        self.v_invoices.addWidget(self.invoice_panel)

        self.stacked_widget.addWidget(self.page_invoices)
        self.page_reports = QWidget()
        self.page_reports.setObjectName(u"page_reports")
        self.v_reports = QVBoxLayout(self.page_reports)
        self.v_reports.setObjectName(u"v_reports")
        self.reportsHeader = QFrame(self.page_reports)
        self.reportsHeader.setObjectName(u"reportsHeader")
        self.h_reports_hdr = QHBoxLayout(self.reportsHeader)
        self.h_reports_hdr.setObjectName(u"h_reports_hdr")
        self.reportsLabel = QLabel(self.reportsHeader)
        self.reportsLabel.setObjectName(u"reportsLabel")

        self.h_reports_hdr.addWidget(self.reportsLabel)

        self.btn_export_reports = QPushButton(self.reportsHeader)
        self.btn_export_reports.setObjectName(u"btn_export_reports")

        self.h_reports_hdr.addWidget(self.btn_export_reports)

        self.spacer_reports = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.h_reports_hdr.addItem(self.spacer_reports)


        self.v_reports.addWidget(self.reportsHeader)

        self.reportsArea = QFrame(self.page_reports)
        self.reportsArea.setObjectName(u"reportsArea")
        self.h_reports_area = QHBoxLayout(self.reportsArea)
        self.h_reports_area.setObjectName(u"h_reports_area")
        self.chartArea = QWidget(self.reportsArea)
        self.chartArea.setObjectName(u"chartArea")
        self.v_chart = QVBoxLayout(self.chartArea)
        self.v_chart.setObjectName(u"v_chart")
        self.v_chart.setContentsMargins(0, 0, 0, 0)

        self.h_reports_area.addWidget(self.chartArea)

        self.table_reports = QTableWidget(self.reportsArea)
        self.table_reports.setObjectName(u"table_reports")

        self.h_reports_area.addWidget(self.table_reports)


        self.v_reports.addWidget(self.reportsArea)

        self.stacked_widget.addWidget(self.page_reports)
        self.page_settings = QWidget()
        self.page_settings.setObjectName(u"page_settings")
        self.v_settings = QVBoxLayout(self.page_settings)
        self.v_settings.setObjectName(u"v_settings")
        self.settingsHeader = QFrame(self.page_settings)
        self.settingsHeader.setObjectName(u"settingsHeader")
        self.h_settings_hdr = QHBoxLayout(self.settingsHeader)
        self.h_settings_hdr.setObjectName(u"h_settings_hdr")
        self.settingsLabel = QLabel(self.settingsHeader)
        self.settingsLabel.setObjectName(u"settingsLabel")
        self.settingsLabel.setStyleSheet(u"font-size: 18px; font-weight: bold;")

        self.h_settings_hdr.addWidget(self.settingsLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.h_settings_hdr.addItem(self.horizontalSpacer)


        self.v_settings.addWidget(self.settingsHeader)

        self.scrollArea = QScrollArea(self.page_settings)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 1016, 687))
        self.verticalLayout_scroll = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_scroll.setSpacing(20)
        self.verticalLayout_scroll.setObjectName(u"verticalLayout_scroll")
        self.appearanceGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.appearanceGroup.setObjectName(u"appearanceGroup")
        self.form_appearance = QFormLayout(self.appearanceGroup)
        self.form_appearance.setObjectName(u"form_appearance")
        self.horizontalLayout_theme = QHBoxLayout()
        self.horizontalLayout_theme.setObjectName(u"horizontalLayout_theme")
        self.lbl_theme = QLabel(self.appearanceGroup)
        self.lbl_theme.setObjectName(u"lbl_theme")

        self.horizontalLayout_theme.addWidget(self.lbl_theme)

        self.combo_theme = QComboBox(self.appearanceGroup)
        self.combo_theme.setObjectName(u"combo_theme")

        self.horizontalLayout_theme.addWidget(self.combo_theme)


        self.form_appearance.setLayout(0, QFormLayout.ItemRole.LabelRole, self.horizontalLayout_theme)

        self.horizontalLayout_font = QHBoxLayout()
        self.horizontalLayout_font.setObjectName(u"horizontalLayout_font")
        self.lbl_font = QLabel(self.appearanceGroup)
        self.lbl_font.setObjectName(u"lbl_font")

        self.horizontalLayout_font.addWidget(self.lbl_font)

        self.combo_fontsize = QComboBox(self.appearanceGroup)
        self.combo_fontsize.setObjectName(u"combo_fontsize")

        self.horizontalLayout_font.addWidget(self.combo_fontsize)


        self.form_appearance.setLayout(1, QFormLayout.ItemRole.LabelRole, self.horizontalLayout_font)


        self.verticalLayout_scroll.addWidget(self.appearanceGroup)

        self.backupGroup = QGroupBox(self.scrollAreaWidgetContents)
        self.backupGroup.setObjectName(u"backupGroup")
        self.form_backup = QFormLayout(self.backupGroup)
        self.form_backup.setObjectName(u"form_backup")
        self.horizontalLayout_interval = QHBoxLayout()
        self.horizontalLayout_interval.setObjectName(u"horizontalLayout_interval")
        self.lbl_backup_interval = QLabel(self.backupGroup)
        self.lbl_backup_interval.setObjectName(u"lbl_backup_interval")

        self.horizontalLayout_interval.addWidget(self.lbl_backup_interval)

        self.combo_backup_interval = QComboBox(self.backupGroup)
        self.combo_backup_interval.setObjectName(u"combo_backup_interval")

        self.horizontalLayout_interval.addWidget(self.combo_backup_interval)


        self.form_backup.setLayout(0, QFormLayout.ItemRole.LabelRole, self.horizontalLayout_interval)

        self.h_backup_dir = QHBoxLayout()
        self.h_backup_dir.setObjectName(u"h_backup_dir")
        self.lbl_backup_dir = QLabel(self.backupGroup)
        self.lbl_backup_dir.setObjectName(u"lbl_backup_dir")

        self.h_backup_dir.addWidget(self.lbl_backup_dir)

        self.edit_backup_dir = QLineEdit(self.backupGroup)
        self.edit_backup_dir.setObjectName(u"edit_backup_dir")

        self.h_backup_dir.addWidget(self.edit_backup_dir)

        self.btn_choose_backup_dir = QPushButton(self.backupGroup)
        self.btn_choose_backup_dir.setObjectName(u"btn_choose_backup_dir")
        icon = QIcon()
        icon.addFile(u":/icons/folder", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_choose_backup_dir.setIcon(icon)

        self.h_backup_dir.addWidget(self.btn_choose_backup_dir)


        self.form_backup.setLayout(1, QFormLayout.ItemRole.LabelRole, self.h_backup_dir)

        self.h_backup_actions = QHBoxLayout()
        self.h_backup_actions.setObjectName(u"h_backup_actions")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.h_backup_actions.addItem(self.horizontalSpacer_2)

        self.btn_backup_db = QPushButton(self.backupGroup)
        self.btn_backup_db.setObjectName(u"btn_backup_db")
        icon1 = QIcon()
        icon1.addFile(u":/icons/save", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_backup_db.setIcon(icon1)

        self.h_backup_actions.addWidget(self.btn_backup_db)

        self.btn_restore_backup = QPushButton(self.backupGroup)
        self.btn_restore_backup.setObjectName(u"btn_restore_backup")
        icon2 = QIcon()
        icon2.addFile(u":/icons/restore", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_restore_backup.setIcon(icon2)

        self.h_backup_actions.addWidget(self.btn_restore_backup)


        self.form_backup.setLayout(2, QFormLayout.ItemRole.LabelRole, self.h_backup_actions)


        self.verticalLayout_scroll.addWidget(self.backupGroup)

        self.widget_buttons = QWidget(self.scrollAreaWidgetContents)
        self.widget_buttons.setObjectName(u"widget_buttons")
        self.horizontalLayout_buttons = QHBoxLayout(self.widget_buttons)
        self.horizontalLayout_buttons.setObjectName(u"horizontalLayout_buttons")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_buttons.addItem(self.horizontalSpacer_3)

        self.btn_save_settings = QPushButton(self.widget_buttons)
        self.btn_save_settings.setObjectName(u"btn_save_settings")
        self.btn_save_settings.setMinimumSize(QSize(150, 40))
        self.btn_save_settings.setStyleSheet(u"QPushButton {\n"
"    background-color: #4CAF50;\n"
"    color: white;\n"
"    border: none;\n"
"    border-radius: 4px;\n"
"    padding: 8px 16px;\n"
"    font-weight: bold;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"    background-color: #45a049;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"    background-color: #3d8b40;\n"
"}")

        self.horizontalLayout_buttons.addWidget(self.btn_save_settings)


        self.verticalLayout_scroll.addWidget(self.widget_buttons)

        self.verticalSpacer1 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_scroll.addItem(self.verticalSpacer1)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.v_settings.addWidget(self.scrollArea)

        self.stacked_widget.addWidget(self.page_settings)

        self.verticalLayout_main.addWidget(self.stacked_widget)


        self.horizontalLayout.addWidget(self.mainArea)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u0646\u0638\u0627\u0645 \u0625\u062f\u0627\u0631\u0629 \u0627\u0644\u0645\u062e\u0627\u0632\u0646 \u0648\u0627\u0644\u0623\u0642\u0633\u0627\u0637", None))
        self.logoLabel.setText(QCoreApplication.translate("MainWindow", u"\u0625\u062f\u0627\u0631\u0629 \u0627\u0644\u0645\u062e\u0632\u0648\u0646 \u0648\u0627\u0644\u0623\u0642\u0633\u0627\u0637", None))
        self.btn_dashboard.setText(QCoreApplication.translate("MainWindow", u"\u0644\u0648\u062d\u0629 \u0627\u0644\u062a\u062d\u0643\u0645", None))
        self.btn_inventory.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u0645\u062e\u0627\u0632\u0646", None))
        self.btn_customers.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u0639\u0645\u0644\u0627\u0621", None))
        self.btn_invoices.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u0641\u0648\u0627\u062a\u064a\u0631", None))
        self.btn_reports.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u062a\u0642\u0627\u0631\u064a\u0631", None))
        self.btn_settings.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a", None))
        self.btn_logout.setText(QCoreApplication.translate("MainWindow", u"\u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062e\u0631\u0648\u062c", None))
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"\u0644\u0648\u062d\u0629 \u0627\u0644\u062a\u062d\u0643\u0645", None))
        self.alertsTitle.setText(QCoreApplication.translate("MainWindow", u"\u062a\u0646\u0628\u064a\u0647\u0627\u062a \u0627\u0644\u0623\u0642\u0633\u0627\u0637 \u0627\u0644\u0645\u062a\u0623\u062e\u0631\u0629", None))
        self.btn_add_inventory.setText(QCoreApplication.translate("MainWindow", u"\u2795 \u0625\u0636\u0627\u0641\u0629 \u0635\u0646\u0641", None))
        self.search_inventory.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0628\u062d\u062b \u0641\u064a \u0627\u0644\u0623\u0635\u0646\u0627\u0641...", None))
        self.btn_add_customer.setText(QCoreApplication.translate("MainWindow", u"\u2795 \u0625\u0636\u0627\u0641\u0629 \u0639\u0645\u064a\u0644", None))
        self.search_customers.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0628\u062d\u062b \u0641\u064a \u0627\u0644\u0639\u0645\u0644\u0627\u0621...", None))
        self.btn_add_invoice.setText(QCoreApplication.translate("MainWindow", u"\u2795 \u0625\u0636\u0627\u0641\u0629 \u0641\u0627\u062a\u0648\u0631\u0629", None))
        self.search_invoices.setPlaceholderText(QCoreApplication.translate("MainWindow", u"\u0628\u062d\u062b \u0641\u064a \u0627\u0644\u0641\u0648\u0627\u062a\u064a\u0631...", None))
        self.reportsLabel.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u062a\u0642\u0627\u0631\u064a\u0631", None))
        self.btn_export_reports.setText(QCoreApplication.translate("MainWindow", u"\u062a\u0635\u062f\u064a\u0631 PDF", None))
        self.settingsLabel.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a", None))
        self.appearanceGroup.setTitle(QCoreApplication.translate("MainWindow", u"\u0625\u0639\u062f\u0627\u062f\u0627\u062a \u0627\u0644\u0645\u0638\u0647\u0631", None))
        self.lbl_theme.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0644\u0633\u0645\u0629:", None))
        self.lbl_font.setText(QCoreApplication.translate("MainWindow", u"\u062d\u062c\u0645 \u0627\u0644\u062e\u0637:", None))
        self.backupGroup.setTitle(QCoreApplication.translate("MainWindow", u"\u0625\u0639\u062f\u0627\u062f\u0627\u062a \u0627\u0644\u0646\u0633\u062e \u0627\u0644\u0627\u062d\u062a\u064a\u0627\u0637\u064a", None))
        self.lbl_backup_interval.setText(QCoreApplication.translate("MainWindow", u"\u0641\u062a\u0631\u0629 \u0627\u0644\u0646\u0633\u062e \u0627\u0644\u0627\u062d\u062a\u064a\u0627\u0637\u064a:", None))
        self.lbl_backup_dir.setText(QCoreApplication.translate("MainWindow", u"\u0645\u0633\u0627\u0631 \u0627\u0644\u062d\u0641\u0638:", None))
        self.btn_choose_backup_dir.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0633\u062a\u0639\u0631\u0627\u0636", None))
        self.btn_backup_db.setText(QCoreApplication.translate("MainWindow", u"\u0625\u0646\u0634\u0627\u0621 \u0646\u0633\u062e\u0629 \u0627\u062d\u062a\u064a\u0627\u0637\u064a\u0629 \u0627\u0644\u0622\u0646", None))
        self.btn_restore_backup.setText(QCoreApplication.translate("MainWindow", u"\u0627\u0633\u062a\u0639\u0627\u062f\u0629 \u0645\u0646 \u0646\u0633\u062e\u0629", None))
        self.btn_save_settings.setText(QCoreApplication.translate("MainWindow", u"\u062d\u0641\u0638 \u0627\u0644\u0625\u0639\u062f\u0627\u062f\u0627\u062a", None))
    # retranslateUi

