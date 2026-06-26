from tkinter import *
from PIL import ImageTk
from tkinter import messagebox
import mysql.connector as c
import subprocess
import bcrypt

class Regi:
    def __init__(self,root):
        self.root = root
        self.root.title("Registration System")
        self.root.geometry("1199x600+150+80")
        self.root.resizable(False, False)

        #background image
        self.bg = ImageTk.PhotoImage(file="./graphics/bgimg/loginbg.jpeg")
        self.bg_image = Label(self.root, image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)


        #login frame
        Frame_regi = Frame(self.root, bg="white")
        Frame_regi.place(x=330, y=150, width=500, height=400)

        #title
        title = Label(Frame_regi, text="Registration Here", font=("Impact", 35, "bold"), fg="#6162FF", bg="white").place(x=90,y=30)
        subtitle = Label(Frame_regi, text="Members Registration Area", font=("Goudy old style", 15, "bold"), fg="#1d1d1d", bg="white").place(x=90,y=100)


        #username
        lbl_user = Label(Frame_regi, text="Username", font=("Goudy old style", 15, "bold"), fg="grey", bg="white").place(x=90,y=140)
        self.username = Entry(Frame_regi, font=("Goudy old style", 15, "bold"), bg="#E7E6E6")
        self.username.place(x=90,y=170, width=320, height=35)
        #user = self.username.get()

        #password
        lbl_password = Label(Frame_regi, text="Password", font=("Goudy old style", 15, "bold"), fg="grey", bg="white").place(x=90,y=210)
        self.password = Entry(Frame_regi, font=("Goudy old style", 15, "bold"), bg="#E7E6E6",show= "*")
        self.password.place(x=90,y=240, width=320, height=35)
        #pass1 = self.password.get()


        #button
        submit = Button(Frame_regi,cursor="hand2",command=lambda: [self.check_function(), self.insertt()] if self.username.get()!="" and self.password.get()!="" else messagebox.showerror("Error","all fields are required", parent=self.root), text="Registration",bd=0, font=("Goudy old style", 15), bg="#6162FF", fg="white").place(x=90,y=290, width=180, height=40)
        lbl_login = Label(Frame_regi, text="Already have an account?", font=("Goudy old style", 12, "bold"), fg="black", bg="white").place(x=90,y=370)
        login = Button(Frame_regi, text="Login now",command=self.change,cursor="hand2",bd=0, font=("Goudy old style", 12), fg="#6162FF", bg="white").place(x=260,y=366)
    
    def change(self):
         root.destroy()
         try:
            subprocess.run(["python", "login.py"])
         except Exception as e:
            messagebox.showerror("Error", f"Failed to run main.py: {e}")
    
    def check_function(self):
            if self.username.get()=="" or self.password.get()=="":
                messagebox.showerror("Error","all fields are required", parent=self.root)
                


    def insertt(self):
        con = c.connect(
        user="root",
        password="",
        host="localhost",
        database="mypydb"
    )
        my_cursor = con.cursor()
        user = self.username.get()
        pass1 = self.password.get().encode('utf-8')
        
        hashed_pass = bcrypt.hashpw(pass1,bcrypt.gensalt())

        query = "Select * from pyuser where user=%s"
        my_cursor.execute(query, (user,))
        result = my_cursor.fetchone()
        if result:
            messagebox.showerror("Error", "User already exists", parent=self.root)
        else:
            query = "Insert into pyuser(user,password) values(%s, %s)"
        my_cursor.execute(query, (user, hashed_pass))
        
        con.commit()
        messagebox.showinfo("Success", "User registered successfully", parent=self.root)
        self.change()
    
root = Tk()
obj = Regi(root)
root.mainloop()