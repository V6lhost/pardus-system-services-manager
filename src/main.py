import signal, sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile,
    Qt
)
from PySide6.QtGui import (
    QStandardItem,
    QStandardItemModel,
    QIcon
)

from helper_functions import *

# Custom ui loader class and function to make the code cleaner
class UiLoader(QUiLoader):
    def __init__(self, baseinstance):
        super().__init__()
        self.baseinstance = baseinstance

    def createWidget(self, class_name, parent=None, name=""):
        if parent is None and self.baseinstance:
            return self.baseinstance
        return super().createWidget(class_name, parent, name)

def load_ui(ui_path, baseinstance=None):
    loader = UiLoader(baseinstance)
    ui_file = QFile(ui_path)
    if not ui_file.open(QFile.ReadOnly):
        print(f"Error while loading ui file: {ui_path}")
        return None
    widget = loader.load(ui_file)
    ui_file.close()
    return widget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        current_dir = Path(__file__).resolve().parent
        ui_path = current_dir.parent / "ui" / "MainWindow.ui"
        load_ui(ui_path, self)

        self.listModel = QStandardItemModel(self)
        self.listViewAutostartApplications.setModel(self.listModel)
        self.stackedWidget.setCurrentIndex(0)
        self.tableWidgetServices.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.connect_ui_events()

        self.add_units_to_gui()
        self.add_autostart_applications_to_gui()

    def add_units_to_gui(self):
        units = list_systemd_units()
        self.tableWidgetServices.setRowCount(len(units))
        for row, unit in enumerate(units):
            unit_path = unit[0]
            unit_name = unit_path.split("/")[-1]
            unit_state = unit[1]
            unit_active_status = get_unit_active_status(unit_name)
            self.tableWidgetServices.setItem(
                row, 0, QTableWidgetItem(unit_name)
            )
            self.tableWidgetServices.setItem(
                row, 1, QTableWidgetItem(unit_state)
            )
            self.tableWidgetServices.setItem(
                row, 2, QTableWidgetItem(unit_active_status)
            )

    def add_autostart_applications_to_gui(self):
        autostart_applications_dir = Path.home() / Path(".config/autostart")
        entries = list_desktop_entries(autostart_applications_dir)
        for entry in entries:
            application_details = get_application_details(entry)
            item = QStandardItem(application_details["name"])
            icon = QIcon.fromTheme(application_details["icon"])
            item.setIcon(icon)
            self.listModel.appendRow(item)
        
    def connect_ui_events(self):
        self.pushButtonAutostartApplications.toggled.connect(lambda page_id: self.stackedWidget.setCurrentIndex(page_id))

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL) # Handle CTRL+C interrupt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())