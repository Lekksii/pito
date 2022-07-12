from ursina import *
from panda3d.core import PerspectiveLens
from panda3d.core import TextureStage
from panda3d.core import DirectionalLight as PandaDirectionalLight
from panda3d.core import PointLight as PandaPointLight
from panda3d.core import AmbientLight as PandaAmbientLight
from panda3d.core import Spotlight as PandaSpotLight


class PitoLight(Entity):
    def __init__(self, **kwargs):
        super().__init__(rotation_x=90)


    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._light.setColor(value)


class PitoDirectionalLight(Light):
    def __init__(self, shadows=True, **kwargs):
        super().__init__()
        self._light = PandaDirectionalLight('directional_light')
        render.setLight(self.attachNewNode(self._light))
        self.shadow_map_resolution = Vec2(1024, 1024)

        for key, value in kwargs.items():
            setattr(self, key ,value)

        invoke(setattr, self, 'shadows', shadows, delay=.1)


    @property
    def shadows(self):
        return self._shadows

    @shadows.setter
    def shadows(self, value):
        self._shadows = value
        if value:
            self._light.set_shadow_caster(True, int(self.shadow_map_resolution[0]), int(self.shadow_map_resolution[1]))
            bmin, bmax = scene.get_tight_bounds(self)
            lens = self._light.get_lens()
            lens.set_near_far(bmin.z*2, bmax.z*2)
            lens.set_film_offset((bmin.xy + bmax.xy) * .5)
            lens.set_film_size((bmax.xy - bmin.xy))
        else:
            self._light.set_shadow_caster(False)




class PitoPointLight(Light):
    def __init__(self,distance=1,colour=(1,1,1,1), **kwargs):
        super().__init__()
        self.keys = None
        self._light = PandaPointLight('point_light')
        self._light.attenuation = (1, 0, 2)
        self._light.max_distance = distance
        self._light.setColor(colour)
        self._pl = self.attachNewNode(self._light)
        #self._light.setShadowCaster(True, 128, 128)
        render.setLight(self._pl)

        for key, value in kwargs.items():
            setattr(self, key ,value)


class PitoAmbientLight(Light):
    def __init__(self,colour=(1,1,1,1), **kwargs):
        super().__init__()
        self.keys = None
        self._light = PandaAmbientLight('ambient_light')
        self._al = render.setLight(self.attachNewNode(self._light))
        self._al.node().setColor(colour)


        for key, value in kwargs.items():
            setattr(self, key ,value)



class PitoSpotLight(Light):
    def __init__(self, **kwargs):
        super().__init__(distance=0.01, color=color.red, exponent=50)
        self.keys = None
        self._light = PandaSpotLight('spot_light')
        self._light.setShadowCaster(True, 128, 128)
        render.setLight(self.attachNewNode(self._light))
        #render.setShaderAuto()

        for key, value in kwargs.items():
            setattr(self, key ,value)
