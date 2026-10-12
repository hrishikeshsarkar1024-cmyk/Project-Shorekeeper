import os
import sys
import threading
import time
import subprocess
import webbrowser
import urllib.parse
from datetime import datetime
from PIL import Image
import customtkinter as ctk
import speech_recognition as sr
import pyperclip
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re
from duckduckgo_search import DDGS
import pywhatkit

# ==========================================================
# 1. GLOBALS & DYNAMIC KNOWLEDGE
# ==========================================================
is_running = True
is_generating = False
mic_enabled = True

def load_knowledge():
    """Dynamically loads identity, persona, and user blueprint."""
    try:
        with open("Shorekeeper_Persona.txt", "r", encoding="utf-8") as f:
            persona = f.read()
        with open("My_blueprint.txt", "r", encoding="utf-8") as f:
            blueprint = f.read()
        with open("shorekeeper_voice_template.txt", "r", encoding="utf-8") as f:
            voice = f.read()
        return persona, blueprint, voice
    except FileNotFoundError as e:
        print(f"⚠️ Warning: Configuration file missing ({e}). Using default prompts.")
        return "", "", ""

persona_data, blueprint_data, voice_data = load_knowledge()

system_instruction = f"""
You must strictly adhere to the persona, rules, and knowledge provided below. Never break character.
[CORE PERSONA]
{persona_data}

[BLUEPRINT & CONSTELLATION NETWORK]
{blueprint_data}

[VOICE & DIALOGUE STYLE]
{voice_data}
"""

chat_history = [{"role": "system", "content": system_instruction}]

def update_memory_file(new_fact: str):
    """Appends learned facts directly to My_blueprint.txt."""
    print(f"\n[System: Writing to memory... '{new_fact}']")
    try:
        with open("My_blueprint.txt", "a", encoding="utf-8") as f:
            f.write(f"\n* [Learned Memory - {datetime.now().strftime('%Y-%m-%d')}]: {new_fact}")
    except Exception as e:
        print(f"Failed to save memory: {e}")

# ==========================================================
# 2. LOCAL NEURAL CORE (Qwen 2.5 3B 4-bit)
# ==========================================================
print("[System: Initializing Qwen 2.5 3B Core Locally...]")
model_id = "unsloth/qwen2.5-3b-instruct-unsloth-bnb-4bit"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map={"": "cuda"},
        torch_dtype=torch.float16
    )
    print("[OK] Local Neural Core Online.")
except Exception as e:
    print(f"[Fatal Error]: Failed to load model into GPU. Details: {e}")
    sys.exit(1)

# ==========================================================
# 3. INTERCEPT TOOLS: APP LAUNCHER, EMAIL, WEB, MEDIA
# ==========================================================
def open_application(app_name: str) -> str:
    app_name = app_name.lower().strip()
    app_map = {
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "chrome",
        "browser": "chrome",
        "vs code": "code",
        "vscode": "code",
        "word": "winword",
        "excel": "excel",
        "spotify": "spotify",
        "file explorer": "explorer"
    }
    target_exe = app_map.get(app_name, app_name)
    try:
        subprocess.Popen(["cmd", "/c", "start", "", target_exe], shell=True)
        return f"I have opened {app_name} for you, my Rover..."
    except Exception:
        return f"I could not reach the shores of {app_name} on your system."

def draft_email(context: str) -> str:
    app.update_status("Drafting your correspondence...")
    email_prompt = (
        f"Write a concise, professional email reply based on this context: {context}. "
        "Do not use 'Dear', instead use 'Respected Sir'."
        "Do not include conversational filler, meta explanations, or markdown. Output only the message body."
    )
    try:
        inputs = tokenizer(email_prompt, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=220,
            max_length=None,
            temperature=0.3,
            pad_token_id=tokenizer.eos_token_id
        )
        prompt_len = inputs.input_ids.shape[-1]
        draft = tokenizer.decode(outputs[0][prompt_len:], skip_special_tokens=True).strip()

        pyperclip.copy(draft)
        
        search_query = urllib.parse.quote(context)
        gmail_url = f"https://mail.google.com/mail/u/0/#search/{search_query}"
        webbrowser.open(gmail_url)
        
        return "I have woven the draft and placed it on your clipboard. I am opening your Gmail now... you need only select the email and paste it."
    except Exception as e:
        return f"The tide was disturbed while drafting: {e}"

def perform_web_search(query: str) -> str:
    """Silently searches the web and returns the raw text content natively."""
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No relevant information could be found across the tides."
        
        formatted_results = " ".join([r.get('body', '') for r in results])
        return formatted_results
    except Exception as e:
        return f"The connection to the data streams was disrupted: {e}"

def play_song(song_name: str) -> str:
    app.update_status(f"Tuning the frequencies to {song_name}...")
    try:
        pywhatkit.playonyt(song_name)
        return f"I have attuned the shores to play {song_name} for you, my Rover..."
    except Exception as e:
        return f"The frequencies were disrupted while trying to play the melody: {e}"

# ==========================================================
# 4. GUI SETUP (CustomTkinter Overlay with Expandable Chat)
# ==========================================================
ctk.set_appearance_mode("dark")

class ShorekeeperUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Shorekeeper Core")
        self.geometry("600x800")
        self.attributes("-topmost", True)
        
        self.is_expanded = False

        try:
            bg_image = Image.open("H.jpg")
            self.bg_ctk_image = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(600, 800))
            self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image, fg_color="transparent")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"⚠️ Warning: Could not load H.jpg background: {e}")

        self.mic_button = ctk.CTkButton(
            self,
            text="🎙️ Mic: ON",
            width=100,
            height=32,
            font=("Segoe UI", 13, "bold"),
            fg_color="#1E325C",
            hover_color="#2A4B8C",
            border_width=1,
            border_color="#4A6B99",
            command=self.toggle_mic
        )
        self.mic_button.place(relx=0.95, rely=0.02, anchor="ne")

        self.chat_box = ctk.CTkTextbox(
            self,
            state="disabled",
            wrap="word",
            font=("Segoe UI", 15),
            fg_color="#070B14",
            text_color="#D8E8F5",
            border_width=1,
            border_color="#1E325C"
        )
        self.chat_box.place(relx=0.05, rely=0.60, relwidth=0.9, relheight=0.20)
        self.chat_box.bind("<Double-Button-1>", self.toggle_chat_size)

        self.text_input = ctk.CTkEntry(
            self,
            height=40,
            placeholder_text="Type to Shorekeeper... (Press Enter to send)",
            font=("Segoe UI", 14),
            fg_color="#0A0F1D",
            text_color="#D8E8F5",
            border_color="#4A6B99"
        )
        self.text_input.place(relx=0.05, rely=0.82, relwidth=0.9)
        self.text_input.bind("<Return>", self.handle_text_input)

        self.status_label = ctk.CTkLabel(
            self,
            text="Aligning frequencies...",
            font=("Segoe UI", 13, "italic"),
            text_color="#88CFFA",
            fg_color="transparent"
        )
        self.status_label.place(relx=0.5, rely=0.94, anchor="center")

    def toggle_mic(self):
        global mic_enabled
        mic_enabled = not mic_enabled
        
        if mic_enabled:
            self.mic_button.configure(text="🎙️ Mic: ON", fg_color="#1E325C", hover_color="#2A4B8C")
            self.update_status("Waiting for wake word 'Shore'...")
        else:
            self.mic_button.configure(text="🔇 Mic: OFF", fg_color="#8B2222", hover_color="#A52A2A")
            self.update_status("Microphone muted. Text input only.")

    def toggle_chat_size(self, event):
        if not self.is_expanded:
            self.chat_box.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.75)
            self.is_expanded = True
        else:
            self.chat_box.place(relx=0.05, rely=0.60, relwidth=0.9, relheight=0.20)
            self.is_expanded = False
            self.chat_box.see("end")

    def update_chat(self, text: str):
        self.after(0, self._safe_update_chat, text)

    def _safe_update_chat(self, text: str):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", text + "\n\n")
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def update_status(self, text: str):
        self.after(0, lambda: self.status_label.configure(text=text))

    def handle_text_input(self, event):
        global is_generating
        
        if is_generating:
            return
            
        user_text = self.text_input.get().strip()
        if not user_text:
            return
            
        self.text_input.delete(0, 'end')
        self.update_chat(f"You: {user_text}")
        
        if user_text.lower() in ['exit', 'quit', 'stop']:
            self.update_chat("Shorekeeper: Rest well, my Rover... I will remain here on the shores.")
            self.update_status("Shutting down...")
            global is_running
            is_running = False
            self.after(2000, self.destroy)
            return
            
        threading.Thread(target=generate_response, args=(user_text,), daemon=True).start()

app = ShorekeeperUI()

# ==========================================================
# 5. CORE INFERENCE & CONVERSATION PIPELINE
# ==========================================================
def generate_response(user_text: str):
    global is_generating
    is_generating = True
    
    text_lower = user_text.lower().strip()

    try:
        # Interceptors
        if "remember" in text_lower:
            update_memory_file(user_text)

        if "open " in text_lower or "launch " in text_lower:
            trigger = "open " if "open " in text_lower else "launch "
            app_name = text_lower.split(trigger)[-1].strip(' .!?,\'"')
            
            app.update_status(f"Opening {app_name}...")
            reply_text = open_application(app_name)
            app.update_chat(f"Shorekeeper: {reply_text}")
            chat_history.append({"role": "user", "content": user_text})
            chat_history.append({"role": "assistant", "content": reply_text})
            return

        search_triggers = ["search the web for", "look up", "search for", "google"]
        if any(trigger in text_lower for trigger in search_triggers):
            trigger = next(t for t in search_triggers if t in text_lower)
            query = text_lower.split(trigger)[-1].strip(' .!?,\'"')
            
            app.update_status(f"Searching the data streams for '{query}'...")
            
            search_results = perform_web_search(query)
            
            search_prompt = (
                f"I asked you to search the web for: '{query}'. "
                f"You found this raw data: {search_results}. "
                f"Summarize this information accurately but maintain your ethereal, poetic persona."
            )
            
            user_text = search_prompt

        if "draft email" in text_lower or "reply to email" in text_lower:
            trigger = "draft email" if "draft email" in text_lower else "reply to email"
            context = text_lower.split(trigger)[-1].strip(' .!?:')
            
            reply_text = draft_email(context)
            app.update_chat(f"Shorekeeper: {reply_text}")
            chat_history.append({"role": "user", "content": user_text})
            chat_history.append({"role": "assistant", "content": reply_text})
            return

        play_triggers = ["play the song ", "play music ", "play "]
        if any(text_lower.startswith(t) or f" {t}" in text_lower for t in play_triggers):
            trigger = next(t for t in play_triggers if text_lower.startswith(t) or f" {t}" in text_lower)
            song_name = text_lower.split(trigger)[-1].strip(' .!?,\'"')
            
            if song_name:
                app.update_status(f"Tuning into {song_name}...")
                reply_text = play_song(song_name)
                app.update_chat(f"Shorekeeper: {reply_text}")
                chat_history.append({"role": "user", "content": user_text})
                chat_history.append({"role": "assistant", "content": reply_text})
                return

        # Standard Conversational Generation
        chat_history.append({
            "role": "user",
            "content": f"[Time: {datetime.now().strftime('%I:%M %p')}]. {user_text}"
        })
        app.update_status("Processing ripples...")

        inputs = tokenizer.apply_chat_template(
            chat_history,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(model.device)

        prompt_len = inputs.input_ids.shape[-1]

        outputs = model.generate(
            **inputs,
            max_new_tokens=160,
            max_length=None, 
            temperature=0.7,
            pad_token_id=tokenizer.eos_token_id
        )

        reply_text = tokenizer.decode(outputs[0][prompt_len:], skip_special_tokens=True).strip()
        chat_history.append({"role": "assistant", "content": reply_text})
        app.update_chat(f"Shorekeeper: {reply_text}")

    except Exception as e:
        app.update_chat(f"[Generation Error]: {e}")
        
    finally:
        is_generating = False
        if mic_enabled:
            app.update_status("Waiting for wake word 'Shore'...")
        else:
            app.update_status("Microphone muted. Text input only.")

# ==========================================================
# 6. AUDIO RECOGNITION & BACKGROUND LISTENER LOOP
# ==========================================================
def listen():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 400
    recognizer.dynamic_energy_threshold = True
    
    with sr.Microphone() as source:
        app.update_status("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=6)
            app.update_status("Decoding voice...")
            return recognizer.recognize_google(audio)
            
        except sr.WaitTimeoutError:
            app.update_status("Waiting for wake word 'Shore'...")
            return None
        except sr.UnknownValueError:
            app.update_status("Waiting for wake word 'Shore'...")
            return None
        except sr.RequestError as e:
            app.update_status("Network error. Retrying...")
            print(f"[Speech API Error]: {e}")
            time.sleep(1)
            return None
        except Exception as e:
            print(f"[Unknown Audio Error]: {e}")
            return None

def assistant_loop():
    global is_running, is_generating, mic_enabled
    welcome = "I am right here... Call my name when you need me."
    app.update_chat(f"Shorekeeper: {welcome}")

    while is_running:
        if not mic_enabled or is_generating:
            time.sleep(1)
            continue

        app.update_status("Waiting for wake word 'Shore'...")
        captured_text = listen()
        if not captured_text:
            continue

        text_lower = captured_text.lower()

        if text_lower in ['exit', 'quit', 'stop']:
            farewell = "Rest well, my Rover... I will remain here on the shores."
            app.update_chat(f"Shorekeeper: {farewell}")
            app.update_status("Shutting down...")
            is_running = False
            app.after(2000, app.destroy)
            break

        wake_words = ["shore", "sure"]
        padded_text = f" {text_lower} "
        if any(f" {w} " in padded_text for w in wake_words):
            
            trigger = next(w for w in wake_words if f" {w} " in padded_text)
            print(f"\n[Wake Word Detected]: {captured_text} (Matched: {trigger})")
            
            wake_index = text_lower.find(trigger)
            command = captured_text[wake_index + len(trigger):].strip(' ,.')

            if not command:
                app.update_chat("Shorekeeper: I am listening...")
                command = listen()
                if not command:
                    continue

            app.update_chat(f"You: {command}")
            threading.Thread(target=generate_response, args=(command,), daemon=True).start()

# ==========================================================
# 7. MAIN EXECUTION
# ==========================================================
if __name__ == "__main__":
    listener_thread = threading.Thread(target=assistant_loop, daemon=True)
    listener_thread.start()

    app.mainloop()
    is_running = False