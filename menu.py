import tkinter as tk
import customtkinter as ctk
from types import FunctionType as function

class CustomMenuBar:
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.menus = []

        # Create a frame to hold the menu items
        self.menu_frame = ctk.CTkFrame(self.parent, fg_color=self.theme["CTk"]["fg_color"][1], corner_radius=0)
        self.menu_frame.pack(fill=tk.X, side=tk.TOP)

    def add_menu(self, label, items):
        """Add a menu with items to the menu bar"""
        menu = CustomMenu(self.menu_frame, label, items, self.theme, bar=self)
        self.menus.append(menu)
        menu.pack(side=tk.LEFT)

    def show(self):
        """Display the menu bar"""
        self.menu_frame.pack(side=tk.TOP, fill=tk.X)

    def set_menu(self):
        for menu in self.menus:
            menu.hide()


class CustomMenu:
    def __init__(self, parent, label, items, theme, offset_y=5, bar: CustomMenuBar | None = None):
        self.parent = parent
        self.theme = theme
        self.offset_y = offset_y
        self.bar = bar

        # 1) Top‐level container: packed
        self.menu_frame = ctk.CTkFrame(parent,
                                       fg_color=theme["CTk"]["fg_color"][1])

        # 2) Header button: packed inside menu_frame
        self.label_button = ctk.CTkButton(
            self.menu_frame,
            text=label,
            command=self.toggle_menu,
            fg_color="transparent",
            hover_color=theme["CTkButton"]["hover_color"][1],
            font=("Roboto", 10),
            width=20,
            height=15,
            corner_radius=0
        )
        self.label_button.pack(fill=tk.X, padx=5, pady=4)

        # 3) Submenu frame: now a child of `self.parent`, not menu_frame
        self.top = self.parent.winfo_toplevel()
        self.items_frame = ctk.CTkFrame(self.top, corner_radius=0,
                                        fg_color=theme["CTk"]["fg_color"][1])
        self.items_frame.place_forget()

        # 4) Pack each submenu button inside items_frame
        self.menu_widgets = []
        assert self.verify_items(items), "Invalid menu items"

        for text, config in items.items():
            if config["type"] == "checkbox":
                cb = ctk.CTkCheckBox(
                    self.items_frame,
                    text=text,
                    variable=config["variable"],
                    font=("Roboto", 9),
                    command=config.get("command"),
                )
                cb.pack(fill=tk.X, pady=5, padx=5)
                self.menu_widgets.append(cb)

            elif config["type"] == "button":
                btn = ctk.CTkButton(
                    self.items_frame,
                    text=text,
                    command=config["command"],
                    fg_color="transparent",
                    hover_color=self.theme["CTkButton"]["hover_color"][1],
                    font=("Roboto", 9),
                    width=30,
                    height=15,
                    corner_radius=0
                )
                btn.pack(fill=tk.X, pady=5, padx=5)
                self.menu_widgets.append(btn)

    def verify_items(self, items):
        for key, val in items.items():
            if not isinstance(val, dict):
                return False
            _type = val.get("type")
            has_var = "variable" in val
            has_cmd = "command" in val
            if _type == "checkbox":
                if not has_var or not isinstance(val["variable"], tk.Variable):
                    return False
                if has_cmd and not callable(val["command"]):
                    return False
            elif _type == "button":
                if not has_cmd or not callable(val["command"]):
                    return False
                if has_var:
                    return False
            else:
                return False
        return True

    def pack(self, **kwargs):
        """Expose pack on the menu_frame itself."""
        self.menu_frame.pack(**kwargs)

    def toggle_menu(self):
        if self.items_frame.winfo_ismapped():
            self.items_frame.place_forget()
        else:
            self.bar.set_menu()
            self.top.update_idletasks()

            # absolute screen coords of label_button
            abs_x = self.label_button.winfo_rootx()
            abs_y = self.label_button.winfo_rooty() + self.label_button.winfo_height()

            # absolute origin of the toplevel
            top_x = self.top.winfo_rootx()
            top_y = self.top.winfo_rooty()

            # relative coords inside toplevel
            rel_x = abs_x - top_x
            rel_y = abs_y - top_y + self.offset_y

            # place submenu into the toplevel
            self.items_frame.place(x=rel_x, y=rel_y, anchor="nw")

    def hide(self):
        self.items_frame.place_forget()