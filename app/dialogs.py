import sqlite3
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, 
                             QComboBox, QPushButton, QVBoxLayout, QTextEdit, 
                             QHBoxLayout, QFileDialog, QMessageBox, QLabel)

from app.database import DB

class OrderDialog(QDialog):
    def __init__(self, data=None):
        super().__init__()
        self.setWindowTitle("Замовлення")

        layout = QFormLayout()

        self.client = QLineEdit()
        self.model = QLineEdit()
        
        self.weight = QDoubleSpinBox()
        self.weight.setMaximum(100000.0) 
        self.weight.setDecimals(1)
        self.weight.setSuffix(" г") 

        self.plastic = QComboBox()
        self.load_plastic()
        self.deadline = QLineEdit()

        layout.addRow("Клієнт:", self.client)
        layout.addRow("Модель:", self.model)
        layout.addRow("Вага:", self.weight)
        layout.addRow("Пластик:", self.plastic)
        layout.addRow("Дедлайн (YYYY-MM-DD):", self.deadline)

        btn = QPushButton("OK")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.setLayout(layout)

        if data is None:
            self.deadline.setText("2026-12-31")
        else:
            self.client.setText(data.get("client", ""))
            self.model.setText(data.get("model", ""))
            
            weight_val = float(data.get("weight", 0)) if data.get("weight") else 0.0
            self.weight.setValue(weight_val)
            
            self.deadline.setText(data.get("deadline", ""))

            plastic_text = data.get("plastic", "")
            index = self.plastic.findText(plastic_text)
            if index >= 0:
                self.plastic.setCurrentIndex(index)

    def get_data(self):
        text = self.plastic.currentText()
        if " (" in text:
            name, color = text.split(" (")
            color = color[:-1]
        else:
            name = text
            color = ""

        return {
            "client": self.client.text(),
            "model": self.model.text(),
            "weight": self.weight.value(), 
            "plastic": name,
            "color": color,
            "deadline": self.deadline.text()
        }

    def load_plastic(self):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("SELECT name, color FROM plastic")
        for name, color in cur.fetchall():
            self.plastic.addItem(f"{name} ({color})")
        conn.close()

class ReceiptDialog(QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle(f"Чек - Замовлення #{data['id']}")
        self.resize(400, 500)
        self.data = data
        
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True) 
        self.text_edit.setStyleSheet("background-color: white; color: black; font-size: 14px;")
        
        self.html_content = f"""
        <h2 style="text-align: center;">ЧЕК ЗАМОВЛЕННЯ #{data['id']}</h2>
        <hr>
        <p><b>Клієнт:</b> {data['client']}</p>
        <p><b>Модель:</b> {data['model']}</p>
        <p><b>Матеріал:</b> {data['plastic']} ({data['weight']} г)</p>
        <p><b>Дедлайн:</b> {data['deadline']}</p>
        <p><b>Статус:</b> {data['status']}</p>
        <br>
        <p><b>Дата видачі чека:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <hr>
        <h2 style="text-align: right; color: #2E7D32;">До сплати: {data['cost']} грн</h2>
        <br>
        <p style="text-align: center; color: #555;"><i>Дякуємо за ваше замовлення!</i></p>
        """
        
        self.text_edit.setHtml(self.html_content)
        layout.addWidget(self.text_edit)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("Зберегти у PDF")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px;")
        save_btn.clicked.connect(self.save_pdf)
        
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(self.close)
        
        btns.addWidget(save_btn)
        btns.addWidget(close_btn)
        layout.addLayout(btns)
        self.setLayout(layout)
        
    def save_pdf(self):
        from PyQt5.QtGui import QTextDocument, QPdfWriter
        
        default_name = f"Check_{self.data['client']}_{self.data['id']}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Зберегти чек як PDF", default_name, "PDF Files (*.pdf)")
        
        if path:
            writer = QPdfWriter(path)
            doc = QTextDocument()
            doc.setHtml(self.html_content)
            doc.print_(writer)
            
            conn = sqlite3.connect(DB) 
            cur = conn.cursor()
            cur.execute("UPDATE orders SET receipt_path=? WHERE id=?", (path, self.data['id']))
            conn.commit()
            conn.close()
            
            self.accept() 
            QMessageBox.information(self, "Успіх", f"Чек успішно збережено за адресою:\n{path}")

class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Гарячі клавіші")
        self.resize(380, 350)
        
        layout = QVBoxLayout()
        
        title = QLabel("Довідник комбінацій клавіш")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        info = QLabel("""
        <table width="100%" cellpadding="10" cellspacing="0">
            <tr><td style="background:#f5f5f5; border-radius:5px; width:45%;"><b>Ctrl + N</b></td>
                <td>Нове замовлення</td></tr>
            <tr><td style="background:#f5f5f5; border-radius:5px;"><b>Ctrl + F</b></td>
                <td>Пошук по клієнтах</td></tr>
            <tr><td style="background:#f5f5f5; border-radius:5px;"><b>F2</b> або <b>Подв. клік</b></td>
                <td>Редагувати замовлення</td></tr>
            <tr><td style="background:#f5f5f5; border-radius:5px;"><b>Ctrl + D</b></td>
                <td>Відмітити як "Виконано"</td></tr>
            <tr><td style="background:#f5f5f5; border-radius:5px;"><b>Delete</b></td>
                <td>Видалити замовлення</td></tr>
            <tr><td style="background:#f5f5f5; border-radius:5px;"><b>Ctrl + P</b></td>
                <td>Згенерувати PDF-чек</td></tr>
            <tr><td style="background:#f5f5f5; border-radius:5px;"><b>F5</b></td>
                <td>Оновити базу даних</td></tr>
        </table>
        """)
        info.setTextFormat(Qt.RichText)
        info.setStyleSheet("font-size: 13px;")
        layout.addWidget(info)
        
        close_btn = QPushButton("Зрозуміло")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            background-color: #2196F3; 
            color: white; 
            font-weight: bold; 
            padding: 8px; 
            border-radius: 5px;
        """)
        
        layout.addStretch()
        layout.addWidget(close_btn)
        self.setLayout(layout)