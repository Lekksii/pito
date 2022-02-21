from ursina import *
from direct.actor.Actor import Actor
from panda3d.core import SamplerState

class PitoActor(Entity):
    def __init__(self,model,texture,idle_anim="idle", **kwargs):
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

        self.actor.reparentTo(self)
        self.texture_npc = application.base.loader.loadTexture(texture)
        self.texture_bp = application.base.loader.loadTexture("assets/textures/texobj2.png")

        self.new_tex = self.actor.find("__Actor_body").findTextureStage('pstalker.png')
        self.new_bp = self.actor.find("__Actor_backpack").findTextureStage('texobj2.png')

        self.texture_npc.setMagfilter(SamplerState.FT_nearest)
        self.texture_bp.setMagfilter(SamplerState.FT_nearest)

        self.actor.find("__Actor_body").setTexture(self.new_tex, self.texture_npc, 1)
        self.actor.find("__Actor_backpack").setTexture(self.new_bp, self.texture_bp, 1)

        self.actor.loop(idle_anim)

        for key, value in kwargs.items ():
            setattr (self, key, value)