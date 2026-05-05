import sys
from PyQt5.QtWidgets import QApplication

from app.database import init_db
from app.ui import LoginWindow


if __name__ == "__main__":
    init_db()

    app = QApplication(sys.argv)

    login = LoginWindow()
    login.show()

    sys.exit(app.exec_())