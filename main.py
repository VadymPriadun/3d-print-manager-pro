import sys
from PyQt5.QtWidgets import QApplication

from app.database import init_db
from app.ui import LoginWindow

def main():
    # Ініціалізуємо БД
    init_db()

    # Запускаємо PyQt застосунок
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()