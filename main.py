import cgi
import speech_recognition as sr
import webbrowser
import pyttsx4
import requests
import google.generativeai as genai
import winsound
import time
import os
import subprocess
import shutil
import winreg
import pywhatkit as pw
from langdetect import detect  # for language detection
import re
# ---------------- API KEYS ----------------
from Api import OPENWEATHER_API, GENAI_API
# ---------------- CLASS ----------------
class VoiceAssistant:
    def __init__(self, name="Aurelia"):
        self.name = name
        self.r = sr.Recognizer()
        self.engine = pyttsx4.init()
        self.engine.setProperty('rate', 125)
        self._set_female_voice()

        # --- Websites ---
        self.websites = {
            "google": "https://google.com",
            "instagram": "https://instagram.com",
            "facebook": "https://facebook.com",
            "udemy": "https://www.udemy.com/home",
            "youtube": "https://youtube.com",
            "chat gpt": "https://chatgpt.com",
            "gemini": "https://gemini.google.com",
            "github": "https://github.com"
        }

        # --- Wake Words ---
        self.wake_words = ["aurelia", "aurlia", "aurelio"]

    # ---------------- VOICE + SPEAK ----------------
    def _set_female_voice(self):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "zira" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break

    def speak(self, text, lang="en"):
        def clean_text_manually(input_text):
            allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,?!-:()'"
            filtered_string = ""
            for char in input_text:
                if char in allowed_chars:
                    filtered_string += char
                elif char == '\n':
                    filtered_string += " "
            return ' '.join(filtered_string.split())

        cleaned_text = clean_text_manually(text)

        print(f"Aurelia ({lang}):", cleaned_text)
        self.engine.say(cleaned_text)
        self.engine.runAndWait()

    # ---------------- LISTEN ----------------
    def listen(self, timeout=6, phrase_time_limit=5, lang="en-IN"):
        with sr.Microphone() as source:
            self.r.adjust_for_ambient_noise(source, duration=1)
            print("Listening...")
            audio = self.r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return self.r.recognize_google(audio, language=lang).lower()

    # ---------------- AI PROCESSING ----------------
    def ai_process(self, query, lang="en"):
        genai.configure(api_key=GENAI_API)
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(query)
        return response.text

    # ---------------- FIND APP IN PC ----------------
    def find_app_in_pc(self, app_name):
        reg_paths = [
            r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths",
            r"SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\App Paths"
        ]
        for reg_path in reg_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    count = winreg.QueryInfoKey(key)[0]
                    for i in range(count):
                        subkey_name = winreg.EnumKey(key, i)
                        if app_name.lower() in subkey_name.lower():
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                app_path, _ = winreg.QueryValueEx(subkey, None)
                                return app_path
            except Exception:
                continue
        return None

    # ---------------- WEATHER INFO ----------------
    def get_weather(self, city, lang="en"):
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API}&units=metric&lang={lang}"
            res = requests.get(url)
            data = res.json()
            if data["cod"] == 200:
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                if lang == "hi":
                    return f"{city} में अभी {desc} है और तापमान {temp} डिग्री सेल्सियस है।"
                else:
                    return f"The weather in {city} is currently {desc} with a temperature of {temp}°C."
            else:
                return "Sorry, I couldn't find that city."
        except Exception as e:
            return f"Error fetching weather: {e}"

    # ---------------- PROCESS COMMAND ----------------
    def process_command(self, c):
        c = c.lower()
        lang = "hi" if detect(c) == "hi" else "en"

        if "open" in c or "खोलो" in c:
            app_name = c.replace("open", "").replace("खोलो", "").strip()

            if app_name in self.websites:
                webbrowser.open(self.websites[app_name])
                self.speak(f"Opening {app_name}...", lang)
                return

            app_path = shutil.which(app_name)
            if app_path:
                subprocess.Popen(app_path)
                self.speak(f"Opening {app_name}...", lang)
                return

            reg_app_path = self.find_app_in_pc(app_name)
            if reg_app_path:
                subprocess.Popen(reg_app_path)
                self.speak(f"Opening {app_name} from system registry...", lang)
                return

            try:
                os.system(f'start {app_name}')
                self.speak(f"Trying to open {app_name}...", lang)
            except Exception:
                self.speak(f"Sorry, I couldn't open {app_name}.", lang)
            return

        elif "weather" in c or "मौसम" in c:
            city = ""
            if "in" in c:
                city = c.split("in")[-1].strip()
            elif "of" in c:
                city = c.split("of")[-1].strip()
            if not city:
                city = "Greater Noida" 

            result = self.get_weather(city, lang)
            self.speak(result, lang)
            return

        elif "play" in c or "चलाओ" in c:
            song = c.replace("play", "").replace("चलाओ", "").strip()
            self.speak(f"Searching YouTube for {song}...", lang)
            pw.playonyt(song)
            return

        else:
            result = self.ai_process(c, lang)
            self.speak(result, lang)


# ---------------- MAIN CLASS ----------------
class Main(VoiceAssistant):
    def run(self):
        self.speak(f"{self.name} is initializing...")
        time.sleep(1)

        while True:
            try:
                word = self.listen(timeout=6, phrase_time_limit=5)
                print("Heard:", word)

                if any(exit_word in word for exit_word in ["stop", "exit", "quit", "goodbye", "bye", "go to sleep"]):
                    self.speak("Alright, shutting down. Goodbye!")
                    break

                if any(w in word for w in self.wake_words):
                    winsound.PlaySound(
                        "C:/Users/huzai/OneDrive/Documents/Sandbox-Python/Sandbox-Python/Ai_Voice_Assistance/pop.wav",
                        winsound.SND_FILENAME | winsound.SND_ASYNC
                    )
                    self.speak("Yes Sir, how may I assist you?")
                    c = self.listen(timeout=8, phrase_time_limit=10)
                    print("Command:", c)

                    if any(exit_word in c for exit_word in ["stop", "exit", "quit", "goodbye", "bye"]):
                        self.speak("Alright, shutting down. Goodbye!")
                        break

                    self.process_command(c)

            except sr.UnknownValueError:
                print("Sorry, could not understand audio.")
            except sr.WaitTimeoutError:
                print("Listening timeout, no speech detected.")
            except sr.RequestError as e:
                print("Speech request error:", e)


if __name__ == "__main__":
    assistant = Main("Aurelia")
    assistant.run()
