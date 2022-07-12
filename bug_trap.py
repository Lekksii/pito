from ursina import *
import ctypes
import datetime
from tkinter import messagebox

# Сообщение с причиной краша игры
def crash_game_msg(title, text, style = 1):
     return messagebox.showerror(title,text)

# Проверка файлов на существование, если их нет - крашим игру!
def check_file(fname):
    if not os.path.isfile(fname + ".json"):
        if no_file_found(fname + ".json"):
            application.quit()

# Проверка директорий на существование, если их нет - крашим игру!
def check_folder(fname):
    if not os.path.isfile(fname):
        if no_file_found(fname):
            application.quit()

# Шаблон вывода окна ошибки с последующим созданием лога в каталоге с игрой
def no_file_found(file_name):
    log = open("crash_log.txt", "w")
    log.write("BUG TRAP crash engine ver. 0.1\nTime: "+ str(datetime.date.today().strftime("%B %d, %m %Y")+" "+
    datetime.datetime.now().strftime("%H:%M:%S"))+"\n\nCrash reason is:\n>>> FILE: "+file_name+" is not found!")
    log.close()
    return crash_game_msg("ERROR!","FILE: \""+file_name+"\" is not found!\n\nCrash log will be saved to the game folder!",1)

def code_error(reason):
    return crash_game_msg("ERROR!","Some problems in code found!\n\nException: {0}".format(reason),1)

def no_key_field_found(file,key):
    if crash_game_msg("Crash!","Can't find \"{0}\" key in {1}.json file!".format(key,file),1):
        application.quit()