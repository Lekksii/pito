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

    def fill_slots_with_items(self,trader_id):
        if self.items_in_inventory:
            for i in self.items_in_inventory:
                destroy(i)
            self.items_in_inventory.clear()


        if not self.items_in_trader:
            for trader_item in traders[trader_id]["items"]:
                self.items_in_trader.append(TradingItem(trader_item,texture=items_db[trader_item]["icon"],
                                                        parent=self.items_container_trader))


        if not self.items_in_inventory:
            if game.get_player().inventory.items_in_inventory:
                for player_item in game.get_player().inventory.items_in_inventory:
                    self.items_in_inventory.append(PlayerItem(player_item.item_id,texture=player_item.texture,
                                                            parent=self.items_container_player,
                                                            item_count=player_item.item_count))
        self.selector_id = self.selector_id
        #self.update_cursor()
        self.update_items()

    def update_items(self):
        # Temp list of last items
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

        #self.buy = True
        #self.selector_id = 0
        self.update_cursor()
        #self.update_selected_text()

    def update_cursor(self):
        self.money.text = "{0}$".format(game.get_player().money)
        if self.buy and self.items_in_trader:
            self.type_caption.text = TKey("trade.buy.state")
            self.selector.parent = self.items_container_trader
            self.selector.y = self.items_in_trader[self.selector_id].y
            self.selector.x = self.items_in_trader[self.selector_id].x

            self.selector.scale_y = self.items_in_trader[self.selector_id].scale_y
            self.selector.scale_x = self.items_in_trader[self.selector_id].scale_x
            if items_db[self.items_in_trader[self.selector_id].item_id]["price"] > game.get_player().money:
                self.selector.color = color_red_alpha
            else:
                self.selector.color = color_orange_alpha
        if not self.buy and self.items_in_inventory:
            self.type_caption.text = TKey("trade.sell.state")
            self.selector.parent = self.items_container_player
            if self.selector_id >= 0:
                self.selector.y = self.items_in_inventory[self.selector_id].y
                self.selector.x = self.items_in_inventory[self.selector_id].x
            else:
                self.selector.y = -5
                self.selector.x = -5

            self.selector.scale_y = self.items_in_inventory[self.selector_id].scale_y
            self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x

            if self.items_in_inventory[self.selector_id].item_id in traders[self.trader_id]["dont_want_to_buy"] or \
                    game.get_player().inventory.rifle_slot_has_item and \
                    game.get_player().inventory.rifle_slot_item.item_id == self.items_in_inventory[self.selector_id].item_id or \
                    game.get_player().inventory.outfit_slot_has_item and \
                    game.get_player().inventory.outfit_slot_item.item_id == self.items_in_inventory[self.selector_id].item_id or \
                    game.get_player().inventory.belt_slots[0]["has_item"] and \
                    game.get_player().inventory.belt_slots[0]["item"].item_id == self.items_in_inventory[self.selector_id].item_id or \
                    game.get_player().inventory.belt_slots[1]["has_item"] and \
                    game.get_player().inventory.belt_slots[1]["item"].item_id == self.items_in_inventory[self.selector_id].item_id or \
                    game.get_player().inventory.belt_slots[2]["has_item"] and \
                    game.get_player().inventory.belt_slots[2]["item"].item_id == self.items_in_inventory[self.selector_id].item_id or \
                    game.get_player().inventory.belt_slots[3]["has_item"] and \
                    game.get_player().inventory.belt_slots[3]["item"].item_id == self.items_in_inventory[self.selector_id].item_id:
                self.selector.color = color_red_alpha
            else:
                self.selector.color = color_orange_alpha
        self.update_selected_text()

    def input(self,key):
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
                        self.update_items()
                        self.update_cursor()

                    if self.selector.x >= 0.35 - self.items_in_trader[self.selector_id].scale_x:
                        self.items_offset_t += self.items_in_trader[self.selector_id].scale_x
                        self.update_items()
                        self.update_cursor()
                    self.update_cursor()
                else:
                    if self.selector_id > len(self.items_in_inventory) - 1:
                        self.selector_id = len(self.items_in_inventory) - 1
                    self.selector.y = self.items_in_inventory[self.selector_id].y
                    self.selector.x = self.items_in_inventory[self.selector_id].x
                    self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
                    if self.selector.x == self.items_in_inventory[0].x and self.items_offset_p != 0:
                        self.items_offset_p = 0
                        self.update_items()
                        self.update_cursor()

                    if self.selector.x >= 0.35 - self.items_in_inventory[self.selector_id].scale_x:
                        self.items_offset_p += self.items_in_inventory[self.selector_id].scale_x
                        self.update_items()
                        self.update_cursor()
                    self.update_cursor()

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
                        self.update_items()
                        self.update_cursor()

                    if self.selector.x <= -0.35 and self.selector.x != self.items_in_trader[0].x:
                        self.items_offset_t -= self.items_in_trader[self.selector_id].scale_x
                        self.update_items()
                        self.update_cursor()
                    else:
                        self.items_offset_t = 0
                        self.update_items()
                        self.update_cursor()
                    self.update_cursor()
                else:
                    if self.selector_id < 0:
                        self.selector_id = 0
                    self.selector.y = self.items_in_inventory[self.selector_id].y
                    self.selector.x = self.items_in_inventory[self.selector_id].x
                    self.selector.scale_x = self.items_in_inventory[self.selector_id].scale_x
                    if self.selector.x == self.items_in_inventory[len(self.items_in_inventory) - 1].x:
                        self.items_offset_p = self.items_in_inventory[len(self.items_in_inventory) - 1].x - 0.31
                        self.update_items()
                        self.update_cursor()

                    if self.selector.x <= -0.35 and self.selector.x != self.items_in_inventory[0].x:
                        self.items_offset_p -= self.items_in_inventory[self.selector_id].scale_x
                        self.update_items()
                        self.update_cursor()
                    else:
                        self.items_offset_p = 0
                        self.update_items()
                        self.update_cursor()
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
                inv_item_id = self.items_in_inventory[self.selector_id].item_id if not self.buy else None
                print(inv_item_id)
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
                    if (not inv_item_id in traders[self.trader_id]["dont_want_to_buy"]) or \
                            (game.get_player().inventory.rifle_slot_has_item and \
                            inv_item_id is not game.get_player().inventory.rifle_slot_item.item_id) or \
                            (game.get_player().inventory.pistol_slot_has_item and \
                            inv_item_id is not game.get_player().inventory.pistol_slot_item.item_id) or \
                            (game.get_player().inventory.outfit_slot_has_item and \
                            inv_item_id is not game.get_player().inventory.outfit_slot_item.item_id) or \
                            (game.get_player().inventory.belt_slots[0]["has_item"] and\
                            inv_item_id is not game.get_player().inventory.belt_slots[0]["item"].item_id) or \
                            (game.get_player().inventory.belt_slots[1]["has_item"] and \
                            inv_item_id is not game.get_player().inventory.belt_slots[1]["item"].item_id) or \
                            (game.get_player().inventory.belt_slots[2]["has_item"] and \
                            inv_item_id is not game.get_player().inventory.belt_slots[2]["item"].item_id) or \
                            (game.get_player().inventory.belt_slots[3]["has_item"] and \
                            inv_item_id is not game.get_player().inventory.belt_slots[3]["item"].item_id):
                        self.buy = False
                        if self.items_in_inventory[self.selector_id].item_count > 0:
                            game.get_player().inventory.delete_item_count(self.items_in_inventory[self.selector_id].item_id)
                        else:
                            game.get_player().inventory.delete_item(self.items_in_inventory[self.selector_id].item_id)
                        if self.selector_id > 0:
                            self.selector_id -= 1
                            self.update_cursor()
                        else:
                            self.selector_id = 0
                        game.get_player().money += items_db[self.items_in_inventory[self.selector_id].item_id]["price"]
                        self.fill_slots_with_items(self.trader_id)


    def update_selected_text(self):
        if self.items_in_trader if self.buy else self.items_in_inventory:
            selected_item = self.items_in_trader[self.selector_id] if self.buy else \
                            self.items_in_inventory[self.selector_id]
            if self.selected_icon:
                invoke(destroy, self.selected_icon, delay=0.00001)

            self.selected_name.text = dedent("{0}".format(TKey(items_db[selected_item.item_id]["name"]))).strip()
            self.selected_caption.text = dedent(
                "<rgb(102, 98, 95)>\"{0}\"".format(TKey(items_db[selected_item.item_id]["caption"]))).strip()
            self.selected_caption.wordwrap = 35
            if len(self.items_in_trader if self.buy else self.items_in_inventory) >= 1:
                if items_db[selected_item.item_id]["type"] == "usable":
                    self.selection_stats.text = dedent(
                        "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}".format(
                            TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                            TKey("inv.itm.stat.price"), items_db[selected_item.item_id]["price"])).strip()
                    if "heal" in items_db[selected_item.item_id]["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                                TKey("inv.itm.stat.price"),
                                items_db[selected_item.item_id]["price"], TKey("inv.itm.stat.heal"),
                                items_db[selected_item.item_id]["on_use"]["heal"], TKey("inv.itm.stat.count"),
                                selected_item.item_count if not self.buy else "1")).strip()
                    if "radiation" in items_db[selected_item.item_id]["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                                TKey("inv.itm.stat.price"),
                                items_db[selected_item.item_id]["price"], TKey("inv.itm.stat.radiation"),
                                "20.0 s", TKey("inv.itm.stat.count"),
                                selected_item.item_count if not self.buy else "1")).strip()
                elif items_db[selected_item.item_id]["type"] == "equipment":
                    self.selection_stats.text = dedent(
                        "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}".format(
                            TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                            TKey("inv.itm.stat.price"),
                            items_db[selected_item.item_id]["price"], TKey("inv.itm.stat.count"),
                            selected_item.item_count if not self.buy else "1")).strip()
                    if "max_hp" in items_db[selected_item.item_id]["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                                TKey("inv.itm.stat.price"),
                                items_db[selected_item.item_id]["price"], TKey("inv.itm.stat.max.hp"),
                                items_db[selected_item.item_id]["on_use"]["max_hp"], TKey("inv.itm.stat.count"),
                                selected_item.item_count if not self.buy else "1")).strip()
                    if "armor" in items_db[selected_item.item_id]["on_use"]:
                        self.selection_stats.text = dedent(
                            "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}\n<rgb(238, 157, 49)>{6}: <rgb(102, 98, 95)>{7}".format(
                                TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                                TKey("inv.itm.stat.price"),
                                items_db[selected_item.item_id]["price"], TKey("inv.itm.stat.armor"),
                                items_db[selected_item.item_id]["on_use"]["armor"], TKey("inv.itm.stat.count"),
                                selected_item.item_count if not self.buy else "1")).strip()
                else:
                    self.selection_stats.text = dedent(
                        "<rgb(238, 157, 49)>{0}:<rgb(102, 98, 95)> {1}\n<rgb(238, 157, 49)>{2}: <rgb(102, 98, 95)>{3}\n<rgb(238, 157, 49)>{4}: <rgb(102, 98, 95)>{5}".format(
                            TKey("inv.itm.stat.type"), TKey(items_db[selected_item.item_id]["type"]),
                            TKey("inv.itm.stat.price"),
                            items_db[selected_item.item_id]["price"], TKey("inv.itm.stat.count"),
                            selected_item.item_count if not self.buy else "1")).strip()
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