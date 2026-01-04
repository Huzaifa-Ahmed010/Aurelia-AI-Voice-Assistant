import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import database
from Aurelia_GUI import AureliaGUI 

class LoginRegisterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aurelia AI - Login")
        self.root.geometry("400x450")
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(pady=40, padx=60, fill="both", expand=True)

        self.label = ctk.CTkLabel(self.frame, text="Aurelia Login", font=("Segoe UI Semibold", 24))
        self.label.pack(pady=20)

        self.user_entry = ctk.CTkEntry(self.frame, placeholder_text="Username", width=200)
        self.user_entry.pack(pady=12, padx=10)

        self.pass_entry = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*", width=200)
        self.pass_entry.pack(pady=12, padx=10)
        
        self.login_button = ctk.CTkButton(self.frame, text="Login", command=self.login)
        self.login_button.pack(pady=20)

        self.register_button = ctk.CTkButton(self.frame, text="Register", command=self.show_register_window, fg_color="transparent", border_width=1)
        self.register_button.pack(pady=5)

    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Username and password cannot be empty.")
            return

        user_id = database.check_user(username, password)
        if user_id:
            messagebox.showinfo("Success", "Login successful!")
            self.root.destroy()  
            main_app_root = ctk.CTk()
            app = AureliaGUI(main_app_root, user_id=user_id, username=username) 
            main_app_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def show_register_window(self):
        register_window = ctk.CTkToplevel(self.root)
        register_window.title("Register New User")
        register_window.geometry("400x400")
        
        frame = ctk.CTkFrame(register_window)
        frame.pack(pady=40, padx=60, fill="both", expand=True)
        
        label = ctk.CTkLabel(frame, text="Create Account", font=("Segoe UI Semibold", 24))
        label.pack(pady=20)
        
        user_entry = ctk.CTkEntry(frame, placeholder_text="Enter Username", width=200)
        user_entry.pack(pady=12, padx=10)
        
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Enter Password", show="*", width=200)
        pass_entry.pack(pady=12, padx=10)

        def register():
            username = user_entry.get()
            password = pass_entry.get()
            if not username or not password:
                messagebox.showerror("Error", "Fields cannot be empty.", parent=register_window)
                return
            
            if database.add_user(username, password):
                messagebox.showinfo("Success", "User registered successfully!", parent=register_window)
                register_window.destroy()
            else:
                messagebox.showerror("Error", "Username already exists.", parent=register_window)

        register_btn = ctk.CTkButton(frame, text="Register", command=register)
        register_btn.pack(pady=20)

if __name__ == "__main__":
    database.setup_database() 
    root = ctk.CTk()
    app = LoginRegisterApp(root)

    root.mainloop()
