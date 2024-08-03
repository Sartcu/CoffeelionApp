from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSizePolicy, QComboBox, QMessageBox)
from logger import DBG_logger
from orderTableWidget import orderTableWidget
from productListBtnWidget import productListBtnWidget
import time, os
from functools import partial

application_path = os.path.dirname(os.path.abspath(__file__))
record_file_path = os.path.join(application_path, 'recorder.txt')

def write_to_record_file(message):
    with open(record_file_path, "a") as file:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        file.write(f"{current_time} - {message}\n")

class CheckoutPage(QWidget):
    def __init__(self, app, manager):
        super().__init__()
        self.app = app
        self.manager = manager

        self.input_text = ""
        self.pay_method = 'Cash'
        self.order_num = 0
        
        self.setup_ui()
        self.setup_link()

    def setup_ui(self):
        checkout_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        checkout_layout.addLayout(left_layout)

        self.order_table = orderTableWidget()
        self.order_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.order_table)

        self.create_order_buttons(left_layout)
        self.create_scan_buttons(left_layout)

        self.product_list_widget = productListBtnWidget()
        self.product_list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        checkout_layout.addWidget(self.product_list_widget)

        self.setLayout(checkout_layout)

    def create_order_buttons(self, layout):
        order_button_layout = QHBoxLayout()
        layout.addLayout(order_button_layout)

        self.order_button = QPushButton("Order")
        order_button_layout.addWidget(self.order_button)

        self.checkout_button = QPushButton("Checkout")
        order_button_layout.addWidget(self.checkout_button)

        self.payment_combo = QComboBox()
        self.payment_combo.addItem("Cash")
        self.payment_combo.addItem("LinePay")
        order_button_layout.addWidget(self.payment_combo)

    def create_scan_buttons(self, layout):
        scan_button_layout = QHBoxLayout()
        layout.addLayout(scan_button_layout)

        self.scan_button = QPushButton("Scan")
        scan_button_layout.addWidget(self.scan_button)
        
        self.scan_plus_button = QPushButton("+")
        scan_button_layout.addWidget(self.scan_plus_button)
        
        self.scan_minus_button = QPushButton("-")
        scan_button_layout.addWidget(self.scan_minus_button)
        
    def order_btn_clicked(self):
        DBG_logger.logger.debug("order_btn_clicked")
        self.manager.order_clear()

    def checkout_btn_clicked(self):
        DBG_logger.logger.debug("checkout_btn_clicked")
        write_to_record_file(f"===== Customer {self.order_num} =====")
        order_summary, sum_total_item_price = self.create_order_summary()

        write_to_record_file(f"Total Price: {sum_total_item_price} TWD")
        write_to_record_file(f"Payment: {self.pay_method}")
        write_to_record_file(f"===== END {self.order_num} ===== \n")

        self.show_order_summary(order_summary, sum_total_item_price)
        self.reset_order()

    def create_order_summary(self):
        order_summary = ""
        sum_total_item_price = 0
        for product, details in self.manager.products_dict.items():
            price = details['Price']
            nums = details['Numbers']
            sum_each_item_price = price * nums

            if nums > 0:
                order_summary += f"{product}: {price} * {nums} = {sum_each_item_price}\n"
                write_to_record_file(f"{product}: {price} * {nums} = {sum_each_item_price}")
                sum_total_item_price += sum_each_item_price
        return order_summary, sum_total_item_price

    def show_order_summary(self, order_summary, sum_total_item_price):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("訂購清單")
        msg_box.setText(f"訂購清單: \n{order_summary}\n\n 總價: {sum_total_item_price} 元 \n\n 支付方式: {self.pay_method}")
        msg_box.exec()

    def reset_order(self):
        self.order_num += 1
        self.manager.print_current_quantities()
        self.manager.order_clear()

    def scan_btn_clicked(self):
        DBG_logger.logger.debug("scan_btn_clicked")
        self.app.scan_btn_state = not self.app.scan_btn_state
        self.app.scan_status_label.setText("Scan ON" if self.app.scan_btn_state else "Scan OFF")

    def scan_plus_clicked(self):
        DBG_logger.logger.debug("scan_plus_btn_clicked")
        self.scan_mode = 0
        self.app.scan_mode_status_label.setText("+")

    def scan_minus_clicked(self):
        DBG_logger.logger.debug("scan_minus_btn_clicked")
        self.scan_mode = 1
        self.app.scan_mode_status_label.setText("-")

    def update_pay_method(self, index):
        self.pay_method = 'Cash' if index == 0 else 'LinePay'

    def setup_link(self):
        self.order_button.clicked.connect(self.order_btn_clicked)
        self.checkout_button.clicked.connect(self.checkout_btn_clicked)
        self.scan_button.clicked.connect(self.scan_btn_clicked)
        self.scan_plus_button.clicked.connect(self.scan_plus_clicked)
        self.scan_minus_button.clicked.connect(self.scan_minus_clicked)

        self.product_list_widget.increaseQuantity.connect(self.manager.increase_quantity_from_signal)
        self.product_list_widget.decreaseQuantity.connect(self.manager.decrease_quantity_from_signal)
        self.manager.updateTable.connect(partial(self.order_table.update_order_table, self.manager))
        self.app.scanModeSignal.connect(self.manager.scan_mode_from_signal)
        self.payment_combo.currentIndexChanged.connect(self.update_pay_method)
    
    def keyPressEvent(self, event):
        self.setFocus()
        super().keyPressEvent(event)
        # print(f"Key pressed: {event.text()} (Key code: {event.key()})")
        key_text = event.text()

        if not self.app.scan_btn_state:
            DBG_logger.logger.info("非掃描添加模式")
            return

        if key_text.isdigit():
            self.input_text += key_text
 
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not self.input_text.isdigit():
                self.input_text = ""  # 清空輸入以避免後續處理錯誤
                DBG_logger.logger.info("滑鼠點擊 Log 顯示視窗")

            DBG_logger.logger.debug(f"Scan {self.input_text} -> {self.manager.find_product_by_code(self.input_text)} mode {self.scan_mode}")
            print(f"Scan {self.input_text} -> {self.manager.find_product_by_code(self.input_text)} mode {self.scan_mode}")
            self.app.scanModeSignal.emit(str(self.manager.find_product_by_code(self.input_text)), int(self.scan_mode))
            self.input_text = ""
        else:
            DBG_logger.logger.info("輸入法有誤")
            self.input_text = ""

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = CheckoutPage(app)
    window.show()
    sys.exit(app.exec())