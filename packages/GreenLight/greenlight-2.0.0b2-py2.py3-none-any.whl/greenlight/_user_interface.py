"""
greenlight/greenlight/_user_interface.py
Copyright (c) 2025 David Katzin, Wageningen Research Foundation
SPDX-License-Identifier: BSD-3-Clause-Clear
https://github.com/davkat1/GreenLight

Sets up the GUI used by greenlight/greenlight/main.py
"""

import datetime
import os
import tkinter as tk
from pathlib import Path, PurePath
from tkinter import filedialog

from tkcalendar import DateEntry


class MainPrompt(tk.Tk):
    def __init__(self, models_dir=""):
        super().__init__()

        # Force the prompt to appear in front
        self.lift()
        self.attributes("-topmost", True)

        # Set the size and location of the prompt
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = screen_width // 2
        height = screen_height
        self.geometry(f"1200x1200+{screen_width // 2 - width // 2}+{screen_height // 2 - height // 2}")

        self.result = {}  # dict containing the result (input values) of running the interface

        self.title("Run a GreenLight simulation")

        # Check if current file is inside a folder which indicates it is called from an installed package
        file_path = PurePath(__file__)
        site_indicators = {"site-packages", "dist-packages", ".venv", "venv", ".egg", ".eggs"}
        is_installed = any(part in site_indicators for part in file_path.parts)

        if is_installed:
            default_base_path = PurePath(Path.cwd())
        else:
            default_base_path = os.path.abspath(models_dir)

        default_model_file = os.path.abspath(
            os.path.join(models_dir, "katzin_2021", "definition", "main_katzin_2021.json")
        )
        default_input_data_file = os.path.abspath(
            os.path.join(models_dir, "katzin_2021", "input_data", "test_data", "Bleiswijk_from_20091019_151500.csv")
        )

        # Determine location for default output path
        if is_installed:  # Save output (by default) in cwd/output
            output_path = os.path.join(PurePath(Path.cwd()), "output")
        else:
            # Save the output (by default) in the models directory
            output_path = os.path.join(models_dir, "katzin_2021", "output")

        if not os.path.exists(output_path):  # If output_path doesn't exist, create it
            os.makedirs(output_path)

        # Set default output directory
        default_output_file = os.path.abspath(
            os.path.join(
                output_path,
                "greenlight_output_" + datetime.datetime.now().strftime("%Y%m%d_%H%M") + ".csv",
            )
        )

        self.base_path = tk.StringVar(value=default_base_path)
        self.model_file = tk.StringVar(value=default_model_file)
        self.input_data_file = tk.StringVar(value=default_input_data_file)

        self.start_date_picker = None
        self.end_date_picker = None

        self.modifications_box = None

        self.save_location = tk.StringVar(value=default_output_file)

        # Set default text modification
        hps_file = os.path.abspath(
            os.path.join(models_dir, os.path.join("katzin_2021", "definition", "lamp_hps_katzin_2021.json"))
        )
        self.default_mod = os.path.relpath(hps_file, default_base_path)

        # Create a scrollable Frame
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        v_scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = tk.Scrollbar(container, orient="horizontal", command=canvas.xview)

        self.scrollable_frame = tk.Frame(canvas)

        # Update scroll region when frame resizes
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Connect scrollbars
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Build widgets
        self.create_widgets()

        # Call the widget builder
        self.create_widgets()

    def create_widgets(self):
        text_font_size = 10  # Default is 10
        # Title
        row = 0
        tk.Label(self.scrollable_frame, text="Run a greenlight simulation", font=("Helvetica", 16, "bold")).grid(
            row=row, column=0, columnspan=1, padx=5, pady=5
        )
        row += 1

        tk.Label(
            self.scrollable_frame,
            text="In order to run a simulation, the following choices must be made:",
            font=("Helvetica", text_font_size),
            anchor="w",
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        # Explanation on base path
        tk.Label(
            self.scrollable_frame, text="Model base path", font=("Helvetica", text_font_size, "bold"), anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        tk.Label(
            self.scrollable_frame,
            text=(
                "This is a location on the local machine that is used for logging purposes. "
                "When logging which files were read and written, they are logged relative to this path.\n"
                "Typically this is a project folder, that the input and output folder are located within it."
            ),
            font=("Helvetica", text_font_size),
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, sticky="w", columnspan=2, padx=5, pady=5)
        row += 1

        # Choose base path
        self._file_row("Select base path:", self.base_path, row, "browse_dir")
        row += 1

        # Explanation on model definition file
        tk.Label(
            self.scrollable_frame, text="Model definition file", font=("Helvetica", text_font_size, "bold"), anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        tk.Label(
            self.scrollable_frame,
            text=(
                'This is a JSON file, typically with a "processing_order" node, '
                "which defines the model structure. "
                "The current default defines a model as in Katzin 2021 (PhD thesis, Chapter 4).\n"
                "This represents a modern high-tech greenhouse with LED lamps."
            ),
            font=("Helvetica", text_font_size),
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, sticky="w", columnspan=2, padx=5, pady=5)
        row += 1

        # Choose model definition file
        self._file_row("Select model definition file:", self.model_file, row, "browse_file")
        row += 1

        # Explanation on input data file
        tk.Label(
            self.scrollable_frame, text="Input data file", font=("Helvetica", text_font_size, "bold"), anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        tk.Label(
            self.scrollable_frame,
            text=(
                "Input data can be added, for example weather data.\n"
                "This can either be a formatted CSV containing data, or a CSV file from EnergyPlus.\n"
                "You can get such files by downloading weather data in EPW format from https://energyplus.net/weather\n"
                "Then installing EnergyPlus (https://energyplus.net/downloads),\n"
                'and using the "Weather statistics and conversion tool" to convert the EPW to CSV.\n '
                "By default a file containing weather data from Bleiswijk, the Netherlands in 2009-2010 is used.\n"
                "If no file is loaded, constant values for the weather inputs are used."
            ),
            font=("Helvetica", text_font_size),
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, sticky="w", columnspan=2, padx=5, pady=5)
        row += 1

        # Choose input data file
        self._file_row("Select input data file:", self.input_data_file, row, "browse_file")
        row += 1

        # Explanation on time range
        tk.Label(
            self.scrollable_frame, text="Simulation date range", font=("Helvetica", text_font_size, "bold"), anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        tk.Label(
            self.scrollable_frame,
            text=(
                "If using a CSV file from EnergyPlus, The chosen weather file will be formatted to describe\n"
                "a chosen growing season, according to the selected date range.\n"
                "Note that since EnergyPlus uses standardized years, the particular choice of year doesn't\n"
                "have an influence. Leap years will be ignored (February 29 will not be included).\n"
                "When using formatted CSV input data (like in the default setting),\n"
                "the input data will always be read from the beginning of the data.\n"
                "The length of the data read is the difference between the start date and the end date.\n"
                "In other words, when reading formatted data the only thing that matters is the\n"
                "difference between the start and end date, not their actual values."
            ),
            font=("Helvetica", text_font_size),
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, sticky="w", columnspan=2, padx=5, pady=5)
        row += 1

        # Start and End Dates
        default_start = datetime.date(2009, 10, 19)
        default_end = datetime.date(2009, 10, 22)

        tk.Label(self.scrollable_frame, text="Start Date:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.start_date_picker = DateEntry(
            self.scrollable_frame, width=50, year=default_start.year, month=default_start.month, day=default_start.day
        )
        self.start_date_picker.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        tk.Label(self.scrollable_frame, text="End Date:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        self.end_date_picker = DateEntry(
            self.scrollable_frame, width=50, year=default_end.year, month=default_end.month, day=default_end.day
        )
        self.end_date_picker.grid(row=row, column=1, padx=5, pady=5)
        row += 1

        # Explanation on custom modifications
        tk.Label(
            self.scrollable_frame, text="Custom modifications", font=("Helvetica", text_font_size, "bold"), anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        tk.Label(
            self.scrollable_frame,
            text=(
                "This text box allows to manually enter custom modifications that will be read by greenlight. "
                "For example, the text currently in the box will have the model load a file\n"
                "that changes the lamp parameters from LED to default HPS lamp values. "
                "Remove this text if you want to keep the default lamps values - LED lamps"
            ),
            font=("Helvetica", text_font_size),
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, sticky="w", columnspan=2, padx=5, pady=5)
        row += 1
        self.modifications_box = tk.Text(self.scrollable_frame, width=40, height=4)
        self.modifications_box.grid(row=row, column=0, columnspan=3, padx=5, pady=(0, 10))
        self.modifications_box.insert("1.0", self.default_mod)
        row += 1

        # Output file
        tk.Label(
            self.scrollable_frame, text="Output file location", font=("Helvetica", text_font_size, "bold"), anchor="w"
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        tk.Label(
            self.scrollable_frame,
            text=(
                "Choose where the simulation results should be stored. The simulation is stored in CSV format, "
                "some log files are also generated in the same folder as the chosen output"
            ),
            font=("Helvetica", text_font_size),
            anchor="w",
            justify="left",
        ).grid(row=row, column=0, sticky="w", columnspan=2, padx=5, pady=5)
        row += 1

        # Choose save location
        self._file_row("Save as:", self.save_location, row, "save_file")
        row += 1

        # Buttons
        tk.Label(
            self.scrollable_frame,
            text="Press OK to run the simulation",
            font=("Helvetica", text_font_size, "bold"),
            anchor="w",
        ).grid(row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5)
        row += 1

        button_frame = tk.Frame(self.scrollable_frame)
        button_frame.grid(row=row, columnspan=2, pady=20)
        row = row + 1

        tk.Button(button_frame, text="OK", width=15, command=self.on_ok).grid(
            row=row, column=0, sticky="w", columnspan=1, padx=5, pady=5
        )
        tk.Button(button_frame, text="Cancel", width=15, command=self.on_cancel).grid(
            row=row, column=1, sticky="w", columnspan=1, padx=5, pady=5
        )

    def _file_row(self, label, var, row, dialog_type="browse_file"):
        """
        File input label and button. dialog_type can be one of the following:
            "browse_file": browse for a file
            "save_file": save a file
            "browse_dir": browse for a directory
        """
        tk.Label(self.scrollable_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(self.scrollable_frame, textvariable=var, width=30).grid(row=row, column=1, padx=5, pady=5)
        tk.Button(self.scrollable_frame, text="Browse...", command=lambda: self.browse_file(var, dialog_type)).grid(
            row=row, column=2, padx=5, pady=5
        )

    @staticmethod
    def browse_file(var, dialog_type="browse_file"):
        if dialog_type == "save_file":
            filename = filedialog.asksaveasfilename(
                initialdir=os.path.join(var.get(), ".."),
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
        elif dialog_type == "browse_dir":
            filename = filedialog.askdirectory(initialdir=os.path.join(var.get(), ".."))
        else:
            filename = filedialog.askopenfilename(initialdir=os.path.join(var.get(), ".."))

        if filename:
            var.set(filename)

    def on_ok(self):
        self.result = {
            "base_path": os.path.abspath(self.base_path.get()),
            "model": os.path.abspath(self.model_file.get()),
            "input_data": os.path.abspath(self.input_data_file.get()),
            "start_date": self.start_date_picker.get_date(),
            "end_date": self.end_date_picker.get_date(),
            "mods": self.modifications_box.get("1.0", "end-1c"),
            "output_file": os.path.abspath(self.save_location.get()),
        }
        self.destroy()

    def on_cancel(self):
        self.destroy()
