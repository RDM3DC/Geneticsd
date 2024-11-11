import tkinter as tk
from tkinter import messagebox
import graphviz
from PIL import Image, ImageTk  # Requires Pillow package (install with `pip install pillow`)

# Sample genetics data
plant_genetics = {
    "Sugermill": {
        "lineage": "Gorilla Glue #4 x Wedding Cake",
        "yield": "250-300 gpsm",
        "flowering_time": "65-70 days",
        "type": "Hybrid (Sativa/Indica)",
        "notes": "Wedding Cake (Triangle Kush x Animal Mints), Gorilla Glue (Sour Dubb x Chocolate Diesel)",
        "gender": "Female"  # Default gender
    },
    "Jupiter": {
        "lineage": "Jupiter OG Kush x Tahoe OG S1 (Reversed)",
        "flowering_time": "65-70 days",
        "type": "55% Sativa / 45% Indica",
        "notes": "Clone only",
        "gender": "Female"
    },
    "Jedi Kush": {
        "lineage": "Deathstar x SFV OG Kush IBL",
        "yield": "Large",
        "flowering_time": "8-9 weeks",
        "type": "Hybrid (Indica/Sativa)",
        "notes": "Deathstar (Sensi Star x Sour Diesel)",
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
    }
}

# Initialize the main app window
root = tk.Tk()
root.title("Cannabis Genetics Tracker")
root.geometry("800x600")

# Function to display all genetics
def display_genetics():
    genetics_text.delete("1.0", tk.END)  # Clear previous text
    for plant, details in plant_genetics.items():
        genetics_text.insert(tk.END, f"{plant} ({details['gender']}) Genetics:\n")
        for key, value in details.items():
            if key != 'gender':  # Exclude gender from the main details display
                genetics_text.insert(tk.END, f"  {key.capitalize()}: {value}\n")
        genetics_text.insert(tk.END, "\n")

# Function to add a new cross
def add_cross():
    new_name = entry_name.get()
    parent1 = entry_parent1.get()
    parent2 = entry_parent2.get()
    gender = gender_var.get()
    notes = entry_notes.get()

    if not new_name or not parent1 or not parent2:
        messagebox.showwarning("Incomplete Data", "Please fill out all required fields.")
        return

    lineage = f"{parent1} x {parent2}"
    plant_genetics[new_name] = {
        "lineage": lineage,
        "yield": "Unknown",
        "flowering_time": "Unknown",
        "type": "Hybrid",
        "notes": notes,
        "gender": gender
    }
    
    # Update dropdown options with the new cross
    plant_options.set(new_name)  # Set new plant as the selected option
    dropdown["menu"].add_command(label=new_name, command=tk._setit(plant_options, new_name))
    
    display_genetics()  # Refresh display to show new entry
    messagebox.showinfo("New Cross Added", f"{new_name} ({gender}) has been added!")

# Function to generate and display the full lineage tree, including all ancestors
def display_lineage_tree():
    plant_name = plant_options.get()
    if plant_name not in plant_genetics:
        messagebox.showerror("Error", "Plant not found.")
        return
    
    # Generate a directed graph using Graphviz
    dot = graphviz.Digraph(comment=plant_name)
    
    # Recursive function to add ancestors to the tree
    def add_to_tree(name):
        if name not in plant_genetics:
            dot.node(name, name)  # If no known lineage, add as-is
            return
        
        current_plant = plant_genetics[name]
        gender = current_plant.get("gender", "Unknown")
        label = f"{name}\n({gender})"  # Display plant name and gender
        dot.node(name, label)
        
        lineage = current_plant["lineage"]
        
        if " x " in lineage:  # Split lineage if there are two parents
            parent1, parent2 = lineage.split(" x ")
            dot.node(parent1, parent1)
            dot.node(parent2, parent2)
            dot.edge(parent1, name)
            dot.edge(parent2, name)
            # Recursively add parent lineage
            add_to_tree(parent1)
            add_to_tree(parent2)

    # Start building tree from the selected plant
    add_to_tree(plant_name)

    # Render the graph to a PNG file
    dot.render("lineage_tree", format="png")
    img = Image.open("lineage_tree.png")
    img = img.resize((400, 400), Image.LANCZOS)  # Increased size for better readability
    img = ImageTk.PhotoImage(img)
    
    # Display the lineage tree in the app
    tree_label.config(image=img)
    tree_label.image = img

# UI elements
genetics_frame = tk.Frame(root)
genetics_frame.pack(pady=10)

genetics_text = tk.Text(genetics_frame, width=60, height=15)
genetics_text.pack()

btn_display = tk.Button(root, text="Display All Genetics", command=display_genetics)
btn_display.pack(pady=5)

# Fields for new cross entry
entry_frame = tk.Frame(root)
entry_frame.pack(pady=10)

tk.Label(entry_frame, text="New Cross Name:").grid(row=0, column=0)
entry_name = tk.Entry(entry_frame)
entry_name.grid(row=0, column=1)

tk.Label(entry_frame, text="Parent 1:").grid(row=1, column=0)
entry_parent1 = tk.Entry(entry_frame)
entry_parent1.grid(row=1, column=1)

tk.Label(entry_frame, text="Parent 2:").grid(row=2, column=0)
entry_parent2 = tk.Entry(entry_frame)
entry_parent2.grid(row=2, column=1)

tk.Label(entry_frame, text="Gender:").grid(row=3, column=0)
gender_var = tk.StringVar(value="Female")  # Default gender
gender_menu = tk.OptionMenu(entry_frame, gender_var, "Female", "Male")
gender_menu.grid(row=3, column=1)

tk.Label(entry_frame, text="Notes:").grid(row=4, column=0)
entry_notes = tk.Entry(entry_frame)
entry_notes.grid(row=4, column=1)

btn_add = tk.Button(root, text="Add New Cross", command=add_cross)
btn_add.pack(pady=5)

# Dropdown menu for lineage tree selection
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10)

# Create a StringVar and populate dropdown with initial plant options
plant_options = tk.StringVar(value="Select Plant")
dropdown = tk.OptionMenu(tree_frame, plant_options, *plant_genetics.keys())
dropdown.grid(row=0, column=1)

btn_lineage = tk.Button(tree_frame, text="Show Lineage Tree", command=display_lineage_tree)
btn_lineage.grid(row=0, column=2)

tree_label = tk.Label(root)  # Label to display lineage tree image
tree_label.pack()

# Start app loop
display_genetics()  # Initial display of genetics
root.mainloop()
