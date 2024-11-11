import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, Toplevel
import json
import os
from datetime import datetime
import graphviz
from PIL import Image, ImageTk

# Constants for file paths
DATA_FILE = 'plant_genetics.json'
GROW_LOG_FILE = 'grow_log.json'
CONFIG_FILE = 'config.json'

# Default colors for the legend
DEFAULT_COLORS = {
    "Owned & Parent Strain": "#32CD32",
    "Parent Strain": "#FFD700",
    "Owned Strain": "#1E90FF",
    "Seed Start Strain": "#00FFFF",
    "Clone Strain": "#FF69B4",  # Color for Clone Strain
    "Not Owned Strain": "#A9A9A9"
}

# Constants for styling
BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"
BUTTON_FG_COLOR = "black"  # Define BUTTON_FG_COLOR
BUTTON_BG_COLOR = "white"  # Define BUTTON_BG_COLOR

class ScrollableFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        canvas = tk.Canvas(self, bg=BACKGROUND_COLOR)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class GrowLogApp:
    def __init__(self, parent, plant_genetics, main_app):
        self.parent = parent
        self.plant_genetics = plant_genetics
        self.main_app = main_app  # Reference to the main app
        self.grow_log = self.load_grow_log_data()

        # Main Frame
        self.main_frame = tk.Frame(self.parent, bg=BACKGROUND_COLOR)
        self.main_frame.pack(fill='both', expand=True)

        # Left and Right Frames
        self.left_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.left_frame.pack(side='left', fill='y')

        self.right_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR)
        self.right_frame.pack(side='left', fill='both', expand=True)

        # Strain Selection Frame
        self.selection_frame = tk.Frame(self.left_frame, bg=BACKGROUND_COLOR)
        self.selection_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(self.selection_frame, text="Select Strain:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(side="left")

        self.strain_var = tk.StringVar()
        strain_options = ["Select Strain"] + sorted(self.plant_genetics.keys(), key=lambda x: x.lower())
        self.strain_dropdown = tk.OptionMenu(self.selection_frame, self.strain_var, *strain_options, command=self.on_strain_select)
        self.strain_dropdown.config(bg="white", fg="black", font=("Helvetica", 12))
        self.strain_dropdown.pack(side="left", padx=10)
        self.strain_var.set("Select Strain")

        # Plant Details and Clones Frame
        self.details_frame = tk.Frame(self.left_frame, bg=BACKGROUND_COLOR)
        self.details_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Title
        tk.Label(self.right_frame, text="Grow Log", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Add Log Entry Button
        btn_add_log = tk.Button(self.right_frame, text="Add Log Entry", command=self.add_log_entry,
                                bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                activebackground="lightgrey", activeforeground="black")
        btn_add_log.pack(pady=10)

        # Log Entries Frame with ScrollableFrame
        self.log_scrollable_frame = ScrollableFrame(self.right_frame)
        self.log_scrollable_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Display existing log entries
        self.display_log_entries()

    def on_strain_select(self, value):
        # Clear details_frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        if value == "Select Strain":
            return

        # Display plant details and clones
        self.show_plant_details(value)

        # Filter log entries based on selected strain
        self.display_log_entries()

    def load_grow_log_data(self):
        if os.path.exists(GROW_LOG_FILE):
            try:
                with open(GROW_LOG_FILE, 'r') as file:
                    data = json.load(file)
                    return data
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode grow_log.json. Starting with empty grow log.")
                return []
        else:
            return []

    def save_grow_log_data(self):
        with open(GROW_LOG_FILE, 'w') as file:
            json.dump(self.grow_log, file, indent=4)

    def add_log_entry(self):
        # Create a new Toplevel window (popup)
        entry_window = Toplevel(self.parent)
        entry_window.title("Add Grow Log Entry")
        entry_window.geometry("500x600")
        entry_window.configure(bg=BACKGROUND_COLOR)

        # Entry Fields
        tk.Label(entry_window, text="Date (YYYY-MM-DD):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_date = tk.Entry(entry_window, font=("Helvetica", 12))
        entry_date.pack(pady=5)
        entry_date.insert(0, datetime.now().strftime('%Y-%m-%d'))

        tk.Label(entry_window, text="Activity Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        activity_var = tk.StringVar()
        activity_options = ["Watered", "Fed Nutrients", "Pruned", "Harvested", "Cloned", "Transplanted", "Mom", "Other"]
        activity_menu = tk.OptionMenu(entry_window, activity_var, *activity_options)
        activity_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        activity_menu.pack(pady=5)
        activity_var.set("Watered")

        tk.Label(entry_window, text="Strain:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        strain_var = tk.StringVar()
        strain_options = ["Select Strain"] + sorted(self.plant_genetics.keys(), key=lambda x: x.lower())
        strain_menu = tk.OptionMenu(entry_window, strain_var, *strain_options)
        strain_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        strain_menu.pack(pady=5)
        strain_var.set("Select Strain")

        tk.Label(entry_window, text="Notes:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_notes = tk.Entry(entry_window, font=("Helvetica", 12))
        entry_notes.pack(pady=5)
        entry_notes.insert(0, '')

        tk.Label(entry_window, text="Status:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        status_var = tk.StringVar()
        status_options = ["Seedling", "Vegetative", "Flowering", "Harvested", "Cloned", "Other"]
        status_menu = tk.OptionMenu(entry_window, status_var, *status_options)
        status_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        status_menu.pack(pady=5)
        status_var.set("Vegetative")

        # Save Button
        btn_save_log = tk.Button(entry_window, text="Save Entry", command=lambda: self.save_log_entry(entry_date.get().strip(),
                                                                                                       activity_var.get().strip(),
                                                                                                       strain_var.get().strip(),
                                                                                                       entry_notes.get().strip(),
                                                                                                       status_var.get().strip(),
                                                                                                       entry_window),
                                 bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                 activebackground="lightgrey", activeforeground="black")
        btn_save_log.pack(pady=20)

    def save_log_entry(self, date, activity, strain, notes, status, window):
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        if not activity:
            messagebox.showwarning("Incomplete Data", "Please select an activity type.")
            return

        if not strain or strain not in self.plant_genetics:
            messagebox.showwarning("Invalid Strain", "Please select a valid strain.")
            return

        # Add new log entry
        self.grow_log.append({
            "date": date,
            "activity_type": activity,
            "strain": strain,
            "notes": notes,
            "status": status
        })
        self.save_grow_log_data()
        self.display_log_entries()
        messagebox.showinfo("Success", "Grow log entry added successfully!")
        window.destroy()

    def display_log_entries(self):
        # Clear existing entries
        for widget in self.log_scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        filtered_log = self.grow_log

        if self.strain_var.get() != "Select Strain":
            # Filter log entries based on selected strain
            filtered_log = [entry for entry in self.grow_log if entry['strain'] == self.strain_var.get()]

        if not filtered_log:
            tk.Label(self.log_scrollable_frame.scrollable_frame, text="No grow log entries yet.",
                     bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(pady=10)
            return

        # Display entries in reverse chronological order
        sorted_log = sorted(filtered_log, key=lambda x: x['date'], reverse=True)

        for idx, entry in enumerate(sorted_log):
            frame = tk.Frame(self.log_scrollable_frame.scrollable_frame, bg=BACKGROUND_COLOR, bd=1, relief="solid")
            frame.pack(pady=5, padx=5, fill='x')

            date_label = tk.Label(frame, text=f"Date: {entry['date']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                  font=("Helvetica", 12, "bold"))
            date_label.pack(anchor='w')

            activity_label = tk.Label(frame, text=f"Activity: {entry['activity_type']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                      font=("Helvetica", 12))
            activity_label.pack(anchor='w')

            strain_label = tk.Label(frame, text=f"Strain: {entry['strain']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                    font=("Helvetica", 12))
            strain_label.pack(anchor='w')

            notes_label = tk.Label(frame, text=f"Notes: {entry['notes']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                   font=("Helvetica", 12))
            notes_label.pack(anchor='w')

            status_label = tk.Label(frame, text=f"Status: {entry['status']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                    font=("Helvetica", 12))
            status_label.pack(anchor='w')

            # Add an Edit button
            btn_edit = tk.Button(frame, text="Edit Entry", command=lambda idx=idx: self.edit_log_entry(idx),
                                 bg="white", fg="black", font=("Helvetica", 12, "bold"),
                                 activebackground="lightgrey", activeforeground="black")
            btn_edit.pack(pady=5)

    def edit_log_entry(self, idx):
        entry = self.grow_log[idx]

        # Create a new Toplevel window (popup)
        edit_window = Toplevel(self.parent)
        edit_window.title("Edit Grow Log Entry")
        edit_window.geometry("500x600")
        edit_window.configure(bg=BACKGROUND_COLOR)

        # Entry Fields
        tk.Label(edit_window, text="Date (YYYY-MM-DD):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_date = tk.Entry(edit_window, font=("Helvetica", 12))
        entry_date.pack(pady=5)
        entry_date.insert(0, entry['date'])

        tk.Label(edit_window, text="Activity Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        activity_var = tk.StringVar()
        activity_options = ["Watered", "Fed Nutrients", "Pruned", "Harvested", "Cloned", "Transplanted", "Mom", "Other"]
        activity_menu = tk.OptionMenu(edit_window, activity_var, *activity_options)
        activity_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        activity_menu.pack(pady=5)
        activity_var.set(entry['activity_type'])

        tk.Label(edit_window, text="Strain:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        strain_var = tk.StringVar()
        strain_options = ["Select Strain"] + sorted(self.plant_genetics.keys(), key=lambda x: x.lower())
        strain_menu = tk.OptionMenu(edit_window, strain_var, *strain_options)
        strain_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        strain_menu.pack(pady=5)
        strain_var.set(entry['strain'])

        tk.Label(edit_window, text="Notes:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_notes = tk.Entry(edit_window, font=("Helvetica", 12))
        entry_notes.pack(pady=5)
        entry_notes.insert(0, entry['notes'])

        tk.Label(edit_window, text="Status:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        status_var = tk.StringVar()
        status_options = ["Seedling", "Vegetative", "Flowering", "Harvested", "Cloned", "Other"]
        status_menu = tk.OptionMenu(edit_window, status_var, *status_options)
        status_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        status_menu.pack(pady=5)
        status_var.set(entry['status'])

        # Save and Delete Buttons
        btn_frame = tk.Frame(edit_window, bg=BACKGROUND_COLOR)
        btn_frame.pack(pady=20)

        btn_save = tk.Button(btn_frame, text="Save Changes", command=lambda: self.save_edit_log_entry(
            idx, entry_date.get().strip(), activity_var.get().strip(), strain_var.get().strip(),
            entry_notes.get().strip(), status_var.get().strip(), edit_window),
            bg="white", fg="black", font=("Helvetica", 12, "bold"),
            activebackground="lightgrey", activeforeground="black")
        btn_save.pack(side='left', padx=20)

        btn_delete = tk.Button(btn_frame, text="Delete Entry", command=lambda: self.delete_log_entry(idx, edit_window),
                               bg="white", fg="black", font=("Helvetica", 12, "bold"),
                               activebackground="lightgrey", activeforeground="black")
        btn_delete.pack(side='right', padx=20)

        # Check if the activity type is 'Mom'
        if entry['activity_type'] == 'Mom':
            btn_create_clone = tk.Button(edit_window, text="Create Clone from this Mother",
                                         command=lambda: self.create_clone_from_mother(entry['strain'], edit_window),
                                         bg="white", fg="black", font=("Helvetica", 12, "bold"),
                                         activebackground="lightgrey", activeforeground="black")
            btn_create_clone.pack(pady=10)

        # Display clones if strain is selected
        if strain_var.get() != "Select Strain":
            self.show_plant_details(strain_var.get())

    def save_edit_log_entry(self, idx, date, activity, strain, notes, status, window):
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        if not activity:
            messagebox.showwarning("Incomplete Data", "Please select an activity type.")
            return

        if not strain or strain not in self.plant_genetics:
            messagebox.showwarning("Invalid Strain", "Please select a valid strain.")
            return

        # Update log entry
        self.grow_log[idx] = {
            "date": date,
            "activity_type": activity,
            "strain": strain,
            "notes": notes,
            "status": status
        }
        self.save_grow_log_data()
        self.display_log_entries()
        messagebox.showinfo("Success", "Grow log entry updated successfully!")
        window.destroy()

    def delete_log_entry(self, idx, window):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this log entry?"):
            del self.grow_log[idx]
            self.save_grow_log_data()
            self.display_log_entries()
            messagebox.showinfo("Deleted", "Grow log entry has been deleted.")
            window.destroy()

    def create_clone_from_mother(self, mother_strain, window):
        # Check if mother_strain exists in plant_genetics
        if mother_strain not in self.plant_genetics:
            messagebox.showerror("Error", f"The mother strain '{mother_strain}' does not exist in plant genetics.")
            return

        # Get the mother plant details
        mother_plant = self.plant_genetics[mother_strain]

        # Get the clone count, increment it
        clone_count = mother_plant.get('clone_count', 0) + 1

        # Update the mother's clone_count
        mother_plant['clone_count'] = clone_count

        # Generate clone suffix
        clone_suffix = self.main_app.get_clone_suffix(clone_count)

        # Generate new clone name
        clone_name = f"{mother_strain} Clone {clone_suffix}"

        # Check if clone_name already exists
        if clone_name in self.plant_genetics:
            messagebox.showwarning("Duplicate Clone", f"The clone name '{clone_name}' already exists.")
            return

        # Create the new clone in plant_genetics
        self.plant_genetics[clone_name] = {
            'lineage': mother_strain,
            'yield': 'Unknown',
            'flowering_time': 'Unknown',
            'type': 'Unknown',
            'notes': '',
            'gender': 'Unknown',
            'owned': True,
            'ownership_type': 'Clone',
            'clone_count': 0,
            'genetic_info': {}
        }

        # Save genetics data
        self.main_app.save_genetics_data()

        # Update UI elements
        self.main_app.display_genetics_buttons()
        self.main_app.update_dropdown_options()

        messagebox.showinfo("Success", f"New clone '{clone_name}' has been created from mother '{mother_strain}'.")

        # Optionally, close the edit window
        # window.destroy()

    def show_plant_details(self, plant_name):
        # Clear details_frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        if (plant_name not in self.plant_genetics):
            messagebox.showerror("Error", "Plant not found.")
            return

        details = self.plant_genetics[plant_name]

        # Plant Details
        info_text = f"{plant_name} ({details.get('gender', 'Unknown')})\n\n"
        for key, value in details.items():
            if key not in ["gender", "owned", "ownership_type", "genetic_info", "clone_count"]:
                info_text += f"{key.capitalize()}: {value}\n"

        label = tk.Label(self.details_frame, text=info_text, justify="left", padx=10, pady=10,
                         bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12))
        label.pack(fill='x', expand=False)

        # Clones
        clones = [name for name, d in self.plant_genetics.items() if d.get('lineage') == plant_name and d.get('ownership_type') == 'Clone']

        if clones:
            tk.Label(self.details_frame, text="Clones:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(pady=10)
            # Use a scrollable frame if there are many clones
            clones_frame = ScrollableFrame(self.details_frame)
            clones_frame.pack(fill='both', expand=True)
            row = 0
            column = 0
            columns = 3  # Number of columns in grid
            for clone_name in clones:
                btn_clone = tk.Button(clones_frame.scrollable_frame, text=clone_name, command=lambda c=clone_name: self.main_app.show_clone_grow_log(c),
                                      bg="white", fg="black", font=("Helvetica", 12),
                                      activebackground="lightgrey", activeforeground="black")
                btn_clone.grid(row=row, column=column, padx=5, pady=5)
                column += 1
                if column >= columns:
                    column = 0
                    row += 1
        else:
            tk.Label(self.details_frame, text="No clones found.", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(pady=10)

class CannabisGeneticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cannabis Genetics Tracker")
        self.root.geometry("1400x1100")  # Increased size for better visibility
        self.root.configure(bg=BACKGROUND_COLOR)  # Set main background to white

        # Load or initialize configuration
        self.legend_colors = self.load_config()

        # Load genetics data
        self.plant_genetics = self.load_genetics_data()

        # Determine parent strains
        self.parent_strains = self.get_parent_strains()

        # Create Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        # Genetics Tab
        self.genetics_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.genetics_tab, text="Genetics")

        # Lineage Tree Tab
        self.lineage_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.lineage_tab, text="Lineage Tree")

        # Grow Log Tab
        self.grow_log_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.grow_log_tab, text="Grow Log")

        # Initialize each tab in the correct order
        self.initialize_grow_log_tab()      # Initialize Grow Log first
        self.initialize_genetics_tab()      # Then Genetics
        self.initialize_lineage_tab()
        self.initialize_settings_tab()

    def load_config(self):
        """
        Loads legend colors from the configuration file. If not present, initializes with default colors.
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as file:
                    config = json.load(file)
                    # Ensure all required colors are present
                    for key in DEFAULT_COLORS:
                        if key not in config:
                            config[key] = DEFAULT_COLORS[key]
                    return config
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode config.json. Using default colors.")
                return DEFAULT_COLORS.copy()
        else:
            # Create config file with default colors
            with open(CONFIG_FILE, 'w') as file:
                json.dump(DEFAULT_COLORS, file, indent=4)
            return DEFAULT_COLORS.copy()

    def load_genetics_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)
                    # Ensure all strains have the necessary fields
                    for strain, details in data.items():
                        if 'clone_count' not in details:
                            data[strain]['clone_count'] = 0
                        if 'owned' not in details:
                            data[strain]['owned'] = True  # Default to owned if not specified
                        if 'ownership_type' not in details:
                            data[strain]['ownership_type'] = 'None'  # Default to 'None' if not specified
                        if 'genetic_info' not in details:
                            data[strain]['genetic_info'] = {}  # Initialize empty genetic_info
                    return {str(k): v for k, v in data.items()}
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode JSON data. Starting with empty data.")
                return {}
        else:
            # Initial data with an empty dictionary
            return {}

    def get_parent_strains(self):
        """
        Collect all parent strain names from the lineage fields.
        """
        parents = set()
        for details in self.plant_genetics.values():
            lineage = details.get('lineage', '')
            if lineage and lineage != "Unknown":
                parent_list = [parent.strip() for parent in lineage.split(' x ')]
                parents.update(parent_list)
        return parents

    def save_genetics_data(self):
        with open(DATA_FILE, 'w') as file:
            json.dump(self.plant_genetics, file, indent=4)

    def initialize_grow_log_tab(self):
        # Initialize Grow Log App within the Grow Log Tab
        self.grow_log_app = GrowLogApp(self.grow_log_tab, self.plant_genetics, self)

    def initialize_genetics_tab(self):
        # Top Frame with Genetics Button
        top_frame = tk.Frame(self.genetics_tab, bg=BACKGROUND_COLOR)
        top_frame.pack(pady=10, padx=20, fill='x')

        # Search Entry
        search_frame = tk.Frame(top_frame, bg=BACKGROUND_COLOR)
        search_frame.pack(fill='x')

        tk.Label(search_frame, text="Search:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_search_results)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 14))
        self.search_entry.pack(side="left", fill='x', expand=True, padx=10)
        self.search_entry.insert(0, '')  # Start with empty search

        # Parent Strain Selector
        parent_selector_frame = tk.Frame(top_frame, bg=BACKGROUND_COLOR)
        parent_selector_frame.pack(fill='x', pady=5)

        tk.Label(parent_selector_frame, text="Select Parent Strain:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(side="left")
        self.parent_strain_var = tk.StringVar()
        parent_strain_options = ["All Parents"] + sorted(self.parent_strains, key=lambda x: x.lower())
        self.parent_strain_dropdown = tk.OptionMenu(parent_selector_frame, self.parent_strain_var, *parent_strain_options, command=self.update_search_results)
        self.parent_strain_dropdown.config(bg="white", fg="black", font=("Helvetica", 14))
        self.parent_strain_dropdown.pack(side="left", padx=10)
        self.parent_strain_var.set("All Parents")

        # Genetics Buttons Frame with ScrollableFrame
        self.genetics_scrollable_frame = ScrollableFrame(self.genetics_tab)
        self.genetics_scrollable_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Legend for Color Coding
        self.legend_frame = tk.Frame(self.genetics_tab, bg=BACKGROUND_COLOR)
        self.legend_frame.pack(pady=10, padx=20, fill='x')

        self.create_legend()

        # Add Plant Frame
        add_frame = tk.LabelFrame(self.genetics_tab, text="Add / Update Plant", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold"))
        add_frame.pack(pady=10, padx=20, fill='x')
        self.create_entry_fields(add_frame)

        # Display Genetics Buttons
        self.display_genetics_buttons()

    def initialize_lineage_tab(self):
        # Selection Frame
        selection_frame = tk.Frame(self.lineage_tab, bg=BACKGROUND_COLOR)
        selection_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(selection_frame, text="Select Strain:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(side="left")
        self.plant_options = tk.StringVar(value="Select Strain")
        self.dropdown = tk.OptionMenu(selection_frame, self.plant_options, *sorted(self.plant_genetics.keys(), key=lambda x: x.lower()))
        self.dropdown.config(bg="white", fg="black", font=("Helvetica", 12))
        self.dropdown.pack(side="left", padx=10)

        self.btn_lineage = tk.Button(selection_frame, text="Show Lineage Tree", command=self.display_lineage_tree,
                                     bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                     activebackground="lightgrey", activeforeground="black")
        self.btn_lineage.pack(side="left", padx=10)

        # Create a Canvas with Scrollbars for the lineage tree image
        self.tree_canvas = tk.Canvas(self.lineage_tab, bg=BACKGROUND_COLOR)
        self.v_scrollbar_tree = tk.Scrollbar(self.lineage_tab, orient="vertical", command=self.tree_canvas.yview)
        self.h_scrollbar_tree = tk.Scrollbar(self.lineage_tab, orient="horizontal", command=self.tree_canvas.xview)
        self.tree_canvas.configure(yscrollcommand=self.v_scrollbar_tree.set, xscrollcommand=self.h_scrollbar_tree.set)

        self.v_scrollbar_tree.pack(side="right", fill="y")
        self.h_scrollbar_tree.pack(side="bottom", fill="x")
        self.tree_canvas.pack(side="left", fill="both", expand=True)

        self.tree_inner_frame = tk.Frame(self.tree_canvas, bg=BACKGROUND_COLOR)
        self.tree_canvas.create_window((0, 0), window=self.tree_inner_frame, anchor="nw")

        self.tree_inner_frame.bind(
            "<Configure>",
            lambda e: self.tree_canvas.configure(
                scrollregion=self.tree_canvas.bbox("all")
            )
        )

    def initialize_settings_tab(self):
        # Settings Tab
        self.settings_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.settings_tab, text="Settings")

        # Title
        tk.Label(self.settings_tab, text="Settings", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Customize Colors Button (Styled White with Black Text)
        btn_customize_colors = tk.Button(self.settings_tab, text="Customize Colors", command=self.customize_colors,
                                         bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                         activebackground="lightgrey", activeforeground="black")
        btn_customize_colors.pack(pady=10, padx=20, fill='x')

        # Delete All Button (Styled White with Black Text)
        btn_delete_all = tk.Button(self.settings_tab, text="Delete All", command=self.delete_all_data,
                                   bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                   activebackground="lightgrey", activeforeground="black")
        btn_delete_all.pack(pady=10, padx=20, fill='x')

    def create_legend(self):
        """
        Creates the legend based on current legend colors.
        """
        # Clear existing legend_frame
        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        tk.Label(self.legend_frame, text="Legend:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(side="left", padx=(0, 20))

        for legend_item, color in self.legend_colors.items():
            legend = tk.Frame(self.legend_frame, bg=color, width=25, height=25)
            legend.pack(side="left", padx=5)
            legend.pack_propagate(False)
            tk.Label(self.legend_frame, text=legend_item, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(side="left", padx=(0, 20))

    def customize_colors(self):
        """
        Opens a window to customize legend colors.
        """
        customize_window = Toplevel(self.root)
        customize_window.title("Customize Legend Colors")
        customize_window.geometry("500x600")
        customize_window.configure(bg=BACKGROUND_COLOR)

        tk.Label(customize_window, text="Customize Legend Colors", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Frame for color settings
        color_frame = tk.Frame(customize_window, bg=BACKGROUND_COLOR)
        color_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Dictionary to hold buttons for each legend item
        self.color_buttons = {}

        row = 0
        for legend_item in self.legend_colors:
            tk.Label(color_frame, text=legend_item + ":", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=row, column=0, sticky='e', padx=5, pady=10)

            btn_color = tk.Button(color_frame, bg=self.legend_colors[legend_item], width=10, command=lambda item=legend_item: self.choose_color(item))
            btn_color.grid(row=row, column=1, sticky='w', padx=5, pady=10)

            self.color_buttons[legend_item] = btn_color
            row += 1

        # Reset to Default Button
        btn_reset = tk.Button(customize_window, text="Reset to Default", command=self.reset_colors,
                              bg="white", fg="black", font=("Helvetica", 12, "bold"),
                              activebackground="lightgrey", activeforeground="black")
        btn_reset.pack(pady=20, padx=20, fill='x')

        # Save Button
        btn_save = tk.Button(customize_window, text="Save Colors", command=lambda: self.save_colors(customize_window),
                             bg="white", fg="black", font=("Helvetica", 14, "bold"),
                             activebackground="lightgrey", activeforeground="black")
        btn_save.pack(pady=10, padx=20, fill='x')

    def choose_color(self, legend_item):
        """
        Opens a color chooser dialog and updates the selected legend item's color.
        """
        color_code = colorchooser.askcolor(title=f"Choose color for {legend_item}")
        if color_code and color_code[1]:
            self.legend_colors[legend_item] = color_code[1]
            self.color_buttons[legend_item].configure(bg=color_code[1])

    def reset_colors(self):
        """
        Resets all legend colors to their default values.
        """
        for key in DEFAULT_COLORS:
            self.legend_colors[key] = DEFAULT_COLORS[key]
            if key in self.color_buttons:
                self.color_buttons[key].configure(bg=DEFAULT_COLORS[key])

    def save_colors(self, window):
        """
        Saves the customized legend colors to the configuration file and updates the legend.
        """
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.legend_colors, file, indent=4)

        # Update the legend in the UI
        self.update_legend_colors()

        window.destroy()
        messagebox.showinfo("Colors Saved", "Legend colors have been updated successfully.")

    def update_legend_colors(self):
        """
        Updates the legend frames with the current legend colors.
        """
        self.create_legend()
        # Refresh the genetics buttons to apply color changes if necessary
        self.display_genetics_buttons()

    def delete_all_data(self):
        """
        Deletes all strain data after user confirmation and resets the application.
        """
        if messagebox.askyesno("Confirm Delete All", "Are you sure you want to delete all strain data? This action cannot be undone."):
            # Reset the data structure
            self.plant_genetics = {}

            # Clear parent strains
            self.parent_strains = set()

            # Save the empty data to the JSON file
            self.save_genetics_data()

            # Update the UI
            self.display_genetics_buttons()
            self.update_dropdown_options()

            messagebox.showinfo("Data Deleted", "All strain data has been deleted. You can start adding new strains.")

    def create_entry_fields(self, parent):
        # Grid configuration for better layout
        for i in range(4):
            parent.columnconfigure(i, weight=1, pad=10)

        # Row 0
        tk.Label(parent, text="Strain Name:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=0, column=0, sticky='e')
        self.entry_name = tk.Entry(parent, font=("Helvetica", 12))
        self.entry_name.grid(row=0, column=1, sticky='we', padx=5, pady=5)

        tk.Label(parent, text="Yield:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=0, column=2, sticky='e')
        self.entry_yield = tk.Entry(parent, font=("Helvetica", 12))
        self.entry_yield.grid(row=0, column=3, sticky='we', padx=5, pady=5)

        # Row 1
        tk.Label(parent, text="Lineage:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=1, column=0, sticky='e')
        self.entry_lineage = tk.Entry(parent, font=("Helvetica", 12))
        self.entry_lineage.grid(row=1, column=1, columnspan=3, sticky='we', padx=5, pady=5)

        # Row 2
        tk.Label(parent, text="Flowering Time:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=2, column=0, sticky='e')
        self.entry_flowering_time = tk.Entry(parent, font=("Helvetica", 12))
        self.entry_flowering_time.grid(row=2, column=1, sticky='we', padx=5, pady=5)
        self.entry_flowering_time.insert(0, 'Unknown')

        tk.Label(parent, text="Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=2, column=2, sticky='e')
        self.entry_type = tk.Entry(parent, font=("Helvetica", 12))
        self.entry_type.grid(row=2, column=3, sticky='we', padx=5, pady=5)
        self.entry_type.insert(0, 'Unknown')

        # Row 3
        tk.Label(parent, text="Gender:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=3, column=0, sticky='e')
        self.gender_var = tk.StringVar(value="Female")
        gender_options = ["Female", "Male", "Unknown"]
        self.gender_menu = tk.OptionMenu(parent, self.gender_var, *gender_options)
        self.gender_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        self.gender_menu.grid(row=3, column=1, sticky='w', padx=5, pady=5)

        tk.Label(parent, text="Owned:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=3, column=2, sticky='e')
        self.owned_var = tk.BooleanVar(value=True)
        self.checkbox_owned = tk.Checkbutton(parent, variable=self.owned_var, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12))
        self.checkbox_owned.grid(row=3, column=3, sticky='w', padx=5, pady=5)

        # Row 4: Ownership Type
        tk.Label(parent, text="Ownership Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=4, column=0, sticky='e', padx=5, pady=5)
        self.ownership_type_var = tk.StringVar(value="None")
        ownership_type_options = ["None", "Clone", "Seed Start"]
        self.ownership_type_menu = tk.OptionMenu(parent, self.ownership_type_var, *ownership_type_options)
        self.ownership_type_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        self.ownership_type_menu.grid(row=4, column=1, sticky='w', padx=5, pady=5)

        # Row 5: Notes
        tk.Label(parent, text="Notes:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=5, column=0, sticky='e', padx=5, pady=5)
        self.entry_notes = tk.Entry(parent, font=("Helvetica", 12))
        self.entry_notes.grid(row=5, column=1, columnspan=3, sticky='we', padx=5, pady=5)
        self.entry_notes.insert(0, '')  # Start with empty notes

        # Row 6: Add / Update Button (Styled White with Black Text)
        self.btn_add = tk.Button(parent, text="Add / Update Plant", command=self.add_or_update_plant,
                                 bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                 activebackground="lightgrey", activeforeground="black")
        self.btn_add.grid(row=6, column=0, columnspan=4, pady=15)

    def display_genetics_buttons(self):
        # Clear existing buttons
        for widget in self.genetics_scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        # Filter strains to only those that are owned
        owned_strains = [name for name, details in self.plant_genetics.items() if details.get('owned', True)]
        sorted_plants = sorted(owned_strains, key=lambda x: x.lower())

        # Arrange buttons in grid
        columns = 5  # Number of columns in grid
        row = 0
        column = 0
        for plant_name in sorted_plants:
            ownership_type = self.plant_genetics[plant_name].get('ownership_type', 'None')
            is_parent = plant_name in self.parent_strains
            is_owned = self.plant_genetics[plant_name].get('owned', True)

            # Determine role and color using legend_colors
            if is_parent and is_owned:
                color = self.legend_colors.get("Owned & Parent Strain", "#32CD32")
            elif not is_parent and is_owned:
                # Assign color based on ownership type
                if ownership_type == "Seed Start":
                    color = self.legend_colors.get("Seed Start Strain", "#00FFFF")
                elif ownership_type == "Clone":
                    color = self.legend_colors.get("Clone Strain", "#FF69B4")
                else:
                    color = self.legend_colors.get("Owned Strain", "#1E90FF")
            else:
                # Skip strains that are not owned
                continue  # We already filtered for owned strains, but this is extra safety

            # Create Button (Retain Color Coding)
            btn = tk.Button(self.genetics_scrollable_frame.scrollable_frame, text=plant_name, width=20,
                            command=lambda p=plant_name: self.show_plant_details(p),
                            bg=color, fg=BACKGROUND_COLOR, font=("Helvetica", 12, "bold"),
                            activebackground=color, activeforeground=BACKGROUND_COLOR)
            btn.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
            column += 1
            if column >= columns:
                column = 0
                row += 1

        # Make buttons expand equally
        for i in range(columns):
            self.genetics_scrollable_frame.scrollable_frame.columnconfigure(i, weight=1)

    def show_plant_details(self, plant_name):
        if (plant_name not in self.plant_genetics):
            messagebox.showerror("Error", "Plant not found.")
            return

        details = self.plant_genetics[plant_name]

        # Create a new Toplevel window (popup)
        details_window = Toplevel(self.root)
        details_window.title(f"{plant_name} Details")
        details_window.geometry("800x600")
        details_window.configure(bg=BACKGROUND_COLOR)

        # Create main frame
        main_frame = tk.Frame(details_window, bg=BACKGROUND_COLOR)
        main_frame.pack(fill='both', expand=True)

        # Left frame for mother's details
        left_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        left_frame.pack(side='left', fill='both', expand=True)

        # Right frame for clones
        right_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        right_frame.pack(side='left', fill='both', expand=True)

        # Display plant details in the left frame
        info_text = f"{plant_name} ({details.get('gender', 'Unknown')})\n\n"
        for key, value in details.items():
            if key not in ["gender", "owned", "ownership_type", "genetic_info", "clone_count"]:
                info_text += f"{key.capitalize()}: {value}\n"

        label = tk.Label(left_frame, text=info_text, justify="left", padx=10, pady=10,
                         bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12))
        label.pack(fill='x', expand=False)

        # Editable Fields in left_frame
        edit_frame = tk.Frame(left_frame, bg=BACKGROUND_COLOR)
        edit_frame.pack(pady=10, padx=20, fill='x')

        # Strain Name
        tk.Label(edit_frame, text="Strain Name:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=0, column=0, sticky='e')
        self.edit_entry_name = tk.Entry(edit_frame, font=("Helvetica", 12))
        self.edit_entry_name.grid(row=0, column=1, sticky='we', padx=5, pady=5)
        self.edit_entry_name.insert(0, plant_name)

        # Yield
        tk.Label(edit_frame, text="Yield:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=1, column=0, sticky='e')
        self.edit_entry_yield = tk.Entry(edit_frame, font=("Helvetica", 12))
        self.edit_entry_yield.grid(row=1, column=1, sticky='we', padx=5, pady=5)
        self.edit_entry_yield.insert(0, details.get('yield', 'Unknown'))

        # Lineage
        tk.Label(edit_frame, text="Lineage:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=2, column=0, sticky='e')
        self.edit_entry_lineage = tk.Entry(edit_frame, font=("Helvetica", 12))
        self.edit_entry_lineage.grid(row=2, column=1, sticky='we', padx=5, pady=5)
        self.edit_entry_lineage.insert(0, details.get('lineage', 'Unknown'))

        # Flowering Time
        tk.Label(edit_frame, text="Flowering Time:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=3, column=0, sticky='e')
        self.edit_entry_flowering_time = tk.Entry(edit_frame, font=("Helvetica", 12))
        self.edit_entry_flowering_time.grid(row=3, column=1, sticky='we', padx=5, pady=5)
        self.edit_entry_flowering_time.insert(0, details.get('flowering_time', 'Unknown'))

        # Type
        tk.Label(edit_frame, text="Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=4, column=0, sticky='e')
        self.edit_entry_type = tk.Entry(edit_frame, font=("Helvetica", 12))
        self.edit_entry_type.grid(row=4, column=1, sticky='we', padx=5, pady=5)
        self.edit_entry_type.insert(0, details.get('type', 'Unknown'))

        # Gender
        tk.Label(edit_frame, text="Gender:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=5, column=0, sticky='e')
        self.edit_gender_var = tk.StringVar(value=details.get("gender", "Unknown"))
        gender_options = ["Female", "Male", "Unknown"]
        self.edit_gender_menu = tk.OptionMenu(edit_frame, self.edit_gender_var, *gender_options)
        self.edit_gender_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        self.edit_gender_menu.grid(row=5, column=1, sticky='w', padx=5, pady=5)

        # Owned
        tk.Label(edit_frame, text="Owned:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=6, column=0, sticky='e')
        self.edit_owned_var = tk.BooleanVar(value=details.get("owned", True))
        self.edit_checkbox_owned = tk.Checkbutton(edit_frame, variable=self.edit_owned_var, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12))
        self.edit_checkbox_owned.grid(row=6, column=1, sticky='w', padx=5, pady=5)

        # Ownership Type
        tk.Label(edit_frame, text="Ownership Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=7, column=0, sticky='e')
        self.edit_ownership_type_var = tk.StringVar(value=details.get("ownership_type", "None"))
        ownership_type_options = ["None", "Clone", "Seed Start"]
        self.edit_ownership_type_menu = tk.OptionMenu(edit_frame, self.edit_ownership_type_var, *ownership_type_options)
        self.edit_ownership_type_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        self.edit_ownership_type_menu.grid(row=7, column=1, sticky='w', padx=5, pady=5)

        # Notes
        tk.Label(edit_frame, text="Notes:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=8, column=0, sticky='e')
        self.edit_entry_notes = tk.Entry(edit_frame, font=("Helvetica", 12))
        self.edit_entry_notes.grid(row=8, column=1, sticky='we', padx=5, pady=5)
        self.edit_entry_notes.insert(0, details.get('notes', ''))

        # Genetic Information Button
        btn_genetic_info = tk.Button(left_frame, text="Genetic Information", command=lambda: self.open_genetic_info_window(plant_name),
                                     bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                     activebackground="lightgrey", activeforeground="black")
        btn_genetic_info.pack(pady=10)

        # Configure grid weights
        for i in range(2):
            edit_frame.columnconfigure(i, weight=1)

        # Save Changes and Delete Buttons in left_frame
        btn_frame = tk.Frame(left_frame, bg=BACKGROUND_COLOR)
        btn_frame.pack(pady=20)

        # Save Changes Button (Styled White with Black Text)
        btn_save = tk.Button(btn_frame, text="Save Changes", command=lambda: self.update_plant_details(plant_name, details_window),
                             bg="white", fg="black", font=("Helvetica", 14, "bold"),
                             activebackground="lightgrey", activeforeground="black")
        btn_save.pack(side='left', padx=20)

        # Delete Button (Styled White with Black Text)
        btn_delete = tk.Button(btn_frame, text="Delete", command=lambda: self.delete_plant(plant_name, details_window),
                               bg="white", fg="black", font=("Helvetica", 14, "bold"),
                               activebackground="lightgrey", activeforeground="black")
        btn_delete.pack(side='right', padx=20)

        # Now, in the right_frame, display clones
        # Find clones of this mother
        clones = [name for name, d in self.plant_genetics.items() if d.get('lineage') == plant_name and d.get('ownership_type') == 'Clone']

        if clones:
            tk.Label(right_frame, text="Clones:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(pady=10)
            # Use a scrollable frame if there are many clones
            clones_frame = ScrollableFrame(right_frame)
            clones_frame.pack(fill='both', expand=True)
            row = 0
            column = 0
            columns = 3  # Number of columns in grid
            for clone_name in clones:
                btn_clone = tk.Button(clones_frame.scrollable_frame, text=clone_name, command=lambda c=clone_name: self.show_clone_grow_log(c),
                                      bg="white", fg="black", font=("Helvetica", 12),
                                      activebackground="lightgrey", activeforeground="black")
                btn_clone.grid(row=row, column=column, padx=5, pady=5)
                column += 1
                if column >= columns:
                    column = 0
                    row += 1
        else:
            tk.Label(right_frame, text="No clones found.", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(pady=10)

    def show_clone_grow_log(self, clone_name):
        # Load grow log data
        if os.path.exists(GROW_LOG_FILE):
            try:
                with open(GROW_LOG_FILE, 'r') as file:
                    grow_log = json.load(file)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode grow_log.json.")
                return
        else:
            messagebox.showinfo("No Grow Log", "No grow log entries found.")
            return

        # Filter entries for the selected clone
        clone_entries = [entry for entry in grow_log if entry.get('strain') == clone_name]

        # Create a new window to display the entries
        grow_log_window = Toplevel(self.root)
        grow_log_window.title(f"Grow Log for {clone_name}")
        grow_log_window.geometry("600x800")
        grow_log_window.configure(bg=BACKGROUND_COLOR)

        tk.Label(grow_log_window, text=f"Grow Log for {clone_name}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Add Log Entry Button
        btn_add_log = tk.Button(grow_log_window, text="Add Log Entry", command=lambda: self.add_log_entry_for_clone(clone_name, grow_log_window),
                                bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                activebackground="lightgrey", activeforeground="black")
        btn_add_log.pack(pady=10)

        # Use a scrollable frame to display the entries
        scrollable_frame = ScrollableFrame(grow_log_window)
        scrollable_frame.pack(pady=10, padx=20, fill='both', expand=True)

        if not clone_entries:
            tk.Label(scrollable_frame.scrollable_frame, text="No grow log entries for this clone.",
                     bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(pady=10)
            return

        # Display entries
        for idx, entry in enumerate(clone_entries):
            frame = tk.Frame(scrollable_frame.scrollable_frame, bg=BACKGROUND_COLOR, bd=1, relief="solid")
            frame.pack(pady=5, padx=5, fill='x')

            date_label = tk.Label(frame, text=f"Date: {entry['date']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                  font=("Helvetica", 12, "bold"))
            date_label.pack(anchor='w')

            activity_label = tk.Label(frame, text=f"Activity: {entry['activity_type']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                      font=("Helvetica", 12))
            activity_label.pack(anchor='w')

            notes_label = tk.Label(frame, text=f"Notes: {entry['notes']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                   font=("Helvetica", 12))
            notes_label.pack(anchor='w')

            status_label = tk.Label(frame, text=f"Status: {entry['status']}", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                                    font=("Helvetica", 12))
            status_label.pack(anchor='w')

            # Add an Edit button
            btn_edit = tk.Button(frame, text="Edit Entry", command=lambda idx=idx: self.edit_clone_log_entry(clone_entries, idx, grow_log_window),
                                 bg="white", fg="black", font=("Helvetica", 12, "bold"),
                                 activebackground="lightgrey", activeforeground="black")
            btn_edit.pack(pady=5)

    def edit_clone_log_entry(self, clone_entries, idx, parent_window):
        entry = clone_entries[idx]

        # Create a new Toplevel window (popup)
        edit_window = Toplevel(self.root)
        edit_window.title("Edit Grow Log Entry")
        edit_window.geometry("500x600")
        edit_window.configure(bg=BACKGROUND_COLOR)

        # Entry Fields
        tk.Label(edit_window, text="Date (YYYY-MM-DD):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_date = tk.Entry(edit_window, font=("Helvetica", 12))
        entry_date.pack(pady=5)
        entry_date.insert(0, entry['date'])

        tk.Label(edit_window, text="Activity Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        activity_var = tk.StringVar()
        activity_options = ["Watered", "Fed Nutrients", "Pruned", "Harvested", "Cloned", "Transplanted", "Mom", "Other"]
        activity_menu = tk.OptionMenu(edit_window, activity_var, *activity_options)
        activity_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        activity_menu.pack(pady=5)
        activity_var.set(entry['activity_type'])

        tk.Label(edit_window, text="Notes:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_notes = tk.Entry(edit_window, font=("Helvetica", 12))
        entry_notes.pack(pady=5)
        entry_notes.insert(0, entry['notes'])

        tk.Label(edit_window, text="Status:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        status_var = tk.StringVar()
        status_options = ["Seedling", "Vegetative", "Flowering", "Harvested", "Cloned", "Other"]
        status_menu = tk.OptionMenu(edit_window, status_var, *status_options)
        status_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        status_menu.pack(pady=5)
        status_var.set(entry['status'])

        # Save and Delete Buttons
        btn_frame = tk.Frame(edit_window, bg=BACKGROUND_COLOR)
        btn_frame.pack(pady=20)

        btn_save = tk.Button(btn_frame, text="Save Changes", command=lambda: self.save_edit_clone_log_entry(
            entry, entry_date.get().strip(), activity_var.get().strip(),
            entry_notes.get().strip(), status_var.get().strip(), edit_window, parent_window),
            bg="white", fg="black", font=("Helvetica", 12, "bold"),
            activebackground="lightgrey", activeforeground="black")
        btn_save.pack(side='left', padx=20)

        btn_delete = tk.Button(btn_frame, text="Delete Entry", command=lambda: self.delete_clone_log_entry(entry, edit_window, parent_window),
                               bg="white", fg="black", font=("Helvetica", 12, "bold"),
                               activebackground="lightgrey", activeforeground="black")
        btn_delete.pack(side='right', padx=20)

    def save_edit_clone_log_entry(self, entry, date, activity, notes, status, window, parent_window):
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        if not activity:
            messagebox.showwarning("Incomplete Data", "Please select an activity type.")
            return

        # Update entry
        entry['date'] = date
        entry['activity_type'] = activity
        entry['notes'] = notes
        entry['status'] = status

        # Save grow log data
        with open(GROW_LOG_FILE, 'w') as file:
            json.dump(self.grow_log_app.grow_log, file, indent=4)

        messagebox.showinfo("Success", "Grow log entry updated successfully!")
        window.destroy()

        # Refresh the clone's grow log window
        parent_window.destroy()
        self.show_clone_grow_log(entry['strain'])

    def delete_clone_log_entry(self, entry, window, parent_window):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this log entry?"):
            # Remove entry from grow log
            self.grow_log_app.grow_log.remove(entry)
            self.grow_log_app.save_grow_log_data()

            messagebox.showinfo("Deleted", "Grow log entry has been deleted.")
            window.destroy()

            # Refresh the clone's grow log window
            parent_window.destroy()
            self.show_clone_grow_log(entry['strain'])

    def add_log_entry_for_clone(self, clone_name, parent_window):
        # Create a new Toplevel window (popup)
        entry_window = Toplevel(parent_window)
        entry_window.title(f"Add Grow Log Entry for {clone_name}")
        entry_window.geometry("500x600")
        entry_window.configure(bg=BACKGROUND_COLOR)

        # Entry Fields
        tk.Label(entry_window, text="Date (YYYY-MM-DD):", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_date = tk.Entry(entry_window, font=("Helvetica", 12))
        entry_date.pack(pady=5)
        entry_date.insert(0, datetime.now().strftime('%Y-%m-%d'))

        tk.Label(entry_window, text="Activity Type:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        activity_var = tk.StringVar()
        activity_options = ["Watered", "Fed Nutrients", "Pruned", "Harvested", "Cloned", "Transplanted", "Mom", "Other"]
        activity_menu = tk.OptionMenu(entry_window, activity_var, *activity_options)
        activity_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        activity_menu.pack(pady=5)
        activity_var.set("Watered")

        tk.Label(entry_window, text="Notes:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        entry_notes = tk.Entry(entry_window, font=("Helvetica", 12))
        entry_notes.pack(pady=5)
        entry_notes.insert(0, '')

        tk.Label(entry_window, text="Status:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 12)).pack(pady=5)
        status_var = tk.StringVar()
        status_options = ["Seedling", "Vegetative", "Flowering", "Harvested", "Cloned", "Other"]
        status_menu = tk.OptionMenu(entry_window, status_var, *status_options)
        status_menu.config(bg="white", fg="black", font=("Helvetica", 12))
        status_menu.pack(pady=5)
        status_var.set("Vegetative")

        # Save Button
        btn_save_log = tk.Button(entry_window, text="Save Entry", command=lambda: self.save_log_entry_for_clone(entry_date.get().strip(),
                                                                                                                 activity_var.get().strip(),
                                                                                                                 clone_name,
                                                                                                                 entry_notes.get().strip(),
                                                                                                                 status_var.get().strip(),
                                                                                                                 entry_window, parent_window),
                                 bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                 activebackground="lightgrey", activeforeground="black")
        btn_save_log.pack(pady=20)

    def save_log_entry_for_clone(self, date, activity, strain, notes, status, window, parent_window):
        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Invalid Date", "Please enter the date in YYYY-MM-DD format.")
            return

        if not activity:
            messagebox.showwarning("Incomplete Data", "Please select an activity type.")
            return

        if not strain or strain not in self.plant_genetics:
            messagebox.showwarning("Invalid Strain", "Please select a valid strain.")
            return

        # Load grow log data
        if os.path.exists(GROW_LOG_FILE):
            try:
                with open(GROW_LOG_FILE, 'r') as file:
                    grow_log = json.load(file)
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode grow_log.json.")
                return
        else:
            grow_log = []

        # Add new log entry
        grow_log.append({
            "date": date,
            "activity_type": activity,
            "strain": strain,
            "notes": notes,
            "status": status
        })

        # Save grow log data
        with open(GROW_LOG_FILE, 'w') as file:
            json.dump(grow_log, file, indent=4)

        messagebox.showinfo("Success", "Grow log entry added successfully!")
        window.destroy()

        # Refresh the clone's grow log window
        parent_window.destroy()
        self.show_clone_grow_log(strain)

    def update_plant_details(self, plant_name, window):
        """
        Updates the plant details based on the edited fields.
        """
        new_name = self.edit_entry_name.get().strip()
        lineage = self.edit_entry_lineage.get().strip()
        gender = self.edit_gender_var.get()
        yield_info = self.edit_entry_yield.get().strip()
        flowering_time = self.edit_entry_flowering_time.get().strip()
        plant_type = self.edit_entry_type.get().strip()
        notes = self.edit_entry_notes.get().strip()
        owned = self.edit_owned_var.get()
        ownership_type = self.edit_ownership_type_var.get()

        if not new_name:
            messagebox.showwarning("Incomplete Data", "Please enter the strain name.")
            return

        # If the name has changed and the new name already exists, prevent duplication
        if new_name != plant_name and new_name in self.plant_genetics:
            messagebox.showerror("Error", f"A strain named '{new_name}' already exists.")
            return

        # Update the plant genetics data
        self.plant_genetics[new_name] = {
            "lineage": lineage if lineage else "Unknown",
            "yield": yield_info or "Unknown",
            "flowering_time": flowering_time or "Unknown",
            "type": plant_type or "Unknown",
            "notes": notes or "",
            "gender": gender or "Unknown",
            "owned": owned,
            "ownership_type": ownership_type if owned else "None",
            "clone_count": self.plant_genetics[plant_name].get('clone_count', 0),
            "genetic_info": self.plant_genetics[plant_name].get('genetic_info', {})
        }

        # If the name has changed, remove the old entry
        if new_name != plant_name:
            del self.plant_genetics[plant_name]
            # Update any clones that have this plant as their mother
            for strain, details in self.plant_genetics.items():
                if details.get('lineage') == plant_name:
                    self.plant_genetics[strain]['lineage'] = new_name

        # Update parent strains after modification
        self.parent_strains = self.get_parent_strains()

        self.save_genetics_data()
        self.display_genetics_buttons()
        self.update_dropdown_options()
        self.update_genetic_traits_tree()
        messagebox.showinfo("Success", f"'{new_name}' has been updated successfully!")
        window.destroy()

    def delete_plant(self, plant_name, window):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{plant_name}'?"):
            del self.plant_genetics[plant_name]
            self.save_genetics_data()
            self.display_genetics_buttons()
            self.update_dropdown_options()
            self.update_genetic_traits_tree()
            window.destroy()
            messagebox.showinfo("Deleted", f"'{plant_name}' has been deleted.")

    def add_or_update_plant(self):
        name = self.entry_name.get().strip()
        lineage = self.entry_lineage.get().strip()
        gender = self.gender_var.get()
        yield_info = self.entry_yield.get().strip()
        flowering_time = self.entry_flowering_time.get().strip()
        plant_type = self.entry_type.get().strip()
        notes = self.entry_notes.get().strip()
        owned = self.owned_var.get()
        ownership_type = self.ownership_type_var.get()

        if not name:
            messagebox.showwarning("Incomplete Data", "Please enter the strain name.")
            return

        # Handle Clone Naming
        if ownership_type == "Clone":
            # Extract mother plant from lineage
            if not lineage or lineage == "Unknown":
                messagebox.showwarning("Invalid Lineage", "Please specify a valid lineage for cloning.")
                return
            parents = [parent.strip() for parent in lineage.split(" x ")]
            if not parents:
                messagebox.showwarning("Invalid Lineage", "Please specify at least one mother plant.")
                return
            mother_plant = parents[0]  # Assuming the first parent is the mother

            if mother_plant not in self.plant_genetics:
                messagebox.showwarning("Unknown Mother Plant", f"The mother plant '{mother_plant}' does not exist.")
                return

            # Generate clone name
            clone_count = self.plant_genetics[mother_plant].get('clone_count', 0) + 1
            clone_suffix = self.get_clone_suffix(clone_count)
            clone_name = f"{mother_plant} Clone {clone_suffix}"

            if clone_name in self.plant_genetics:
                messagebox.showwarning("Duplicate Clone", f"The clone name '{clone_name}' already exists.")
                return

            # Update clone count
            self.plant_genetics[mother_plant]['clone_count'] = clone_count

            name = clone_name  # Override the entered name with the auto-generated clone name

        # Optional: Validate that parents exist or are 'Unknown'
        if lineage != "Unknown":
            parents = [parent.strip() for parent in lineage.split(" x ")]
            for parent in parents:
                if parent and parent not in self.plant_genetics:
                    if messagebox.askyesno("Unknown Parent", f"Parent '{parent}' does not exist. Do you want to add it as a new plant?"):
                        # Add parent as a new plant with minimal information
                        self.plant_genetics[parent] = {
                            "lineage": "Unknown",
                            "yield": "Unknown",
                            "flowering_time": "Unknown",
                            "type": "Unknown",
                            "notes": "",
                            "gender": "Unknown",
                            "owned": False,
                            "ownership_type": "None",
                            "clone_count": 0,
                            "genetic_info": {}
                        }
                    else:
                        return

        # If updating an existing strain with a different name
        if name in self.plant_genetics and name != name:
            del self.plant_genetics[name]

        self.plant_genetics[name] = {
            "lineage": lineage if lineage else "Unknown",
            "yield": yield_info or "Unknown",
            "flowering_time": flowering_time or "Unknown",
            "type": plant_type or "Unknown",
            "notes": notes or "",
            "gender": gender or "Unknown",
            "owned": owned,
            "ownership_type": ownership_type if owned else "None",
            "clone_count": self.plant_genetics.get(name, {}).get('clone_count', 0),
            "genetic_info": self.plant_genetics.get(name, {}).get('genetic_info', {})
        }

        # Update parent strains after adding new plant
        self.parent_strains = self.get_parent_strains()

        self.save_genetics_data()
        self.display_genetics_buttons()
        self.update_dropdown_options()
        self.update_genetic_traits_tree()
        messagebox.showinfo("Success", f"'{name}' has been added/updated!")

        # Clear input fields
        self.clear_entry_fields()

    def get_clone_suffix(self, clone_count):
        """
        Generates a clone suffix based on the clone count.
        For example: 1 -> A, 2 -> B, ..., 26 -> Z, 27 -> A1, 28 -> B1, etc.
        """
        import string
        if clone_count <= 26:
            return string.ascii_uppercase[clone_count - 1]
        else:
            # For counts beyond 26, append numbers
            first_part = string.ascii_uppercase[(clone_count - 1) // 26 - 1]
            second_part = string.ascii_uppercase[(clone_count - 1) % 26]
            return f"{first_part}{second_part}"

    def clear_entry_fields(self):
        self.entry_name.delete(0, tk.END)
        self.entry_lineage.delete(0, tk.END)
        self.gender_var.set("Female")
        self.owned_var.set(True)
        self.ownership_type_var.set("None")
        self.entry_yield.delete(0, tk.END)
        self.entry_flowering_time.delete(0, tk.END)
        self.entry_type.delete(0, tk.END)
        self.entry_notes.delete(0, tk.END)

    def update_dropdown_options(self):
        """
        Updates dropdown options across all relevant components.
        """
        # Update options in the Lineage Tree tab
        menu = self.dropdown["menu"]
        menu.delete(0, "end")
        for strain in sorted(self.plant_genetics.keys(), key=lambda x: x.lower()):
            menu.add_command(label=strain, command=lambda value=strain: self.plant_options.set(value))
        self.plant_options.set("Select Strain")  # Reset selection

        # Update options in Grow Log strain selection
        if hasattr(self.grow_log_app, 'strain_var'):
            strain_options = ["Select Strain"] + sorted(self.plant_genetics.keys(), key=lambda x: x.lower())
            menu = self.grow_log_app.strain_dropdown["menu"]
            menu.delete(0, "end")
            for strain in strain_options:
                menu.add_command(label=strain, command=lambda value=strain: self.grow_log_app.strain_var.set(value))
            self.grow_log_app.strain_var.set("Select Strain")

        # Update options in the Genetics tab parent strain dropdown
        if hasattr(self, 'parent_strain_dropdown'):
            parent_strain_options = ["All Parents"] + sorted(self.parent_strains, key=lambda x: x.lower())
            menu = self.parent_strain_dropdown["menu"]
            menu.delete(0, "end")
            for parent in parent_strain_options:
                menu.add_command(label=parent, command=lambda value=parent: self.parent_strain_var.set(value))
            self.parent_strain_var.set("All Parents")

    def display_lineage_tree(self):
        plant_name = self.plant_options.get()
        if plant_name not in self.plant_genetics:
            messagebox.showerror("Error", "Please select a valid strain.")
            return

        dot = graphviz.Digraph(comment=plant_name)
        visited = set()

        def add_to_tree(name):
            if name in visited:
                return  # Prevent duplicate nodes
            visited.add(name)

            if name not in self.plant_genetics:
                # Strain not in data; display as a separate node
                dot.node(name, name, color="black")
                return

            current_plant = self.plant_genetics[name]
            gender = current_plant.get("gender", "Unknown")
            label = f"{name}\n({gender})"

            # Determine node color
            is_parent = name in self.parent_strains
            is_owned = current_plant.get('owned', True)
            ownership_type = current_plant.get('ownership_type', 'None')

            if is_parent and is_owned:
                node_color = self.legend_colors.get("Owned & Parent Strain", "#32CD32")
            elif is_parent and not is_owned:
                node_color = self.legend_colors.get("Parent Strain", "#FFD700")
            elif not is_parent and is_owned:
                if ownership_type == "Clone":
                    node_color = self.legend_colors.get("Clone Strain", "#FF69B4")
                elif ownership_type == "Seed Start":
                    node_color = self.legend_colors.get("Seed Start Strain", "#00FFFF")
                else:
                    node_color = self.legend_colors.get("Owned Strain", "#1E90FF")
            else:
                node_color = self.legend_colors.get("Not Owned Strain", "#A9A9A9")

            dot.node(name, label, style='filled', fillcolor=node_color)

            lineage = current_plant.get("lineage", "Unknown")
            if lineage != "Unknown":
                parents = [parent.strip() for parent in lineage.split(" x ")]
                for parent in parents:
                    add_to_tree(parent)
                    dot.edge(parent, name)

        add_to_tree(plant_name)

        try:
            dot.render("lineage_tree", format="png", cleanup=True)
            img = Image.open("lineage_tree.png")
            img_width, img_height = img.size
            max_width = 1200
            max_height = 1200

            # Resize image if it's too large
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width / img_width, max_height / img_height)
                img = img.resize((int(img_width * ratio), int(img_height * ratio)), Image.LANCZOS)

            img = ImageTk.PhotoImage(img)

            # Clear previous image
            for widget in self.tree_inner_frame.winfo_children():
                widget.destroy()

            # Display new image
            self.image_label = tk.Label(self.tree_inner_frame, image=img, bg=BACKGROUND_COLOR)
            self.image_label.image = img  # Keep a reference
            self.image_label.pack()

            # Update scrollregion
            self.tree_canvas.update_idletasks()
            self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox("all"))
        except graphviz.backend.ExecutableNotFound:
            messagebox.showerror("Graphviz Not Found", "Graphviz executable not found. Please install Graphviz and ensure it's added to your system's PATH.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate lineage tree.\n{e}")

    def open_genetic_info_window(self, plant_name):
        """
        Opens a new window to view and edit genetic information for the selected strain.
        """
        genetic_info = self.plant_genetics[plant_name].get('genetic_info', {})

        genetic_window = Toplevel(self.root)
        genetic_window.title(f"{plant_name} Genetic Information")
        genetic_window.geometry("600x700")
        genetic_window.configure(bg=BACKGROUND_COLOR)

        # Title
        tk.Label(genetic_window, text=f"{plant_name} Genetic Information", bg=BACKGROUND_COLOR, fg=TEXT_COLOR,
                 font=("Helvetica", 16, "bold")).pack(pady=10)

        # Genetic Information Frame with ScrollableFrame
        genetic_scrollable_frame = ScrollableFrame(genetic_window)
        genetic_scrollable_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Existing Genetic Info
        self.genetic_info_entries = {}
        row = 0
        for key, value in genetic_info.items():
            tk.Label(genetic_scrollable_frame.scrollable_frame, text=f"{key}:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=row, column=0, sticky='e', padx=5, pady=5)
            entry = tk.Entry(genetic_scrollable_frame.scrollable_frame, font=("Helvetica", 12))
            entry.grid(row=row, column=1, sticky='we', padx=5, pady=5)
            entry.insert(0, value)
            self.genetic_info_entries[key] = entry
            row += 1

        # Add New Genetic Info
        add_frame = tk.Frame(genetic_scrollable_frame.scrollable_frame, bg=BACKGROUND_COLOR)
        add_frame.grid(row=row, column=0, columnspan=2, pady=10)

        tk.Label(add_frame, text="New Attribute:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.new_genetic_key = tk.Entry(add_frame, font=("Helvetica", 12))
        self.new_genetic_key.grid(row=0, column=1, sticky='we', padx=5, pady=5)

        tk.Label(add_frame, text="Value:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.new_genetic_value = tk.Entry(add_frame, font=("Helvetica", 12))
        self.new_genetic_value.grid(row=1, column=1, sticky='we', padx=5, pady=5)

        # Add Button (Styled White with Black Text)
        btn_add_genetic = tk.Button(genetic_window, text="Add Genetic Attribute", command=lambda: self.add_genetic_attribute(genetic_info, genetic_scrollable_frame),
                                     bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                     activebackground="lightgrey", activeforeground="black")
        btn_add_genetic.pack(pady=10)

        # Save Button (Styled White with Black Text)
        btn_save_genetic = tk.Button(genetic_window, text="Save Genetic Information", command=lambda: self.save_genetic_info(plant_name, genetic_window),
                                     bg="white", fg="black", font=("Helvetica", 14, "bold"),
                                     activebackground="lightgrey", activeforeground="black")
        btn_save_genetic.pack(pady=10)

    def add_genetic_attribute(self, genetic_info, frame):
        """
        Adds a new genetic attribute entry to the Genetics window.
        """
        key = self.new_genetic_key.get().strip()
        value = self.new_genetic_value.get().strip()

        if not key or not value:
            messagebox.showwarning("Incomplete Data", "Please enter both attribute name and value.")
            return

        if key in genetic_info:
            messagebox.showwarning("Duplicate Attribute", "This attribute already exists.")
            return

        # Add to genetic_info dictionary
        genetic_info[key] = value

        # Add to UI
        row = len(self.genetic_info_entries)
        tk.Label(frame.scrollable_frame, text=f"{key}:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).grid(row=row, column=0, sticky='e', padx=5, pady=5)
        entry = tk.Entry(frame.scrollable_frame, font=("Helvetica", 12))
        entry.grid(row=row, column=1, sticky='we', padx=5, pady=5)
        entry.insert(0, value)
        self.genetic_info_entries[key] = entry

        # Clear input fields
        self.new_genetic_key.delete(0, tk.END)
        self.new_genetic_value.delete(0, tk.END)

    def save_genetic_info(self, plant_name, window):
        """
        Saves the genetic information back to the main data structure and updates the JSON file.
        """
        genetic_info = {}
        for key, entry in self.genetic_info_entries.items():
            value = entry.get().strip()
            if value:
                genetic_info[key] = value

        self.plant_genetics[plant_name]['genetic_info'] = genetic_info
        self.save_genetics_data()
        self.display_genetics_buttons()
        self.update_genetic_traits_tree()
        window.destroy()
        messagebox.showinfo("Success", f"Genetic information for '{plant_name}' has been saved.")

    def update_genetic_traits_tree(self):
        # Placeholder for future implementations if needed
        pass

    def update_search_results(self, *args):
        search_term = self.search_var.get().lower()
        for widget in self.genetics_scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        # Filter plant names based on search term and ownership
        owned_strains = [name for name, details in self.plant_genetics.items() if details.get('owned', True)]
        filtered_plants = [name for name in owned_strains if search_term in name.lower()]

        # Further filter based on selected parent strain
        selected_parent = self.parent_strain_var.get()
        if selected_parent != "All Parents":
            filtered_plants = [name for name in filtered_plants
                               if selected_parent in self.plant_genetics[name].get('lineage', '')]

        # Arrange buttons in grid
        columns = 5  # Number of columns in grid
        row = 0
        column = 0
        for plant_name in sorted(filtered_plants, key=lambda x: x.lower()):
            ownership_type = self.plant_genetics[plant_name].get('ownership_type', 'None')
            is_parent = plant_name in self.parent_strains
            is_owned = self.plant_genetics[plant_name].get('owned', True)

            # Determine role and color using legend_colors
            if is_parent and is_owned:
                color = self.legend_colors.get("Owned & Parent Strain", "#32CD32")
            elif not is_parent and is_owned:
                # Assign color based on ownership type
                if ownership_type == "Seed Start":
                    color = self.legend_colors.get("Seed Start Strain", "#00FFFF")
                elif ownership_type == "Clone":
                    color = self.legend_colors.get("Clone Strain", "#FF69B4")
                else:
                    color = self.legend_colors.get("Owned Strain", "#1E90FF")
            else:
                # Skip strains that are not owned
                continue  # We already filtered for owned strains, but this is extra safety

            btn = tk.Button(self.genetics_scrollable_frame.scrollable_frame, text=plant_name, width=20,
                            command=lambda p=plant_name: self.show_plant_details(p),
                            bg=color, fg=BACKGROUND_COLOR, font=("Helvetica", 12, "bold"),
                            activebackground=color, activeforeground=BACKGROUND_COLOR)
            btn.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
            column += 1
            if column >= columns:
                column = 0
                row += 1

        # Make buttons expand equally
        for i in range(columns):
            self.genetics_scrollable_frame.scrollable_frame.columnconfigure(i, weight=1)

    @staticmethod
    def main():
        root = tk.Tk()
        app = CannabisGeneticsApp(root)
        root.mainloop()

if __name__ == "__main__":
    CannabisGeneticsApp.main()
