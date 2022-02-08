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

class JournalWindow(Entity):
    def journal_update(self):
        self.quests.clear()
        for q in game.get_player().quests.quests_list:
            self.quests.append(Text(q.title,color=color_orange))

        if self.quests:
            offset = 0.2
            spacing = .01
            height = 0.01 - spacing

            if isinstance (self.quests, dict):
                self.quests = self.quests.values ()

            for p in self.quests:
                if isinstance (p, Text):
                    p.x -= 0
                    p.y = offset
                    p.parent = self
                    p.origin = (0, 0)
                    height += len (p.lines) / 100 * 5
                    p.y -= height

            self.selector.position = (self.quests[0].x-0.01*self.quests[0].width,self.quests[0].y)

    def __init__(self, **kwargs):
        super().__init__(z=-0.112)
        self.root_window = None
        self.quests = []
        self.selector_id = 0
        self.quest_info = JournalWindowQuestDescription(enabled=False,root_window=self)
        self.click_sound = Audio ("assets/sounds/click", autoplay=False, loop=False)

        self.parent = camera.ui
        self.journal = Entity (parent=self, model="quad", color=rgb (10, 10, 10), scale=window.size)

        self.frame = Sprite (ui_folder + "16_9_frame.png", parent=self, scale=0.222)
        Text (TKey("pause.journal.title").upper (), parent=self, y=0.4, origin=(0, 0))
        self.selector = Sprite (ui_folder + "rad_icn.png", parent=self, y=2, x=2,
                                scale=.21, origin=(-.5, 0),color = color.clear)
        self.tip_bottom = Text (
            dedent (TKey("pause.journal.control.tip")).strip (),
            parent=self, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)

        for key, value in kwargs.items ():
            setattr(self, key, value)

    def input(self,key):
        if self.enabled:
            if key == "escape" and self.root_window is not None:
                self.root_window.enable()
                self.disable()

            if self.quests:
                if key == "down arrow" or key == "s":
                    #self.click_sound.play()
                    self.selector_id += 1
                    if self.selector_id > len (self.quests) - 1:
                        self.selector_id = 0
                    self.selector.position = (-self.quests[self.selector_id].width,self.quests[self.selector_id].y)

                if key == "up arrow" or key == "w":
                    #self.click_sound.play()
                    self.selector_id -= 1
                    if self.selector_id < 0:
                        self.selector_id = len (self.quests) - 1
                    self.selector.position = (-self.quests[self.selector_id].width,self.quests[self.selector_id].y)

                if key == "enter":
                    pass
                    # self.click_sound.play()
                    # self.disable ()
                    # self.quest_info.title = game.get_player ().quests.quests_list[self.selector_id].title
                    # self.quest_info.descr = game.get_player ().quests.quests_list[self.selector_id].description
                    # self.quest_info.update_text()
                    # self.quest_info.enable()

class JournalWindowQuestDescription(Entity):
    def __init__(self, **kwargs):
        super ().__init__ (z=-0.12)
        self.root_window = None
        self.title = ""
        self.descr = ""
        self.parent = camera.ui
        Entity (parent=self, model="quad", color=rgb (10, 10, 10), scale=window.size)

        self.frame = Sprite (ui_folder + "16_9_frame.png", parent=self, scale=0.222)
        self.title_text = Text (self.title.upper (), parent=self, y=0.4, origin=(0, 0), color=color_orange)
        self.descr_text = Text (text=dedent(self.descr).strip(), parent=self, y=0.0, origin=(0, 0),wordwrap=80)
        self.tip_bottom = Text (
            dedent (TKey("pause.journal.quest.control.tip")).strip (),
            parent=self, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)

        for key, value in kwargs.items ():
            setattr(self, key, value)

    def input(self,key):
        if self.enabled:
            if key == "escape":
                self.disable()
                self.root_window.enable ()

    def update_text(self):
        self.title_text.text = self.title
        self.descr_text.text = self.descr

if __name__ == "__main__":
    game = Ursina()

    game.run()
