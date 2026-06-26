import tkinter as tk
import pygame, sys
import subprocess
from tkinter import messagebox


def next_button():    # Code for button
    root.destroy()
    try:
        subprocess.run(["python", "main2.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run main2.py: {e}")

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

next_button = tk.Button(root, text="NEXT", font=("Goudy old style", 15, "bold"), fg="gold", bg="red",command=next_button).place(x=350,y=355, width=180, height=40)
home_button = tk.Button(root, text="HOME", font=("Goudy old style", 15, "bold"), fg="gold", bg="red",command=home_button).place(x=700,y=355, width=180, height=40)

Warning_details_info = tk.Label(root, text="Warning:\n\nIf You Lose In This Level You Have To Start From Level 1", font=("Goudy old style", 15, "bold"), fg="red", bg="grey")
Warning_details_info.place(x=240, y=420, width=800, height=100)

root.mainloop()