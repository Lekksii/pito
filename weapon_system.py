from ursina import *
from ui import UILinePanel
import game
import my_json
import bug_trap
from language_system import TKey

ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

# Пресеты для цветов
color_orange = color.rgb (238, 157, 49)
color_red = color.rgb (232, 0, 0)
color_green = color.rgb (40, 190, 56)

color_sky_day = color.rgb (74, 116, 159)
color_sky_evening = color.rgb (57, 46, 61)
color_sky_night = color.rgb (10, 10, 10)

weapons_config = my_json.read("assets/gameplay/weapons")
items_config = my_json.read("assets/gameplay/items")

class Weapon():
    def __init__(self,id="",data={},clip=0,slot="",speed=0,**kwargs):
        super().__init__()
        self.id = id
        self.data=data
        self.clip = clip
        self.slot = slot
        self.shoot_sound = Audio(sound_folder + data["fire_sound"], autoplay=False, loop=False,volume=0.7)
        self.speed = speed
        self.damage = data["damage"]

        #print("[Weapon()][{0}] was created and attached to [{1}] slot".format(self.id,self.slot))

        for key, value in kwargs.items ():
            setattr (self, key, value)

class WeaponSystem():
    def __init__(self,**kwargs):
        super().__init__()
        self.current_weapon = None
        self.pistol = None
        self.rifle = None
        self.infinite_ammo=False
        self.cant_show_weapon = False
        self.ammo_in_inventory = 0
        self.weapons_clips_last = {}
        self.reload_sound = Audio(sound_folder + "reload", autoplay=False, loop=False,volume=0.8)
        self.empty_sound = Audio(sound_folder + "empty", autoplay=False, loop=False,volume=0.7)

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def update_weapons(self):
        if not self.current_weapon:
            #print("[WeaponSystem] Found active hud, destroying it!")
            destroy(game.get_player().weapon_2d_hud)
            game.get_player().ammo_text.text = ""
        if self.cant_show_weapon:
            if self.current_weapon:
                self.hide_weapon()

    def update_ammo_rifle(self):
        self.ammo_in_inventory = 0
        if self.current_weapon and items_config[self.current_weapon.id]["slot"] == "rifle":
            for ammo in game.get_player().inventory.items_in_inventory:
                if ammo.item_id == self.current_weapon.data["ammo_type"]:
                    self.ammo_in_inventory += 1
            self.update_ammo()

    def update_ammo(self):
        if self.infinite_ammo:
            game.get_player().ammo_text.text = "{0}/-".format(self.current_weapon.clip)
        else:
            game.get_player().ammo_text.text = "{0}/{1} ".format(self.current_weapon.clip, self.ammo_in_inventory)

    def shoot(self):
        if self.current_weapon:
            if self.infinite_ammo:
                if self.current_weapon.clip == 0:
                    self.reload_weapon()
            if self.current_weapon.clip > 0:
                if "shoot_count" in self.current_weapon.data:
                    self.current_weapon.clip -= self.current_weapon.data["shoot_count"]
                else:
                    self.current_weapon.clip -= 1
            self.current_weapon.shoot_sound.play()
            invoke(self.change_cam_rot,rot_minus=1,left=1,delay=0)
            invoke(self.change_cam_rot, rot_plus=1,right=1, delay=0.1)
            game.get_player().shoot_sparkle.enable()
            game.get_player().shoot_sparkle.position = (
                self.current_weapon.data["sparkle_position"][0],
                self.current_weapon.data["sparkle_position"][1],
            0.002)
            invoke(self.disable_sparkle, delay=0.1)
            #print("speed is {0}".format(self.current_weapon.speed))
            self.update_ammo()

    def disable_sparkle(self):
        game.get_player().shoot_sparkle.enabled = False

    def change_cam_rot(self,rot_minus=0,rot_plus=0,left=0,right=0):
        if rot_plus > 0:
            game.get_player().camera_pivot.rotation_x += rot_plus
        if rot_minus > 0:
            game.get_player().camera_pivot.rotation_x -= rot_minus
        if left > 0:
            game.get_player().camera_pivot.rotation_y -= left
        if right > 0:
            game.get_player().camera_pivot.rotation_y += right

    # >> Берём оружие в руки
    def draw_weapon(self,slot):
        # >> Прицел становистя перекрестьем
        #print("[WeaponSystem] Update cursor to cross!")
        game.get_player().cursor.texture = "assets/ui/crosshair_weapon.png"
        # >> Если слот пистолета и он надет в слоте в инвентаре
        if slot == "pistol" and game.get_player().inventory.pistol_slot_has_item:
            # >> Текущее оружие в руках теперь пистолет
            self.current_weapon = self.pistol
            if "inf_ammo" in self.current_weapon.data and self.current_weapon.data["inf_ammo"]:
                self.infinite_ammo = True
            if "ammo_type" in self.current_weapon.data and self.current_weapon.data["ammo_type"] is not None:
                self.infinite_ammo = False
            # >> Если находим ключ-айди пистолета в словаре с сохранёнными патронами от прошлого этого же оружия
            if self.pistol.id in self.weapons_clips_last:
                # >> То возвращаем то кол-во патронов, на котором мы спрятали пистолет
                self.current_weapon.clip = self.weapons_clips_last[self.pistol.id]
            else:
                # >> Иначе просто установить максимальное кол-во в обойме
                self.current_weapon.clip = self.pistol.clip
            # >> Если 2д худ не пустой
            if game.get_player().weapon_2d_hud:
                # >> Удаляем худ
                destroy(game.get_player().weapon_2d_hud)
            # >> Устанавливаем худ с оружия из слота
            game.get_player().weapon_2d_hud = Sprite(self.current_weapon.data["hud"], scale=.5,
                   position=(.65,-.33, 0.001),
                   parent=camera.ui)
            # >> Устанавливаем текст с кол-вом патронов
            self.update_ammo()
        # >> Если слот - автомат и он надет в инвентаре
        if slot == "rifle" and game.get_player().inventory.rifle_slot_has_item:
            #print("[WeaponSystem] Found active rifle in slot.")
            # >> Берём в руки автомат
            self.current_weapon = self.rifle
            #print("[WeaponSystem] ID of self.current_weapon is [{0}]".format(self.current_weapon.id))
            if "inf_ammo" in self.current_weapon.data and self.current_weapon.data["inf_ammo"]:
                self.infinite_ammo = True
            else:
                self.infinite_ammo = False
            # >> Если находим ключ-айди автомата в словаре с сохранёнными патронами от прошлого этого же оружия
            if self.rifle.id in self.weapons_clips_last:
                #print("[WeaponSystem] Found last weapon usage with this ID")
                # >> То возвращаем то кол-во патронов, на котором мы спрятали автомат
                self.current_weapon.clip = self.weapons_clips_last[self.rifle.id]
            else:
                #print("[WeaponSystem] This is first equipped weapon, set max count of ammo.")
                # >> Иначе просто установить максимальное кол-во в обойме
                self.current_weapon.clip = self.rifle.clip
            # >> Если 2д худ не пустой
            if game.get_player().weapon_2d_hud:
                # >> Удаляем
                destroy(game.get_player().weapon_2d_hud)
            # >> Создаём новый худ из слота
            #print("[WeaponSystem] Creating new hud.")
            game.get_player().weapon_2d_hud = Sprite(self.current_weapon.data["hud"], scale=.5,
                   position=(.65,-.33, 0.001),
                   parent=camera.ui)
            # >> Если бесконечные патроны
            if self.infinite_ammo:
                #print("[WeaponSystem] Found infinite ammo!")
                # >> То показываем только кол-во патронов в обойме, из рюкзака не показываем
                self.update_ammo()
            else:
                #print("[WeaponSystem] Try to find ammo in inventory!")
                # >> Иначе итерируем инвентарь на наличие типа обойм, которые указаны в профиле оружия
                self.ammo_in_inventory = 0
                for ammo in game.get_player().inventory.items_in_inventory:
                    if ammo.item_id == self.current_weapon.data["ammo_type"]:
                        #print("[WeaponSystem] Found ammo [{0}] for [{1}]!".format(self.current_weapon.data["ammo_type"],
                        #    self.current_weapon.id))
                        self.ammo_in_inventory += 1
                self.update_ammo()
        self.update_weapons()

    def hide_weapon(self):
        if self.current_weapon:
            game.get_player().cursor.texture = "assets/ui/crosshair.png"
            destroy(game.get_player().weapon_2d_hud)
            game.get_player().ammo_text.text = ""
            if self.current_weapon.slot == "pistol":
                self.pistol.clip = self.current_weapon.clip
            if self.current_weapon.slot == "rifle":
                self.rifle.clip = self.current_weapon.clip
            self.current_weapon = None

    def delete_weapon(self,slot):
        if slot == "pistol":
            pass
        if slot == "rifle":
            #print("[WeaponSystem] No previous rifles found, save last clips!")
            self.weapons_clips_last[self.rifle.id] = self.rifle.clip
            #print("[WeaponSystem] self.weapons_clips_last = [\"{0}\":{1}]".format(self.rifle.id,self.weapons_clips_last[self.rifle.id]))
            self.rifle = None


    def reload_weapon(self):
        if self.current_weapon.clip < self.current_weapon.data["clip_ammo_max"]:
            if self.infinite_ammo:
                self.current_weapon.clip = self.current_weapon.data["clip_ammo_max"]
            else:
                for ammo in game.get_player().inventory.items_in_inventory:
                    if ammo.item_id == self.current_weapon.data["ammo_type"]:
                        self.current_weapon.clip = self.current_weapon.data["clip_ammo_max"]
                        game.get_player().inventory.delete_item(ammo.item_id)
                        self.ammo_in_inventory -= 1
                        break
            self.reload_sound.play()
            self.update_ammo()