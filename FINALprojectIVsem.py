import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from gtts import gTTS
import pygame
import os
import time
import threading

# Initialize the recognizer
recognizer = sr.Recognizer()

# List of supported Indian languages with their language codes
supported_languages = {
    'Hindi': 'hi-IN',
    'Bengali': 'bn-IN',
    'Tamil': 'ta-IN',
    'Telugu': 'te-IN',
    'Gujarati': 'gu-IN',
    'Marathi': 'mr-IN',
    'Kannada': 'kn-IN',
    'Malayalam': 'ml-IN',
    'Urdu': 'ur-IN'
}

# Initialize pygame mixer
pygame.mixer.init()

# Function to play an audio file
def play_audio(file):
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def animate_dots():
    global listening
    dots = ""
    while listening:
        dots = (dots + ".") if len(dots) < 3 else ""
        listening_var.set(f"Listening{dots}")
        root.update()
        time.sleep(0.5)
    listening_var.set("")  

def recognize_speech(language_code):
    global listening
    
    # Update listening_var to "Listening..."
    listening_var.set("Listening...")
    
    # Listen to the user's speech
    with sr.Microphone() as source:
        try:
            audio_data = recognizer.listen(source, timeout=5)
            listening = False  
            text = recognizer.recognize_google(audio_data, language=language_code)
            
            # Append recognized text to a file
            with open("recognized_text.txt", "a", encoding="utf-8") as file:
                file.write(f"{text}\n")
            
            # Display recognized text
            result_var.set(text)
            
            # Speak back the recognized text in the same language
            tts = gTTS(text, lang=language_code.split('-')[0])
            tts.save("output.mp3")
            play_audio("output.mp3")
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            os.remove("output.mp3")
        
        except sr.UnknownValueError:
            listening = False  
            result_var.set("Sorry, I could not understand your speech. Please try again.")
        
        except sr.RequestError as e:
            listening = False  
            result_var.set(f"Sorry, there was an error with the Google Web Speech API: {e}")
        
        except Exception as e:
            listening = False  
            result_var.set(f"An error occurred: {str(e)}")

def start_listening():
    global listening
    listening = True
    
    language_code = language_var.get()
    if language_code not in supported_languages.values():
        messagebox.showerror("Error", "Sorry, the entered language code is not supported.")
        return
    
    # Adjust for ambient noise
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    
    # Start the listening animation in a separate thread
    animation_thread = threading.Thread(target=animate_dots)
    animation_thread.start()
    
    # Start the speech recognition in a separate thread
    recognition_thread = threading.Thread(target=recognize_speech, args=(language_code,))
    recognition_thread.start()

def delete_text_file():
    if os.path.exists("recognized_text.txt"):
        os.remove("recognized_text.txt")
        result_var.set("Text file deleted.")
    else:
        result_var.set("Text file does not exist.")

# Set up the main application window
root = tk.Tk()
root.title("Indian Language Speech Converter")
root.geometry("600x650")
root.configure(bg="#1e1e1e")

# Create a style
style = ttk.Style(root)
style.theme_use('clam')
style.configure('TButton', font=('Arial', 12), borderwidth=1)
style.configure('TCombobox', font=('Arial', 12))

# Header
header_frame = tk.Frame(root, bg="#1e1e1e")
header_frame.pack(pady=20)

title_label = tk.Label(header_frame, text="Indian Language Speech Converter", font=("Arial", 24, "bold"), fg="#ffffff", bg="#1e1e1e")
title_label.pack()

# Language selection
language_frame = tk.Frame(root, bg="#1e1e1e")
language_frame.pack(pady=20)

tk.Label(language_frame, text="Select Language:", font=("Arial", 14), fg="#ffffff", bg="#1e1e1e").pack(side=tk.LEFT, padx=10)
language_var = tk.StringVar(value='hi-IN')
language_menu = ttk.Combobox(language_frame, textvariable=language_var, values=list(supported_languages.values()), width=30)
language_menu.pack(side=tk.LEFT)

# Button to start listening
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(pady=20)

listen_button = ttk.Button(button_frame, text="🎤 Start Listening", command=start_listening)
listen_button.pack(pady=10)

# Label to display the listening animation
listening_var = tk.StringVar()
listening_label = tk.Label(root, textvariable=listening_var, font=("Arial", 14), fg="#ffffff", bg="#1e1e1e")
listening_label.pack(pady=10)

# Label to display the result
result_frame = tk.Frame(root, bg="#2c2c2c", padx=20, pady=20)
result_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

result_var = tk.StringVar()
result_label = tk.Label(result_frame, textvariable=result_var, font=("Arial", 14), fg="#ffffff", bg="#2c2c2c", wraplength=500, justify=tk.LEFT)
result_label.pack(fill=tk.BOTH, expand=True)

# Button to delete the text file
delete_button = ttk.Button(root, text="🗑 Delete Text File", command=delete_text_file)
delete_button.pack(pady=20)

# Footer
footer_label = tk.Label(root, text="© 2024 Indian Language Speech Converter By Priyanshu Pilkhwal", font=("Arial", 10), fg="#888888", bg="#1e1e1e")
footer_label.pack(side=tk.BOTTOM, pady=10)

# Run the GUI event loop
root.mainloop()
