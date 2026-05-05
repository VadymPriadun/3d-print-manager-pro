# 🖨️ 3D Print Manager PRO

> Desktop application for managing orders and tracking material usage in 3D printing.

## 📌 Description

**3D Print Manager PRO** is a local desktop application designed to simplify order management in 3D printing studios or educational labs.

**The app allows you to:**

* manage orders;
* track material (filament) usage;
* automatically calculate costs;
* generate PDF receipts;
* export data to Excel;
* analyze material consumption.

---

## 🧠 Features

### 📦 Order Management

* create, edit, and delete orders;
* change status (in progress / completed);
* search by client;
* color status indicators.

### 🏭 Material Tracking

* add and edit materials;
* monitor stock levels;
* automatic material deduction.

### 💰 Finance

Automatic cost calculation using the formula:
`cost = (weight / 1000) * price_per_kg`

### 📄 Reports

* generate PDF receipts;
* export to Excel (`.xlsx`);
* build usage charts.

### ⚡ UX

* keyboard shortcuts;
* session saving (Remember me);
* simple and clear GUI.

---

## 🏗️ Architecture

The application is built as a local desktop app and consists of:

* GUI (`PyQt5`)
* Business logic
* `SQLite` database

Database includes 2 main tables:

1. `orders` — orders
2. `plastic` — materials

---

## 🛠️ Technologies

* Python 3
* PyQt5
* SQLite3
* matplotlib
* openpyxl

---

## 🚀 Run

Clone the repository and install dependencies:

```bash
git clone https://github.com/your_username/3d-print-manager.git
cd 3d-print-manager
pip install -r requirements.txt
python main.py
```

---

## 🔐 Default Login

Login: admin
Password: 1234

---

## 🗄️ Database

SQLite is used. The database:

* is created automatically on first launch;
* is stored locally at: `Documents/3D_Print_Manager/`

---

## 📸 Interface



<img width="322" height="453" alt="Знімок екрана 2026-05-04 о 14 09 36" src="https://github.com/user-attachments/assets/782ef3cd-257f-480b-b31f-a280673a33fe" />



<img width="1728" height="982" alt="Знімок екрана 2026-05-04 о 14 02 03" src="https://github.com/user-attachments/assets/991081f3-2f48-4c56-9f93-24fabac148fb" />



<img width="1728" height="982" alt="Знімок екрана 2026-05-04 о 14 03 33" src="https://github.com/user-attachments/assets/1f2ee472-8c15-43a1-8373-08cae20faf2f" />



<img width="397" height="534" alt="Знімок екрана 2026-05-04 о 14 04 24" src="https://github.com/user-attachments/assets/c5843ab1-11cb-4841-813a-504b6a765903" />



---

## ⚠️ Limitations

* no multi-user system;
* simplified authentication;
* local database only (no server connection).

---

## 📈 Future Improvements

* [ ] move logic into separate modules
* [ ] add API
* [ ] multi-user system with roles
* [ ] cloud storage (backups)

---

## 👨‍💻 Author

Computer Science student.

Developed as part of academic practice.
