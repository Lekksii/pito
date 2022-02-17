from ursina import *
import my_json
import game
import bug_trap
from language_system import TKey
import ui

items_db = my_json.read("assets/gameplay/items")
traders = my_json.read("assets/creatures/traders")
characters = my_json.read("assets/creatures/characters")
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

class TradeWindow(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=-0.09)
        self.trader_id = ""
        self.items_in_inventory = []
        self.items_in_trader = []
        self.selector_id = 0
        self.buy = False
        self.items_offset_p = 0
        self.items_offset_t = 0

        Entity(parent=self, model="quad", color=rgb(10, 10, 10), scale=window.size)
        self.frame = Sprite(ui_folder + "trading_frame.png", parent=self, scale=.208, z=-0.0001)
        self.title = Text(TKey("pause.trading").upper(), parent=self, y=0.495, x=-0.57, z=-0.001,
                              color=color_orange,origi=(0,0))

        self.type_caption = Text("Type caption for this trading".upper(), parent=self, y=-0.357, z=-0.001,
                                 origin=(0, 0), color=color_orange)
        self.money = Text("0$".upper(), parent=self, x=0.64,y=-0.379, z=-0.001,
                                 origin=(0, 0), color=color_green)

        self.items_container_trader = Entity(model="quad", parent=self, position=(0, 0, -0.003), scale_x=2,
                                      color=color.rgba(255, 255, 255, 0))
        self.items_container_trader.set_scissor(Vec3(-0.359, 0.445, -1), Vec3(0.359, 0.41, 1))

        self.items_container_player = Entity(model="quad", parent=self, position=(0, 0, -0.003), scale_x=2,
                                      color=color.rgba(255, 255, 255, 0))
        self.items_container_player.set_scissor(Vec3(-0.359, -0.439, -1), Vec3(0.359, -0.399, 1))

        self.selector = Entity(model="quad", color=color.white, parent=self, y=0, x=0, z=-0.001,
                               scale=.21, origin=(-.5, 0))
        ui.UIText(TKey("inv.use.tip"), parent=self, y=-0.47, x=-0.65, origin=(0, 0), color=color_orange, size=4,
                  z=-0.003)
        ui.UIText(TKey("inv.back.tip"), parent=self, y=-0.47, x=0.65, origin=(0, 0), color=color_orange, size=4,
                  z=-0.003)

        # ITEM DESCRIPTION
        self.selected_name = Text("", parent=self, y=0.36, x=-.11, origin=(-.5, 0), color=color_orange, z=-0.01)
        self.selected_icon = None
        self.selected_caption = Text("", parent=self, y=.1, x=0, origin=(0, 0.5), z=-0.01)
        self.selection_stats = Text("", parent=self, y=0.32, x=-0.11, origin=(-.5, 0.5), z=-0.01)

        for key, value in kwargs.items():
            setattr(self, key, value)

    # Обновляем список преметов в слотах
    def fill_slots_with_items(self,trader_id):
        # Если в слотах на продажу есть что-то - удаляем
        if self.items_in_inventory:
            for i in self.items_in_inventory:
                destroy(i)
            self.items_in_inventory.clear()

        # Если слоты покупок пустые – заполняем товарами продавца
        if not self.items_in_trader:
            for trader_item in traders[trader_id]["items"]:
                self.items_in_trader.append(TradingItem(trader_item,texture=items_db[trader_item]["icon"],
                                                        parent=self.items_container_trader))

        # Если слоты на продажу пустые – заполняем товарами из инвентаря
        if not self.items_in_inventory:
            if game.get_player().inventory.items_in_inventory:
                for player_item in game.get_player().inventory.items_in_inventory:
                    self.items_in_inventory.append(PlayerItem(player_item.item_id,texture=player_item.texture,
                                                            parent=self.items_container_player,
                                                            item_count=player_item.item_count))
        self.selector_id = self.selector_id
        self.update_items()

    def update_items(self):
        # Буфер для последних предметов в инв
        last_items_player = []
        last_items_trader = []
        last_items_player.clear()
        last_items_trader.clear()

        for itm_in_inv in self.items_in_inventory:
            last_items_player.append(itm_in_inv)

        for itm_in_trader in self.items_in_trader:
            last_items_trader.append(itm_in_trader)

        # clear current inventory list
        if self.items_in_inventory:
            for inv_i in self.items_in_inventory:
                destroy(inv_i)
        self.items_in_inventory.clear()

        # clear current trader list
        if self.items_in_trader:
            for itm_t in self.items_in_trader:
                destroy(itm_t)
        self.items_in_trader.clear()

        start_x_pos_p = -0.357  # Start spawn point X Player items
        start_z_pos_p = -0.005
        start_x_pos_t = -0.357  # Start spawn point X Trader items
        start_z_pos_t = -0.005
        # spawn items again (COPY ALL DATA FROM OLD TO NEW)
        for item_p in last_items_player:
            itm_p = PlayerItem(item_p.item_id,texture=item_p.texture,parent=item_p.parent, item_count=item_p.item_count,
                               origin=(-.5, 0))
            itm_p.scale_y = 0.03  # Scale Y
            itm_p.scale_x = itm_p.scale_y * (itm_p.texture.width / itm_p.texture.height) / 2  # Scale X

            itm_p.x = start_x_pos_p - self.items_offset_p
            itm_p.y = -.42  # Start spawn point Y
            itm_p.z = start_z_pos_p
            start_x_pos_p += itm_p.scale_x

            self.items_in_inventory.append(itm_p)

        # spawn items again (COPY ALL DATA FROM OLD TO NEW)
        for item_t in last_items_trader:
            itm_t = TradingItem(item_t.item_id, texture=item_t.texture, parent=item_t.parent,origin=(-.5, 0))
            itm_t.scale_y = 0.03  # Scale Y
            itm_t.scale_x = itm_t.scale_y * (itm_t.texture.width / itm_t.texture.height) / 2  # Scale X

            itm_t.x = start_x_pos_t - self.items_offset_t
            itm_t.y = .427  # Start spawn point Y
            itm_t.z = start_z_pos_t
            start_x_pos_t += itm_t.scale_x

            self.items_in_trader.append(itm_t)

        self.update_cursor()

    # Обновляем курсор и тексты
    def update_cursor(self):
        self.money.text = "{0}$".format(game.get_player().money)
        sel = self.selector

        if self.buy and self.items_in_trader:
            trader_items = self.items_in_trader[self.selector_id]

            self.type_caption.text = TKey("trade.buy.state")
            sel.parent = self.items_container_trader
            sel.y = trader_items.y
            sel.x = trader_items.x

            sel.scale_y = trader_items.scale_y
            sel.scale_x = trader_items.scale_x

            if items_db[trader_items.item_id]["price"] > game.get_player().money:
                sel.color = color_red_alpha
            else:
                sel.color = color_orange_alpha

        if not self.buy and self.items_in_inventory:
            inv_items = self.items_in_inventory[self.selector_id]

            self.type_caption.text = TKey("trade.sell.state")
            sel.parent = self.items_container_player

            if self.selector_id >= 0:
                sel.y = inv_items.y
                sel.x = inv_items.x
            else:
                sel.y = -5
                sel.x = -5

            sel.scale_y = inv_items.scale_y
            sel.scale_x = inv_items.scale_x

            def checkItems():
                rifle_slot_has = game.get_player().inventory.rifle_slot_has_item
                rifle_slot = game.get_player().inventory.rifle_slot_item
                outfit_slot_has = game.get_player().inventory.outfit_slot_has_item
                outfit_slot = game.get_player().inventory.outfit_slot_item
                blacklist = traders[self.trader_id]["dont_want_to_buy"]
                belt_slot = game.get_player().inventory.belt_slots

                def belt():
                    for i in belt_slot:
                        if belt_slot[i]["has_item"] and belt_slot[i]["item"].item_id == inv_items.item_id:
                            return True

                if (inv_items.item_id in blacklist) or \
                (rifle_slot_has and rifle_slot.item_id == inv_items.item_id) or \
                (outfit_slot_has and outfit_slot.item_id == inv_items.item_id) or \
                belt():
                    return True
                else:
                    return False

            if checkItems():
                self.selector.color = color_red_alpha
            else:
                self.selector.color = color_orange_alpha
        self.update_selected_text()

    def input(self,key):

        def selectItem():
            return self.items_in_inventory[self.selector_id].item_id if not self.buy else \
                self.items_in_trader[self.selector_id].item_id

        def updateCursorItems():
            self.update_items()
            self.update_cursor()

        if self.enabled:
            if key == "escape":
                self.enabled = False
                game.get_player().weapon.update_ammo_rifle()

            # >> Управление курсором вправо
            if key == "right arrow" or key == "d" or key == "d hold" or key == "right arrow hold":
                #self.click_sound.play()
                self.selector_id += 1
                if self.buy:
                    if self.selector_id > len(self.items_in_trader) - 1:
                        self.selector_id = len(self.items_in_trader) - 1
                    self.selector.y = self.items_in_trader[self.selector_id].y
                    self.selector.x = self.items_in_trader[self.selector_id].x
                    self.selector.scale_x = self.items_in_trader[self.selector_id].scale_x
                    if self.selector.x == self.items_in_trader[0].x and self.items_offset_t != 0:
                        self.items_offset_t = 0
                        updateCursorItems()

                    if self.selector.x >= 0.35 - self.items_in_trader[self.selector_id].scale_x:
                        self.items_offset_t += self.items_in_trader[self.selector_id].scale_x
                        updateCursorItems()
                    self.update_cursor()
                else:
                    if self.selector_id > len(self.items_in_inventory) - 1:
                        self.selector_id = len(self.items_in_inventory) - 1
                    self.selector.y = self.items_in_inventory[self.selector_id].y
                    self.selector.x = self.items_in_inventory[self.selector_id].x
                    self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
                    if self.selector.x == self.items_in_inventory[0].x and self.items_offset_p != 0:
                        self.items_offset_p = 0
                        updateCursorItems()

                    if self.selector.x >= 0.35 - self.items_in_inventory[self.selector_id].scale_x:
                        self.items_offset_p += self.items_in_inventory[self.selector_id].scale_x
                        updateCursorItems()
                    self.update_cursor()
                print("Стрелка вправо, текущий предмет "+selectItem())

            # >> Управление курсором влево
            if key == "left arrow" or key == "a" or key == "a hold" or key == "left arrow hold":
                #self.click_sound.play()
                self.selector_id -= 1
                if self.buy:
                    if self.selector_id < 0:
                        self.selector_id = 0
                    self.selector.y = self.items_in_trader[self.selector_id].y
                    self.selector.x = self.items_in_trader[self.selector_id].x
                    self.selector.scale_x = self.items_in_trader[self.selector_id].scale_x
                    if self.selector.x == self.items_in_trader[len(self.items_in_trader) - 1].x:
                        self.items_offset_t = self.items_in_trader[len(self.items_in_trader) - 1].x - 0.31
                        updateCursorItems()

                    if self.selector.x <= -0.35 and self.selector.x != self.items_in_trader[0].x:
                        self.items_offset_t -= self.items_in_trader[self.selector_id].scale_x
                        updateCursorItems()
                    else:
                        self.items_offset_t = 0
                        updateCursorItems()
                    self.update_cursor()
                else:
                    if self.selector_id < 0:
                        self.selector_id = 0
                    self.selector.y = self.items_in_inventory[self.selector_id].y
                    self.selector.x = self.items_in_inventory[self.selector_id].x
                    self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
                    if self.selector.x == self.items_in_inventory[len(self.items_in_inventory) - 1].x:
                        self.items_offset_p = self.items_in_inventory[len(self.items_in_inventory) - 1].x - 0.31
                        updateCursorItems()

                    if self.selector.x <= -0.35 and self.selector.x != self.items_in_inventory[0].x:
                        self.items_offset_p -= self.items_in_inventory[self.selector_id].scale_x
                        updateCursorItems()
                    else:
                        self.items_offset_p = 0
                        updateCursorItems()
                    self.update_cursor()

            if key == "up arrow" or key == "w":
                self.buy = True
                self.selector_id = 0
                self.update_cursor()

            if key == "down arrow" or key == "s":
                self.buy = False
                self.selector_id = 0
                self.update_cursor()

            if key == "enter":
                if self.buy:
                    if game.get_player().money >= items_db[self.items_in_trader[self.selector_id].item_id]["price"]:
                        self.buy = True
                        game.get_player().inventory.add_item(self.items_in_trader[self.selector_id].item_id)
                        game.get_player().money -= items_db[self.items_in_trader[self.selector_id].item_id]["price"]
                        self.fill_slots_with_items(self.trader_id)
                        self.update_cursor()
                        self.update_items()
                        game.get_player().weapon.update_ammo_rifle()
                else:
                    def chekItem():
                        # Занят ли автоматный слот
                        rifle_slot_has = game.get_player().inventory.rifle_slot_has_item
                        # Итем в автоматном слоте
                        r_slot = game.get_player().inventory.rifle_slot_item
                        # Занят ли пистолетный слот
                        pistol_slot_has = game.get_player().inventory.pistol_slot_has_item
                        # Итем в пистолетном слоте
                        p_slot = game.get_player().inventory.pistol_slot_item
                        # Занят ли слот костюма
                        outfit_has = game.get_player().inventory.outfit_slot_has_item
                        # Итем в слоте костюма
                        o_slot = game.get_player().inventory.outfit_slot_item
                        # Список предметов у торговца, которые он не покупает
                        blacklist = traders[self.trader_id]["dont_want_to_buy"]
                        b_slots = game.get_player().inventory.belt_slots

                        def checkBelt():
                            for i in b_slots:
                                if b_slots[i]["has_item"] and b_slots[i]["item"].item_id != selectItem() or \
                                        not b_slots[i]["has_item"]:
                                    return True

                        if (selectItem() not in blacklist) and \
                        (rifle_slot_has and r_slot.item_id != selectItem() or not rifle_slot_has) and \
                        (pistol_slot_has and p_slot.item_id != selectItem() or not pistol_slot_has) and \
                        (outfit_has and o_slot.item_id != selectItem() or not outfit_has) and \
                        (checkBelt() is True):
                            return True
                        else:
                            return False
                    # Если всё впорядке и предмет можно продавать
                    if chekItem() is True:
                        # Сбрасываем селектор в положение "Продать"
                        self.buy = False
                        # Если кол-во предмета больше 1
                        # то просто отнимаем 1 при продаже
                        if self.items_in_inventory[self.selector_id].item_count > 0:
                            game.get_player().inventory.delete_item_count(self.items_in_inventory[self.selector_id].item_id)
                        else:
                            # Если всего 1 предмет, просто удаляем его из инвентаря
                            game.get_player().inventory.delete_item(self.items_in_inventory[self.selector_id].item_id)

                        if self.selector_id > 0:
                            self.selector_id -= 1
                            self.update_cursor()
                        else:
                            self.selector_id = 0
                        # Прибавляем деньги по стоимости предмета
                        game.get_player().money += items_db[self.items_in_inventory[self.selector_id].item_id]["price"]
                        self.fill_slots_with_items(self.trader_id)


    def update_selected_text(self):
        if self.items_in_trader if self.buy else self.items_in_inventory:
            selected_item = self.items_in_trader[self.selector_id] if self.buy else \
                            self.items_in_inventory[self.selector_id]
            db_items = items_db[selected_item.item_id]
            stat_type = TKey("inv.itm.stat.type")
            stat_price = TKey("inv.itm.stat.price")
            stat_heal = TKey("inv.itm.stat.heal")
            stat_count = TKey("inv.itm.stat.count")
            stat_rad = TKey("inv.itm.stat.radiation")
            stat_max_hp = TKey("inv.itm.stat.max.hp")
            stat_armor = TKey("inv.itm.stat.armor")

            if self.selected_icon:
                invoke(destroy, self.selected_icon, delay=0.00001)

            def changeName(key):
                self.selected_name.text = dedent("{0}".format(key)).strip()

            def changeDescription(key, wordwrap=35):
                self.selected_caption.text = dedent(
                    "<rgb(102, 98, 95)>\"{0}\"".format(key)).strip()
                self.selected_caption.wordwrap = wordwrap

            def setStats(stat,value):
                pattern = ""

                for i in range(len(stat)):
                    pattern += "<rgb(238, 157, 49)>"+str(stat[i])+":<rgb(102, 98, 95)> "+str(value[i])+"\n"

                self.selection_stats.text = dedent(pattern).strip()

            changeName(TKey(db_items["name"]))
            changeDescription(TKey(db_items["caption"]))

            if len(self.items_in_trader if self.buy else self.items_in_inventory) >= 1:
                if db_items["type"] == "usable":
                    setStats([stat_type, stat_price],[db_items["type"], db_items["price"]])
                    if "heal" in db_items["on_use"]:
                        setStats([stat_type, stat_price, stat_heal,stat_count],
                                 [TKey(db_items["type"]), db_items["price"],
                                  db_items["on_use"]["heal"],selected_item.item_count if not self.buy else "1"])
                    if "radiation" in db_items["on_use"]:
                        setStats([stat_type, stat_price, stat_rad,stat_count],
                                 [TKey(db_items["type"]), db_items["price"],"20.0 s",
                                  selected_item.item_count if not self.buy else "1"])
                elif db_items["type"] == "equipment":
                    setStats([stat_type, stat_price,stat_count],[TKey(db_items["type"]),db_items["price"],
                                                                 selected_item.item_count if not self.buy else "1"])
                    if "max_hp" in db_items["on_use"]:
                        if "heal" in db_items["on_use"]:
                            setStats([stat_type, stat_price, stat_max_hp, stat_count],
                                     [TKey(db_items["type"]), db_items["price"],
                                      db_items["on_use"]["max_hp"], selected_item.item_count if not self.buy else "1"])
                    if "armor" in db_items["on_use"]:
                        setStats([stat_type, stat_price, stat_armor, stat_count],
                                 [TKey(db_items["type"]), db_items["price"],
                                  db_items["on_use"]["armor"], selected_item.item_count if not self.buy else "1"])
                else:
                    setStats([stat_type, stat_price, stat_count], [TKey(db_items["type"]), db_items["price"],
                                                                   selected_item.item_count if not self.buy else "1"])
            else:
                self.selection_stats.text = ""

            self.selected_icon = Sprite(texture=items_db[selected_item.item_id]["icon"], parent=self, y=0.265, x=-0.235,
                                        origin=(0, 0), scale=0.5, z=-0.001)
        else:
            self.selected_name.text = ""
            self.selected_caption.text = ""
            self.selected_icon.texture = None
            self.selected_icon.color = color.clear

class TradingItem(Sprite):
    def __init__(self,item_id="", **kwargs):
        super().__init__()

        self.item_id = item_id

        for key, value in kwargs.items():
            setattr(self, key, value)

class PlayerItem(Sprite):
    def __init__(self,item_id="",item_count=1, **kwargs):
        super().__init__()

        self.item_id = item_id
        self.item_count = item_count

        for key, value in kwargs.items():
            setattr(self, key, value)