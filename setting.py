import my_json
import bug_trap
import os.path
from ursina import *

title = "Picnic in the Oblivion"
version = 0.5
version_type = "build #2504"

window_show_quit_button = False
game_show_fps = True
fullscreen = False

cursor = True
cursor_lock = True

developer_mode = False
show_raycast_debug = False

game_font = "assets/fonts/fix.ttf"
camera_move_speed = 15
camera_fov = 67


def inits():
    global developer_mode

    if os.path.isfile("assets/options.json"):
        opt = my_json.read("assets/options")
        if "dev" in opt:
            developer_mode = opt["dev"]
    else:
        if bug_trap.no_file_found("assets/options.json"):
            application.quit()

inits()
