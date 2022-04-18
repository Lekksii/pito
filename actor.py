from ursina import *
from direct.actor.Actor import Actor
from direct.interval.ActorInterval import LerpAnimInterval
from panda3d.core import SamplerState
import my_json
import game
import callbacks

class PitoActor(Entity):
    def __init__(self,profile_id, **kwargs):
        #model,texture,gasmask=False,weapon="w_ak",idle_anim="idle",weapon_hold="r_hand"
        super().__init__()
        self.id = ""
        self.keys = {}
        self.profile = my_json.read("assets/creatures/characters")[profile_id]
        self.anims = my_json.read("assets/creatures/animations")

        self.npc_model = self.profile["model"]
        self.npc_texture = "assets/textures/"+self.profile["texture"]+".png"
        self.gasmask = self.profile["gasmask"]
        self.npc_weapon = self.profile["weapon"]
        self.weapon_hold = self.profile["weapon_hold"]
        self.idle_anim = self.profile["idle_animation"]

        self.actor = Actor(
            {"body": "assets/models/"+self.npc_model,
             "backpack": "assets/models/anim/npc_backpack"}, {
                "body": self.anims,
                "backpack": self.anims
            })
        self.texture_bp = application.base.loader.loadTexture("assets/textures/texobj2.png")

        self.r_hand = self.actor.exposeJoint(None,"body","r_arm_1")
        self.l_hand = self.actor.exposeJoint(None, "body", "l_arm_1")
        self.backpack = self.actor.exposeJoint(None, "body", "torso")
        self.head = self.actor.exposeJoint(None, "body", "head")

        # r_hand, l_hand, #backpack
        self.weapon_place = self.weapon_hold
        self.antigas = self.gasmask
        self.antigas_type = self.profile["gasmask_type"] # antigas, elite

        self.weapon_scale = 2.5
        self.weapon_model = "assets/models/"+self.npc_weapon
        self.weapon_tex = "assets/textures/texobj2.png" if "w_tex" not in self.profile else self.profile["w_tex"]

        self.weapon = Entity(position=0, rotation=0, scale=self.weapon_scale,
                             model=self.weapon_model, texture=self.weapon_tex)
        self.antigas_model = Entity(position=0, rotation=0, scale=2.5,
                             model=None, texture="assets/textures/antigas.png")

        def stickToBone(bone,pos,rot):
            self.weapon.parent = bone
            self.weapon.position = pos
            self.weapon.rotation = rot

        def changeWeapon(model,texture):
            self.weapon.model = model
            self.weapon.texture = texture

        def setAntigas(bone, pos, rot):
            self.antigas_model.parent = bone
            self.antigas_model.position = pos
            self.antigas_model.rotation = rot

        def changeAntigas(model, texture):
            self.antigas_model.model = model
            self.antigas_model.texture = texture

        if self.weapon_place == "backpack":
            changeWeapon("assets/models/" + self.npc_weapon, self.weapon_tex)
            stickToBone(self.backpack,(0.4,-0.5, 0.5),(0, 0, 15))

        if self.weapon_place == "l_hand":
            changeWeapon("assets/models/" + self.npc_weapon, self.weapon_tex)
            stickToBone(self.l_hand,(-0.05, 0.15, 0.9),(-15, -5, 15))

        if self.weapon_place == "r_hand":
            changeWeapon("assets/models/"+self.npc_weapon,self.weapon_tex)
            stickToBone(self.r_hand,(-0.05, 0.15, 0.9),(-15, -5, 15))

        if self.antigas:
            changeAntigas("assets/models/antigas","assets/textures/"+self.antigas_type+".png")
            setAntigas(self.head,(0, 0.3, 0),(-90, 180, 0))

        self.actor.reparentTo(self)
        self.texture_npc = application.base.loader.loadTexture(self.npc_texture)

        self.collider = BoxCollider(self,center=Vec3(0,1.2,0),size=Vec3(0.3,1.2,0.3))

        self.new_tex = self.actor.find("__Actor_body").findTextureStage('pstalker.png')
        self.new_bp = self.actor.find("__Actor_backpack").findTextureStage('texobj2.png')

        self.texture_npc.setMagfilter(SamplerState.FT_nearest)
        self.texture_bp.setMagfilter(SamplerState.FT_nearest)

        self.actor.find("__Actor_body").setTexture(self.new_tex, self.texture_npc, 1)
        self.actor.find("__Actor_backpack").setTexture(self.new_bp, self.texture_bp, 1)

        self.actor.loop(self.idle_anim)

        for key, value in kwargs.items ():
            setattr (self, key, value)

class PitoHostile(Entity):
    def __init__(self,profile_id,state, **kwargs):
        super().__init__()
        self.id = ""
        self.keys = {}
        #stalker, bandit, soldier, mercenary
        self.profile = my_json.read("assets/creatures/enemy")[profile_id]
        self.health = round(random.uniform(self.profile["health"][0],self.profile["health"][1]),1)
        self.damage = round(random.uniform(self.profile["damage"][0],self.profile["damage"][1]),1)
        self.anims = my_json.read("assets/creatures/animations")
        self.player_look_at_me = False
        self.dead = False
        self.state_machine_run = False
        self.current_animation = None
        self.sequence = Sequence()
        self.isAttack = True
        self.state_anims_count = 0

        self.attack_state = state if state is not None else "ignore"

        self.attack_states = {
            "attack_from_left": ["shoot_left", "hide_left"],
            "attack_from_right": ["shoot_right", "hide_right"],
            "attack_from_down": ["shoot_up", "hide_down"],
            "attack_forward": "shoot_forward",
            "ignore": "idle"
        }

        self.npc_model = "assets/models/"+self.profile["model"]
        self.npc_texture = "assets/textures/" + random.choice(self.profile["texture"]) + ".png"

        self.actor = Actor(
            {"body": self.npc_model,
             "backpack": "assets/models/anim/npc_backpack"}, {
                "body": self.anims,
                "backpack": self.anims
            })
        self.texture_bp = application.base.loader.loadTexture("assets/textures/texobj2.png")

        self.r_hand = self.actor.exposeJoint(None, "body", "r_arm_1")
        self.l_hand = self.actor.exposeJoint(None, "body", "l_arm_1")
        self.backpack = self.actor.exposeJoint(None, "body", "torso")
        self.head = self.actor.exposeJoint(None, "body", "head")

        # r_hand, l_hand, #backpack
        self.weapon_place = "r_hand"

        self.weapon_scale = 2.5
        self.weapon_model = "assets/models/" + random.choice(self.profile["weapons"])
        self.weapon_tex = "assets/textures/texobj2.png" if "w_tex" not in self.profile else self.profile["w_tex"]

        self.weapon = Entity(position=0, rotation=0, scale=self.weapon_scale,
                             model=self.weapon_model, texture=self.weapon_tex)
        self.hitbox = EnemyHitBox(id="enemy",root=self,model="cube",color=color.rgba(255,0,0,128) if game.setting.developer_mode else color.clear,
                                  parent=self.backpack,
                             scale=(1,1,2),position=(0,0,1),collider="mesh")
        #BoxCollider(self, center=Vec3(0, 1.2, 0), size=Vec3(0.3, 1.2, 0.3))

        def stickToBone(bone, pos, rot):
            self.weapon.parent = bone
            self.weapon.position = pos
            self.weapon.rotation = rot

        def changeWeapon(model, texture):
            self.weapon.model = model
            self.weapon.texture = texture

        if self.weapon_place == "backpack":
            changeWeapon(self.weapon_model, self.weapon_tex)
            stickToBone(self.backpack, (0.4, -0.5, 0.5), (0, 0, 15))

        if self.weapon_place == "l_hand":
            changeWeapon(self.weapon_model, self.weapon_tex)
            stickToBone(self.l_hand, (-0.05, 0.15, 0.9), (-15, -5, 15))

        if self.weapon_place == "r_hand":
            changeWeapon(self.weapon_model, self.weapon_tex)
            stickToBone(self.r_hand, (-0.05, 0.15, 0.9), (-5, -2, 15))

        self.actor.reparentTo(self)
        self.texture_npc = application.base.loader.loadTexture(self.npc_texture)

        self.new_tex = self.actor.find("__Actor_body").findTextureStage('pstalker.png')
        self.new_bp = self.actor.find("__Actor_backpack").findTextureStage('texobj2.png')

        self.texture_npc.setMagfilter(SamplerState.FT_nearest)
        self.texture_bp.setMagfilter(SamplerState.FT_nearest)

        self.actor.find("__Actor_body").setTexture(self.new_tex, self.texture_npc, 1)
        self.actor.find("__Actor_backpack").setTexture(self.new_bp, self.texture_bp, 1)

        #invoke(self.start_state,delay=0.01)

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def player_look(self,bool):
        if self.health > 0:
            self.player_look_at_me = bool
            if not self.player_look_at_me:
                #self.isAttack = True
                #self.sequence.loop = True
                pass

    def hit(self,damage):
        self.health -= round(damage,1)
        callbacks.npc_on_hit(self)
        if self.health <= 0:
            self.health = 0
            game.get_current_level().hostile_data.remove(self)
            callbacks.npc_death(self)
            self.death()

    def death(self):
        def state_type(state):
            if self.attack_state == state:
                return True
            else:
                return False

        self.dead = True
        self.actor.stop()

        if self.hitbox is not None:
            destroy(self.hitbox,0.01)

        if state_type("attack_from_down") or state_type("attack_forward"):
            self.play_anim("death_front")
        elif state_type("attack_from_left"):
            self.play_anim("death_left")
        elif state_type("attack_from_right"):
            self.play_anim("death_right")
        else:
            death_anims = ["death_front","death_front_new"]
            self.play_anim(random.choice(death_anims))

    def play_anim(self,animation):
        self.actor.play(animation)
        self.current_animation = animation

        #print(self.current_animation)

    def update(self):
        if self.dead and self.sequence is not None:
            #print("SEQUENCE: Not paused while dead!")
            self.sequence.pause()
            #print("SEQUENCE: Paused!")
            self.sequence.kill()
            self.sequence = None
            #print("SEQUENCE: Killed!")

        if self.health > 0 and not self.dead:
            def anim_seq():
                self.sequence.append(Func(self.actor.play, self.attack_states[self.attack_state][0]))
                #self.sequence.append(Func(print, self.attack_states[self.attack_state][0]))
                self.sequence.append(Wait(0.7))
                if not game.pause:
                    self.sequence.append(Func(game.get_player().hit,random.uniform(self.profile["damage"][0], self.profile["damage"][1])))
                self.sequence.append(Wait(random.randint(self.profile["attack_delay"][0], self.profile["attack_delay"][1])))
                self.sequence.append(Func(self.actor.play, self.attack_states[self.attack_state][1]))
                #self.sequence.append(Func(print, self.attack_states[self.attack_state][1]))
                self.sequence.append(Wait(random.randint(self.profile["attack_delay"][0], self.profile["attack_delay"][1])))
                self.sequence.loop = True
                self.sequence.start()
                self.isAttack = False

            if self.attack_state == "ignore" and self.isAttack:
                self.actor.loop(self.attack_states[self.attack_state])
                self.current_animation = self.attack_states[self.attack_state]
                #print("started ignore state")
                self.isAttack = False

            if self.attack_state == "attack_from_left" and self.isAttack:
                anim_seq()

            if self.attack_state == "attack_from_right" and self.isAttack:
                anim_seq()

            if self.attack_state == "attack_from_down" and self.isAttack:
                anim_seq()

            if self.attack_state == "attack_forward" and self.isAttack:
                self.actor.loop(self.attack_states[self.attack_state])
                self.isAttack = False
                #print("started attack_forward state")


class EnemyHitBox(Entity):
    def __init__(self, **kwargs):
        super().__init__()

        self.id = ""
        self.root = None

        for key, value in kwargs.items ():
            setattr (self, key, value)
