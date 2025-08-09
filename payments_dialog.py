from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, 
                             QLabel, QMessageBox, QTextEdit, QDateEdit, QDoubleSpinBox,
                             QAbstractSpinBox, QTextDocument, QWidget, QSizePolicy)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QTextCursor, QTextFormat, QColor
from database import Database

def icon(name):
    return name  # This is a placeholder, replace with your actual icon function

class AddPaymentDialog(QDialog):
    def __init__(self, invoice_id, remaining, parent=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        self.remaining = remaining
        self.setWindowTitle("إضافة دفعة")
        self.setMinimumWidth(400)

        # Main layout
        layout = QVBoxLayout(self)
        
        # Form layout for input fields
        form_layout = QFormLayout()
        
        # Amount input
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setMaximum(remaining)
        self.amount_input.setMinimum(0.01)
        self.amount_input.setValue(min(remaining, 1000))  # Default to 1000 or remaining, whichever is smaller
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" د.ع")
        self.amount_input.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
        
        # Connect value changed to update remaining label
        self.amount_input.valueChanged.connect(self.update_remaining_label)
        
        # Remaining amount label
        self.lbl_remaining = QLabel(f"المبلغ المتبقي: {remaining:,.2f} د.ع")
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
        btn_ok = QPushButton("حفظ الدفعة")
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
        self.lbl_remaining.setText(f"المبلغ المتبقي: {remaining:,.2f} د.ع")
        
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


class PaymentsDialog(QDialog):
    def __init__(self, invoice_id, customer_name="", product_name="", parent=None):
        super().__init__(parent)
        self.invoice_id = invoice_id
        self.setWindowTitle(f"إدارة دفعات الفاتورة #{invoice_id}")
        self.resize(700, 500)
        self.setMinimumSize(600, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Invoice info
        info_group = QGroupBox("معلومات الفاتورة")
        info_layout = QFormLayout()
        
        self.lbl_customer = QLabel(customer_name)
        self.lbl_product = QLabel(product_name)
        
        info_layout.addRow("العميل:", self.lbl_customer)
        info_layout.addRow("المنتج:", self.lbl_product)
        info_group.setLayout(info_layout)
        
        # Payment summary
        summary_group = QGroupBox("ملخص المدفوعات")
        summary_layout = QHBoxLayout()
        
        self.lbl_total = QLabel("0.00 د.ع")
        self.lbl_paid = QLabel("0.00 د.ع")
        self.lbl_remaining = QLabel("0.00 د.ع")
        
        # Style labels
        for label in [self.lbl_total, self.lbl_paid, self.lbl_remaining]:
            label.setMinimumWidth(150)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")
        
        # Add to summary layout
        summary_layout.addWidget(QLabel("الإجمالي:"))
        summary_layout.addWidget(self.lbl_total)
        summary_layout.addWidget(QLabel("المدفوع:"))
        summary_layout.addWidget(self.lbl_paid)
        summary_layout.addWidget(QLabel("المتبقي:"))
        summary_layout.addWidget(self.lbl_remaining)
        summary_group.setLayout(summary_layout)
        
        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(4)
        self.payments_table.setHorizontalHeaderLabels(["#", "تاريخ الدفعة", "المبلغ", "ملاحظات"])
        self.payments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.payments_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)  # Stretch notes column
        self.payments_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.payments_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_add_payment = QPushButton("إضافة دفعة")
        self.btn_add_payment.setIcon(icon("add_payment.svg"))
        self.btn_delete_payment = QPushButton("حذف الدفعة المحددة")
        self.btn_delete_payment.setIcon(icon("delete.svg"))
        self.btn_print = QPushButton("طباعة السجل")
        self.btn_print.setIcon(icon("print.svg"))
        self.btn_close = QPushButton("إغلاق")
        self.btn_close.setIcon(icon("close.svg"))
        
        # Add buttons to layout
        btn_layout.addWidget(self.btn_add_payment)
        btn_layout.addWidget(self.btn_delete_payment)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_print)
        btn_layout.addWidget(self.btn_close)
        
        # Add widgets to main layout
        layout.addWidget(info_group)
        layout.addWidget(summary_group)
        layout.addWidget(QLabel("سجل المدفوعات:"))
        layout.addWidget(self.payments_table)
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.btn_add_payment.clicked.connect(self.add_payment)
        self.btn_delete_payment.clicked.connect(self.delete_payment)
        self.btn_print.clicked.connect(self.print_payments)
        self.btn_close.clicked.connect(self.accept)
        
        # Load data
        self.load_payments()
        self.update_summary()

    def load_payments(self):
        self.payments_table.setRowCount(0)
        db = Database()
        
        # Get payments with row numbers
        payments = db.fetch_all(
            """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY payment_date DESC, id DESC) as row_num,
                id,
                strftime('%Y-%m-%d %H:%M', payment_date) as payment_date,
                amount,
                COALESCE(notes, '') as notes
            FROM payments 
            WHERE invoice_id = ?
            ORDER BY payment_date DESC, id DESC
            """,
            (self.invoice_id,)
        )
        
        for row_data in payments:
            row = self.payments_table.rowCount()
            self.payments_table.insertRow(row)
            
            # Add items to table
            for col, value in enumerate(row_data[1:]):  # Skip row_num
                item = QTableWidgetItem(str(value) if col != 2 else f"{float(value):,.2f} د.ع")
                item.setData(Qt.UserRole, row_data[1])  # Store payment ID in first column
                
                # Right align amount
                if col == 2:  # Amount column
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                self.payments_table.setItem(row, col, item)
        
        # Resize columns to contents
        self.payments_table.resizeColumnsToContents()
        
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
        self.lbl_total.setText(f"{total:,.2f} د.ع")
        self.lbl_paid.setText(f"{paid:,.2f} د.ع")
        self.lbl_remaining.setText(f"{remaining:,.2f} د.ع")
        
        # Update colors based on status
        self.lbl_remaining.setStyleSheet(
            f"color: {'#d32f2f' if remaining > 0 else '#388e3c'}; "
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        self.lbl_paid.setStyleSheet("color: #388e3c; font-size: 14px; font-weight: bold; padding: 5px;")
        self.lbl_total.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px;")

    def add_payment(self):
        # Get remaining amount
        total = float(self.lbl_total.text().replace(" د.ع", "").replace(",", ""))
        paid = float(self.lbl_paid.text().replace(" د.ع", "").replace(",", ""))
        remaining = total - paid

        if remaining <= 0:
            QMessageBox.information(self, "تم الدفع بالكامل", "تم سداد كامل مبلغ الفاتورة")
            return

        dialog = AddPaymentDialog(self.invoice_id, remaining, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                db = Database()
                db.execute(
                    """
                    INSERT INTO payments (invoice_id, payment_date, amount, notes)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        self.invoice_id,
                        dialog.get_payment_date(),
                        dialog.get_amount(),
                        dialog.get_notes() or None
                    )
                )
                
                # Refresh data
                self.load_payments()
                self.update_summary()
                
                # Notify parent to refresh
                if hasattr(self.parent(), 'refresh_invoices'):
                    self.parent().refresh_invoices()
                    
                QMessageBox.information(self, "تم الحفظ", "تمت إضافة الدفعة بنجاح")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الدفعة: {str(e)}")
    
    def delete_payment(self):
        selected = self.payments_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "تحذير", "الرجاء تحديد دفعة للحذف")
            return
            
        # Get payment ID from first column
        payment_id = selected[0].data(Qt.UserRole)
        
        if not payment_id:
            QMessageBox.warning(self, "خطأ", "تعذر تحديد الدفعة المحددة")
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل أنت متأكد من حذف هذه الدفعة؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db = Database()
                db.execute("DELETE FROM payments WHERE id = ?", (payment_id,))
                
                # Refresh data
                self.load_payments()
                self.update_summary()
                
                # Notify parent to refresh
                if hasattr(self.parent(), 'refresh_invoices'):
                    self.parent().refresh_invoices()
                    
                QMessageBox.information(self, "تم الحذف", "تم حذف الدفعة بنجاح")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف الدفعة: {str(e)}")
    
    def print_payments(self):
        """Print payments report"""
        try:
            from PySide6.QtPrintSupport import QPrinter, QPrintDialog
            
            # Create printer and dialog
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.Accepted:
                # Create document with payment details
                doc = QTextDocument()
                cursor = QTextCursor(doc)
                
                # Add title
                title_format = cursor.charFormat()
                title_format.setFontPointSize(14)
                title_format.setFontWeight(75)  # Bold
                title_format.setAlignment(Qt.AlignCenter)
                
                cursor.setCharFormat(title_format)
                cursor.insertText(f"\nسجل المدفوعات - الفاتورة #{self.invoice_id}\n\n")
                
                # Add invoice info
                cursor.insertText(f"العميل: {self.lbl_customer.text()}\n")
                cursor.insertText(f"المنتج: {self.lbl_product.text()}\n\n")
                
                # Add summary
                cursor.insertText(f"إجمالي الفاتورة: {self.lbl_total.text()}\n")
                cursor.insertText(f"المبلغ المدفوع: {self.lbl_paid.text()}\n")
                cursor.insertText(f"المبلغ المتبقي: {self.lbl_remaining.text()}\n\n")
                
                # Add table header
                table_format = cursor.charFormat()
                table_format.setFontPointSize(10)
                cursor.setCharFormat(table_format)
                
                cursor.insertText("تفاصيل المدفوعات:\n")
                cursor.insertText("-" * 80 + "\n")
                cursor.insertText(f"{'#':<5} {'التاريخ':<20} {'المبلغ':<15} {'الملاحظات'}\\n")
                cursor.insertText("-" * 80 + "\\n")
                
                # Add payments
                for row in range(self.payments_table.rowCount()):
                    row_num = self.payments_table.item(row, 0).text()
                    date = self.payments_table.item(row, 1).text()
                    amount = self.payments_table.item(row, 2).text()
                    notes = self.payments_table.item(row, 3).text()
                    
                    cursor.insertText(f"{row_num:<5} {date:<20} {amount:<15} {notes}\\n")
                
                # Print the document
                doc.print_(printer)
                
        except ImportError:
            QMessageBox.warning(self, "تحذير", "لا يمكن فتح نافذة الطباعة")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الطباعة: {str(e)}")
