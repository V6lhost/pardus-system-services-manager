import signal, sys
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QDialogButtonBox,
    QHeaderView
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import (
    QFile,
    Qt,
    QSortFilterProxyModel,
    QUrl,
    QSize,
    QThread,
    QTimer,
    Signal
)
from PySide6.QtGui import (
    QStandardItem,
    QStandardItemModel,
    QIcon,
    QDesktopServices
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

class UnitListReloadThread(QThread):
    # Use qthread to prevent gui lags. otherwise reloading unit list blockes the gui thread and causes freeze(and sometimes crashes)
    add_units = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
    
    def run(self):
        units = list_systemd_units()
        for row,unit in enumerate(units):
            units[row]["active_status"] = get_unit_active_status(unit["unit_file"])
        
        units = sorted(units, key=lambda x: x["unit_file"].lower())
        self.add_units.emit(units)

def load_ui(ui_path, baseinstance=None):
    loader = UiLoader(baseinstance)
    ui_file = QFile(ui_path)
    if not ui_file.open(QFile.ReadOnly):
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

        self.groupBoxUnitDetails.hide()
        self.groupBoxApplicationDetails.hide()

        self.tableProxyModel = QSortFilterProxyModel(self)
        self.tableProxyModel.setSourceModel(self.tableModel)
        self.tableProxyModel.setFilterKeyColumn(0)
        self.tableProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.tableViewUnits.setModel(self.tableProxyModel)

        self.stackedWidget.setCurrentIndex(0)

        self.units = []
        
        self.thread = UnitListReloadThread(self)
        self.thread.add_units.connect(self.add_units_to_gui)

        self.timerUpdateUnits = QTimer()
        self.timerUpdateUnits.timeout.connect(self.thread.start)
        self.timerUpdateUnits.start(5000)

        # call the thread manually once to load ui faster
        self.thread.start()

        self.add_autostart_applications_to_gui()
        self.connect_ui_events()

    def add_units_to_gui(self, units):
        if units == self.units:
            return
        self.units = units

        # get selected unit name to reselect it after updating table
        self.selected_unit_name = None
        selected_indexes = self.tableViewUnits.selectionModel().selectedRows()
        if selected_indexes:
            proxy_index = selected_indexes[0]
            source_index = self.tableProxyModel.mapToSource(proxy_index)
            name_item = self.tableModel.item(source_index.row(), 0)
            if name_item:
                self.selected_unit_name = name_item.text()

        self.tableViewUnits.clearSelection()
        self.tableModel.clear()
        self.tableModel.setHorizontalHeaderLabels(["Name", "State", "Active Status"])

        for unit in units:
            unit_name = unit["unit_file"]
            unit_state = unit["state"]
            unit_active_status = unit["active_status"]

            item_name = QStandardItem(unit_name)
            item_state = QStandardItem(unit_state)
            item_active_status = QStandardItem(unit_active_status)

            self.tableModel.appendRow([item_name, item_state, item_active_status])

            if unit_active_status == "failed":
                item_active_status.setForeground(Qt.red)
            elif unit_active_status == "active":
                item_active_status.setForeground(Qt.green)
            elif unit_active_status == "inactive":
                item_active_status.setForeground(Qt.yellow)
            else:
                item_active_status.setForeground(Qt.gray)
        
            # reselect the latest selected unit again. this also helps to update the unit description part automatically
            if self.selected_unit_name:
                for row in range(self.tableModel.rowCount()):
                    item = self.tableModel.item(row, 0)
                    if item and item.text() == self.selected_unit_name:
                        source_index = self.tableModel.index(row, 0)
                        proxy_index = self.tableProxyModel.mapFromSource(source_index)
                        
                        if proxy_index.isValid():
                            self.tableViewUnits.setCurrentIndex(proxy_index)
                            self.tableViewUnits.selectRow(proxy_index.row())

    def fill_unit_details(self, unit_name, unit_state, unit_active_state, unit_active_state_color): # take unit state and active state from table instead of check again because checking again takes some time
        self.groupBoxUnitDetails.show()
        self.labelUnitNameText.setText(unit_name)

        unit_description = get_unit_description(unit_name)
        self.labelUnitDescriptionText.setText(unit_description)

        self.radioButtonUnitEnabled.setChecked(True if unit_state == "enabled" else False)
        self.radioButtonUnitEnabled.setEnabled(True if unit_state in ["enabled", "disabled", "alias"] else False)

        self.pushButtonUnitStartRestart.setEnabled(True if unit_active_state != "activation is not possible" else False)
        self.pushButtonUnitStop.setEnabled(True if unit_active_state == "active" else False)

        self.labelUnitLoadStatusText.setText(unit_state)
        self.labelUnitActiveStatusText.setText(unit_active_state)
        self.labelUnitActiveStatusText.setStyleSheet(f"color: {unit_active_state_color};")
    
        unit_status = get_unit_exit_status(unit_name)
        self.labelUnitSubStatusText.setText(f"{unit_status['status']}\n{unit_status['result']}")
        self.labelUnitExitCodeText.setText(f"{unit_status['code']}")

        self.pushButtonEditUnitFile.setEnabled(True if not "@" in unit_name else False)

    def fill_application_details(self, entry):
        self.groupBoxApplicationDetails.show()
        application_details = get_application_details(entry)

        theme_icon = QIcon.fromTheme(application_details["icon"])
        pixmap = theme_icon.pixmap(QSize(64, 64))

        self.labelIcon.setPixmap(pixmap)

        self.labelApplicationNameText.setText(application_details["name"])
        self.labelApplicationDescriptionText.setText(application_details["comment"])
        self.labelEntryFilePath.setText(str(entry))

    def add_autostart_applications_to_gui(self):
        autostart_applications_dir = Path.home() / Path(".config/autostart")
        entries = list_desktop_entries(autostart_applications_dir)
        self.listModel.clear()
        for entry in entries:
            application_details = get_application_details(entry)
            item = QStandardItem(application_details["name"])
            icon = QIcon.fromTheme(application_details["icon"])
            item.setIcon(icon)
            item.setData(entry, Qt.UserRole)
            self.listModel.appendRow(item)
    
    def add_application_to_autostart(self, entry_path):
        autostart_applications_dir = Path.home() / Path(".config/autostart")
        copy_desktop_entry(entry_path, autostart_applications_dir)
        self.add_autostart_applications_to_gui() # refresh the autostart applications list
    
    def filter_units(self, text):
        self.tableProxyModel.setFilterFixedString(text)
    
    def open_file(self, path):
        url = QUrl.fromLocalFile(path)
        QDesktopServices.openUrl(url)
        
    def connect_ui_events(self):
        self.pushButtonAutostartApplications.toggled.connect(lambda page_id: self.stackedWidget.setCurrentIndex(page_id))
        self.pushButtonAddApplication.clicked.connect(self.open_applications_dialog)
        self.lineEditSearchUnits.textChanged.connect(self.filter_units)
        self.tableViewUnits.selectionModel().selectionChanged.connect(self.on_unit_item_clicked)
        self.pushButtonEditUnitFile.clicked.connect(self.open_edit_unit_warning_dialog)
        self.pushButtonUnitShowLogs.clicked.connect(lambda: self.open_file(save_logs_to_temporary_file(self.labelUnitNameText.text())))
    
        self.listViewAutostartApplications.selectionModel().selectionChanged.connect(self.on_application_item_clicked)
        self.pushButtonEditEntryFile.clicked.connect(lambda: self.open_file(Path(self.labelEntryFilePath.text())))
        self.pushButtonRemoveFromAutostart.clicked.connect(self.remove_current_entry_file)

        self.radioButtonUnitEnabled.clicked.connect(self.set_unit_enabled)
        self.pushButtonUnitStartRestart.clicked.connect(self.start_restart_unit)
        self.pushButtonUnitStop.clicked.connect(self.stop_unit)

    def remove_current_entry_file(self):
        entry = self.labelEntryFilePath.text()
        path = Path(entry)
        remove_autostart_entry_file(path)
        self.add_autostart_applications_to_gui()

    def on_unit_item_clicked(self, selected):
        indexes = selected.indexes()
        if not indexes:
            return
        
        proxy_index = indexes[0]
        source_index = self.tableProxyModel.mapToSource(proxy_index)
        row = source_index.row()
        name_item = self.tableModel.item(row, 0)
        state_item = self.tableModel.item(row, 1)
        active_state_item = self.tableModel.item(row, 2)
        active_state_color = active_state_item.foreground().color()

        if name_item:
            self.fill_unit_details(name_item.text(), state_item.text(), active_state_item.text(), active_state_color.name())
    
    def on_application_item_clicked(self, selected):
        indexes = selected.indexes()
        if not indexes:
            return

        index = indexes[0]
        self.fill_application_details(index.data(Qt.UserRole))

    def set_unit_enabled(self):
        self.radioButtonUnitEnabled.setEnabled(False)
        if self.radioButtonUnitEnabled.isChecked():
            unit_enable(self.labelUnitNameText.text())
        else:
            unit_disable(self.labelUnitNameText.text())
        self.radioButtonUnitEnabled.setEnabled(True)
    
    def start_restart_unit(self):
        self.pushButtonUnitStartRestart.setEnabled(False)
        if self.labelUnitActiveStatusText.text() == "active":
            unit_restart(self.labelUnitNameText.text())
        else:
            unit_start(self.labelUnitNameText.text())
        self.pushButtonUnitStartRestart.setEnabled(True)

    def stop_unit(self):
        self.pushButtonUnitStop.setEnabled(False)
        unit_stop(self.labelUnitNameText.text())
        self.pushButtonUnitStop.setEnabled(True)

    def open_applications_dialog(self):
        applications_dialog = ApplicationsDialog(self)
        result = applications_dialog.exec()

        if result == QDialog.Accepted:
            self.add_application_to_autostart(applications_dialog.entry_path)
            self.add_autostart_applications_to_gui()
    
    def open_edit_unit_warning_dialog(self):
        unit_name = self.labelUnitNameText.text()
        warning_dialog = EditUnitWarningDialog(self, unit_name=unit_name)
        result = warning_dialog.exec()

        if result == QDialog.Accepted:
            self.open_file(get_unit_file_path(unit_name))

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
        self.listViewApplications.doubleClicked.connect(self.get_selected_application)
    
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

class EditUnitWarningDialog(QDialog):
    def __init__(self, parent=None, unit_name=None):
        super(EditUnitWarningDialog, self).__init__()

        current_dir = Path(__file__).resolve().parent
        ui_path = current_dir.parent / "ui" / "EditUnitWarningDialog.ui"
        load_ui(ui_path, self)

        self.labelUnitNameText.setText(unit_name)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL) # Handle CTRL+C interrupt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
