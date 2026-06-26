from tkinter import *
from PIL import ImageTk
from tkinter import messagebox
import mysql.connector as c
import subprocess
import bcrypt

class Login:
    def __init__(self,root):
        self.root = root
        self.root.title("Login System")
        self.root.geometry("1199x600+150+80")
        self.root.resizable(False, False)

        #background image
        self.bg = ImageTk.PhotoImage(file="./graphics/bgimg/loginbg.jpeg")
        self.bg_image = Label(self.root, image=self.bg).place(x=0,y=0,relwidth=1,relheight=1)


        #login frame
        Frame_login = Frame(self.root, bg="white")
        Frame_login.place(x=330, y=150, width=500, height=400)

        #title
        title = Label(Frame_login, text="Login Here", font=("Impact", 35, "bold"), fg="#6162FF", bg="white").place(x=90,y=30)
        subtitle = Label(Frame_login, text="Members Login Area", font=("Goudy old style", 15, "bold"), fg="#1d1d1d", bg="white").place(x=90,y=100)


        #username
        lbl_user = Label(Frame_login, text="Username", font=("Goudy old style", 15, "bold"), fg="grey", bg="white").place(x=90,y=140)
        self.username = Entry(Frame_login, font=("Goudy old style", 15, "bold"), bg="#E7E6E6")
        self.username.place(x=90,y=170, width=320, height=35)

        #password
        lbl_user = Label(Frame_login, text="Password", font=("Goudy old style", 15, "bold"), fg="grey", bg="white").place(x=90,y=210)
        self.password = Entry(Frame_login, font=("Goudy old style", 15, "bold"), bg="#E7E6E6",show= "*")
        self.password.place(x=90,y=240, width=320, height=35)

        #button
        #forget = Button(Frame_login, text="forgot password?",cursor="hand2",bd=0, font=("Goudy old style", 12), fg="#6162FF", bg="white").place(x=90,y=280)
        submit = Button(Frame_login,command=self.login,cursor="hand2", text="Login",bd=0, font=("Goudy old style", 15), bg="#6162FF", fg="white").place(x=90,y=290, width=180, height=40)
        lbl_signup = Label(Frame_login, text="Don't have an account?", font=("Goudy old style", 12, "bold"), fg="black", bg="white").place(x=90,y=370)
        signup = Button(Frame_login, text="Signup now",command=self.change,cursor="hand2",bd=0, font=("Goudy old style", 12), fg="#6162FF", bg="white").place(x=245,y=366)

    def check_function(self):
            if self.username.get()=="" or self.password.get()=="":
                messagebox.showerror("Error","all fields are required", parent=self.root)
            

    def change(self):
         root.destroy()
         try:
            subprocess.run(["python", "regi.py"])
         except Exception as e:
            messagebox.showerror("Error", f"Failed to run main.py: {e}")

    def login(self):
        con = c.connect(
            user="root",
            password="",
            host="localhost",
            database="mypydb"
        )
        my_cursor = con.cursor()

        user = self.username.get()
        pass1 = self.password.get().encode('utf-8')

        if not user or not pass1:
            messagebox.showerror("Error", "All fields are required", parent=self.root)
            return
            

        query = "Select password from pyuser where user=%s"
        my_cursor.execute(query, (user,))
        result = my_cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "User not found", parent=self.root)
            return

        hashed_pass = result[0].encode('utf-8')
        
        if bcrypt.checkpw(pass1, hashed_pass):
            messagebox.showinfo("Success", "Login successful", parent=self.root)
            root.destroy()
            try:
                subprocess.run(["python", "home.py"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to run home.py: {e}")
        else:
            messagebox.showerror("Error", "Invalid username or password", parent=self.root)   
root = Tk()
obj = Login(root)
root.mainloop()
