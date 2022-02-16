from ursina import *
import setting
import my_json
import game as gm
from main import language
import bug_trap
import os.path
from language_system import TKey
from language_system import language
import ui

scene = None
# Картинка в главное меню
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

mm_image = ui_folder + "i2_mm.png"
# Активный пункт элемента в меню
menu_buttons_counter = 0

# Список пунктов меню
menu_buttons_list = [
    TKey("mm.new.game"),
    TKey("mm.opt"),
    TKey("mm.about"),
    TKey("mm.exit")
]

# Пресеты для цветов
color_orange = color.rgb(238, 157, 49)
color_red = color.rgb(232, 0, 0)
color_green = color.rgb(40, 190, 56)

color_sky_day = color.rgb(74, 116, 159)
color_sky_evening = color.rgb(57, 46, 61)
color_sky_night = color.rgb(10, 10, 10)


class MainMenu(Entity):

    def __init__(self):
        super().__init__(parent=camera.ui, z=-0.001)
        global scene
        # Звук кликанья
        self.click_sound = Audio(sound_folder + "click", autoplay=False, loop=False)
        scene = self
        # Главное меню
        self.main_menu = Entity(parent=self, enabled=True)
        Entity(parent=self.main_menu, model="quad", color=rgb(10, 10, 10), scale=2)
        # Главное Меню
        Sprite(parent=self.main_menu, texture=mm_image, y=0.1, scale=0.5)
        self.menu_punkt = Text(parent=self.main_menu, text="← {0} →".format(menu_buttons_list[menu_buttons_counter]),
                               origin=(0, 0), y=-0.4,
                               color=color_orange)
        # self.rad_icon = Sprite(parent=self.main_menu, texture=ui_folder+"rad_icn.png", origin=(0, -.1),x=-.1, y=-0.4,
        #                       scale=.15)
        # self.ShowMessageBox("Test message box", "Test caption for this message window!","info")

    def ShowMessageBox(self, title, caption, type="info"):
        msg = ui.MessageBox(title, caption, type)
        msg.ignored_input_entity = self
        self.ignore_input = True

    def ChangeScreen(self, screen):
        camera.overlay.color = color.black
        loading = Text(TKey("loading"), origin=(0, 0), color=color_orange, always_on_top=True)
        destroy(loading, delay=1)
        invoke(screen, delay=1)
        destroy(self)
        invoke(setattr, camera.overlay, 'color', color.clear, delay=1)

    def input(self, key):
        global menu_buttons_counter
        if self.main_menu.enabled:
            # Если нажали ESCAPE то закрыть приложение
            #if key == "escape":
            #    application.quit()
                # my_json.change_key("assets/options","current_language","en")
            # Если нажали А то переключили пункт меню
            if key == "a" or key == "left arrow":
                self.click_sound.play()
                if menu_buttons_counter > 0:
                    menu_buttons_counter = menu_buttons_counter - 1
                else:
                    menu_buttons_counter = 3
            # Если нажали D то переключили пункт меню
            if key == "d" or key == "right arrow":
                self.click_sound.play()
                if menu_buttons_counter < 3:
                    menu_buttons_counter = menu_buttons_counter + 1
                else:
                    menu_buttons_counter = 0

            # Если нажали ENTER выбрав какой-то пункт меню, делаем действие
            if key == "enter":
                # Новая игра
                if menu_buttons_counter == 0:
                    self.ChangeScreen(gm.Gameplay)
                # Опции
                if menu_buttons_counter == 1:
                    self.main_menu.enabled = False
                    Options().options_menu.enabled = True
                # Об игре
                if menu_buttons_counter == 2:
                    self.main_menu.enabled = False
                    About().about_menu.enabled = True
                # Выйти в ОС
                if menu_buttons_counter == 3: application.quit()

            # Обновлять текст пунктов меню
            self.menu_punkt.text = "← {0} →".format(menu_buttons_list[menu_buttons_counter])


class Options(Entity):
    def __init__(self):
        super().__init__(z=0.002)
        global scene
        self.click_sound = Audio(sound_folder + "click", autoplay=False, loop=False)
        # Чтение файла настроек
        self.options = my_json.read("assets/options")
        # Опции
        self.options_menu = Entity(parent=camera.ui, enabled=False)
        self.fps_show_mode = self.options["show_fps"]
        self.autodotect_size = self.options["autodetect"]
        self.option_selector = 0
        self.option_punkts_list = []
        Entity(parent=self.options_menu, model="quad", color=rgb(10, 10, 10), scale=2)
        self.frame = Sprite(ui_folder + "16_9_frame.png", parent=self.options_menu, scale=0.222)
        Text(parent=self.options_menu, text=TKey("mm.opt"), y=window.top.y - 0.1, origin=(0.05, 0),
             color=color_orange)
        self.lang_punkt = Text(parent=self.options_menu, text=TKey("mm.opt.lang.selector"), origin=(-.5, 0), x=-0.4,
                               y=0.2)
        self.lang_text = ui.UIText(parent=self.options_menu, color=color_orange,
                                   text="[{0}]".format(TKey("lang." + language)), origin=(.5, -.5), x=0.3, y=0.21)
        self.fps_punkt = Text(parent=self.options_menu, text=TKey("mm.opt.fps.selector"), origin=(-.5, 0), x=-0.4,
                              y=0.15)
        self.fps_text = ui.UIText(parent=self.options_menu, color=color_orange,
                                  text="[{0}]".format(TKey("opt.yes") if self.options["show_fps"] else TKey("opt.no")),
                                  origin=(.5, -.5), x=0.3, y=0.16)
        self.autodetect_punkt = Text(parent=self.options_menu, text=TKey("mm.opt.autodetect.res.selector"),
                                     origin=(-.5, 0), x=-0.4, y=0.08)
        ui.UIText(parent=self.options_menu, color=color_orange,
                  text="[{0}]".format(TKey("opt.yes") if self.options["autodetect"] else TKey("opt.no")),
                  origin=(.5, -.5), x=0.3, y=0.07)
        self.apply_punkt = Text(parent=self.options_menu, text=TKey("mm.opt.apply"), origin=(0, 0), color=color_orange,
                                y=-0.3)

        # Adding all options elements to list for selector
        self.option_punkts_list.append(self.lang_punkt)
        self.option_punkts_list.append(self.fps_punkt)
        self.option_punkts_list.append(self.autodetect_punkt)

        # The last element in list (ALWAYS)
        self.option_punkts_list.append(self.apply_punkt)

        self.selector = Sprite(ui_folder + "rad_icn.png", parent=self.options_menu,
                               y=self.option_punkts_list[self.option_selector].y,
                               x=self.option_punkts_list[self.option_selector].x - 0.05, scale=.21,
                               origin=(-.5, 0))
        self.message = None
        self.tip_bottom = Text(
            dedent(TKey("mm.control.tip")).strip(),
            parent=self.options_menu, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)

    def ShowMessageBox(self, title, caption, type="info"):
        if self.message:
            invoke(destroy, self.message, delay=0.00001)
        self.message = ui.MessageBox(title, caption, type, parent=self.options_menu)
        self.message.ignored_input_entity = self
        self.options_menu.ignore_input = True

    def input(self, key):
        if self.enabled and key == "escape":
            scene.main_menu.enable()
            self.option_selector = 0
            self.options_menu.disable()

        if key == "w" or key == "up arrow":
            if self.option_selector > 0:
                self.option_selector -= 1
            else:
                self.option_selector = len(self.option_punkts_list) - 1
            # print (self.option_selector)

            if self.option_selector == len(self.option_punkts_list) - 1:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.15,
                                          self.option_punkts_list[self.option_selector].y)
            else:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.05,
                                          self.option_punkts_list[self.option_selector].y)

        if key == "s" or key == "down arrow":
            if self.option_selector < len(self.option_punkts_list) - 1:
                self.option_selector += 1
            else:
                self.option_selector = 0

            if self.option_selector == len(self.option_punkts_list) - 1:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.15,
                                          self.option_punkts_list[self.option_selector].y)
            else:
                self.selector.position = (self.option_punkts_list[self.option_selector].x - 0.05,
                                          self.option_punkts_list[self.option_selector].y)
        # print(self.option_selector)

        if self.enabled and key == "enter":
            self.click_sound.play()
            # FPS counter show
            if self.option_selector == 1:
                self.fps_show_mode = not self.fps_show_mode
                self.fps_text.setText("[{0}]".format(TKey("opt.yes") if self.fps_show_mode else TKey("opt.no")))

            # Apply button
            if self.option_selector == len(self.option_punkts_list) - 1:
                # apply settings
                # my_json.change_key ("assets/options", "show_fps", self.fps_show_mode)
                # close options
                # self.ShowMessageBox("Test message box", "Test caption for this message window!","info")
                scene.main_menu.enable()
                self.option_selector = 0
                self.options_menu.disable()


class About(Entity):
    def __init__(self):
        super().__init__(z=-0.003)
        global scene

        # Об игре
        self.about_menu = Entity(parent=camera.ui, enabled=False)
        Entity(parent=self.about_menu, model="quad", color=rgb(10, 10, 10), scale=2)
        self.frame = Sprite(ui_folder + "16_9_frame.png", parent=self.about_menu, scale=0.222)
        Text(parent=self.about_menu, text=TKey("mm.about"), y=window.top.y - 0.1, origin=(0.05, 0), color=color.clear)
        Text(parent=self.about_menu, text="ver. " + str(setting.version) + " " + setting.version_type,
             x=0,
             y=window.bottom.y + 0.1, z=-0.004, origin=(0, 0))
        Text(parent=self.about_menu, text=dedent(TKey("mm.about.text")).strip(),
             origin=(0, .5), wordwrap=70, y=0.1)

        Text(parent=self.about_menu, text=dedent(TKey("mm.about.text.1")).strip(),
             origin=(0, .5), wordwrap=70, y=-0.2)
        Text(parent=self.about_menu, text=dedent(TKey("mm.about.text.2")).strip(),
             origin=(0, .5), wordwrap=70, y=-0.25)
        Text(parent=self.about_menu, text=dedent(TKey("mm.about.text.3")).strip(),
             origin=(0, 0), wordwrap=70, y=-0.3)

        Sprite("assets/ui/i2.png", parent=self.about_menu, x=-0.15, y=0.25, scale=0.3)
        Sprite("assets/ui/gsc.png", parent=self.about_menu, x=0.15, y=0.25, scale=0.3)
        Sprite("ursina_logo.png", parent=self.about_menu, x=-0.15, y=-0.1, scale=0.04)
        Sprite("ursina_wink_0001.png", parent=self.about_menu, x=0.15, y=-.1, scale=0.25)

        self.tip_bottom = Text(
            dedent(TKey("pause.journal.quest.control.tip")).strip(),
            parent=self.about_menu, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)

    def input(self, key):
        if self.enabled and key == "escape":
            scene.main_menu.enabled = True
            self.about_menu.enabled = False


if __name__ == '__main__':
    app = Ursina()

    app.run()
