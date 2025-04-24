import customtkinter as ctk
import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib as mpl
from scipy.stats import lognorm, norm
import os
import utility


theme = os.path.join(".", "assets", "themes", "green.json")

class DistributionApp(ctk.CTk):
    def __init__(self, resolution="900x600"):
        super().__init__()
        ctk.set_default_color_theme(theme)
        utility.load_theme(theme)

        self.title("Distribution Viewer")
        self.resolution = int((resolution.split("x"))[0]), int((resolution.split("x"))[1])
        self.geometry(resolution)

        self.manual_xlim = None
        self.show_mean_line = tk.BooleanVar(value=True)
        self.show_median_line = tk.BooleanVar(value=False)
        self.show_mode_line = tk.BooleanVar(value=False)
        self.show_stddev_lines = tk.BooleanVar(value=False)
        self.show_skewness = tk.BooleanVar(value=False)
        self.show_kurtosis = tk.BooleanVar(value=False)
        self.show_range = tk.BooleanVar(value=False)

        # Main frames
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True)

        self.control_frame = ctk.CTkFrame(self, width=200)
        self.control_frame.pack(side=ctk.TOP, fill=ctk.Y)

        self.create_menu()
        self.create_controls()
        self.create_plot_canvas()
        self.plot_distribution()

    def create_plot_canvas(self):
        # Create figure and canvas once
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def create_menu(self):
        menubar = tk.Menu(self,
                    bg=utility.gray_to_hex(ctk.ThemeManager.theme["CTk"]["fg_color"][0]),
                    fg=utility.gray_to_hex(ctk.ThemeManager.theme["CTk"]["fg_color"][1]))

        axis_menu = tk.Menu(menubar, tearoff=0)
        axis_menu.add_command(label="Set Manual Limits", command=self.set_manual_xlim)
        axis_menu.add_command(label="Reset to Auto", command=self.reset_xlim)

        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_checkbutton(label="Mean", variable=self.show_mean_line, command=self.plot_distribution)
        edit_menu.add_checkbutton(label="Median", variable=self.show_median_line, command=self.plot_distribution)
        edit_menu.add_checkbutton(label="Mode", variable=self.show_mode_line, command=self.plot_distribution)
        edit_menu.add_checkbutton(label="Std Dev Range", variable=self.show_stddev_lines, command=self.plot_distribution)
        edit_menu.add_checkbutton(label="Skewness", variable=self.show_skewness, command=self.plot_distribution)
        edit_menu.add_checkbutton(label="Kurtosis", variable=self.show_kurtosis, command=self.plot_distribution)
        edit_menu.add_checkbutton(label="Range (Min, Max)", variable=self.show_range, command=self.plot_distribution)


        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Show Mean Line", variable=self.show_mean_line, command=self.plot_distribution)
        view_menu.add_checkbutton(label="Show Median Line", variable=self.show_median_line, command=self.plot_distribution)
        view_menu.add_checkbutton(label="Show Mode Line", variable=self.show_mode_line, command=self.plot_distribution)
        view_menu.add_checkbutton(label="Show Std Dev Range", variable=self.show_stddev_lines, command=self.plot_distribution)

        menubar.add_cascade(label="X-Axis Range", menu=axis_menu)
        menubar.add_cascade(label="View", menu=view_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        self.config(menu=menubar)

    def set_manual_xlim(self):
        dialog = ctk.CTkInputDialog(text="Enter x-axis min,max (e.g. -10,10):", title="Set X-Axis Limits")
        result = dialog.get_input()
        if result:
            try:
                xmin, xmax = map(float, result.split(","))
                if xmin >= xmax:
                    raise ValueError("Min must be less than Max")
                self.manual_xlim = (xmin, xmax)
                self.plot_distribution()
            except Exception as e:
                print(f"Invalid input: {e}")

    def reset_xlim(self):
        self.manual_xlim = None
        self.plot_distribution()

    def create_controls(self):
        ctk.CTkLabel(self.control_frame, text="Mean").pack(pady=(10, 0))
        self.mean_var = ctk.DoubleVar(value=0)
        self.mean_slider = ctk.CTkSlider(
            self.control_frame, from_=-10, to=10,
            variable=self.mean_var, command=self.plot_distribution
        )
        self.mean_slider.pack(padx=10, pady=(0, 10))

        ctk.CTkLabel(self.control_frame, text="Standard Deviation").pack(pady=(10, 0))
        self.std_var = ctk.DoubleVar(value=1)
        self.std_slider = ctk.CTkSlider(
            self.control_frame, from_=0.1, to=20,
            variable=self.std_var, command=self.plot_distribution
        )
        self.std_slider.pack(padx=10, pady=(0, 20))

        ctk.CTkLabel(self.control_frame, text="Skewness").pack(pady=5)
        self.skew_var = ctk.IntVar(value=0)
        self.skew_slider = ctk.CTkSlider(self.control_frame, from_=-10, to=10, variable=self.skew_var, command=self.plot_distribution)
        self.skew_slider.pack(padx=10)

        ctk.CTkButton(self.control_frame, text="Update", command=self.plot_distribution).pack(pady=10)


    def plot_distribution(self, *args):
        self.ax.clear()

        mean = self.mean_var.get()
        std = self.std_var.get()
        skew = self.skew_var.get()  # Get the skewness from the slider

        x = np.linspace(mean - 4 * std, mean + 4 * std, 400)
        y = norm.pdf(x, loc=mean, scale=std)

        if std < 0:
            raise ValueError("Standard Deviation cannot be negative")

        line_color = mpl.rcParams["lines.color"]
        self.ax.plot(x, y, label='Distribution', color=line_color)

        # Add mean line
        if self.show_mean_line.get():
            self.ax.axvline(x=mean, color='r', linestyle='--', label='Mean')

        # Show other statistics as needed
        if self.show_median_line.get():
            median = np.median(x)
            self.ax.axvline(x=median, color='g', linestyle='-.', label='Median')

        if self.show_mode_line.get():
            mode = mean 
            self.ax.axvline(x=mode, color='b', linestyle=':', label='Mode')

        if self.show_stddev_lines.get():
            self.ax.axvline(x=mean - std, color='purple', linestyle='--', label='-1σ')
            self.ax.axvline(x=mean + std, color='purple', linestyle='--', label='+1σ')
            self.ax.axvline(x=mean - std*2, color='purple', linestyle='--', label='-2σ')
            self.ax.axvline(x=mean + std*2, color='purple', linestyle='--', label='+2σ')
            self.ax.axvline(x=mean - std*3, color='purple', linestyle='--', label='-3σ')
            self.ax.axvline(x=mean + std*3, color='purple', linestyle='--', label='+3σ')


        if self.show_skewness.get():
            self.ax.text(mean, 0.3, f"Skewness={skew}", horizontalalignment='center', color='orange')

        if self.show_kurtosis.get():
            kurt = 3  # Normal distribution kurtosis is 3 (simplified)
            self.ax.text(mean, 0.3, f"Kurtosis={kurt}", horizontalalignment='center', color='brown')

        if self.show_range.get():
            self.ax.axvline(x=np.min(x), color='purple', linestyle='-', label=f'Min={np.min(x):.2f}')
            self.ax.axvline(x=np.max(x), color='purple', linestyle='-', label=f'Max={np.max(x):.2f}')

        self.ax.set_title(f"Distribution(mean={mean}, std={std}, skew={skew})")
        self.ax.grid(True)

        # Auto x-limits based on data
        if self.manual_xlim:
            self.ax.set_xlim(*self.manual_xlim)
        else:
            self.ax.set_xlim(x[0], x[-1])

        self.ax.set_ylim(0, 0.5)
        self.canvas.draw()



# Run the app
if __name__ == "__main__":
    app = DistributionApp()
    app.mainloop()
