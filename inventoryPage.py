from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QSizePolicy
    )

from quantityControlDialog import QuantityControlDialog
from logger import DBG_logger


class inventoryTableWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create a vertical layout and set it for the widget
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create the table widget
        self.table_widget = QTableWidget()
        self.table_widget.setMinimumSize(600, 400)
        self.table_widget.setObjectName("inventory_table")
        self.table_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)  # Select all rows
        self.table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Can't modify the table value

        # Set column headers
        headers = ["品名", "Code", "數量"]
        self.table_widget.setColumnCount(len(headers))
        self.table_widget.setHorizontalHeaderLabels(headers)

        # Set column widths
        self.table_widget.setColumnWidth(0, 200)
        self.table_widget.setColumnWidth(1, 90)
        self.table_widget.setColumnWidth(2, 90)

        # Add table widget to the layout
        self.layout.addWidget(self.table_widget)

        # stop keyPressEvent in this widget
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def update_table(self, data_dict):
        sorted_data = sorted(data_dict.items(), key=lambda item: item[0])
        self.table_widget.setRowCount(len(sorted_data))

        for row, (code, details) in enumerate(sorted_data):
            item_name = QTableWidgetItem(details['name'])
            item_code = QTableWidgetItem(code)
            item_quantity = QTableWidgetItem(str(details['quantity']))

            self.table_widget.setItem(row, 0, item_name)
            self.table_widget.setItem(row, 1, item_code)
            self.table_widget.setItem(row, 2, item_quantity)

class InventoryPage(QWidget):
    def __init__(self, app, inventoryManager):
        super().__init__()
        self.app = app
        self.inventoryManager = inventoryManager
        
        self.input_text = ""
        self.scan_btn_state = False
        self.scan_mode = None
        
        self.setup_ui()
        self.setup_link()

    def get_table_name(self):
        index = self.app.tab_widget.currentIndex()
        table_name = self.app.tab_widget.tabText(index)
        return table_name

    def setup_ui(self):
        inventory_layout = QVBoxLayout()
        self.inventory_table = inventoryTableWidget()
        inventory_layout.addWidget(self.inventory_table)

        button_layout = QVBoxLayout()
        inventory_layout.addLayout(button_layout)

        # self.refresh_btn = QPushButton(f"Refresh")
        # button_layout.addWidget(self.refresh_btn)

        self.quantity_control_button = QPushButton(f"Quantity Control")
        button_layout.addWidget(self.quantity_control_button)

        horizontal_buttons_layout = QHBoxLayout()
        self.inventory_table_scan_btn = QPushButton("Scan")
        horizontal_buttons_layout.addWidget(self.inventory_table_scan_btn)
        self.inventory_table_plus_btn = QPushButton("+")
        horizontal_buttons_layout.addWidget(self.inventory_table_plus_btn)
        self.inventory_table_minus_btn = QPushButton("-")
        horizontal_buttons_layout.addWidget(self.inventory_table_minus_btn)

        button_layout.addLayout(horizontal_buttons_layout)
        self.inventory_table_write_btn = QPushButton("Write")
        button_layout.addWidget(self.inventory_table_write_btn)
        inventory_layout.addLayout(button_layout)
        self.setLayout(inventory_layout)

    # def refresh_btn_clicked(self):
    #     DBG_logger.logger.debug("refresh_btn_clicked")
    #     inventory_dict = self.inventoryManager._get_inventory_dict(self.get_table_name())
    #     self.inventory_table.update_table(inventory_dict)
    
    def show_dialog(self):
        dialog = QuantityControlDialog(self)
        if dialog.exec():
            code, number = dialog.get_input()
            
            try:
                number = int(number)
            except ValueError:
                DBG_logger.logger.warning(f"Invalid input for number: {number}. Must be an integer.")
                return

            DBG_logger.logger.info(f"QuantityControlDialog Code: {code}, Number: {number}")
            self.inventoryManager.update_quantity(self.get_table_name(), code, int(number))

        inventory_dict = self.inventoryManager._get_inventory_dict(self.get_table_name())
        self.inventory_table.update_table(inventory_dict)

    def inventory_table_scan_clicked(self):
        DBG_logger.logger.debug("inventory_table_scan_clicked")
        self.scan_btn_state = not self.scan_btn_state
        self.app.scan_status_label.setText("Scan ON" if self.scan_btn_state else "Scan OFF")

    def inventory_table_plus_clicked(self):
        DBG_logger.logger.debug("inventory_table_plus_clicked")
        self.scan_mode = 0
        self.app.scan_mode_status_label.setText("+")

    def inventory_table_minus_clicked(self):
        DBG_logger.logger.debug("inventory_table_minus_clicked")
        self.scan_mode = 1
        self.app.scan_mode_status_label.setText("-")

    def inventory_table_write_clicked(self):
        DBG_logger.logger.debug("inventory_table_write_clicked")
        self.inventoryManager.save_inventory_to_file(self.get_table_name())

    def setup_link(self):
        self.quantity_control_button.clicked.connect(self.show_dialog)
        # self.refresh_btn.clicked.connect(self.refresh_btn_clicked)
        self.inventory_table_scan_btn.clicked.connect(self.inventory_table_scan_clicked)
        self.inventory_table_plus_btn.clicked.connect(self.inventory_table_plus_clicked)
        self.inventory_table_minus_btn.clicked.connect(self.inventory_table_minus_clicked)
        self.inventory_table_write_btn.clicked.connect(self.inventory_table_write_clicked)

    def scan_num(self):
        if self.scan_mode == 0:
            num = 1
        elif self.scan_mode == 1:
            num = -1
        else:
            num = 0
        return num

    def keyPressEvent(self, event):
        self.setFocus()
        super().keyPressEvent(event)
        add_num = self.scan_num()

        print(f"Key pressed: {event.text()} (Key code: {event.key()})")
        key_text = event.text()

        if not self.scan_btn_state:
            DBG_logger.logger.info("非掃描添加模式")
            return

        if key_text.isdigit():
            self.input_text += key_text
 
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not self.input_text.isdigit():
                self.input_text = ""  # 清空輸入以避免後續處理錯誤
                DBG_logger.logger.info("滑鼠點擊 Tablewidget 顯示視窗")
            
            print(f"scan: {self.scan_btn_state}, scan mode: {self.scan_mode}, add_num: {add_num}")
            DBG_logger.logger.debug(f" scan: {self.scan_btn_state}, scan mode: {self.scan_mode}, add_num: {add_num}")

            self.inventoryManager.update_quantity(self.get_table_name(), self.input_text, add_num)
            self.input_text = ""
            
            inventory_dict = self.inventoryManager._get_inventory_dict(self.get_table_name())
            self.inventory_table.update_table(inventory_dict)
        else:
            DBG_logger.logger.info("輸入法有誤")
            self.input_text = ""