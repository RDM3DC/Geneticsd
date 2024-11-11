# grow_log.py
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from datetime import datetime
import json
import os
from constants import GROW_LOG_FILE, BACKGROUND_COLOR, TEXT_COLOR
from components import ScrollableFrame

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

        btn_save = tk.Button(btn_frame, text="Save Changes", command=lambda: self.save_edit_log_entry(idx, entry_date.get().strip(),
                                                                                                       activity_var.get().strip(),
                                                                                                       strain_var.get().strip(),
                                                                                                       entry_notes.get().strip(),
                                                                                                       status_var.get().strip(),
                                                                                                       edit_window),
                             bg="white", fg="black", font=("Helvetica", 12, "bold"),
                             activebackground="lightgrey", activeforeground="black")
        btn_save.pack(side='left', padx=20)

        btn_delete = tk.Button(btn_frame, text="Delete Entry", command=lambda: self.delete_log_entry(idx, edit_window),
                               bg="white", fg="black", font=("Helvetica", 12, "bold"),
                               activebackground="lightgrey", activeforeground="black")
        btn_delete.pack(side='right', padx=20)

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

    def show_plant_details(self, plant_name):
        # Implementation remains the same
        # Display plant details and clones
        # ...
        pass  # Placeholder for brevity
