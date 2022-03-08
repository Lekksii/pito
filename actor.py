from ursina import *
from direct.actor.Actor import Actor
from panda3d.core import SamplerState
import my_json

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