from ursina import *
import my_json
import os.path
import bug_trap

# Language system v1.0
# by Leksii
# 12/Feb/2021
options = my_json.read("assets/options")

language = "en"

# Ставим язык указанный в опциях, если не находим, то будет ошибка
for lang in options["languages"]:
    if lang == options["current_language"]:
        language = options["current_language"]

# Ищет ключи в языковом файле и возвращает значение ключа
def TKey(key):
    if os.path.isfile("assets/texts/lang_"+language+".json"):
        lang = my_json.read("assets/texts/lang_"+language)
        if key in lang:
            return str(lang[key])
        else:
            print("There is no key \"{0}\" in assets/texts/lang_{1}".format(key,language))
            return str(key)
    else:
        if bug_trap.no_file_found("assets/texts/lang_"+language+".json"):
            application.quit()
