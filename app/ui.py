from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QFont, QCursor, QColor, QKeySequence

import sqlite3

from .database import DB
from .dialogs import OrderDialog, ReceiptDialog, ShortcutsDialog