from tkinter import *
import customtkinter
from openai import OpenAI
import os
import pickle
from gtts import gTTS
import playsound
import speech_recognition as sr
import threading
import pyttsx3


root = customtkinter.CTk()
root.title("OracleGPT")
root.geometry("620x620")
root.iconbitmap("ai_lt.ico")

no_api = 0
session_tokens = 0
options_active = False
male_voice = False

# set color scheme
color = "dark-blue"
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme(color)

# Language in which you want to convert
language = 'en'

event = threading.Event()

class AssistantTask:
    def run(self):
        global event
        my_text.insert(END, "Establishing mic feed...\n")
        r = sr.Recognizer()
        while not event.is_set():
            if 'normal' == root.state():
                with sr.Microphone() as source:
                    my_text.insert(END, "Listening...\n")
                    audio = r.listen(source)
                    if audio:
                        clear()
                        my_text.insert(END, "Audio detected...\n")
                        try:
                            text = r.recognize_google(audio)
                            if "oracle" in text.lower():
                                clean_text = text.lower().replace("oracle", "").replace("  ", " ")
                                my_text.insert(END, f"\n{clean_text}\n")
                                bot_read("api_key", clean_text)
                            elif "stop listening" in text.lower():
                                my_text.insert(END, "\nStopped Listening\n")
                                event.set()
                            elif "clear the screen" in text.lower():
                                clear()
                            else:
                                print(text)
                        except sr.UnknownValueError:
                            print("Could not understand audio")
                    
            else:
                print("Stopped Listening")
                return
        return

def listen():
    global event
    clear()
    event.clear()
    assistant_thread = threading.Thread(target=AssistantTask().run)
    assistant_thread.start()


def stop():
    global event
    clear()
    my_text.insert(END, "Stopped Listening\n")
    event.set()


def speak():
    if chat_entry.get():
        filename = "api_key"
        bot_read(filename, chat_entry.get())


def get_response(code, text):
    try:
        # add api key
        client = OpenAI(
            api_key=code
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model="gpt-3.5-turbo",
        )

        return response
    except Exception as e:
        print(e)
        input_file = open("api_key", "wb")
        input_file.close()
        os.remove("api_key")
        
        return False

                
def bot_read(filename, text):
    global no_api
    global session_tokens

    try:
        if os.path.isfile(filename):
            # open the file
            input_file = open(filename, 'rb')
            # load the data from the file into a variable
            stuff = pickle.load(input_file)

            if "sk-proj" not in stuff:
                input_file = open(filename, "wb")
                input_file.close()
                os.remove("api_key")
            else:
                response = get_response(stuff, text)
                if response:
                    clear()
                    text_response = (response.choices[0].message.content)
                    total_tokens = (response.usage.total_tokens)
                    session_tokens = session_tokens + total_tokens
                    my_text.insert(END, f"{text_response} [current - {total_tokens}, total - {session_tokens}]\n\n")
                    text_to_speech(text_response)
                else:
                    my_text.insert(END, "API key error!\n")
                    return

        else:
            input_file = open(filename, "wb")
            input_file.close()
            os.remove("api_key")
           
            if not no_api:
                my_text.insert(END, "\nChatGPT requires an API key. Read aloud mode activated:")
                no_api = 1
                os.remove("api_key")
            if len(text) > 2:
                my_text.insert(END, f"\n{text}")
                text_to_speech(text)

    except Exception as e:
        print(f"\nAn error occurred in reading text: \n{e}")
        os.remove(filename)


def text_to_speech(res):
    global male_voice
    # Passing the text and language to the engine,
    # here we have marked slow=False. Which tells
    # the module that the converted audio should
    # have a high speed
    try:
        if male_voice == 1:
            engine = pyttsx3.init()

            # Set properties before adding anything to speak
            engine.setProperty('rate', 150)  # Speed percent (can go over 100)
            engine.setProperty('volume', 0.9)  # Volume 0-1
        
            # Adding text to speak
            engine.say(res)
            
            # Blocks while processing all the currently queued commands
            engine.runAndWait()
            engine.stop()
        else:
            engine = gTTS(text=res, lang=language, slow=False)
            # Saving the converted audio in a mp3 file named
            filename = "response.mp3"
            engine.save(filename)
            
            playsound.playsound(filename)
            os.remove("response.mp3")
    except Exception as e:
        print(f"\nAn error occurred: \n{e}")
        text_to_speech(res)


def clear():
    # clear main text box
    my_text.delete(1.0, END)
    # clear entry box
    chat_entry.delete(0, END)


def key():
    global options_active
    filename = "api_key"
    try:
        if os.path.isfile(filename):
            # open the file
            input_file = open(filename, 'rb')

            print(input_file)

            # load the data from the file into a variable
            stuff = pickle.load(input_file)

            # Output entry stuff
            api_entry.insert(END, stuff)
        else:
            input_file = open(filename, "wb")
            input_file.close()
            print(input_file)

    except Exception as e:
        print(f"\nAn error occurred:\n{e}")

    root.geometry("620x720")
    api_frame.pack(pady=10)
    options_active = 1


def options():
    global options_active
    if options_active:
        root.geometry("620x620")
        options_active = 0
    else:
        key()

    

def end():
    root.destroy()
    os._exit


def save_key():
    filename = "api_key"
    try:
        output_file = open(filename, 'wb')
        # add data to file
        pickle.dump(api_entry.get(), output_file)
        api_entry.delete(0, END)
        api_frame.pack_forget()
        root.geometry("620x620")
        customtkinter.set_default_color_theme("dark-blue")

    except Exception as e:
        print(f"\n\nAn error occurred while saving the key:\n\n{e}")


def change_voice():
    global male_voice
    male_voice = not male_voice
    my_text.insert(END, f"\nMale Voice: {male_voice}\n")



# Add text frame
text_frame = customtkinter.CTkFrame(root)
text_frame.pack(pady=20)

# get text widget responses
my_text = Text(text_frame,
               bg="#343638",
               width=65,
               bd=1,
               fg="#d6d6d6",
               relief="flat",
               wrap=WORD)
my_text.grid(
    row=0,
    column=0)

# create scroll bar for text widget
text_scroll = customtkinter.CTkScrollbar(text_frame,
                                         command=my_text.yview)
text_scroll.grid(row=0, column=1, sticky="ns")

# add the scrollbar to the text box
my_text.configure(yscrollcommand=text_scroll.set)

# entry widget
chat_entry = customtkinter.CTkEntry(root,
                                    placeholder_text="Allow the oracle to listen or submit text...",
                                    width=535,
                                    height=50,
                                    border_width=1)
chat_entry.pack(pady=10)

# create button frame
button_frame = customtkinter.CTkFrame(root, fg_color="#242424")
button_frame.pack(pady=10)

# create buttons
submit_button = customtkinter.CTkButton(button_frame,
                                        text="Submit",
                                        command=speak)
submit_button.grid(row=0, column=0, padx=24)

listen_button = customtkinter.CTkButton(button_frame,
                                        text="Listen",
                                        command=listen)
listen_button.grid(row=0, column=1, padx=24, pady=10)


api_button = customtkinter.CTkButton(button_frame,
                                     text="Options",
                                     command=options)
api_button.grid(row=0, column=2, padx=24, pady=10)

clear_button = customtkinter.CTkButton(button_frame,
                                       text="Clear",
                                       command=clear)
clear_button.grid(row=1, column=0, padx=24)

stop_button = customtkinter.CTkButton(button_frame,
                                      text="Stop",
                                      command=stop)

stop_button.grid(row=1, column=1, padx=24, pady=10)

exit_button = customtkinter.CTkButton(button_frame,
                                      fg_color=("", "black"),
                                      text="Exit",
                                      command=end)

exit_button.grid(row=1, column=2, padx=24, pady=10)
# api frame
api_frame = customtkinter.CTkFrame(root, fg_color="#242424")
api_frame.pack(pady=10)

# APi entry widget
api_entry = customtkinter.CTkEntry(api_frame, placeholder_text="Enter API Key",
                                   width=200, height=50, border_width=1)
api_entry.grid(row=0, column=0, padx=10, pady=5)

# Add api button
api_save_button = customtkinter.CTkButton(api_frame,
                                          text="Save Key",
                                          command=save_key)
api_save_button.grid(row=0, column=1, padx=10)
# Add api button
voice_button = customtkinter.CTkButton(api_frame,
                                          text="Change Voice",
                                          command=change_voice)
voice_button.grid(row=0, column=2, padx=10, pady=10)

root.mainloop()
