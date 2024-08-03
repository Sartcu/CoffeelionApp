import sqlite3
import os
import json
from datetime import datetime

class InventoryManager:
    def __init__(self, db_name="coffeelion_inventory.db"):
        super().__init__()
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.official_inventory_dict = {}
        self.shopee_inventory_dict = {}
        self.create_table('Official')
        self.create_table('Shopee')
        self.load_inventory('Official')
        self.load_inventory('Shopee')

    def create_table(self, table_name):
        query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT UNIQUE,
            price REAL,
            quantity INTEGER NOT NULL DEFAULT 0
        )
        '''
        self.conn.execute(query)
        self.conn.commit()

    def add_item(self, table_name, name, code, price, quantity=0):
        try:
            query = f'INSERT INTO {table_name} (name, code, price, quantity) VALUES (?, ?, ?, ?)'
            self.conn.execute(query, (name, code, price, quantity))
            self.conn.commit()
            print(f"{name} (Code: {code}, Price: {price}, Quantity: {quantity}) added to {table_name}.")
            self._update_inventory_dict(table_name, code, name, price, quantity)
        except sqlite3.IntegrityError:
            print(f"Item with code {code} already exists. Use update_item to modify details.")

    def update_item(self, table_name, name, code, price):
        query = f'UPDATE {table_name} SET name = ?, price = ? WHERE code = ?'
        self.conn.execute(query, (name, price, code))
        self.conn.commit()
        print(f"{name} (Code: {code}, Price: {price}) updated in {table_name}.")
        self._update_inventory_dict(table_name, code, name, price)

    def remove_item(self, table_name, code):
        query = f'DELETE FROM {table_name} WHERE code = ?'
        self.conn.execute(query, (code,))
        self.conn.commit()
        print(f"Item with code {code} removed from {table_name}.")

        inventory_dict = self._get_inventory_dict(table_name)
        if code in inventory_dict:
            del inventory_dict[code]

    def update_quantity(self, table_name, code, quantity):
        query = f'''
        UPDATE {table_name}
        SET quantity = CASE
            WHEN quantity + ? < 0 THEN 0
            ELSE quantity + ?
        END
        WHERE code = ?
        '''
        self.conn.execute(query, (quantity, quantity, code))
        self.conn.commit()

        inventory_dict = self._get_inventory_dict(table_name)
        if code in inventory_dict:
            new_quantity = max(0, inventory_dict[code]['quantity'] + quantity)
            inventory_dict[code]['quantity'] = new_quantity
            print(f"Quantity for item code {code} updated. New quantity is {inventory_dict[code]['quantity']}.")

    def load_inventory(self, table_name):
        query = f'SELECT name, code, quantity, price FROM {table_name}'
        cursor = self.conn.execute(query)
        rows = cursor.fetchall()
        inventory_dict = {}
        for row in rows:
            inventory_dict[row[1]] = {
                'name': row[0],
                'quantity': row[2],
                'price': row[3]
            }
        if table_name == 'Official':
            self.official_inventory_dict = inventory_dict
        elif table_name == 'Shopee':
            self.shopee_inventory_dict = inventory_dict

    def view_inventory(self, table_name):
        inventory_dict = self._get_inventory_dict(table_name)
        if not inventory_dict:
            print(f"{table_name} inventory is empty.")
        else:
            for code, details in inventory_dict.items():
                print(f"{table_name} - Name: {details['name']}, Code: {code}, Quantity: {details['quantity']}, Price: {details['price']}")

    def print_inventory_dict(self, table_name):
        inventory_dict = self._get_inventory_dict(table_name)
        if not inventory_dict:
            print(f"{table_name} inventory dictionary is empty.")
        else:
            for code, details in inventory_dict.items():
                print(f"{table_name} - Code: {code}, Details: {details}")

    def save_inventory_to_file(self, table_name):
        folder_name = "CoffeeLion_Inventory"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        filename = datetime.now().strftime(f"%Y%m%d_%H%M%S_{table_name}.txt")
        file_path = os.path.join(folder_name, filename)
        inventory_dict = self._get_inventory_dict(table_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            for code, details in inventory_dict.items():
                line = f"Code: {code}, Name: {details['name']}, Quantity: {details['quantity']}, Price: {details['price']}\n"
                f.write(line)
        print(f"Inventory saved to {file_path}")

    def add_or_update_item(self, table_name, name, code, price):
        cursor = self.conn.execute(f"SELECT code FROM {table_name} WHERE code = ?", (code,))
        if cursor.fetchone():
            self.update_item(table_name, name, code, price)
        else:
            self.add_item(table_name, name, code, price)

    def _update_inventory_dict(self, table_name, code, name, price, quantity=None):
        inventory_dict = self._get_inventory_dict(table_name)
        if quantity is not None:
            inventory_dict[code] = {'name': name, 'quantity': quantity, 'price': price}
        else:
            if code in inventory_dict:
                inventory_dict[code]['name'] = name
                inventory_dict[code]['price'] = price

    def _get_inventory_dict(self, table_name):
        if table_name == 'Official':
            return self.official_inventory_dict
        elif table_name == 'Shopee':
            return self.shopee_inventory_dict
        else:
            return {}

    def __del__(self):
        self.conn.close()

def update_table(table_name):
    # 新增或更新 Official 表的品項
    for product in product_list:
        name = product.get("Name")
        code = product.get("Code")
        price = product.get("Price")
        if code:  # 如果有商品編號
            inventory.add_or_update_item(table_name, name, code, price)
        else:
            print(f"Product {name} has no code and cannot be added to the {table_name} inventory.")

if __name__ == '__main__':
    inventory = InventoryManager()

    path = 'coffeelionProductList.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    product_list = data.get("CoffeeLineProduct", [])

    update_table('Official')
    update_table('Shopee')
    
    inventory.update_quantity('Shopee', '10101001', 10)
    inventory.update_quantity('Official', '10101012', 90)
    
    # 查看 Official 庫存
    inventory.view_inventory('Official')
    # inventory.print_inventory_dict('Official')
    # inventory.save_inventory_to_file('Official')

    inventory.view_inventory('Shopee')
    # inventory.print_inventory_dict('Shopee')
    # inventory.save_inventory_to_file('Shopee')