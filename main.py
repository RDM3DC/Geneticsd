# main.py
from app import CannabisGeneticsApp
import tkinter as tk

def main():
    root = tk.Tk()
    app = CannabisGeneticsApp(root)
    app.main()

if __name__ == "__main__":
    main()
