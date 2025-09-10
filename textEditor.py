# this program is a text editor for the user.

# library imports
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

# global variable
tab_control = None
cursor_pos = None
root = None
chunk_size = 1024 * 8 # 8KB chunk size for reading and writing files.


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


# Overriding the default redo key bind.
def redo_text(event):
    try:
        event.widget.edit_redo()
    except:
        pass
    return "break"


# This should be self-explanatory...
def switch_tab(event):
    return "break"

def switch_tab_backward(event):
    return "break"


# removes default key binding behaviors.
def do_nothing(event):
    return "break"


# Updates the label that displays the cursors position.
def cursor_update(event):
    global cursor_pos
    if tab_control.select(): # check if a tab exists.
        try:
            # get the cursors position and update the label.
            text_frame = tab_control.nametowidget(tab_control.select())
            text_widget = text_frame.winfo_children()[0]
            line, col = text_widget.index(tk.INSERT).split(".")
            cursor_pos.config(text=f"Line: {line} | Column: {int(col)+1}")
        except:
            # display an empty label.
            cursor_pos.config(text="")
    else: # no tab is selected.
        cursor_pos.config(text="")
    return


# Properly removes tabs.
def remove_tab_event(event):
    remove_tab()
    return "break"

def remove_tab(index=None):
    result = None # return value.
    global tab_control
    if tab_control.select(): # check if a tab exists.
        if index is None:
            idx = tab_control.select()
        elif isinstance(index, int):
            idx = tab_control.tabs()[index]
        tab_control.forget(idx)
        result = True

        # hide the tab control if no tabs exist.
        if not tab_control.select(): # check if any tabs exists.
            tab_control.grid_remove()
    else:
        result = False
    
    return result


# Properly adds tabs to the program (new file creation).
def add_tab_event(event):
    add_tab()
    return "break"

def add_tab(path="untitled"):
    global tab_control
    
    # make the tab control visible if it is hidden.
    if not tab_control.select(): # check if a tab exists.
        tab_control.grid(row=0, column=0, sticky="nsew")
    
    # create frame for the tab.
    tab_frame = tk.Frame(tab_control)
    tab_frame.rowconfigure(0, weight=1)
    tab_frame.columnconfigure(0, weight=1)

    # add a new text widget to the tab.
    text_widget = tk.Text(tab_frame, wrap="none", undo=True, autoseparators=True, bd=0)
    text_widget.grid(row=0, column=0, sticky="nsew")

    # adds a scrollbar for the text box.
    Vscrollbar = tk.Scrollbar(tab_frame, orient="vertical", command=text_widget.yview)
    Vscrollbar.grid(row=0, column=1, sticky="ns")
    text_widget.config(yscrollcommand=Vscrollbar.set)

    tab_control.add(tab_frame, text=path)

    # update key bindings for the text widget.
    text_widget.bind("<Control-y>", do_nothing)
    text_widget.bind("<Control-o>", open_file_event)
    text_widget.bind("<KeyRelease>", cursor_update)
    text_widget.bind("<ButtonRelease>", cursor_update)

    # switch to the new tab.
    tab_control.select(tab_frame)

    # focus on the text widget.
    text_widget.focus_set()

    # right click context menu for text widgets.
    context_menu = tk.Menu(tab_control, tearoff=0)
    context_menu.add_command(label="Undo")
    context_menu.add_command(label="Redo")
    context_menu.add_separator()
    context_menu.add_command(label="Cut")
    context_menu.add_command(label="Copy")
    context_menu.add_command(label="Paste")
    context_menu.add_separator()
    context_menu.add_command(label="Select All")
    def show_context_menu(event):
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    text_widget.bind("<Button-3>", show_context_menu)

    return text_widget


# Opens a selected file and puts the contents into a text box.
def open_file_event(event):
    open_file()
    return "break"

def open_file():
    result = None # return value.
    # select the file to open.
    new_path = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if new_path:
        try:
            with open(new_path, "r") as file:
                text_widget = add_tab(new_path)
                # read the file in chunks to avoid memory issues
                chunk = file.read(chunk_size)
                while chunk:
                    text_widget.insert(tk.END, chunk)
                    #text_widget.insert(tk.END, "\n") This was adding an extra new line at the end of each chunk which helped reduce lag
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


# Saves the file under a new name.
def save_as_file_event(event=None):
    save_as_file()
    return "break"

def save_as_file():
    pass


# Saves the currently selected file.
def save_file_event(event):
    save_file()
    return "break"

def save_file():
    # Check if a tab exists
    global tab_control
    file_path = None
    # Check if the currently selected file has a path, make one if not.
    if tab_control.select(): # Check if a tab exists
        file_path = tab_control.tab(tab_control.select(), "text")
        if file_path == "untitled":
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir="/", title="Save File As", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
            if file_path:
                # Update the tab's text
                tab_control.tab(tab_control.select(), text=file_path)
    
    result = None # return value
    # If the file_path is valid, save it.
    if file_path:
        try:
            with open(file_path, "w") as file:
                # Obtain the text widget.
                text_frame = tab_control.nametowidget(tab_control.select())
                text_widget = text_frame.winfo_children()[0]
                # Find the end of the file.
                end_index = int(text_widget.index("end").split(".")[0]) - 1
                line_index = 1
                # Save the file in chunks.
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


# sets up the menu tab on the main window.
def menu_setup():
    global root
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


# Sets up the settings window.
def settings_layout():
    global root
    settings = tk.Toplevel(root)


# Sets up the main layout.
def GUI_layout():
    # global variable
    global tab_control
    global cursor_pos
    global root

    # configure the grid layout
    root.rowconfigure(0, weight=1)
    root.columnconfigure(1, weight=1, minsize=200)

    # list of files frame
    file_frame = tk.Frame(root, width=140, bg="lightgrey")
    file_frame.grid(row=0, column=0, sticky="ns")
    file_frame.rowconfigure(0, weight=1)
    file_frame.columnconfigure(0, weight=1, minsize=100)

    settings_btn = tk.Button(file_frame, text="Settings", command=settings_layout)
    settings_btn.grid(row=0, column=0, sticky="ew", padx=5)

    # the main text editing frame
    edit_frame = tk.Frame(root, width=200, bg="white")
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
    welcome_label.grid(row=0, column=0)
    ttk.Separator(start_frame, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=3) 
    open_button = tk.Button(start_frame, text="Open", command=open_file)
    open_button.grid(row=2, column=0, sticky="new", padx=10, pady=3)
    new_button = tk.Button(start_frame, text="New", command=add_tab)
    new_button.grid(row=3, column=0, sticky="new", padx=10, pady=(3, 6))

    # Text frames using tab control
    tab_control = ttk.Notebook(edit_frame)
    tab_control.grid(row=0, column=0, sticky="nsew")
    tab_control.rowconfigure(0, weight=1)
    tab_control.columnconfigure(0, weight=1)
    tab_control.grid_remove()

    tab_control.bind("<<NotebookTabChanged>>", cursor_update)

    # Add a small label at the bottom.
    status_frame = tk.Frame(root, height=25)
    status_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
    status_frame.rowconfigure(0, weight=1)
    status_frame.columnconfigure(0, weight=1)
    cursor_pos = tk.Label(status_frame, text="", bd=1, textvariable=cursor_pos)
    cursor_pos.grid(row=1, column=0, sticky="e")
    
    return


# the main function
def main():
    global root
    # the GUI component
    root = tk.Tk()
    root.title("Texitor - A Simple Text Editor")
    root.geometry("800x600")
    #root.minsize(400, 200)

    # create a menu for the GUI
    menu = menu_setup()

    # Setup gui layout
    GUI_layout()

    # bind the cpy for the app
    root.bind("<Control-c>", copy_text)
    root.bind("<Control-Shift-Z>", redo_text)
    root.bind("<Control-y>", do_nothing)
    root.bind("<Control-s>", save_file_event)
    root.bind("<Control-Shift-S>", save_as_file_event)
    root.bind("<Control-n>", add_tab_event)
    root.bind("<Control-o>", open_file_event)
    root.bind("<Control-w>", remove_tab_event)
    root.bind("<Control-Shift-N>", remove_tab_event)
    root.bind("<Control-Tab>", switch_tab)
    root.bind("<Control-Shift-Tab>", switch_tab_backward)

    # focus on the root window
    root.focus_set()

    # runs the GUI
    root.mainloop()

    return

# run funciton if the file is directly called on
if __name__ == "__main__":
    main()
