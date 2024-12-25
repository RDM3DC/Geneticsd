import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
from tkcalendar import Calendar

class CloneEditDialog:
    def __init__(self, parent, clone_data):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Edit Clone")
        self.clone_data = clone_data

        # Create fields
        fields = ['stage', 'status', 'notes'] 
        self.entries = {}
        
        for field in fields:
            ttk.Label(self.top, text=field.capitalize() + ":").pack(pady=5)
            entry = ttk.Entry(self.top)
            entry.insert(0, clone_data.get(field, ''))
            entry.pack(pady=5)
            self.entries[field] = entry

        # Buttons
        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side='left')

        self.top.grab_set()
        self.top.wait_window()

    def save(self):
        self.result = {field: entry.get() for field, entry in self.entries.items()}
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

class CloneDialog:
    def __init__(self, parent, mother_plants):
        self.result = None
        self.top = tk.Toplevel(parent)
        self.top.title("Add New Clone")
        
        # Mother plant selection
        frame = ttk.Frame(self.top)
        frame.pack(pady=5, padx=10, fill='x')
        ttk.Label(frame, text="Mother Plant:").pack(side='left')
        self.mother = ttk.Combobox(frame, values=sorted(mother_plants))
        if mother_plants:
            self.mother.current(0)
        self.mother.pack(side='right', expand=True, fill='x')

        # Buttons  
        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Create", command=self.save).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel).pack(side='left')

        self.top.grab_set()
        self.top.wait_window()

    def save(self):
        if self.mother.get():
            self.result = self.mother.get()
        self.top.destroy()

    def cancel(self):
        self.top.destroy()

class GrowLogEntry:
    def __init__(self, date, entry_type, data):
        self.date = date
        self.entry_type = entry_type
        self.data = data

class CloneData:
    def __init__(self, parent_frame, plant_genetics, main_app, grow_log_file):
        self.parent_frame = parent_frame 
        self.plant_genetics = plant_genetics
        self.main_app = main_app
        self.grow_log_file = grow_log_file
        self.grow_logs = {}
        self.load_data()
        self.setup_ui()
        self.setup_detail_view()

    # Rest of the CloneData implementation...

class GrowLogManager:
    def __init__(self, parent_frame, plant_genetics, main_app, grow_log_file):
        self.parent_frame = parent_frame
        self.plant_genetics = plant_genetics
        self.main_app = main_app
        self.grow_log_file = grow_log_file
        self.grow_log = self.load_grow_log()

        self.initialize_ui()

    def load_grow_log(self):
        try:
            with open(self.grow_log_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_grow_log_data(self):
        with open(self.grow_log_file, 'w') as file:
            json.dump(self.grow_log, file, indent=4)

    def initialize_ui(self):
        # Control Panel Frame
        control_frame = tk.Frame(self.parent_frame, bg='white')
        control_frame.pack(fill='x', padx=10, pady=5)

        # Strain Selection
        tk.Label(control_frame, text="Select Strain:", bg='white').pack(side='left', padx=5)
        self.strain_var = tk.StringVar()
        strain_options = ["Select Strain"] + sorted([name for name, details in self.plant_genetics.items() 
                                                   if details.get('ownership_type') == 'Clone'])
        self.strain_dropdown = ttk.Combobox(control_frame, textvariable=self.strain_var, values=strain_options)
        self.strain_dropdown.pack(side='left', padx=5)
        self.strain_dropdown.bind('<<ComboboxSelected>>', self.update_log_display)

        # Stage Filter
        tk.Label(control_frame, text="Growth Stage:", bg='white').pack(side='left', padx=5)
        self.stage_var = tk.StringVar(value="All")
        stages = ["All", "Clone", "Vegetation", "Flowering", "Harvested"]
        stage_dropdown = ttk.Combobox(control_frame, textvariable=self.stage_var, values=stages)
        stage_dropdown.pack(side='left', padx=5)
        stage_dropdown.bind('<<ComboboxSelected>>', self.update_log_display)

        # Add Log Entry Button
        tk.Button(control_frame, text="Add Log Entry", 
                 command=self.show_add_entry_dialog,
                 bg='white').pack(side='right', padx=5)

        # Clone Progress Frame
        progress_frame = tk.LabelFrame(self.parent_frame, text="Clone Progress", bg='white')
        progress_frame.pack(fill='x', padx=10, pady=5)

        # Days in Current Stage
        self.days_label = tk.Label(progress_frame, text="Days in current stage: N/A", bg='white')
        self.days_label.pack(side='left', padx=10)

        # Current Stage
        self.stage_label = tk.Label(progress_frame, text="Current Stage: N/A", bg='white')
        self.stage_label.pack(side='left', padx=10)

        # Expected Harvest Date (if flowering)
        self.harvest_label = tk.Label(progress_frame, text="Expected Harvest: N/A", bg='white')
        self.harvest_label.pack(side='left', padx=10)

        # Log Display
        self.create_log_display()

    def create_log_display(self):
        # Create Treeview for log entries
        columns = ('Date', 'Stage', 'Activity', 'Notes', 'Status')
        self.log_tree = ttk.Treeview(self.parent_frame, columns=columns, show='headings')
        
        # Configure columns
        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.parent_frame, orient='vertical', command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        scrollbar.pack(side='right', fill='y')
        self.log_tree.pack(fill='both', expand=True, padx=10, pady=5)

        # Bind double-click event for editing entries
        self.log_tree.bind('<Double-1>', self.edit_entry)

    def show_add_entry_dialog(self):
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Add Log Entry")
        dialog.geometry("400x500")
        dialog.configure(bg='white')

        # Date picker using Calendar
        tk.Label(dialog, text="Date:", bg='white').pack(pady=5)
        cal = Calendar(dialog, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)
        
        # Stage
        tk.Label(dialog, text="Stage:", bg='white').pack(pady=5)
        stage_var = tk.StringVar(value="Clone")
        stage_menu = ttk.Combobox(dialog, textvariable=stage_var, 
                                values=["Clone", "Vegetation", "Flowering", "Harvested"])
        stage_menu.pack(pady=5)

        # Activity
        tk.Label(dialog, text="Activity:", bg='white').pack(pady=5)
        activity_var = tk.StringVar(value="Watered")
        activity_menu = ttk.Combobox(dialog, textvariable=activity_var, 
                                   values=["Watered", "Fed", "Pruned", "Stage Change", 
                                          "Problem Found", "Problem Resolved", "Other"])
        activity_menu.pack(pady=5)

        # Notes
        tk.Label(dialog, text="Notes:", bg='white').pack(pady=5)
        notes_text = tk.Text(dialog, height=4)
        notes_text.pack(pady=5)

        # Status
        tk.Label(dialog, text="Plant Status:", bg='white').pack(pady=5)
        status_var = tk.StringVar(value="Healthy")
        status_menu = ttk.Combobox(dialog, textvariable=status_var, 
                                 values=["Healthy", "Needs Attention", "Problems", "Critical"])
        status_menu.pack(pady=5)

        def save_entry():
            if not self.strain_var.get() or self.strain_var.get() == "Select Strain":
                messagebox.showerror("Error", "Please select a strain first")
                return

            # Get the selected date from calendar
            selected_date = cal.get_date()
            selected_strain = self.strain_var.get()

            # Validate required fields
            if not selected_date or not selected_strain:
                messagebox.showerror("Error", "Date and strain are required fields")
                return
                
            new_entry = {
                "date": selected_date,
                "strain": selected_strain,
                "stage": stage_var.get() or "Clone",  # Default to Clone if empty
                "activity_type": activity_var.get() or "Watered",  # Default to Watered if empty
                "notes": notes_text.get("1.0", "end-1c").strip(),
                "status": status_var.get() or "Healthy"  # Default to Healthy if empty
            }
            
            # Load existing data with validation
            try:
                with open(self.grow_log_file, 'r') as file:
                    try:
                        self.grow_log = json.load(file)
                        if not isinstance(self.grow_log, list):
                            self.grow_log = []
                    except json.JSONDecodeError:
                        self.grow_log = []
            except FileNotFoundError:
                self.grow_log = []
            
            # Add new entry
            self.grow_log.append(new_entry)
            
            # Save updated data
            try:
                with open(self.grow_log_file, 'w') as file:
                    json.dump(self.grow_log, file, indent=4)
                messagebox.showinfo("Success", "Grow log entry saved successfully!")
                self.update_log_display()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save entry: {str(e)}")

        tk.Button(dialog, text="Save", command=save_entry, bg='white').pack(pady=20)

    def edit_entry(self, event):
        if not self.log_tree.selection():
            return
            
        item = self.log_tree.selection()[0]
        values = self.log_tree.item(item)['values']
        
        if not values:
            return
            
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Edit Log Entry")
        dialog.geometry("400x500")
        dialog.configure(bg='white')

        # Date picker
        tk.Label(dialog, text="Date:", bg='white').pack(pady=5)
        cal = Calendar(dialog, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=5)
        try:
            cal.selection_set(values[0])  # Set current date
        except:
            pass

        # Stage
        tk.Label(dialog, text="Stage:", bg='white').pack(pady=5)
        stage_var = tk.StringVar(value=values[1])
        stage_menu = ttk.Combobox(dialog, textvariable=stage_var, 
                                values=["Clone", "Vegetation", "Flowering", "Harvested"])
        stage_menu.pack(pady=5)

        # Activity
        tk.Label(dialog, text="Activity:", bg='white').pack(pady=5)
        activity_var = tk.StringVar(value=values[2])
        activity_menu = ttk.Combobox(dialog, textvariable=activity_var, 
                                   values=["Watered", "Fed", "Pruned", "Stage Change", 
                                          "Problem Found", "Problem Resolved", "Other"])
        activity_menu.pack(pady=5)

        # Notes
        tk.Label(dialog, text="Notes:", bg='white').pack(pady=5)
        notes_text = tk.Text(dialog, height=4)
        notes_text.pack(pady=5)
        notes_text.insert('1.0', values[3])

        # Status
        tk.Label(dialog, text="Plant Status:", bg='white').pack(pady=5)
        status_var = tk.StringVar(value=values[4])
        status_menu = ttk.Combobox(dialog, textvariable=status_var, 
                                 values=["Healthy", "Needs Attention", "Problems", "Critical"])
        status_menu.pack(pady=5)

        def save_edited_entry():
            # Find and update the entry in grow_log
            for entry in self.grow_log:
                if (entry['date'] == values[0] and 
                    entry['strain'] == self.strain_var.get() and 
                    entry['stage'] == values[1]):
                    
                    entry['date'] = cal.get_date()
                    entry['stage'] = stage_var.get()
                    entry['activity_type'] = activity_var.get()
                    entry['notes'] = notes_text.get("1.0", "end-1c")
                    entry['status'] = status_var.get()
                    break

            # Save to file
            with open(self.grow_log_file, 'w') as file:
                json.dump(self.grow_log, file, indent=4)

            # Update display
            self.update_log_display()
            dialog.destroy()
            messagebox.showinfo("Success", "Entry updated successfully!")

        # Add Delete button
        def delete_entry():
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this entry?"):
                # Remove from grow_log
                self.grow_log = [entry for entry in self.grow_log 
                               if not (entry['date'] == values[0] and 
                                     entry['strain'] == self.strain_var.get() and 
                                     entry['stage'] == values[1])]
                
                # Save to file
                with open(self.grow_log_file, 'w') as file:
                    json.dump(self.grow_log, file, indent=4)
                
                # Update display
                self.update_log_display()
                dialog.destroy()
                messagebox.showinfo("Success", "Entry deleted successfully!")

        # Buttons frame
        btn_frame = tk.Frame(dialog, bg='white')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Save", command=save_edited_entry, 
                 bg='white').pack(side='left', padx=5)
        tk.Button(btn_frame, text="Delete", command=delete_entry, 
                 bg='white').pack(side='left', padx=5)

    def update_log_display(self, event=None):
        selected_strain = self.strain_var.get()
        selected_stage = self.stage_var.get()

        # Clear existing entries
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)

        if selected_strain and selected_strain != "Select Strain":
            # Filter and sort entries with validation
            filtered_entries = []
            for entry in self.grow_log:
                try:
                    if (isinstance(entry, dict) and 
                        entry.get('strain') == selected_strain and 
                        (selected_stage == "All" or entry.get('stage') == selected_stage)):
                        filtered_entries.append(entry)
                except Exception:
                    continue  # Skip invalid entries
            
            # Sort by date with validation
            try:
                filtered_entries.sort(key=lambda x: datetime.strptime(x.get('date', '1900-01-01'), '%Y-%m-%d'))
            except Exception:
                # If sorting fails, leave unsorted
                pass

            # Update entries in treeview with validation
            for entry in filtered_entries:
                try:
                    self.log_tree.insert('', 'end', values=(
                        entry.get('date', 'No Date'),
                        entry.get('stage', 'Unknown'),
                        entry.get('activity_type', 'Unknown'),
                        entry.get('notes', ''),
                        entry.get('status', 'Unknown')
                    ))
                except Exception:
                    continue  # Skip problematic entries

            # Update progress information
            if filtered_entries:
                self.update_progress_info(filtered_entries)
            else:
                self.clear_progress_info()

    def clear_progress_info(self):
        """Clear all progress information labels"""
        self.days_label.config(text="Days in current stage: N/A")
        self.stage_label.config(text="Current Stage: N/A")
        self.harvest_label.config(text="Expected Harvest: N/A")

    def update_progress_info(self, entries):
        if not entries:
            self.days_label.config(text="Days in current stage: N/A")
            self.stage_label.config(text="Current Stage: N/A")
            self.harvest_label.config(text="Expected Harvest: N/A")
            return

        # Get current stage from most recent entry
        current_stage = entries[-1]['stage']
        current_date = datetime.strptime(entries[-1]['date'], '%Y-%m-%d')
        
        # Find when this stage started
        stage_start = current_date
        for entry in reversed(entries):
            if entry['stage'] != current_stage:
                stage_start = datetime.strptime(entry['date'], '%Y-%m-%d')
                break

        # Calculate days in current stage
        days_in_stage = (datetime.now() - stage_start).days

        # Update labels
        self.days_label.config(text=f"Days in current stage: {days_in_stage}")
        self.stage_label.config(text=f"Current Stage: {current_stage}")

        # Calculate expected harvest date if in flowering
        if current_stage == "Flowering":
            strain_name = self.strain_var.get()
            if strain_name in self.plant_genetics:
                flowering_time = self.plant_genetics[strain_name].get('flowering_time', 'Unknown')
                if flowering_time.isdigit():
                    days_to_harvest = int(flowering_time) - days_in_stage
                    if days_to_harvest > 0:
                        harvest_date = datetime.now() + timedelta(days=days_to_harvest)
                        self.harvest_label.config(text=f"Expected Harvest: {harvest_date.strftime('%Y-%m-%d')}")
                        return
            self.harvest_label.config(text="Expected Harvest: Unknown")
        else:
            self.harvest_label.config(text="Expected Harvest: N/A")

GROW_LOG_FILE = 'grow_log.json'
CONFIG_FILE = 'config.json'