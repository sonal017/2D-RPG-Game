import tkinter as tk
import pygame, sys
import subprocess
from tkinter import messagebox


def home_button():
     # Code for button
    root.destroy()  
    try:
        subprocess.run(["python", "home.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run home.py: {e}")             # Close the current window
    
root = tk.Tk()
root.title("Victory")
root.resizable(False,False)

# Set the window size
root.geometry("1199x600+150+80")

# Load the image
image = tk.PhotoImage(file='./graphics/bgimg/victory1.png')

# Create a label to display the image
image_label = tk.Label(root, image=image)
image_label.pack()

home_button = tk.Button(root, text="HOME", font=("Goudy old style", 15, "bold"), fg="gold", bg="red",command=home_button).place(x=512,y=355, width=180, height=40)

root.mainloop()