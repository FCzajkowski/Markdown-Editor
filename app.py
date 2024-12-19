import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import json

class MarkdownEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown Editor")

        self.settings_file = "settings.json"
        self.settings = self.load_settings()

        self.text_area = tk.Text(root, wrap="word", font=(self.settings.get("font", "Arial"), self.settings.get("font_size", 14)), padx=20, pady=20, bg=self.settings.get("bg_color", "white"), fg=self.settings.get("fg_color", "black"))
        self.text_area.pack(fill="both", expand=True)

        self.file_path = None

        self.status_bar = tk.Label(root, text="Lines: 0", anchor="e")
        self.status_bar.pack(fill="x")

        self.text_area.bind("<KeyRelease>", self.update_line_count)

        self.create_menu()
        self.update_line_count()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Close", accelerator="Ctrl+W", command=self.close_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As", accelerator="Ctrl+Shift+S", command=self.save_as_file)

        menu_bar.add_cascade(label="File", menu=file_menu)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Change Font", command=self.change_font)
        settings_menu.add_command(label="Change Font Size", command=self.change_font_size)
        settings_menu.add_command(label="Change Theme", command=self.change_theme)

        menu_bar.add_cascade(label="Settings", menu=settings_menu)

        self.root.config(menu=menu_bar)
        self.add_shortcuts()

    def add_shortcuts(self):
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-w>", lambda event: self.close_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-S>", lambda event: self.save_as_file())

    def new_file(self):
        if self.confirm_unsaved_changes():
            self.text_area.delete("1.0", tk.END)
            self.file_path = None
            self.root.title("Markdown Editor - New File")
            self.update_line_count()

    def open_file(self):
        if self.confirm_unsaved_changes():
            file_path = filedialog.askopenfilename(filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")])
            if file_path:
                with open(file_path, "r") as file:
                    content = file.read()
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", content)
                self.file_path = file_path
                self.root.title(f"Markdown Editor - {file_path}")
                self.update_line_count()

    def close_file(self):
        if self.confirm_unsaved_changes():
            self.text_area.delete("1.0", tk.END)
            self.file_path = None
            self.root.title("Markdown Editor")
            self.update_line_count()

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w") as file:
                file.write(self.text_area.get("1.0", tk.END).rstrip())
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".md", filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get("1.0", tk.END).rstrip())
            self.file_path = file_path
            self.root.title(f"Markdown Editor - {file_path}")

    def confirm_unsaved_changes(self):
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save changes to your file?")
            if response:  # Yes
                self.save_file()
                return True
            elif response is None:  # Cancel
                return False
        return True

    def change_font(self):
        fonts = ["Arial", "Courier New", "Times New Roman", "Verdana", "Helvetica"]

        def set_font(event):
            selected_font = font_var.get()
            self.settings["font"] = selected_font
            current_size = self.settings.get("font_size", 14)
            self.text_area.config(font=(selected_font, current_size))
            self.save_settings()
            font_window.destroy()

        font_window = tk.Toplevel(self.root)
        font_window.title("Select Font")
        font_var = tk.StringVar(value=self.settings.get("font", "Arial"))

        font_listbox = tk.Listbox(font_window, listvariable=tk.StringVar(value=fonts), height=5, selectmode="single")
        font_listbox.bind("<<ListboxSelect>>", lambda event: font_var.set(font_listbox.get(font_listbox.curselection())))
        font_listbox.pack(fill="both", expand=True)

        select_button = ttk.Button(font_window, text="Select", command=lambda: set_font(None))
        select_button.pack()

    def change_font_size(self):
        sizes = list(range(8, 30))

        def set_size(event):
            selected_size = size_var.get()
            self.settings["font_size"] = selected_size
            current_font = self.settings.get("font", "Arial")
            self.text_area.config(font=(current_font, selected_size))
            self.save_settings()
            size_window.destroy()

        size_window = tk.Toplevel(self.root)
        size_window.title("Select Font Size")
        size_var = tk.IntVar(value=self.settings.get("font_size", 14))

        size_listbox = tk.Listbox(size_window, listvariable=tk.StringVar(value=sizes), height=10, selectmode="single")
        size_listbox.bind("<<ListboxSelect>>", lambda event: size_var.set(int(size_listbox.get(size_listbox.curselection()))))
        size_listbox.pack(fill="both", expand=True)

        select_button = ttk.Button(size_window, text="Select", command=lambda: set_size(None))
        select_button.pack()

    def change_theme(self):
        themes = {
            "Light": {"bg_color": "white", "fg_color": "black"},
            "Dark": {"bg_color": "black", "fg_color": "white"},
            "Solarized": {"bg_color": "#fdf6e3", "fg_color": "#657b83"}
        }

        def set_theme(event):
            selected_theme = theme_var.get()
            self.settings.update(themes[selected_theme])
            self.text_area.config(bg=self.settings["bg_color"], fg=self.settings["fg_color"])
            self.save_settings()
            theme_window.destroy()

        theme_window = tk.Toplevel(self.root)
        theme_window.title("Select Theme")
        theme_var = tk.StringVar(value="Light")

        theme_listbox = tk.Listbox(theme_window, listvariable=tk.StringVar(value=list(themes.keys())), height=5, selectmode="single")
        theme_listbox.bind("<<ListboxSelect>>", lambda event: theme_var.set(theme_listbox.get(theme_listbox.curselection())))
        theme_listbox.pack(fill="both", expand=True)

        select_button = ttk.Button(theme_window, text="Select", command=lambda: set_theme(None))
        select_button.pack()

    def update_line_count(self, event=None):
        lines = int(self.text_area.index("end-1c").split(".")[0])
        self.status_bar.config(text=f"Lines: {lines}")

    def load_settings(self):
        try:
            with open(self.settings_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"font": "Arial", "font_size": 14, "bg_color": "white", "fg_color": "black"}

    def save_settings(self):
        with open(self.settings_file, "w") as file:
            json.dump(self.settings, file)

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownEditor(root)
    root.mainloop()
