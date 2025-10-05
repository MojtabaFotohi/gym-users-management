import sys
import sqlite3
from datetime import datetime, timedelta
from jdatetime import datetime as jdatetime, date
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QComboBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QMessageBox, QScrollArea, QSizePolicy, QHeaderView,
    QStyledItemDelegate, QStyleOptionViewItem, QStyle, QFrame
)
from PyQt5.QtCore import Qt, QDateTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QBrush, QPixmap

# Database setup
DB_NAME = 'gym_management.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            program_type TEXT NOT NULL,
            diet BOOLEAN NOT NULL,
            training BOOLEAN NOT NULL,
            coach BOOLEAN NOT NULL,
            registration_date TEXT NOT NULL,
            expiration_date TEXT NOT NULL,
            active BOOLEAN NOT NULL DEFAULT 1
        )
    ''')
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'active' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1')
    conn.commit()
    conn.close()

def add_user(name, phone, program_type, diet, training, coach, active=True):
    registration_date = datetime.now().isoformat()
    expiration_date = (datetime.now() + timedelta(days=30)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, phone, program_type, diet, training, coach, registration_date, expiration_date, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, phone, program_type, int(diet), int(training), int(coach), registration_date, expiration_date, int(active)))
    conn.commit()
    conn.close()

def update_user(user_id, name, phone, program_type, diet, training, coach, active):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT active FROM users WHERE id=?', (user_id,))
    result = cursor.fetchone()
    current_active = result[0] if result else 0
    
    if active and not current_active:
        new_expiration = (datetime.now() + timedelta(days=30)).isoformat()
        cursor.execute('''
            UPDATE users SET name=?, phone=?, program_type=?, diet=?, training=?, coach=?, active=?, expiration_date=?
            WHERE id=?
        ''', (name, phone, program_type, int(diet), int(training), int(coach), int(active), new_expiration, user_id))
    else:
        cursor.execute('''
            UPDATE users SET name=?, phone=?, program_type=?, diet=?, training=?, coach=?, active=?
            WHERE id=?
        ''', (name, phone, program_type, int(diet), int(training), int(coach), int(active), user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users WHERE active=1')
    active_users = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users WHERE active=0')
    inactive_users = cursor.fetchone()[0]
    conn.close()
    return total_users, active_users, inactive_users

def search_users(query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE name LIKE ? OR phone LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def renew_subscription(user_id):
    new_expiration = (datetime.now() + timedelta(days=30)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET expiration_date=?, active=1 WHERE id=?', (new_expiration, user_id))
    conn.commit()
    conn.close()

def is_subscription_active(expiration_date):
    exp_date = datetime.fromisoformat(expiration_date)
    return datetime.now() < exp_date

def to_jalali(iso_date):
    dt = datetime.fromisoformat(iso_date)
    jdt = jdatetime.fromgregorian(datetime=dt)
    return jdt.strftime('%Y/%m/%d')

def get_current_jalali_date_time():
    now = datetime.now()
    jnow = jdatetime.fromgregorian(datetime=now)
    persian_days = {
        'Saturday': 'شنبه',
        'Sunday': 'یکشنبه',
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه',
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنجشنبه',
        'Friday': 'جمعه'
    }
    weekday_eng = jnow.strftime('%A')
    weekday = persian_days.get(weekday_eng, weekday_eng)
    date_str = jnow.strftime('%Y/%m/%d')
    time_str = now.strftime('%H:%M:%S')
    return f"{weekday} - {date_str} - {time_str}"

class CheckBoxDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        value = index.data(Qt.DisplayRole)
        if value is not None:
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)
            
            checkbox_size = 32
            x = opt.rect.x() + (opt.rect.width() - checkbox_size) // 2
            y = opt.rect.y() + (opt.rect.height() - checkbox_size) // 2
            
            painter.save()
            if bool(value):
                painter.setPen(QColor("green"))
                painter.setFont(QFont("Arial", 28, QFont.Bold))
                painter.drawText(x, y + checkbox_size - 5, "✓")
            else:
                painter.setPen(QColor("red"))
                painter.setFont(QFont("Arial", 28, QFont.Bold))
                painter.drawText(x, y + checkbox_size - 5, "✗")
            painter.restore()

class UserProfileDialog(QDialog):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle(f"پروفایل: {user[1]}")
        self.setMinimumSize(800, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)

        form_widget = QWidget()
        form_widget.setLayoutDirection(Qt.RightToLeft)
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop)
        form_layout.setSpacing(25)

        self.name_edit = QLineEdit(user[1])
        self.name_edit.setFont(QFont("Arial", 26))
        self.name_edit.setMinimumHeight(55)
        self.name_edit.setAlignment(Qt.AlignRight)
        self.phone_edit = QLineEdit(user[2])
        self.phone_edit.setFont(QFont("Arial", 26))
        self.phone_edit.setMinimumHeight(55)
        self.phone_edit.setAlignment(Qt.AlignRight)
        self.program_type_combo = QComboBox()
        self.program_type_combo.addItems(['عادی', 'ویژه'])
        self.program_type_combo.setCurrentText('عادی' if user[3] == 'normal' else 'ویژه')
        self.program_type_combo.setFont(QFont("Arial", 26))
        self.program_type_combo.setMinimumHeight(55)
        self.program_type_combo.setLayoutDirection(Qt.RightToLeft)
        
        diet_container = QWidget()
        diet_container.setLayoutDirection(Qt.RightToLeft)
        diet_layout = QHBoxLayout(diet_container)
        diet_layout.setContentsMargins(0, 0, 0, 0)
        self.diet_check = QCheckBox()
        self.diet_check.setChecked(bool(user[4]))
        self.diet_check.setFont(QFont("Arial", 26))
        diet_layout.addWidget(self.diet_check)
        diet_layout.addStretch()
        
        training_container = QWidget()
        training_container.setLayoutDirection(Qt.RightToLeft)
        training_layout = QHBoxLayout(training_container)
        training_layout.setContentsMargins(0, 0, 0, 0)
        self.training_check = QCheckBox()
        self.training_check.setChecked(bool(user[5]))
        self.training_check.setFont(QFont("Arial", 26))
        training_layout.addWidget(self.training_check)
        training_layout.addStretch()
        
        coach_container = QWidget()
        coach_container.setLayoutDirection(Qt.RightToLeft)
        coach_layout = QHBoxLayout(coach_container)
        coach_layout.setContentsMargins(0, 0, 0, 0)
        self.coach_check = QCheckBox()
        self.coach_check.setChecked(bool(user[6]))
        self.coach_check.setFont(QFont("Arial", 26))
        coach_layout.addWidget(self.coach_check)
        coach_layout.addStretch()
        
        reg_date = to_jalali(user[7])
        exp_date = to_jalali(user[8])
        self.reg_label = QLabel(f"تاریخ ثبت‌نام: {reg_date}")
        self.reg_label.setFont(QFont("Arial", 26))
        self.reg_label.setAlignment(Qt.AlignRight)
        self.exp_label = QLabel(f"تاریخ انقضا: {exp_date}")
        self.exp_label.setFont(QFont("Arial", 26))
        self.exp_label.setAlignment(Qt.AlignRight)
        active_sub = is_subscription_active(user[8])
        self.status_label = QLabel("فعال" if active_sub else "منقضی")
        self.status_label.setFont(QFont("Arial", 26, QFont.Bold))
        self.status_label.setStyleSheet("color: green;" if active_sub else "color: red;")
        self.status_label.setAlignment(Qt.AlignRight)
        
        active_container = QWidget()
        active_container.setLayoutDirection(Qt.RightToLeft)
        active_layout = QHBoxLayout(active_container)
        active_layout.setContentsMargins(0, 0, 0, 0)
        self.active_check = QCheckBox("فعال")
        self.active_check.setChecked(bool(user[9]))
        self.active_check.setFont(QFont("Arial", 26))
        self.active_check.setLayoutDirection(Qt.RightToLeft)
        active_layout.addWidget(self.active_check)
        active_layout.addStretch()
        
        renew_container = QWidget()
        renew_container.setLayoutDirection(Qt.RightToLeft)
        renew_layout = QHBoxLayout(renew_container)
        renew_layout.setContentsMargins(0, 0, 0, 0)
        self.renew_check = QCheckBox("تمدید اشتراک (۳۰ روز)")
        self.renew_check.setEnabled(not active_sub)
        self.renew_check.setFont(QFont("Arial", 26))
        self.renew_check.setLayoutDirection(Qt.RightToLeft)
        renew_layout.addWidget(self.renew_check)
        renew_layout.addStretch()

        name_label = QLabel("نام:")
        name_label.setFont(QFont("Arial", 26))
        phone_label = QLabel("شماره تلفن:")
        phone_label.setFont(QFont("Arial", 26))
        program_label = QLabel("نوع برنامه:")
        program_label.setFont(QFont("Arial", 26))
        diet_label = QLabel("برنامه غذایی:")
        diet_label.setFont(QFont("Arial", 26))
        training_label = QLabel("برنامه تمرینی:")
        training_label.setFont(QFont("Arial", 26))
        coach_label = QLabel("مربی:")
        coach_label.setFont(QFont("Arial", 26))
        active_label = QLabel("وضعیت کاربر:")
        active_label.setFont(QFont("Arial", 26))
        status_header = QLabel("وضعیت اشتراک:")
        status_header.setFont(QFont("Arial", 26))

        form_layout.addRow(name_label, self.name_edit)
        form_layout.addRow(phone_label, self.phone_edit)
        form_layout.addRow(program_label, self.program_type_combo)
        form_layout.addRow(diet_label, diet_container)
        form_layout.addRow(training_label, training_container)
        form_layout.addRow(coach_label, coach_container)
        form_layout.addRow(active_label, active_container)
        form_layout.addRow(self.reg_label)
        form_layout.addRow(self.exp_label)
        form_layout.addRow(status_header, self.status_label)
        form_layout.addRow(renew_container)

        layout.addWidget(form_widget)

        buttons_container = QWidget()
        buttons_container.setLayoutDirection(Qt.RightToLeft)
        buttons = QHBoxLayout(buttons_container)
        save_btn = QPushButton("ذخیره")
        save_btn.setFont(QFont("Arial", 26))
        save_btn.setMinimumHeight(65)
        save_btn.setMinimumWidth(150)
        save_btn.clicked.connect(self.save_changes)
        delete_btn = QPushButton("حذف")
        delete_btn.setFont(QFont("Arial", 26))
        delete_btn.setMinimumHeight(65)
        delete_btn.setMinimumWidth(150)
        delete_btn.clicked.connect(self.delete_user)
        close_btn = QPushButton("بستن")
        close_btn.setFont(QFont("Arial", 26))
        close_btn.setMinimumHeight(65)
        close_btn.setMinimumWidth(150)
        close_btn.clicked.connect(self.close)
        buttons.addWidget(save_btn)
        buttons.addWidget(delete_btn)
        buttons.addWidget(close_btn)
        layout.addWidget(buttons_container)

        self.setLayout(layout)

    def save_changes(self):
        program_type = 'normal' if self.program_type_combo.currentText() == 'عادی' else 'vip'
        update_user(
            self.user[0], self.name_edit.text(), self.phone_edit.text(),
            program_type, self.diet_check.isChecked(),
            self.training_check.isChecked(), self.coach_check.isChecked(),
            self.active_check.isChecked()
        )
        if self.renew_check.isChecked():
            renew_subscription(self.user[0])
        QMessageBox.information(self, "موفقیت", "کاربر به‌روزرسانی شد.")
        self.accept()

    def delete_user(self):
        if QMessageBox.warning(self, "تأیید", "آیا مطمئن هستید که می‌خواهید این کاربر را حذف کنید؟", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            delete_user(self.user[0])
            self.accept()

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("افزودن کاربر جدید")
        self.setMinimumSize(800, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)

        form_widget = QWidget()
        form_widget.setLayoutDirection(Qt.RightToLeft)
        form_layout = QFormLayout(form_widget)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignRight | Qt.AlignTop)
        form_layout.setSpacing(25)

        self.name_edit = QLineEdit()
        self.name_edit.setFont(QFont("Arial", 26))
        self.name_edit.setMinimumHeight(55)
        self.name_edit.setAlignment(Qt.AlignRight)
        self.phone_edit = QLineEdit()
        self.phone_edit.setFont(QFont("Arial", 26))
        self.phone_edit.setMinimumHeight(55)
        self.phone_edit.setAlignment(Qt.AlignRight)
        self.program_type_combo = QComboBox()
        self.program_type_combo.addItems(['عادی', 'ویژه'])
        self.program_type_combo.setFont(QFont("Arial", 26))
        self.program_type_combo.setMinimumHeight(55)
        self.program_type_combo.setLayoutDirection(Qt.RightToLeft)
        
        diet_container = QWidget()
        diet_container.setLayoutDirection(Qt.RightToLeft)
        diet_layout = QHBoxLayout(diet_container)
        diet_layout.setContentsMargins(0, 0, 0, 0)
        self.diet_check = QCheckBox()
        self.diet_check.setFont(QFont("Arial", 26))
        diet_layout.addWidget(self.diet_check)
        diet_layout.addStretch()
        
        training_container = QWidget()
        training_container.setLayoutDirection(Qt.RightToLeft)
        training_layout = QHBoxLayout(training_container)
        training_layout.setContentsMargins(0, 0, 0, 0)
        self.training_check = QCheckBox()
        self.training_check.setFont(QFont("Arial", 26))
        training_layout.addWidget(self.training_check)
        training_layout.addStretch()
        
        coach_container = QWidget()
        coach_container.setLayoutDirection(Qt.RightToLeft)
        coach_layout = QHBoxLayout(coach_container)
        coach_layout.setContentsMargins(0, 0, 0, 0)
        self.coach_check = QCheckBox()
        self.coach_check.setFont(QFont("Arial", 26))
        coach_layout.addWidget(self.coach_check)
        coach_layout.addStretch()
        
        active_container = QWidget()
        active_container.setLayoutDirection(Qt.RightToLeft)
        active_layout = QHBoxLayout(active_container)
        active_layout.setContentsMargins(0, 0, 0, 0)
        self.active_check = QCheckBox("فعال")
        self.active_check.setChecked(True)
        self.active_check.setFont(QFont("Arial", 26))
        self.active_check.setLayoutDirection(Qt.RightToLeft)
        active_layout.addWidget(self.active_check)
        active_layout.addStretch()

        name_label = QLabel("نام:")
        name_label.setFont(QFont("Arial", 26))
        phone_label = QLabel("شماره تلفن:")
        phone_label.setFont(QFont("Arial", 26))
        program_label = QLabel("نوع برنامه:")
        program_label.setFont(QFont("Arial", 26))
        diet_label = QLabel("برنامه غذایی:")
        diet_label.setFont(QFont("Arial", 26))
        training_label = QLabel("برنامه تمرینی:")
        training_label.setFont(QFont("Arial", 26))
        coach_label = QLabel("مربی:")
        coach_label.setFont(QFont("Arial", 26))
        active_label = QLabel("وضعیت کاربر:")
        active_label.setFont(QFont("Arial", 26))

        form_layout.addRow(name_label, self.name_edit)
        form_layout.addRow(phone_label, self.phone_edit)
        form_layout.addRow(program_label, self.program_type_combo)
        form_layout.addRow(diet_label, diet_container)
        form_layout.addRow(training_label, training_container)
        form_layout.addRow(coach_label, coach_container)
        form_layout.addRow(active_label, active_container)

        layout.addWidget(form_widget)

        buttons_container = QWidget()
        buttons_container.setLayoutDirection(Qt.RightToLeft)
        buttons = QHBoxLayout(buttons_container)
        add_btn = QPushButton("افزودن")
        add_btn.setFont(QFont("Arial", 26))
        add_btn.setMinimumHeight(65)
        add_btn.setMinimumWidth(150)
        add_btn.clicked.connect(self.add_user)
        cancel_btn = QPushButton("لغو")
        cancel_btn.setFont(QFont("Arial", 26))
        cancel_btn.setMinimumHeight(65)
        cancel_btn.setMinimumWidth(150)
        cancel_btn.clicked.connect(self.close)
        buttons.addWidget(add_btn)
        buttons.addWidget(cancel_btn)
        layout.addWidget(buttons_container)

        self.setLayout(layout)

    def add_user(self):
        name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        if not name or not phone:
            QMessageBox.warning(self, "خطا", "نام و شماره تلفن الزامی است.")
            return
        program_type = 'normal' if self.program_type_combo.currentText() == 'عادی' else 'vip'
        add_user(
            name, phone, program_type,
            self.diet_check.isChecked(), self.training_check.isChecked(),
            self.coach_check.isChecked(), self.active_check.isChecked()
        )
        QMessageBox.information(self, "موفقیت", "کاربر اضافه شد.")
        self.accept()

class UsersManagementWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.RightToLeft)
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Create search container widget
        search_container = QWidget()
        search_container.setLayoutDirection(Qt.RightToLeft)
        search_layout = QHBoxLayout(search_container)
        
        # Back to Home button
        back_btn = QPushButton("بازگشت به صفحه اصلی")
        back_btn.setFont(QFont("Arial", 26))
        back_btn.setMinimumHeight(65)
        back_btn.setMinimumWidth(280)
        back_btn.clicked.connect(self.back_to_home)
        search_layout.addWidget(back_btn)
        
        add_btn = QPushButton("افزودن کاربر")
        add_btn.setFont(QFont("Arial", 26))
        add_btn.setMinimumHeight(65)
        add_btn.setMinimumWidth(280)
        add_btn.clicked.connect(self.add_user)
        search_layout.addWidget(add_btn)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("جستجو بر اساس نام یا شماره تلفن...")
        self.search_edit.setFont(QFont("Arial", 26))
        self.search_edit.setMinimumHeight(65)
        self.search_edit.setAlignment(Qt.AlignRight)
        self.search_edit.textChanged.connect(self.refresh_table)
        search_layout.addWidget(self.search_edit)

        layout.addWidget(search_container)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "شناسه", "نام", "شماره", "نوع", "غذایی", "تمرینی", "مربی", "وضعیت کاربر", "وضعیت اشتراک", "انقضا"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(70)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.open_profile)
        self.table.setFont(QFont("Arial", 24))
        self.table.setLayoutDirection(Qt.RightToLeft)
        for col in [4, 5, 6, 7]:
            self.table.setItemDelegateForColumn(col, CheckBoxDelegate(self.table))
        layout.addWidget(self.table)

        self.refresh_table()
        self.setLayout(layout)

    def back_to_home(self):
        main_window = self.window()
        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_label = QLabel("خوش آمدید به سیستم مدیریت باشگاه")
        home_label.setFont(QFont("Arial", 500, QFont.Bold))
        home_label.setAlignment(Qt.AlignCenter)
        home_label.setStyleSheet("color: #2C3E50; margin: 40px; font-size: 40px; font-weight: bold;")
        home_layout.addWidget(home_label)

        manage_btn = QPushButton("مدیریت کاربران")
        manage_btn.setFont(QFont("Arial", 30))
        manage_btn.setMinimumHeight(80)
        manage_btn.clicked.connect(main_window.show_users_management)
        manage_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        manage_btn.setMinimumWidth(400)
        home_layout.addWidget(manage_btn, alignment=Qt.AlignCenter)

        # Add club logo
        logo_label = QLabel()
        pixmap = QPixmap(200, 200)  # Placeholder for logo
        pixmap.fill(Qt.transparent)
        logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        home_layout.addStretch()
        home_widget.setLayout(home_layout)
        main_window.scroll.setWidget(home_widget)

    def refresh_table(self):
        query = self.search_edit.text()
        users = search_users(query) if query else get_all_users()
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            active_sub = is_subscription_active(user[8])
            if not active_sub:
                row_color = QColor(255, 180, 180)
            else:
                row_color = QColor(255, 255, 255)
                
            id_item = QTableWidgetItem(str(user[0]))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setFont(QFont("Arial", 13, QFont.Bold))
            self.table.setItem(row, 0, id_item)
                
            name_item = QTableWidgetItem(user[1])
            name_item.setTextAlignment(Qt.AlignCenter)
            name_item.setFont(QFont("Arial", 13, QFont.Bold))
            self.table.setItem(row, 1, name_item)
                
            phone_item = QTableWidgetItem(user[2])
            phone_item.setTextAlignment(Qt.AlignCenter)
            phone_item.setFont(QFont("Arial", 13, QFont.Bold))
            self.table.setItem(row, 2, phone_item)
                
            type_item = QTableWidgetItem('عادی' if user[3] == 'normal' else 'ویژه')
            type_item.setTextAlignment(Qt.AlignCenter)
            type_item.setFont(QFont("Arial", 13, QFont.Bold))
            self.table.setItem(row, 3, type_item)
                
            diet_item = QTableWidgetItem()
            diet_item.setData(Qt.DisplayRole, bool(user[4]))
            diet_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, diet_item)
                
            training_item = QTableWidgetItem()
            training_item.setData(Qt.DisplayRole, bool(user[5]))
            training_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, training_item)
                
            coach_item = QTableWidgetItem()
            coach_item.setData(Qt.DisplayRole, bool(user[6]))
            coach_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 6, coach_item)
                
            active_item = QTableWidgetItem()
            active_item.setData(Qt.DisplayRole, bool(user[9]))
            active_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 7, active_item)
                
            status_item = QTableWidgetItem("فعال" if active_sub else "منقضی")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(QColor("green") if active_sub else QColor("red"))
            status_item.setFont(QFont("Arial", 13, QFont.Bold))
            self.table.setItem(row, 8, status_item)
                
            exp_date = to_jalali(user[8])
            exp_item = QTableWidgetItem(exp_date)
            exp_item.setTextAlignment(Qt.AlignCenter)
            exp_item.setFont(QFont("Arial", 13, QFont.Bold))
            self.table.setItem(row, 9, exp_item)
                
            for col in range(10):
                if self.table.item(row, col):
                    self.table.item(row, col).setBackground(row_color)

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_():
            self.refresh_table()
            self.window().update_user_stats()

    def open_profile(self, item):
        row = item.row()
        user_id = int(self.table.item(row, 0).text())
        user = get_user_by_id(user_id)
        dialog = UserProfileDialog(user, self)
        if dialog.exec_():
            self.refresh_table()
            self.window().update_user_stats()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم مدیریت باشگاه")
        self.setMinimumSize(1200, 800)
        self.setWindowIcon(QIcon())

        self.header_frame = QFrame()
        header_layout = QHBoxLayout(self.header_frame)

        # User stats box (remains on the left)
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 10px;")
        stats_layout = QVBoxLayout(self.stats_frame)
        stats_layout.setAlignment(Qt.AlignRight)
        self.total_users_label = QLabel("تعداد کل کاربران: 0")
        self.active_users_label = QLabel("کاربران فعال: 0")
        self.inactive_users_label = QLabel("کاربران غیرفعال: 0")
        for label in [self.total_users_label, self.active_users_label, self.inactive_users_label]:
            label.setFont(QFont("Arial", 20))
            label.setAlignment(Qt.AlignRight)
            label.setStyleSheet("font-size: 25px; font-weight: bold;")
            stats_layout.addWidget(label)
        header_layout.addWidget(self.stats_frame)

        # Add stretch to push datetime to the center
        header_layout.addStretch()

        # Datetime label centered independently
        self.datetime_label = QLabel(get_current_jalali_date_time())
        self.datetime_label.setFont(QFont("Arial", 40, QFont.Bold))
        self.datetime_label.setAlignment(Qt.AlignCenter)
        self.datetime_label.setStyleSheet("color: white; font-size: 40px; font-weight: bold;")
        header_layout.addWidget(self.datetime_label, alignment=Qt.AlignCenter)

        self.header_frame.setLayout(header_layout)
        self.header_frame.setStyleSheet("background-color: #2C3E50; padding: 20px; border-radius: 10px;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.header_frame)

        home_widget = QWidget()
        home_layout = QVBoxLayout(home_widget)
        home_label = QLabel("خوش آمدید به سیستم مدیریت باشگاه")
        home_label.setFont(QFont("Arial", 500, QFont.Bold))
        home_label.setAlignment(Qt.AlignCenter)
        home_label.setStyleSheet("color: #2C3E50; margin: 40px; font-size: 40px; font-weight: bold;")
        home_layout.addWidget(home_label)

        manage_btn = QPushButton("مدیریت کاربران")
        manage_btn.setFont(QFont("Arial", 30))
        manage_btn.setMinimumHeight(80)
        manage_btn.clicked.connect(self.show_users_management)
        manage_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        manage_btn.setMinimumWidth(400)
        home_layout.addWidget(manage_btn, alignment=Qt.AlignCenter)

        # Add club logo
        logo_label = QLabel()
        pixmap = QPixmap(200, 200)  # Placeholder for logo
        pixmap.fill(Qt.transparent)
        logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        home_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        home_layout.addStretch()
        home_widget.setLayout(home_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(home_widget)
        main_layout.addWidget(self.scroll)

        app.setStyle("Fusion")
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ECF0F1;
                color: #2C3E50;
            }
            QLabel {
                color: #2C3E50;
                font-size: 26px;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 20px;
                border-radius: 12px;
                font-size: 26px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
            QLineEdit, QComboBox {
                background-color: white;
                color: #2C3E50;
                border: 2px solid #BDC3C7;
                padding: 12px;
                border-radius: 8px;
                font-size: 26px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 2px solid #3498DB;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #F8F9FA;
                gridline-color: #BDC3C7;
                color: #2C3E50;
                font-size: 24px;
                selection-background-color: #3498DB;
                selection-color: white;
                border: 2px solid #BDC3C7;
                border-radius: 8px;
            }
            QTableWidget::item:hover {
                background-color: #AED6F1;
            }
            QHeaderView::section {
                background-color: #34495E;
                color: white;
                padding: 15px;
                border: none;
                font-size: 26px;
                font-weight: bold;
            }
            QCheckBox {
                font-size: 26px;
                spacing: 10px;
            }
            QCheckBox::indicator {
                width: 35px;
                height: 35px;
                border-radius: 5px;
                border: 2px solid #BDC3C7;
            }
            QCheckBox::indicator:checked {
                background-color: #27AE60;
                border: 2px solid #27AE60;
            }
            QScrollArea {
                border: none;
            }
            QDialog {
                background-color: #ECF0F1;
            }
            QMessageBox {
                font-size: 24px;
            }
            QMessageBox QPushButton {
                min-width: 120px;
                min-height: 50px;
            }
        """)

        main_layout.setContentsMargins(25, 25, 25, 25)
        home_layout.setSpacing(30)

        self.update_user_stats()

    def update_datetime(self):
        self.datetime_label.setText(get_current_jalali_date_time())
        self.update_user_stats()

    def update_user_stats(self):
        total, active, inactive = get_user_stats()
        self.total_users_label.setText(f"تعداد کل کاربران: {total}")
        self.active_users_label.setText(f"کاربران فعال: {active}")
        self.inactive_users_label.setText(f"کاربران غیرفعال: {inactive}")

    def show_users_management(self):
        users_widget = UsersManagementWidget()
        self.scroll.setWidget(users_widget)

if __name__ == "__main__":
    init_db()
    app = QApplication(sys.argv)
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(236, 240, 241))
    palette.setColor(QPalette.WindowText, QColor(44, 62, 80))
    palette.setColor(QPalette.Base, Qt.white)
    palette.setColor(QPalette.AlternateBase, QColor(248, 249, 250))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, QColor(44, 62, 80))
    palette.setColor(QPalette.Text, QColor(44, 62, 80))
    palette.setColor(QPalette.Button, QColor(52, 152, 219))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(52, 152, 219))
    palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())