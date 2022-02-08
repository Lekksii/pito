from ursina import *
import setting
import main_menu
from tkinter import Tk
from game import Player
from game import Gameplay
from game import Level
from level_editor import LevelEditor
from language_system import language
import my_json
import os.path
import bug_trap
import glob

root = Tk()

options = None


# Проверка файлов на существование, если их нет - крашим игру!
def check_files(fname):
    if not os.path.isfile(fname + ".json"):
        if bug_trap.no_file_found(fname + ".json"):
            application.quit()


# Список проверяемых файлов
def check_assets_folder():
    check_files("assets/gameplay/items")
    check_files("assets/gameplay/quests")
    check_files("assets/creatures/player")


if __name__ == "__main__":

    if os.path.isdir("assets") is None:
        if bug_trap.crash_game_msg("No game data found!", "What, where is \"assets\" folder?", 1):
            application.quit()

    if os.path.isfile("assets/options.json"):
        options = my_json.read("assets/options")
    else:
        if bug_trap.no_file_found("assets/options.json"):
            application.quit()

    check_assets_folder()

    window.borderless = True
    window.cog_button = False
    window.vsync = True
    window.forced_aspect_ratio = options["aspect"][0]/options["aspect"][1]
    #print(window.aspect_ratio)
    #window.fullscreen_size = (options["window_size"][0], options["window_size"][1])
    #window.size = (options["window_size"][0], options["window_size"][1])
    #window.fixed_size = window.size

    app = Ursina()

    if options["autodetect"]:
        window.fullscreen = True
    else:
        window.fullscreen = False

    window.cog_button = False

    # НАСТРОЙКА ПЕРЕМЕННЫХ, ПРИЛОЖЕНИЯ, ДВИЖКА
    scene = None
    window.icon = "Icon.ico"
    window.title = setting.title
    window.fps_counter.enabled = True
    window.fps_counter.position = (100, 100)
    window.exit_button.visible = setting.window_show_quit_button



    window.color = color.black
    mouse.enabled = setting.cursor
    mouse.locked = setting.cursor_lock
    Text.default_font = setting.game_font

    text.default_resolution = 720 * Text.size
    Texture.default_filtering = False
    application.development_mode = False

    # НАЧИНАЕМ ИГРУ С ГЛАВНОГО МЕНЮ
    scene = main_menu.MainMenu()

    #scene = Gameplay()

    #scene = LevelEditor("ai_test")

    app.run()
