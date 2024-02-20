import sqlite3

db = sqlite3.connect('database.db')
c = db.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS materials(
          name TEXT,
          price FLOATING,
          count FLOATING
)''')
c.execute('''CREATE TABLE IF NOT EXISTS items(
          name TEXT,
          cost_price FLOATING,
          desire_price FLOATING,
          price_for_ozon FLOATING,
          price_for_avito FLOATING,
          sell_count INTEGER,
          profit FLOATING,
          materiallist TEXT
)''')
db.commit()


class Material():
    name = ''
    price = 0
    count = 0
    value = 0

    def __init__(self, name, price, count):
        self.name = name
        self.price = price
        self.count = count

class Product():
    name = ''
    desire_price = 0
    sell_count = 0
    materials = []

    def __init__(self, name, desire_price, sell_count, materials):
        self.name = name
        self.desire_price = desire_price
        self.sell_count = sell_count
        self.materials = materials


def get_material_list():
    mat_list = []
    list = c.execute('SELECT * FROM materials')
    
    for i in list:
        mat_list.append(Material(i[0], i[1], i[2]))

    db.commit()
    return mat_list

def get_product_list():
    item_list = []
    list = c.execute('SELECT * FROM items')
    db.commit()
    
    for i in list.fetchall():
        item_list.append(Product(i[0],
                              i[1],
                              i[2],
                              get_list_from_string(i[3])))


    return item_list


def get_list_from_string(str):
    mat_list = []
    el_list = []
    el = ''
    sw = True

    for i in str:
        if i == ' ':
            el_list.append(el)
            el = ''
            continue

        el += i


    for el in el_list:
        sw = True
        name = ''
        price = 0
        count = 0
        value = ''
        for i in el:
            if i == ':':
                sw = False
                continue

            if sw: name += i
            else: value += i

        mat = Material(name, price, count)
        for mat1 in get_material_list():
            if name == mat1.name:
                mat.price = mat1.price

        mat.value = float(value)
        mat_list.append(mat)

    return mat_list

def get_string_from_list(list):
    s = ''

    for mat in list:
        s += f'{mat.name}:{mat.value} '

    return s


def save_material(material):
    c.execute(f'INSERT INTO materials VALUES (?, ?, ?)', (material.name, str(material.price), str(material.count)))
    db.commit()

def replace_material(current, new):
    c.execute(f'UPDATE materials SET name = \'{new.name}\' WHERE name = \'{current.name}\'')
    c.execute(f'UPDATE materials SET price = \'{new.price}\' WHERE name = \'{current.name}\'')
    c.execute(f'UPDATE materials SET count = \'{new.count}\' WHERE name = \'{current.name}\'')
    db.commit()

def delete_material(mat):
    c.execute(f'DELETE FROM materials WHERE name = \'{mat.name}\'')
    db.commit()


def save_product(prod:Product):
    c.execute(f'INSERT INTO items VALUES (?, ?, ?, ?)', (prod.name, str(prod.desire_price), str(prod.sell_count), get_string_from_list(prod.materials)))
    db.commit()

def replace_product(current:Product, new:Product):
    c.execute(f'UPDATE items SET name = \'{new.name}\' WHERE name = \'{current.name}\'')
    c.execute(f'UPDATE items SET desire_price = \'{new.desire_price}\' WHERE name = \'{current.name}\'')
    c.execute(f'UPDATE items SET sell_count = \'{new.sell_count}\' WHERE name = \'{current.name}\'')
    c.execute(f'UPDATE items SET materiallist = \'{get_string_from_list(new.materials)}\' WHERE name = \'{current.name}\'')
    db.commit()

def delete_product(prod:Product):
    c.execute(f'DELETE FROM items WHERE name = \'{prod.name}\'')
    db.commit()
