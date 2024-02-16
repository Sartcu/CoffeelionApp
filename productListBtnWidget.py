from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal
import json
from logger import DBG_logger

class productListBtnWidget(QWidget):
    quantityChanged = pyqtSignal(str, int)
    increaseQuantity = pyqtSignal(str)
    decreaseQuantity = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # read 'coffeelionProductList.json'
        with open('coffeelionProductList.json', 'r') as file:
            data = json.load(file)

        max_name_width = max(len(item["Name"]) for item in data["CoffeeLineProduct"])

        # 根據 JSON 中的項目數量新增按鈕
        for item in data["CoffeeLineProduct"]:
            code = item["Code"]
            name = item["Name"]
            price = item["Price"]

            # 新增水平布局
            hbox = QHBoxLayout()

            # 新增 QLabel 顯示名稱
            name_label = QLabel(f'{name}', self)
            # 調整價格標籤寬度以避免價格被蓋住
            name_label.setFixedWidth(max_name_width * 10 + 30)  # 加上一些額外空間
            hbox.addWidget(name_label)

            # 新增 QLabel 顯示code
            code_label = QLabel(f'{code}', self)
            code_label.setFixedWidth(max_name_width * 10)  # 加上一些額外空間
            hbox.addWidget(code_label)

            # 新增 QLabel 顯示價格
            price_label = QLabel(f'{price:.1f}', self)
            # 調整價格標籤寬度以避免價格被蓋住
            price_label.setFixedWidth(max_name_width * 5)  # 加上一些額外空間
            hbox.addWidget(price_label)

            # 新增 Item +1 按鈕
            btn_plus = QPushButton(f'+1', self)
            btn_plus.setFixedSize(50, 30)  # 設置按鈕大小
            btn_plus.clicked.connect(lambda checked, name=name, price=price: self.on_plus_clicked(name))
            hbox.addWidget(btn_plus)

            # 新增 Item -1 按鈕
            btn_minus = QPushButton(f'-1', self)
            btn_minus.setFixedSize(50, 30)  # 設置按鈕大小
            btn_minus.clicked.connect(lambda checked, name=name, price=price: self.on_minus_clicked(name))
            hbox.addWidget(btn_minus)

            layout.addLayout(hbox)

    def on_plus_clicked(self, name):
        self.increaseQuantity.emit(name)
        DBG_logger.logger.debug(f"order {name} +1")

    def on_minus_clicked(self, name):
        self.decreaseQuantity.emit(name)
        DBG_logger.logger.debug(f"order {name} -1")

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = productListBtnWidget()
    window.show()
    sys.exit(app.exec())