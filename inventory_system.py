from ursina import *
from ui import UILinePanel
import game
import my_json
import bug_trap
from language_system import TKey
from weapon_system import Weapon
import ui
from setting import game_font

ui_folder = "assets/ui/"

# Пресеты для цветов
color_orange = color.rgb(238, 157, 49)
color_orange_alpha = color.rgba(238, 157, 49, 90)
color_red = color.rgb(232, 0, 0)
color_red_alpha = color.rgba(232, 0, 0, 90)
color_green = color.rgb(40, 190, 56)
color_green_alpha = color.rgba(40, 190, 56, 90)
color_gray = color.rgb(102, 98, 95)

color_sky_day = color.rgb(74, 116, 159)
color_sky_evening = color.rgb(57, 46, 61)
color_sky_night = color.rgb(10, 10, 10)
i_db = my_json.read("assets/gameplay/items")
player_creature = my_json.read("assets/creatures/player")
long_quad = Mesh(
    vertices=((-0.5, -0.5, 0.0), (1.0, -0.5, 0.0), (1.0, 0.5, 0.0), (-0.5, 0.5, 0.0),),
    triangles=(0, 2, 3, 0, 1, 2),
    uvs=((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)),
    normals=((0.0, 0.0, -1.0),) * 4)


# New Item class
class ItemNew(Sprite):
    def __init__(self, **kwargs):
        super().__init__(ppu=16, parent=camera.ui)
        # self.model = self.long_quad
        self.item_id = ""
        self.item_data = {}
        self.item_count = 1
        self.equipped = False
        # self.scale_x = self.scale_y * self.aspect_ratio

        for key, value in kwargs.items():
            setattr(self, key, value)


class Slot(Sprite):
    def __init__(self, **kwargs):
        super().__init__(ppu=16, parent=camera.ui)
        self.slot_id = ""
        self.item = None
        self.icon_entity = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_slot(self):
        if self.item:
            self.texture = self.item.item_data["icon"]


# Inventory system class
class Inventory(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=-0.001)
        self.items_in_inventory = []
        self.selector_id = 0
        self.root_window = None
        self.click_sound = Audio("assets/sounds/click", autoplay=False, loop=False)
        self.stack_items = True
        self.items_offset = 0
        self.w_left = window.left
        self.w_top = window.top
        self.belt_slots = {
            0:{
                "item": None,
                "has_item": False,
                "icon_position": (self.w_left.x+0.265,-0.06,-0.005),
                "icon": None
            },
            1:{
                "item": None,
                "has_item": False,
                "icon_position": (self.w_left.x+0.385, -0.06, -0.005),
                "icon": None
             },
            2:{
                "item": None,
                "has_item": False,
                "icon_position": (self.w_left.x+0.505, -0.06, -0.005),
                "icon": None
             },
            3:{
                "item": None,
                "has_item": False,
                "icon_position": (self.w_left.x+0.625, -0.06, -0.005),
                "icon": None
             }
        }
        self.outfit_slot = Sprite("assets/null.png", parent=self, scale=0.5, x=-0.267, y=0.145, z=-0.005)
        self.outfit_slot_has_item = False
        self.outfit_slot_item = None

        self.rifle_slot = Sprite("assets/null.png", parent=self, scale=0.5, x=-0.37, y=0.34, z=-0.005)
        self.rifle_slot_has_item = False
        self.rifle_slot_item = None

        self.pistol_slot = Sprite("assets/null.png", parent=self, scale=0.5, x=-0.445, y=0.15, z=-0.005)
        self.pistol_slot_has_item = False
        self.pistol_slot_item = None

        Entity(model="quad", parent=self, position=(0, 0, -0.001), scale=window.size, color=rgb(2, 2, 0))
        self.frame = Sprite(ui_folder + "inventory_frame.png", position=(0, 0, -0.002), parent=self, scale=.208)
        self.items_container = Entity(model="quad", parent=self, position=(0, 0, -0.003), scale_x=2,
                                      color=color.rgba(255,255,255,0))
        self.items_container.set_scissor(Vec3(-0.359, -0.439, -1), Vec3(0.359, -0.399, 1))

        # >> Add items from player.json file
        for item in player_creature["start_items"]:
            self.add_item(item)

        # >> Inventory title
        ui.UIText(TKey("pause.inv").upper(), offset=(0.0015, 0.0015), color=color_orange, parent=self,
                  y=0.483, x=-.58, origin=(0, 0), z=-0.003)
        # >> Info window title
        ui.UIText(TKey("inv.info").upper(), offset=(0.0015, 0.0015), color=color_orange, parent=self,
                  y=0.427, x=.065, origin=(0, 0), z=-0.003)

        self.weight_text = Text("[0/0]", parent=self, y=0.35, origin=(0, 0), color=color.clear)

        self.belt_slots_ui = Sprite(ui_folder + "belt.png", parent=self, origin=(-.5, .5),
                                    scale=.6, position=(window.left.x + .2, window.top.y - .5, -0.003))
        self.armor_slot_ui = Sprite(ui_folder + "armor_slot.png", parent=self, origin=(-.5, .5),
                                    scale=.6, position=(window.left.x + .47, window.top.y - .27, -0.003))
        self.pistol_slot_ui = Sprite(ui_folder + "pistol_slot.png", parent=self, origin=(-.5, .5),
                                     scale=.6, position=(window.left.x + .27, window.top.y - .29, -0.003))
        self.weapon_slot_ui = Sprite(ui_folder + "weapon_slot.png", parent=self, origin=(-.5, .5),
                                     scale=.6, position=(window.left.x + .27, window.top.y - .1, -0.003))

        # фон полоски здоровья
        self.health_bar_gui = Sprite(ui_folder + "hp_ui.png", parent=self, origin=(-.5, .5),
                                     scale=.6, position=(window.left.x + .2, window.top.y - .7, -0.003))
        # полоска здоровья
        self.health_bar = Entity(parent=self, model="quad", texture=ui_folder + "hp_bar.png", scale=(.333, .02),
                                 position=(window.left.x + .286, window.top.y - .745, -0.004),
                                 origin=(-.5, 0))

        self.money_text = Text("$0", parent=self, y=-0.379, x=.63, origin=(0, 0), color=color_green, z=-0.003)
        self.health_text = Text("+0", parent=self, y=-0.3, x=-0.37, origin=(0, 0), color=color.clear, z=-0.003)
        self.rad_text = Text(TKey("inv.rad") + " [0]", parent=self, y=-0.35, x=0.4, origin=(0, 0),
                             z=-0.003, color=color.clear)
        ui.UIText(TKey("inv.use.tip"), parent=self, y=-0.47, x=-0.65, origin=(0, 0), color=color_orange, size=4,
                  z=-0.003)
        ui.UIText(TKey("inv.back.tip"), parent=self, y=-0.47, x=0.65, origin=(0, 0), color=color_orange, size=4,
                  z=-0.003)
        self.selector = Entity(model="quad", color=color.white, parent=self.items_container, y=2, x=2, ppu=16,
                               scale=.21, origin=(-.5, 0), z=-0.003)

        # ITEM DESCRIPTION
        self.selected_name = Text("", parent=self, y=0.39, x=0.4, origin=(0, 0), color=color_orange, z=-0.004)
        self.selected_icon = None
        self.selected_caption = Text("", parent=self, y=0.1, x=0.38, origin=(0, 0.5), z=-0.004)
        self.selection_stats = Text("", parent=self, y=0.32, x=0.25, origin=(-.5, 0.5), z=-0.004)

        invoke(self.update_inv_healthbar, delay=0.0001)

        # self.update_items()
        for use in player_creature["use_items_after_start"]:
            invoke(self.use_item,use,delay=0.0001)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_inv_healthbar(self):
        self.health_bar.scale_x = clamp(.333 * game.get_player().health / game.get_player().health_max, 0, .333)

    def clear_slot(self, slot_id,item = None):
        if slot_id:
            if slot_id == "rifle":
                if self.rifle_slot_has_item:
                    destroy(self.rifle_slot)
                    self.rifle_slot = Sprite("assets/null.png", parent=self, scale=0.5, x=-0.37, y=0.34, z=-0.005)
                    self.rifle_slot_has_item = False
                    self.rifle_slot_item = None
            if slot_id == "pistol":
                if self.pistol_slot_has_item:
                    destroy(self.pistol_slot)
                    self.pistol_slot = Sprite("assets/null.png", parent=self, scale=0.5, x=-0.445, y=0.15, z=-0.005)
                    self.pistol_slot_has_item = False
                    self.pistol_slot_item = None
            if slot_id == "outfit":
                if self.outfit_slot_has_item:
                    destroy(self.outfit_slot)
                    self.outfit_slot = Sprite("assets/null.png", parent=self, scale=0.5, x=-0.267, y=0.145, z=-0.005)
                    self.outfit_slot_has_item = False
                    self.outfit_slot_item = None
            if slot_id == "belt":
                for slot in self.belt_slots:
                    if self.belt_slots[slot]["has_item"]:
                        if self.belt_slots[slot]["item"].item_id == item.item_id:
                            destroy(self.belt_slots[slot]["icon"])
                            self.belt_slots[slot]["icon"] = Sprite("assets/null.png", parent=self, scale=0.5, position=self.belt_slots[slot]["icon_position"])
                            self.belt_slots[slot]["has_item"] = False
                            self.belt_slots[slot]["item"] = None
                            break

    def move_to_slot(self, item, slot_id):
        left = window.left
        top = window.top
        if slot_id:
            if slot_id == "rifle":
                destroy(self.rifle_slot)
                self.rifle_slot = Sprite(item.item_data["icon"], parent=self, scale=0.5, x=left.x+0.43, y=0.34, z=-0.005)
                self.rifle_slot_item = item
                self.rifle_slot_has_item = True
            if slot_id == "pistol":
                destroy(self.pistol_slot)
                self.pistol_slot = Sprite(item.item_data["icon"], parent=self, scale=0.5, x=left.x+0.36, y=0.15, z=-0.005)
                self.pistol_slot_item = item
                self.pistol_slot_has_item = True
            if slot_id == "outfit":
                destroy(self.outfit_slot)
                self.outfit_slot = Sprite(item.item_data["icon"], parent=self, scale=0.5, x=left.x+0.533, y=0.145, z=-0.005)
                self.outfit_slot_item = item
                self.outfit_slot_has_item = True
            if slot_id == "belt":
                for slot in self.belt_slots:
                    if not self.belt_slots[slot]["has_item"]:
                        destroy(self.belt_slots[slot]["icon"])
                        self.belt_slots[slot]["icon"] = Sprite(item.item_data["icon"], parent=self, scale=0.5, position=self.belt_slots[slot]["icon_position"])
                        self.belt_slots[slot]["item"] = item
                        self.belt_slots[slot]["has_item"] = True
                        break

    def add_item(self, item_id):
        found_duplicate = False
        duplicate_item = None
        if self.stack_items:
            for i in self.items_in_inventory:
                if item_id == i.item_id:
                    if i.item_data["type"] == "usable":
                        found_duplicate = True
                        duplicate_item = i
                        break
                else:
                    found_duplicate = False

        if item_id in i_db:
            if not found_duplicate:
                self.items_in_inventory.append(
                    ItemNew(parent=self.items_container, texture="assets/null.png", item_id=item_id, item_data=i_db[item_id]))
                # print("[DEBUG] Item [{0}] added!".format(item_id))
                self.update_items_2()
            else:
                print("Found duplicate of [{0}]".format(item_id))
                duplicate_item.item_count += 1
        else:
            if bug_trap.crash_game_msg("Item ID error!",
                                       "[{0}] id not found in assets/gameplay/items.json!".format(item_id), 1):
                application.quit()

    def delete_item(self, item_id):
        for item in self.items_in_inventory:
            if item_id == item.item_id and not item.equipped:
                self.items_in_inventory.remove(item)
                destroy(item)
                break

        self.update_items_2()
        self.update_cursor()
        self.update_selected_text()
        self.update_player_stats()

    def delete_item_count(self,item_id,count=1):
        for item in self.items_in_inventory:
            if item_id == item.item_id and not item.equipped:
                item.item_count -= count
                if item.item_count < 1:
                    self.items_in_inventory.remove(item)
                    destroy(item)
                    break
                break

        self.update_items_2()
        self.update_cursor()
        self.update_selected_text()
        self.update_player_stats()

    def use_item(self, item_id):
        if self.items_in_inventory:
            for item in self.items_in_inventory:
                if item.item_id == item_id:
                    # >> Храним выбранный предмет в двух переменных
                    # >> Для доступа сразу к ключам
                    selected_item = item.item_data
                    # >> Для доступа к корневому уровню предмета
                    selected_item_root = item

                    def undo_equipment_effects_selected():
                        if "max_hp" in selected_item["on_use"]:
                            game.get_player().health_max -= selected_item["on_use"]["max_hp"]
                            if game.get_player().health > game.get_player().health_max:
                                game.get_player().health = game.get_player().health_max
                            self.update_inv_healthbar()
                            game.get_player().update_healthbar()
                        if "armor" in selected_item["on_use"]:
                            game.get_player().armor -= selected_item["on_use"]["armor"]

                    def undo_equipment_effects_outfit_slot():
                        if self.outfit_slot_item is not None:
                            if "max_hp" in self.outfit_slot_item.item_data["on_use"]:
                                game.get_player().health_max -= self.outfit_slot_item.item_data["on_use"]["max_hp"]
                                if game.get_player().health > game.get_player().health_max:
                                    game.get_player().health = game.get_player().health_max
                                self.update_inv_healthbar()
                                game.get_player().update_healthbar()
                            if "armor" in self.outfit_slot_item.item_data["on_use"]:
                                game.get_player().armor -= self.outfit_slot_item.item_data["on_use"]["armor"]

                    def apply_equipment_effects_selected():
                        # >> если есть значение максимального хп в коллбеке использования
                        if "max_hp" in selected_item["on_use"]:
                            # >> добавляем новое значение к макс здоровью
                            game.get_player().health_max += selected_item["on_use"]["max_hp"]
                            self.update_inv_healthbar()
                            game.get_player().update_healthbar()
                        # >>  если есть значение максимальной брони
                        if "armor" in selected_item["on_use"]:
                            # >> добавляем новое значение к броне
                            game.get_player().armor += selected_item["on_use"]["armor"]

                    def usable_items_effects():
                        # >> Если есть поле диалога
                        if "dialogue" in selected_item:
                            game.get_player().weapon.update_ammo_rifle()
                            invoke(game.get_player().show_custom_dialogue, selected_item["dialogue"]["id"],
                                   TKey(selected_item["dialogue"]["name"]), delay=0.01)
                            self.selector_id = 0
                            self.update_cursor()
                            self.root_window.disable()
                            self.disable()
                            game.pause = False

                        # >> Если есть поле function
                        if "function" in selected_item:
                            Func(selected_item["on_use"]["function"]["name"],
                                 selected_item["on_use"]["function"]["args"])

                        # >> Если есть поле лечения в коллбеке "При использовании"
                        if "heal" in selected_item["on_use"]:
                            # >> Если здоровье меньше максимального
                            if game.get_player().health < game.get_player().health_max:
                                # >> Лечим
                                game.get_player().health += selected_item["on_use"]["heal"]
                                # >> Если здоровье больше максимального
                                if game.get_player().health > game.get_player().health_max:
                                    # >> Устанавливаем равное максимальному
                                    game.get_player().health = game.get_player().health_max
                                # >> Обновляем статистику
                                self.update_player_stats()
                                # >> Обновляем хп бар на интерфейсе
                                game.get_player().update_healthbar()
                                self.update_inv_healthbar()
                                # >> Отнимаем количество предмета
                                selected_item_root.item_count -= 1
                                # >> Если кол-во меньше 1
                                if selected_item_root.item_count < 1:
                                    # >> Удаляем предмет
                                    self.delete_item(selected_item_root.item_id)
                                # >> Обновляем список предметов и позицию курсора
                                self.update_items_2()
                                self.update_cursor()

                        # >> Если есть поле лечения в коллбеке "При использовании"
                        if "radiation" in selected_item["on_use"]:
                            game.get_player().radiation = selected_item["on_use"]["radiation"]
                            game.get_player().run_antirad()
                            selected_item_root.item_count -= 1
                            if selected_item_root.item_count < 1:
                                self.delete_item(selected_item_root.item_id)
                            self.update_items_2()
                            self.update_cursor()


                    # >> Если тип предмета "Использование"
                    if selected_item["type"] == "usable":
                        usable_items_effects()

                    if selected_item["type"] == "weapon":
                        if not selected_item_root.equipped:
                            if selected_item["slot"] == "pistol":
                                if not self.pistol_slot_has_item:
                                    selected_item_root.equipped = True
                                    self.move_to_slot(selected_item_root, selected_item["slot"])
                                    game.get_player().weapon.pistol = Weapon(selected_item_root.item_id,
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]],
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["clip_ammo_max"],
                                    selected_item["slot"],
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["speed"])
                                    game.get_player().weapon.draw_weapon("pistol")
                                else:
                                    self.pistol_slot_item.equipped = False
                                    for i in self.items_in_inventory:
                                        # >> Находим по айдишнику предмет в рюкзаке и сравниваем со слотом
                                        if i.item_id == self.pistol_slot_item.item_id:
                                            # >> Применяем значение
                                            i.equipped = self.pistol_slot_item.equipped
                                    selected_item_root.equipped = True
                                    # >> Устанавливаем иконку в слоте на иконку предмета
                                    self.move_to_slot(selected_item_root, selected_item["slot"])
                                    game.get_player().weapon.pistol = Weapon(selected_item_root.item_id,
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]],
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["clip_ammo_max"],
                                    selected_item["slot"],
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["speed"])
                                    game.get_player().weapon.draw_weapon("pistol")
                            if selected_item["slot"] == "rifle":
                                if not self.rifle_slot_has_item:
                                    selected_item_root.equipped = True
                                    self.move_to_slot(selected_item_root, selected_item["slot"])
                                    game.get_player().weapon.rifle = Weapon(selected_item_root.item_id,
                                     my_json.read("assets/gameplay/weapons")[selected_item["profile"]],
                                     my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["clip_ammo_max"],
                                     selected_item["slot"],
                                     my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["speed"])
                                    game.get_player().weapon.draw_weapon("rifle")
                                else:
                                    game.get_player().weapon.delete_weapon("rifle")
                                    self.rifle_slot_item.equipped = False
                                    for i in self.items_in_inventory:
                                        # >> Находим по айдишнику предмет в рюкзаке и сравниваем со слотом
                                        if i.item_id == self.rifle_slot_item.item_id:
                                            # >> Применяем значение
                                            i.equipped = self.rifle_slot_item.equipped
                                    selected_item_root.equipped = True
                                    # >> Устанавливаем иконку в слоте на иконку предмета
                                    self.move_to_slot(selected_item_root, selected_item["slot"])
                                    game.get_player().weapon.rifle = Weapon(selected_item_root.item_id,
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]],
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["clip_ammo_max"],
                                    selected_item["slot"],
                                    my_json.read("assets/gameplay/weapons")[selected_item["profile"]]["speed"])
                                    game.get_player().weapon.draw_weapon("rifle")
                        else:
                            if selected_item["slot"] == "pistol":
                                if "attach" not in selected_item or "attach" in selected_item and not selected_item["attach"]:
                                    if self.pistol_slot_item.item_id == selected_item_root.item_id:
                                        self.clear_slot("pistol")
                                        selected_item_root.equipped = False
                                        game.get_player().weapon.hide_weapon()
                                        game.get_player().weapon.delete_weapon("pistol")

                                else:
                                    print("YOU CAN'T UNWEAR PISTOL!")
                            if selected_item["slot"] == "rifle":
                                if "attach" not in selected_item or "attach" in selected_item and not selected_item["attach"]:
                                    if self.rifle_slot_item.item_id == selected_item_root.item_id:
                                        self.clear_slot("rifle")
                                        selected_item_root.equipped = False
                                        game.get_player().weapon.hide_weapon()
                                        game.get_player().weapon.delete_weapon("rifle")

                                else:
                                    print("YOU CAN'T UNWEAR RIFLE!")

                            # >> Обновляем список предметов (Для смены имени предмета) и курсор
                        self.update_items_2()
                        self.update_player_stats()
                        self.update_cursor()
                    # >> Если тип предмета - "Экипировка" (Общее для пояса и костюмов)
                    if selected_item["type"] == "equipment":
                        # >> Если выбранный предмет не надет
                        if not selected_item_root.equipped:
                            # >> Если слот выбранного предмета "Броня"
                            if selected_item["slot"] == "outfit":
                                # >> Если в слоте нет предметов
                                if not self.outfit_slot_has_item:
                                    # >> То ставим выбранный предмет в значение "Надето"
                                    selected_item_root.equipped = True
                                    # >> Устанавливаем иконку в слоте на иконку предмета
                                    self.move_to_slot(selected_item_root, selected_item["slot"])
                                    # >> Применяем эффекты от выбранного премета в рюкзаке
                                    apply_equipment_effects_selected()

                                # >> Иначе если есть в слоте уже предмет
                                else:
                                    # >> Отменяем все эффекты предмета из слота
                                    undo_equipment_effects_outfit_slot()
                                    # >> Мы устанавливаем значение "Не надето" в предмете из слота
                                    self.outfit_slot_item.equipped = False
                                    # >> Применяем значение на предмете в рюкзаке
                                    # >> Так как я понял, что питон делает не прямую ссылку на объект
                                    # >> а ебучую копию, то из-за этой проблемы, я три часа своей
                                    # >> жизни потратил, на поиск этой хуйни -_-
                                    # >> Решено...
                                    for i in self.items_in_inventory:
                                        # >> Находим по айдишнику предмет в рюкзаке и сравниваем со слотом
                                        if i.item_id == self.outfit_slot_item.item_id:
                                            # >> Применяем значение
                                            i.equipped = self.outfit_slot_item.equipped
                                    # >> Ставим выбранный предмет в значение "Надето"
                                    selected_item_root.equipped = True
                                    # >> Устанавливаем иконку в слоте на иконку предмета
                                    self.move_to_slot(selected_item_root, selected_item["slot"])
                                    # >> Применяем эффекты от выбранного премета в рюкзаке
                                    apply_equipment_effects_selected()

                            if selected_item["slot"] == "belt":
                                # >> Если в слоте нет предметов
                                for slot in self.belt_slots:
                                    if not self.belt_slots[slot]["has_item"]:
                                        # >> То ставим выбранный предмет в значение "Надето"
                                        selected_item_root.equipped = True
                                        # >> Устанавливаем иконку в слоте на иконку предмета
                                        self.move_to_slot(selected_item_root, selected_item["slot"])
                                        # >> Применяем эффекты от выбранного премета в рюкзаке
                                        apply_equipment_effects_selected()

                                        break
                                    # >> Иначе если есть в слоте уже предмет
                        # >> Если предмет надет, то снимаем его и отменяем свойства
                        else:
                            undo_equipment_effects_selected()

                            if selected_item["slot"] == "outfit":
                                if self.outfit_slot_item.item_id == selected_item_root.item_id:
                                    self.clear_slot("outfit")

                            if selected_item["slot"] == "belt":
                                self.clear_slot("belt",selected_item_root)

                            selected_item_root.equipped = False

                        # >> Обновляем список предметов (Для смены имени предмета) и курсор
                        self.update_items_2()
                        self.update_player_stats()
                        self.update_cursor()
                        break

    def update_player_stats(self):
        self.money_text.text = "${0}".format(game.get_player().money)
        self.health_text.text = dedent(
            "+ {0} / {1}%".format(game.get_player().health, game.get_player().health_max)).strip()
        self.rad_text.text = TKey("inv.rad") + " [{0}]".format(game.get_player().radiation)
        self.weight_text.text = "[{0}/15]".format(len(self.items_in_inventory))

    def update_cursor(self):
        if self.items_in_inventory:
            self.selector_id = 0
            self.selector.y = self.items_in_inventory[self.selector_id].y
            self.selector.x = self.items_in_inventory[self.selector_id].x
            # self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
            self.selector.scale_y = self.items_in_inventory[self.selector_id].scale_y
            self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
            self.selector.color = color_orange_alpha

            self.update_selected_text()

    def update_selected_text(self):
        if self.items_in_inventory:
            selected_item = self.items_in_inventory[self.selector_id] if self.items_in_inventory else None
            if self.selected_icon:
                invoke(destroy, self.selected_icon, delay=0.00001)

            self.selected_name.text = dedent("{0}".format(TKey(selected_item.item_data["name"]))).strip()
            self.selected_caption.text = dedent(
                "<rgb(102, 98, 95)>\"{0}\"".format(TKey(selected_item.item_data["caption"]))).strip()
            self.selected_caption.wordwrap = 35
            if len(self.items_in_inventory) >= 1:
                if selected_item.item_data["type"] == "usable":
                    self.selection_stats.text = dedent(
                        "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}".format(
                            TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                            TKey("inv.itm.stat.price"), selected_item.item_data["price"])).strip()
                    if "heal" in selected_item.item_data["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                                TKey("inv.itm.stat.price"),
                                selected_item.item_data["price"], TKey("inv.itm.stat.heal"),
                                selected_item.item_data["on_use"]["heal"], TKey("inv.itm.stat.count"),
                                selected_item.item_count)).strip()
                    if "radiation" in selected_item.item_data["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                                TKey("inv.itm.stat.price"),
                                selected_item.item_data["price"], TKey("inv.itm.stat.radiation"),
                                "20.0 s", TKey("inv.itm.stat.count"),
                                selected_item.item_count)).strip()
                elif selected_item.item_data["type"] == "equipment":
                    self.selection_stats.text = dedent(
                        "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}".format(
                            TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                            TKey("inv.itm.stat.price"),
                            selected_item.item_data["price"], TKey("inv.itm.stat.count"),
                            selected_item.item_count)).strip()
                    if "max_hp" in selected_item.item_data["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                                TKey("inv.itm.stat.price"),
                                selected_item.item_data["price"], TKey("inv.itm.stat.max.hp"),
                                selected_item.item_data["on_use"]["max_hp"], TKey("inv.itm.stat.count"),
                                selected_item.item_count)).strip()
                    if "armor" in selected_item.item_data["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                                TKey("inv.itm.stat.price"),
                                selected_item.item_data["price"], TKey("inv.itm.stat.armor"),
                                selected_item.item_data["on_use"]["armor"], TKey("inv.itm.stat.count"),
                                selected_item.item_count)).strip()
                else:
                    self.selection_stats.text = dedent(
                        "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}".format(
                            TKey("inv.itm.stat.type"), TKey(selected_item.item_data["type"]),
                            TKey("inv.itm.stat.price"),
                            selected_item.item_data["price"], TKey("inv.itm.stat.count"),
                            selected_item.item_count)).strip()
            else:
                self.selection_stats.text = ""

            self.selected_icon = Sprite(texture=selected_item.item_data["icon"], parent=self, y=0.22, x=0.14,
                                        origin=(0, 0), scale=0.5, z=-0.004)
        else:
            self.selected_name.text = ""
            self.selected_caption.text = ""
            self.selected_icon.texture = None
            self.selected_icon.color = color.clear
            self.selector.x = -5
            self.selector.y = -5

    def update_items_2(self):
        # Temp list of last items
        last_items = []
        last_items.clear()
        for itm_in_inv in self.items_in_inventory:
            last_items.append(itm_in_inv)

        # clear current inventory list
        if self.items_in_inventory:
            for i in self.items_in_inventory:
                destroy(i)
        self.items_in_inventory.clear()

        start_x_pos = -0.357  # Start spawn point X
        start_z_pos = -0.005
        # spawn items again (COPY ALL DATA FROM OLD TO NEW)
        for item in last_items:
            if "rotate_icon" in item.item_data and item.item_data["rotate_icon"]:
                itm = ItemNew(texture=item.item_data["icon"], item_data=item.item_data, equipped=item.equipped,
                              item_id=item.item_id, item_count=item.item_count,
                              parent=item.parent, origin=(0, -.5), rotation_z=90)
            else:
                itm = ItemNew(texture=item.item_data["icon"], item_data=item.item_data, equipped=item.equipped,
                              item_id=item.item_id, parent=item.parent, item_count=item.item_count,
                              origin=(-.5, 0))
            itm.scale_y = 0.03  # Scale Y
            itm.scale_x = itm.scale_y * (itm.texture.width / itm.texture.height)/2  # Scale X

            itm.x = start_x_pos - self.items_offset
            itm.y = -.42  # Start spawn point Y
            itm.z = start_z_pos
            start_x_pos += itm.scale_x

            self.items_in_inventory.append(itm)
            #self.selector_id = 0

    def update_items(self):
        N = 3
        if self.items:
            for index, item in enumerate(self.items):
                # itm = Sprite (self.items[index].item_icon, parent=self, origin=(0, 0), scale=0.5, x=-0.6, y=0.25)
                itm = Text(self.items[index].item_name, parent=self, origin=(-.5, 0), x=-0.65, y=0.25)
                row = index // N  # so it is 0 from 0 to 3 and 1 from 4 to 7 and so on
                column = index - row * N
                itm.x += 0.3 * column
                itm.y -= 0.1 * row

    def input(self, key):
        if self.enabled:
            if self.items_in_inventory:
                def check_item_status():
                    if self.items_in_inventory[self.selector_id].equipped:
                        self.selector.color = color_green_alpha
                    else:
                        self.selector.color = color_orange_alpha

                # >> Управление курсором вправо
                if key == "right arrow" or key == "d" or key == "d hold" or key == "right arrow hold":
                    self.click_sound.play()
                    self.selector_id += 1
                    if self.selector_id > len(self.items_in_inventory) - 1:
                        self.selector_id = len(self.items_in_inventory) - 1
                    self.selector.y = self.items_in_inventory[self.selector_id].y
                    self.selector.x = self.items_in_inventory[self.selector_id].x
                    self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
                    if self.selector.x == self.items_in_inventory[0].x and self.items_offset != 0:
                        self.items_offset = 0
                        self.update_items_2()
                        self.update_cursor()

                    if self.selector.x >= 0.35-self.items_in_inventory[self.selector_id].scale_x:
                        self.items_offset += self.items_in_inventory[self.selector_id].scale_x
                        self.update_items_2()
                        self.update_cursor()
                    # self.selector.scale = self.items_in_inventory[self.selector_id].scale
                    check_item_status()
                    self.update_selected_text()
                # >> Управление курсором влево
                if key == "left arrow" or key == "a" or key == "a hold" or key == "left arrow hold":
                    self.click_sound.play()
                    self.selector_id -= 1

                    if self.selector_id < 0:
                        self.selector_id = 0

                    self.selector.y = self.items_in_inventory[self.selector_id].y
                    self.selector.x = self.items_in_inventory[self.selector_id].x
                    self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x

                    if self.selector.x == self.items_in_inventory[len(self.items_in_inventory)-1].x and self.selector_id != 0:
                        self.items_offset = self.items_in_inventory[len(self.items_in_inventory)-1].x-0.31
                        self.update_items_2()
                        self.update_cursor()

                    if self.selector.x <= -0.36 and self.selector.x != self.items_in_inventory[0].x:
                        self.items_offset -= self.items_in_inventory[self.selector_id].scale_x
                        self.update_items_2()
                        self.update_cursor()
                    #else:
                    #    self.items_offset = 0
                    #    self.update_items_2()
                    #    self.update_cursor()

                    check_item_status()
                    self.update_selected_text()
                # >> Удаление предмета
                if key == "z":
                    if self.items_in_inventory:
                        self.delete_item(self.items_in_inventory[self.selector_id].item_id)
                # >> Обработка нажатия ентер
                if key == "enter":
                    self.use_item(self.items_in_inventory[self.selector_id].item_id)

            # >> Выходим в меню
            if key == "escape" and self.enabled:
                invoke(self.root_window.enable,delay=0.0001)
                game.get_player().weapon.update_ammo_rifle()
                self.selector_id = 0
                self.update_cursor()
                self.disable()


if __name__ == "__main__":
    app = Ursina()

    app.run()
