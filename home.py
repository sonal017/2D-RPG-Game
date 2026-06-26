import tkinter as tk
import subprocess
from tkinter import messagebox

def start_button():
    root.destroy()
    try:
        subprocess.run(["python", "main.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run main.py: {e}")

def logout_button():
    root.destroy()

root = tk.Tk()
root.title("Home")
root.resizable(False, False)

root.geometry("1199x600+150+80")

image = tk.PhotoImage(file='./graphics/bgimg/homebg.png')

image_label = tk.Label(root, image=image)
image_label.pack()

start_button = tk.Button(root, text="START", font=("Goudy old style", 15, "bold"), fg="black", bg="grey", command=start_button).place(x=400, y=255, width=180, height=40)
logout_button = tk.Button(root, text="LOGOUT", font=("Goudy old style", 15, "bold"), fg="black", bg="grey", command=logout_button).place(x=650, y=255, width=180, height=40)

game_details_info = tk.Label(root, text="Game Details:\n\nThis is a simple game where the player can move around using the Arrow keys.\n SPACE key to attack and select.\nLeft-Ctrl to use special ability.\n E key to change special ability.\n Q key to change weapons.\n M key to Upgrade Attack,Health,Energy,Speed and Magic ", font=("Goudy old style", 15, "bold"), fg="black", bg="grey")
game_details_info.place(x=240, y=320, width=800, height=260)

root.mainloop()