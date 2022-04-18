import game

def forest_road_quest():
    if game.get_player().quests.get_quest("quest_rusty_0"):
        game.get_player().quests.get_quest("quest_rusty_0").complete()
        game.get_player().pause_menu.pda_window.add_marker("village_marker")
        game.enable_pda_in_pause(True)

def first_battle():
    game.get_player().quests.add_quest("quest_find_camp")
    game.enable_pda_in_pause(True)

def first_in_village():
    if game.get_player().quests.has_quest("quest_find_camp"):
        game.get_player().quests.get_quest("quest_find_camp").complete()