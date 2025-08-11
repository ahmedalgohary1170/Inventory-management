from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QFileDialog, QMessageBox, QHBoxLayout)
from PySide6.QtCore import Qt
import os

class DbPathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تحديد موقع قاعدة البيانات")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "مرحباً بك في برنامج إدارة المبيعات بالتقسيط.\n\n"
            "الرجاء تحديد موقع حفظ ملف قاعدة البيانات. يمكنك اختيار موقع جديد أو اختيار ملف موجود."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Path input
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("اختر مسار حفظ ملف قاعدة البيانات...")
        self.path_edit.setReadOnly(True)
        
        browse_btn = QPushButton("استعراض...")
        browse_btn.clicked.connect(self.browse_path)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # Buttons
        btn_box = QHBoxLayout()
        ok_btn = QPushButton("موافق")
        cancel_btn = QPushButton("إلغاء")
        
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(ok_btn)
        btn_box.addWidget(cancel_btn)
        
        layout.addLayout(btn_box)
        
        # Set focus to browse button
        browse_btn.setFocus()
    
    def browse_path(self):
        # Default to hidden directory in user's home with dot prefix
        default_dir = os.path.join(os.path.expanduser("~"), ".inventory_data")
        
        # Create hidden directory if it doesn't exist
        os.makedirs(default_dir, exist_ok=True, mode=0x1c0)  # 0x1c0 = 0700 in octalns to owner only
        
        # If path_edit has text, use its directory
        if self.path_edit.text():
            default_dir = os.path.dirname(self.path_edit.text())
        
        # Show file dialog to select or create database file
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "حفظ ملف قاعدة البيانات",
            os.path.join(default_dir, ".installments.db"),
            "قاعدة البيانات SQLite (*.db *.sqlite *.sqlite3);;كل الملفات (*)"
        )
        
        if file_path:
            # Ensure the directory exists and is hidden (on Windows)
            db_dir = os.path.dirname(file_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True, mode=0o700)
            
            # Hide the directory on Windows
            if os.name == 'nt':  # Windows
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(db_dir, 0x02)  # FILE_ATTRIBUTE_HIDDEN
                except Exception:
                    pass
            
            # Ensure the file has a .db extension
            if not file_path.lower().endswith(('.db', '.sqlite', '.sqlite3')):
                file_path += '.db'
            
            self.path_edit.setText(file_path)
    
    def get_db_path(self):
        return self.path_edit.text()
    
    @staticmethod
    def get_database_path(parent=None):
        dialog = DbPathDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog.get_db_path()
        return None
