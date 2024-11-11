# app.py
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, Toplevel
import json
import os
from datetime import datetime
import graphviz
from PIL import Image, ImageTk
from constants import DATA_FILE, GROW_LOG_FILE, CONFIG_FILE, DEFAULT_COLORS, BACKGROUND_COLOR, TEXT_COLOR
from components import ScrollableFrame
from grow_log import GrowLogApp

import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CannabisGeneticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cannabis Genetics Tracker")
        self.root.geometry("1400x1100")
        self.root.configure(bg=BACKGROUND_COLOR)

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

        # Settings Tab
        self.settings_tab = tk.Frame(self.notebook, bg=BACKGROUND_COLOR)
        self.notebook.add(self.settings_tab, text="Settings")

        # Initialize each tab
        self.initialize_grow_log_tab()
        self.initialize_genetics_tab()
        self.initialize_lineage_tab()
        self.initialize_settings_tab()

    def load_config(self):
        logging.debug("Loading configuration...")
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as file:
                    config = json.load(file)
                    # Ensure all required colors are present
                    for key in DEFAULT_COLORS:
                        if key not in config:
                            config[key] = DEFAULT_COLORS[key]
                    logging.debug("Configuration loaded successfully.")
                    return config
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode config.json. Using default colors.")
                logging.error("Failed to decode config.json. Using default colors.")
                return DEFAULT_COLORS.copy()
        else:
            # Create config file with default colors
            with open(CONFIG_FILE, 'w') as file:
                json.dump(DEFAULT_COLORS, file, indent=4)
            logging.debug("Configuration file created with default colors.")
            return DEFAULT_COLORS.copy()

    def load_genetics_data(self):
        logging.debug("Loading genetics data...")
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
                    logging.debug("Genetics data loaded successfully.")
                    return {str(k): v for k, v in data.items()}
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode plant_genetics.json. Starting with empty data.")
                logging.error("Failed to decode plant_genetics.json. Starting with empty data.")
                return {}
        else:
            # Initial data with an empty dictionary
            logging.debug("plant_genetics.json not found. Starting with empty data.")
            return {}

    def get_parent_strains(self):
        logging.debug("Determining parent strains...")
        parents = set()
        for details in self.plant_genetics.values():
            lineage = details.get('lineage', '')
            if lineage and lineage != "Unknown":
                parent_list = [parent.strip() for parent in lineage.split(' x ')]
                parents.update(parent_list)
        logging.debug(f"Parent strains identified: {parents}")
        return parents

    def save_genetics_data(self):
        logging.debug("Saving genetics data...")
        with open(DATA_FILE, 'w') as file:
            json.dump(self.plant_genetics, file, indent=4)
        logging.debug("Genetics data saved successfully.")

    def initialize_grow_log_tab(self):
        logging.debug("Initializing Grow Log Tab...")
        # Initialize Grow Log App within the Grow Log Tab
        self.grow_log_app = GrowLogApp(self.grow_log_tab, self.plant_genetics, self)
        logging.debug("Grow Log Tab initialized successfully.")

    def initialize_genetics_tab(self):
        logging.debug("Initializing Genetics Tab...")
        # Top Frame with Search and Parent Strain Selector
        top_frame = tk.Frame(self.genetics_tab, bg=BACKGROUND_COLOR)
        top_frame.pack(pady=10, padx=20, fill='x')

        # Search Entry
        search_frame = tk.Frame(top_frame, bg=BACKGROUND_COLOR)
        search_frame.pack(fill='x')

        tk.Label(search_frame, text="Search:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_search_results)  # Ensure the method exists
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
        logging.debug("Genetics Tab initialized successfully.")

    def update_search_results(self, *args):
        """
        Updates the displayed plant buttons based on the search term and selected parent strain.
        This method is called whenever the search_var changes or a parent strain is selected.
        """
        logging.debug("Updating search results based on search term and selected parent strain.")
        
        # Retrieve the current search term and selected parent strain
        search_term = self.search_var.get().strip().lower()
        selected_parent = self.parent_strain_var.get()
        
        logging.debug(f"Search Term: '{search_term}', Selected Parent Strain: '{selected_parent}'")
        
        # Clear existing buttons in the genetics scrollable frame
        for widget in self.genetics_scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Filter strains based on ownership
        owned_strains = [name for name, details in self.plant_genetics.items() if details.get('owned', True)]
        
        # Further filter based on search term
        if search_term:
            owned_strains = [name for name in owned_strains if search_term in name.lower()]
        
        # Further filter based on selected parent strain if not "All Parents"
        if selected_parent != "All Parents":
            owned_strains = [name for name in owned_strains if selected_parent in self.plant_genetics[name].get('lineage', '')]
        
        logging.debug(f"Filtered Strains: {owned_strains}")
        
        # Sort the filtered strains alphabetically
        sorted_plants = sorted(owned_strains, key=lambda x: x.lower())
        
        # Arrange buttons in a grid layout
        columns = 5  # Number of columns in the grid
        row = 0
        column = 0
        for plant_name in sorted_plants:
            ownership_type = self.plant_genetics[plant_name].get('ownership_type', 'None')
            is_parent = plant_name in self.parent_strains
            is_owned = self.plant_genetics[plant_name].get('owned', True)

            # Determine the color based on ownership and type
            if is_parent and is_owned:
                color = self.legend_colors.get("Owned & Parent Strain", "#32CD32")
            elif not is_parent and is_owned:
                if ownership_type == "Seed Start":
                    color = self.legend_colors.get("Seed Start Strain", "#8000ff")
                elif ownership_type == "Clone":
                    color = self.legend_colors.get("Clone Strain", "#0000ff")
                else:
                    color = self.legend_colors.get("Owned Strain", "#0000ff")
            else:
                continue  # Skip strains that are not owned

            # Create the plant button
            btn = tk.Button(
                self.genetics_scrollable_frame.scrollable_frame,
                text=plant_name,
                width=20,
                command=lambda p=plant_name: self.show_plant_details(p),
                bg=color,
                fg=BACKGROUND_COLOR,
                font=("Helvetica", 12, "bold"),
                activebackground=color,
                activeforeground=BACKGROUND_COLOR
            )
            btn.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')

            column += 1
            if column >= columns:
                column = 0
                row += 1

        # Make the buttons expand equally within their columns
        for i in range(columns):
            self.genetics_scrollable_frame.scrollable_frame.columnconfigure(i, weight=1)

        logging.debug("Search results updated successfully.")

    def initialize_lineage_tab(self):
        logging.debug("Initializing Lineage Tree Tab...")
        # Selection Frame
        selection_frame = tk.Frame(self.lineage_tab, bg=BACKGROUND_COLOR)
        selection_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(selection_frame, text="Select Strain:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(side="left")
        self.plant_options_lineage = tk.StringVar(value="Select Strain")
        self.dropdown_lineage = tk.OptionMenu(selection_frame, self.plant_options_lineage, *sorted(self.plant_genetics.keys(), key=lambda x: x.lower()))
        self.dropdown_lineage.config(bg="white", fg="black", font=("Helvetica", 12))
        self.dropdown_lineage.pack(side="left", padx=10)

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
        logging.debug("Lineage Tree Tab initialized successfully.")

    def initialize_settings_tab(self):
        logging.debug("Initializing Settings Tab...")
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
        logging.debug("Settings Tab initialized successfully.")

    def create_legend(self):
        logging.debug("Creating legend...")
        # Clear existing legend_frame
        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        tk.Label(self.legend_frame, text="Legend:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 14, "bold")).pack(side="left", padx=(0, 20))

        for legend_item, color in self.legend_colors.items():
            legend = tk.Frame(self.legend_frame, bg=color, width=25, height=25)
            legend.pack(side="left", padx=5)
            legend.pack_propagate(False)
            tk.Label(self.legend_frame, text=legend_item, bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(side="left", padx=(0, 20))
        logging.debug("Legend created successfully.")

    def customize_colors(self):
        logging.debug("Opening Customize Colors window...")
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
        logging.debug("Customize Colors window opened.")

    def choose_color(self, legend_item):
        logging.debug(f"Choosing color for {legend_item}...")
        color_code = colorchooser.askcolor(title=f"Choose color for {legend_item}")
        if color_code and color_code[1]:
            self.legend_colors[legend_item] = color_code[1]
            self.color_buttons[legend_item].configure(bg=color_code[1])
            logging.debug(f"Color for {legend_item} set to {color_code[1]}.")

    def reset_colors(self):
        logging.debug("Resetting colors to default...")
        for key in DEFAULT_COLORS:
            self.legend_colors[key] = DEFAULT_COLORS[key]
            if key in self.color_buttons:
                self.color_buttons[key].configure(bg=DEFAULT_COLORS[key])
        logging.debug("Colors reset to default.")

    def save_colors(self, window):
        logging.debug("Saving customized colors...")
        with open(CONFIG_FILE, 'w') as file:
            json.dump(self.legend_colors, file, indent=4)

        # Update the legend in the UI
        self.update_legend_colors()

        window.destroy()
        messagebox.showinfo("Colors Saved", "Legend colors have been updated successfully.")
        logging.debug("Customized colors saved and window closed.")

    def update_legend_colors(self):
        logging.debug("Updating legend colors in UI...")
        self.create_legend()
        # Refresh the genetics buttons to apply color changes if necessary
        self.display_genetics_buttons()
        logging.debug("Legend colors updated.")

    def delete_all_data(self):
        logging.debug("Attempting to delete all data...")
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
            logging.debug("All data deleted and UI updated.")

    def create_entry_fields(self, parent):
        logging.debug("Creating entry fields for Add / Update Plant...")
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

        logging.debug("Entry fields created successfully.")

    def display_genetics_buttons(self):
        logging.debug("Displaying Genetics Buttons...")
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
                    color = self.legend_colors.get("Seed Start Strain", "#8000ff")
                elif ownership_type == "Clone":
                    color = self.legend_colors.get("Clone Strain", "#0000ff")
                else:
                    color = self.legend_colors.get("Owned Strain", "#0000ff")
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
        logging.debug("Genetics Buttons displayed successfully.")

    def add_or_update_plant(self):
        logging.debug("Adding or updating plant...")
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
            logging.warning("Strain name not provided.")
            return

        # Handle Clone Naming
        if ownership_type == "Clone":
            # Extract mother plant from lineage
            if not lineage or lineage == "Unknown":
                messagebox.showwarning("Invalid Lineage", "Please specify a valid lineage for cloning.")
                logging.warning("Invalid lineage for cloning.")
                return
            parents = [parent.strip() for parent in lineage.split(" x ")]
            if not parents:
                messagebox.showwarning("Invalid Lineage", "Please specify at least one mother plant.")
                logging.warning("No parents specified for cloning.")
                return
            mother_plant = parents[0]  # Assuming the first parent is the mother

            if mother_plant not in self.plant_genetics:
                messagebox.showwarning("Unknown Mother Plant", f"The mother plant '{mother_plant}' does not exist.")
                logging.warning(f"Mother plant '{mother_plant}' does not exist.")
                return

            # Generate clone name
            clone_count = self.plant_genetics[mother_plant].get('clone_count', 0) + 1
            clone_suffix = self.get_clone_suffix(clone_count)
            clone_name = f"{mother_plant} Clone {clone_suffix}"

            if clone_name in self.plant_genetics:
                messagebox.showwarning("Duplicate Clone", f"The clone name '{clone_name}' already exists.")
                logging.warning(f"Clone name '{clone_name}' already exists.")
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
                        logging.info(f"Added unknown parent strain '{parent}'.")
                    else:
                        logging.warning(f"Unknown parent strain '{parent}' not added.")
                        return

        # If updating an existing strain with a different name
        original_name = plant_name  # Store the original name
        if name in self.plant_genetics and original_name != name:
            del self.plant_genetics[original_name]

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
        logging.debug(f"Plant '{name}' added/updated successfully.")

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
        logging.debug("Clearing entry fields...")
        self.entry_name.delete(0, tk.END)
        self.entry_lineage.delete(0, tk.END)
        self.gender_var.set("Female")
        self.owned_var.set(True)
        self.ownership_type_var.set("None")
        self.entry_yield.delete(0, tk.END)
        self.entry_flowering_time.delete(0, tk.END)
        self.entry_type.delete(0, tk.END)
        self.entry_notes.delete(0, tk.END)
        logging.debug("Entry fields cleared.")

    def update_dropdown_options(self):
        logging.debug("Updating dropdown options...")
        # Update options in the Lineage Tree tab
        menu = self.dropdown_lineage["menu"]
        menu.delete(0, "end")
        for strain in sorted(self.plant_genetics.keys(), key=lambda x: x.lower()):
            menu.add_command(label=strain, command=lambda value=strain: self.plant_options_lineage.set(value))
        self.plant_options_lineage.set("Select Strain")  # Reset selection

        # Update options in Grow Log strain selection
        if hasattr(self.grow_log_app, 'strain_var'):
            strain_options = ["Select Strain"] + sorted(self.plant_genetics.keys(), key=lambda x: x.lower())
            menu = self.grow_log_app.strain_dropdown["menu"]
            menu.delete(0, "end")
            for strain in strain_options:
                menu.add_command(label=strain, command=lambda value=strain: self.grow_log_app.strain_var.set(value))
            self.grow_log_app.strain_var.set("Select Strain")

        # Update options in the Genetics tab parent strain dropdown
        menu = self.parent_strain_dropdown["menu"]
        menu.delete(0, "end")
        parent_strain_options = ["All Parents"] + sorted(self.parent_strains, key=lambda x: x.lower())
        for parent in parent_strain_options:
            menu.add_command(label=parent, command=lambda value=parent: self.parent_strain_var.set(value))
        self.parent_strain_var.set("All Parents")
        logging.debug("Dropdown options updated.")

    def update_genetic_traits_tree(self):
        # Implement the method to update the genetic traits tree
        # This could involve redrawing the tree or updating related UI elements
        logging.debug("Updating genetic traits tree...")
        # ... [Implement as needed]
        pass  # Replace with actual implementation

    def show_plant_details(self, plant_name):
        logging.debug(f"Showing details for plant '{plant_name}'...")
        if plant_name not in self.plant_genetics:
            messagebox.showerror("Error", f"Plant '{plant_name}' not found.")
            logging.error(f"Plant '{plant_name}' not found.")
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

        # Left frame for plant's details
        left_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        # Right frame for clones
        right_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
        right_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

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

        logging.debug(f"Details for plant '{plant_name}' displayed successfully.")

    def show_clone_grow_log(self, clone_name):
        logging.debug(f"Showing Grow Log for clone '{clone_name}'...")
        # Implement the method to show clone's grow log
        # This can involve opening a new window similar to GrowLogApp
        clone_log_window = Toplevel(self.root)
        clone_log_window.title(f"Grow Log for {clone_name}")
        clone_log_window.geometry("600x600")
        clone_log_window.configure(bg=BACKGROUND_COLOR)

        clone_log_app = GrowLogApp(clone_log_window, self.plant_genetics, self)
        clone_log_app.display_log_entries_for_clone(clone_name)
        logging.debug(f"Grow Log for clone '{clone_name}' displayed successfully.")

    def display_lineage_tree(self):
        logging.debug("Displaying lineage tree...")
        plant_name = self.plant_options_lineage.get()
        if plant_name not in self.plant_genetics:
            messagebox.showerror("Error", "Please select a valid strain.")
            logging.error("Invalid strain selected for lineage tree.")
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
                    node_color = self.legend_colors.get("Clone Strain", "#0000ff")
                elif ownership_type == "Seed Start":
                    node_color = self.legend_colors.get("Seed Start Strain", "#8000ff")
                else:
                    node_color = self.legend_colors.get("Owned Strain", "#0000ff")
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
            logging.debug("Lineage tree displayed successfully.")
        except graphviz.backend.ExecutableNotFound:
            messagebox.showerror("Graphviz Not Found", "Graphviz executable not found. Please install Graphviz and ensure it's added to your system's PATH.")
            logging.error("Graphviz executable not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate lineage tree.\n{e}")
            logging.error(f"Failed to generate lineage tree: {e}")

    def open_genetic_info_window(self, plant_name):
        logging.debug(f"Opening genetic information window for '{plant_name}'...")
        # Implement the method to open a window for genetic information
        genetic_info_window = Toplevel(self.root)
        genetic_info_window.title(f"Genetic Information for {plant_name}")
        genetic_info_window.geometry("600x400")
        genetic_info_window.configure(bg=BACKGROUND_COLOR)

        genetic_info = self.plant_genetics[plant_name].get('genetic_info', {})

        info_text = f"Genetic Information for {plant_name}:\n\n"
        for key, value in genetic_info.items():
            info_text += f"{key}: {value}\n"

        tk.Label(genetic_info_window, text=info_text, justify="left", padx=10, pady=10,
                 bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12)).pack(fill='both', expand=True)
        logging.debug(f"Genetic information window for '{plant_name}' opened.")

    def update_plant_details(self, plant_name, window):
        logging.debug(f"Updating details for plant '{plant_name}'...")
        # Retrieve updated details from the edit fields
        updated_name = self.edit_entry_name.get().strip()
        updated_lineage = self.edit_entry_lineage.get().strip()
        updated_yield = self.edit_entry_yield.get().strip()
        updated_flowering_time = self.edit_entry_flowering_time.get().strip()
        updated_type = self.edit_entry_type.get().strip()
        updated_gender = self.edit_gender_var.get()
        updated_owned = self.edit_owned_var.get()
        updated_ownership_type = self.edit_ownership_type_var.get()
        updated_notes = self.edit_entry_notes.get().strip()

        # Validate inputs
        if not updated_name:
            messagebox.showwarning("Incomplete Data", "Strain name cannot be empty.")
            logging.warning("Attempted to update plant with empty name.")
            return

        # Update the plant details
        self.plant_genetics[plant_name].update({
            "lineage": updated_lineage if updated_lineage else "Unknown",
            "yield": updated_yield if updated_yield else "Unknown",
            "flowering_time": updated_flowering_time if updated_flowering_time else "Unknown",
            "type": updated_type if updated_type else "Unknown",
            "gender": updated_gender if updated_gender else "Unknown",
            "owned": updated_owned,
            "ownership_type": updated_ownership_type if updated_owned else "None",
            "notes": updated_notes if updated_notes else ""
        })

        self.save_genetics_data()
        self.display_genetics_buttons()
        self.update_dropdown_options()
        self.update_genetic_traits_tree()

        messagebox.showinfo("Success", f"Details for '{plant_name}' have been updated.")
        logging.debug(f"Details for plant '{plant_name}' updated successfully.")
        window.destroy()

    def delete_plant(self, plant_name, window):
        logging.debug(f"Attempting to delete plant '{plant_name}'...")
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the plant '{plant_name}'?"):
            del self.plant_genetics[plant_name]
            self.save_genetics_data()
            self.display_genetics_buttons()
            self.update_dropdown_options()
            self.update_genetic_traits_tree()
            messagebox.showinfo("Deleted", f"Plant '{plant_name}' has been deleted.")
            logging.debug(f"Plant '{plant_name}' deleted successfully.")
            window.destroy()

    def show_clone_grow_log(self, clone_name):
        logging.debug(f"Showing Grow Log for clone '{clone_name}'...")
        # Implement the method to show clone's grow log
        # This can involve opening a new window similar to GrowLogApp
        clone_log_window = Toplevel(self.root)
        clone_log_window.title(f"Grow Log for {clone_name}")
        clone_log_window.geometry("600x600")
        clone_log_window.configure(bg=BACKGROUND_COLOR)

        clone_log_app = GrowLogApp(clone_log_window, self.plant_genetics, self)
        clone_log_app.display_log_entries_for_clone(clone_name)
        logging.debug(f"Grow Log for clone '{clone_name}' displayed successfully.")

    def main(self):
        self.root.mainloop()

    @staticmethod
    def run_app():
        root = tk.Tk()
        app = CannabisGeneticsApp(root)
        app.main()

if __name__ == "__main__":
    CannabisGeneticsApp.run_app()
