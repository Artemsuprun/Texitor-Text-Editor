# A simple text editor using tkinter
#
# Author:   Artem Suprun
# Date:     12/29/2025 *(last updated)*
# Description:
#   A simple text editor application built using the tkinter library in Python.
#

# library imports
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import queue


# This is a Custom Notebook, but I don't feel great taking 
# credit for the idea becuase it wasn't from me. the reference 
# came from this stack overflow link (https://stackoverflow.com/a/39459376)
class BetterNotebook(ttk.Notebook):
    __initialized = False
    def __init__(self, *args, **kwargs):
        if not self.__initialized:
            self.__initialize_custom_style()
            self.__initialized = True
        
        kwargs["style"] = "BetterNotebook"
        ttk.Notebook.__init__(self, *args, **kwargs)

        self._active = None
        self.q = queue.SimpleQueue()

        self.bind("<ButtonPress-1>", self.on_close_press, True)
        self.bind("<ButtonRelease-1>", self.on_close_release)
    
    def on_close_press(self, event):
        element = self.identify(event.x, event.y)

        if "close" in element:
            index = self.index("@%d,%d" % (event.x, event.y))
            self.state(['pressed'])
            self._active = index
            return "break"
        
    def on_close_release(self, event):
        if not self.instate(["pressed"]):
            return
        
        element = self.identify(event.x, event.y)
        if "close" not in element:
            return
        
        index = self.index("@%d,%d" % (event.x, event.y))

        if self._active == index:
            self.q.put(index)
            self.event_generate("<<NotebookTabClosed>>")
        
        self.state(["!pressed"])
        self._active = None
    
    def __initialize_custom_style(self):
        style = ttk.Style()
        self.images = (
            tk.PhotoImage("img_close", data='''
                R0lGODlhCAAIAMIBAAAAADs7O4+Pj9nZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
                '''),
            tk.PhotoImage("img_closeactive", data='''
                R0lGODlhCAAIAMIEAAAAAP/SAP/bNNnZ2cbGxsbGxsbGxsbGxiH5BAEKAAQALAAA
                AAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU5kEJADs=
                '''),
            tk.PhotoImage("img_closepressed", data='''
                R0lGODlhCAAIAMIEAAAAAOUqKv9mZtnZ2Ts7Ozs7Ozs7Ozs7OyH+EUNyZWF0ZWQg
                d2l0aCBHSU1QACH5BAEKAAQALAAAAAAIAAgAAAMVGDBEA0qNJyGw7AmxmuaZhWEU
                5kEJADs=
            ''')
        )

        style.element_create("close", "image", "img_close",
                            ("active", "pressed", "!disabled", "img_closepressed"),
                            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        style.layout("BetterNotebook", [("BetterNotebook.client", {"sticky": "nswe"})])
        style.layout("BetterNotebook.Tab", [
            ("BetterNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("BetterNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("BetterNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("BetterNotebook.label", {"side": "left", "sticky": ''}),
                                    ("BetterNotebook.close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])

# Settings page of the app.
class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

# the main page of the app.
class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # setting up the frame's grid layout.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, minsize=200)

        # side bare of the text editor
        side_frame = tk.Frame(self, width=140, bg="lightgrey")
        side_frame.grid(row=0, column=0, sticky="ns")
        side_frame.rowconfigure(1, weight=1)
        side_frame.columnconfigure(0, weight=1, minsize=100)

        # program options on the side bar
        terminal_btn = tk.Button(side_frame, text="Terminal")#, command=self._terminal)
        terminal_btn.grid(row=1, column=0, sticky="sew", padx=5, pady=5)
        ttk.Separator(side_frame, orient="horizontal").grid(row=1, column=0, sticky="sew")
        settings_btn = tk.Button(side_frame, text="Settings", command=lambda: controller._show_frame(Settings))
        settings_btn.grid(row=2, column=0, sticky="sew", padx=5, pady=5)
        
        # the main text editing frame
        edit_frame = tk.Frame(self, width=200, bg="white")
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
        open_button = tk.Button(start_frame, text="Open", command=controller._open_file)
        open_button.grid(row=2, column=0, sticky="new", padx=10, pady=3)
        new_button = tk.Button(start_frame, text="New", command=controller._add_tab)
        new_button.grid(row=3, column=0, sticky="new", padx=10, pady=(3, 6))

        # Text frames using tab control
        self.tab_control = BetterNotebook(edit_frame)
        self.tab_control.enable_traversal()
        self.tab_control.grid(row=0, column=0, sticky="nsew")
        self.tab_control.rowconfigure(0, weight=1)
        self.tab_control.columnconfigure(0, weight=1)
        self.tab_control.grid_remove()

        self.tab_control.bind("<<NotebookTabChanged>>", controller._cursor_update)

        # Add a small label at the bottom.
        status_frame = tk.Frame(self, height=25)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        status_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        self.cursor_pos = tk.Label(status_frame, text="", bd=1)
        self.cursor_pos.grid(row=1, column=0, sticky="e")
        return
    
    def get_tab_index(self):
        return self.tab_control.index("current")
    
    def set_cursor(self, txt=""):
        if not isinstance(txt, str):
            txt = str(txt)
        self.cursor_pos.config(text=txt)
        return
    
    def forget_tab(self, tab):
        if isinstance(tab, int):
            self.tab_control.forget(tab)
        return
    
    def hide_tabs(self):
        self.tab_control.grid_remove()
        return
    
    def display_tabs(self):
        self.tab_control.grid(row=0, column=0, sticky="nsew")
        return
    
    def add_tab(self, path="untitled"):
        # create frame for the tab.
        tab_frame = tk.Frame(self.tab_control)
        tab_frame.rowconfigure(0, weight=1)
        tab_frame.columnconfigure(0, weight=1)

        # add a new text widget to the tab.
        text_widget = tk.Text(tab_frame, wrap="none", undo=True, autoseparators=True, bd=0)
        text_widget.grid(row=0, column=0, sticky="nsew")

        # adds a scrollbar for the text box.
        Vscrollbar = tk.Scrollbar(tab_frame, orient="vertical", command=text_widget.yview)
        Vscrollbar.grid(row=0, column=1, sticky="ns")
        text_widget.config(yscrollcommand=Vscrollbar.set)

        Hscrollbar = tk.Scrollbar(tab_frame, orient="horizontal", command=text_widget.xview)
        Hscrollbar.grid(row=1, column=0, sticky="ew")
        text_widget.config(xscrollcommand=Hscrollbar.set)

        self.tab_control.add(tab_frame, text=path)

        # right click context menu for text widgets.
        context_menu = tk.Menu(self.tab_control, tearoff=0)
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
    
    def switch_tab(self, tab=None):
        if isinstance(tab, int):
            self.tab_control.select(tab)
        else:
            self.tab_control.select(self.tab_control.index("end")-1)
        return
    
    def get_tab_name(self, tab=None):
        if isinstance(tab, int):
            name = self.tab_control.tab(tab, "text")
        else:
            name = self.tab_control.tab(self.tab_control.select(), "text")
        return name
    
    def set_tab_name(self, name, tab=None):
        if isinstance(tab, int):
            self.tab_control.tab(tab, text=name)
        else:
            self.tab_control.tab(self.tab_control.select(), text=name)
        return


# Class form of the app.
class TextEditor(tk.Tk):
    def __init__(self, *args, **kwargs):
        # Properly initializing the parent constructor to start.
        tk.Tk.__init__(self, *args, **kwargs)
        # member variables
        self.chunk_size = 1024 * 8 # 8KB chunk size for reading and writing files.
        self.tabs = [] # keeps track of the tabs.
        self.current_frame = MainPage
        # Title of the main page.
        self.title("Texitor ~ A Simple Text Editor")
        # Setting up the window size of the app.
        self.geometry("800x600")
        # Setting up the grid layout.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # setting up the base container
        container = tk.Frame(self, background="lightblue")
        container.grid(row=0, column=0, sticky="nsew")
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)

        # contain the frames.
        self.frames = {}
        for F in [MainPage, Settings]: # might add more frames for other options later on.
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self._show_frame(MainPage)

        # binding keys to the main window
        self.bind("<Control-c>", self._copy_text)
        self.bind("<Control-Shift-Z>", self._redo_text)
        self.bind("<Control-y>", self._do_nothing)
        self.bind("<Control-s>", self._save_file_event)
        self.bind("<Control-Shift-S>", self._save_as_file_event)
        self.bind("<Control-n>", self._add_tab_event)
        self.bind("<Control-o>", self._open_file_event)
        self.bind("<Control-Shift-N>", self._remove_tab_event)
        self.bind("<<NotebookTabClosed>>", self._remove_tab_event)

        # set up the menu options
        self._menu_setup()

        # focus on the window
        self.focus_set()

        # ensure files are saved if needed.
        self.protocol("WM_DELETE_WINDOW", self._unsaved_file)
        return

    # A method of switching view frames.
    def _show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()
        self.current_frame = f
        return
    
    # sets up the menu tab on the main window.
    def _menu_setup(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        filemenu = tk.Menu(menu, tearoff=False)
        filemenu.add_command(label="New", command=self._add_tab)
        filemenu.add_command(label="Open...", command=self._open_file)
        filemenu.add_command(label="Save", command=self._save_file)
        filemenu.add_command(label="Save As...", command=self._save_as_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._unsaved_file)
        menu.add_cascade(label="File", menu=filemenu)
        helpmenu = tk.Menu(menu, tearoff=False)
        helpmenu.add_command(label="About")
        menu.add_cascade(label="Help", menu=helpmenu)
        return
    
    # Overriding the copy event to add a new line when copying nothing.
    def _copy_text(self, event):
        selected_text = ""
        try:
            selected_text = event.widget.selection_get()
        except tk.TclError:# no text is selected
            selected_text = "\n"
        event.widget.clipboard_clear()
        event.widget.clipboard_append(selected_text)
        return "break"
    
    # Overriding the default redo key bind.
    def _redo_text(self, event):
        try:
            event.widget.edit_redo()
        except:
            pass
        return "break"
    
    # removes default key binding behaviors.
    def _do_nothing(self, event):
        return "break"

    # Updates the label that displays the cursors position.
    def _cursor_update(self, event):
        result = None
        text = ''
        if self.tabs: # check if a tab exists.
            try:
                # get the cursors position and update the label.
                text_widget = self.tabs[self.frames[MainPage].get_tab_index()]
                line, col = text_widget.index(tk.INSERT).split(".")
                text = f"Line: {line} | Column: {int(col)+1}"
                result = True
            except:
                # display an empty label.
                result = False
        self.frames[MainPage].set_cursor(text)
        return result

    # Properly removes tabs.
    def _remove_tab_event(self, event):
        if event.type == tk.EventType.KeyPress:
            self._remove_tab()
        else: # if the event came from tab button.
            self._remove_tab(event.widget.q.get())
        return "break"

    def _remove_tab(self, index=None):
        result = None # return value.
        if self.tabs: # check if a tab exists.
            if index is None:
                idx = self.frames[MainPage].get_tab_index() # get current if none is given.
            else:
                idx = index
            self.tabs.pop(idx)
            self.frames[MainPage].forget_tab(idx)
            result = True

            # hide the tab control if no tabs exist.
            if not self.tabs: # check if any tabs exists.
                self.frames[MainPage].hide_tabs()
        else:
            result = False
        
        return result

    # Properly adds tabs to the program (new file creation).
    def _add_tab_event(self, event):
        self._add_tab()
        return "break"

    def _add_tab(self, path="untitled"):
        # make the tab control visible if it is hidden.
        if not self.tabs: # check if a tab exists.
            self.frames[MainPage].display_tabs()
        
        text_widget = self.frames[MainPage].add_tab(path)
        self.tabs.append(text_widget)

        # update key bindings for the text widget.
        text_widget.bind("<Control-y>", self._do_nothing)
        text_widget.bind("<Control-o>", self._open_file_event)
        text_widget.bind("<KeyRelease>", self._cursor_update)
        text_widget.bind("<ButtonRelease>", self._cursor_update)

        # switch to the new tab at the end.
        self.frames[MainPage].switch_tab(len(self.tabs)-1)

        # focus on the text widget.
        text_widget.focus_set()

        return text_widget

    # Opens a selected file and puts the contents into a text box.
    def _open_file_event(self, event):
        self._open_file()
        return "break"

    def _open_file(self):
        result = None # return value.
        # select the file to open.
        new_path = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if new_path:
            try:
                with open(new_path, "r") as file:
                    text_widget = self._add_tab(new_path)
                    # read the file in chunks to avoid memory issues
                    chunk = file.read(self.chunk_size)
                    while chunk:
                        text_widget.insert(tk.END, chunk)
                        #text_widget.insert(tk.END, "\n") This was adding an extra new line at the end of each chunk which helped reduce lag
                        chunk = file.read(self.chunk_size)
                    # reset the text redo/undo stack
                    text_widget.edit_reset()
                    # move cursor to the start.
                    text_widget.mark_set("insert", "1.0")
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
    def _save_as_file_event(self, event=None):
        self._save_as_file()
        return "break"

    def _save_as_file(self):
        # check if the tab exist
        if self.tabs:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir="/", title="Save File As", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
            if self.__save(file_path): # if the file was successfully saved
                self.frames[MainPage].set_tab_name(file_path) # rename the tab.
        return

    # Saves the currently selected file.
    def _save_file_event(self, event):
        self._save_file()
        return "break"

    def _save_file(self):
        file_path = None
        # Check if the currently selected file has a path, make one if not.
        if self.tabs: # Check if a tab exists.
            file_path = self.frames[MainPage].get_tab_name()
            if file_path == "untitled":
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir="/", title="Save File As", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
                if file_path:
                    # Update the tab's text
                    self.frames[MainPage].set_tab_name(file_path)
        
            self.__save(file_path)
        return
    
    def __save(self, file_path, tab=None):
        result = None
        if tab is None: # get the current index if none is provided.
            tab = self.frames[MainPage].get_tab_index()
        # Obtain the text widget.
        text_widget = self.tabs[tab]
        # If the file_path is valid, save it.
        if file_path:
            try:
                with open(file_path, "w") as file:
                    # Find the end of the file.
                    end_index = int(text_widget.index("end").split(".")[0]) - 1
                    line_index = 1
                    # Save the file in chunks.
                    while line_index < end_index:
                        n = 0
                        line_len = int(text_widget.index(f'{line_index}.end').split(".")[1])
                        while n <= line_len:
                            if n + self.chunk_size > line_len:
                                line = text_widget.get(f"{line_index}.{n}", f"{line_index}.end+1c")
                            else:
                                line = text_widget.get(f"{line_index}.{n}", f"{line_index}.{n+self.chunk_size}")
                            file.write(line)
                            n += self.chunk_size
                        line_index += 1
                    n = 0
                    line_len = int(text_widget.index(f'{line_index}.end').split(".")[1])
                    while n < line_len:
                        if n + self.chunk_size > line_len:
                            line = text_widget.get(f"{line_index}.{n}", f"{line_index}.end")
                        else:
                            line = text_widget.get(f"{line_index}.{n}", f"{line_index}.{n+self.chunk_size}")
                        file.write(line)
                        n += self.chunk_size
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
    
    # Checks if there are unsaved files.
    def _unsaved_file(self):
        changed = True# insert logic here for checking changed files here...
        if changed:
            result = messagebox.askyesnocancel("Confirm", "Do you want to save your changes before leaving?")
            if result is True: # Save changes.
                # save logic
                self.destroy()
            elif result is False: # Discard changes.
                self.destroy()
            else: # Return to the program.
                pass
        else:
            pass
        return


# run funciton if the file is directly called on
if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()
