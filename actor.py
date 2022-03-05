from ursina import *
from direct.actor.Actor import Actor
from panda3d.core import SamplerState

class PitoActor(Entity):
    def __init__(self,model,texture,gasmask=False,weapon="w_ak",idle_anim="idle",weapon_hold="r_hand", **kwargs):
        super().__init__()
        self.animations = {
            "idle": "assets/models/anim/pito_npc-idle",
            "idle_arm": "assets/models/anim/pito_npc-idle_arm",
            "idle_cross": "assets/models/anim/pito_npc-idle_cross",
            "idle_weapon": "assets/models/anim/pito_npc-idle_weapon",
            "idle_sit": "assets/models/anim/pito_npc-idle_sit",
            "idle_sit_ground": "assets/models/anim/pito_npc-idle_sit_ground"
        }
        self.actor = Actor(
            {"body": "assets/models/"+model,
             "backpack": "assets/models/anim/npc_backpack"}, {
                "body": {
                    "idle": "assets/models/anim/pito_npc-idle",
                    "idle_arm": "assets/models/anim/pito_npc-idle_arm",
                    "idle_cross": "assets/models/anim/pito_npc-idle_cross",
                    "idle_weapon": "assets/models/anim/pito_npc-idle_weapon",
                    "idle_sit": "assets/models/anim/pito_npc-idle_sit",
                    "idle_sit_ground": "assets/models/anim/pito_npc-idle_sit_ground"
                },
                "backpack": {
                    "idle": "assets/models/anim/pito_npc-idle",
                    "idle_arm": "assets/models/anim/pito_npc-idle_arm",
                    "idle_cross": "assets/models/anim/pito_npc-idle_cross",
                    "idle_weapon": "assets/models/anim/pito_npc-idle_weapon",
                    "idle_sit": "assets/models/anim/pito_npc-idle_sit",
                    "idle_sit_ground": "assets/models/anim/pito_npc-idle_sit_ground"
                }})
        self.texture_bp = application.base.loader.loadTexture("assets/textures/texobj2.png")

        self.r_hand = self.actor.exposeJoint(None,"body","r_arm_1")
        self.l_hand = self.actor.exposeJoint(None, "body", "l_arm_1")
        self.backpack = self.actor.exposeJoint(None, "body", "torso")
        self.head = self.actor.exposeJoint(None, "body", "head")

        # r_hand, l_hand, #backpack
        self.weapon_place = weapon_hold
        self.antigas = gasmask
        self.antigas_type = "antigas" # standard, elite

        self.weapon_scale = 2.5
        self.weapon_model = "assets/models/w_ak"
        self.weapon_tex = "assets/textures/texobj2.png"

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
            changeWeapon("assets/models/" + weapon, self.weapon_tex)
            stickToBone(self.backpack,(0.4,-0.5, 0.5),(0, 0, 15))

        if self.weapon_place == "l_hand":
            changeWeapon("assets/models/" + weapon, self.weapon_tex)
            stickToBone(self.l_hand,(-0.05, 0.15, 0.9),(-15, -5, 15))

        if self.weapon_place == "r_hand":
            changeWeapon("assets/models/"+weapon,self.weapon_tex)
            stickToBone(self.r_hand,(-0.05, 0.15, 0.9),(-15, -5, 15))

        if self.antigas:
            changeAntigas("assets/models/antigas","assets/textures/"+self.antigas_type+".png")
            setAntigas(self.head,(0, 0.3, 0),(-90, 180, 0))

        self.actor.reparentTo(self)
        self.texture_npc = application.base.loader.loadTexture(texture)


        self.new_tex = self.actor.find("__Actor_body").findTextureStage('pstalker.png')
        self.new_bp = self.actor.find("__Actor_backpack").findTextureStage('texobj2.png')

        self.texture_npc.setMagfilter(SamplerState.FT_nearest)
        self.texture_bp.setMagfilter(SamplerState.FT_nearest)

        self.actor.find("__Actor_body").setTexture(self.new_tex, self.texture_npc, 1)
        self.actor.find("__Actor_backpack").setTexture(self.new_bp, self.texture_bp, 1)

        self.actor.loop(idle_anim)

        for key, value in kwargs.items ():
            setattr (self, key, value)