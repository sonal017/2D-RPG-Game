import tkinter as tk
import pygame, sys
import subprocess
from tkinter import messagebox

def restart_button():    # Code for button
    root.destroy()
    try:
        subprocess.run(["python", "main.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run main.py: {e}")
    


def home_button():    # Code for button
    root.destroy()
    try:
        subprocess.run(["python", "home.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run home.py: {e}")
    
root = tk.Tk()
root.title("Game Over")
root.resizable(False,False)

# Set the window size
root.geometry("1199x600+150+80")

# Load the image
image = tk.PhotoImage(file='./graphics/bgimg/game_over_neon_lights_hd_game_over.png')

# Create a label to display the image
image_label = tk.Label(root, image=image)
image_label.pack()

restart_button = tk.Button(root, text="Restart", font=("Goudy old style", 15, "bold"), fg="blue", bg="white",command=restart_button).place(x=400,y=295, width=180, height=40)
home_button = tk.Button(root, text="Home", font=("Goudy old style", 15, "bold"), fg="blue", bg="white",command=home_button).place(x=650,y=295, width=180, height=40)

root.mainloop()