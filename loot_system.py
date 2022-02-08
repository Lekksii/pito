from ursina import *
import my_json
import game
import bug_trap
from language_system import TKey
import ui

items_db = my_json.read("assets/gameplay/items")
loot_box = my_json.read("assets/gameplay/loot_containers")
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


class LootWindow(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=-0.09)

        self.items_in_container = []
        self.loot_id = ""
        self.click_sound = Audio("assets/sounds/click", autoplay=False, loop=False)
        self.selector_id = 0
        self.items_offset = 0

        Entity(parent=self, model="quad", color=rgb(10, 10, 10), scale=window.size)
        self.frame = Sprite(ui_folder + "loot_frame.png", parent=self, scale=.208,z=-0.0001)
        self.loot_name = Text("Loot".upper(), parent=self, y=0.495, x=-0.55,z=-0.001, color=color_orange)
        # Entity (parent=self, y=0.37, x=0, model="quad", scale_y=0.002, color=color.dark_gray, scale_x=window.size.x)
        self.loot_caption = Text("Optional caption for this loot box".upper(), parent=self, y=-0.382, z=-0.001,
                                 origin=(0, 0), color=color_orange)
        self.tip_bottom = Text(dedent(TKey("loot.control.tip")).strip(),
                               parent=self, y=-0.43, x=-0.7, origin=(-.5, 0), color=color_gray, size=4)

        self.items_container = Entity(model="quad", parent=self, position=(0, 0, -0.003), scale_x=2,
                                      color=color.rgba(255, 255, 255, 0))
        self.items_container.set_scissor(Vec3(-0.359, 0.445, -1), Vec3(0.359, 0.41, 1))

        self.selector = Entity(model="quad", color=color.white, parent=self.items_container, y=0, x=0, z=-0.001,
                               scale=.21, origin=(-.5, 0))

        ui.UIText(TKey("inv.use.tip"), parent=self, y=-0.47, x=-0.65, origin=(0, 0), color=color_orange, size=4,
                  z=-0.003)
        ui.UIText(TKey("inv.back.tip"), parent=self, y=-0.47, x=0.65, origin=(0, 0), color=color_orange, size=4,
                  z=-0.003)

        # ITEM DESCRIPTION
        self.selected_name = Text("", parent=self, y=0.33, x=-.11, origin=(-.5, 0), color=color_orange, z=-0.01)
        self.selected_icon = None
        self.selected_caption = Text("", parent=self, y=.1, x=0, origin=(0, 0.5), z=-0.01)
        self.selection_stats = Text("", parent=self, y=0.3, x=-0.11, origin=(-.5, 0.5), z=-0.01)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def start_loot(self, loot_id):
        self.enable()
        self.loot_id = loot_id
        self.loot_name.text = TKey(loot_box[loot_id]["name"])
        self.loot_caption.text = TKey(loot_box[loot_id]["caption"])
        for loot in loot_box[loot_id]["items"]:
            self.items_in_container.append(LootItem(parent=self.items_container, item_id=loot, item_data=items_db[loot],
                                                    texture="assets/null.png",
                                                    scale=0.03))
        self.update_loot()
        self.update_cursor()

    def update_cursor(self):
        if self.items_in_container:
            self.selector.y = self.items_in_container[self.selector_id].y
            self.selector.x = self.items_in_container[self.selector_id].x
            self.selector.scale_y = self.items_in_container[self.selector_id].scale_y
            self.selector.scale_x = self.items_in_container[self.selector_id].scale_x
            self.selector.color = color_orange_alpha
        else:
            self.selector.x = -5

    def update_loot(self):
        # Temp list of last items
        last_items = []
        last_items.clear()
        for itm_in_container in self.items_in_container:
            last_items.append(itm_in_container)

        # clear current inventory list
        if self.items_in_container:
            for i in self.items_in_container:
                destroy(i)
        self.items_in_container.clear()

        start_x_pos = -0.357  # Start spawn point X
        start_z_pos = -0.005
        # spawn items again (COPY ALL DATA FROM OLD TO NEW)
        for item in last_items:
            if "rotate_icon" in item.item_data and item.item_data["rotate_icon"]:
                itm = LootItem(texture=item.item_data["icon"], item_data=item.item_data,
                               item_id=item.item_id, item_count=item.item_count,
                               parent=item.parent, origin=(0, -.5), rotation_z=90)
            else:
                itm = LootItem(texture=item.item_data["icon"], item_data=item.item_data,
                               item_id=item.item_id, parent=item.parent, item_count=item.item_count,
                               origin=(-.5, 0))
            itm.scale_y = 0.03  # Scale Y
            itm.scale_x = itm.scale_y * (itm.texture.width / itm.texture.height) / 2  # Scale X

            itm.x = start_x_pos - self.items_offset
            itm.y = .427  # Start spawn point Y
            itm.z = start_z_pos
            start_x_pos += itm.scale_x

            self.items_in_container.append(itm)

        #self.selector_id = 0
        self.update_cursor()
        self.update_selected_text()

    def delete_selected(self):
        for item in self.items_in_container:
            if item.item_id == self.items_in_container[self.selector_id].item_id:
                self.items_in_container.remove(item)
                destroy(item)
                if self.selector_id > 0:
                    self.selector_id -= 1
                else:
                    self.selector_id = 0
                self.update_loot()
                break

    def update_selected_text(self):
        if self.items_in_container:
            selected_item = self.items_in_container[self.selector_id] if self.items_in_container else None
            if self.selected_icon:
                invoke(destroy, self.selected_icon, delay=0.00001)

            self.selected_name.text = dedent("{0}".format(TKey(selected_item.item_data["name"]))).strip()
            self.selected_caption.text = dedent(
                "<rgb(102, 98, 95)>\"{0}\"".format(TKey(selected_item.item_data["caption"]))).strip()
            self.selected_caption.wordwrap = 35
            if len(self.items_in_container) >= 1:
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

            self.selected_icon = Sprite(texture=selected_item.item_data["icon"], parent=self, y=0.24, x=-0.23,
                                        origin=(0, 0), scale=0.5, z=-0.001)
        else:
            self.selected_name.text = ""
            self.selected_caption.text = ""
            self.selected_icon.texture = None
            self.selected_icon.color = color.clear

    def input(self, key):
        if self.enabled and self.items_in_container:
            if key == "space":
                for i in self.items_in_container:
                    game.get_player().inventory.add_item(i.item_id)

                if self.items_in_container:
                    for i in self.items_in_container:
                        destroy(i)
                    self.items_in_container.clear()
                game.get_player().weapon.update_ammo_rifle()
                self.selector_id = 0
                self.disable()


            if key == "right arrow" or key == "d" or key == "d hold" or key == "right arrow hold":
                self.click_sound.play()
                self.selector_id += 1
                if self.selector_id > len(self.items_in_container) - 1:
                    self.selector_id = len(self.items_in_container) - 1



                if self.selector.x >= 0.34 - self.items_in_container[self.selector_id].scale_x:
                    self.items_offset += self.items_in_container[self.selector_id].scale_x
                    self.update_loot()
                    self.update_cursor()

                self.update_cursor()
                self.update_selected_text()

            if key == "left arrow" or key == "a" or key == "a hold" or key == "left arrow hold":
                self.click_sound.play()
                self.selector_id -= 1
                if self.selector_id < 0:
                    self.selector_id = 0

                if self.selector.x == self.items_in_container[0].x and self.items_offset != 0:
                    self.items_offset = 0
                    self.update_loot()
                    self.update_cursor()

                if self.selector.x <= -0.35:
                    self.items_offset -= self.items_in_container[self.selector_id].scale_x if self.selector.x != self.items_in_container[0].x else 0
                    self.update_loot()
                    self.update_cursor()

                self.update_cursor()
                self.update_selected_text()

            if key == "enter":
                game.get_player().inventory.add_item(self.items_in_container[self.selector_id].item_id)
                self.delete_selected()

        if key == "escape":
            if self.items_in_container:
                for i in self.items_in_container:
                    destroy(i)
                self.items_in_container.clear()
            game.get_player().weapon.update_ammo_rifle()
            self.selector_id = 0
            self.disable()

    def update(self):
        if len(self.items_in_container) == 0:
            self.items_in_container.clear()
            self.selector_id = 0
            self.disable()


# New Item class
class LootItem(Sprite):
    def __init__(self, **kwargs):
        super().__init__(ppu=16, parent=camera.ui)
        # self.model = self.long_quad
        self.item_id = ""
        self.item_data = {}
        self.item_count = 1

        # if self.item_id not in items_db:
        #    if bug_trap.crash_game_msg("Error","Item ID [{0}] not found in assets/gameplay/items.json".format(self.item_id),1):
        #        application.quit()
        # self.scale_x = self.scale_y * self.aspect_ratio

        for key, value in kwargs.items():
            setattr(self, key, value)
