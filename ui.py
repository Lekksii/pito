from ursina import *
from language_system import TKey
import game
import main_menu
ui_folder = "assets/ui/"

# Пресеты для цветов
color_orange = color.rgb(238, 157, 49)
color_red = color.rgb(232, 0, 0)
color_green = color.rgb(40, 190, 56)

color_sky_day = color.rgb(74, 116, 159)
color_sky_evening = color.rgb(57, 46, 61)
color_sky_night = color.rgb(10, 10, 10)

class UILinePanel(Entity):
    def __init__(self, width=1, **kwargs):
        super().__init__()
        self.width = width
        self.closed = True
        self.parent = camera.ui
        count = 0
        left = Sprite (ui_folder + "bottom_line_left.png",parent=self,scale = self.scale)
        while count < self.width:
            center = Sprite (ui_folder + "bottom_line_center.png",parent=self, scale = self.scale,x=left.x+0.3)
            center.x = center.x + 0.3
            count += 1
        if self.closed:
            Sprite (ui_folder + "bottom_line_right.png", parent=self, scale=self.scale,x=center.x+0.2)

        for key, value in kwargs.items ():
            setattr (self, key, value)

class UIText(Text):
    def hideHUD(self):
        return color.rgba(1,1,1,0) if not game.show_hud else color.rgba(1,1,1,1)

    def __init__(self,text="",origin=(0,0),offset=(0.001,0.001),color=color.white,**kwargs):
        super().__init__(parent=camera.ui, origin=origin)
        self.shadow = True

        if self.shadow:
            self.shadow_text = Text(text,parent=self,origin=self.origin,x=self.x+offset[0],
                                y=self.y-offset[1],color=rgb(10,10,10) if game.show_hud else self.hideHUD(),z=self.z+0.001)
        self.origin_text = Text (text, parent=self, origin=self.origin,color = color,x=self.x,
                                y=self.y,z=self.z)

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def setText(self,text):
        if self.shadow:
            self.shadow_text.text = text
        self.origin_text.text = text

# MESSAGE BOX
class MessageBox(Entity):
    def __init__(self, title, message,type = "info", **kwargs):
        super().__init__(parent=camera.ui,z=-999)
        self.ignored_input_entity = None
        Entity(parent=self, model="quad", color=color.rgba(10,10,10,200), scale = (1*window.aspect_ratio,1),position=(0,0))
        Sprite (ui_folder+"message_box.png",parent=self,scale=0.25, position=(0, 0))
        self.title = UIText(title, parent=self,color=color_orange,origin=(.5,0),position = (-.31,0.178))
        self.message = Text(parent=self, text=dedent(message).strip(),
             origin=(-.5, .5),wordwrap=35,position=(-.3,0.14)).set_scissor(Vec3(-1,-0.3,0), Vec3(1,1,0))
        self
        self.msg_box_type = type

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def input(self,key):
        if key == "enter":
            invoke (destroy, self, delay=0.0001)
            if self.ignored_input_entity is not None:
                self.ignored_input_entity.ignore_input = False

                #if self.msg_box_type == "restart_game":
                #    invoke(application.quit,delay=2)

class GameOverScreen(Entity):
    def __init__(self,**kwargs):
        super().__init__(parent=camera.ui,z=-999,ignore_paused=True)
        Entity(parent=self, model="quad", color=color.rgba(10, 10, 10, 255), scale=window.size,
               position=(0, 0))
        Text(TKey("gameover"),parent=self,origin=(0,0))

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def input(self,key):
        if game.isdead and self.enabled:
            if key == "escape" or key == "enter":
                scene.clear()
                camera.overlay.color = color.black
                loading = Text(TKey("loading"), origin=(0, 0), color=color_orange, always_on_top=True)
                invoke(main_menu.MainMenu, delay=0.0001)
                destroy(loading, delay=1)
                invoke(setattr, camera.overlay, 'color', color.clear, delay=1)
                application.paused = False

if __name__ == "__main__":
    app = Ursina()

    app.run()