from tkinter import *
import tkinter.scrolledtext as scrolledText
from tkinter import messagebox

# Window
app = Tk()

app.title('Item Editor')
app.geometry('400x550')
app.resizable(False, False)

workspace = Frame(app)
result_frame = Frame(app, bg="black", bd=1)
buttons = Frame(app)
result_title = Frame(app)

types = [
    "usable",
    "equipment",
    "item",
    "weapon"
]

item_id_value = StringVar()
item_name_value = StringVar()
item_caption_value = StringVar()
item_icon_value = StringVar()
item_price_value = IntVar()
item_type_value = StringVar()
item_type_value.set(types[2])


# Label object
def LabelText(root, text, size=14, font_size='regular', padx=0, pady=0, row=0, column=0, justify=LEFT):
    obj = Label(root, text=text, anchor='e', font=(font_size, size), padx=padx, pady=pady, justify=justify)
    obj.grid(row=row, column=column)
    return obj


# Input field for text
def InputField(root, var, row=0, column=0):
    obj = Entry(root, textvariable=var)
    obj.grid(row=row, column=column)
    return obj


def clear_btn_callback():
    if checkVars():
        item_id_value.set("")
        item_name_value.set("")
        item_caption_value.set("")
        item_icon_value.set("")
        item_price_value.set("0")
        result.delete(1.0, END)

    print("Clear data")

def checkVars():
    if item_id_value.get() == "" and\
    item_name_value.get() == "" and\
    item_caption_value.get() == "" and \
    item_icon_value.get() == "":
        return False
    else:
        return True

def onTypeChange(event):
    pass

def gen_data_callback():
    if checkVars():

        result.configure(state="normal")
        result.delete(1.0, END)

        def setVar(var):
            return str(var.get()) if var.get() else "no_data"

        data = """\""""+setVar(item_id_value)+"""\": {
    "name": \""""+setVar(item_name_value)+"""\",
    "caption": \""""+setVar(item_caption_value)+"""\",
    "icon": "assets/ui/items/"""+setVar(item_icon_value)+""".png",
    "price": """+setVar(item_price_value)+""",
    "type": \""""+setVar(item_type_value)+"""\"
    }"""

        result.insert(INSERT,data)
    else:
        messagebox.showerror("Error!","Item data fields are empty!")

itm_id_label = LabelText(workspace, text="Item ID:", row=0, column=0)
itm_name_label = LabelText(workspace, text="Name:", row=1, column=0)
itm_caption_label = LabelText(workspace, text="Caption:", row=2, column=0)
itm_icon_label = LabelText(workspace, text="Icon:", row=3, column=0)
itm_price_label = LabelText(workspace, text="Price:", row=4, column=0)
itm_type_label = LabelText(workspace, text="Type:", row=5, column=0)

result_label = LabelText(result_title, text="Result:", row=0, column=0, pady=0)
result = scrolledText.ScrolledText(result_frame, width=50, height=15, wrap=WORD)
result.grid(row=1, column=0)
result.configure(state="disabled")

itm_id = InputField(workspace, item_id_value, column=1)
itm_name = InputField(workspace, item_name_value, row=1, column=1)
itm_caption = InputField(workspace, item_caption_value, row=2, column=1)
itm_icon = InputField(workspace, item_icon_value, row=3, column=1)
itm_price = InputField(workspace, item_price_value, row=4, column=1)
itm_type = OptionMenu(workspace, item_type_value, *types, command=onTypeChange)
itm_type.config(width=18)
itm_type.grid(row=5, column=1)

clear_data = Button(buttons, text='Clear all', width=15, command=clear_btn_callback)
clear_data.grid(row=7, column=0, pady=30)
generate_data = Button(buttons, text='Generate', width=15, command=gen_data_callback)
generate_data.grid(row=7, column=1, pady=30)

workspace.pack(anchor='center', pady=10)
buttons.pack(anchor='center')
result_title.pack(anchor='center')
result_frame.pack(anchor='center', pady=0)

# Start
app.mainloop()
