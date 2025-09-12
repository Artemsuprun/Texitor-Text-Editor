# this program is a text editor for the user.

# library imports
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox


# the main page of the app.
class MainPage(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        # member variables
        self.chunk_size = 1024 * 8 # 8KB chunk size for reading and writing files.
        self.tabs = [] # keeps track of the tabs
        self.parent = parent

        # setting up the frame's grid layout.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1, minsize=200)

        # list of files
        file_frame = tk.Frame(self, width=140, bg="lightgrey")
        file_frame.grid(row=0, column=0, sticky="ns")
        file_frame.rowconfigure(1, weight=1)
        file_frame.columnconfigure(0, weight=1, minsize=100)

        settings_btn = tk.Button(file_frame, text="Settings", command=self._settings_layout)
        settings_btn.grid(row=0, column=0, sticky="new", padx=5, pady=5)
        ttk.Separator(file_frame, orient="horizontal").grid(row=1, column=0, sticky="new")
        
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
        open_button = tk.Button(start_frame, text="Open", command=self._open_file)
        open_button.grid(row=2, column=0, sticky="new", padx=10, pady=3)
        new_button = tk.Button(start_frame, text="New", command=self._add_tab)
        new_button.grid(row=3, column=0, sticky="new", padx=10, pady=(3, 6))

        # Text frames using tab control
        self.tab_control = ttk.Notebook(edit_frame)
        self.tab_control.grid(row=0, column=0, sticky="nsew")
        self.tab_control.rowconfigure(0, weight=1)
        self.tab_control.columnconfigure(0, weight=1)
        self.tab_control.grid_remove()

        self.tab_control.bind("<<NotebookTabChanged>>", self._cursor_update)

        # Add a small label at the bottom.
        status_frame = tk.Frame(self, height=25)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        status_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        self.cursor_pos = tk.Label(status_frame, text="", bd=1)
        self.cursor_pos.grid(row=1, column=0, sticky="e")
        return
    
    # Sets up the settings window.
    def _settings_layout(self):
        settings = tk.Toplevel(self.parent)
        settings.title("Settings")
        settings.geometry("400x500")

        settings.lift()
        settings.attributes("-topmost", True)
        settings.focus_set()
        return
    
    # This should be self-explanatory...
    def _switch_tab(self, event):
        return "break"

    def _switch_tab_backward(self, event):
        return "break"


    # Updates the label that displays the cursors position.
    def _cursor_update(self, event):
        if self.tab_control.select(): # check if a tab exists.
            try:
                # get the cursors position and update the label.
                text_widget = self.tabs[self.tab_control.index(self.tab_control.select())]
                line, col = text_widget.index(tk.INSERT).split(".")
                self.cursor_pos.config(text=f"Line: {line} | Column: {int(col)+1}")
            except:
                # display an empty label.
                self.cursor_pos.config(text="")
        else: # no tab is selected.
            self.cursor_pos.config(text="")
        return


    # Properly removes tabs.
    def _remove_tab_event(self, event):
        self._remove_tab()
        return "break"

    def _remove_tab(self, index=None):
        result = None # return value.
        if self.tab_control.select(): # check if a tab exists.
            if index is None:
                idx = self.tab_control.select()
            elif isinstance(index, int):
                idx = self.tab_control.tabs()[index]
            self.tabs.pop(self.tab_control.index(idx))
            self.tab_control.forget(idx)
            result = True

            # hide the tab control if no tabs exist.
            if not self.tab_control.select(): # check if any tabs exists.
                self.tab_control.grid_remove()
        else:
            result = False
        
        return result


    # Properly adds tabs to the program (new file creation).
    def _add_tab_event(self, event):
        self._add_tab()
        return "break"

    def _add_tab(self, path="untitled"):
        # make the tab control visible if it is hidden.
        if not self.tab_control.select(): # check if a tab exists.
            self.tab_control.grid(row=0, column=0, sticky="nsew")
        
        # create frame for the tab.
        tab_frame = tk.Frame(self.tab_control)
        tab_frame.rowconfigure(0, weight=1)
        tab_frame.columnconfigure(0, weight=1)

        # add a new text widget to the tab.
        text_widget = tk.Text(tab_frame, wrap="none", undo=True, autoseparators=True, bd=0)
        text_widget.grid(row=0, column=0, sticky="nsew")
        self.tabs.append(text_widget)

        # adds a scrollbar for the text box.
        Vscrollbar = tk.Scrollbar(tab_frame, orient="vertical", command=text_widget.yview)
        Vscrollbar.grid(row=0, column=1, sticky="ns")
        text_widget.config(yscrollcommand=Vscrollbar.set)

        self.tab_control.add(tab_frame, text=path)

        # update key bindings for the text widget.
        text_widget.bind("<Control-y>", self.parent._do_nothing)
        text_widget.bind("<Control-o>", self._open_file_event)
        text_widget.bind("<KeyRelease>", self._cursor_update)
        text_widget.bind("<ButtonRelease>", self._cursor_update)

        # switch to the new tab.
        self.tab_control.select(tab_frame)

        # focus on the text widget.
        text_widget.focus_set()

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

    def _save_as_file():
        pass


    # Saves the currently selected file.
    def _save_file_event(self, event):
        self._save_file()
        return "break"

    def _save_file(self):
        file_path = None
        # Check if the currently selected file has a path, make one if not.
        if self.tab_control.select(): # Check if a tab exists
            file_path = self.tab_control.tab(self.tab_control.select(), "text")
            if file_path == "untitled":
                file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir="/", title="Save File As", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
                if file_path:
                    # Update the tab's text
                    self.tab_control.tab(self.tab_control.select(), text=file_path)
        
        result = None # return value
        # If the file_path is valid, save it.
        if file_path:
            try:
                with open(file_path, "w") as file:
                    # Obtain the text widget.
                    text_widget = self.tabs[self.tab_control.index(self.tab_control.select)]
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
        # insert logic for checking changed files here...

        #if changed:
        result = messagebox.askyesnocancel("Confirm", "Do you want to save your changes before leaving?")
        if result is True: # Save changes.
            # save logic
            self.parent.destroy()
        elif result is False: # Discard changes.
            self.parent.destroy()
        else: # Return to the program.
            pass
        #else:
        return

# Class form of the app.
class TextEditor(tk.Tk):
    def __init__(self, *args, **kwargs):
        # Properly initializing the parent constructor to start.
        tk.Tk.__init__(self, *args, **kwargs)
        # Title of the main page.
        self.title("Texitor ~ A Simple Text Editor")
        # Setting up the window size of the app.
        self.geometry("800x600")
        # Setting up the grid layout.
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # contain the frames.
        self.frames = {}
        for f in (MainPage,): # might add more frames for other options later on.
            frame = f(self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self._show_frame(MainPage)

        # binding keys to the main window
        self.bind("<Control-c>", self._copy_text)
        self.bind("<Control-Shift-Z>", self._redo_text)
        self.bind("<Control-y>", self._do_nothing)
        self.bind("<Control-s>", self.frames[MainPage]._save_file_event)
        self.bind("<Control-Shift-S>", self.frames[MainPage]._save_as_file_event)
        self.bind("<Control-n>", self.frames[MainPage]._add_tab_event)
        self.bind("<Control-o>", self.frames[MainPage]._open_file_event)
        self.bind("<Control-Shift-N>", self.frames[MainPage]._remove_tab_event)
        self.bind("<Control-Tab>", self.frames[MainPage]._switch_tab)
        self.bind("<Control-Shift-Tab>", self.frames[MainPage]._switch_tab_backward)

        # set up the menu options
        self._menu_setup()

        # focus on the window
        self.focus_set()

        # ensure files are saved if needed.
        self.protocol("WM_DELETE_WINDOW", self.frames[MainPage]._unsaved_file)
        return

    # A method of switching view frames.
    def _show_frame(self, f):
        frame = self.frames[f]
        frame.tkraise()
        return
    
    # sets up the menu tab on the main window.
    def _menu_setup(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        filemenu = tk.Menu(menu, tearoff=False)
        filemenu.add_command(label="New", command=self.frames[MainPage]._add_tab)
        filemenu.add_command(label="Open...", command=self.frames[MainPage]._open_file)
        filemenu.add_command(label="Save", command=self.frames[MainPage]._save_file)
        filemenu.add_command(label="Save As...", command=self.frames[MainPage]._save_as_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.frames[MainPage]._unsaved_file)
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



# run funciton if the file is directly called on
if __name__ == "__main__":
    app = TextEditor()
    app.mainloop()
