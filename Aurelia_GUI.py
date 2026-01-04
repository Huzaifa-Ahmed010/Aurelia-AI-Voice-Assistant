import os
import sys
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import customtkinter as ctk
from PIL import Image, ImageTk
from datetime import datetime
import math
import speech_recognition as sr
import winsound
from main import Main
import database  # Import the database module
import subprocess
class AureliaGUI:
    def __init__(self, root, user_id, username):
        self.root = root
        self.root.title("Aurelia - Your AI Voice Assistant")
        self.root.geometry("900x650")
        self.root.configure(bg="#0d1117")

        self.assistant = Main("Aurelia")
        self.listening = False
        self.assistant_thread = None

        self.user_id = user_id
        self.username = username

        self.header = ctk.CTkLabel(
            root, text="🪄 AURELIA AI", font=("Segoe UI Semibold", 28, "bold"), text_color="#58a6ff"
        )
        self.header.pack(pady=15)

        self.chat_box = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, font=("Consolas", 13), bg="#161b22",
            fg="#c9d1d9", insertbackground="white", relief="flat", height=18, width=90
        )
        self.chat_box.pack(padx=20, pady=10)
        self.chat_box.insert(tk.END, f"👋 Hello, {self.username}! I'm Aurelia. Tap the mic to begin.\n\n")
        self.chat_box.config(state=tk.DISABLED)

        mic_frame = ctk.CTkFrame(root, fg_color="#0d1117")
        mic_frame.pack(pady=15)

        self.canvas = tk.Canvas(mic_frame, width=150, height=150, bg="#0d1117", highlightthickness=0)
        self.canvas.pack()

        mic_path = self.resource_path("mic.png")
        mic_img = Image.open(mic_path).resize((80, 80))
        self.mic_icon = ImageTk.PhotoImage(mic_img)
        self.mic_button = self.canvas.create_image(75, 75, image=self.mic_icon)
        self.canvas.bind("<Button-1>", self.toggle_assistant_session)

        self.status_label = ctk.CTkLabel(
            root, text="Status: Idle", font=("Segoe UI", 14), text_color="#8b949e"
        )
        self.status_label.pack(pady=10)

        footer = ctk.CTkFrame(root, fg_color="#0d1117")
        footer.pack(pady=10)

        self.time_label = ctk.CTkLabel(footer, text="", font=("Segoe UI", 13), text_color="#8b949e")
        self.time_label.grid(row=0, column=0, padx=20)

        self.weather_label = ctk.CTkLabel(footer, text="🌤 Weather: Unknown", font=("Segoe UI", 13), text_color="#8b949e")
        self.weather_label.grid(row=0, column=1, padx=20)
        self.logout_button = ctk.CTkButton(footer, text="Log Out", command=self.logout,fg_color=("#d73a49", "#d73a49"), hover_color=("#b52d3a", "#b52d3a"))
        self.logout_button.grid(row=0, column=2, padx=20)

        self.update_clock()
        self.animate_pulse()
        
        self.load_history()

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_history(self):
        """Loads the last few conversations for this user."""
        history = database.get_last_conversation(self.user_id)
        self.update_chat("📜 System", "--- Loading recent conversation history ---")
        for command, response in history:
            self.update_chat(f"🗣 {self.username} (Past)", command)
            if response:
                self.update_chat("🧠 Aurelia (Past)", response)
        self.update_chat("📜 System", "--- History loaded ---")

    def update_clock(self):
        now = datetime.now().strftime("%I:%M %p | %a, %d %b %Y")
        self.time_label.configure(text=f"⏰ {now}")
        self.root.after(1000, self.update_clock)

    def update_chat(self, speaker, text):
        self.chat_box.config(state=tk.NORMAL)
        if text:
            self.chat_box.insert(tk.END, f"{speaker}: {text}\n\n")
            self.chat_box.see(tk.END)
        self.chat_box.config(state=tk.DISABLED)
    def animate_pulse(self):
        self.canvas.delete("pulse")
        if self.listening:
            t = time.time()
            radius = 45 + 5 * math.sin(t * 4)
            color_hex = '#58a6ff'
            self.canvas.create_oval(
                75 - radius, 75 - radius, 75 + radius, 75 + radius,
                outline=color_hex, width=3, tags="pulse"
            )
        self.root.after(50, self.animate_pulse)

    def toggle_assistant_session(self, event=None):
        if not self.listening:
            self.assistant_thread = threading.Thread(target=self.run_assistant_session, daemon=True)
            self.assistant_thread.start()
        else:
            self.listening = False
            self.status_label.configure(text="Stopping...", text_color="#d73a49")
            self.update_chat("🧠 Aurelia", "Manual stop initiated. Session ended.")
    
    def run_assistant_session(self):
        self.listening = True
        self.status_label.configure(text="▶️ Session Started. Listening for 'Aurelia'...", text_color="#58a6ff")
        self.update_chat("🧠 Aurelia", "Say 'Aurelia' to activate me.")
    
        while self.listening:
            try:
                self.status_label.configure(text="🎙 Listening for wake word...", text_color="#58a6ff")
                word = self.assistant.listen(timeout=8, phrase_time_limit=5)
                if word:
                    self.update_chat(f"🗣 {self.username}", word)

                if not self.listening:
                    break

                if any(w in word for w in self.assistant.wake_words):
                    pop_path = self.resource_path("pop.wav")
                    winsound.PlaySound(pop_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

                    self.status_label.configure(text="✅ Wake word detected!", text_color="#238636")
                    self.assistant.speak("Yes Sir?")
                    self.update_chat("Aurelia", "Yes Sir? I'm listening...")

                    time.sleep(0.3)
                    
                    pop_path = self.resource_path("pop.wav")
                    winsound.PlaySound(pop_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

                    self.status_label.configure(text="🎙 Speak your command...", text_color="#58a6ff")
                    command = self.assistant.listen(timeout=12, phrase_time_limit=14)
                    if not command:
                        self.update_chat("System", "Didn't hear a command. Listening for wake word again.")
                        continue
                    
                    self.update_chat(f"{self.username}", command)

                    stop_commands = ["stop listening", "go to sleep", "that's all", "cancel", "end session"]
                    if any(cmd in command.lower() for cmd in stop_commands):
                        response_text = "Understood. Ending our session. Goodbye!"
                        self.assistant.speak(response_text)
                        self.update_chat("Aurelia", response_text)
                        database.log_command(self.user_id, command, response_text)
                        self.listening = False
                        break

                    self.status_label.configure(text="⚙️ Processing command...", text_color="#e3b341")
                    self.process_and_display(command)
                    self.update_chat("Aurelia", "Task complete. Listening for wake word again.")

            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                self.update_chat("System", "Couldn't understand that. Listening for wake word.")
                continue
            except Exception as e:
                self.update_chat("Error", str(e))
                time.sleep(2)
        
        self.status_label.configure(text="Status: Idle", text_color="#8b949e")
        self.update_chat("Aurelia", "Session has ended.")
    
    def process_and_display(self, command):
        response_text_to_log = []
        try:
            original_speak = self.assistant.speak
            
            def speak_and_capture(text, lang="en"):
                self.update_chat("Aurelia", text)
                response_text_to_log.append(text)
                original_speak(text, lang)

            self.assistant.speak = speak_and_capture
            self.assistant.process_command(command)

            final_response = " ".join(response_text_to_log)
            database.log_command(self.user_id, command, final_response) # Log to DB

            if "weather" in command.lower() or "मौसम" in command.lower():
                if final_response:
                    self.weather_label.configure(text=f"🌤 {final_response}")

            self.assistant.speak = original_speak

        except Exception as e:
            self.update_chat("Error", f"An error occurred: {e}")
            database.log_command(self.user_id, command, f"Error: {e}")
    def logout(self):
        self.listening = False
        self.update_chat("📜 System", "Logging out... Goodbye!")
        self.status_label.configure(text="Status: Logging out...", text_color="#d73a49")
        self.root.after(200, self.perform_logout)
    def perform_logout(self):
        try:
            self.root.destroy()
            subprocess.Popen([sys.executable, "login.py"]) 
        except Exception as e:

            print(f"Error during logout: {e}")
