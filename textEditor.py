# this program is a text editor for the user.

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# global variable
tab_control = None
chunk_size = 4096


# overriding the copy event to add a new line when copying nothing.
def copy_text(event):
    selected_text = ""
    try:
        selected_text = event.widget.selection_get()
    except tk.TclError:# no text is selected
        selected_text = "\n"
    event.widget.clipboard_clear()
    event.widget.clipboard_append(selected_text)
    return "break"


def redo_text(event):
    try:
        event.widget.edit_redo()
    except:
        pass
    return "break"


def do_nothing(event):
    return "break"


def remove_tab_event(event):
    #remove_tab(tab_control.index("current"))
    return "break"

def remove_tab(index):
    pass


def add_tab_event(event):
    add_tab()
    return "break"

# Could also be used for new file creation
def add_tab(path="untitled"):
    global tab_control
    # make the tab control visible if it is hidden
    if not tab_control.select(): # check if a tab exists
        tab_control.grid(row=0, column=0, sticky="nsew")
        
    # add a new tab
    text_widget = tk.Text(tab_control, wrap="word", undo=True, autoseparators=True, bd=0)
    text_widget.rowconfigure(0, weight=1)
    text_widget.columnconfigure(0, weight=1)
    tab_control.add(text_widget, text=path)
    Vscrollbar = tk.Scrollbar(text_widget, orient="vertical")
    Vscrollbar.grid(row=0, column=1, sticky="ns")
    text_widget.config(yscrollcommand=Vscrollbar.set)

    # update key bindings
    text_widget.bind("<Control-y>", do_nothing)
    text_widget.bind("<Control-o>", open_file_event)
    text_widget.bind("<Control-Shift-Z>", redo_text)

    # switch to the new tab
    tab_control.select(text_widget)

    # focus on the text widget
    text_widget.focus_set()

    return text_widget


def open_file_event(event):
    open_file()
    return "break"

def open_file():
    result = None # return value
    new_path = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if new_path:
        try:
            with open(new_path, "r") as file:
                text_widget = add_tab(new_path)
                # read the file in chunks to avoid memory issues
                chunk = file.read(chunk_size)
                while chunk:
                    text_widget.insert(tk.END, chunk)
                    chunk = file.read(chunk_size)
        except FileNotFoundError:
            print("The file"+new_path+"was not found.")
        except IOError:
            print("An error occurred while reading the file.")
        except Exception as e:
            print(f"Error: '{e}'")
        result = True
    else:
        result = False
    
    return result


def save_as_file_event(event=None):
    save_as_file()
    return "break"

def save_as_file():
    pass


def save_file_event(event):
    save_file()
    return "break"

def save_file():
    # check if a tab exists
    global tab_control
    file_path = None
    if tab_control.select(): # check if a tab exists
        file_path = tab_control.tab(tab_control.select(), "text")
        if file_path == "untitled":
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir="/", title="Save File As", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
            if file_path:
                tab_control.tab(tab_control.select(), text=file_path)
    
    result = None # return value
    if file_path:
        try:
            with open(file_path, "w") as file:
                text_widget = tab_control.nametowidget(tab_control.select())
                end_index = int(text_widget.index("end").split(".")[0]) - 1
                line_index = 1
                while line_index < end_index:
                    n = 0
                    line_len = int(text_widget.index(f'{line_index}.end').split(".")[1])
                    while n <= line_len:
                        if n + chunk_size > line_len:
                            line = text_widget.get(f"{line_index}.{n}", f"{line_index}.end+1c")
                        else:
                            line = text_widget.get(f"{line_index}.{n}", f"{line_index}.{n+chunk_size}")
                        file.write(line)
                        n += chunk_size
                    line_index += 1
                n = 0
                line_len = int(text_widget.index(f'{line_index}.end').split(".")[1])
                while n < line_len:
                    if n + chunk_size > line_len:
                        line = text_widget.get(f"{line_index}.{n}", f"{line_index}.end")
                    else:
                        line = text_widget.get(f"{line_index}.{n}", f"{line_index}.{n+chunk_size}")
                    file.write(line)
                    n += chunk_size
        except FileNotFoundError:
            print("The file"+file_path+"was not found.")
        except IOError:
            print("An error occurred while reading the file.")
        except Exception as e:
            print(f"Error: '{e}'")
        result = True
    else:
        result = False
    
    return result


def menu_setup(root):
    menu = tk.Menu(root)
    root.config(menu=menu)
    filemenu = tk.Menu(menu, tearoff=False)
    filemenu.add_command(label="New", command=add_tab)
    filemenu.add_command(label="Open...", command=open_file)
    filemenu.add_command(label="Save", command=save_file)
    filemenu.add_command(label="Save As...", command=save_as_file)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menu.add_cascade(label="File", menu=filemenu)
    helpmenu = tk.Menu(menu, tearoff=False)
    helpmenu.add_command(label="About")
    menu.add_cascade(label="Help", menu=helpmenu)
    return menu


def GUI_layout(root):
    # global variable
    global tab_control

    # configure the grid layout
    root.rowconfigure(0, weight=1)
    root.columnconfigure(1, weight=1, minsize=200)

    # list of files frame
    file_frame = tk.Frame(root, width=100, height=100, bg="lightgrey")
    file_frame.grid(row=0, column=0, sticky="ns")
    file_frame.rowconfigure(1, weight=1)
    file_frame.columnconfigure(0, weight=1, minsize=100)

    # the main text editing frame
    edit_frame = tk.Frame(root, width=200, height=200, bg="white")
    edit_frame.grid(row=0, column=1, sticky="nsew")
    edit_frame.rowconfigure(0, weight=1)
    edit_frame.columnconfigure(0, weight=1, minsize=200)
    
    # when opening the app, show the open and new button first
    start_pos = tk.Frame(edit_frame, height=50, bg="lightgrey")
    start_pos.grid(row=0, column=0, sticky="n", pady=70)
    start_pos.rowconfigure(0, weight=1, minsize=100)
    start_pos.columnconfigure(0, weight=1)

    start_frame = tk.Frame(start_pos, bg="lightgrey")
    start_frame.grid(row=0, column=0)
    start_frame.rowconfigure(3, weight=1)
    start_frame.columnconfigure(0, weight=1, minsize=100)

    welcome_label = tk.Label(start_frame, text="Welcome!", bg="lightgrey")
    ttk.Separator(start_frame, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=3) 
    welcome_label.grid(row=0, column=0)
    open_button = tk.Button(start_frame, text="Open", command=open_file)
    open_button.grid(row=2, column=0, sticky="new", padx=10, pady=3)
    new_button = tk.Button(start_frame, text="New", command=add_tab)
    new_button.grid(row=3, column=0, sticky="new", padx=10, pady=(3, 6))

    # Text frames using tab control
    tab_control = ttk.Notebook(edit_frame)
    tab_control.grid(row=0, column=0, sticky="nsew")
    tab_control.grid_remove()
    
    return


# the main function
def main():
    # the GUI component
    root = tk.Tk()
    root.title("texitor")
    root.geometry("800x600")
    #root.minsize(400, 200)

    # create a menu for the GUI
    menu = menu_setup(root)

    # Setup gui layout
    GUI_layout(root)

    # bind the cpy for the app
    root.bind("<Control-c>", copy_text)
    root.bind("<Control-Shift-Z>", redo_text)
    root.bind("<Control-y>", do_nothing)
    root.bind("<Control-s>", save_file_event)
    root.bind("<Control-Shift-S>", save_as_file_event)
    root.bind("<Control-n>", add_tab_event)
    root.bind("<Control-o>", open_file_event)
    root.bind("<Control-w>", remove_tab_event)
    #root.bind("<Control-Tab>", switch_tab)
    #root.bind("<Control-Shift-Tab>", switch_tab_backward)
    
    # runs the GUI
    root.mainloop()

    return

# run funciton if the file is directly called on
if __name__ == "__main__":
    main()


# test text
'''
1. This is ONE!
2. THIS IS two
3.
4. testing
5.
'''

'''
# global variable
    global text_widget

    # configure the grid layout
    root.rowconfigure(0, weight=1)
    root.columnconfigure(1, weight=1, minsize=200)

    # list of files frame
    file_frame = tk.Frame(root, width=100, height=100, bg="lightgrey")
    file_frame.grid(row=0, column=0, sticky="ns")
    #file_frame.pack(side="left", fill="y")
    #tk.Label(file_frame, text="Files!.").pack()
    file_frame.rowconfigure(1, weight=1)
    file_frame.columnconfigure(0, weight=1, minsize=100)
    #tk.Label(file_frame, text="Files").grid(row=0, column=0, sticky="n", pady=5)
    open_button = tk.Button(file_frame, text="Open", command=open_file)
    open_button.grid(row=0, column=0, sticky="new", padx=5, pady=5)
    new_button = tk.Button(file_frame, text="New", command=new_file)
    new_button.grid(row=1, column=0, sticky="new", padx=5)

    # the main text editing frame
    #edit_frame = tk.Frame(root, width=200, bg="white")
    #edit_frame.pack(side="left", fill="both", expand=True)

    text_widget = tk.Text(root, wrap="word", undo=True, autoseparators=True)
    text_widget.grid(row=0, column=1, sticky="nsew")

    # create text widget
    #text_widget = tk.Text(edit_frame, wrap="word", undo=True, autoseparators=True)
    #text_widget.pack(side="left", fill="both", expand=True)
    # adds a scrollbar for the text box
    #Vscrollbar = tk.Scrollbar(edit_frame, orient="vertical")
    Vscrollbar = tk.Scrollbar(root, orient="vertical")
    Vscrollbar.grid(row=0, column=2, sticky="ns")
    #Vscrollbar.pack(side="right", fill="y")
    # connect text widget to the scrollbar
    text_widget.config(yscrollcommand=Vscrollbar.set)
    # bind the cpy for the app
    text_widget.bind("<Control-c>", copy_text)
    text_widget.bind("<Control-Shift-Z>", redo_text)
    text_widget.unbind("<Control-y>")


    #tabControl.add(text_widget, text="Untitled")

    #text_widget2 = tk.Text(tab_frame, wrap="word", undo=True, autoseparators=True, bd=0)
    #text_widget2.grid(row=0, column=0, sticky="nsew")
    #tabControl.add(text_widget2, text="Untitled")

    #text_widget = tk.Text(root, wrap="word", undo=True, autoseparators=True)
    #text_widget.grid(row=0, column=1, sticky="nsew")
'''