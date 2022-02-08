from ursina import *
import setting
import os.path
import my_json
import bug_trap
import glob
import ui

# ИНИЦИАЛИЗАЦИЯ
# объявлям папки с ассетами
tex_folder = "assets/textures/"
mesh_folder = "assets/models/"
ui_folder = "assets/ui/"
sound_folder = "assets/sounds/"

# Пресеты для цветов
color_orange = color.rgb (238, 157, 49)
color_red = color.rgb (232, 0, 0)
color_green = color.rgb (40, 190, 56)

color_sky_day = color.rgb (74, 116, 159)
color_sky_evening = color.rgb (57, 46, 61)
color_sky_night = color.rgb (10, 10, 10)

level_editor_session = None

can_control_camera = True
can_select_objects = True

can_add_object = False

def get_selected_entity():
    return level_editor_session.editor_camera.selected_entity

def set_camera_control(b):
    global can_control_camera
    can_control_camera = b

class LevelEditor(Entity):
    def __init__(self,lvl_loader, **kwargs):
        super().__init__()
        global level_editor_session

        self.loaded_level = None
        self.default_sky = color_sky_day
        level_editor_session = self
        self.editor_camera = LevelEditorCamera()

        if not lvl_loader:
            self.loaded_level = "new"
        else:
            self.loaded_level = lvl_loader

        self.editor_camera.position = (0,5,0)



        self.editor_scene = []
        self.editor_camera.editor_title.text = "LEVEL EDITOR -> assets/levels/" + self.loaded_level

        for key, value in kwargs.items ():
            setattr (self, key, value)

        # ЗАГРУЗКА УРОВНЯ ЕСЛИ ИМЯ УРОВНЯ НЕ NEW
        if self.loaded_level != "new":
            if os.path.isdir ("assets/levels/" + self.loaded_level):


                level_data = my_json.read ("assets/levels/" + self.loaded_level + "/level")

                # Настраиваем цвет неба
                window.color = color.rgb (level_data["weather_color"][0], level_data["weather_color"][1],
                                          level_data["weather_color"][2])


                # Создаём объекты из папки с уровнем
                # Если просто имеем базовый объект - спауним
                for obj in level_data["level_data"]:

                    if "light" in level_data:
                        for light in level_data["light"]:
                            if light["type"] == "point":
                                l_obj = EditorObject(model="cube",
                                    color=color.rgba(light["color"][0], light["color"][1],
                                                                 light["color"][2], .1),
                                               position=light["position"],
                                               rotation=light["rotation"],
                                               parent=self)
                                l_obj.gizmo_name.text = "[Point Light]"
                                self.editor_scene.append(l_obj)
                                break

                    if "id" in obj:
                        if obj["id"] == "animation":
                            anim = Animation(tex_folder + obj["sequence"], position=obj["position"], rotation=obj["rotation"],
                                      scale=obj["scale"])
                            self.editor_scene.append(anim)
                    else:

                        obj3d = EditorObject(model=obj["model"],
                                        texture=obj["texture"] if "texture" in obj else None,
                                        rotation=obj["rotation"] if "rotation" in obj else (0,0,0),
                                        position=obj["position"] if "position" in obj else (0,0,0),
                                        filtering=None,
                                        collider="mesh",
                                        scale=obj["scale"] if "scale" in obj else 1,
                                        color=color.rgba(obj["color"][0],obj["color"][1],obj["color"][2],obj["color"][3]) if "color" in obj else color.white,
                                        double_sided=obj["double_sided"] if "double_sided" in obj else False)
                        obj3d.keys = obj


                        obj3d.gizmo_name.text = "[" + obj3d.keys["le_name"] + "]" if "le_name" in obj3d.keys else "[game_object]"

                        obj3d.ingame_collider = obj["collider"] if "collider" in obj else None

                        self.editor_scene.append(obj3d)
        else:
            window.color = self.default_sky

class LevelEditorCamera(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.object_viewer = None
        self.properties_viewer = ObjectProperties()
        self.properties_viewer.root.disable()

        self.selected_entity = None

        self.speed = setting.camera_move_speed
        self.camera_pivot = Entity (parent=self, y=0)
        self.crosshair_tip_text = ""
        #self.cursor = Sprite (ui_folder + "crosshair.png", parent=camera.ui, scale=(0.12, 0.12))
        self.crosshair_tip = Text (parent=camera.ui,text=self.crosshair_tip_text, origin=(0, -.5), y=-0.04,
                                   color=color_orange, scale=.8)
        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        camera.fov = setting.camera_fov
        camera.clip_plane_near = 0.01
        mouse.locked = False
        mouse.position = (0,0,0)
        self.hit_text = "None"
        self.raycast_point_pos_text = ""
        self.hit_pos_info = Text ("", y=0.1, origin=(0, 0))
        self.mouse_sensitivity = Vec2 (35, 35)
        self.ray_hit = raycast (self.position + (self.down * 0.04), direction=(0, -1, 0), ignore=(self,), distance=50,
                                debug=False)
        # Окно инструментов
        self.tools_bar = Entity(parent=camera.ui,model="quad",color=color.rgba(10,10,10,255),origin=(-.5, .5),
                                position=(window.top_left.x, window.top_left.y),scale=(window.size.x,0.05))


        # Рисуем окно с выводом дебаг информации
        self.debug_text = Text(parent=camera.ui, text="null", color=color_orange, origin=(-.5, .5),
                                position=(window.top_left.x + 0.03, window.top_left.y - 0.08))
        Text (parent=camera.ui, text="Q - Up\nE - Down\n\nRMB(Hold) - Rotate camera\n\nW A S D - Move\nESC - Quit",
            color=color_orange, origin=(-.5, -.5), position=(window.bottom_left.x+.03, window.bottom_left.y+.03),
            background=True)

        # Title of Editor
        self.editor_title = Text(parent=camera.ui, text="LEVEL EDITOR -> assets/levels/",
                                 origin=(-.5,.5),position=(window.top_left.x+.01,
                                 window.top_left.y-.01))

        self.fps_counter = ui.UIText ("fps", (0.0015, 0.0015), color=color_orange,
                                      position=(window.right.x - 0.13, window.right.y + .35))

        # Debug info
        self.debug_text.text = "POS X: " + str (round (self.x, 2)) + \
                               "\nPOS Y: " + str (round (self.y, 2)) + \
                               "\nPOS Z: " + str (round (self.z, 2)) + \
                               "\n\nROT X: " + str (round (self.camera_pivot.rotation.x, 2)) + \
                               "\nROT Y: " + str (round (self.rotation.y, 2)) + \
                               "\nROT Z: " + str (round (self.camera_pivot.rotation.z, 2)) + \
                               "\n\nVEL X: " + str (round (mouse.velocity[0], 2)) + \
                               "\nVEL Y: " + str (round (mouse.velocity[1], 2)) + \
                               "\n\nHIT: " + str (self.hit_text)

        def action_add_btn():
            set_camera_control(False)
            if self.object_viewer is None:
                self.object_viewer = ObjectViewer()
            else:
                self.object_viewer.root.enable()

        # Toolbar
        self.add_btn = Button("Object [+]", parent=camera.ui, color=rgb(40,40,40), scale=(.18,.04), origin=(-.5, 0),
                               position=(.428, .475), on_click=action_add_btn)
        self.del_btn = Button ("Object [-]", parent=camera.ui, color=rgb (40, 40, 40), scale=(.18, .04),
                               origin=(-.5, 0),
                               position=(.614, .475))


        for key, value in kwargs.items ():
            setattr (self, key, value)

        if self.debug_text is not None:
            self.debug_text.background = True

    def update_debug_info(self):
        self.debug_text.text = "POS X: " + str (round (self.x, 2)) + \
                               "\nPOS Y: " + str (round (self.y, 2)) + \
                               "\nPOS Z: " + str (round (self.z, 2)) + \
                               "\n\nROT X: " + str (round (self.camera_pivot.rotation.x, 2)) + \
                               "\nROT Y: " + str (round (self.rotation.y, 2)) + \
                               "\nROT Z: " + str (round (self.camera_pivot.rotation.z, 2)) + \
                               "\n\nVEL X: " + str (round (mouse.velocity[0], 2)) + \
                               "\nVEL Y: " + str (round (mouse.velocity[1], 2)) + \
                               "\n\nHIT: " + str (self.hit_text)

    def input(self, key):
        global can_add_object

        entity_exclude = [
            "button", "le_input_field"
        ]
        # Если нажали ESCAPE то закрыть приложение
        if key == "escape": application.quit()
        # Если игровой процесс запущен (Геймплей)

        if can_control_camera:
            if key == "l":
                for obj in level_editor_session.editor_scene:
                    print(obj)

            if key == "left mouse down":
                if can_add_object:
                    if mouse.world_point:
                        EditorObject (model="cube",
                                      position=mouse.world_point,color=color.rgba(10,10,10,128),
                                      filtering=None, collider="box",
                                      scale=1)
                        can_add_object = False

                if mouse.hovered_entity is not None:
                    if can_select_objects and not mouse.hovered_entity.name in entity_exclude:
                        self.selected_entity = mouse.hovered_entity
                        #self.hit_text = self.selected_entity.name
                        self.properties_viewer.prop_name_text.text = "NAME: "+self.selected_entity.name
                        self.properties_viewer.position_title.text = "POSITION: \nX: " + \
                        str(round(self.selected_entity.x,2))+"\nY: "+str(round(self.selected_entity.y,2))+"\nZ: "+ \
                        str(round(self.selected_entity.z,2))
                        if hasattr(self.selected_entity, "keys"):
                            if "id" in self.selected_entity.keys:
                                self.properties_viewer.prop_id_field.text = self.selected_entity.keys["id"]
                                self.properties_viewer.keys_list = self.selected_entity.keys
                            else:
                                self.properties_viewer.prop_id_field.text = "None"
                                self.properties_viewer.keys_list.clear()
                        self.properties_viewer.show_props()
                else:
                    self.hit_text = "None"
                    self.properties_viewer.close_prop()

            if key == "right mouse down":
                mouse.enabled = False
                mouse.locked = True
                mouse.enabled = True
            if key == "right mouse up":
                mouse.enabled = False
                mouse.locked = False
                mouse.enabled = True

    def update(self):
        self.fps_counter.setText("FPS: {0}".format(window.fps_counter.text))
        if can_control_camera:
            origin = self.position + (self.down * 0.04)

            self.direction = Vec3 (camera.forward)

            if mouse.velocity > 0 or mouse.velocity < 0:
                self.ray_hit = raycast (origin, self.direction, ignore=(self,), distance=50,
                                        debug=setting.show_raycast_debug)
                self.update_debug_info()

            if held_keys["w"]:
                self.position += self.direction * self.speed * time.dt
                self.update_debug_info ()

            if held_keys["s"]:
                self.position -= self.direction * self.speed * time.dt
                self.update_debug_info ()

            if held_keys["a"]:
                self.position += self.left * self.speed * time.dt
                self.update_debug_info ()

            if held_keys["d"]:
                self.position += self.right * self.speed * time.dt
                self.update_debug_info ()

                # Управление летающей камерой
            if held_keys["q"]:
                self.y -= setting.camera_move_speed * time.dt
                self.update_debug_info ()

            if held_keys["e"]:
                self.y += setting.camera_move_speed * time.dt
                self.update_debug_info ()

                # обновлять информацию в дебаг окне


            self.debug_text.background = True

            if mouse.right:

                # Поворот камеры с помощью мышки
                self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
                # self.rotation_y = clamp(self.rotation_y, -90, 90)
                self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
                self.camera_pivot.rotation_x = clamp (self.camera_pivot.rotation_x, -30, 30)

            self.crosshair_tip.text = self.crosshair_tip_text

class EditorObject(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.keys = {}

        self.gizmo_name = Text ("[" + self.keys["le_name"] if "le_name" in self.keys else self.name + "]", parent=camera,
                         origin=(0, 0), ignore=True, background=True, always_on_top=True,billboard=True)
        self.ingame_collider = None

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def update(self):
        self.gizmo_name.world_position = self.world_position

        self.gizmo_name.world_rotation.x = level_editor_session.editor_camera.camera_pivot.rotation_x
        self.gizmo_name.world_rotation.y = level_editor_session.editor_camera.rotation_y

        self.gizmo_name.scale = distance(self.position,level_editor_session.editor_camera.position)*4.5/10

class ObjectViewer(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.objects_list = {}
        self.selector = 0
        registered_objects = my_json.read("assets/models/le_models")

        def getList(dict):
            return [*dict]

        for obj in registered_objects:
            if os.path.isfile("assets/models/"+obj+".obj"):
                self.objects_list[obj] = registered_objects[obj]["texture"]
            else:
                if bug_trap.crash_game_msg("Level Editor","[assets/models/{0}.obj] model is not found!".format(obj),1):
                    application.quit()

        self.root = Entity(parent=camera.ui, model="quad", color=color.rgb(10,10,10), scale=(.8,.5),always_on_top=True)
        self.root_title = Text(parent=self.root,text="LEVEL EDITOR -> OBJECT VIEWER", scale=(1.2,1.5),
                               position=(-.04,.46), origin=(.5,0))
        Text (parent=self.root, text="_"*66, scale=(1.2, 1.5),
              position=(-.496, .44), origin=(-.5, 0))

        def action():
            set_camera_control(True)
            self.root.disable()

        def step_prev():
            if self.selector < 0:
                self.selector = len (self.objects_list) - 1
            self.selector -= 1
            self.prev_3d.model = "assets/models/"+getList(self.objects_list)[self.selector]
            self.prev_3d.texture = "assets/" + self.objects_list[getList (self.objects_list)[self.selector]]

        def step_next():
            if self.selector > len (self.objects_list)-2:
                self.selector = 0
            self.selector += 1
            self.prev_3d.model = "assets/models/"+getList(self.objects_list)[self.selector]
            self.prev_3d.texture = "assets/"+self.objects_list[getList(self.objects_list)[self.selector]]

        Button("X",parent=self.root, color=color_red, scale=.07,origin=(-.5,0),position=(.428,.463),
               on_click=action)
        Button("Take",parent=self.root, scale=0.1,position=(0,-.4))

        Button ("Previous", parent=self.root, scale=0.12, position=(-.35, 0), on_click=step_prev)
        Button ("Next", parent=self.root, scale=0.12, position=(.35, 0), on_click=step_next)
        if self.objects_list:
            self.prev_3d = Entity(parent=self.root,model=mesh_folder+getList(self.objects_list)[0],color=rgb(255,255,255),
                              origin=(0,0), scale=self.world_scale/8,
                              texture="assets/"+self.objects_list[getList(self.objects_list)[0]],
                              double_sided=False, rotation=(-45,0,15),position=(0,0,-2))

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def update(self):
        if held_keys["left arrow"]:
            self.prev_3d.rotation.y -= 0.1 * time.dt

        if held_keys["right arrow"]:
            self.prev_3d.rotation.y += 0.1 * time.dt


class ObjectProperties(Entity):
    def __init__(self, **kwargs):
        super().__init__(z=-0.01)

        self.keys_list = {}
        self.keys_panel = None


        def on_edit_key_btn(key_id,key_value):

            def apply_key(new_value):
                get_selected_entity().keys[key_id] = new_value
                for obj in self.keys_panel.content:
                    if obj.text == key_id:
                        obj.text = "[\"{0}\"] = {1}".format(key_id,new_value)
                edit_key_window.disable()

            edit_key_window = WindowPanel (title="[\"{0}\"] KEY EDITOR".format (key_id), content=(
                Space (0.6),
                LEInputField (text=key_value),
                Button ("Apply", on_click=Func(apply_key,edit_key_window.content[1].text))
            ))

        def on_keys_hide_btn():
            self.keys_list_btn.enable()
            self.keys_panel.disable()

        def on_keys_show_btn():
            keys = []
            keys.append(Space(.5))
            for k, v in self.keys_list.items():
                keys.append(Button("[\"{0}\"] = {1}".format (k, v),on_click=Func(on_edit_key_btn,k,v)))
            self.keys_list_btn.disable()
            keys.append(Button("Close", on_click=on_keys_hide_btn, color=color_red))
            self.keys_panel = WindowPanel(title="Keys",content=keys,position=(0,.3))

        self.root = Entity(parent=camera.ui)
        self.root_widget = Entity (parent=self.root, model="quad", color=color.rgb (10, 10, 10), scale=(.5, .8),
                position=(window.right.x - .258, .045))

        self.root_title = Text (parent=self.root, text="OBJECT PROPERTIES",
                                position=(.31, .42), origin=(-.5, 0))
        Text(parent=self.root, text="_" * 40,position=(window.right.x -.508, .41), origin=(-.5, 0),color=rgb(80,80,80))

        self.prop_name_text = Text(parent=self.root, text="NAME: [None]",
              position=(.31, .37), origin=(-.5, 0), color = color_orange)

        self.prop_id = Text(parent=self.root,text="ID:",
              position=(.31, .31), origin=(-.5, 0), color = color_orange)
        self.prop_id_field = LEInputField(parent=self.prop_id,position=(.25, .0))

        self.keys_list_text = Text (parent=self.root, text="KEYS:",
                             position=(.31, .25), origin=(-.5, 0), color=color_orange)

        self.keys_list_btn = Button ("Show list", parent=self.root, color=rgb (40, 40, 40), scale=(.18, .04),
                                 origin=(0, 0),
                                 position=(window.right.x - .32, .25), on_click=on_keys_show_btn)

        self.position_title = Text (parent=self.root, text="POSITION:",
                                    position=(.31, .15), origin=(-.5, 0), color=color_orange)

        self.apply_btn = Button ("Apply", parent=self.root, color=rgb (40, 40, 40), scale=(.18, .04),
                               origin=(0, 0),
                               position=(window.right.x - .255, -.31), on_click=self.close_prop)


        for key, value in kwargs.items ():
            setattr (self, key, value)

    def close_prop(self):
        self.root.disable ()

    def show_props(self, **kwargs):
        self.root.enable()
        self.update_values()

    def update_values(self):
        self.prop_name_text.text = self.prop_name_text.text
        self.prop_id_field.text = self.prop_id_field.text




class LEInputField(Button):
    def __init__(self, **kwargs):
        super().__init__()
        self.mouse_inside = False
        self.selected = False
        self.max_char = 30
        self.char_size = 1.3
        self.origin = (0,.0)
        self.always_on_top = True
        self.text_origin = (-.5, 0)
        self.input_background = Entity (model="quad", parent=self, color=color.rgba (40, 40, 40), origin=self.text_origin)
        self.text = "None"

        self.text_entity.position = (.004,0)
        self.scale = ((self.scale_x * self.char_size/100)*self.max_char,self.scale.y / 25)
        self.color = color.clear

        self.shifted_keys = {
            '-': '_',
            '.': ':',
            ',': ';',
            '\'': '*',
            '<': '>',
            '+': '?',
            '0': '=',
            '1': '!',
            '2': '"',
            '3': '#',
            # '4' : '¤',
            '5': '%',
            '6': '&',
            '7': '/',
            '8': '(',
            '9': ')',
        }
        self.alted_keys = {
            '\'': '´',
            '0': '}',
            '2': '@',
            '3': '£',
            '4': '¤',
            '5': '€',
            '7': '{',
            '8': '[',
            '9': ']',
        }
        self.shortcuts = {
            'newline': ('enter', 'enter hold'),
            'erase': ('backspace', 'backspace hold'),
            'erase_word': ('ctrl+backspace', 'ctrl+backspace hold'),
            'delete_line': ('ctrl+shift+k',),
            'undo': ('ctrl+z', 'ctrl+z hold'),
            'redo': ('ctrl+y', 'ctrl+y hold', 'ctrl+shift+z', 'ctrl+shift+z hold'),
            # 'save':             ('ctrl+s',),
            # 'save_as':          ('ctrl+shift+s',),
            'indent': ('tab',),
            'dedent': ('shift+tab',),
            'move_line_down': ('ctrl+down arrow', 'ctrl+down arrow hold'),
            'move_line_up': ('ctrl+up arrow', 'ctrl+up arrow hold'),
            # 'cut':              ('ctrl+x',),
            'copy': ('ctrl+c',),
            'paste': ('ctrl+v',),
            # 'select_all':       ('ctrl+a',),
            # 'toggle_comment':   ('ctrl+alt+c',),
            # 'find':             ('ctrl+f',),

            'move_left': ('left arrow', 'left arrow hold'),
            'move_right': ('right arrow', 'right arrow hold'),
            'move_up': ('up arrow', 'up arrow hold'),
            'move_down': ('down arrow', 'down arrow hold'),
            'move_to_end_of_word': ('ctrl+right arrow', 'ctrl+right arrow hold'),
            'move_to_start_of_word': ('ctrl+left arrow', 'ctrl+left arrow hold'),

            'select_word_left': ('ctrl+shift+left arrow', 'ctrl+shift+left arrow hold'),
            'select_word': ('double click'),
        }

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def input(self,key):

        if key == "left mouse down":
            print ("mouse press")
            if self.mouse_inside:
                self.selected = True
            else:
                self.selected = False

        if self.selected and len(self.text) < self.max_char:
            if key == 'space':
                key = ' '

            ctrl, shift, alt = '', '', ''
            if held_keys['control'] and key != 'control':
                ctrl = 'ctrl+'
            if held_keys['shift'] and key != 'shift':
                shift = 'shift+'
            if held_keys['alt'] and key != 'alt':
                alt = 'alt+'

            key = ctrl + shift + alt + key

            k = key.replace (' hold', '')
            k = k.replace ('shift+', '')

            if len (k) == 1 and not held_keys['control']:

                if held_keys['shift']:
                    k = k.upper ()
                    if k in self.shifted_keys:
                        k = self.shifted_keys[k]
                    if k in self.alted_keys:
                        k = self.alted_keys[k]

                self.text += k

            if k == '(':
                self.text += (')')

            if k == '[':
                self.text += (']')
            if k == '{':
                self.text += ('}')

            if key in ('space', 'space hold'):
                self.text += (' ')

            if len (self.text) > 0 and held_keys["backspace"]:
                self.text = self.text[:len (self.text) - 1]


    def on_mouse_enter(self):
        self.input_background.color = color.rgba(40,40,40,50)
        self.mouse_inside = True

    def on_mouse_exit(self):
        self.input_background.color = color.rgba (40, 40, 40, 255)
        self.mouse_inside = False

    def update(self):
        self.text = self.text


if __name__ == "__main__":
    app = Ursina()

    app.run()