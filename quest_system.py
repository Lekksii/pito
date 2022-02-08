from ursina import *
import my_json
import game
from language_system import TKey

system = None

class Quests():
    def __init__(self):
        global system
        self.quests_list = []
        self.active_quest = None
        self.player = None
        system = self
        self.q_file = my_json.read("assets/gameplay/quests")

    def add_quest(self,quest_id):
        for q in self.q_file:
            if q["id"] == quest_id:
                self.quests_list.append (
                    quest_element (q["id"], q["title"], q["description"], q["quest_items"],
                                   q["reward"],q["pda"] if "pda" in q else None))
                break
        invoke(game.show_message,TKey ("message.new.quest"), 5,delay=0.001)

    def get_quest(self,quest_id):
        for q in self.quests_list:
            if q.id == quest_id:
                return q
                break

class quest_element():
    def __init__(self,id=None,title="",description="",quest_items=[],reward={},pda=None):
        self.id = id
        self.title = TKey(title)
        self.description = "<default>"+TKey(description)
        self.quest_items = quest_items
        self.reward = reward
        self.items_file = my_json.read ("assets/gameplay/items")
        self.pda = pda

        if self.quest_items:
            translated_keys = []
            for qi in self.quest_items:
                translated_keys.append(TKey(self.items_file[qi]["name"]))

            self.description += "\n\n>> <rgb(238, 157, 49)>"+"<default>, <rgb(238, 157, 49)>".join(translated_keys)

    #quest fail
    def fail(self):
        for q in system.quests_list:
            if q.id == self.id:
                system.quests_list.remove(q)

    def complete(self):
        has_all_items = False
        q_item_need_count = 0
        print("[DEBUG QUEST] need item count [{0}]".format(q_item_need_count))
        if "money" in self.reward and self.quest_items is None:
            system.player.money += self.reward["money"]
            invoke (game.show_message, "Quest complete!\n+{0}$".format (self.reward["money"]), 5, delay=0.001)
            for q in system.quests_list:
                if q.id == self.id:
                    system.quests_list.remove(q)

        for itm in self.quest_items:
            for inv_itm in game.get_player().inventory.items_in_inventory:
                if itm == inv_itm.item_id:
                    print("Item [{0}] in inventory!".format(itm))
                    q_item_need_count += 1
        print ("[DEBUG QUEST] need item count [{0}]".format (q_item_need_count))
        if q_item_need_count == len(self.quest_items):
            has_all_items = True

        if has_all_items:
            if "money" in self.reward:
                game.get_player().money += self.reward["money"]
                invoke (game.show_message, "Quest complete!\n+{0}$".format(self.reward["money"]), 5, delay=0.001)

            if "items" in self.reward:
                for items in self.reward["items"]:
                    game.get_player().inventory.add_item(items)

            for q_itm in self.quest_items:
                game.get_player().inventory.delete_item(q_itm)
                print("[{0}] was deleted from inventory by quest!".format(q_itm))

            for q in system.quests_list:
                if q.id == self.id:
                    system.quests_list.remove(q)
        else:
            invoke (game.show_message, "You don't have quest items\nfor complete this quest!", 5, delay=0.001)




if __name__ == "__main__":
    app = Ursina()

    app.run()