from ursina import *
import game
from language_system import TKey

# объявлям папки с ассетами и доп файлы
tex_folder = "assets/textures/"
mesh_folder = "assets/models/"
ui_folder = "assets/ui/"


# Пресеты для цветов
color_orange = color.rgb (238, 157, 49)
color_red = color.rgb (232, 0, 0)
color_green = color.rgb (40, 190, 56)

class SkillsWindow(Entity):
    def __init__(self, **kwargs):
        super().__init__(z=-0.112)
        self.root_window = None
        self.parent = camera.ui
        self.skills_root = Entity(parent=self, model="quad", color=rgb(2, 2, 0), scale=window.size)
        self.frame = Sprite(ui_folder + "16_9_frame.png", parent=self, scale=0.222)
        Text(TKey("pause.skills").upper(), parent=self, y=0.4, origin=(0, 0))

        for key, value in kwargs.items ():
            setattr(self, key, value)

    def input(self,key):
        if self.enabled:
            if key == "escape" and self.root_window is not None:
                self.root_window.enable()
                self.disable()