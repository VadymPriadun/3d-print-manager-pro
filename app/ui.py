import sqlite3

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QCheckBox, QPushButton, QMessageBox, 
                             QTabWidget, QTableWidget, QAbstractItemView, 
                             QHeaderView, QShortcut, QTableWidgetItem, QInputDialog)
from PyQt5.QtGui import QCursor, QKeySequence, QColor

from app.database import DB
from app.dialogs import OrderDialog, ReceiptDialog, ShortcutsDialog

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вхід у систему")
        self.setFixedSize(320, 420) 
        self.setStyleSheet("background-color: #f4f5f7;") 

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 40, 30, 40) 
        layout.setSpacing(15) 

        title = QLabel("Авторизація")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: #2C3E50; 
            margin-bottom: 15px;
        """)

        input_style = """
            QLineEdit {
                padding: 12px;
                border: 2px solid #dce4ec;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #3498DB;
            }
        """

        self.login = QLineEdit()
        self.login.setPlaceholderText("Логін")
        self.login.setStyleSheet(input_style)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Пароль")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(input_style)

        self.remember_cb = QCheckBox("Запам'ятати мене на цьому ПК")
        self.remember_cb.setCursor(QCursor(Qt.PointingHandCursor))
        self.remember_cb.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #7f8c8d;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)

        btn = QPushButton("Увійти")
        btn.setCursor(QCursor(Qt.PointingHandCursor)) 
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #1F618D;
            }
        """)
        btn.clicked.connect(self.check)

        layout.addWidget(title)
        layout.addWidget(self.login)
        layout.addWidget(self.password)
        layout.addWidget(self.remember_cb)
        layout.addWidget(btn)
        layout.addStretch() 

        self.setLayout(layout)

    def check(self):
        if self.login.text() == "admin" and self.password.text() == "1234":
            if self.remember_cb.isChecked():
                settings = QSettings("My3DPrintApp", "ManagerPRO")
                settings.setValue("is_logged_in", True)

            self.main = App()
            self.main.show()
            self.close()
        else:
            QMessageBox.warning(self, "Помилка", "Невірний логін або пароль")
            self.password.clear() 

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Print Manager PRO")
        self.resize(1050, 650)

        layout = QVBoxLayout()

        top_bar = QHBoxLayout()
        
        title = QLabel("Панель управління") 
        title.setStyleSheet("font-weight: bold; color: #555;")
        
        help_btn = QPushButton("⌨️ Гарячі клавіші")
        help_btn.setFixedSize(140, 30)
        help_btn.setStyleSheet("background-color: #E3F2FD; border: 1px solid #BBDEFB; border-radius: 4px;")
        help_btn.clicked.connect(self.show_shortcuts_guide) 

        top_bar.addWidget(title)
        top_bar.addStretch() 
        top_bar.addWidget(help_btn)
        
        layout.addLayout(top_bar)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.orders_tab(), "Замовлення")
        self.tabs.addTab(self.plastic_tab(), "Склад")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.setup_shortcuts()

    def orders_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.search = QLineEdit()
        self.search.setPlaceholderText("Пошук...")
        self.search.textChanged.connect(self.load_orders)
        layout.addWidget(self.search)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9) 
        self.table.setHorizontalHeaderLabels([
            "ID", "Клієнт", "Модель", "Вага",
            "Пластик", "Дедлайн", "Статус", "Вартість", "Чек" 
        ])

        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemDoubleClicked.connect(lambda item: self.edit_order())
        
        shortcut_f2 = QShortcut(QKeySequence("F2"), self.table)
        shortcut_f2.activated.connect(self.edit_order)
        
        shortcut_del = QShortcut(QKeySequence("Delete"), self.table)
        shortcut_del.activated.connect(self.delete_order)

        shortcut_done = QShortcut(QKeySequence("Ctrl+D"), self.table)
        shortcut_done.activated.connect(self.mark_done)

        layout.addWidget(self.table)
        
        btns = QHBoxLayout()
        add = QPushButton("Додати")
        add.clicked.connect(self.add_order)

        edit = QPushButton("Редагувати")
        edit.clicked.connect(self.edit_order)

        delete = QPushButton("Видалити")
        delete.clicked.connect(self.delete_order)

        done = QPushButton("Виконано")
        done.clicked.connect(self.mark_done)

        graph_btn = QPushButton("Графік")
        graph_btn.clicked.connect(self.show_graph)

        export_btn = QPushButton("Excel")
        export_btn.clicked.connect(self.export_excel)
        
        refresh_btn = QPushButton("Оновити")
        refresh_btn.clicked.connect(self.refresh_all)

        receipt_btn = QPushButton("Чек")
        receipt_btn.clicked.connect(self.generate_receipt)

        btns.addWidget(add)
        btns.addWidget(edit)
        btns.addWidget(delete)
        btns.addWidget(done)
        btns.addWidget(receipt_btn) 
        btns.addWidget(graph_btn)
        btns.addWidget(export_btn)
        btns.addWidget(refresh_btn)
        
        layout.addLayout(btns)
        tab.setLayout(layout)
        self.load_orders()
        return tab

    def plastic_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.plastic_table = QTableWidget()
        self.plastic_table.setColumnCount(5)
        self.plastic_table.setHorizontalHeaderLabels([
            "ID", "Назва", "Колір", "Залишок", "Ціна/кг"
        ])
        
        self.plastic_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plastic_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.plastic_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.plastic_table.itemDoubleClicked.connect(self.edit_plastic)
        
        shortcut_f2 = QShortcut(QKeySequence("F2"), self.plastic_table)
        shortcut_f2.activated.connect(self.edit_plastic)
        
        shortcut_del = QShortcut(QKeySequence("Delete"), self.plastic_table)
        shortcut_del.activated.connect(self.delete_plastic)
        
        layout.addWidget(self.plastic_table)
        
        btns = QHBoxLayout()
        add = QPushButton("Додати")
        add.clicked.connect(self.add_plastic)
        
        edit = QPushButton("Редагувати")
        edit.clicked.connect(self.edit_plastic)
        
        delete = QPushButton("Видалити")
        delete.clicked.connect(self.delete_plastic)
        
        refresh_btn = QPushButton("Оновити")
        refresh_btn.clicked.connect(self.refresh_all)
        
        btns.addWidget(add)
        btns.addWidget(edit)
        btns.addWidget(delete)
        btns.addWidget(refresh_btn)
        
        layout.addLayout(btns)
        tab.setLayout(layout)
        self.load_plastic()
        return tab

    def load_plastic(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT * FROM plastic")
        data = cur.fetchall()
        self.plastic_table.setRowCount(len(data))
        for i, row in enumerate(data):
            for j, val in enumerate(row):
                self.plastic_table.setItem(i, j, QTableWidgetItem(str(val)))
        conn.close()

    def add_order(self):
        dialog = OrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            conn = sqlite3.connect(DB)
            cur = conn.cursor()

            cur.execute(
                "SELECT id, price, stock FROM plastic WHERE name=? AND color=?",
                (data["plastic"], data["color"])
            )       
            res = cur.fetchone()
            if not res:
                QMessageBox.warning(self, "Помилка", "Нема такого пластику")
                return
            
            plastic_id, price, stock = res
            
            if data["weight"] > stock:
                QMessageBox.warning(self, "Помилка", "Недостатньо пластику")
                return
            
            cur.execute(
                "UPDATE plastic SET stock = stock - ? WHERE id=?",
                (data["weight"], plastic_id)
            )
            
            cost = (data["weight"] / 1000) * price
            
            cur.execute("""
            INSERT INTO orders (client, model, weight, plastic, deadline, status, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                data["client"],
                data["model"],
                data["weight"],
                plastic_id,  
                data["deadline"],
                "В роботі",
                cost
            ))
            
            conn.commit()
            conn.close()
            self.load_orders()
            self.load_plastic()

    def edit_order(self):
        row = self.table.currentRow()
        if row == -1: return
            
        status = self.table.item(row, 6).text()
        if status == "Виконано":
            QMessageBox.warning(self, "Заблоковано", "Замовлення вже виконано!\nЩоб змінити дані, скасуйте статус 'Виконано'.")
            return
            
        order_id = self.table.item(row, 0).text()
        
        data = {
            "client": self.table.item(row, 1).text(),
            "model": self.table.item(row, 2).text(),
            "weight": self.table.item(row, 3).text(),
            "plastic": self.table.item(row, 4).text(),
            "deadline": self.table.item(row, 5).text(),
        }
        
        dialog = OrderDialog(data)
        if dialog.exec():
            new_data = dialog.get_data()
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            
            cur.execute("SELECT weight, plastic FROM orders WHERE id=?", (order_id,))
            old_weight, old_plastic_id = cur.fetchone()
            
            cur.execute("SELECT id, price, stock FROM plastic WHERE name=? AND color=?", (new_data["plastic"], new_data["color"]))
            new_plastic_res = cur.fetchone()
            
            if not new_plastic_res:
                QMessageBox.warning(self, "Помилка", "Пластик не знайдено!")
                return
                
            new_plastic_id, new_price, new_stock = new_plastic_res
            
            if old_plastic_id == new_plastic_id:
                available_stock = new_stock + old_weight
            else:
                available_stock = new_stock
                
            if new_data["weight"] > available_stock:
                QMessageBox.warning(self, "Помилка", f"Недостатньо пластику! Доступно: {available_stock}г")
                return
                
            cur.execute("UPDATE plastic SET stock = stock + ? WHERE id=?", (old_weight, old_plastic_id))
            cur.execute("UPDATE plastic SET stock = stock - ? WHERE id=?", (new_data["weight"], new_plastic_id))
            
            new_cost = (new_data["weight"] / 1000) * new_price

            cur.execute("""
            UPDATE orders SET client=?, model=?, weight=?, plastic=?, deadline=?, cost=? WHERE id=?
            """, (new_data["client"], new_data["model"], new_data["weight"], new_plastic_id, new_data["deadline"], new_cost, order_id))
            
            conn.commit()
            conn.close()
            self.load_orders()
            self.load_plastic()

    def delete_order(self):
        row = self.table.currentRow()
        if row == -1:
            return
            
        reply = QMessageBox.question(
            self, 'Підтвердження', 
            'Ви дійсно хочете видалити це замовлення?', 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return 

        order_id = self.table.item(row, 0).text()
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        
        cur.execute("SELECT weight, plastic FROM orders WHERE id=?", (order_id,))
        res = cur.fetchone()
        if res:
            weight, plastic_id = res
            cur.execute("UPDATE plastic SET stock = stock + ? WHERE id=?", (weight, plastic_id))
        
        cur.execute("DELETE FROM orders WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        self.load_orders()
        self.load_plastic() 

    def mark_done(self):
        row = self.table.currentRow()
        if row == -1:
            return
            
        order_id = self.table.item(row, 0).text()
        current_status = self.table.item(row, 6).text()
        
        new_status = "В роботі" if current_status == "Виконано" else "Виконано"
        
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
        conn.commit()
        conn.close()
        self.load_orders()

    def add_plastic(self):
        name, ok = QInputDialog.getText(self, "Назва", "Назва пластику:")
        if not ok: return

        color, _ = QInputDialog.getText(self, "Колір", "Колір:")
        stock, _ = QInputDialog.getDouble(self, "Залишок", "г:")
        price, _ = QInputDialog.getDouble(self, "Ціна", "грн/кг:")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
        INSERT INTO plastic (name, color, stock, price)
        VALUES (?, ?, ?, ?)
        """, (name, color, stock, price))
        conn.commit()
        conn.close()

        self.recalc_costs()
        self.load_plastic()
        self.load_orders()

    def edit_plastic(self):
        row = self.plastic_table.currentRow()
        if row == -1: return
            
        p_id = self.plastic_table.item(row, 0).text()
        name = self.plastic_table.item(row, 1).text()
        color = self.plastic_table.item(row, 2).text()
        stock = float(self.plastic_table.item(row, 3).text())
        price = float(self.plastic_table.item(row, 4).text())
        
        new_name, ok1 = QInputDialog.getText(self, "Редагувати", "Назва пластику:", text=name)
        if not ok1: return
        new_color, ok2 = QInputDialog.getText(self, "Редагувати", "Колір:", text=color)
        if not ok2: return
        new_stock, ok3 = QInputDialog.getDouble(self, "Редагувати", "Залишок (г):", value=stock, max=1000000)
        if not ok3: return
        new_price, ok4 = QInputDialog.getDouble(self, "Редагувати", "Ціна (грн/кг):", value=price, max=100000)
        if not ok4: return
        
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            UPDATE plastic SET name=?, color=?, stock=?, price=? WHERE id=?
        """, (new_name, new_color, new_stock, new_price, p_id))
        conn.commit()
        conn.close()
        
        self.load_plastic()
        self.load_orders() 

    def delete_plastic(self):
        row = self.plastic_table.currentRow()
        if row == -1: return
            
        reply = QMessageBox.question(
            self, 'Підтвердження', 
            'Ви дійсно хочете видалити цей пластик зі складу?', 
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
            
        p_id = self.plastic_table.item(row, 0).text()
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("DELETE FROM plastic WHERE id=?", (p_id,))
        conn.commit()
        conn.close()
        
        self.load_plastic()
        self.load_orders()

    def show_graph(self):
        import matplotlib.pyplot as plt
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            SELECT p.name, p.color, SUM(o.weight)
            FROM orders o
            LEFT JOIN plastic p ON o.plastic = p.id
            GROUP BY p.name, p.color
        """)
        data = cur.fetchall()
        labels = [f"{name} ({color})" if color else str(name) for name, color, w in data if name is not None]
        weights = [w for name, color, w in data if name is not None]
        plt.bar(labels, weights)
        plt.title("Витрати пластику")
        plt.xlabel("Тип (колір)")
        plt.ylabel("Грами")
        plt.xticks(rotation=45)
        plt.show()

    def recalc_costs(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            SELECT o.id, o.weight, p.price
            FROM orders o
            JOIN plastic p ON o.plastic = p.id
        """)
        rows = cur.fetchall()
        for order_id, weight, price in rows:
            cost = (weight / 1000) * price
            cur.execute("UPDATE orders SET cost=? WHERE id=?", (cost, order_id))
        conn.commit()
        conn.close()

    def load_orders(self):
        self.recalc_costs()
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        text = self.search.text()
        self.table.setSortingEnabled(False)
        
        query = """
            SELECT o.id, o.client, o.model, o.weight,
                p.name, p.color, o.deadline, o.status, o.cost, o.receipt_path
            FROM orders o
            LEFT JOIN plastic p ON o.plastic = p.id
        """
        if text:
            query += " WHERE o.client LIKE ?"
            cur.execute(query, ('%' + text + '%',))
        else:
            cur.execute(query)
            
        data = cur.fetchall()
        self.table.setRowCount(len(data))
        conn.close()
        
        for i, row in enumerate(data):
            id_, client, model, weight, name, color, deadline, status, cost, receipt = row
            plastic_text = f"{name} ({color})" if color else (name if name else "Невідомо")
            receipt_text = receipt if receipt else "—" 
            
            values = [id_, client, model, weight, plastic_text, deadline, status, cost, receipt_text]
            
            for j, val in enumerate(values):
                item = QTableWidgetItem()
                if j in [0, 3, 7]: 
                    item.setData(Qt.EditRole, float(val) if '.' in str(val) else int(val))
                else:
                    item.setData(Qt.EditRole, str(val))
                    
                if status == "Виконано":
                    item.setBackground(QColor("#A8D5BA"))
                elif status == "В роботі":
                    item.setBackground(QColor("#F5E6A3"))
                    
                self.table.setItem(i, j, item)
                
        self.table.setSortingEnabled(True)

    def export_excel(self):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT o.id, o.client, o.model, o.weight, 
                   COALESCE(p.name || ' (' || p.color || ')', 'Невідомо'), 
                   o.deadline, o.status, o.cost, o.receipt_path
            FROM orders o
            LEFT JOIN plastic p ON o.plastic = p.id
        """)
        rows = cur.fetchall()
        
        headers = ["ID", "Client", "Model", "Weight", "Plastic", "Deadline", "Status", "Cost", "Receipt"]
        ws.append(headers)
        for row in rows:
            ws.append(row)
        conn.close()
        wb.save("orders.xlsx")
        QMessageBox.information(self, "Готово", "Експортовано в orders.xlsx з правильними назвами!")

    def refresh_all(self):
        self.load_orders()
        self.load_plastic()

    def show_shortcuts_guide(self):
        dialog = ShortcutsDialog(self)
        dialog.exec_()

    def setup_shortcuts(self):
        shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        shortcut_f5.activated.connect(self.refresh_all)

        shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        shortcut_new.activated.connect(self.add_order)

        shortcut_find = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_find.activated.connect(self.search.setFocus)

        shortcut_print = QShortcut(QKeySequence("Ctrl+P"), self)
        shortcut_print.activated.connect(self.generate_receipt)

    def generate_receipt(self):
        row = self.table.currentRow()
        if row == -1: return
            
        order_data = {
            "id": self.table.item(row, 0).text(),
            "client": self.table.item(row, 1).text(),
            "model": self.table.item(row, 2).text(),
            "weight": self.table.item(row, 3).text(),
            "plastic": self.table.item(row, 4).text(),
            "deadline": self.table.item(row, 5).text(),
            "status": self.table.item(row, 6).text(),
            "cost": self.table.item(row, 7).text(),
        }
        
        dialog = ReceiptDialog(order_data)
        if dialog.exec_(): 
            self.load_orders()