from ursina import *
import bug_trap
import my_json
import os.path
from language_system import TKey
import game

ui_folder = "assets/ui/"

# Пресеты для цветов
color_orange = color.rgb (238, 157, 49)
color_red = color.rgb (232, 0, 0)
color_green = color.rgb (40, 190, 56)

color_sky_day = color.rgb (74, 116, 159)
color_sky_evening = color.rgb (57, 46, 61)
color_sky_night = color.rgb (10, 10, 10)

class Dialogue(Entity):
    def answers_update(self):
        if self.answers:
            offset = -0.15
            spacing = 7
            height = 0.03

            if isinstance (self.answers, dict):
                self.answers = self.answers.values ()

            for p in self.answers:
                if isinstance (p, Text):
                    p.x -= .7
                    p.y = offset
                    p.parent = self
                    p.origin = (-.5, 0)
                    height += len (p.lines) / 100 * spacing
                    p.y -= height
                    p.wordwrap = 90
                    p.color = color.dark_gray

            self.selector_id = 0
            self.selector.position = (self.answers[0].x-0.04,self.answers[0].y)
            self.answers[0].color = color_orange

    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui,z=-0.1)
        self.answers=[]
        self.selector_id = 0
        self.dialogue_file = ""
        self.click_sound = Audio ("assets/sounds/click", autoplay=False, loop=False)

        Entity(parent=self,model="quad",color=rgb(10,10,10),scale=window.size)
        self.frame = Sprite (ui_folder + "16_9_frame.png", parent=self, scale=0.222)
        self.npc_name = Text("NPC".upper(),parent=self,y=0.4,x=-0.7,color=color_orange)
        Entity (parent=self, y=0.37, x=0, model="quad", scale_y=0.002, color=color.dark_gray, scale_x=window.size.x)
        self.npc_dialogue = Text("...",parent=self,
            y=0.3,x=-0.7,color=color.white)
        Text (TKey("dialogue.player.answers").upper (), parent=self, y=-0.17, x=0.61, color=color_orange)

        Entity (parent=self, y=-0.2, x=0, model="quad", scale_y=0.002, color=color.dark_gray, scale_x=window.size.x)
        self.selector = Sprite (ui_folder + "rad_icn.png", parent=self, y=2, x=2,
                                scale=.21, origin=(-.5, 0))

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def change_dialogue(self,id):
        if self.enabled:
            if os.path.isfile ("assets/dialogues/" + self.dialogue_file + ".json"):
                d = my_json.read ("assets/dialogues/" + self.dialogue_file)
                for old_answer in self.answers:
                    destroy(old_answer)

                self.answers.clear()
                self.npc_dialogue.text = dedent(TKey(d["dialogues"][id]["text"])).strip()
                self.npc_dialogue.wordwrap = 85
                for answer in d["dialogues"][id]["answers"]:
                    self.answers.append (Answer (dedent(TKey(answer["text"])).strip(),keys=answer))
                self.answers_update ()
            else:
                if bug_trap.crash_game_msg ("Error", "Dialogue file [asstes/dialogues/{0}.json] not found!".format (self.dialogue_file),
                                        1):
                    application.quit ()

    def start_dialogue(self,id):
        if os.path.isfile("assets/dialogues/"+id+".json"):
            d = my_json.read("assets/dialogues/"+id)
            self.enable()
            for old_answer in self.answers:
                destroy (old_answer)

            self.answers.clear()

            self.npc_dialogue.text = dedent(TKey(d["dialogues"][d["start_dialogue"]]["text"])).strip()
            self.npc_dialogue.wordwrap = 90
            for answer in d["dialogues"][d["start_dialogue"]]["answers"]:
                self.answers.append(Answer(dedent(TKey(answer["text"])).strip(),keys=answer))
            self.answers_update()
        else:
            if bug_trap.crash_game_msg("Error","Dialogue file [asstes/dialogues/{0}.json] not found!".format(id),1):
                application.quit()

    def input(self,key):
        if self.enabled:
            if self.answers:
                if key == "down arrow" or key == "s":
                    self.click_sound.play()
                    self.selector_id += 1
                    if self.selector_id > len (self.answers) - 1:
                        self.answers[len (self.answers) - 1].color = color.dark_gray
                        self.selector_id = 0
                    else:
                        self.answers[self.selector_id - 1].color = color.dark_gray
                    self.selector.y = self.answers[self.selector_id].y
                    self.answers[self.selector_id].color = color_orange

                if key == "up arrow" or key == "w":
                    self.click_sound.play ()
                    self.selector_id -= 1
                    if self.selector_id < 0:
                        self.selector_id = len (self.answers) - 1
                        self.answers[0].color = color.dark_gray
                    else:
                        self.answers[self.selector_id + 1].color = color.dark_gray
                    self.selector.y = self.answers[self.selector_id].y
                    self.answers[self.selector_id].color = color_orange

                if key == "enter":
                    if self.answers:
                        if "action" in self.answers[self.selector_id].keys:
                            if "add_e_key" in self.answers[self.selector_id].keys["action"]:
                                for ek in self.answers[self.selector_id].keys["action"]["add_e_key"]:
                                    game.add_e_key(ek)
                            if "del_e_key" in self.answers[self.selector_id].keys["action"]:
                                for ek in self.answers[self.selector_id].keys["action"]["del_e_key"]:
                                    game.del_e_key(ek)
                            if "add_money" in self.answers[self.selector_id].keys["action"]:
                                game.get_player().money += self.answers[self.selector_id].keys["action"]["add_money"]
                            if "del_money" in self.answers[self.selector_id].keys["action"]:
                                game.get_player().money -= self.answers[self.selector_id].keys["action"]["del_money"]
                            if "add_quest" in self.answers[self.selector_id].keys["action"]:
                                for q in self.answers[self.selector_id].keys["action"]["add_quest"]:
                                    game.get_player ().quests.add_quest(q)
                            if "add_item" in self.answers[self.selector_id].keys["action"]:
                                for i in self.answers[self.selector_id].keys["action"]["add_item"]:
                                    game.get_player().inventory.add_item(i)
                            if "del_item" in self.answers[self.selector_id].keys["action"]:
                                for i in self.answers[self.selector_id].keys["action"]["del_item"]:
                                    game.get_player().inventory.delete_item(i)

                        if self.answers[self.selector_id].keys["go_to"] == "close_dialog":
                            for answer in self.answers:
                                destroy(answer)
                            self.answers.clear()
                            self.disable()
                        elif self.answers[self.selector_id].keys["go_to"] == "close_game":
                            application.quit()
                        else:
                            self.change_dialogue(self.answers[self.selector_id].keys["go_to"])

class Answer(Text):
    def __init__(self,txt="",**kwargs):
        super().__init__(text=txt)

        self.keys = {}

        for key, value in kwargs.items ():
            setattr (self, key, value)

if __name__ == "__main__":
    app = Ursina()

    app.run()