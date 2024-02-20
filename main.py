from kivymd.app import MDApp
from kivy.core.window import Window
from data import get_material_list, get_product_list, save_material, replace_material, delete_material, save_product, replace_product, delete_product, Material, Product

Window.size = (375, 667)

from kivymd.uix.screen import MDScreen
from kivymd.uix.list import ThreeLineAvatarIconListItem, OneLineAvatarIconListItem
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.menu import MDDropdownMenu


class ProductManagerApp(MDApp):
    main_scr = None

    def build(self):
        self.main_scr = MainScreen()
        self.main_scr.screen_manager.duration = .1
        return self.main_scr
    
    def switch_theme(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style_switch_animation_duration = 0.35
        if self.theme_cls.theme_style == "Dark":
            self.theme_cls.theme_style = "Light"
        else:
            self.theme_cls.theme_style = "Dark"
    

class MainScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.screen_manager.transition.direction = 'right'

        self.update_materials()
        self.update_products()

    def add_item_screen(self):
        self.screen_manager.transition.direction = 'left'

        if self.screen_manager.current == 'materials_screen':
            self.screen_manager.current = 'edit_material_screen'
            self.edit_material_screen.current_material = Material('', 0, 0)

        else:
            self.screen_manager.current = 'edit_product_screen'
            self.edit_product_screen.current_product = Product('', 0, 0, [])
            self.edit_product_screen.materials_menu = MaterialsMenu(self.edit_product_screen)

    def edit_item_screen(self, item):
        self.screen_manager.transition.direction = 'left'

        if self.screen_manager.current == 'materials_screen':
            self.screen_manager.current = 'edit_material_screen'
            self.edit_material_screen.current_material = item

            self.edit_material_screen.name_textfield.text = str(item.name)
            self.edit_material_screen.price_textfield.text = str(item.price)
            self.edit_material_screen.count_textfield.text = str(item.count)
        else:
            self.screen_manager.current = 'edit_product_screen'
            self.edit_product_screen.current_product = item

            self.edit_product_screen.name_textfield.text = str(item.name)
            self.edit_product_screen.desire_price_textfield.text = str(item.desire_price)
            self.edit_product_screen.sell_count_textfield.text = str(item.sell_count)
            self.edit_product_screen.update_materials()
            self.edit_product_screen.materials_menu = MaterialsMenu(self.edit_product_screen)


    def back_screen(self):
        self.screen_manager.transition.direction = 'right'

        if self.screen_manager.current == 'edit_material_screen':
            self.screen_manager.current = 'materials_screen'
        else:
            self.screen_manager.current = 'products_screen'

    def update_materials(self):
        self.materials_list.clear_widgets()

        for mat in get_material_list():
            item = ListItem()
            item.item = mat
            item.text = f'{mat.name}'
            item.secondary_text = f'{mat.price} руб/м'
            item.tertiary_text = f'Остаток: {int(self.get_material_count(mat))} м.'
            self.materials_list.add_widget(item)

        self.data_table.update()

    def get_material_count(self, material):
        count = material.count
        for prod in get_product_list():
            mat_sum = 0
            for mat in prod.materials:
                if mat.name == material.name: mat_sum += float(mat.value) * prod.sell_count

            count -= mat_sum
        return count

    def update_products(self):
        self.products_list.clear_widgets()

        for prod in get_product_list():
            item = ListItem()
            item.item = prod
            item.text = f'{prod.name}'
            item.secondary_text = f'Прибыль: {prod.desire_price} руб'
            self.products_list.add_widget(item)

        self.update_materials()
        self.data_table.update()


class ProductDataTable(MDScreen):
    data_table = MDDataTable

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data_table = MDDataTable(
            use_pagination=True,
            pagination_menu_pos='center',
            column_data=[
                ("Название", 50),
                ("Себестоимость", 30),
                ("Прибыль", 30),
                ("Цена для Ozon", 30),
                ("Цена для Avito", 30),
                ("Список продаж", 30),
                ("Общая прибыль", 30)
            ],
            row_data=[])
        
        self.data_table.create_pagination_menu([5, 10, 15, 20])
        self.add_widget(self.data_table)

    def update(self):
        self.data_table.row_data = []
        for prod in get_product_list():
            cost = format(self.get_cost_price(prod), '.2f')
            ozon = format(self.get_ozon_price(prod.desire_price, float(cost)), '.2f')
            avito = format(self.get_avito_price(prod.desire_price, float(cost)), '.2f')
            profit = format(self.get_profit_price(prod), '.2f')

            self.data_table.add_row((prod.name,
                                     cost,
                                     str(prod.desire_price),
                                     ozon,
                                     avito,
                                     str(prod.sell_count),
                                     profit))

    def get_cost_price(self, prod):
        sum = 0
        for mat in prod.materials:
            sum += mat.price * mat.value
        return sum

    def get_ozon_price(self, desire, cost):
        return desire + ((desire + 106 + cost) / 0.81) - desire

    def get_avito_price(self, desire, cost):
        return desire + ((desire + cost) / 0.95) - desire

    def get_profit_price(self, prod):
        return prod.sell_count * prod.desire_price


class ListItem(ThreeLineAvatarIconListItem):
    item = None


class EditMaterialScreen(MDScreen):
    current_material = None
    is_error = False

    def press_save_button(self, *args):
        if self.name_textfield.text == '': self.name_textfield.error = True
        if self.price_textfield.text == '': self.price_textfield.error = True
        if self.count_textfield.text == '': self.count_textfield.error = True

        if self.is_error: return False

        for i in args:
            i()

        if self.current_material.name == '': self.save()
        else: self.replace()

    def save(self):
        mat = Material(self.name_textfield.text,
                       float(self.price_textfield.text),
                       float(self.count_textfield.text))
        
        save_material(mat)

    def replace(self):
        mat = Material(self.name_textfield.text,
                       float(self.price_textfield.text),
                       float(self.count_textfield.text))
        
        replace_material(self.current_material, mat)
        self.current_material = None
        
    def delete(self, back):
        delete_material(self.current_material)
        for i in back:
            i()


class EditProductScreen(MDScreen):
    current_product = None
    materials_menu = None
    is_error = False

    def press_save_button(self, *args):
        if self.name_textfield.text == '': self.name_textfield.error = True
        if self.desire_price_textfield.text == '': self.desire_price_textfield.error = True
        if self.sell_count_textfield.text == '': self.sell_count_textfield.error = True

        if self.is_error: return False

        for i in args:
            i()

        if self.current_product.name == '': self.save()
        else: self.replace()

    def save(self):
        prod = Product(self.name_textfield.text,
                       float(self.desire_price_textfield.text),
                       float(self.sell_count_textfield.text),
                       self.current_product.materials)
        
        save_product(prod)

    def replace(self):
        prod = Product(self.name_textfield.text,
                       float(self.desire_price_textfield.text),
                       float(self.sell_count_textfield.text),
                       self.current_product.materials)
        
        replace_product(self.current_product, prod)
        self.current_product = Product('', 0, 0, [])
        
    def delete(self, back):
        delete_product(self.current_product)
        for i in back:
            i()

    def add_material(self, material):
        self.current_product.materials.append(material)
        self.update_materials()

    def delete_material(self, material):
        self.current_product.materials.remove(material)
        self.update_materials()

    def update_materials(self):
        self.materials_list.clear_widgets()
        for mat in self.current_product.materials:
                name = 'Материал не найден'
                for gen_mat in get_material_list():
                    if gen_mat.name == mat.name: name = mat.name

                widget = MaterialListItem()
                widget.text_field.hint_text = name
                widget.text_field.text = str(mat.value)
                widget.material = mat

                print(widget.text_field.error)

                self.materials_list.add_widget(widget)


class MaterialListItem(OneLineAvatarIconListItem):
    material = None


class MaterialsMenu():
    menu = None
    parent = None

    def __init__(self, ref):
        self.parent = ref

    def open(self, caller):
        self.menu = MDDropdownMenu(caller = caller, items = self.init_menu_items())
        self.menu.open()

    def menu_callback(self, mat):
        self.parent.add_material(mat)
        self.menu.dismiss()

    def init_menu_items(self):
        new_mat_list = get_material_list()
        remove_names = []
        try:
            for mat in self.parent.current_product.materials:
                remove_names.append(mat.name)
        except:
            pass

        for mat in get_material_list():
            if mat.name in remove_names:
                for i in new_mat_list:
                    if i.name == mat.name: new_mat_list.remove(i)

        menu_items = [
            {
                "text": mat.name,
                "on_release": lambda x=mat: self.menu_callback(x),
            } for mat in new_mat_list
        ]

        return menu_items



ProductManagerApp().run()