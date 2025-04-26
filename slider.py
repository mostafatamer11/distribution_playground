import customtkinter as ctk

class Slider(ctk.CTkFrame):
    def __init__(self, master, label_text="Label", from_=0, to=100, step=1, command=None, variable=None, **kwargs):
        super().__init__(master, **kwargs)

        self.ready = False  # <-- Add this line FIRST

        self.from_ = from_
        self.to = to
        self.step = step
        self.command = command
        self.hold_job = None

        # --- create UI elements ---
        self.label = ctk.CTkLabel(self, text=label_text, font=("Arial", 12))
        self.label.grid(row=0, column=0, columnspan=4, pady=(0, 5))

        self.slider = ctk.CTkSlider(self, from_=self.from_, to=self.to, command=self.slider_changed, variable=variable)
        self.slider.grid(row=1, column=0, columnspan=4, sticky="ew", padx=5)

        self.minus_button = ctk.CTkButton(self, text="-", width=25, height=25)
        self.minus_button.grid(row=2, column=0, padx=(5, 2), pady=5)

        self.entry = ctk.CTkEntry(self, width=60, height=25)
        self.entry.grid(row=2, column=1, columnspan=2, pady=5)
        self.entry.bind("<Return>", self.entry_changed)

        self.plus_button = ctk.CTkButton(self, text="+", width=25, height=25)
        self.plus_button.grid(row=2, column=3, padx=(2, 5), pady=5)

        # --- bind buttons for hold ---
        self.minus_button.bind("<ButtonPress-1>", lambda e: self.start_hold(self.decrement))
        self.minus_button.bind("<ButtonRelease-1>", lambda e: self.stop_hold())
        self.plus_button.bind("<ButtonPress-1>", lambda e: self.start_hold(self.increment))
        self.plus_button.bind("<ButtonRelease-1>", lambda e: self.stop_hold())

        if not variable:
            self.set_value((self.from_ + self.to) / 2)
        else:
            self.set_value(variable.get())

        self.ready = True  # <-- Set ready after setup is finished

    def set_value(self, value, trigger_command=True):
        value = max(min(value, self.to), self.from_)
        self.slider.set(value)
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{value:.2f}")

        if self.command and trigger_command and self.ready:
            self.command(value)

    def slider_changed(self, value):
        self.set_value(value)

    def entry_changed(self, event=None):
        try:
            value = float(self.entry.get())
            self.set_value(value)
        except ValueError:
            pass

    def increment(self):
        self.set_value(self.slider.get() + self.step)

    def decrement(self):
        self.set_value(self.slider.get() - self.step)

    def start_hold(self, func):
        func()  # Run once immediately
        self.hold_job = self.after(150, self._repeat_hold, func)

    def _repeat_hold(self, func):
        func()
        self.hold_job = self.after(100, self._repeat_hold, func)

    def stop_hold(self):
        if self.hold_job:
            self.after_cancel(self.hold_job)
            self.hold_job = None

