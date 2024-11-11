import tkinter as tk
from tkinter import messagebox, Toplevel
import graphviz
from PIL import Image, ImageTk  # Requires Pillow package (install with `pip install pillow`)
import json
import os

# Constants
DATA_FILE = 'plant_genetics.json'

# Rasta Colors
RASTA_RED = "#FFFFFF"
RASTA_GOLD = "#000000"
RASTA_GREEN = "#FFFFFF"
RASTA_DARK_GREEN = "#006400"
RASTA_LIGHT_GOLD = "#FFFACD"
TEXT_COLOR = "#000000"  # Black for readability

class CannabisGeneticsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cannabis Genetics Tracker")
        self.root.geometry("1000x800")
        self.root.configure(bg=RASTA_GREEN)  # Set main background to Rasta green
        
        # Load genetics data
        self.plant_genetics = self.load_genetics_data()
        
        # Initialize UI elements
        self.create_widgets()
        self.display_genetics_buttons()

    def load_genetics_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as file:
                    data = json.load(file)
                    # Convert keys to strings in case they're not
                    return {str(k): v for k, v in data.items()}
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Failed to decode JSON data. Starting with empty data.")
                return {}
        else:
            # Initial data with all provided strains
            initial_data = {
                "Sugermill #1": {
                    "lineage": "Gorilla Glue #4 x Wedding Cake",
                    "yield": "250-300 gpsm",
                    "flowering_time": "65-70 days",
                    "type": "Hybrid (Sativa/Indica)",
                    "notes": "Wedding Cake (Triangle Kush x Animal Mints), Gorilla Glue (Sour Dubb x Chocolate Diesel)",
                    "gender": "Female"
                },
                "Sugermill #2": {
                    "lineage": "Gorilla Glue #4 x Wedding Cake",
                    "yield": "250-300 gpsm",
                    "flowering_time": "65-70 days",
                    "type": "Hybrid (Sativa/Indica)",
                    "notes": "Slightly taller, different trichome density",
                    "gender": "Female"
                },
                "Jedi Kush #1": {
                    "lineage": "Deathstar x SFV OG Kush IBL",
                    "yield": "Large",
                    "flowering_time": "8-9 weeks",
                    "type": "Hybrid (Indica/Sativa)",
                    "notes": "Deathstar (Sensi Star x Sour Diesel)",
                    "gender": "Female"
                },
                "Jedi Kush #2": {
                    "lineage": "Deathstar x SFV OG Kush IBL",
                    "yield": "Large",
                    "flowering_time": "8-9 weeks",
                    "type": "Hybrid (Indica/Sativa)",
                    "notes": "More indica-like growth structure",
                    "gender": "Female"
                },
                "Jedi Kush #3": {
                    "lineage": "Deathstar x SFV OG Kush IBL",
                    "yield": "Large",
                    "flowering_time": "8-9 weeks",
                    "type": "Hybrid (Indica/Sativa)",
                    "notes": "Fastest flowering time",
                    "gender": "Female"
                },
                "Jupiter": {
                    "lineage": "Jupiter OG Kush x Tahoe OG S1 (Reversed)",
                    "flowering_time": "65-70 days",
                    "type": "55% Sativa / 45% Indica",
                    "notes": "Single phenotype with high resin production",
                    "gender": "Female"
                },
                "Deathstar": {
                    "lineage": "Sensi Star x Sour Diesel",
                    "type": "Hybrid",
                    "notes": "Known for potency and high THC content",
                    "gender": "Female"
                },
                "Wedding Cake": {
                    "lineage": "Triangle Kush x Animal Mints",
                    "type": "Indica-dominant Hybrid",
                    "notes": "High yield, good for trichome production",
                    "gender": "Unknown"
                },
                "Gorilla Glue #4": {
                    "lineage": "Sour Dubb x Chocolate Diesel",
                    "type": "Hybrid",
                    "notes": "Known for high resin production",
                    "gender": "Unknown"
                },
                "Sensi Star": {
                    "lineage": "Unknown",
                    "type": "Indica",
                    "notes": "Known for high potency",
                    "gender": "Female"
                },
                "Sour Diesel": {
                    "lineage": "Unknown",
                    "type": "Sativa",
                    "notes": "Classic strain with uplifting effects",
                    "gender": "Female"
                },
                "Jupiter OG Kush": {
                    "lineage": "Unknown",
                    "type": "Hybrid",
                    "notes": "Parent of Jupiter, known for strong OG genetics",
                    "gender": "Unknown"
                },
                "Tahoe OG S1 (Reversed)": {
                    "lineage": "Unknown",
                    "type": "Indica-dominant Hybrid",
                    "notes": "Reversed phenotype of Tahoe OG used in breeding",
                    "gender": "Male"
                }
            }
            return initial_data

    def save_genetics_data(self):
        with open(DATA_FILE, 'w') as file:
            json.dump(self.plant_genetics, file, indent=4)

    def create_widgets(self):
        # Search Entry
        search_frame = tk.Frame(self.root, bg=RASTA_GREEN)
        search_frame.pack(pady=5, fill='x', padx=10)
        
        tk.Label(search_frame, text="Search:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 12, "bold")).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.update_search_results)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 12))
        self.search_entry.pack(side="left", fill='x', expand=True, padx=5)
        self.search_entry.insert(0, '')  # Start with empty search

        # Genetics Buttons Frame
        self.genetics_frame = tk.Frame(self.root, bg=RASTA_GREEN)
        self.genetics_frame.pack(pady=10, padx=10, fill='both', expand=True)

        # Add Plant Frame
        add_frame = tk.LabelFrame(self.root, text="Add / Update Plant", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"))
        add_frame.pack(pady=10, padx=10, fill='x')
        self.create_entry_fields(add_frame)

        # Lineage Tree Frame
        lineage_frame = tk.LabelFrame(self.root, text="Lineage Tree", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"))
        lineage_frame.pack(pady=10, padx=10, fill='x')
        self.create_lineage_tree_widgets(lineage_frame)

        # Image Display Label
        self.tree_label = tk.Label(self.root, bg=RASTA_GREEN)
        self.tree_label.pack(pady=10)

    def create_entry_fields(self, parent):
        # Grid configuration for better layout
        for i in range(4):
            parent.columnconfigure(i, weight=1, pad=5)

        # Row 0
        tk.Label(parent, text="Strain Name:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=0, column=0, sticky='e')
        self.entry_name = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_name.grid(row=0, column=1, sticky='we', padx=5, pady=2)

        tk.Label(parent, text="Yield:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=0, column=2, sticky='e')
        self.entry_yield = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_yield.grid(row=0, column=3, sticky='we', padx=5, pady=2)

        # Row 1
        tk.Label(parent, text="Parent 1:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=1, column=0, sticky='e')
        self.entry_parent1 = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_parent1.grid(row=1, column=1, sticky='we', padx=5, pady=2)

        tk.Label(parent, text="Flowering Time:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=1, column=2, sticky='e')
        self.entry_flowering_time = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_flowering_time.grid(row=1, column=3, sticky='we', padx=5, pady=2)

        # Row 2
        tk.Label(parent, text="Parent 2:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=2, column=0, sticky='e')
        self.entry_parent2 = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_parent2.grid(row=2, column=1, sticky='we', padx=5, pady=2)

        tk.Label(parent, text="Type:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=2, column=2, sticky='e')
        self.entry_type = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_type.grid(row=2, column=3, sticky='we', padx=5, pady=2)

        # Row 3
        tk.Label(parent, text="Gender:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=3, column=0, sticky='e')
        self.gender_var = tk.StringVar(value="Female")
        gender_options = ["Female", "Male", "Unknown"]
        self.gender_menu = tk.OptionMenu(parent, self.gender_var, *gender_options)
        self.gender_menu.config(bg=RASTA_RED, fg=RASTA_GOLD, activebackground=RASTA_RED, activeforeground=RASTA_GOLD, font=("Helvetica", 11))
        self.gender_menu.grid(row=3, column=1, sticky='w', padx=5, pady=2)

        tk.Label(parent, text="Notes:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=3, column=2, sticky='e')
        self.entry_notes = tk.Entry(parent, font=("Helvetica", 11))
        self.entry_notes.grid(row=3, column=3, sticky='we', padx=5, pady=2)

        # Add / Update Button
        self.btn_add = tk.Button(parent, text="Add / Update Plant", command=self.add_or_update_plant,
                                 bg=RASTA_RED, fg=RASTA_GOLD, font=("Helvetica", 12, "bold"), activebackground=RASTA_GOLD, activeforeground=RASTA_RED)
        self.btn_add.grid(row=4, column=0, columnspan=4, pady=10)

    def create_lineage_tree_widgets(self, parent):
        # Grid configuration
        parent.columnconfigure(1, weight=1, pad=5)

        tk.Label(parent, text="Select Plant:", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.plant_options = tk.StringVar(value="Select Plant")
        self.dropdown = tk.OptionMenu(parent, self.plant_options, *self.plant_genetics.keys())
        self.dropdown.config(bg=RASTA_RED, fg=RASTA_GOLD, activebackground=RASTA_RED, activeforeground=RASTA_GOLD, font=("Helvetica", 11))
        self.dropdown.grid(row=0, column=1, sticky='we', padx=5, pady=5)

        self.btn_lineage = tk.Button(parent, text="Show Lineage Tree", command=self.display_lineage_tree,
                                     bg=RASTA_RED, fg=RASTA_GOLD, font=("Helvetica", 12, "bold"),
                                     activebackground=RASTA_GOLD, activeforeground=RASTA_RED)
        self.btn_lineage.grid(row=0, column=2, padx=5, pady=5)

    def display_genetics_buttons(self):
        # Clear existing buttons
        for widget in self.genetics_frame.winfo_children():
            widget.destroy()
        
        # Sort plant names alphabetically
        sorted_plants = sorted(self.plant_genetics.keys(), key=lambda x: x.lower())

        # Arrange buttons in grid
        columns = 4  # Number of columns in grid
        row = 0
        column = 0
        for plant_name in sorted_plants:
            btn = tk.Button(self.genetics_frame, text=plant_name, width=20,
                            command=lambda p=plant_name: self.show_plant_details(p),
                            bg=RASTA_RED, fg=RASTA_GOLD, font=("Helvetica", 11, "bold"),
                            activebackground=RASTA_GOLD, activeforeground=RASTA_RED)
            btn.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
            column += 1
            if column >= columns:
                column = 0
                row +=1

        # Make buttons expand equally
        for i in range(columns):
            self.genetics_frame.columnconfigure(i, weight=1)

    def show_plant_details(self, plant_name):
        if plant_name not in self.plant_genetics:
            messagebox.showerror("Error", "Plant not found.")
            return

        details = self.plant_genetics[plant_name]

        # Create a new Toplevel window (popup)
        details_window = Toplevel(self.root)
        details_window.title(f"{plant_name} Details")
        details_window.geometry("400x400")
        details_window.configure(bg=RASTA_GREEN)

        # Display plant details in the popup
        info_text = f"{plant_name} ({details.get('gender', 'Unknown')})\n\n"
        for key, value in details.items():
            if key != "gender":
                info_text += f"{key.capitalize()}: {value}\n"

        label = tk.Label(details_window, text=info_text, justify="left", padx=10, pady=10,
                         bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11))
        label.pack(fill='both', expand=True)

        # Edit and Delete Buttons
        btn_frame = tk.Frame(details_window, bg=RASTA_GREEN)
        btn_frame.pack(pady=10)

        btn_edit = tk.Button(btn_frame, text="Edit", command=lambda: self.edit_plant(plant_name, details_window),
                             bg=RASTA_RED, fg=RASTA_GOLD, font=("Helvetica", 10, "bold"),
                             activebackground=RASTA_GOLD, activeforeground=RASTA_RED)
        btn_edit.pack(side='left', padx=10)

        btn_delete = tk.Button(btn_frame, text="Delete", command=lambda: self.delete_plant(plant_name, details_window),
                               bg=RASTA_RED, fg=RASTA_GOLD, font=("Helvetica", 10, "bold"),
                               activebackground=RASTA_GOLD, activeforeground=RASTA_RED)
        btn_delete.pack(side='right', padx=10)

    def edit_plant(self, plant_name, window):
        window.destroy()
        details = self.plant_genetics[plant_name]

        # Populate the entry fields with existing data
        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, plant_name)

        lineage = details.get('lineage', '')
        parents = [parent.strip() for parent in lineage.split(' x ')]
        parent1 = parents[0] if len(parents) > 0 else ''
        parent2 = parents[1] if len(parents) > 1 else ''

        self.entry_parent1.delete(0, tk.END)
        self.entry_parent1.insert(0, parent1)
        self.entry_parent2.delete(0, tk.END)
        self.entry_parent2.insert(0, parent2)

        self.gender_var.set(details.get('gender', 'Unknown'))
        self.entry_yield.delete(0, tk.END)
        self.entry_yield.insert(0, details.get('yield', ''))
        self.entry_flowering_time.delete(0, tk.END)
        self.entry_flowering_time.insert(0, details.get('flowering_time', ''))
        self.entry_type.delete(0, tk.END)
        self.entry_type.insert(0, details.get('type', ''))
        self.entry_notes.delete(0, tk.END)
        self.entry_notes.insert(0, details.get('notes', ''))

    def delete_plant(self, plant_name, window):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{plant_name}'?"):
            del self.plant_genetics[plant_name]
            self.save_genetics_data()
            self.display_genetics_buttons()
            self.update_dropdown_options()
            window.destroy()
            messagebox.showinfo("Deleted", f"'{plant_name}' has been deleted.")

    def add_or_update_plant(self):
        name = self.entry_name.get().strip()
        parent1 = self.entry_parent1.get().strip()
        parent2 = self.entry_parent2.get().strip()
        gender = self.gender_var.get()
        yield_info = self.entry_yield.get().strip()
        flowering_time = self.entry_flowering_time.get().strip()
        plant_type = self.entry_type.get().strip()
        notes = self.entry_notes.get().strip()

        if not name:
            messagebox.showwarning("Incomplete Data", "Please enter the strain name.")
            return

        # Optional: Validate that parents exist or are 'Unknown'
        if parent1 and parent1 not in self.plant_genetics:
            if messagebox.askyesno("Unknown Parent", f"Parent 1 '{parent1}' does not exist. Do you want to add it as a new plant?"):
                # Add parent1 as a new plant with minimal information
                self.plant_genetics[parent1] = {
                    "lineage": "Unknown",
                    "yield": "Unknown",
                    "flowering_time": "Unknown",
                    "type": "Unknown",
                    "notes": "",
                    "gender": "Unknown"
                }
            else:
                return

        if parent2 and parent2 not in self.plant_genetics:
            if messagebox.askyesno("Unknown Parent", f"Parent 2 '{parent2}' does not exist. Do you want to add it as a new plant?"):
                # Add parent2 as a new plant with minimal information
                self.plant_genetics[parent2] = {
                    "lineage": "Unknown",
                    "yield": "Unknown",
                    "flowering_time": "Unknown",
                    "type": "Unknown",
                    "notes": "",
                    "gender": "Unknown"
                }
            else:
                return

        lineage = f"{parent1} x {parent2}" if parent1 and parent2 else "Unknown"

        self.plant_genetics[name] = {
            "lineage": lineage,
            "yield": yield_info or "Unknown",
            "flowering_time": flowering_time or "Unknown",
            "type": plant_type or "Unknown",
            "notes": notes or "",
            "gender": gender or "Unknown"
        }

        self.save_genetics_data()
        self.display_genetics_buttons()
        self.update_dropdown_options()
        messagebox.showinfo("Success", f"'{name}' has been added/updated!")

        # Clear input fields
        self.clear_entry_fields()

    def clear_entry_fields(self):
        self.entry_name.delete(0, tk.END)
        self.entry_parent1.delete(0, tk.END)
        self.entry_parent2.delete(0, tk.END)
        self.gender_var.set("Female")
        self.entry_yield.delete(0, tk.END)
        self.entry_flowering_time.delete(0, tk.END)
        self.entry_type.delete(0, tk.END)
        self.entry_notes.delete(0, tk.END)

    def update_dropdown_options(self):
        menu = self.dropdown["menu"]
        menu.delete(0, "end")
        for plant in sorted(self.plant_genetics.keys(), key=lambda x: x.lower()):
            menu.add_command(label=plant, command=lambda value=plant: self.plant_options.set(value))
        self.plant_options.set("Select Plant")  # Reset selection

    def update_search_results(self, *args):
        search_term = self.search_var.get().lower()
        for widget in self.genetics_frame.winfo_children():
            widget.destroy()

        filtered_plants = sorted(
            [plant for plant in self.plant_genetics.keys() if search_term in plant.lower()],
            key=lambda x: x.lower()
        )

        if not filtered_plants:
            tk.Label(self.genetics_frame, text="No matching plants found.", bg=RASTA_GREEN, fg=TEXT_COLOR, font=("Helvetica", 11)).pack()
            return

        columns = 4
        row = 0
        column = 0
        for plant_name in filtered_plants:
            btn = tk.Button(self.genetics_frame, text=plant_name, width=20,
                            command=lambda p=plant_name: self.show_plant_details(p),
                            bg=RASTA_RED, fg=RASTA_GOLD, font=("Helvetica", 11, "bold"),
                            activebackground=RASTA_GOLD, activeforeground=RASTA_RED)
            btn.grid(row=row, column=column, padx=5, pady=5, sticky='nsew')
            column += 1
            if column >= columns:
                column = 0
                row += 1

        # Make buttons expand equally
        for i in range(columns):
            self.genetics_frame.columnconfigure(i, weight=1)

    def display_lineage_tree(self):
        plant_name = self.plant_options.get()
        if plant_name not in self.plant_genetics:
            messagebox.showerror("Error", "Please select a valid plant.")
            return

        dot = graphviz.Digraph(comment=plant_name)
        visited = set()

        def add_to_tree(name):
            if name in visited:
                return  # Prevent duplicate nodes
            visited.add(name)

            if name not in self.plant_genetics:
                dot.node(name, name)
                return

            current_plant = self.plant_genetics[name]
            gender = current_plant.get("gender", "Unknown")
            label = f"{name}\n({gender})"
            dot.node(name, label)

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
            img = img.resize((600, 600), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

            self.tree_label.config(image=img)
            self.tree_label.image = img
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate lineage tree.\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CannabisGeneticsApp(root)
    root.mainloop()
