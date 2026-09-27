import tkinter as tk
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("audio2textdaSilva")
    root.geometry("600x400")
    
    ttk.Label(root, text="Bem-vindo ao audio2text da Silva", font=("Arial", 14)).pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    main()