import json
from PyQt6.QtCore import QObject, pyqtSignal
from logger import DBG_logger

import os
application_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(application_path, 'coffeelionProductList.json')

class ProductManager(QObject):
    updateTable = pyqtSignal()
    def __init__(self, file_path):
        super().__init__()
        self.products_dict = self.load_products(file_path)

    def load_products(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)

        products_dict = {}
        for product in data['CoffeeLineProduct']:
            product_info = {
                'Code': product['Code'],
                'Price': product['Price'],
                'Numbers': 0  # 初始數量為0
            }
            products_dict[product['Name']] = product_info

        return products_dict

    def find_product_by_code(self, code):
        for product_key, product_info in self.products_dict.items():
            if product_info['Code'] == code:
                return product_key
        return None

    def order_clear(self):
        for product_info in self.products_dict.values():
            product_info['Numbers'] = 0
        self.updateTable.emit()

    def increase_quantity(self, product_name, amount=1):
        if product_name in self.products_dict:
            self.products_dict[product_name]['Numbers'] += amount
            self.updateTable.emit()
        else:
            DBG_logger.logger.info(f"找不到產品 {product_name}")

    def decrease_quantity(self, product_name, amount=1):
        if product_name in self.products_dict:
            if self.products_dict[product_name]['Numbers'] >= amount:
                self.products_dict[product_name]['Numbers'] -= amount
                self.updateTable.emit()
            else:
                DBG_logger.logger.info(f"產品 {product_name} 的數量不足")
        else:
            DBG_logger.logger.info(f"找不到產品 {product_name}")

    def print_current_quantities(self):
        DBG_logger.logger.info("===== 當前產品數量：")
        for product_name, product_info in self.products_dict.items():
            if product_info['Numbers'] > 0:
                DBG_logger.logger.info(f"{product_name}: {product_info['Numbers']}")
        DBG_logger.logger.info("=====\n")
    def increase_quantity_from_signal(self, product_name):
        self.increase_quantity(product_name)
        # self.print_current_quantities()

    def decrease_quantity_from_signal(self, product_name):
        self.decrease_quantity(product_name)
        # self.print_current_quantities()

    def scan_mode_from_signal(self, product_name, mode):
        if mode == 0:
            self.increase_quantity_from_signal(product_name)
        elif mode == 1:
            self.decrease_quantity_from_signal(product_name)
        else:
            pass

if __name__ == '__main__':
    manager = ProductManager('coffeelionProductList.json')

    manager.increase_quantity('綜合水果凍乾(30g)', 3)
    manager.decrease_quantity('綜合水果凍乾(30g)', 2)

    # manager.print_current_quantities()
    print(f" 10101003 is {manager.find_product_by_code('10101003')}")
