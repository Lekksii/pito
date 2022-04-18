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

# WAYPOINT CREATOR
class WaypointWindow(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, z=-999)

        self.ignored_input_entity = None
        self.root = Entity(parent=self, model=Quad(radius=.03), color=color.rgba(10, 10, 10, 255), scale=(.4,.3),
               position=(0, 0))
        self.root.parent = self
        self.add_point = Button("Add",position=(0.25,-0.3),scale=(0.2,0.1),parent=self.root)
        self.add_point.on_click = self.apply_clicked
        self.cancel = Button("Cancel",position=(-0.25,-0.3), scale=(0.2,0.1),parent=self.root)
        self.cancel.on_click = self.cancel_click
        self.title = UIText("Create new Waypoint",position=(0,0.11),color=color_orange,parent=self)

        self.pos = UIText("XYZ: [{0}, {1}, {2}]".format(round(game.get_player().position[0],2),
                                                        round(game.get_player().position[1],2),
                                                        round(game.get_player().position[2],2)),
                                                        position=(0, 0.06), parent=self)
        self.pos = UIText("ROT: [{0}, {1}, {2}]".format(round(game.get_player().rotation[0], 2),
                                                        round(game.get_player().rotation[1], 2),
                                                        round(game.get_player().rotation[2], 2)),
                                                        position=(0, 0.03), parent=self)
        game.get_player().panel_opened = True

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def cancel_click(self):
        mouse.locked = True
        game.get_player().mouse_conrol = True
        game.get_player().panel_opened = False
        game.get_player().wp_wnd = None
        destroy(self)
        print("Cancel clicked!")

    def apply_clicked(self):
        data = "\"position\": [{0}, {1}, {2}],\n\"rotation\": [{3}, {4}, {5}],\n\"speed\": 2".format(
            round(game.get_player().position[0], 2),
            round(game.get_player().position[1], 2),
            round(game.get_player().position[2], 2),
            round(game.get_player().rotation[0], 2),
            round(game.get_player().rotation[1], 2),
            round(game.get_player().rotation[2], 2))
        result = "{\n"+data+"\n}"
        game.copy_to_clipboard(result)

        mouse.locked = True
        game.get_player().mouse_conrol = True
        game.get_player().panel_opened = False
        game.get_player().wp_wnd = None
        destroy(self)
        print("Add clicked!")

# MESSAGE BOX
class MessageBox(Entity):
    def __init__(self, title, message,type = "info", **kwargs):
        super().__init__(parent=camera.ui,z=-999)
        self.ignored_input_entity = None
        Entity(parent=self, model="quad", color=color.rgba(10,10,10,200), scale = (1*window.aspect_ratio,1),position=(0,0))
        Sprite (ui_folder+"message_box.png",parent=self,scale=0.25, position=(0, 0))
        self.title = UIText(title,shadow=True, parent=self,color=color_orange,origin=(-.5,0),position=(-.32,0.168))
        self.close = Button("OK",position=(0,-0.15),scale=(0.1,0.04),parent=self)
        self.close.on_click = self.close_window
        self.message = Text(parent=self, text=dedent(message).strip(),
             origin=(-.5, .5),wordwrap=33,position=(-.3,0.14)).set_scissor(Vec3(-1,-0.3,0), Vec3(1,1,0))
        self
        self.msg_box_type = type
        game.pause = True
        game.get_player().mouse_conrol = False
        mouse.locked = False

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def close_window(self):
        game.pause = False
        game.get_player().mouse_conrol = True
        mouse.locked = True

        if self.ignored_input_entity is not None:
            self.ignored_input_entity.ignore_input = False

        invoke(destroy, self, delay=0.0001)

    def input(self,key):
        if key == "enter" or key == "escape":
            self.close_window()

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