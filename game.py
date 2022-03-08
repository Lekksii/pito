from ursina import *
from ursina.shaders import *
from ursina.shaders import ssao_shader
from pito_light import *
from direct.filter.CommonFilters import CommonFilters
from inventory_system import Inventory
from weapon_system import WeaponSystem
from quest_system import Quests
from pause_journal import JournalWindow
from dialogue_system import Dialogue
from loot_system import LootWindow
from trading_system import TradeWindow
from skills_system import SkillsWindow
from pda import PDA
#from tkinter import Tk
from camera_effects_shader import *
from language_system import TKey
import setting
import os.path
import my_json
import bug_trap
import main_menu
import ui
from actor import *

# ИНИЦИАЛИЗАЦИЯ
# объявлям папки с ассетами и доп файлы
tex_folder = "assets/textures/"
mesh_folder = "assets/models/"
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

player_creature = my_json.read("assets/creatures/player")
options_file = my_json.read("assets/options")
npc_profiles = my_json.read("assets/creatures/characters")
# -----------

# Игра начата
gameplay = True
# Переменная, в которой хранится класс игрового процесса
game_session = None
pause = False
isdead=False
fps_mode = False
show_hud = True

# Пресеты для цветов
color_orange = color.rgb(238, 157, 49)
color_red = color.rgb(232, 0, 0)
color_green = color.rgb(40, 190, 56)
color_gray = color.rgb(102, 98, 95)

color_sky_day = color.rgb(74, 116, 159)
color_sky_evening = color.rgb(57, 46, 61)
color_sky_night = color.rgb(10, 10, 10)


# получить класс игрока
def get_player():
    if game_session:
        if game_session.player is not None:
            return game_session.player
    else:
        return None


# получить текстовый идентификатор уровня
def get_current_level_id():
    if game_session:
        return game_session.get_level()
    else:
        return None


# получить класс текущего уровня, на котором мы сейчас находимся
def get_current_level():
    if game_session:
        return game_session.current_level
    else:
        return None


# запустить новый уровень по id из папки levels
def set_current_level(lvl):
    if game_session:
        game_session.current_level = Level(get_player(), level_id=lvl)


# скопировать текст в буфер обмена
#def copy_to_clipboard(string):
#    r = Tk()
#    r.withdraw()
#    r.clipboard_clear()
#    r.clipboard_append(str(string))
#    r.update()  # now it stays on the clipboard after the window is closed
#    r.destroy()


# что-то типа инфопоршней из оригинальной трилогии сталкера
def add_e_key(key_id):
    get_player().event_keys.append(key_id)
    print("[Event Key] \"{0}\" has been added!".format(key_id))


def has_e_key(key_id):
    if key_id in get_player().event_keys:
        return True
    else:
        return False


def del_e_key(key_id):
    if key_id in get_player().event_keys:
        get_player().event_keys.remove(key_id)
        print("[Event Key] \"{0}\" has been removed!".format(key_id))


def enable_pda_in_pause(b):
    if b:
        show_message(TKey("message.pda.enabled"), 3)

    get_player().pause_menu.pda_enabled = b


def show_message(txt, life_time):
    get_player().msg.setText("")
    get_player().msg.setText(txt)
    invoke(get_player().msg.setText, "", delay=life_time)


# КЛАСС ИГРОКА
class Player(Entity):
    def hideHUD(self):
        return color.rgba(1,1,1,0) if not show_hud else color.rgba(1,1,1,1)

    def __init__(self, **kwargs):
        super().__init__()
        # скорость перемещения камеры (для режима разработчика)
        self.speed = setting.camera_move_speed
        # точка опоры для камеры
        self.camera_pivot = Entity(parent=self, y=0)
        # текст под прицелом
        self.crosshair_tip_text = "Demo"
        # прицел в центре экрана
        self.cursor = Sprite(ui_folder + "crosshair.png", parent=camera.ui, scale=.26, color = self.hideHUD())
        # объект для текста под прицелом
        self.crosshair_tip = ui.UIText(parent=camera.ui, offset=(0.0015,0.0015), text=self.crosshair_tip_text, origin=(0, 0), y=0.04,
                                       color=color_orange if show_hud else self.hideHUD(), scale=1, x=0, z=-0.001)
        # родитель камеры
        camera.parent = self.camera_pivot
        # позиция камеры
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        # угол зрения камеры
        camera.fov = setting.camera_fov
        self.original_fov = camera.fov
        camera.clip_plane_near = 0.06
        camera.clip_plane_far = 500
        # мышь зафиксирована или нет
        mouse.locked = setting.cursor_lock
        #self.filters = CommonFilters(application.base.win,application.base.cam)
        #self.filters.set_inverted()
        #camera.shader = camera_grayscale_shader
        #camera.set_shader_input("c_R", 0.93)
        #camera.set_shader_input("c_G", 0.95)
        #camera.set_shader_input("c_B", 1.05)




        # дебаг рейкаста (луча столкновения) в режиме разработчика
        self.hit_text = "None"
        self.raycast_point_pos_text = ""
        self.hit_pos_info = Text("", y=0.1, origin=(0, 0))
        # чувствительность мыши вращения камеры
        self.mouse_sensitivity = Vec2(options_file["mouse_sensitivity"], options_file["mouse_sensitivity"])
        self.rot_array_x = []
        self.rot_average_x = 0.0
        self.rot_array_y = []
        self.rot_average_y = 0.0
        self.rot_x = 0
        self.rot_y = 0
        self.frame_count = 2
        self.strange_mouse = False
        self.radiation_sound = Audio(sound_folder+"radiation",autoplay=False,volume=0.5)
        self.steps_sound = Audio(sound_folder+"walk",autoplay=False, loop=False)
        self.hit_sound = Audio(sound_folder+"hit",autoplay=False,loop=False)
        # рейкаст (луч столкновений)
        self.ray_hit = raycast(self.position + (self.down * 0.04), direction=(0, -1, 0), ignore=(self,), distance=50,
                               debug=False)
        # -----INTERFACE----------------

        self.frame_game = Sprite(ui_folder + "fr_game_1.png", parent=camera.ui, origin=(-.5, .5), scale=.445,
                                 position=(window.left.x - 0.002, window.top.y), color=self.hideHUD())

        # фон полоски здоровья
        self.health_bar_gui = Sprite(ui_folder + "hp_ui.png", parent=camera.ui, origin=(-.5, .5),
                                     scale=.4, position=(window.left.x + .02, window.top.y - .03, -0.001),
                                     color=self.hideHUD())
        # полоска здоровья
        self.health_bar = Entity(parent=camera.ui, model="quad", texture=ui_folder + "hp_bar.png", scale=(.22, .01),
                                 position=(window.left.x + .08, window.top.y - .062, -0.002), origin=(-.5, 0),
                                 color=self.hideHUD())

        # фон полоски радиации
        self.rad_bar_gui = Sprite(ui_folder + "antirad.png", parent=camera.ui, origin=(-.5, .5),
                                     scale=.4, position=(window.left.x + .02, window.top.y - .1, -0.001),
                                  color=color.clear)
        # полоска радиации
        self.rad_bar = Entity(parent=camera.ui, model="quad", texture=ui_folder + "rad_bar.png", scale=(.22, .01),
                                 position=(window.left.x + .085, window.top.y - .13, -0.002), origin=(-.5, 0),
                              color=color.clear)

        self.hit_indicator_l = Sprite(ui_folder + "dmgL.png", parent=camera.ui, origin=(0, 0),
                                     scale=.4, position=(-.3,0),
                                  color=color.clear)
        self.hit_indicator_r = Sprite(ui_folder + "dmgR.png", parent=camera.ui, origin=(0, 0),
                                      scale=.4, position=(.3, 0),
                                      color=color.clear)

        self.work_in_progress = ui.UIText("WORK IN PROGRESS",offset=(0.0015,0.0015),color=color_red if show_hud else self.hideHUD(),y=-0.38)

        self.scope = None

        if fps_mode:
            # 3д модель худа рук
            self.hud_hands = Entity(parent=self.camera_pivot, model=mesh_folder + "fps_hands",
                                    texture=tex_folder + "pstalker.png",
                                    rotation=(-6, 13, 4), position=(.02, -.18, .34), scale=1)
            # 3д модель оружия в руках
            self.hud_weapon = Entity(parent=self.hud_hands, model=mesh_folder + "fps_lr_300",
                                     texture=tex_folder + "texobj2.png",
                                     rotation=(0, 3, 0), position=(-.04, 0, .03), scale=1, double_sided=True)

        self.weapon_2d_hud = Sprite(ui_folder+"fort_hud.png",scale=.5,
                                    position=(.485,-.4,0.001),
                                    parent=camera.ui)

        self.ammo_counter = Sprite(ui_folder+"ammo_hud.png",scale=.25,
                                    position=(0,-.451,0.001),
                                    parent=camera.ui, color=self.hideHUD())

        self.ammo_text = Text("12/12",position=(0,-.455,-0.002),origin=(0,0),parent=camera.ui,
                              color=color_gray if show_hud else self.hideHUD())

        self.shoot_sparkle = Sprite(ui_folder+"wm.png",
                                    position=(0.25,-0.29,0.001),scale=0.5,
                                    parent=camera.ui,origin=(0,0),enabled=False,color=self.hideHUD())

        #self.ammo_icon = Sprite(ui_folder+"items/ammo_oc.png",
        #                            position=(-0.1,window.bottom.y+0.05,-0.001),scale=0.3,
        #                            parent=camera.ui,origin=(-.5,0))

        self.press_f = ui.UIText(TKey("press")+" [F]", parent=camera.ui,offset=(0.0018,0.0018), y=-0.35, enabled=False,
                                 color=color.white,origin=(0,0))

        self.fps_counter = ui.UIText("fps", (0.0018, 0.0018), color=color_orange,
                                     position=(window.right.x - 0.13, window.top.y - .1))
        # >> сообщение сбоку экрана
        self.msg = ui.UIText("", origin=(-.5, 0),offset=(0.0015, 0.0015), parent=camera.ui,
                             position=(window.left.x+0.02, 0),
                             color=color_orange if show_hud else self.hideHUD())

        #self.side_window = Sprite(ui_folder + "window_hud.png", scale=.25,
        #                           position=(window.left.x, window.bottom_left.y, 0.001),
        #                           parent=camera.ui)
        #self.side_window.x = window.left.x+self.side_window.scale_x/2 + 0.02
        #self.side_window.y = window.bottom_left.y + self.side_window.scale_y/2 + 0.01

        self.gameover_screen = ui.GameOverScreen(enabled=False)

        # ------------------------------
        # если режим разработчика вкл
        if setting.developer_mode:
            # Рисуем окно с выводом дебаг информации
            # Темный фон
            self.debug_info_window = Entity(parent=camera.ui, model="quad", color=color.rgba(10, 10, 10, 200) if show_hud else self.hideHUD(),
                                            origin=(-.5, .5),
                                            position=Vec2(window.top_left.x + 0.02, window.top_left.y - 0.073),
                                            scale=Vec2(0.4, 0.4))
            # Текст на фоне
            self.debug_text = Text(parent=camera.ui, text="null", color=color_orange if show_hud else self.hideHUD(), origin=(-.5, .5),
                                   position=(window.top_left.x + 0.03, window.top_left.y - 0.08, -0.003))
            # подсказка для управления камеры
            Text(parent=camera.ui, text="Q - Up\nE - Down\n\nRMB(Hold) - Rotate camera\n\nW A S D - Move\nESC - Quit",
                 color=color_orange if show_hud else self.hideHUD(), origin=(-.5, -.5),
                 position=(window.bottom_left.x + .03, window.bottom_left.y + .03),
                 background=show_hud)

        # ПАРАМЕТРЫ ИГРОКА
        self.health = player_creature["start_max_hp"]
        self.health_max = player_creature["start_max_hp"]
        self.radiation = False
        self.radiation_timer = 20
        self.radiation_on_level = False
        self.armor = 0
        self.damage = 0
        self.accuracy = 0.05
        self.anomaly_armor = 0
        self.money = player_creature["start_money"]
        # ИГРОВЫЕ ОКНА
        self.inventory = Inventory(enabled=False)
        self.dialogue = Dialogue(enabled=False)
        self.loot = LootWindow(enabled=False)
        self.trading = TradeWindow(enabled=False)
        self.pause_menu = GamePause(enabled=False)
        # СИСТЕМЫ
        self.quests = Quests()
        self.weapon = WeaponSystem()
        self.event_keys = []
        # ДИАПАЗОН ПОВОРОТА ПО [Y]
        self.rotation_range_y = [-60,60]
        # ----------------
        self.health = self.health_max
        # ----------------
        self.at_marker_pos = False
        self.transition_trigger = None
        self.waypoints = []
        self.wp_index = 0
        self.last_waypoint = False
        self.mouse_conrol = True

        if pause:
            self.pause_menu.enable()

        for key, value in kwargs.items():
            setattr(self, key, value)

        for q in player_creature["start_quests"]:
            self.quests.add_quest(q)

        for ek in player_creature["start_event_keys"]:
            self.event_keys.append(ek)

        # Test dialogue launch
        #invoke(self.show_custom_dialogue, "tutorial_info", "info", delay=0.01)

        if options_file["first_launch"]:
            invoke(self.show_custom_dialogue,"tutorial_info","info",delay=0.01)
            my_json.change_key("assets/options", "first_launch", False)

        invoke(enable_pda_in_pause,True,delay=0.0001)
        invoke(self.weapon.update_weapons,delay=0.001)

    def show_custom_dialogue(self, id, name):
        self.dialogue.start_dialogue(id)
        self.dialogue.dialogue_file = id
        self.dialogue.npc_name.text = name.upper()

    def antirad_counter(self):
        if self.radiation and self.radiation_timer <= 0:
            self.rad_bar_gui.color = color.clear
            self.rad_bar.color = color.clear
            self.radiation = False
            self.radiation_timer = 20
            self.hit_by_radiation()
        if self.radiation and self.radiation_timer > 0:
            if self.radiation_sound.playing and pause or not pause:
                self.radiation_sound.stop(destroy=False)
                if not pause:
                    self.radiation_timer -= 1
            self.update_radbar()
            invoke(self.antirad_counter,delay=1)

    def hit_by_radiation(self):
        if self.radiation_on_level and not pause:
            if not self.radiation:
                if not self.radiation_sound.playing:
                    self.radiation_sound.play()
                self.hit(5)
                invoke(self.hit_by_radiation,delay=3)



    def run_antirad(self):
        self.rad_bar_gui.color = color.white
        self.rad_bar.color = color.white
        self.antirad_counter()


    # провести луч для проверки столкновения
    def raycast_once(self):
        self.ray_hit = raycast(self.position + (self.down * 0.04), direction=Vec3(camera.forward), ignore=(self,),
                               distance=50,
                               debug=False)

    # нанести урон в кол-ве value
    def hit(self, value):
        global isdead

        def hide_rad_indicators():
            self.hit_indicator_l.color = color.clear
            self.hit_indicator_r.color = color.clear

        if self.health > 0:
            self.health -= value
            self.update_healthbar()
            self.hit_sound.play()
            if self.radiation_on_level:
                self.hit_indicator_l.color = color.white
                self.hit_indicator_r.color = color.white
                invoke(hide_rad_indicators,delay=.7)
                invoke(hide_rad_indicators, delay=.7)

        if self.health <= 0:
            self.health = 0
            isdead = True

        if isdead:
            application.pause()
            self.gameover_screen.enabled = True

    def set_health(self,value):
        self.health = value
        self.update_healthbar()

    def set_max_health(self,value):
        self.health_max = value
        self.update_healthbar()

    def set_radiation(self,value):
        self.radiation = value

    def set_player_pos(self,x,y,z):
        self.position = (x,y,z)

    def set_crosshair(self,b):
        if not b:
            self.crosshair_tip.color = color.clear
            self.cursor.color = color.clear
            self.press_f.color = color.clear
        else:
            self.crosshair_tip.color = color.white
            self.cursor.color = color.white
            self.press_f.color = color.white

    def get_player_pos(self):
        return self.position

    def update_healthbar(self):
        self.health_bar.scale_x = clamp(.22 * self.health / self.health_max, 0, .22)

    def update_radbar(self):
        self.rad_bar.scale_x = clamp(.22 * self.radiation_timer / 20, 0, .22)

    # функция отслеживания нажатий
    def input(self, key):
        global gameplay
        global pause

        if not pause and not self.dialogue.enabled and not self.loot.enabled:
            # >> Стрельба
            if key == "left mouse down" and self.weapon.current_weapon:
                if self.weapon.current_weapon.clip > 0:
                    invoke(self.weapon.shoot,delay=self.weapon.current_weapon.speed)
                else:
                    self.weapon.empty_sound.play()

            if key == "right mouse down":
                if self.weapon.current_weapon and "scope" in self.weapon.current_weapon.data:
                    camera.fov = lerp(self.original_fov, self.weapon.current_weapon.data["scope"]["fov"],1)
                    self.scope = Sprite(ui_folder + "scope.png", parent=camera.ui, origin=(0, 0), scale=.4,
                                 position=(0, 0,-1))
                    self.cursor.color = color.clear
                    #self.crosshair_tip.color = color.clear
            elif key == "right mouse up":
                camera.fov = self.original_fov
                if self.scope:
                    self.cursor.color = color.white
                    destroy(self.scope,delay=0.0001)
                    #self.crosshair_tip.color = color_orange

            # >> Перезарядка
            if key == "r" and self.weapon.current_weapon:
                self.weapon.reload_weapon()

            # Если кнопка С нажата и в режиме разработчика, то копируем нашу позицию в буфер
            if key == "c" and not setting.developer_mode:
                pass
                #self.hit(15)
                #self.quests.get_quest("quest_rusty_1").complete()

            if key == "1" and self.weapon.pistol:
                if self.weapon.current_weapon and self.weapon.current_weapon.id == self.weapon.pistol.id:
                    self.weapon.hide_weapon()
                if self.weapon.current_weapon and self.weapon.current_weapon.id != self.weapon.pistol.id or self.weapon.current_weapon is None:
                    self.weapon.hide_weapon()
                    self.weapon.draw_weapon("pistol")

            if key == "2" and self.weapon.rifle:
                if self.weapon.current_weapon and self.weapon.current_weapon.id == self.weapon.rifle.id:
                    self.weapon.hide_weapon()
                if self.weapon.current_weapon and self.weapon.current_weapon.id != self.weapon.rifle.id or self.weapon.current_weapon is None:
                    self.weapon.hide_weapon()
                    self.weapon.draw_weapon("rifle")

            # если луч столкнулся с объектом
            if self.ray_hit.hit:

                def getHitData():
                    return self.ray_hit.entity

                def clearCrosshairText():
                    self.crosshair_tip_text = ""
                    self.press_f.enabled = False

                # если объект имеет энтити и его id не пустой
                if getHitData() and getHitData().id is not None:
                    # при нажатии кнопки взаимодействия
                    if key == "f" and game_session:
                        # получаем ключи объекта уровня
                        lvl_keys = getHitData().keys
                        # если айди объекта "переход" то перемещаем игрока
                        if getHitData().id == "transition":
                            self.steps_sound.play()
                            # делаем экран чёрным
                            camera.overlay.color = color.black
                            # спавним текст загрузки по центру
                            loading = Text(TKey("loading"), origin=(0, 0), color=color_orange, always_on_top=True)
                            loading_icon = Animation("assets/ui/rads", fps=12, origin=(.5, 0), x=-.1,
                                                     always_on_top=True,
                                                     parent=camera.ui, scale=0.03)
                            # если есть ключ конкретных координат
                            if "target_position" in lvl_keys:
                                # перемещаем игрока по ним в пределах уровня
                                get_player().position = (lvl_keys["target_position"])
                            else:
                                # иначе перемещаем непосредственно на позицию триггера перехода
                                get_player().position = (getHitData().x, get_player().y, getHitData().z)
                            # через секунду убрать чёрный экран
                            invoke(setattr, camera.overlay, 'color', color.clear, delay=1)
                            # удалить текст с загрузкой
                            destroy(loading, delay=1)
                            destroy(loading_icon, delay=1)
                        # если айди объекта "переход на уровень" то меняем уровень
                        if getHitData().id == "transition_to_level":
                            self.at_marker_pos = False
                            self.transition_trigger = getHitData()
                            if "waypoints" in getHitData().keys:
                                self.waypoints = my_json.read("assets/scripts/waypoints")[getHitData().keys["waypoints"]]["list"]

                        # если айди объекта "обыскать деньги" то
                        if getHitData().id == "loot_money":
                            # создаём текст с получаемой суммой
                            loot = ui.UIText("$" + str(getHitData().keys["value"]), origin=(-.5, 0),
                                             position=(window.left.x + .03, 0), scale=1.1, color=color_orange)
                            # прибавляем деньги
                            get_player().money += getHitData().keys["value"]
                            # удаляем невидимый триггер объект
                            destroy(getHitData())
                            # удаляем надпись
                            destroy(loot, delay=1)
                            self.crosshair_tip_text = ""

                        if getHitData().id == "loot":
                            self.loot.start_loot(getHitData().keys["loot_id"])
                            destroy(getHitData())
                            self.crosshair_tip_text = ""

                        if getHitData().id == "npc":
                            # Если есть ключ с диалогом и НПС не торговец
                            if getHitData().profile["dialogues"] and getHitData().profile["trader_profile"] is None:
                                # Функция начала диалога
                                def startDialog():
                                    self.dialogue.start_dialogue(d["dialogue"])
                                    self.dialogue.dialogue_file = d["dialogue"]
                                    self.dialogue.npc_name.text = TKey(getHitData().profile["name"]).upper()
                                    clearCrosshairText()

                                for d in getHitData().profile["dialogues"]:
                                    # Если dont_has_event_key ключ существует, а has_event_key не существует
                                    if "dont_has_event_key" in d and "has_event_key" not in d:
                                        if not has_e_key(d["dont_has_event_key"]):
                                            startDialog()
                                    # Если has_event_key существует и dont_has_event_key существует
                                    if "has_event_key" in d and "dont_has_event_key" in d:
                                        if has_e_key(d["has_event_key"]) and not has_e_key(d["dont_has_event_key"]):
                                            startDialog()
                                    # Если has_event_key существует, а dont_has_event_key не сущесвтует
                                    if "has_event_key" in d and "dont_has_event_key" not in d:
                                        if has_e_key(d["has_event_key"]):
                                            startDialog()
                                    # Если has_event_key не существует и dont_has_event_key тоже
                                    if "has_event_key" not in d and "dont_has_event_key" not in d:
                                        startDialog()
                                        break
                            # Если НПС имеет профиль торговца
                            if getHitData().profile["trader_profile"] is not None:
                                # Если нет файла профиля - крашим игру
                                if getHitData().profile["trader_profile"] not in my_json.read("assets/creatures/traders"):
                                        if bug_trap.crash_game_msg("Error", "Trader [{0}] ID not found in \"assets/creatures/traders.json\"!", 1):
                                            application.quit()
                                else:
                                    self.trading.enable()
                                    self.trading.trader_id = getHitData().profile["trader_profile"]
                                    self.trading.buy = True
                                    self.trading.selector_id = 0
                                    self.trading.fill_slots_with_items(getHitData().profile["trader_profile"])
                                    clearCrosshairText()
                        # запускаем луч, что бы убрать все надписи под прицелом
                        invoke(self.raycast_once, delay=.05)

            if key == "escape" and not self.dialogue.enabled and not self.loot.enabled and not self.trading.enabled:
                pause = True
                invoke(self.pause_menu.enable, delay=0.001)
                self.pause_menu.inventory_window = self.inventory
                self.pause_menu.update_colors()

        # Если мы в игре
        #if gameplay:
            # Если нажали ESCAPE то закрыть приложение
        if key == "x":
            application.quit()
        # Если игровой процесс запущен (Геймплей)

    # ФУНКЦИЯ ОБНОВЛЕНЯ ДЛЯ КАЖДОГО КАДРА
    def update(self):
        if not pause and \
           not self.dialogue.enabled and \
           not self.loot.enabled and \
           not self.trading.enabled:

            if options_file["show_fps"]:
                self.fps_counter.setText("FPS: {0}".format(window.fps_counter.text))
            # позиция луча
            origin = self.position + (self.down * 0.04)
            # направление камеры
            self.direction = Vec3(camera.forward)

            #animated transition between levels
            if not self.at_marker_pos and self.transition_trigger is not None:
                # moving by waypoints
                self.mouse_conrol = False
                self.set_crosshair(False)
                if self.waypoints:
                    i = self.wp_index
                    wp = self.waypoints

                    if distance(wp[i]["position"], get_player().position) < 5:
                        if self.wp_index < len(wp)-1:
                            self.wp_index += 1
                        else:
                            self.last_waypoint = True
                            self.wp_index = 0

                    else:
                        if not self.last_waypoint:
                            get_player().position = lerp(get_player().position, wp[i]["position"], time.dt * wp[i]["speed"])
                            #get_player().shake(duration=1,magnitude=0.01,speed=0.7,direction=(0,1.5))
                            get_player().rotation = lerp(get_player().rotation, wp[i]["rotation"], time.dt * wp[i]["speed"])

                    if self.last_waypoint:
                        get_player().position = lerp(get_player().position, self.transition_trigger.position, time.dt * 1)
                        get_player().rotation = lerp(get_player().rotation, self.transition_trigger.rotation, time.dt * 1)

                else:
                    get_player().position = lerp(get_player().position, self.transition_trigger.position, time.dt * 1)
                if distance(get_player().position, self.transition_trigger.position) < 3:
                    self.steps_sound.play()
                    # зачерняем экран
                    camera.overlay.color = color.black
                    # создаём текст загрузки
                    loading = Text(TKey("loading"), origin=(0, 0), color=color_orange, always_on_top=True)
                    loading_icon = Animation("assets/ui/rads", fps=12, origin=(.5, 0), x=-.1,
                                             always_on_top=True,
                                             parent=camera.ui, scale=0.03)
                    # удаляем текущий уровень
                    destroy(get_current_level())
                    # загружаем новый по айди из ключа "уровень"
                    set_current_level(self.transition_trigger.keys["level"])
                    self.transition_trigger = None
                    self.last_waypoint = False
                    self.waypoints = []
                    self.mouse_conrol = True
                    self.set_crosshair(True)
                    # убрать чёрный экран
                    invoke(setattr, camera.overlay, 'color', color.clear, delay=2)
                    # удалить текст загрузки
                    destroy(loading, delay=2)
                    destroy(loading_icon, delay=2)


            # если мышь двигается
            if self.mouse_conrol:
                if mouse.velocity > 0 or mouse.velocity < 0:
                    # пускаем луч
                    self.ray_hit = raycast(origin, self.direction, ignore=(self,), distance=50,
                                           debug=setting.show_raycast_debug)
                    # self.hit_pos_info.text = self.raycast_point_pos_text

            def setCrosshairTip(text):
                self.crosshair_tip_text = TKey(text)
                self.press_f.enabled = True

            def clearCrosshairText():
                self.crosshair_tip_text = ""
                self.press_f.enabled = False

            def getHitData():
                if self.ray_hit.hit:
                    return self.ray_hit.entity

                # РЭЙКАСТИНГ, ВЗАИМОДЕЙСТВИЕ С МИРОМ
            if self.ray_hit.hit:
                if getHitData() is not None:

                    if setting.developer_mode:
                        self.hit_text = getHitData() if getHitData() else "None"

                    if self.weapon.current_weapon:
                        self.cursor.texture = "assets/ui/crosshair.png"
                        self.cursor.scale = .04
                    else:
                        self.cursor.texture = "assets/ui/crosshair.png"
                        self.cursor.scale = .04

                    if getHitData().id == "transition" or getHitData().id == "transition_to_level":
                        setCrosshairTip("interact.go")

                    if getHitData().id == "loot_money":
                        setCrosshairTip("interact.loot.money")

                    if getHitData().id == "loot":
                        setCrosshairTip("interact.loot")

                    if getHitData().id == "npc":
                        setCrosshairTip(getHitData().profile["name"])

                    if getHitData().id == "" or getHitData().id is None:
                        clearCrosshairText()
            else:
                if setting.developer_mode:
                    self.hit_text = "None"
                if self.weapon.current_weapon:
                    self.cursor.texture = "assets/ui/crosshair_weapon.png"
                    self.cursor.scale = .06
                else:
                    self.cursor.texture = "assets/ui/crosshair.png"
                    self.cursor.scale = .04
                clearCrosshairText()

            # если в режиме разработчика, то включаем полёт персонажа и вывод инфы
            if setting.developer_mode:
                # self.raycast_point_pos_text = mouse.world_point

                if held_keys["w"]:
                    self.position += self.direction * self.speed * time.dt
                if held_keys["s"]:
                    self.position -= self.direction * self.speed * time.dt
                if held_keys["a"]:
                    self.position += self.left * self.speed * time.dt
                if held_keys["d"]:
                    self.position += self.right * self.speed * time.dt


                # Управление летающей камерой
                if held_keys["q"]: self.y -= setting.camera_move_speed * time.dt
                if held_keys["e"]: self.y += setting.camera_move_speed * time.dt

                # Если включён режим разработчика, обновлять информацию в дебаг окне
            if setting.developer_mode:
                self.debug_text.text = "POS X: " + str(round(self.x, 2)) + \
                                       "\nPOS Y: " + str(round(self.y, 2)) + \
                                       "\nPOS Z: " + str(round(self.z, 2)) + \
                                       "\n\nROT X: " + str(round(self.camera_pivot.rotation.x, 2)) + \
                                       "\nROT Y: " + str(round(self.rotation.y, 2)) + \
                                       "\nROT Z: " + str(round(self.camera_pivot.rotation.z, 2)) + \
                                       "\n\nVEL X: " + str(round(mouse.velocity[0], 2)) + \
                                       "\nVEL Y: " + str(round(mouse.velocity[1], 2)) + \
                                       "\n\nHIT: " + str(self.hit_text)
            if self.mouse_conrol:
                if self.strange_mouse:
                    # Поворот камеры с помощью мышки
                    self.rot_average_x = 0
                    self.rot_average_y = 0

                    self.rot_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                    self.rot_x += mouse.velocity[1] * self.mouse_sensitivity[0]

                    self.rot_array_y.append(self.rot_y)
                    self.rot_array_x.append(self.rot_x)

                    if len(self.rot_array_y) >= self.frame_count:
                        self.rot_array_y.remove(self.rot_array_y[0])
                    if len(self.rot_array_x) >= self.frame_count:
                        self.rot_array_x.remove(self.rot_array_x[0])

                    for rotY in self.rot_array_y:
                        self.rot_average_y += rotY
                    for rotX in self.rot_array_x:
                        self.rot_average_x += rotX

                    self.rot_average_y /= len(self.rot_array_y)
                    self.rot_average_x /= len(self.rot_array_x)

                    self.rotation_y += self.rot_average_y
                    self.rotation_y = clamp(self.rotation_y, self.rotation_range_y[0], self.rotation_range_y[1])
                    self.camera_pivot.rotation_x -= self.rot_average_x
                    self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -30, 30)
                else:
                    self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                    self.rotation_y = clamp(self.rotation_y, self.rotation_range_y[0], self.rotation_range_y[1]) if not setting.developer_mode else self.rotation_y
                    self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                    self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -30, 30) if not setting.developer_mode else clamp(self.camera_pivot.rotation_x, -90, 90)

                if not self.scope:
                    self.crosshair_tip.setText(self.crosshair_tip_text)

# Главный класс игрового процесса
class Gameplay():
    def __init__(self, **kwargs):
        super().__init__()
        # Глобальные переменные для изменения
        global gameplay
        global game_session

        game_session = self
        # переменная с ссылкой на класс игрока (спауним гг)
        self.player = Player()
        # переменная с ссылкой на класс уровня (спауним уровень)
        # передаём ссылку с созданным гг в уровень для дальнейшего доступа к классу гг
        self.current_level = Level(self.player, level_id=player_creature["start_level"])
        # игровой процесс запущен
        gameplay = True

        # цикл для проверки аргументов и изменение переменных
        for key, value in kwargs.items():
            setattr(self, key, value)

    # получить идентификатор текущего уровня
    def get_level(self):
        return self.current_level.level_id


# Класс уровня
class Level(Entity):
    def __init__(self, p, **kwargs):
        super().__init__()
        # текстовый идентификатор уровня
        self.level_id = None
        # ссылка на существующего гг
        self.player_data = p
        self.with_light = False
        self.level_objects = []
        self.npc_data = []

        for key, value in kwargs.items():
            setattr(self, key, value)

        # DirectionalLight (parent=Entity(), y=35, rotation=(45,0,0), shadows=True)

        # Если мы начали игру
        if os.path.isdir("assets/levels/" + str(self.level_id)):
            level_data = my_json.read("assets/levels/" + str(self.level_id) + "/level")
            # Настраиваем цвет неба
            window.color = color.rgb(level_data["weather_color"][0], level_data["weather_color"][1],
                                     level_data["weather_color"][2])
            if "rotation_range" in level_data:
                self.player_data.rotation_range_y[0] = level_data["rotation_range"][0]
                self.player_data.rotation_range_y[1] = level_data["rotation_range"][1]
            else:
                self.player_data.rotation_range_y[0] = -60
                self.player_data.rotation_range_y[1] = 60

            if "radiation" in level_data:
                if level_data["radiation"]:
                    get_player().radiation_on_level = True
                    invoke(get_player().hit_by_radiation,delay=4)
                else:
                    get_player().radiation_on_level = False
            else:
                get_player().radiation_on_level = False

            # Создаём объекты из папки с уровнем из файла level
            for obj in level_data["level_data"]:

                if "light" in level_data:
                    for light in level_data["light"]:
                        if light["type"] == "point":
                            PitoPointLight(shadows=light["shadows"],
                                       colour=color.rgba(light["color"][0],light["color"][1],light["color"][2],.1),
                                       position=light["position"],
                                       rotation=light["rotation"],
                                       distance=light["distance"],
                                       parent=self)
                            break

                # если в объекте уровня есть ключ ID и его параметр spawn_point
                if "id" in obj:
                    # Присваиваем начальную позицию гг, равную позиции спавн точки
                    if obj["id"] == "spawn_point":
                        self.player_data.position = obj["position"]

                    if obj["id"] == "animation":
                        Animation(tex_folder + obj["sequence"], position=obj["position"], rotation=obj["rotation"],
                                  scale=obj["scale"],parent=self)


                    if obj["id"] == "text":
                        Text(parent=scene, text=obj["string"], position=obj["position"],
                             rotation_y=get_player().rotation.y,
                             scale=obj["scale"])

                    if obj["id"] == "npc":
                        lvl_npc = PitoActor(obj["profile"])
                        lvl_npc.position = obj["position"]
                        lvl_npc.rotation = obj["rotation"]
                        lvl_npc.id = obj["id"]
                        lvl_npc.keys = obj
                        if "collider" in obj:
                            lvl_npc.collider = BoxCollider(lvl_npc,center=obj["collider"]["pos"],
                                                           size=obj["collider"]["size"])
                        self.npc_data.append(lvl_npc)
                        if "shader" in obj and obj["shader"]:
                            lvl_npc.shader = colored_lights_shader

                        if "ambient" in obj:
                            _light = PandaAmbientLight('ambient_light')
                            for l in level_data["light"]:
                                if "id" in l and l["id"] == obj["ambient"]:
                                    _light.setColor(color.rgba(l["color"][0], l["color"][1], l["color"][2], 1))
                                    break

                            lvl_npc.setLight(lvl_npc.attachNewNode(_light))

                # Cоздаём объект
                lvl_obj = LevelObject(parent=self, model=obj["model"] if "model" in obj else "cube",
                                      texture=obj["texture"] if "texture" in obj else None,
                                      rotation=obj["rotation"] if "rotation" in obj else (0,0,0),
                                      position=obj["position"] if "position" in obj else (0,0,0),
                                      filtering=None,
                                      collider=obj["collider"] if "collider" in obj else None,
                                      scale=obj["scale"] if "scale" in obj else 1,
                                      double_sided=obj["double_sided"] if "double_sided" in obj else False,
                                      color=color.rgba(obj["color"][0],
                                                       obj["color"][1],
                                                       obj["color"][2],
                                                       obj["color"][3]) if "color" in obj and setting.developer_mode or "color" in obj and "id" in obj and setting.developer_mode else color.white if "id" not in obj else color.clear,
                                      id=obj["id"] if "id" in obj else None)

                if "shader" in obj and obj["shader"]:
                    lvl_obj.shader = colored_lights_shader

                if "ambient" in obj:
                    _light = PandaAmbientLight('ambient_light')
                    for l in level_data["light"]:
                        if "id" in l and l["id"] == obj["ambient"]:
                            _light.setColor(color.rgba(l["color"][0],l["color"][1],l["color"][2],1))
                            break

                    lvl_obj.setLight(lvl_obj.attachNewNode(_light))

                scene.fog_density = 0.015
                scene.fog_color = color.rgb(level_data["weather_color"][0], level_data["weather_color"][1],
                                     level_data["weather_color"][2])

                #if not setting.developer_mode and lvl_obj.id:
                #    lvl_obj.color = color.clear

                # присваиваем ему все ключи из файла с уровнем
                lvl_obj.keys = obj
                self.level_objects.append(lvl_obj)

        else:
            if bug_trap.crash_game_msg("Error","Level assets/levels/\"{0}\" not found!".format(self.level_id),1):
                application.quit()

# Класс объекта на уровне
class LevelObject(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        # ключ идентификатор
        self.id = None
        # словарь ключей из файла с уровнем "ключ": значение
        self.keys = {}

        for key, value in kwargs.items():
            setattr(self, key, value)


class GamePause(Entity):
    def __init__(self, **kwargs):
        super().__init__(z=-0.11)
        self.selected_element = 0
        self.journal_window = JournalWindow(enabled=False)
        self.inventory_window = None
        self.pda_window = PDA(enabled=False)
        self.pda_enabled = True
        self.skills_window = SkillsWindow(enabled=False)
        self.click_sound = Audio("assets/sounds/click", autoplay=False, loop=False)

        self.menu_punkts = [
            Text(TKey("pause.resume"), color=color_orange),
            Text(TKey("pause.inv"), color=color_orange),
            Text(TKey("pause.journal"), color=color_orange),
            Text(TKey("pause.pda"), color=rgb(40,40,40)),
            Text(TKey("pause.skills"),color=color_orange),
            Text(TKey("pause.exit"), color=color_orange)
        ]

        self.update_colors()

        self.parent = camera.ui
        Entity(parent=self, model="quad", color=rgb(10, 10, 10), scale=window.size)
        self.frame = Sprite(ui_folder + "16_9_frame.png", parent=self, scale=0.222,z=-0.001)

        Text(TKey("mm.title").upper(), parent=self, y=0.35, x=0, origin=(0, 0))
        Text(TKey("pause.title").upper(), parent=self, y=0.30, x=0, origin=(0, 0))
        self.tip_bottom = Text(
            dedent(TKey("pause.control.tip")).strip(),
            parent=self, y=-0.40, x=-0.7,z=-0.001, origin=(-.5, 0), color=color.dark_gray, size=4)

        if self.menu_punkts:
            offset = 0.25
            spacing = .01
            height = 0.01 - spacing
            if isinstance(self.menu_punkts, dict):
                self.menu_punkts = self.menu_punkts.values()

            for p in self.menu_punkts:
                if isinstance(p, Text):
                    p.x -= .045
                    p.y = offset
                    p.parent = self
                    p.origin = (-.5, 0)
                    height += len(p.lines) / 100 * 7
                    p.y -= height
                    p.z = -0.01

            self.selector = Sprite(ui_folder + "rad_icn.png", parent=self, y=self.menu_punkts[0].y, x=-.085,z=-0.003, scale=.21,
                                   origin=(-.5, 0))
        else:
            if bug_trap.code_error("game_session->player->pause_menu->menu_punkts is empty!"):
                application.quit()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update_colors(self):
        if self.pda_enabled:
            self.menu_punkts[3].color = color_orange
        else:
            self.menu_punkts[3].color = rgb(40, 40, 40)

    def input(self, key):
        global pause

        if pause and self.enabled:
            if key == "escape":
                pause = False
                invoke(get_player().hit_by_radiation,delay=3)
                self.disable()

            if key == "down arrow" or key == "s":
                self.click_sound.play()
                self.selected_element += 1
                if self.selected_element > len(self.menu_punkts) - 1:
                    self.selected_element = 0
                self.selector.y = self.menu_punkts[self.selected_element].y

            if key == "up arrow" or key == "w":
                self.click_sound.play()
                self.selected_element -= 1
                if self.selected_element < 0:
                    self.selected_element = len(self.menu_punkts) - 1
                self.selector.y = self.menu_punkts[self.selected_element].y

            if key == "enter":
                # Resume
                if self.selected_element == 0:
                    pause = False
                    self.disable()

                # Inventory
                if self.selected_element == 1:
                    invoke(self.inventory_window.enable, delay=0.001)
                    self.inventory_window.root_window = self

                    self.disable()
                    self.inventory_window.update_items_2()
                    self.inventory_window.update_player_stats()
                    self.inventory_window.update_inv_healthbar()
                    self.inventory_window.update_cursor()

                # Journal
                if self.selected_element == 2:
                    invoke(self.journal_window.enable, delay=0.001)
                    self.journal_window.root_window = self

                    self.disable()
                    self.journal_window.journal_update()

                # PDA
                if self.selected_element == 3:
                    if self.pda_enabled:
                        invoke(self.pda_window.enable, delay=0.001)
                        self.pda_window.root_window = self
                        self.pda_window.update_markers()
                        self.pda_window.update_cursor()
                        self.disable()

                # SKILLS
                if self.selected_element == 4:
                    invoke(self.skills_window.enable, delay=0.001)
                    self.skills_window.root_window = self
                    self.disable()

                # Exit
                if self.selected_element == len(self.menu_punkts) - 1:
                    scene.clear()
                    camera.overlay.color = color.black
                    loading = Text(TKey("loading"), origin=(0, 0), color=color_orange, always_on_top=True)
                    loading_icon = Animation("assets/ui/rads", fps=12, origin=(.5, 0), x=-.1,
                                             always_on_top=True,
                                             parent=camera.ui, scale=0.03)
                    invoke(main_menu.MainMenu, delay=0.0001)
                    destroy(loading, delay=2)
                    invoke(setattr, camera.overlay, 'color', color.clear, delay=2)
                    destroy(loading_icon, delay=2)


if __name__ == "__main__":
    game = Ursina()

    game.run()
