#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, functools, json
from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox, QDialog, QLabel,
                               QLineEdit, QFormLayout, QDialogButtonBox, QVBoxLayout,
                               QPushButton, QTableWidget, QTableWidgetItem, QWidget, QHBoxLayout,
                               QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QHeaderView, QAbstractItemView, QTextEdit,
                               QAbstractSpinBox, QScrollArea, QTabWidget, QCalendarWidget)
from PySide6.QtCore import QFile, Qt, QSize, QDate, QLocale
from PySide6.QtGui import QIcon, QColor, QGuiApplication, QBrush
from PySide6.QtUiTools import QUiLoader
from database import Database, DB_PATH
import sys
from payments_dialog import AddPaymentDialog


from mainwindow_ui import Ui_MainWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QSS_LIGHT = os.path.join(BASE_DIR, "style_light.qss")
QSS_DARK = os.path.join(BASE_DIR, "style_dark.qss")
ICONS_DIR = os.path.join(BASE_DIR, "icons")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# try import QtCharts
try:
    from PySide6.QtCharts import QChartView, QChart, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
    CHARTS_AVAILABLE = True
except Exception:
    CHARTS_AVAILABLE = False

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Ensure required keys exist
                if 'theme' not in config:
                    config['theme'] = 'light'
                if 'font_size' not in config:
                    config['font_size'] = 15
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
    return {"theme": "light", "font_size": 15}

def save_config(conf):
    try:
        # Remove db_path if it exists to keep config clean
        if 'db_path' in conf:
            del conf['db_path']
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(conf, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def icon(name):
    p = os.path.join(ICONS_DIR, name)
    if os.path.exists(p):
        return QIcon(p)
    return QIcon()

def find(widget, name):
    return widget.findChild(QWidget, name)

# ---------------- Dialogs ----------------
class CustomerDialog(QDialog):
    def __init__(self, parent=None, title="إضافة عميل", data=None):
        super().__init__(parent); self.setWindowTitle(title); self.setModal(True); self.resize(420,180)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.name_edit = QLineEdit(); self.phone_edit = QLineEdit(); self.note_edit = QLineEdit()
        form.addRow("الاسم:", self.name_edit); form.addRow("الهاتف:", self.phone_edit); form.addRow("ملاحظة:", self.note_edit)
        layout.addLayout(form); buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
        if data: self.name_edit.setText(data.get("name","")); self.phone_edit.setText(data.get("phone","")); self.note_edit.setText(data.get("note",""))
    def get_data(self): return {"name": self.name_edit.text().strip(), "phone": self.phone_edit.text().strip(), "note": self.note_edit.text().strip()}

class ProductDialog(QDialog):
    def __init__(self, parent=None, title="إضافة منتج", data=None):
        super().__init__(parent); self.setWindowTitle(title); self.setModal(True); self.resize(420,200)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.name_edit = QLineEdit(); self.price_spin = QDoubleSpinBox(); self.price_spin.setMaximum(10**9); self.price_spin.setDecimals(2)
        self.stock_spin = QDoubleSpinBox(); self.stock_spin.setMaximum(10**6); self.stock_spin.setDecimals(0)
        form.addRow("الاسم:", self.name_edit); form.addRow("السعر:", self.price_spin); form.addRow("الكمية:", self.stock_spin)
        layout.addLayout(form); buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
        if data: self.name_edit.setText(data.get("name","")); self.price_spin.setValue(data.get("price",0)); self.stock_spin.setValue(data.get("stock",0))
    def get_data(self): return {"name": self.name_edit.text().strip(), "price": float(self.price_spin.value()), "stock": int(self.stock_spin.value())}

class InstallmentDialog(QDialog):
    def __init__(self, parent=None, title="إضافة قسط", data=None):
        super().__init__(parent); self.setWindowTitle(title); self.setModal(True); self.resize(480,240)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.customer_cb = QComboBox(); self.product_cb = QComboBox(); self.due_date = QDateEdit(); self.due_date.setDisplayFormat("yyyy-MM-dd"); self.due_date.setDate(QDate.currentDate())
        self.amount_spin = QDoubleSpinBox(); self.amount_spin.setMaximum(10**9); self.amount_spin.setDecimals(2)
        customers = Database().fetch_all("SELECT id, name FROM customers ORDER BY name");
        for c in customers: self.customer_cb.addItem(c[1], c[0])
        products = Database().fetch_all("SELECT id, name FROM products ORDER BY name");
        for p in products: self.product_cb.addItem(p[1], p[0])
        form.addRow("العميل:", self.customer_cb); form.addRow("المنتج:", self.product_cb); form.addRow("تاريخ الاستحقاق:", self.due_date); form.addRow("المبلغ:", self.amount_spin)
        layout.addLayout(form); buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
        if data:
            idx_c = self.customer_cb.findData(data.get("customer_id"));
            if idx_c>=0: self.customer_cb.setCurrentIndex(idx_c)
            idx_p = self.product_cb.findData(data.get("product_id"));
            if idx_p>=0: self.product_cb.setCurrentIndex(idx_p)
            if data.get("due_date"):
                try:
                    y,m,d = map(int, data.get("due_date").split("-")); self.due_date.setDate(QDate(y,m,d))
                except: pass
            if data.get("amount"): self.amount_spin.setValue(data.get("amount"))
    def get_data(self): return {"customer_id": self.customer_cb.currentData(), "product_id": self.product_cb.currentData(), "due_date": self.due_date.date().toString("yyyy-MM-dd"), "amount": float(self.amount_spin.value())}

class InvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("فاتورة جديدة")
        self.setModal(True)
        self.resize(520, 300)
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.customer_cb = QComboBox()
        self.product_cb = QComboBox()
        self.qty_spin = QDoubleSpinBox(); self.qty_spin.setMaximum(1000); self.qty_spin.setDecimals(0); self.qty_spin.setValue(1)
        self.total_spin = QDoubleSpinBox(); self.total_spin.setMaximum(10**9); self.total_spin.setDecimals(2)
        self.upfront_spin = QDoubleSpinBox(); self.upfront_spin.setMaximum(10**9); self.upfront_spin.setDecimals(2)
        self.months_spin = QDoubleSpinBox(); self.months_spin.setMaximum(36); self.months_spin.setDecimals(0); self.months_spin.setValue(12)
        
        # Add date field with Arabic localization
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        current_date = QDate.currentDate()
        self.date_edit.setDate(current_date)
        self.date_edit.setDisplayFormat("yyyy/MM/dd")
        
        # Set Arabic locale for the calendar
        locale = QLocale(QLocale.Arabic, QLocale.SaudiArabia)
        QLocale.setDefault(locale)  # Set default locale for the application
        
        # Create and configure the calendar
        calendar = QCalendarWidget()
        calendar.setLocale(locale)
        calendar.setFirstDayOfWeek(Qt.Sunday)  # Week starts on Sunday in Arabic locale
        
        # Configure calendar appearance and behavior
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)  # Hide week numbers
        calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)  # Show short day names
        calendar.setGridVisible(False)  # Hide the grid
        
        # Set current month view and disable dates from other months
        calendar.setCurrentPage(current_date.year(), current_date.month())
        calendar.setDateEditEnabled(False)  # Prevent direct date editing
        
        # Hide days from other months completely
        calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        calendar.setHorizontalHeaderFormat(QCalendarWidget.ShortDayNames)
        calendar.setGridVisible(False)
        
        # Apply custom stylesheet to style the calendar
        calendar.setStyleSheet("""
            /* Base style for all calendar elements */
            QCalendarWidget {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            
            /* Header styling */
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #f5f5f5;
                border-bottom: 1px solid #e0e0e0;
            }
            
            /* Month and year button */
            QCalendarWidget QToolButton {
                color: #333333;
                font-weight: bold;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
            
            QCalendarWidget QToolButton:hover {
                background: #e0e0e0;
            }
            
            /* Weekday header */
            QCalendarWidget QWidget#qt_calendar_calendarview {
                alternate-background-color: white;
            }
            
            /* Weekday names */
            QCalendarWidget QAbstractItemView {
                color: #333333;
                selection-background-color: #2196F3;
                selection-color: white;
                outline: 0;
            }
            
            /* Days of the month */
            QCalendarWidget QAbstractItemView:enabled {
                color: #333333;
                background: white;
            }
            
            /* Hide days from other months */
            QCalendarWidget QAbstractItemView:disabled {
                color: transparent;
                background: transparent;
                border: none;
            }
            
            /* Selected date */
            QCalendarWidget QAbstractItemView:selected {
                background-color: #2196F3;
                color: white;
                border-radius: 4px;
            }
            
            /* Today's date */
            QCalendarWidget QAbstractItemView:enabled:selected {
                background: #1565C0;
                color: white;
            }
            
            /* Hover effect */
            QCalendarWidget QAbstractItemView:enabled:hover {
                background: #E3F2FD;
            }
        """)
        
        # Set the calendar widget
        self.date_edit.setCalendarWidget(calendar)
        self.date_edit.setCalendarPopup(True)
        
        # Connect month changed signal to update the view
        calendar.currentPageChanged.connect(lambda y, m: self.update_calendar_view(calendar, y, m))
        
        # Set date range (current month only initially)
        self.update_calendar_view(calendar, current_date.year(), current_date.month())
        
        # Add method to handle month changes
        def update_date_edit():
            selected_date = calendar.selectedDate()
            self.date_edit.setDate(selected_date)
            
        calendar.clicked.connect(update_date_edit)

        # customers
        customers = Database().fetch_all("SELECT id, name FROM customers ORDER BY name")
        for c in customers: self.customer_cb.addItem(c[1], c[0])

        # products list with prices
        self.products = []
        products = Database().fetch_all("SELECT id, name, price FROM products ORDER BY name")
        for p in products:
            self.product_cb.addItem(p[1], p[0])
            self.products.append({"id": p[0], "name": p[1], "price": p[2]})

        form.addRow("العميل:", self.customer_cb)
        form.addRow("المنتج:", self.product_cb)
        form.addRow("الكمية:", self.qty_spin)
        form.addRow("المبلغ الإجمالي:", self.total_spin)
        form.addRow("المدفوع مقدماً:", self.upfront_spin)
        form.addRow("عدد الشهور:", self.months_spin)
        form.addRow("تاريخ الفاتورة:", self.date_edit)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # auto calc
        self.product_cb.currentIndexChanged.connect(self.calculate_total)
        self.qty_spin.valueChanged.connect(self.calculate_total)
        self.calculate_total()

    def calculate_total(self):
        idx = self.product_cb.currentIndex()
        if idx >= 0 and idx < len(self.products):
            price = self.products[idx]["price"]
            qty = self.qty_spin.value()
            total = price * qty
            self.total_spin.setValue(total)

    def update_calendar_view(self, calendar, year, month):
        """Update calendar to show only the current month's days"""
        # Store the current date
        current_date = QDate.currentDate()
        
        # Calculate first and last day of the month
        first_day = QDate(year, month, 1)
        last_day = QDate(year, month, first_day.daysInMonth())
        
        # Set date range to current month only
        calendar.setMinimumDate(first_day)
        calendar.setMaximumDate(last_day)
        
        # Set the current page
        calendar.setCurrentPage(year, month)
        
        # Force update the view
        calendar.updateCells()
        
        # Ensure the calendar shows the current date if it's in the current month
        if current_date.year() == year and current_date.month() == month:
            calendar.setSelectedDate(current_date)
        else:
            calendar.setSelectedDate(first_day)
        
    def get_data(self):
        months = int(self.months_spin.value())
        upfront_paid = float(self.upfront_spin.value())
        total_amount = float(self.total_spin.value())
        installment_amount = (total_amount - upfront_paid) / months if months else 0
        
        # Get the selected date
        selected_date = self.date_edit.date()
        
        return {
            "customer_id": self.customer_cb.currentData(),
            "product_id": self.product_cb.currentData(),
            "quantity": int(self.qty_spin.value()),
            "total_amount": total_amount,
            "months": months,
            "installment_count": months,
            "installment_amount": installment_amount,
            "start_date": selected_date.toString("yyyy-MM-dd"),
            "upfront_paid": upfront_paid,
            "invoice_date": selected_date.toString("yyyy-MM-dd")
        }

class InstallmentPaymentDialog(QDialog):
    def __init__(self, installment_id, remaining, parent=None):
        super().__init__(parent)
        self.installment_id = installment_id
        self.remaining = remaining
        self.setWindowTitle("سداد قسط")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for input fields
        form_layout = QFormLayout()
        
        # Amount input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(remaining)
        self.amount_input.setMinimum(0.01)
        self.amount_input.setValue(0.00)  # Default to 0.00 (empty)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" ج.م")
        self.amount_input.setButtonSymbols(QAbstractSpinBox.UpDownArrows)
        
        # Connect value changed to update remaining label
        self.amount_input.valueChanged.connect(self.update_remaining_label)
        
        # Remaining amount label
        self.lbl_remaining = QLabel(f"المبلغ المتبقي: {remaining:,.2f} ج.م")
        self.lbl_remaining.setStyleSheet("font-weight: bold; color: #d32f2f;")
        
        # Payment date
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # Notes field
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("ملاحظات إضافية (اختياري)")
        self.notes_input.setMaximumHeight(100)
        
        # Add to form
        form_layout.addRow("المبلغ:", self.amount_input)
        form_layout.addRow("", self.lbl_remaining)
        form_layout.addRow("تاريخ الدفعة:", self.date_edit)
        form_layout.addRow("ملاحظات:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("سداد القسط")
        btn_ok.setIcon(icon("save.svg"))
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.setIcon(icon("cancel.svg"))
        
        btn_ok.clicked.connect(self.validate_and_accept)
        btn_cancel.clicked.connect(self.reject)
        
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        
        layout.addLayout(btn_box)
        
        # Set focus to amount input
        self.amount_input.setFocus()

    def update_remaining_label(self, value):
        remaining = self.remaining - value
        self.lbl_remaining.setText(f"المبلغ المتبقي: {remaining:,.2f} ج.م")
        
        # Update color based on remaining amount
        if remaining <= 0:
            self.lbl_remaining.setStyleSheet("font-weight: bold; color: #388e3c;")
        else:
            self.lbl_remaining.setStyleSheet("font-weight: bold; color: #d32f2f;")

    def validate_and_accept(self):
        amount = self.amount_input.value()
        if amount <= 0:
            QMessageBox.warning(self, "خطأ", "الرجاء إدخال مبلغ صحيح")
            return
            
        if amount > self.remaining:
            QMessageBox.warning(self, "خطأ", "المبلغ المدخل أكبر من المتبقي")
            return
            
        self.accept()
    
    def get_amount(self):
        return self.amount_input.value()
        
    def get_notes(self):
        return self.notes_input.toPlainText().strip()
        
    def get_payment_date(self):
        return self.date_edit.date().toString("yyyy-MM-dd")


class AddInvoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة فاتورة جديدة")
        self.resize(400, 300)

        layout = QFormLayout(self)

        self.customer_name = QLineEdit()
        self.product_name = QLineEdit()
        self.total_amount = QSpinBox()
        self.total_amount.setMaximum(1000000)
        self.total_amount.setMinimum(1)
        self.installment_count = QSpinBox()
        self.installment_count.setMinimum(1)
        self.installment_count.setMaximum(36)
        self.start_date = QDateEdit(QDate.currentDate())
        self.start_date.setCalendarPopup(True)

        layout.addRow("اسم العميل:", self.customer_name)
        layout.addRow("اسم المنتج:", self.product_name)
        layout.addRow("الإجمالي (مبلغ):", self.total_amount)
        layout.addRow("عدد الأقساط:", self.installment_count)
        layout.addRow("تاريخ بداية التقسيط:", self.start_date)

        btn_box = QHBoxLayout()
        btn_ok = QPushButton("حفظ")
        btn_cancel = QPushButton("إلغاء")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)
        layout.addRow(btn_box)

    def get_data(self):
        return {
            "customer_name": self.customer_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "total_amount": self.total_amount.value(),
            "installment_count": self.installment_count.value(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd")
        }

    def update_summary(self):
        db = Database()
        
        # Get invoice total
        invoice = db.fetch_all(
            "SELECT total_amount FROM invoices WHERE id = ?",
            (self.invoice_id,)
        )
        
        if not invoice:
            return
            
        total = invoice[0][0]
        
        # Get paid amount
        result = db.fetch_all(
            "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE invoice_id = ?",
            (self.invoice_id,)
        )
        paid = result[0][0] if result else 0
        remaining = total - paid
        
        # Update labels
        self.lbl_total.setText(f"{total:,.2f} ج.م")
        self.lbl_paid.setText(f"{paid:,.2f} ج.م")
        self.lbl_remaining.setText(f"{remaining:,.2f} ج.م")
        
        # Update colors based on status
        self.lbl_remaining.setStyleSheet(
            f"color: {'#d32f2f' if remaining > 0 else '#388e3c'}; "
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        self.lbl_paid.setStyleSheet("color: #388e3c; font-size: 14px; font-weight: bold; padding: 5px;")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")

    def add_payment(self):
        # Get remaining amount
        total = float(self.lbl_total.text().replace(" ج.م", "").replace(",", ""))
        paid = float(self.lbl_paid.text().replace(" ج.م", "").replace(",", ""))
        remaining = total - paid

        if remaining <= 0:
            QMessageBox.information(self, "تم الدفع بالكامل", "تم سداد كامل مبلغ الفاتورة")
            return

        dialog = AddPaymentDialog(self.invoice_id, remaining, self)
        if dialog.exec() == QDialog.Accepted:
            pass
            
    def get_data(self):
        return {
            "customer_name": self.customer_name.text().strip(),
            "product_name": self.product_name.text().strip(),
            "total_amount": self.total_amount.value(),
            "installment_count": self.installment_count.value(),
            "start_date": self.start_date.date().toString("yyyy-MM-dd")
        }

def create_tables():
    # Set the database path before creating any Database instances
    from database import DB_PATH as db_path
    print(f"Using database at: {db_path}")
    
    # Initialize database and create tables if they don't exist
    db = Database()
    db.create_tables()
    # Create products table
    db.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL,
        stock INTEGER
    )
    ''')
    
    # Create installments table
    Database().execute('''
    CREATE TABLE IF NOT EXISTS installments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        invoice_id INTEGER,
        due_date TEXT,
        amount REAL,
        paid REAL DEFAULT 0
    )
    ''')
    
    # Create invoices table
    Database().execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        total_amount REAL,
        upfront_paid REAL,
        months INTEGER,
        created_at TEXT
    )
    ''')

# ---------------- Main App ----------------
class MainApp(QMainWindow, Ui_MainWindow):  # نبدل ترتيب الوراثة
    def __init__(self):
        super().__init__()

        # تحميل التصميم من ملف mainwindow_ui.py
        self.setupUi(self)

        # ضبط حجم النافذة حسب الشاشة الحالية
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        geometry = screen.availableGeometry()
        self.setGeometry(geometry)
        self.setWindowTitle("معرض الحاج سيد قايد للأجهزة الحديثة")

        # Load config
        self.config = load_config()
        self.apply_theme(self.config.get("theme", "light"), self.config.get("font_size", 15))

        # Set database path
        from database import DB_PATH
        print(f"Using database at: {DB_PATH}")
        
        # Ensure the directory exists
        db_dir = os.path.dirname(DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # Initialize database and create tables
        try:
            # This will now use the path we just set
            db = Database()
            create_tables()
            print(f"Using database at: {db.db_path}")  # Debug print
        except Exception as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", 
                               f"حدث خطأ أثناء تهيئة قاعدة البيانات:\n{str(e)}")
            sys.exit(1)

        # widgets
        self.stacked = self.findChild(QWidget,"stacked_widget")
        self.titleLabel = self.findChild(QWidget,"titleLabel")
        self.table_inventory = self.findChild(QWidget,"table_inventory")
        self.table_customers = self.findChild(QWidget,"table_customers")

        self.table_alerts = self.findChild(QWidget,"table_alerts")
        self.table_reports = self.findChild(QWidget,"table_reports")
        self.chartArea = self.findChild(QWidget,"chartArea")
        self.table_invoices = self.findChild(QWidget, "table_invoices")
        if self.table_invoices:
            self.table_invoices.setColumnCount(10)
            
        # Initialize installments table
        self.table_installments = self.findChild(QWidget, "table_installments")
        if self.table_installments:
            # Setup installments table with appropriate columns
            self.setup_table(self.table_installments, [
                "رقم الفاتورة", "العميل", "المنتج", "تاريخ الاستحقاق", 
                "المبلغ", "المسدد", "المتبقي", "رقم الفاتورة", "الحالة", "العمليات"
            ])

        self.btn_add_inventory = self.findChild(QWidget,"btn_add_inventory")
        self.btn_add_customer = self.findChild(QWidget,"btn_add_customer")
        self.btn_add_installment = self.findChild(QWidget,"btn_add_installment")
        self.btn_add_invoice = self.findChild(QWidget,"btn_add_invoice")
        # search fields
        self.search_inventory = self.findChild(QWidget, "search_inventory")
        self.search_customers = self.findChild(QWidget, "search_customers")

        self.search_invoices = self.findChild(QWidget, "search_invoices")

        # sidebar mapping (include invoices) - تم إزالة الربط المزدوج
        # mapping = {
        #     "btn_dashboard": ("page_dashboard", "لوحة التحكم"),
        #     "btn_inventory": ("page_inventory", "المخازن"),
        #     "btn_customers": ("page_customers", "العملاء"),
        #     "btn_installments": ("page_installments", "الأقساط"),
        #     "btn_invoices": ("page_invoices", "الفواتير"),
        #     "btn_reports": ("page_reports", "التقارير"),
        #     "btn_settings": ("page_settings", "الإعدادات")
        # }
        # for bn,(pn,title) in mapping.items():
        #     b = self.findChild(QWidget,bn); p = self.findChild(QWidget,pn)
        #     if b and p: b.clicked.connect(functools.partial(self.switch_page,p,title))

        # logout
        btn_logout = self.findChild(QWidget,"btn_logout");
        if btn_logout: btn_logout.clicked.connect(self.logout)

        # icons
        ico_map = {
            "btn_dashboard": "dashboard.svg",
            "btn_inventory": "products.svg",
            "btn_customers": "customers.svg",
            "btn_installments": "payments.svg",
            "btn_invoices": "invoice.svg",
            "btn_reports": "reports.svg",
            "btn_add_inventory": "add.svg",
            "btn_add_customer": "add.svg",
            "btn_add_installment": "add.svg",
            "btn_add_invoice": "add.svg",
            "btn_export_reports": "reports.svg",
            "btn_backup_db": "save.svg",
            "btn_restore_backup": "invoice.svg",
            "btn_choose_backup_dir": "products.svg",
            "btn_export_inventory_csv": "reports.svg",
            "btn_export_customers_csv": "reports.svg",
            "btn_export_installments_csv": "reports.svg",
            "btn_export_invoices_csv": "reports.svg"
        }
        for k,v in ico_map.items():
            w = self.findChild(QWidget,k)
            if w:
                try:
                    w.setIcon(icon(v)); w.setIconSize(QSize(18,18))
                except: pass

        # connect add buttons
        if self.btn_add_inventory: self.btn_add_inventory.clicked.connect(self.add_product)
        if self.btn_add_customer: self.btn_add_customer.clicked.connect(self.add_customer)
        if self.btn_add_installment: self.btn_add_installment.clicked.connect(self.add_installment)
        if self.btn_add_invoice: self.btn_add_invoice.clicked.connect(self.add_invoice)
        # connect search
        if self.search_inventory: self.search_inventory.textChanged.connect(self.refresh_products)
        if self.search_customers: self.search_customers.textChanged.connect(self.refresh_customers)

        if self.search_invoices: self.search_invoices.textChanged.connect(self.refresh_invoices)

        # export & backup buttons
        self.btn_export_reports = self.findChild(QWidget, "btn_export_reports")
        if self.btn_export_reports: self.btn_export_reports.clicked.connect(self.export_reports_pdf)
        self.btn_backup_db = self.findChild(QWidget, "btn_backup_db")
        if self.btn_backup_db: self.btn_backup_db.clicked.connect(self.backup_database)
        # removed CSV export buttons per request

        # settings init
        combo_theme = self.findChild(QWidget,"combo_theme")
        combo_font = self.findChild(QWidget,"combo_fontsize")
        if combo_theme:
            combo_theme.addItem("فاتح","light"); combo_theme.addItem("داكن","dark");
            idx = combo_theme.findData(self.config.get("theme","light")); combo_theme.setCurrentIndex(idx if idx>=0 else 0)
        if combo_font:
            for s in [14,15,16,18,20]: combo_font.addItem(str(s), s)
            idxf = combo_font.findData(self.config.get("font_size",15)); combo_font.setCurrentIndex(idxf if idxf>=0 else 1)
        btn_save = self.findChild(QWidget,"btn_save_settings")
        if btn_save: btn_save.clicked.connect(self.save_settings)

        # backup settings widgets
        self.combo_backup_interval = self.findChild(QWidget, "combo_backup_interval")
        self.edit_backup_dir = self.findChild(QWidget, "edit_backup_dir")
        self.btn_choose_backup_dir = self.findChild(QWidget, "btn_choose_backup_dir")
        self.btn_restore_backup = self.findChild(QWidget, "btn_restore_backup")
        if self.combo_backup_interval:
            self.combo_backup_interval.addItem("يدوياً", "manual")
            self.combo_backup_interval.addItem("يومي", "daily")
            self.combo_backup_interval.addItem("أسبوعي", "weekly")
            self.combo_backup_interval.addItem("شهري", "monthly")
        if self.btn_choose_backup_dir: self.btn_choose_backup_dir.clicked.connect(self.choose_backup_dir)
        if self.btn_restore_backup: self.btn_restore_backup.clicked.connect(self.restore_backup)
        # load backup settings from config
        backup_conf = self.config.get("backup", {"interval":"manual","dir": BASE_DIR})
        if self.combo_backup_interval:
            idxb = self.combo_backup_interval.findData(backup_conf.get("interval","manual"))
            self.combo_backup_interval.setCurrentIndex(idxb if idxb>=0 else 0)
        if self.edit_backup_dir:
            self.edit_backup_dir.setText(backup_conf.get("dir", BASE_DIR))

        # setup tables (columns)
        self.setup_table(self.table_inventory,["ID","الصنف","الكمية","السعر","العمليات"])
        self.setup_table(self.table_customers,["ID","اسم العميل","الهاتف","ملاحظة","العمليات"])
        # installments: add status and actions columns

        self.setup_table(self.table_alerts,["المبلغ","تاريخ الاستحقاق","العميل"])
        self.setup_table(self.findChild(QWidget,"table_reports"),["المؤشر","القيمة","ملاحظة"])
        self.setup_table(self.table_invoices,["ID","العميل","المنتج","الكمية","الإجمالي","المدفوع مقدماً","عدد الشهور","تاريخ الإنشاء","المتبقي","العمليات"])

        # add customer filter combobox on installments header (if header exists)
        inst_header = self.findChild(QWidget, "instHeader")
        self.filter_customer_cb = None
        if inst_header:
            # create a small combobox and add to header layout if possible
            try:
                from PySide6.QtWidgets import QHBoxLayout
                layout = inst_header.layout()
                self.filter_customer_cb = QComboBox(inst_header)
                self.filter_customer_cb.setObjectName("filter_customer_cb")
                self.filter_customer_cb.addItem("كل العملاء", None)
                customers = Database().fetch_all("SELECT id, name FROM customers ORDER BY name")
                for c in customers:
                    self.filter_customer_cb.addItem(c[1], c[0])
                # insert at the end of header layout
                layout.addWidget(self.filter_customer_cb)
                self.filter_customer_cb.currentIndexChanged.connect(self.refresh_installments)
            except Exception:
                self.filter_customer_cb = None

        # connect double-click on installments to pay


        # Configure form layout properties
        self.configure_form_layouts()
        
        # initial load
        self.refresh_all()
        self.switch_page(self.findChild(QWidget,"page_dashboard"), "لوحة التحكم")

        # schedule automatic backup if configured
        self.schedule_backup_if_needed()

        # أزرار التنقل
        self.btn_dashboard = self.findChild(QWidget, "btn_dashboard")
        self.btn_inventory = self.findChild(QWidget, "btn_inventory")
        self.btn_customers = self.findChild(QWidget, "btn_customers")
        self.btn_installments = self.findChild(QWidget, "btn_installments")
        self.btn_invoices = self.findChild(QWidget, "btn_invoices")
        self.btn_reports = self.findChild(QWidget, "btn_reports")
        self.btn_settings = self.findChild(QWidget, "btn_settings")
        self.btn_logout = self.findChild(QWidget, "btn_logout")
        
        # ربط أزرار التنقل
        if self.btn_dashboard: self.btn_dashboard.clicked.connect(lambda: self.show_page("page_dashboard"))
        if self.btn_inventory: self.btn_inventory.clicked.connect(lambda: self.show_page("page_inventory"))
        if self.btn_customers: self.btn_customers.clicked.connect(lambda: self.show_page("page_customers"))
        if self.btn_installments: self.btn_installments.clicked.connect(lambda: self.show_page("page_installments"))
        if self.btn_invoices: self.btn_invoices.clicked.connect(lambda: self.show_page("page_invoices"))
        if self.btn_reports: self.btn_reports.clicked.connect(lambda: self.show_page("page_reports"))
        if self.btn_settings: self.btn_settings.clicked.connect(lambda: self.show_page("page_settings"))
        if self.btn_logout: self.btn_logout.clicked.connect(self.logout)

    # ---------------- UI / helpers ----------------
    def apply_theme(self, theme, font_size):
        try:
            app = QApplication.instance()
            p = QSS_DARK if theme == "dark" else QSS_LIGHT
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f: 
                    app.setStyleSheet(f.read())
            
            # Increase base font size by 2 points for better readability
            base_font_size = font_size + 2
            table_font_size = base_font_size + 1
            sidebar_font_size = base_font_size + 1
            
            # Apply font sizes to different components
            app.setStyleSheet(app.styleSheet() + f"""
                /* Base font size for the application */
                QWidget {{ 
                    font-size: {base_font_size}px; 
                }}
                
                /* Tables */
                QTableWidget, QTableView, QTreeView, QListWidget, QTreeWidget, QTableCornerButton::section {{
                    font-size: {table_font_size}px;
                }}
                
                QHeaderView::section {{
                    font-size: {table_font_size}px;
                    padding: 10px;
                }}
                
                /* Sidebar */
                QFrame#sidebar, QFrame#sidebar QPushButton {{
                    font-size: {sidebar_font_size}px;
                    font-weight: bold;
                }}
                
                /* Buttons in tables */
                QPushButton.table-action {{
                    font-size: {table_font_size}px;
                    padding: 5px 10px;
                }}
                
                /* Form elements */
                QLabel, QLineEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox, QPushButton, QToolButton {{
                    font-size: {base_font_size}px;
                }}
            """)
        except Exception as e:
            print("apply_theme error:", e)
            QMessageBox.warning(None, "خطأ", f"حدث خطأ في تطبيق السمة: {str(e)}")

    def save_settings(self):
        combo_theme = self.findChild(QWidget,"combo_theme"); combo_font = self.findChild(QWidget,"combo_fontsize")
        if combo_theme and combo_font:
            t = combo_theme.currentData(); s = combo_font.currentData()
            self.config["theme"] = t; self.config["font_size"] = s
        # backup settings
        if self.combo_backup_interval and self.edit_backup_dir:
            self.config["backup"] = {
                "interval": self.combo_backup_interval.currentData() or "manual",
                "dir": self.edit_backup_dir.text().strip() or BASE_DIR
            }
        save_config(self.config)
        self.apply_theme(self.config.get("theme","light"), self.config.get("font_size",15))
        QMessageBox.information(self, "نجح", "تم حفظ الإعدادات")

    def switch_page(self, page_widget, title):
        idx = self.stacked.indexOf(page_widget);
        if idx>=0: self.stacked.setCurrentIndex(idx)
        lbl = self.findChild(QWidget,"titleLabel");
        if lbl: lbl.setText(title)

    def show_page(self, page_name):
        """عرض صفحة معينة باستخدام اسمها"""
        page_widget = self.findChild(QWidget, page_name)
        if page_widget:
            # البحث عن العنوان المناسب من mapping
            mapping = {
                "page_dashboard": "لوحة التحكم",
                "page_inventory": "المخازن",
                "page_customers": "العملاء",
                "page_installments": "الأقساط",
                "page_invoices": "الفواتير",
                "page_reports": "التقارير",
                "page_settings": "الإعدادات"
            }
            title = mapping.get(page_name, page_name)
            self.switch_page(page_widget, title)
            
            # تحديث البيانات عند تغيير الصفحة
            if page_name == "page_customers":
                self.refresh_customers()
            elif page_name == "page_inventory":
                self.refresh_products()
            elif page_name == "page_installments":
                self.refresh_installments()
            elif page_name == "page_invoices":
                self.refresh_invoices()
            elif page_name == "page_dashboard":
                self.refresh_dashboard_cards()
                self.refresh_alerts()
                # منع تكبير النافذة عند الذهاب للصفحة الرئيسية
                self.prevent_maximization()

    def setup_table(self, table, headers):
        if table is None: return
        table.setColumnCount(len(headers)); table.setHorizontalHeaderLabels(headers)
        hdr = table.horizontalHeader(); hdr.setSectionResizeMode(QHeaderView.Stretch)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers); table.setSelectionBehavior(QAbstractItemView.SelectRows); table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().setVisible(False); table.setAlternatingRowColors(True); table.resizeRowsToContents()

    def ensure_sample_data(self):
        if not Database().fetch_all("SELECT 1 FROM customers LIMIT 1"):
            Database().execute("INSERT INTO customers (name,phone,note) VALUES (?,?,?)", ("أحمد علي","011100000","عميل جيد"))
            Database().execute("INSERT INTO customers (name,phone,note) VALUES (?,?,?)", ("منى سمير","012200000",""))
        if not Database().fetch_all("SELECT 1 FROM products LIMIT 1"):
            Database().execute("INSERT INTO products (name,price,stock) VALUES (?,?,?)", ("هاتف ذكي",250.0,10))
            Database().execute("INSERT INTO products (name,price,stock) VALUES (?,?,?)", ("غسالة",450.0,4))
        if not Database().fetch_all("SELECT 1 FROM invoices LIMIT 1"):
            # create a sample invoice to have something to show
            Database().execute(
                "INSERT INTO invoices (customer_id,product_id,quantity,total_amount,upfront_paid,installment_count,installment_amount,start_date,created_at) VALUES (?,?,?,?,?,?,?,?,datetime('now'))",
                (1,1,1,250.0,0.0,5,50.0,"2025-08-09")
            )
            invoice_id = Database().fetch_all("SELECT last_insert_rowid()")[0][0]

        # ---------------- refresh / render ----------------
    def refresh_all(self):
        self.refresh_products()
        self.refresh_customers()
        self.refresh_alerts()
        self.refresh_dashboard_cards()
        self.refresh_reports_table()
        self.refresh_invoices()

    def refresh_products(self):
        table = self.table_inventory; table.setRowCount(0)
        params = []
        query = "SELECT id,name,stock,price FROM products WHERE 1=1"
        if self.search_inventory and self.search_inventory.text().strip():
            term = f"%{self.search_inventory.text().strip()}%"
            query += " AND name LIKE ?"
            params.append(term)
        query += " ORDER BY id DESC"
        rows = Database().fetch_all(query, tuple(params))
        for r,row in enumerate(rows):
            table.insertRow(r)
            table.setItem(r,0,QTableWidgetItem(str(row[0]))); table.setItem(r,1,QTableWidgetItem(row[1])); table.setItem(r,2,QTableWidgetItem(str(row[2]))); table.setItem(r,3,QTableWidgetItem(str(row[3])))
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0); h.setSpacing(6)
            be = QPushButton(); be.setIcon(icon("edit.svg")); be.setFlat(True); be.clicked.connect(functools.partial(self.edit_product,row[0]))
            bd = QPushButton(); bd.setIcon(icon("delete.svg")); bd.setFlat(True); bd.clicked.connect(functools.partial(self.delete_product,row[0]))
            be.setProperty("class","table-action"); bd.setProperty("class","table-action"); h.addWidget(be); h.addWidget(bd); table.setCellWidget(r,4,w)
        table.resizeRowsToContents()

    def refresh_customers(self):
        table = self.table_customers; table.setRowCount(0)
        params = []
        query = "SELECT id,name,phone,note FROM customers WHERE 1=1"
        if self.search_customers and self.search_customers.text().strip():
            term = f"%{self.search_customers.text().strip()}%"
            query += " AND (name LIKE ? OR phone LIKE ?)"
            params.extend([term, term])
        query += " ORDER BY id DESC"
        rows = Database().fetch_all(query, tuple(params))
        for r,row in enumerate(rows):
            table.insertRow(r); table.setItem(r,0,QTableWidgetItem(str(row[0]))); table.setItem(r,1,QTableWidgetItem(row[1])); table.setItem(r,2,QTableWidgetItem(row[2] or "")); table.setItem(r,3,QTableWidgetItem(row[3] or ""))
            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0); h.setSpacing(6)
            be = QPushButton(); be.setIcon(icon("edit.svg")); be.setFlat(True); be.clicked.connect(functools.partial(self.edit_customer,row[0]))
            bd = QPushButton(); bd.setIcon(icon("delete.svg")); bd.setFlat(True); bd.clicked.connect(functools.partial(self.delete_customer,row[0]))
            be.setProperty("class","table-action"); bd.setProperty("class","table-action"); h.addWidget(be); h.addWidget(bd); table.setCellWidget(r,4,w)
        table.resizeRowsToContents()

    def refresh_installments(self):
        try:
            # Safely get the installments table
            table = getattr(self, 'table_installments', None)
            if not table:
                table = self.findChild(QTableWidget, "table_installments")
                if not table:
                    print("Warning: Installments table not found")
                    return
                self.table_installments = table
            
            # Make sure the table is properly initialized
            if not hasattr(table, 'setRowCount'):
                print("Error: Invalid table widget")
                return
                
            # Clear existing rows
            table.setRowCount(0)
            
            # Initialize filters
            params = []
            where = " WHERE 1=1"
            if hasattr(self, 'filter_customer_cb') and self.filter_customer_cb:
                customer_id = self.filter_customer_cb.currentData()
                if customer_id:
                    where += " AND c.id = ?"
                    params.append(customer_id)
                    
            # 1) Aggregated rows for installments linked to an invoice
            agg_query = f"""
                SELECT i.invoice_id,
                       c.id as customer_id,
                       c.name as customer_name,
                       p.name as product_name,
                       MIN(CASE WHEN IFNULL(i.paid,0) < i.amount THEN i.due_date ELSE NULL END) as next_due,
                       SUM(i.amount) as total_amount,
                       SUM(IFNULL(i.paid,0)) as total_paid,
                       COUNT(*) as inst_count
                FROM installments i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN products p ON i.product_id = p.id
                {where} AND i.invoice_id IS NOT NULL
                GROUP BY i.invoice_id, c.id, c.name, p.name
                ORDER BY next_due ASC
            """
            agg_rows = Database().fetch_all(agg_query, tuple(params)) if params else []

            row_index = 0
            for row in agg_rows:
                try:
                    invoice_id = row[0]
                    cust_id = row[1]
                    cust_name = row[2] or ""
                    prod_name = row[3] or ""
                    next_due = row[4] or ""
                    total_amount = float(row[5] or 0)
                    total_paid = float(row[6] or 0)
                    inst_count = int(row[7] or 0)
                    remaining = max(0.0, total_amount - total_paid)

                    # Insert new row
                    table.insertRow(row_index)
                    
                    # Set row data
                    table.setItem(row_index, 0, QTableWidgetItem(f"INV-{invoice_id}"))
                    table.setItem(row_index, 1, QTableWidgetItem(cust_name))
                    table.setItem(row_index, 2, QTableWidgetItem(f"{prod_name} ({inst_count} شهر)"))
                    table.setItem(row_index, 3, QTableWidgetItem(next_due))
                    table.setItem(row_index, 4, QTableWidgetItem(f"{total_amount:,.2f} ج.م"))
                    table.setItem(row_index, 5, QTableWidgetItem(f"{total_paid:,.2f} ج.م"))
                    
                    # Set remaining amount with color coding
                    rem_item = QTableWidgetItem(f"{remaining:,.2f} ج.م")
                    rem_item.setForeground(QColor("#388e3c") if remaining <= 0 else QColor("#d32f2f"))
                    table.setItem(row_index, 6, rem_item)
                    
                    # Set invoice ID and status
                    table.setItem(row_index, 7, QTableWidgetItem(str(invoice_id)))
                    status_item = QTableWidgetItem("مسدد" if remaining <= 0 else "غير مسدد")
                    status_item.setForeground(QColor("#388e3c") if remaining <= 0 else QColor("#d32f2f"))
                    table.setItem(row_index, 8, status_item)

                    # Create action buttons
                    w = QWidget()
                    h = QHBoxLayout(w)
                    h.setContentsMargins(5, 2, 5, 2)
                    h.setSpacing(5)
                    
                    # View payments button
                    btn_open = QPushButton()
                    btn_open.setIcon(icon("payments.svg"))
                    btn_open.setToolTip("عرض التفاصيل والدفعات")
                    btn_open.setProperty("class", "table-action")
                    btn_open.setFlat(True)
                    btn_open.setIconSize(QSize(16, 16))
                    btn_open.setFixedSize(28, 28)
                    btn_open.clicked.connect(functools.partial(self.view_invoice_payments, invoice_id, cust_name, prod_name))
                    h.addWidget(btn_open)
                    
                    # View invoice button
                    btn_view = QPushButton()
                    btn_view.setIcon(icon("reports.svg"))
                    btn_view.setToolTip("عرض الفاتورة")
                    btn_view.setProperty("class", "table-action")
                    btn_view.setFlat(True)
                    btn_view.setIconSize(QSize(16, 16))
                    btn_view.setFixedSize(28, 28)
                    btn_view.clicked.connect(functools.partial(self.show_invoice_details, invoice_id))
                    h.addWidget(btn_view)
                    
                    h.addStretch()
                    table.setCellWidget(row_index, 9, w)
                    
                    # Highlight overdue installments
                    if next_due and QDate.fromString(next_due, "yyyy-MM-dd") < QDate.currentDate() and remaining > 0:
                        for col in range(table.columnCount()):
                            if table.item(row_index, col):
                                table.item(row_index, col).setBackground(QColor(255, 200, 200))
                    
                    row_index += 1
                    
                except Exception as e:
                    print(f"Error processing installment row: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in refresh_installments: {e}")
            import traceback
            traceback.print_exc()

        # 2) Orphan installments (no invoice_id): show individually as before
        orphan_query = f"""
            SELECT i.id,
                   c.id as customer_id,
                   c.name,
                   p.name,
                   i.due_date,
                   i.amount,
                   IFNULL(i.paid, 0) as paid
            FROM installments i
            LEFT JOIN customers c ON i.customer_id = c.id
            LEFT JOIN products p ON i.product_id = p.id
            {where} AND i.invoice_id IS NULL
            ORDER BY i.due_date ASC
        """
        orphan_rows = Database().fetch_all(orphan_query, tuple(params))
        for row in orphan_rows:
            iid = row[0]
            cust_id = row[1]
            cust_name = row[2] or ""
            prod_name = row[3] or ""
            due_date = row[4] or ""
            amount = float(row[5] or 0)
            paid = float(row[6] or 0)
            remaining = amount - paid

            table.insertRow(row_index)
            table.setItem(row_index, 0, QTableWidgetItem(str(iid)))
            table.setItem(row_index, 1, QTableWidgetItem(cust_name))
            table.setItem(row_index, 2, QTableWidgetItem(prod_name))
            table.setItem(row_index, 3, QTableWidgetItem(due_date))
            table.setItem(row_index, 4, QTableWidgetItem(f"{amount:,.2f} ج.م"))
            table.setItem(row_index, 5, QTableWidgetItem(f"{paid:,.2f} ج.م"))
            rem2 = QTableWidgetItem(f"{remaining:,.2f} ج.م")
            rem2.setForeground(QColor("#388e3c") if remaining <= 0 else QColor("#d32f2f"))
            table.setItem(row_index, 6, rem2)
            table.setItem(row_index, 7, QTableWidgetItem(""))
            status2 = QTableWidgetItem("مسدد" if remaining <= 0 else "غير مسدد")
            status2.setForeground(QColor("#388e3c") if remaining <= 0 else QColor("#d32f2f"))
            table.setItem(row_index, 8, status2)

            w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0); h.setSpacing(6)
            btn_cust = QPushButton(); btn_cust.setIcon(icon("customers.svg")); btn_cust.setToolTip("تفاصيل العميل")
            btn_cust.setProperty("class","table-action"); btn_cust.setFlat(True); btn_cust.setIconSize(QSize(18,18)); btn_cust.setFixedSize(30,30)
            btn_cust.clicked.connect(functools.partial(self.show_customer_details, cust_id)); h.addWidget(btn_cust)
            if remaining > 0:
                btn_pay = QPushButton(); btn_pay.setIcon(icon("payments.svg")); btn_pay.setToolTip("تسديد القسط")
                btn_pay.setProperty("class","table-action"); btn_pay.setFlat(True); btn_pay.setIconSize(QSize(18,18)); btn_pay.setFixedSize(30,30)
                btn_pay.clicked.connect(functools.partial(self.open_pay_dialog, iid)); h.addWidget(btn_pay)
            table.setCellWidget(row_index, 9, w)

            if due_date and QDate.fromString(due_date, "yyyy-MM-dd") < QDate.currentDate() and remaining > 0:
                for col in range(table.columnCount()):
                    if table.item(row_index, col):
                        table.item(row_index, col).setBackground(QColor(255, 200, 200))
            row_index += 1

        table.resizeRowsToContents()

    def view_invoice_payments(self, invoice_id, customer_name, product_name):
        """Open payments dialog for the selected invoice"""
        from payments_dialog import PaymentsDialog
        dlg = PaymentsDialog(invoice_id, customer_name, product_name, self)
        dlg.exec()
        # Refresh invoices to show updated payment status
        self.refresh_invoices()
        self.refresh_alerts()
        self.refresh_dashboard_cards()

    def show_invoice_details(self, invoice_id):
        """Show invoice details in a dialog with payment information"""
        try:
            # Fetch invoice details with customer and product info
            rows = Database().fetch_all("""
                SELECT i.*, c.name as customer_name, p.name as product_name,
                       c.phone as customer_phone
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN products p ON i.product_id = p.id
                WHERE i.id = ?
            """, (invoice_id,))
            
            if not rows:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على الفاتورة")
                return
                
            invoice = dict(rows[0])
            
            # Show payments dialog directly
            self.view_invoice_payments(
                invoice_id,
                invoice.get('customer_name', ''),
                invoice.get('product_name', '')
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "خطأ", 
                f"حدث خطأ أثناء تحميل تفاصيل الفاتورة: {str(e)}"
            )

    def refresh_alerts(self):
        try:
            table = self.table_alerts
            table.setRowCount(0)
            
            # First, check if there are any installments in the database
            check_installments = "SELECT COUNT(*) as count FROM installments"
            installments_result = Database().fetch_all(check_installments)
            installments_count = installments_result[0][0] if installments_result and len(installments_result) > 0 else 0
            print(f"Total installments in database: {installments_count}")
            
            # Check for any overdue installments without the customer join
            check_overdue = """
                SELECT COUNT(*) as count 
                FROM installments 
                WHERE IFNULL(paid, 0) < amount 
                AND date(due_date) < date('now')
            """
            overdue_result = Database().fetch_all(check_overdue)
            overdue_count = overdue_result[0][0] if overdue_result and len(overdue_result) > 0 else 0
            print(f"Overdue installments (without customer check): {overdue_count}")
            
            # Check for any installments with invalid customer IDs
            check_customers = """
                SELECT COUNT(*) as count 
                FROM installments i
                LEFT JOIN customers c ON i.customer_id = c.id
                WHERE c.id IS NULL
            """
            invalid_customers_result = Database().fetch_all(check_customers)
            invalid_customers = invalid_customers_result[0][0] if invalid_customers_result and len(invalid_customers_result) > 0 else 0
            print(f"Installments with invalid customer IDs: {invalid_customers}")
            
            # If no installments found, show a message and return
            if installments_count == 0:
                print("No installments found in the database.")
                table.setRowCount(1)
                no_data = QTableWidgetItem("لا توجد أقساط في قاعدة البيانات")
                no_data.setTextAlignment(Qt.AlignCenter)
                table.setItem(0, 0, no_data)
                table.setSpan(0, 0, 1, 3)
                return
            
            # Get a sample of installments to check the data
            sample_query = """
                SELECT 
                    i.id,
                    i.due_date,
                    i.amount,
                    IFNULL(i.paid, 0) as paid,
                    i.customer_id,
                    c.name as customer_name
                FROM installments i
                LEFT JOIN customers c ON i.customer_id = c.id
                ORDER BY i.due_date DESC
                LIMIT 5
            """
            sample_data = Database().fetch_all(sample_query)
            print("\nSample of recent installments:")
            for row in sample_data:
                print(f"ID: {row[0]}, Due: {row[1]}, Amount: {row[2]}, Paid: {row[3]}, Customer ID: {row[4]}, Name: {row[5]}")
            
            # Modified query to show installments with or without customer data
            query = '''
                SELECT 
                    i.id, 
                    COALESCE(p.name, 'منتج غير معروف') as product_name,
                    i.due_date, 
                    i.amount, 
                    IFNULL(i.paid, 0) as paid, 
                    COALESCE(c.name, 'معلومات إضافية مطلوبة') as customer_name,
                    (i.amount - IFNULL(i.paid, 0)) as remaining,
                    i.customer_id,
                    i.product_id  -- Using product_id as additional reference
                FROM installments i
                LEFT JOIN products p ON i.product_id = p.id
                LEFT JOIN customers c ON i.customer_id = c.id
                WHERE IFNULL(i.paid, 0) < i.amount 
                  AND date(i.due_date) < date('now')
                ORDER BY i.due_date ASC
                LIMIT 50
            '''
            print("\nExecuting main query...")
            
            # Execute the query
            rows = Database().fetch_all(query)
            print(f"Number of overdue installments found: {len(rows) if rows else 0}")
            
            # If no rows found, show a message
            if not rows:
                table.setRowCount(1)
                no_data = QTableWidgetItem("لا توجد أقساط متأخرة")
                no_data.setTextAlignment(Qt.AlignCenter)
                table.setItem(0, 0, no_data)
                table.setSpan(0, 0, 1, 3)
                return
            
            if not rows:
                return
                
            # Configure table properties
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.setSelectionMode(QTableWidget.SingleSelection)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            # Apply style to match customers page
            table.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    gridline-color: #e0e0e0;
                    font-size: 13px;
                    selection-background-color: #e3f2fd;
                    selection-color: #0d47a1;
                    outline: 0;
                }
                QTableWidget::item {
                    padding: 8px 12px;
                    border: none;
                    border-right: 1px solid #e0e0e0;
                    border-bottom: 1px solid #e0e0e0;
                }
                QTableWidget::item:selected {
                    background: #e3f2fd;
                    color: #0d47a1;
                }
                QHeaderView::section {
                    background-color: #f5f5f5;
                    color: #424242;
                    padding: 12px;
                    font-weight: 600;
                    border: none;
                    border-right: 1px solid #e0e0e0;
                    border-bottom: 2px solid #e0e0e0;
                }
                QHeaderView::section:last {
                    border-right: none;
                }
                QTableWidget::item:first {
                    border-left: 1px solid #e0e0e0;
                }
            """)
            
            # Set up columns with proper widths and headers
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["اسم العميل", "المنتج", "المبلغ", "تاريخ الاستحقاق"])
            
            # Set header properties
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)  # Customer name column
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Product column
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Amount column
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Date column
            header.setDefaultAlignment(Qt.AlignCenter)
            
            # Set column widths
            table.setColumnWidth(2, 150)  # Fixed width for amount column
            table.setColumnWidth(3, 150)  # Fixed width for date column
            
            # Set row height and alignment
            table.verticalHeader().setDefaultSectionSize(50)
            table.verticalHeader().setVisible(False)  # Hide row numbers
            
            for r, row in enumerate(rows):
                try:
                    # Extract data from the row based on the SQL query structure
                    inst_id = row[0]  # i.id
                    prod_name = row[1]  # product_name
                    due_date = row[2]   # i.due_date
                    amount = float(row[3] or 0)  # i.amount
                    paid = float(row[4] or 0)    # i.paid
                    cust_name = row[5] or "غير معروف"  # customer_name
                    remaining = float(row[6] or 0)  # remaining amount
                    customer_id = row[7]  # i.customer_id
                    product_id = row[8]   # i.product_id
                    
                    # Format date if it exists
                    if due_date:
                        try:
                            if isinstance(due_date, str):
                                due_date = QDate.fromString(due_date, 'yyyy-MM-dd').toString('yyyy/MM/dd')
                            else:
                                due_date = due_date.toString('yyyy/MM/dd')
                        except Exception as e:
                            print(f"Error formatting date: {e}")
                            due_date = "تاريخ غير صالح"
                            pass
                    
                    # Add a new row to the table
                    table.insertRow(r)
                    
                    # Set row height
                    table.setRowHeight(r, 45)
                    
                    # Column 0: Customer Name (centered)
                    customer_item = QTableWidgetItem(cust_name or "غير معروف")
                    customer_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 0, customer_item)
                    
                    # Column 1: Product Name (centered)
                    product_item = QTableWidgetItem(prod_name or "غير محدد")
                    product_item.setTextAlignment(Qt.AlignCenter)
                    product_item.setData(Qt.UserRole, inst_id)
                    table.setItem(r, 1, product_item)
                    
                    # Column 2: Remaining Amount (centered, in red)
                    amount_item = QTableWidgetItem(f"{remaining:,.2f} ج.م")
                    amount_item.setTextAlignment(Qt.AlignCenter)
                    amount_item.setForeground(QColor(200, 0, 0))  # Red text for overdue amount
                    table.setItem(r, 2, amount_item)
                    
                    # Column 3: Due Date (centered, in red)
                    due_date_item = QTableWidgetItem(due_date)
                    due_date_item.setTextAlignment(Qt.AlignCenter)
                    due_date_item.setForeground(QColor(200, 0, 0))  # Red text for overdue date
                    table.setItem(r, 3, due_date_item)
                    
                    # Make all cells non-editable
                    for col in range(4):
                        item = table.item(r, col)
                        if item:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                
                except Exception as e:
                    print(f"Error processing row {r}: {str(e)}")
                    continue
            
            # Resize rows to fit content
            table.resizeRowsToContents()
            
            # Force a style update
            table.style().unpolish(table)
            table.style().polish(table)
            table.viewport().update()  # Fixed update() call
            
        except Exception as e:
            print(f"Error in refresh_alerts: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث قائمة التنبيهات: {str(e)}")

    def refresh_dashboard_cards(self):
        area = self.findChild(QWidget,"cardsArea")
        try:
            layout = area.layout()
            for i in reversed(range(layout.count())):
                w = layout.itemAt(i).widget();
                if w: w.setParent(None)
        except Exception:
            pass
        from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
        customers_count = Database().fetch_all("SELECT COUNT(*) FROM customers")[0][0]
        products_count = Database().fetch_all("SELECT COUNT(*) FROM products")[0][0]
        total_due = Database().fetch_all("SELECT IFNULL(SUM(amount-IFNULL(paid,0)),0) FROM installments WHERE IFNULL(paid,0) < amount")[0][0]
        due_this_month = Database().fetch_all(
            """
            SELECT IFNULL(SUM(amount-IFNULL(paid,0)),0)
            FROM installments
            WHERE IFNULL(paid,0) < amount
              AND strftime('%Y-%m', due_date) = strftime('%Y-%m', 'now')
            """
        )[0][0]
        active_installments = Database().fetch_all("SELECT COUNT(*) FROM installments WHERE IFNULL(paid,0) < amount")[0][0]
        def make_card(title,value):
            f = QFrame(); f.setMinimumSize(220,120); f.setStyleSheet("background:#fff;border-radius:12px;"); v = QVBoxLayout(f)
            lblVal = QLabel(str(value)); lblVal.setAlignment(Qt.AlignCenter); lblVal.setStyleSheet("font-size:20px;font-weight:700;"); lblT = QLabel(title); lblT.setAlignment(Qt.AlignCenter); v.addWidget(lblVal); v.addWidget(lblT); return f
        layout.addWidget(make_card("العملاء",customers_count))
        layout.addWidget(make_card("المنتجات",products_count))
        layout.addWidget(make_card("الأقساط الجارية",active_installments))
        layout.addWidget(make_card("المستحق هذا الشهر", f"{float(due_this_month):,.2f} ج.م"))
        layout.addWidget(make_card("إجمالي المتبقي", f"{float(total_due):,.2f} ج.م"))

    def refresh_reports_table(self):
        table = self.findChild(QWidget,"table_reports"); table.setRowCount(0)
        rows = [("إجمالي العملاء", str(Database().fetch_all("SELECT COUNT(*) FROM customers")[0][0]), ""),
                ("إجمالي المنتجات", str(Database().fetch_all("SELECT COUNT(*) FROM products")[0][0]), ""),
                ("أقساط مستحقة", str(Database().fetch_all("SELECT IFNULL(SUM(amount-paid),0) FROM installments WHERE IFNULL(paid,0) < amount")[0][0]), "")]
        for r,row in enumerate(rows):
            table.insertRow(r); table.setItem(r,0,QTableWidgetItem(row[0])); table.setItem(r,1,QTableWidgetItem(row[1])); table.setItem(r,2,QTableWidgetItem(row[2]))
        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def schedule_backup_if_needed(self):
        try:
            from PySide6.QtCore import QTimer
            cfg = self.config.get('backup', {})
            interval_code = cfg.get('interval', 'manual')
            if interval_code == 'manual':
                return
            # map interval to milliseconds (approx)
            ms_map = {
                'daily': 24*60*60*1000,
                'weekly': 7*24*60*60*1000,
                'monthly': 30*24*60*60*1000
            }
            msec = ms_map.get(interval_code)
            if not msec:
                return
            self._backup_timer = QTimer(self)
            self._backup_timer.setInterval(msec)
            self._backup_timer.timeout.connect(self.backup_database)
            self._backup_timer.start()
        except Exception:
            pass

    def export_reports_pdf(self):
        try:
            from PySide6.QtPrintSupport import QPrinter
            from PySide6.QtGui import QTextDocument
            doc = QTextDocument()
            html = [
                "<h2 style='text-align:center'>تقرير المختصر</h2>",
            ]
            customers_count = Database().fetch_all("SELECT COUNT(*) FROM customers")[0][0]
            products_count = Database().fetch_all("SELECT COUNT(*) FROM products")[0][0]
            total_due = Database().fetch_all("SELECT IFNULL(SUM(amount-IFNULL(paid,0)),0) FROM installments WHERE IFNULL(paid,0) < amount")[0][0]
            due_this_month = Database().fetch_all("""
                SELECT IFNULL(SUM(amount-IFNULL(paid,0)),0)
                FROM installments
                WHERE IFNULL(paid,0) < amount AND strftime('%Y-%m', due_date)=strftime('%Y-%m','now')
            """)[0][0]
            html.append(f"<p>العملاء: {customers_count}</p>")
            html.append(f"<p>المنتجات: {products_count}</p>")
            html.append(f"<p>الأقساط الجارية: {Database().fetch_all('SELECT COUNT(*) FROM installments WHERE IFNULL(paid,0) < amount')[0][0]}</p>")
            html.append(f"<p>المستحق هذا الشهر: {float(due_this_month):,.2f} ج.م</p>")
            html.append(f"<p>إجمالي المتبقي: {float(total_due):,.2f} ج.م</p>")
            doc.setHtml("".join(html))
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(os.path.join(BASE_DIR, "report.pdf"))
            doc.print_(printer)
            QMessageBox.information(self, "تم", "تم تصدير التقرير إلى report.pdf")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر تصدير التقرير: {e}")

    def backup_database(self):
        try:
            import shutil
            # destination dir from settings
            backup_dir = self.config.get('backup',{}).get('dir', BASE_DIR)
            os.makedirs(backup_dir, exist_ok=True)
            src = os.path.join(BASE_DIR, 'installments.db')
            dst = os.path.join(backup_dir, f"installments_backup.db")
            shutil.copy2(src, dst)
            QMessageBox.information(self, "تم", f"تم إنشاء نسخة احتياطية في: {dst}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر إنشاء النسخة الاحتياطية: {e}")

    def choose_backup_dir(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            from PySide6.QtCore import QDir, QLibraryInfo, QLocale, QTranslator
            
            # Get the current directory or fallback to BASE_DIR
            current_dir = self.edit_backup_dir.text() if (self.edit_backup_dir and self.edit_backup_dir.text()) else BASE_DIR
            
            # Create a file dialog with native options
            dialog = QFileDialog(self)
            dialog.setWindowTitle("اختر مجلد النسخ الاحتياطي")
            dialog.setFileMode(QFileDialog.Directory)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
            dialog.setOption(QFileDialog.DontUseNativeDialog, False)  # Force native dialog
            dialog.setDirectory(QDir.toNativeSeparators(current_dir))
            
            # Set Arabic text for dialog buttons and labels
            dialog.setLabelText(QFileDialog.Accept, "موافق")
            dialog.setLabelText(QFileDialog.Reject, "إلغاء")
            dialog.setLabelText(QFileDialog.LookIn, "الانتقال إلى:")
            dialog.setLabelText(QFileDialog.FileName, "اسم المجلد:")
            dialog.setLabelText(QFileDialog.FileType, "نوع الملف:")
            
            # Show the dialog
            if dialog.exec() == QFileDialog.Accepted:
                selected_dirs = dialog.selectedFiles()
                if selected_dirs and self.edit_backup_dir:
                    self.edit_backup_dir.setText(selected_dirs[0])
                    
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر اختيار المجلد: {str(e)}")

    def restore_backup(self):
        try:
            from PySide6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getOpenFileName(self, "استيراد نسخة قاعدة البيانات", self.config.get('backup',{}).get('dir', BASE_DIR), "Database (*.db)")
            if not path:
                return
            import shutil
            dst = os.path.join(BASE_DIR, 'installments.db')
            shutil.copy2(path, dst)
            QMessageBox.information(self, "تم", "تم استيراد قاعدة البيانات بنجاح. أعد تشغيل التطبيق.")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر الاستيراد: {e}")

    # CSV export removed per request

    def delete_invoice(self, invoice_id):
        """Delete an invoice after confirmation"""
        try:
            # Get invoice details for confirmation message
            invoice_rows = Database().fetch_all(
                """
                SELECT i.id, c.name, p.name, i.total_amount, i.quantity, i.product_id
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN products p ON i.product_id = p.id
                WHERE i.id = ?
                """,
                (invoice_id,)
            )
            
            if not invoice_rows:
                QMessageBox.warning(self, "خطأ", "تعذر العثور على الفاتورة المحددة.")
                return
                
            invoice = invoice_rows[0]  # Get first row from results
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                'تأكيد الحذف',
                f'هل أنت متأكد من حذف الفاتورة رقم {invoice[0]} للعميل {invoice[1]} بقيمة {invoice[3]:,.2f} ج.م؟\n\n' 
                'سيتم حذف جميع المدفوعات المرتبطة بهذه الفاتورة أيضاً.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # First, delete related payments
                Database().execute("DELETE FROM payments WHERE invoice_id = ?", (invoice_id,))
                
                # Then delete the invoice
                Database().execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
                
                # Return the product quantity to stock
                if invoice[4] and invoice[5]:  # if quantity and product_id exist
                    Database().execute(
                        "UPDATE products SET stock = stock + ? WHERE id = ?",
                        (invoice[4], invoice[5])
                    )
                
                # Refresh UI
                self.refresh_invoices()
                self.refresh_dashboard_cards()
                self.refresh_reports_table()
                self.refresh_alerts()
                self.refresh_products()
                
                QMessageBox.information(self, "تم الحذف", "تم حذف الفاتورة بنجاح.")
                        
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء معالجة طلب الحذف:\n{str(e)}"
            )

    def refresh_invoices(self):
        try:
            table = self.table_invoices
            table.setRowCount(0)
            params = []
            where = ""
            if self.search_invoices and self.search_invoices.text().strip():
                term = f"%{self.search_invoices.text().strip()}%"
                where = " WHERE (c.name LIKE ? OR p.name LIKE ?)"
                params.extend([term, term])
            
            # Get the invoice data with customer and product names (including ID but not displaying it)
            query = """
                SELECT 
                    i.id,
                    c.name as customer_name, 
                    p.name as product_name, 
                    i.quantity, 
                    i.total_amount,
                    i.upfront_paid, 
                    i.installment_count,
                    i.start_date,
                    i.invoice_date,
                    i.created_at
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                LEFT JOIN products p ON i.product_id = p.id
                %s
                ORDER BY i.id DESC
            """ % where
            
            rows = Database().fetch_all(query, tuple(params) if params else ())
            
            # Set column headers (without ID)
            headers = [
                "العميل", 
                "المنتج", 
                "الكمية", 
                "الإجمالي", 
                "المدفوع مقدماً", 
                "عدد الأقساط", 
                "تاريخ بداية التقسيط", 
                "تاريخ الفاتورة", 
                "المتبقي", 
                "العمليات"
            ]
            
            # First set the column count and headers
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            
            # Then set column widths
            table.setColumnWidth(0, 150)  # Customer
            table.setColumnWidth(1, 150)  # Product
            table.setColumnWidth(2, 80)   # Quantity
            table.setColumnWidth(3, 100)  # Total
            table.setColumnWidth(4, 100)  # Upfront paid
            table.setColumnWidth(5, 80)   # Installments count
            table.setColumnWidth(6, 120)  # Start date
            table.setColumnWidth(7, 120)  # Invoice date
            table.setColumnWidth(8, 100)  # Remaining
            table.setColumnWidth(9, 300)  # Operations (wider to fit all buttons)
            
            # Set alignment and styling for the table
            table.setStyleSheet("""
                QTableWidget {
                    gridline-color: #e0e0e0;
                    font-size: 15px;  /* Increased base font size */
                    selection-background-color: #e3f2fd;
                }
                QTableWidget::item { 
                    text-align: center;
                    padding: 6px;
                }
                /* Style for operations column buttons (smaller font) */
                QTableWidget QPushButton {
                    font-size: 13px;
                }
                QHeaderView::section {
                    background-color: #f5f5f5;
                    padding: 8px;
                    border: none;
                    border-right: 1px solid #e0e0e0;
                    border-bottom: 2px solid #e0e0e0;
                    font-weight: bold;
                }
                QTableWidget::item:selected {
                    background-color: #e3f2fd;
                    color: #000000;
                }
            """)
            
            for r, row in enumerate(rows):
                try:
                    # Extract values from the row
                    invoice_id = row[0]  # ID is at index 0
                    total_amount = float(row[4] or 0)  # Total amount is at index 4
                    upfront_paid = float(row[5] or 0)  # Upfront paid is at index 5
                    
                    # Get all payments for this invoice
                    payments_result = Database().fetch_all(
                        """
                        SELECT COALESCE(SUM(amount), 0) 
                        FROM payments 
                        WHERE invoice_id = ?
                        """, 
                        (invoice_id,)
                    )
                    
                    # Get the total payments sum
                    total_paid = float(payments_result[0][0] or 0) if payments_result else 0.0
                    
                    # Calculate remaining amount (total_amount - total_paid)
                    remaining = max(0, total_amount - total_paid)
                    
                    # Debug print to verify calculations
                    print(f"Invoice {invoice_id}: Total={total_amount}, Upfront={upfront_paid}, Paid={total_paid}, Remaining={remaining}")
                    
                    # Add new row to table
                    table.insertRow(r)
                    
                    # Fill in the row data and center align all cells
                    # The row data contains: [id, customer_name, product_name, quantity, total_amount, upfront_paid, installment_count, start_date, invoice_date]
                    
                    # Customer name (index 1 in row data)
                    customer_item = QTableWidgetItem(str(row[1]) if row[1] is not None else "")
                    customer_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 0, customer_item)
                    
                    # Product name (index 2 in row data)
                    product_item = QTableWidgetItem(str(row[2]) if row[2] is not None else "")
                    product_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 1, product_item)
                    
                    # Quantity (index 3 in row data)
                    quantity_item = QTableWidgetItem(str(row[3]) if row[3] is not None else "")
                    quantity_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 2, quantity_item)
                    
                    # Total amount (index 4 in row data)
                    total_amount_val = float(row[4] or 0)
                    total_item = QTableWidgetItem(f"{total_amount_val:,.2f} ج.م")
                    total_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 3, total_item)
                    
                    # Upfront paid (index 5 in row data)
                    upfront_paid_val = float(row[5] or 0)
                    upfront_item = QTableWidgetItem(f"{upfront_paid_val:,.2f} ج.م")
                    upfront_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 4, upfront_item)
                    
                    # Installment count (index 6 in row data)
                    installments_item = QTableWidgetItem(str(row[6]) if row[6] is not None else "0")
                    installments_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 5, installments_item)
                    
                    # Start date (index 7 in row data)
                    start_date = row[7] if row[7] else ""
                    start_date_item = QTableWidgetItem(str(start_date))
                    start_date_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 6, start_date_item)
                    
                    # Invoice date (index 8 in row data)
                    inv_date = row[8] if row[8] else ""
                    inv_date_item = QTableWidgetItem(str(inv_date))
                    inv_date_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 7, inv_date_item)
                    
                    # Remaining amount (calculated)
                    remaining_item = QTableWidgetItem(f"{remaining:,.2f} ج.م")
                    remaining_item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(r, 8, remaining_item)
                    
                    # Debug information
                    print(f"Invoice ID: {invoice_id}, Total: {total_amount}, Upfront: {upfront_paid}, Paid: {total_paid}, Remaining: {remaining}")
                    
                    # Create action buttons container with smaller font
                    btn_widget = QWidget()
                    btn_widget.setObjectName(f"btn_widget_{invoice_id}")
                    btn_widget.setStyleSheet("""
                        QWidget {
                            background: transparent;
                            font-size: 13px;
                            margin: 0;
                            padding: 0;
                        }
                    """)
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.setContentsMargins(5, 2, 5, 2)
                    btn_layout.setSpacing(6)
                    btn_layout.setAlignment(Qt.AlignCenter)
                    
                    # Common button style with smaller font
                    button_style = """
                        QPushButton {
                            border: 1px solid #e0e0e0;
                            border-radius: 6px;
                            padding: 6px 8px;
                            min-width: 70px;
                            max-width: 70px;
                            min-height: 30px;
                            max-height: 30px;
                            font-size: 11px;
                            font-weight: bold;
                            margin: 1px;
                            text-align: center;
                        }
                        QPushButton:hover {
                            opacity: 0.95;
                            border: 1px solid #bdbdbd;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                        }
                        QPushButton:pressed {
                            position: relative;
                            top: 1px;
                        }
                        QPushButton:disabled {
                            opacity: 0.6;
                        }
                    """
                    
                    # View button
                    btn_view = QPushButton("عرض الفاتورة")
                    btn_view.setToolTip("عرض تفاصيل الفاتورة")
                    btn_view.setStyleSheet(button_style + """
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: 1px solid #388E3C;
                        }
                        QPushButton:hover {
                            background-color: #43A047;
                            border-color: #2E7D32;
                        }
                        QPushButton:pressed {
                            background-color: #388E3C;
                        }
                        QPushButton:disabled {
                            background-color: #A5D6A7;
                            border: 1px solid #81C784;
                        }
                    """)
                    btn_view.clicked.connect(lambda checked, iid=invoice_id: self.show_invoice_details(iid))
                    
                    # Payment button
                    btn_payment = QPushButton("تسديد دفعة")
                    btn_payment.setToolTip("تسديد دفعة للفاتورة")
                    btn_payment.setStyleSheet(button_style + """
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: 1px solid #1976D2;
                        }
                        QPushButton:hover {
                            background-color: #1976D2;
                            border-color: #1565C0;
                        }
                        QPushButton:pressed {
                            background-color: #1565C0;
                        }
                        QPushButton:disabled {
                            background-color: #90CAF9;
                            border: 1px solid #64B5F6;
                        }
                    """)
                    btn_payment.clicked.connect(lambda checked, iid=invoice_id, rem=remaining: self.open_add_payment_dialog(iid, rem))
                    
                    # Add delete button
                    btn_delete = QPushButton("حذف")
                    btn_delete.setToolTip("حذف الفاتورة")
                    btn_delete.setStyleSheet(button_style + """
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: 1px solid #d32f2f;
                        }
                        QPushButton:hover {
                            background-color: #d32f2f;
                            border-color: #b71c1c;
                        }
                        QPushButton:pressed {
                            background-color: #b71c1c;
                        }
                        QPushButton:disabled {
                            background-color: #ef9a9a;
                            border: 1px solid #ef9a9a;
                        }
                    """)
                    btn_delete.clicked.connect(lambda checked, iid=invoice_id: self.delete_invoice(iid))
                    
                    # Add buttons to layout with proper spacing
                    btn_layout.addWidget(btn_view)
                    btn_layout.addSpacing(4)  # Reduced spacing to fit all buttons
                    btn_layout.addWidget(btn_payment)
                    btn_layout.addSpacing(4)  # Reduced spacing to fit all buttons
                    btn_layout.addWidget(btn_delete)
                    btn_layout.addStretch()
                    
                    # Ensure the table has enough columns
                    if table.columnCount() <= 9:
                        table.setColumnCount(10)
                    
                    # Set the widget in the operations column (last column)
                    operations_col = 9  # 10th column (0-based index 9)
                    
                    # Make sure the column exists
                    if operations_col < table.columnCount():
                        table.setCellWidget(r, operations_col, btn_widget)
                    
                    # Set row height to accommodate buttons
                    table.setRowHeight(r, 50)
                    
                    # Make sure the row is properly added
                    if r >= table.rowCount():
                        table.insertRow(r)
            
                except Exception as e:
                    print(f"Error processing invoice row {r}: {str(e)}")
                    continue
                    
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحديث قائمة الفواتير: {str(e)}")
            print(f"Error in refresh_invoices: {str(e)}")
            
        # Adjust column widths to fit content
        table.resizeColumnsToContents()
        
        # Set column resize modes
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Customer
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Product
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Quantity
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Total
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Upfront paid
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Installment count
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Start date
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Invoice date
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Remaining
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Operations
        
        # Set minimum width for operations column to prevent button squishing
        table.setColumnWidth(9, 300)  # Set fixed width for operations column
        
        # Set default row height
        table.verticalHeader().setDefaultSectionSize(60)
        table.verticalHeader().setVisible(False)  # Hide row numbers

    # ---------------- actions ----------------
    def add_customer(self):
        dlg = CustomerDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["name"]:
                QMessageBox.warning(self,"تنبيه","الاسم مطلوب")
                return
            Database().execute("INSERT INTO customers (name,phone,note) VALUES (?,?,?)", (data["name"],data["phone"],data["note"]))
            self.refresh_customers(); self.refresh_dashboard_cards(); self.refresh_alerts(); self.refresh_reports_table()

    def edit_customer(self, cid):
        row = Database().fetch_all("SELECT name,phone,note FROM customers WHERE id=?", (cid,))
        if not row: 
            return
        old = {"name": row[0][0], "phone": row[0][1], "note": row[0][2]}
        dlg = CustomerDialog(self, "تعديل عميل", old)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            Database().execute(
                "UPDATE customers SET name=?, phone=?, note=? WHERE id=?", 
                (data["name"], data["phone"], data["note"], cid)
            )
            self.refresh_customers()
            self.refresh_installments()
            self.refresh_alerts()
            self.refresh_dashboard_cards()
            self.refresh_reports_table()

    def add_product(self):
        dlg = ProductDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            if not data["name"]:
                QMessageBox.warning(self,"تنبيه","الاسم مطلوب")
                return
            Database().execute("INSERT INTO products (name,price,stock) VALUES (?,?,?)", 
                             (data["name"], data["price"], data["stock"]))
            self.refresh_products()
            self.refresh_dashboard_cards()
            self.refresh_alerts()
            self.refresh_reports_table()

    def edit_product(self, pid):
        row = Database().fetch_all("SELECT name,price,stock FROM products WHERE id=?", (pid,))
        if not row: 
            return
        old = {"name": row[0][0], "price": row[0][1], "stock": row[0][2]}
        dlg = ProductDialog(self, "تعديل منتج", old)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            Database().execute("UPDATE products SET name=?,price=?,stock=? WHERE id=?", 
                             (data["name"], data["price"], data["stock"], pid))
            self.refresh_products()
            self.refresh_dashboard_cards()
            self.refresh_alerts()
            self.refresh_reports_table()

    def delete_customer(self, cid):
        try:
            # Get customer name for better error message
            customer = Database().fetch_all("SELECT name FROM customers WHERE id=?", (cid,))
            if not customer:
                QMessageBox.warning(self, "خطأ", "العميل غير موجود")
                return
                
            customer_name = customer[0][0]
                
            # Check if customer has any invoices first
            invoice_count = Database().fetch_all(
                "SELECT COUNT(*) as count FROM invoices WHERE customer_id=?", (cid,)
            )
            if invoice_count and invoice_count[0][0] > 0:
                QMessageBox.warning(
                    self,
                    "خطأ",
                    f"لا يمكن حذف العميل '{customer_name}' لأنه لديه فواتير مرتبطة.\nالرجاء حذف الفواتير أولاً."
                )
                return
                
            reply = QMessageBox.question(
                self,
                "تأكيد الحذف",
                f"هل أنت متأكد من حذف العميل '{customer_name}'؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                Database().execute("DELETE FROM customers WHERE id=?", (cid,))
                self.refresh_customers()
                self.refresh_installments()
                self.refresh_alerts()
                self.refresh_dashboard_cards()
                self.refresh_reports_table()
                QMessageBox.information(self, "تم", f"تم حذف العميل '{customer_name}' بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف العميل: {str(e)}\nالرجاء المحاولة مرة أخرى.")

    def delete_product(self, pid):
        try:
            # Get product name for better error message
            product = Database().fetch_all("SELECT name FROM products WHERE id=?", (pid,))
            if not product:
                QMessageBox.warning(self, "خطأ", "المنتج غير موجود")
                return
                
            product_name = product[0][0]
                
            # Check if product has any invoices first
            invoice_count = Database().fetch_all(
                "SELECT COUNT(*) as count FROM invoices WHERE product_id=?", (pid,)
            )
            if invoice_count and invoice_count[0][0] > 0:
                QMessageBox.warning(
                    self,
                    "خطأ",
                    f"لا يمكن حذف المنتج '{product_name}' لأنه مستخدم في فواتير.\nالرجاء حذف الفواتير أولاً."
                )
                return
                
            reply = QMessageBox.question(
                self,
                "تأكيد الحذف",
                f"هل أنت متأكد من حذف المنتج '{product_name}'؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                Database().execute("DELETE FROM products WHERE id=?", (pid,))
                self.refresh_products()
                self.refresh_installments()
                self.refresh_alerts()
                self.refresh_dashboard_cards()
                self.refresh_reports_table()
                QMessageBox.information(self, "تم", f"تم حذف المنتج '{product_name}' بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف المنتج: {str(e)}\nالرجاء المحاولة مرة أخرى.")
            
    def add_invoice(self):
        dlg = InvoiceDialog(self)
        if dlg.exec() == QDialog.Accepted:
            data = dlg.get_data()
            # stock check
            stock = Database().fetch_all("SELECT stock FROM products WHERE id=?", (data["product_id"],))
            if not stock or stock[0][0] < data["quantity"]:
                QMessageBox.warning(self,"تنبيه","لا توجد كمية كافية من المنتج")
                return
            # subtract stock
            Database().execute("UPDATE products SET stock = stock - ? WHERE id=?", 
                             (data["quantity"], data["product_id"]))
            # insert invoice with upfront payment and invoice date
            Database().execute(
                """INSERT INTO invoices 
                (customer_id, product_id, quantity, total_amount, upfront_paid, 
                 installment_count, installment_amount, start_date, invoice_date, created_at) 
                VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))""",
                (
                    data["customer_id"], 
                    data["product_id"], 
                    data["quantity"], 
                    data["total_amount"],
                    data["upfront_paid"],
                    data["months"], 
                    (data["total_amount"]-data["upfront_paid"])/data["months"] if data["months"] > 0 else 0, 
                    data["start_date"],
                    data["invoice_date"]
                )
            )
            # get last inserted invoice id
            invoice_id = Database().fetch_all("SELECT last_insert_rowid()")[0][0]
            # compute installments only if there's remaining amount after upfront payment
            remaining = max(0, data["total_amount"] - data["upfront_paid"])
            
            # Parse the invoice date for calculating installment due dates
            invoice_date = QDate.fromString(data["invoice_date"], "yyyy-MM-dd")
            
            # Only create installments if there's remaining amount and months > 0
            if remaining > 0 and data["months"] > 0:
                monthly = round(remaining / data["months"], 2)
                for m in range(data["months"]):
                    due_date = invoice_date.addMonths(m+1).toString("yyyy-MM-dd")
                    Database().execute(
                        """INSERT INTO installments 
                        (customer_id, product_id, due_date, amount, paid, invoice_id) 
                        VALUES (?,?,?,?,?,?)""",
                        (data["customer_id"], data["product_id"], due_date, monthly, 0, invoice_id)
                    )
                    
            # If there was an upfront payment, record it as a payment
            if data["upfront_paid"] > 0:
                Database().execute(
                    """INSERT INTO payments 
                    (invoice_id, payment_date, amount, notes) 
                    VALUES (?,?,?,?)""",
                    (invoice_id, QDate.currentDate().toString("yyyy-MM-dd"), 
                     float(data["upfront_paid"]), "دفعة مقدمة")
                )
            # refresh everything
            self.refresh_products()
            self.refresh_invoices()
            self.refresh_alerts()
            self.refresh_dashboard_cards()
            self.refresh_reports_table()
            QMessageBox.information(self,"نجح","تم إنشاء الفاتورة والأقساط بنجاح")
            # انتقل إلى صفحة الفواتير بعد الإضافة
            page = self.findChild(QWidget, "page_invoices")
            if page:
                self.switch_page(page, "الفواتير")

    def delete_installment(self, iid):
        try:
            if QMessageBox.question(
                self,
                "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا القسط؟",
                QMessageBox.Yes | QMessageBox.No
            ) == QMessageBox.Yes:
                Database().execute("DELETE FROM installments WHERE id=?", (iid,))
                self.refresh_alerts()
                self.refresh_dashboard_cards()
                self.refresh_reports_table()
                self.refresh_invoices()
                QMessageBox.information(self, "تم", "تم حذف القسط بنجاح")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف القسط: {str(e)}")

    def show_invoice_for_installment(self, invoice_id):
        if not invoice_id:
            QMessageBox.information(self, "معلومة", "هذا القسط غير مرتبط بفاتورة.")
            return
        rows = Database().fetch_all("SELECT id, customer_id, product_id, quantity, total_amount, upfront_paid, months, created_at FROM invoices WHERE id=?", (invoice_id,))
        if not rows:
            QMessageBox.information(self, "معلومة", "لم يتم العثور على الفاتورة.")
            return
        inv = rows[0]
        # Simple info dialog
        txt = f"فاتورة رقم: {inv[0]}\nالعميل: {Database().fetch_all('SELECT name FROM customers WHERE id=?', (inv[1],))[0][0]}\nالمنتج: {Database().fetch_all('SELECT name FROM products WHERE id=?', (inv[2],))[0][0]}\nالكمية: {inv[3]}\nالإجمالي: {inv[4]}\nالمدفوع مقدماً: {inv[5]}\nعدد الشهور: {inv[6]}\nتاريخ الإنشاء: {inv[7]}"
        QMessageBox.information(self, "تفاصيل الفاتورة", txt)

    def open_add_payment_dialog(self, invoice_id, remaining_amount):
        """Open dialog to add a new payment for an invoice"""
        from payments_dialog import AddPaymentDialog
        dlg = AddPaymentDialog(invoice_id, remaining_amount, self)
        if dlg.exec() == QDialog.Accepted:
            # Get payment data
            amount = dlg.get_amount()
            notes = dlg.get_notes()
            payment_date = dlg.get_payment_date()
            
            # Record the payment
            try:
                db = Database()
                
                # Start a transaction
                db.conn.execute('BEGIN TRANSACTION')
                
                # Get invoice details including upfront payment
                invoice_result = db.fetch_all(
                    "SELECT total_amount, upfront_paid FROM invoices WHERE id = ?",
                    (invoice_id,)
                )
                
                if not invoice_result:
                    raise Exception("الفاتورة غير موجودة")
                
                total_amount = float(invoice_result[0][0] or 0)
                upfront_paid = float(invoice_result[0][1] or 0)
                
                # Record the payment
                db.execute(
                    "INSERT INTO payments (invoice_id, amount, payment_date, notes) VALUES (?, ?, ?, ?)",
                    (invoice_id, amount, payment_date, notes)
                )
                
                # Update installment paid amounts - find the first unpaid installment
                unpaid_installment = db.fetch_all(
                    """
                    SELECT id, amount, COALESCE(paid, 0) as paid
                    FROM installments 
                    WHERE invoice_id = ? AND COALESCE(paid, 0) < amount
                    ORDER BY due_date ASC
                    LIMIT 1
                    """,
                    (invoice_id,)
                )
                
                if unpaid_installment and len(unpaid_installment) > 0:
                    installment_id, installment_amount, already_paid = unpaid_installment[0]
                    new_paid_amount = min(already_paid + amount, installment_amount)
                    
                    # Update the installment
                    db.execute(
                        "UPDATE installments SET paid = ? WHERE id = ?",
                        (new_paid_amount, installment_id)
                    )
                
                # Commit the transaction
                db.conn.commit()
                
                QMessageBox.information(self, "نجح", "تم تسجيل الدفعة بنجاح")
                
                # Force refresh all data
                self.refresh_invoices()
                self.refresh_alerts()
                self.refresh_dashboard_cards()
                self.refresh_installments()  # Refresh installments view as well
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"تعذر تسجيل الدفعة: {e}")

    def show_customer_details(self, customer_id: int):
        try:
            row = Database().fetch_all("SELECT name, phone, COALESCE(note, '') FROM customers WHERE id=?", (customer_id,))
            if not row:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على العميل")
                return
            name, phone, note = row[0][0], row[0][1] or "", row[0][2] or ""

            from payments_dialog import PaymentsDialog

            dlg = QDialog(self)
            dlg.setWindowTitle(f"تفاصيل العميل - {name}")
            dlg.setMinimumSize(800, 600)
            v = QVBoxLayout(dlg)

            info = QLabel(f"<b>الاسم:</b> {name} &nbsp;&nbsp; <b>الهاتف:</b> {phone}<br/><b>ملاحظات:</b> {note}")
            v.addWidget(info)

            tabs = QTabWidget()
            v.addWidget(tabs)

            # الفواتير
            w_invoices = QWidget(); l_inv = QVBoxLayout(w_invoices)
            tbl_inv = QTableWidget(); tbl_inv.setColumnCount(8)
            tbl_inv.setHorizontalHeaderLabels(["#","المنتج","الكمية","الإجمالي","المدفوع","المتبقي","تاريخ الإنشاء","إجراءات"]) 
            tbl_inv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            l_inv.addWidget(tbl_inv)

            inv_rows = Database().fetch_all(
                """
                SELECT i.id, p.name, i.quantity, i.total_amount, i.upfront_paid, i.created_at
                FROM invoices i LEFT JOIN products p ON i.product_id=p.id
                WHERE i.customer_id=? ORDER BY i.id DESC
                """, (customer_id,)
            )
            for r, inv in enumerate(inv_rows):
                invoice_id = inv[0]
                total_amount = float(inv[3] or 0)
                paid_sum = Database().fetch_all("SELECT IFNULL(SUM(amount),0) FROM payments WHERE invoice_id=?", (invoice_id,))[0][0]
                remaining = max(0.0, total_amount - float(paid_sum or 0))

                tbl_inv.insertRow(r)
                tbl_inv.setItem(r,0,QTableWidgetItem(str(invoice_id)))
                tbl_inv.setItem(r,1,QTableWidgetItem(str(inv[1] or "")))
                tbl_inv.setItem(r,2,QTableWidgetItem(str(inv[2] or 0)))
                tbl_inv.setItem(r,3,QTableWidgetItem(f"{total_amount:,.2f} ج.م"))
                tbl_inv.setItem(r,4,QTableWidgetItem(f"{float(paid_sum):,.2f} ج.م"))
                rem_item = QTableWidgetItem(f"{remaining:,.2f} ج.م")
                rem_item.setForeground(QColor("#388e3c") if remaining <= 0 else QColor("#d32f2f"))
                tbl_inv.setItem(r,5, rem_item)
                tbl_inv.setItem(r,6,QTableWidgetItem(str(inv[5] or "")))

                w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
                btn_add = QPushButton("إضافة دفعة"); btn_add.setProperty("class","table-action")
                btn_add.clicked.connect(lambda _, iid=invoice_id: PaymentsDialog(iid, name, str(inv[1] or ""), self).exec())
                h.addWidget(btn_add)
                btn_view = QPushButton("عرض السجل")
                btn_view.setProperty("class","table-action")
                btn_view.clicked.connect(lambda _, iid=invoice_id: PaymentsDialog(iid, name, str(inv[1] or ""), self).exec())
                h.addWidget(btn_view)
                tbl_inv.setCellWidget(r,7,w)

            tabs.addTab(w_invoices, "الفواتير")

            # الأقساط
            w_inst = QWidget(); l_ins = QVBoxLayout(w_inst)
            tbl_ins = QTableWidget(); tbl_ins.setColumnCount(7)
            tbl_ins.setHorizontalHeaderLabels(["#","المنتج","تاريخ الاستحقاق","المبلغ","المسدّد","المتبقي","رقم الفاتورة"]) 
            tbl_ins.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            l_ins.addWidget(tbl_ins)

            inst_rows = Database().fetch_all(
                """
                SELECT i.id, p.name, i.due_date, i.amount, IFNULL(i.paid,0) as paid, i.invoice_id
                FROM installments i LEFT JOIN products p ON i.product_id=p.id
                WHERE i.customer_id=? ORDER BY i.due_date ASC
                """, (customer_id,)
            )
            for r, it in enumerate(inst_rows):
                amt = float(it[3] or 0); pd = float(it[4] or 0); rem = amt - pd
                tbl_ins.insertRow(r)
                tbl_ins.setItem(r,0,QTableWidgetItem(str(it[0])))
                tbl_ins.setItem(r,1,QTableWidgetItem(str(it[1] or "")))
                tbl_ins.setItem(r,2,QTableWidgetItem(str(it[2] or "")))
                tbl_ins.setItem(r,3,QTableWidgetItem(f"{amt:,.2f} ج.م"))
                tbl_ins.setItem(r,4,QTableWidgetItem(f"{pd:,.2f} ج.م"))
                rem_item2 = QTableWidgetItem(f"{rem:,.2f} ج.م"); rem_item2.setForeground(QColor("#388e3c") if rem<=0 else QColor("#d32f2f"))
                tbl_ins.setItem(r,5, rem_item2)
                tbl_ins.setItem(r,6,QTableWidgetItem(str(it[5] or "")))

            tabs.addTab(w_inst, "الأقساط")

            # المدفوعات السابقة
            w_pay = QWidget(); l_pay = QVBoxLayout(w_pay)
            tbl_pay = QTableWidget(); tbl_pay.setColumnCount(4)
            tbl_pay.setHorizontalHeaderLabels(["#","تاريخ الدفعة","المبلغ","ملاحظات"]) 
            tbl_pay.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            l_pay.addWidget(tbl_pay)

            pay_rows = Database().fetch_all(
                """
                SELECT p.id, p.payment_date, p.amount, COALESCE(p.notes,'')
                FROM payments p
                INNER JOIN invoices i ON p.invoice_id = i.id
                WHERE i.customer_id = ?
                ORDER BY p.payment_date DESC, p.id DESC
                """, (customer_id,)
            )
            for r, pr in enumerate(pay_rows):
                tbl_pay.insertRow(r)
                tbl_pay.setItem(r,0,QTableWidgetItem(str(pr[0])))
                tbl_pay.setItem(r,1,QTableWidgetItem(str(pr[1] or "")))
                tbl_pay.setItem(r,2,QTableWidgetItem(f"{float(pr[2] or 0):,.2f} ج.م"))
                tbl_pay.setItem(r,3,QTableWidgetItem(str(pr[3] or "")))

            tabs.addTab(w_pay, "المدفوعات")

            dlg.exec()

        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"تعذر فتح تفاصيل العميل: {e}")

    def _on_installment_double(self, row, col):
        try:
            iid = int(self.table_installments.item(row,0).text()); self.open_pay_dialog(iid)
        except Exception:
            pass

    def logout(self):
        """تسجيل الخروج من التطبيق"""
        reply = QMessageBox.question(self, "تأكيد", "هل تريد إغلاق التطبيق؟", 
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()
            
    def prevent_maximization(self):
        """منع تكبير النافذة والحفاظ على الحجم المحدد"""
        # الحصول على أبعاد الشاشة الحالية
        screen = self.screen()
        screen_geometry = screen.geometry()
        
        # التأكد من أن النافذة ليست مكبرة
        if self.isMaximized():
            self.showNormal()
        
        # إعادة تعيين الحجم ليطابق أبعاد الشاشة
        self.resize(screen_geometry.width(), screen_geometry.height())
        
    def configure_form_layouts(self):
        """Configure form layout properties that couldn't be set in the UI file"""
        # Configure appearance form layout
        form_appearance = self.findChild(QFormLayout, "form_appearance")
        if form_appearance:
            form_appearance.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
            form_appearance.setRowWrapPolicy(QFormLayout.DontWrapRows)
            form_appearance.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
            form_appearance.setFormAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
            
        # Configure backup form layout
        form_backup = self.findChild(QFormLayout, "form_backup")
        if form_backup:
            form_backup.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
            form_backup.setRowWrapPolicy(QFormLayout.DontWrapRows)
            form_backup.setLabelAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
            form_backup.setFormAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)



# ---------------- main ----------------
def main():
    # تفعيل خيار OpenGL قبل إنشاء التطبيق
    from PySide6.QtCore import QCoreApplication
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv); app.setLayoutDirection(Qt.RightToLeft)
    try:
        with open(QSS_LIGHT, "r", encoding="utf-8") as f: app.setStyleSheet(f.read())
    except: pass
    win = MainApp();
    
    # الحصول على أبعاد الشاشة الرئيسية
    screen = app.primaryScreen()
    screen_geometry = screen.geometry()
    
    # تعيين حجم النافذة ليطابق أبعاد الشاشة بالضبط
    win.resize(screen_geometry.width(), screen_geometry.height())
    
    # تعيين موقع النافذة ليكون في أعلى يسار الشاشة
    win.move(screen_geometry.x(), screen_geometry.y())
    
    # عرض النافذة
    win.show()
    
    sys.exit(app.exec())

if __name__ == "__main__": main()
