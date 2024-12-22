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
    def __init__(self, parent, plant_genetics, main_app, log_file):
        self.parent = parent
        self.main_app = main_app
        self.plant_genetics = plant_genetics
        self.log_file = log_file
        self.create_ui()

    def create_ui(self):
        tk.Label(self.parent, text="Grow Log Entries", font=("Helvetica", 14, "bold")).pack(pady=10)
        self.log_text = tk.Text(self.parent, wrap="word", height=20, width=80)
        self.log_text.pack(pady=10)
        self.load_logs()

        frame_buttons = tk.Frame(self.parent)
        frame_buttons.pack()
        tk.Button(frame_buttons, text="Add Entry", command=self.add_entry).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Save Log", command=self.save_logs).pack(side="left", padx=5)

    def load_grow_log_data(self):
        """Load grow log data from JSON file."""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    raise ValueError("Grow log file must contain a list of entries")
                return logs
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Failed to decode grow log file: {e}")
            return []
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid grow log format: {e}")
            return []

    def display_grow_log(self):
        """Display grow log entries in the UI."""
        logs = self.load_grow_log_data()
        
        # Clear existing entries
        for widget in self.log_frame.winfo_children():
            widget.destroy()
            
        # Display each log entry
        for log in logs:
            try:
                date = log["date"]
                strain = log["strain"]
                activity = log["activity_type"]
                status = log.get("status", "Unknown")
                notes = log.get("notes", "")
                
                self.create_log_entry_widget(date, strain, activity, status, notes)
            except KeyError as e:
                print(f"Skipping malformed log entry: missing {e}")
                continue

    def load_logs(self):
        """Loads and displays grow log entries from JSON file."""
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
                if not isinstance(logs, list):
                    logs = []  # Reset to empty list if invalid format
                self.log_text.delete('1.0', tk.END)  # Clear existing text
                for log in logs:
                    if isinstance(log, dict) and 'date' in log and 'entry_type' in log and 'data' in log:
                        self.log_text.insert(tk.END, f"{log['date']}: {log['entry_type']} - {log['data']}\n")
        except FileNotFoundError:
            logs = []  # Start with empty list if file doesn't exist
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Failed to decode grow log file. Starting with empty log.")
            logs = []  # Start fresh if file is corrupted

    def save_logs(self):
        """Saves grow log entries as a JSON list of dictionaries."""
        logs = []
        content = self.log_text.get("1.0", tk.END).strip()
        if content:
            for line in content.split("\n"):
                try:
                    date, rest = line.split(": ", 1)
                    entry_type, data = rest.split(" - ", 1)
                    logs.append({
                        "date": date.strip(),
                        "entry_type": entry_type.strip(),
                        "data": data.strip()
                    })
                except ValueError:
                    continue  # Skip malformed lines

        try:
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=4)
            messagebox.showinfo("Success", "Grow log saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save grow log: {e}")

    def add_entry(self):
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry_type = "New Entry"
        data = "Sample data"
        self.log_text.insert(tk.END, f"{date}: {entry_type} - {data}\n")

GROW_LOG_FILE = 'grow_log.json'
CONFIG_FILE = 'config.json'