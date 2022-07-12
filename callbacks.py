import game
from ursina import *
import ui
import my_json
from language_system import TKey

import story

# [Callbacks for Enemy actor] (PitoHostile class)
#
# obj:
# .id - ID of Actor "enemy"
#
# .keys{} - Dictionary of this object keys from level.json, contain:
#   {
#   id - ID of Actor "enemy"
#   profile - Profile id from assets/characters/enemy.json
#   state - State of combat animation (attack_from_left, attack_from_right, attack_from_down, attack_forward, ignore)
#   position[] - Vec3 Position of object (X,Y,Z)
#   rotation[] - Vec3 Rotation of object (X,Y,Z)
#   }
#
# .name - Object name
# .profile[] - Json dictionary of profile from assets/characters/enemy.json
# .health (int) - Enemy's health
# .damage (float) - Enemy's damage
# .player_look_at_me (bool) - are player look at enemy?
# .dead (bool) - Enemy are dead?
# .isAttack (bool) - Enemy are attacking?

# Check if player is currently on level
def check_level(lvl):
    if game.get_current_level_id() == lvl:
        return True
    else:
        return False
# Check how many enemies alive on the level
def dead_enemies(val):
    if len(game.get_current_level().hostile_data) == val:
        return True
    else:
        return False

# Callback if enemy was killed
# (arg: obj - PitoHostile class object, that contains all enemy data)
def npc_death(obj = None):
    # Forest road mission
    if dead_enemies(0) and check_level("forest_road"):
        story.forest_road_quest()
    # Intro level bandits
    elif dead_enemies(0) and check_level("intro_battle"):
        invoke(ui.MessageBox,TKey("inv.info"),TKey("msgbox.first_battle.text"),delay=1)
        story.first_battle()
    else:
        print("Enemies on level: {0}".format(str(len(game.get_current_level().hostile_data))))

# Callback if enemy was hit by player
# (arg: obj - PitoHostile class object, that contains all enemy data)
def npc_on_hit(obj = None):
    print("{0} was wounded by {1}!".format(obj.profile_text_id,game.get_player().name))

# Callback if player was hit by enemy
# (arg: player - Player class object, that contains all player data)
# (arg: obj - PitoHostile class object, that contains all enemy data)
def player_on_hit(player = None, obj = None):
    print("{0} was hit by {1}".format(player.name,obj.profile_text_id))

# Callback if level loaded
def on_level_loaded():
    if game.get_current_level().hostile_data:
        for enemies in game.get_current_level().hostile_data:
            enemies.on_level_loaded = True

    if check_level("village"):
        story.first_in_village()
        print("FIRST IN VILLAGE")

# Callback if gameplay started
def on_game_started():
    pass

# Callback when quest added
def on_quest_add(quest):
    pass