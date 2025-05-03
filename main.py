import customtkinter as ctk
import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib as mpl
import os
import utility
import menu
import pdf
from slider import Slider


theme = utility.resource_path(os.path.join("assets", "themes", "green.json"))

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

        self.std_var = ctk.DoubleVar(value=1)
        self.mean_var = ctk.DoubleVar(value=0)
        self.skew_var = ctk.IntVar(value=0)
        self.kurt_var = ctk.IntVar(value=0)

        # Main frames
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True)

        self.create_menu()
        self.control_frame = ctk.CTkFrame(self, width=200)
        self.control_frame.pack(side=ctk.TOP, fill=ctk.Y)

        self.x = np.linspace(self.mean_var.get() - 4 * self.std_var.get(),
                        self.mean_var.get() + 4 * self.std_var.get(), 40000)
        self.f = pdf.EditablePDF(
            mean=self.mean_var.get(),
            std=self.std_var.get(),
            skew=self.skew_var.get(),
            kurtosis=self.kurt_var.get(),
            x=self.x
        )

        self.create_controls()
        self.create_plot_canvas()
        self.plot_distribution()

    def create_plot_canvas(self):
        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def create_menu(self):
        self.menubar = menu.CustomMenuBar(self, {
            "CTk": {
                "fg_color": ["gray92", "gray34"]
            },
            "CTkButton": {
                "fg_color": ["#2CC985", "#2FA572"],
                "hover_color": ["#0C955A", "#106A43"]
            }
        })

        self.menubar.add_menu("Axis",
            {
                "Set Manual Limits": {"command": self.set_manual_xlim, "type": "button"},
                "Reset to Auto": {"command": self.reset_xlim, "type": "button"},
            })

        self.menubar.add_menu("View",
            {
                "Show Mean Line": {"variable": self.show_mean_line, "type": "checkbox", "command": self.plot_distribution},
                "Show Median Line": {"variable": self.show_median_line, "type": "checkbox", "command": self.plot_distribution},
                "Show Mode Line": {"variable": self.show_mode_line, "type": "checkbox", "command": self.plot_distribution},
                "Show Std Dev Range": {"variable": self.show_stddev_lines, "type": "checkbox", "command": self.plot_distribution},
        })

        self.menubar.show()

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
        self.layout = 2, 2
        self.mean_slider = Slider(
            self.control_frame, label_text="Mean", from_=-10, to=10,
            variable=self.mean_var, command=self.plot_distribution
        )
        self.mean_slider.grid(padx=10, pady=(0, 20), row=0, column=0)

        self.std_slider = Slider(
            self.control_frame, label_text="Standard Deviation", from_=0.1, to=20,
            variable=self.std_var, command=self.plot_distribution
        )
        self.std_slider.grid(padx=10, pady=(0, 20), row=1, column=0)

        self.skew_slider = Slider(self.control_frame, label_text="Skewness", from_=-10, to=10, variable=self.skew_var, command=self.plot_distribution)
        self.skew_slider.grid(padx=10, pady=(0, 20), row=0, column=1)

        self.kurt_slider = Slider(self.control_frame, label_text="Kurtosis", from_=-10, to=10, variable=self.kurt_var, command=self.plot_distribution)
        self.kurt_slider.grid(padx=10, pady=(0, 20), row=1, column=1)

    def plot_distribution(self, *args):
        self.ax.clear()

        mean = self.mean_var.get()
        std = self.std_var.get()
        skew = self.skew_var.get()
        kurt = self.kurt_var.get()

        if std < 0:
            raise ValueError("Standard Deviation cannot be negative")

        self.f.set_kurtosis(kurt)
        self.f.set_skew(skew)
        self.f.set_mean(mean)
        self.f.set_std(std)

        summ:tuple = self.f.plot
        self.x = summ[0]
        self.y = summ[1]
        self.mean_var.set(summ[2])
        self.std_var.set(summ[3])
        self.skew_var.set(summ[4])
        self.kurt_var.set(summ[5])

        line_color = mpl.rcParams["lines.color"]
        self.ax.plot(self.x, self.y, label="Distribution", color=line_color)

        if self.show_mean_line.get():
            self.ax.axvline(x=mean, color="r", linestyle="--", label="Mean")

        if self.show_stddev_lines.get():
            self.ax.axvline(x=mean - std, color="purple", linestyle="--", label="-1σ")
            self.ax.axvline(x=mean + std, color="purple", linestyle="--", label="+1σ")
            self.ax.axvline(x=mean - std*2, color="purple", linestyle="--", label="-2σ")
            self.ax.axvline(x=mean + std*2, color="purple", linestyle="--", label="+2σ")
            self.ax.axvline(x=mean - std*3, color="purple", linestyle="--", label="-3σ")
            self.ax.axvline(x=mean + std*3, color="purple", linestyle="--", label="+3σ")

        self.ax.set_title(f"Distribution(mean={mean:.2f}, std={std:.2f}, skew={skew:.2f}, kurt={kurt:.2f})")
        self.ax.grid(True)

        if self.manual_xlim:
            self.ax.set_xlim(*self.manual_xlim)
        else:
            self.ax.set_xlim(self.x[0], self.x[-1])

        self.ax.set_ylim(0, 0.5)
        self.canvas.draw()



# Run the app
if __name__ == "__main__":
    app = DistributionApp()
    app.mainloop()
