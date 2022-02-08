from ursina import *
import game
import my_json
import bug_trap
from language_system import TKey
import ui

# Пресеты для цветов
color_orange = color.rgb(238, 157, 49)
color_red = color.rgb(232, 0, 0)
color_green = color.rgb(40, 190, 56)

color_sky_day = color.rgb(74, 116, 159)
color_sky_evening = color.rgb(57, 46, 61)
color_sky_night = color.rgb(10, 10, 10)
ui_folder = "assets/ui/"

class Marker(Sprite):
    def __init__(self,marker=None,marker_position=None,level_id=None,q_name=None, **kwargs):
        super().__init__(parent=camera.ui,z=-0.13)
        self.quest_name = q_name
        self.texture = marker
        self.level_id = level_id
        self.position = marker_position

        for key, value in kwargs.items ():
            setattr (self, key, value)

class PDA(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui,z=-0.13)
        self.root_window = None
        self.bg = Entity(parent=self,model="quad",scale=window.size,color=rgb(10,10,10))
        self.frame = Sprite (ui_folder + "16_9_frame.png", parent=self, scale=0.222)
        self.frame_1 = Sprite (ui_folder + "wnd_2_1.png", parent=self, scale=0.17)
        self.coordinator = False
        self.markers = []
        self.selector_id = 0



        self.map_container = Entity(parent=self,model="quad",color=color.rgba(255,255,255,0),y=0.0235)
        self.map_container.set_scissor(Vec3(-0.22,-0.26,-1),Vec3(0.22,0.26,1))
        Sprite(ui_folder + "i12.png", parent=self.map_container, scale=0.25)

        self.line_h = Entity(parent=self.map_container,model="quad",color=color_green,scale_y=0.002,scale_x=window.size.x)
        self.line_v = Entity(parent=self.map_container,model="quad",color=color_green,scale_y=window.size.y,scale_x=0.002)

        self.quest_name = ui.UIText(dedent("").strip(),offset=(0.0015,0.0015),color=color_orange,
                                    parent=self,position=(0,-.259,-.131),origin=(0,.5),scale=0.8)
        self.tip_bottom = Text (
            dedent (TKey("pause.pda.controls")).strip (),
            parent=self, y=-0.40, x=-0.7, origin=(-.5, 0), color=color.dark_gray, size=4)
        Text ("PDA".upper (), parent=self, y=0.38, origin=(0, 0))
        if self.coordinator:
            self.coordinator_data = ui.UIText("X: {0}, Y: {1}".format(round(self.line_v.x,2),round(self.line_h.y,2)),parent=self,
                                              origin=(-.5,.5),color=color_green,y=-0.3,x=-0.1)

        #Marker("assets/ui/pda/area_neutral.png",(0.1,0),"",parent=self.map_container,scale=0.015)

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def update_cursor(self):
        if self.markers:
            for m in self.markers:
                if game.get_current_level_id() == m.level_id:
                    self.line_v.x = m.x
                    self.line_h.y = m.y
                    self.quest_name.setText(dedent(m.quest_name).strip())
                    #self.quest_name.wordwrap = 3
                    break
                else:
                    self.line_v.x = -1
                    self.line_h.y = -1
                    self.quest_name.setText("")
                    break
    def update_cursor_position(self,selection):
        if self.markers:
            self.line_v.x = selection.x
            self.line_h.y = selection.y
            self.quest_name.setText(dedent(selection.quest_name).strip())

    def update_markers(self):
        if self.markers:
            for m in self.markers:
                destroy(m)
        self.markers.clear()
        for q in game.get_player().quests.quests_list:
            if q.pda is not None:
                m = Marker("assets/ui/pda/"+q.pda["spot"],q.pda["position"],q.pda["level_id"],q.title,
                           parent=self.map_container,scale=0.019)
                self.markers.append(m)

    def input(self,key):
        if self.enabled:
            if key == "escape":
                self.root_window.enable()
                self.disable()

            if self.coordinator:
                if key == "up arrow" or key == "up arrow hold":
                    self.line_h.y += 0.01
                    self.coordinator_data.setText("X: {0}, Y: {1}".format(round(self.line_v.x,2),round(self.line_h.y,2)))
                if key == "down arrow" or key == "down arrow hold":
                    self.line_h.y -= 0.01
                    self.coordinator_data.setText("X: {0}, Y: {1}".format(round(self.line_v.x,2),round(self.line_h.y,2)))
                if key == "left arrow" or key == "left arrow hold":
                    self.line_v.x -= 0.01
                    self.coordinator_data.setText("X: {0}, Y: {1}".format(round(self.line_v.x,2),round(self.line_h.y,2)))
                if key == "right arrow" or key == "right arrow hold":
                    self.line_v.x += 0.01
                    self.coordinator_data.setText("X: {0}, Y: {1}".format(round(self.line_v.x,2),round(self.line_h.y,2)))
            else:
                if self.markers:
                    if key == "up arrow" or key == "right arrow":
                        self.selector_id += 1
                        if self.selector_id >= len(self.markers)-1:
                            self.selector_id = len(self.markers)-1
                        self.update_cursor_position(self.markers[self.selector_id])
                    if key == "down arrow" or key == "left arrow":
                        self.selector_id -= 1
                        if self.selector_id < 0:
                            self.selector_id = 0
                        self.update_cursor_position(self.markers[self.selector_id])
                if key == "enter":
                    if self.markers:
                        if self.markers[self.selector_id].level_id != game.get_current_level_id():
                            game.get_player().steps_sound.play()
                            # зачерняем экран
                            camera.overlay.color = color.black
                            # создаём текст загрузки
                            loading = Text(TKey("loading"), origin=(0, 0),x=-.01, color=color_orange, always_on_top=True,
                                           parent=camera.ui)
                            loading_icon = Animation("assets/ui/rads",fps=12,origin=(.5,0),x=-.1,always_on_top=True,
                                                     parent=camera.ui,scale=0.03)
                            # удаляем текущий уровень
                            destroy(game.get_current_level())
                            # загружаем новый по айди из ключа "уровень"
                            game.set_current_level(self.markers[self.selector_id].level_id)
                            self.crosshair_tip_text = ""
                            # убрать чёрный экран
                            invoke(setattr, camera.overlay, 'color', color.clear, delay=3)
                            # удалить текст загрузки
                            destroy(loading, delay=3)
                            destroy(loading_icon,delay=3)
                            game.enable_pda_in_pause(False)
                            self.root_window.disable()
                            self.disable()
                            game.pause = False

if __name__ == "__main__":
    game = Ursina()

    game.run()
