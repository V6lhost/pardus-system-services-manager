import signal, sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QDialogButtonBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile,
    Qt,
    QSortFilterProxyModel
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

        self.tableModel = QStandardItemModel(self)
        self.tableViewUnits.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.tableProxyModel = QSortFilterProxyModel(self)
        self.tableProxyModel.setSourceModel(self.tableModel)
        self.tableProxyModel.setFilterKeyColumn(0)
        self.tableProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.tableViewUnits.setModel(self.tableProxyModel)

        self.stackedWidget.setCurrentIndex(0)

        self.connect_ui_events()

        self.add_units_to_gui()
        self.add_autostart_applications_to_gui()

    def add_units_to_gui(self):
        units = list_systemd_units()

        self.tableModel.clear()
        self.tableModel.setHorizontalHeaderLabels(["Name", "State", "Active Status"])

        for unit in units:
            unit_path = unit[0]
            unit_name = unit_path.split("/")[-1]
            unit_state = unit[1]
            unit_active_status = get_unit_active_status(unit_name)

            item_name = QStandardItem(unit_name)
            item_state = QStandardItem(unit_state)
            item_active_status = QStandardItem(unit_active_status)

            self.tableModel.appendRow([item_name, item_state, item_active_status])

            if unit_active_status.lower() == "failed":
                item_active_status.setForeground(Qt.red)
            elif unit_active_status.lower() == "active":
                item_active_status.setForeground(Qt.green)
            elif unit_active_status.lower() == "inactive":
                item_active_status.setForeground(Qt.yellow)
            else:
                item_active_status.setForeground(Qt.gray)

    def add_autostart_applications_to_gui(self):
        autostart_applications_dir = Path.home() / Path(".config/autostart")
        entries = list_desktop_entries(autostart_applications_dir)
        self.listModel.clear()
        for entry in entries:
            application_details = get_application_details(entry)
            item = QStandardItem(application_details["name"])
            icon = QIcon.fromTheme(application_details["icon"])
            item.setIcon(icon)
            self.listModel.appendRow(item)
    
    def add_application_to_autostart(self, entry_path):
        autostart_applications_dir = Path.home() / Path(".config/autostart")
        copy_desktop_entry(entry_path, autostart_applications_dir)
        self.add_autostart_applications_to_gui() # refresh the autostart applications list
    
    def filter_units(self, text):
        self.tableProxyModel.setFilterFixedString(text)
        
    def connect_ui_events(self):
        self.pushButtonAutostartApplications.toggled.connect(lambda page_id: self.stackedWidget.setCurrentIndex(page_id))
        self.pushButtonAddApplication.clicked.connect(self.open_applications_dialog)
        self.lineEditSearchUnits.textChanged.connect(self.filter_units)

    def open_applications_dialog(self):
        applications_dialog = ApplicationsDialog(self)
        result = applications_dialog.exec()

        if result == QDialog.Accepted:
            self.add_application_to_autostart(applications_dialog.entry_path)

class ApplicationsDialog(QDialog):
    def __init__(self, parent=None):
        super(ApplicationsDialog, self).__init__()

        current_dir = Path(__file__).resolve().parent
        ui_path = current_dir.parent / "ui" / "ApplicationsDialog.ui"
        load_ui(ui_path, self)

        self.listModel = QStandardItemModel(self)

        # Use a proxy model for filtering purposes
        self.proxy_model = QSortFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.listModel)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.listViewApplications.setModel(self.proxy_model)

        self.ok_button = self.buttonBox.button(QDialogButtonBox.Ok)

        self.add_applications_to_gui()
        self.connect_ui_events()
    
    def add_applications_to_gui(self):
        paths = [Path("/usr/share/applications"), Path("/usr/local/share/applications"), (Path.home() / ".local/share/applications")]

        for path in paths:
            try:
                entries = list_desktop_entries(path)
            except:
                pass
            else:
                for entry in entries:
                    application_details = get_application_details(entry)
                    item = QStandardItem(application_details["name"])
                    icon = QIcon.fromTheme(application_details["icon"])
                    item.setIcon(icon)
                    item.setData(entry, Qt.UserRole)
                    self.listModel.appendRow(item)
    
    def connect_ui_events(self):
        self.lineEditSearch.textChanged.connect(self.filter_list)
        self.ok_button.pressed.connect(self.get_selected_application)
    
    def filter_list(self, text):
        self.proxy_model.setFilterFixedString(text)
    
    def get_selected_application(self):
        selected_index = self.listViewApplications.currentIndex()
    
        if not selected_index.isValid():
            self.reject()
            return
        
        source_index = self.proxy_model.mapToSource(selected_index) # Convert the proxy model to original before getting data
        self.entry_path = source_index.data(Qt.UserRole)

        self.accept()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL) # Handle CTRL+C interrupt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())